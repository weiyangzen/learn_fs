# sources/distributed-fs/ceph-client/drivers/ata/sata_mv.c

## Purpose
Implements the libata low-level driver for Marvell SATA controllers, covering PCI 50xx/60xx/6042/7042 adapters and Marvell SoC platform controllers. It binds controller-specific register maps, EDMA command/response queues, NCQ, port multiplier support, interrupt coalescing, PCI/MSI handling, SoC clocks/PHYs/MBUS windows, and many silicon errata into the `ata_port_operations` expected by libata.

## Important APIs, Types, And Functions
- Module parameters `msi`, `irq_coalescing_io_count`, and `irq_coalescing_usecs` tune interrupt delivery.
- Core private state is `struct mv_host_priv` for host flags, MMIO bases, IRQ mask cache, chip operations, clocks/PHYs, and DMA pools, and `struct mv_port_priv` for CRQB/CRPB rings, per-tag SG tables, ring indices, cached registers, and delayed error state.
- Hardware formats include `struct mv_crqb`, `struct mv_crqb_iie`, `struct mv_crpb`, and `struct mv_sg`.
- Port ops are split into `mv5_ops`, `mv6_ops`, and `mv_iie_ops`; `mv_hw_ops` selects generation-specific PHY, reset, flash, LED, and bus handling.
- Command path functions include `mv_qc_defer`, `mv_qc_prep`, `mv_qc_prep_iie`, `mv_qc_issue`, `mv_start_edma`, `mv_stop_edma`, `mv_fill_sg`, and BMDMA helpers used for ATAPI and DSM/TRIM fallback.
- Interrupt and EH functions include `mv_interrupt`, `mv_host_intr`, `mv_port_intr`, `mv_process_crpb_entries`, `mv_err_intr`, `mv_pmp_error_handler`, `mv_eh_freeze`, and `mv_eh_thaw`.
- Probe and lifecycle paths include `mv_pci_init_one`, `mv_platform_probe`, `mv_init_host`, `mv_create_dma_pools`, `mv_platform_suspend/resume`, `mv_pci_device_resume`, `mv_init`, and `mv_exit`.

## Control Flow
PCI or platform probe allocates an `ata_host`, initializes `mv_host_priv`, maps controller MMIO, creates DMA pools for EDMA queues and SG tables, fills per-port MMIO descriptors, identifies the chip generation with `mv_chip_id`, performs global and per-port reset/PHY errata through `mv_hw_ops`, clears interrupts, configures optional coalescing, and activates the host with `mv_interrupt`.

For I/O, libata calls `mv_qc_defer` to serialize incompatible PIO/non-NCQ operations against active EDMA/NCQ traffic. `mv_qc_prep` or `mv_qc_prep_iie` builds the hardware command request block and per-tag ePRD table, splitting SG entries on 64 KiB boundaries. `mv_qc_issue` starts EDMA for DMA/NCQ commands and advances the request producer pointer; PIO, no-data, ATAPI, and DSM paths stop EDMA, select the PMP, enable the needed interrupt bits, and fall back through SFF/BMDMA or direct FIS issue for selected errata workarounds.

Interrupt handling reads the cached main cause/mask, optionally blocks MSI reentry, handles PCI fault causes, acknowledges host-controller cause bits, and routes per-port DONE/ERR bits. DONE processing consumes CRPB responses, completes the complement of unfinished tags with `ata_qc_complete_multiple`, and advances the response consumer pointer. ERR processing reads and clears SError, EDMA error cause, and GenIIe FIS cause, classifies device, hotplug, parity, SError, self-disable, and async-notify cases, and either aborts links or freezes the port for libata EH. GenIIe FIS-based switching plus NCQ device errors are delayed until outstanding commands drain so PMP-specific NCQ analysis can run before a full freeze.

## State And Persistence
Persistent runtime state lives in libata host/port structures, MMIO registers, and coherent DMA objects. `mv_host_priv` caches hardware flags, IRQ mask state, register offsets, number of ports, optional SoC clocks/PHYs, and DMA pools. `mv_port_priv` persists EDMA queue indices, coherent CRQB/CRPB rings, per-tag SG tables, cached `FISCFG`/`LTMODE`/`EDMA_HALTCOND`/reserved register values, EDMA/NCQ/FBS flags, and delayed EH PMP maps. Hardware state persists across operations in EDMA queue pointers, SCR registers, IRQ masks/causes, PHY mode registers, MBUS windows, and PCI/SoC bus configuration. Suspend/resume reinitializes adapter hardware and resumes libata hosts; platform remove and error paths power off clocks/PHYs and detach the host.

## Dependencies And Integration Points
The file integrates heavily with libata core and SFF/BMDMA helpers (`ata_host_activate`, `ata_bmdma_qc_issue`, `ata_sff_softreset`, `sata_pmp_error_handler`, `ata_qc_complete_multiple`, EH descriptors/actions), SCSI host templates and NCQ queue-depth support, PCI resource/MSI/DMA APIs, platform device and device-tree probing, common clock framework, generic PHY API, Marvell MBUS DRAM window data, kernel interrupt locking, and endian/DMA memory primitives. It also relies on hardware-specific Marvell register definitions embedded in the file.

## Risks And Edge Cases
The driver is dominated by silicon errata: COMRESET writes must avoid sleep bits, 60x1 SATA#24 can corrupt large multiwrite PIO, SATA#25 affects NCQ error log reads, PHY_MODE writes can corrupt adjacent PHY state, GenIIe BMDMA requires a reserved bit, and some links need fallback to 1.5 Gb/s after repeated hardreset status `0x121`. Ring pointer/cache mismatches can lose or double-complete commands. Interrupt mask naming is inverted in hardware, so coalescing bits must remain exclusive with per-port DONE bits. FBS+NCQ errors require delayed handling and are unsafe if EDMA self-disables unexpectedly. Platform probe must unwind partially enabled clocks/PHYs correctly. HighPoint RocketRAID boards are warned as data-corrupting due to BIOS metadata behavior.

## Test Signals
Useful signals include successful probe for Gen I, Gen II, Gen IIE, PCIe, and SoC variants; DMA/NCQ I/O with per-tag completions and no ring desynchronization; DSM/TRIM and ATAPI fallback through BMDMA; PMP command routing and FIS-based-switching NCQ error recovery; hotplug connect/disconnect freezes; async notification without unnecessary reset; interrupt coalescing enabled/disabled paths; MSI masking/unmasking; suspend/resume reinitialization; SoC clock/PHY error unwinding; SG entries crossing 64 KiB boundaries; and hardreset fallback from 3 Gb/s to 1.5 Gb/s on troublesome links.
