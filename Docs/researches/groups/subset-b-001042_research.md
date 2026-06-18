# subset-b-001042 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_mv.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_mv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_nv.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_nv.c

## Purpose
Implements the libata low-level driver for NVIDIA nForce SATA controllers. It supports legacy BMDMA-style controllers, NF2/NF3 and CK804 interrupt layouts, CK804/MCP04 ADMA with NCQ, MCP5x software NCQ, optional MSI, reset quirks, hotplug handling, and device-specific NCQ limitations.

## Important APIs, Types, And Functions
- Module parameters `adma`, `swncq`, and `msi` choose optional ADMA, software NCQ, and MSI behavior.
- `enum nv_host_type`, `nv_pci_tbl`, `nv_port_info`, and `struct nv_pi_priv` map PCI IDs to port ops, interrupt handlers, and SCSI host templates.
- ADMA state uses `struct nv_adma_port_priv`, `struct nv_adma_cpb`, and `struct nv_adma_prd`; major functions are `nv_adma_port_start`, `nv_adma_qc_prep`, `nv_adma_qc_issue`, `nv_adma_interrupt`, `nv_adma_error_handler`, `nv_adma_sdev_configure`, `nv_adma_register_mode`, and `nv_adma_mode`.
- Software NCQ state uses `struct nv_swncq_port_priv` and `struct defer_queue`; major functions are `nv_swncq_qc_prep`, `nv_swncq_qc_issue`, `nv_swncq_host_interrupt`, `nv_swncq_sdbfis`, `nv_swncq_dmafis`, and `nv_swncq_error_handler`.
- Generic paths include `nv_host_intr`, `nv_generic_interrupt`, `nv_nf2_interrupt`, `nv_ck804_interrupt`, `nv_scr_read`, `nv_scr_write`, `nv_hardreset`, freeze/thaw variants, `nv_init_one`, `nv_pci_device_resume`, and host stop helpers.

## Control Flow
Probe first rejects non-SATA NVIDIA IDE-function matches by requiring all six PCI BARs. It enables the PCI device, optionally upgrades CK804 to ADMA or MCP5x to SWNCQ according to module parameters, prepares a libata BMDMA host, maps BAR5, configures SCR addresses, enables SATA register space on CK804-or-newer chips, initializes ADMA or SWNCQ mode if selected, optionally enables MSI, and activates the host through the selected interrupt handler.

Legacy interrupts either scan active tags directly or decode NVIDIA per-port interrupt status bits before calling `nv_host_intr`, which freezes on hotplug, completes BMDMA commands on device IRQs, and clears status for idle interrupts. Reset flow intentionally prefers softreset during boot and error handling and uses `nv_hardreset` only for post-boot probing of empty ports; signature acquisition is deliberately reported as unreliable by returning `-EAGAIN`.

ADMA mode allocates coherent CPB/APRD memory after first allocating 32-bit legacy BMDMA resources, programs CPB bases, and starts ports in register mode. Per-device configuration disables ADMA and lowers DMA limits when ATAPI is present because ATAPI must use the legacy 32-bit DMA path. ADMA command prep builds a CPB taskfile and in-CPB or external APRD list, marks the CPB valid only after barriers, and issue appends the tag to hardware. The ADMA interrupt path handles register-mode fallback, notifier/error bitmaps, hotplug/timeouts/SError freezes, CPB response inspection, multi-tag completion, and notifier clear ordering required by NVIDIA.

SWNCQ mode uses normal taskfile issue for one NCQ command at a time while queueing additional tags in `defer_queue`. DMA setup FIS interrupts program per-tag PRD tables and start BMDMA, SDB FIS interrupts compare software active bits with `SCR_ACTIVE`, complete done tags, and reissue or dequeue commands when device-to-host FIS sequencing requires it. Hotplug and illegal FIS sequences freeze the port for libata EH.

## State And Persistence
`nv_host_priv` persists the selected host type. ADMA port state keeps coherent CPB/APRD pointers, BAR5 control/generic/notifier clear addresses, the effective ADMA DMA mask, mode flags for register fallback and ATAPI setup, and the last NCQ mode issued. SWNCQ port state keeps coherent PRD tables, MMIO pointers for SActive/IRQ/tag registers, a software active bitmap, deferred tag FIFO, last issued tag, and bitmaps of observed D2H/DMA/SDB FIS activity. PCI config register `NV_MCP_SATA_CFG_20` persists SATA-space, port enable, and ADMA port bits and is restored on resume. Freeze/thaw paths persist interrupt masks in chipset-specific MMIO or SCR register blocks.

## Dependencies And Integration Points
The driver depends on PCI managed resource helpers, libata BMDMA/SFF/EH/NCQ APIs, SCSI queue-limit callbacks, tracepoints for taskfile and BMDMA status, DMA mask management, PCI MSI, and NVIDIA PCI device IDs/config registers. ADMA and SWNCQ integrate with libata queue depth through `ata_ncq_sdev_groups` and `ata_scsi_change_queue_depth`, while fallback paths reuse `ata_bmdma_port_start`, `ata_bmdma_qc_issue`, `ata_bmdma_error_handler`, and standard SCR helpers.

## Risks And Edge Cases
Hardreset behavior is intentionally conservative because several NVIDIA generations fail link bring-up or device signature capture after hardreset. ADMA cannot safely handle ATAPI and must coordinate per-device queue limits with a shared PCI DMA mask. Entering register mode while ADMA commands are outstanding aborts command processing, so result taskfiles for NCQ are rejected. NVIDIA notifier clearing requires both ports' clear registers to be written together. SWNCQ sequencing is fragile: missing D2H FIS, backout interrupts, stale `SCR_ACTIVE`, and deferred tag FIFO errors can mis-complete or reissue commands incorrectly. Known Maxtor devices on MCP51/MCP55 early revisions have SWNCQ disabled by reducing queue depth to one.

## Test Signals
Important tests include BAR-count rejection of IDE functions, generic/NF2/CK804 interrupt masking and hotplug handling, boot probing via softreset with post-boot hardreset on empty ports, ADMA DMA/NCQ completion and CPB error classification, ATAPI fallback that changes DMA mask and segment limits, notifier clear behavior across both ports, ADMA suspend/resume with ATAPI port bits restored, SWNCQ deferred multi-tag issue/completion, backout and missing-D2H reissue paths, Maxtor queue-depth disablement, and MSI activation when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_nv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_promise.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_promise.c

## Purpose
Implements the libata low-level driver for Promise SATA/PATA TX2/TX4/TX4000 controllers. It supports first- and second-generation Promise SATA adapters, optional PATA ports, Promise packet command submission, SATA SCR access and hotplug, PATA cable detection, DMA/ATAPI filtering, port reset quirks, and shared PCI interrupt handling.

## Important APIs, Types, And Functions
- `pdc_port_info` and `pdc_ata_pci_tbl` map Promise board variants to SATA, PATA, generation, and port-count flags.
- `struct pdc_port_priv` holds the coherent 128-byte command packet and DMA address; `struct pdc_host_priv` provides `hard_reset_lock` for serialized port hardreset register toggles.
- Port ops are layered as `pdc_common_ops`, `pdc_sata_ops`, `pdc_old_sata_ops`, and `pdc_pata_ops`.
- Command preparation and issue are handled by `pdc_qc_prep`, `pdc_fill_sg`, `pdc_atapi_pkt`, `pdc_packet_start`, and `pdc_qc_issue`, with packet helpers supplied by `sata_promise.h`.
- Reset/EH/IRQ helpers include `pdc_reset_port`, `pdc_sata_hardreset`, `pdc_pata_softreset`, `pdc_error_handler`, `pdc_post_internal_cmd`, `pdc_error_intr`, `pdc_host_intr`, and `pdc_interrupt`.
- Probe/setup functions include `pdc_common_port_start`, `pdc_sata_port_start`, `pdc_ata_setup_port`, `pdc_host_init`, and `pdc_ata_init_one`.

## Control Flow
Probe enables the PCI device, maps the MMIO BAR, selects two or four SATA/PATA ports from board flags and a flash-control PATA-present bit, allocates a libata host plus private reset lock, assigns per-port ATA and SCR MMIO windows including special SATAII TX4 port remapping, initializes global Promise registers and hotplug masks, sets a 32-bit ATA DMA mask, and activates the host with `pdc_interrupt`.

Port start allocates standard BMDMA resources plus a coherent Promise command packet. Gen II SATA start additionally adjusts `PHYMODE4`. For DMA and most no-data commands, `pdc_qc_prep` builds an ASIC packet with a PRD table pointer, taskfile register writes, optional LBA48 fields, final command register write, or ATAPI packet sequence. `pdc_qc_issue` submits the packet by writing a sequence register and `PDC_PKT_SUBMIT`; polling or CDB-interrupt cases fall back to SFF issue.

The interrupt handler serializes on `host->lock`, reads and clears Gen II hotplug flags, reads/acks the sequence interrupt mask, freezes ports with plug/unplug status, and dispatches packet interrupts to `pdc_host_intr`. `pdc_host_intr` checks per-port global error bits, maps them to libata error classes, snapshots SError for SATA links, resets the port, and aborts; otherwise it waits idle and completes DMA/no-data packet commands. Error handling resets the Promise port before invoking libata SFF EH unless the port is already frozen.

## State And Persistence
Per-port persistent state is the coherent packet buffer, the standard BMDMA PRD table, MMIO taskfile/SCR addresses, and libata flags for generation/port type. Host persistent state is the hard-reset spinlock and mapped BAR. Hardware state persists in sequence interrupt masks, hotplug control/status bits, flash/TBG/slew registers, per-port control/status reset and DMA-enable bits, FPDMA control/status flags, SATA error/link-layer registers, and PCI-control hardreset bits. The driver uses managed allocations and `ata_pci_remove_one`, so teardown is mostly devres/libata-managed.

## Dependencies And Integration Points
The file depends on libata SFF/BMDMA helpers, SCSI host templates, PCI managed mapping and DMA-mask APIs, Promise packet construction helpers from `sata_promise.h`, ATA/SCSI command constants, and libata EH/SCR/hotplug APIs. It integrates with libata via custom taskfile load/execute wrappers that warn on DMA use, custom ATAPI DMA filters, port-specific freeze/thaw hooks, hardreset/softreset callbacks, and shared IRQ activation.

## Risks And Edge Cases
The hardware has a known PRD/ASIC bug requiring `PDC_MAX_PRD = LIBATA_MAX_PRD - 1` and an extra split when the final PRD length exceeds `41*4`. PRDs are 32-bit only, so DMA addresses are truncated after the driver restricts the DMA mask. Gen I SATA cannot use ATAPI DMA, and even Gen II filters ATAPI DMA to a whitelist plus a `WRITE_10` high-LBA PIO exception. SATA hardreset cannot reliably acquire the first D2H register FIS and relies on follow-up SRST. Hotplug register access must stay serialized under the host lock. Gen II FPDMA reset requires byte-sized writes because full-register writes are unsafe while NCQ runs.

## Test Signals
Useful tests include probe of two-port, four-port, SATA+PATA, and SATAII TX4 remapped boards; PATA cable detection; DMA packet issue and completion; no-data packet issue outside polling/CDB-interrupt cases; ATAPI DMA whitelist/PIO fallback behavior; 64 KiB PRD splitting and final-entry ASIC bug split; Gen II hotplug freeze/thaw masking; port reset after packet errors and internal commands; SATA hardreset followed by SRST; and shared IRQ behavior with empty masks or `0xffffffff` reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_promise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_promise.h -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_promise.h

## Purpose
Provides common inline helpers and packet bit definitions for Promise SATA packet construction. The header is used by `sata_promise.c` to serialize ATA taskfile state into the controller's command packet format for DMA and no-data commands.

## Important APIs, Types, And Functions
- `enum pdc_packet_bits` defines packet flags for read/no-data, size fields, clear-BSY/wait-DRDY semantics, last-register markers, and device-control encoding.
- `pdc_pkt_header` initializes packet control words, writes the SG table DMA address, selects master/slave device state, and emits the device-control register write.
- `pdc_pkt_footer` optionally emits the taskfile device register and always emits the command register with the last-register marker.
- `pdc_prep_lba28` serializes feature, sector count, and 28-bit LBA registers.
- `pdc_prep_lba48` serializes high-order then low-order feature, count, and LBA bytes for 48-bit commands.

## Control Flow
`sata_promise.c` calls `pdc_pkt_header` first for ATA DMA or no-data commands, then chooses `pdc_prep_lba48` or `pdc_prep_lba28` according to `ATA_TFLAG_LBA48`, and finishes with `pdc_pkt_footer`. The helpers append bytes into a caller-owned 128-byte coherent packet buffer and return the next write offset so the caller can chain the packet pieces without extra parsing.

## State And Persistence
The header owns no persistent state. It mutates only the provided packet buffer using taskfile fields and the SG table DMA address. Endianness is explicit for 32-bit packet words via `cpu_to_le32`; individual register opcodes and values are byte writes.

## Dependencies And Integration Points
The header depends on `<linux/ata.h>` for taskfile fields, ATA register constants, protocol identifiers, and device-selection bits. It is tightly coupled to Promise controller packet layout and to `sata_promise.c`'s `pdc_qc_prep` sequencing.

## Risks And Edge Cases
`pdc_pkt_header` supports only `ATA_PROT_DMA` and `ATA_PROT_NODATA` and calls `BUG()` for other protocols, so callers must filter ATAPI and PIO paths before using it. The SG table address is stored as a 32-bit little-endian value, matching the 32-bit DMA mask requirement in the driver. LBA48 serialization order must remain high-byte then low-byte for each register pair. Incorrect offset chaining can corrupt the packet because the helpers do not bounds-check the caller's buffer.

## Test Signals
Test signals include correct packet bytes for read vs write DMA, no-data commands, master/slave device selection, device-control propagation, LBA28 and LBA48 register ordering, command byte with `PDC_LAST_REG`, and no use of these helpers for unsupported protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_promise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_qstor.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_qstor.c

## Purpose
Implements the libata low-level driver for Pacific Digital QStor four-port SATA controllers. It drives a packet DMA engine for ATA DMA commands, uses MMIO/SFF register mode for other commands and reset/EH, handles the controller's status FIFO interrupt format, initializes global/channel FIFO and PHY state, and chooses 32- or 64-bit DMA masks based on the host bus.

## Important APIs, Types, And Functions
- `qs_port_info`, `qs_ata_pci_tbl`, and `qs_ata_ops` define a four-port SATA, PIO-polling, UDMA6 libata controller.
- `struct qs_port_priv` stores one coherent packet/PRD buffer, its DMA address, and whether the port is in MMIO or packet mode.
- Command path functions are `qs_qc_prep`, `qs_fill_sg`, `qs_packet_start`, and `qs_qc_issue`.
- Mode/reset/EH functions include `qs_enter_reg_mode`, `qs_reset_channel_logic`, `qs_freeze`, `qs_thaw`, `qs_prereset`, `qs_error_handler`, and SCR accessors.
- Interrupt and completion helpers include `qs_intr`, `qs_intr_pkt`, `qs_intr_mmio`, and `qs_do_or_die`.
- Probe/setup helpers include `qs_ata_setup_port`, `qs_port_start`, `qs_host_init`, `qs_set_dma_masks`, `qs_host_stop`, and `qs_ata_init_one`.

## Control Flow
Probe allocates a four-port host, enables PCI, maps BAR4, selects a DMA mask from the QStor physical-interface register, assigns per-port MMIO taskfile and SCR addresses at 0x4000-byte channel strides, performs global/channel reset and FIFO/CPB setup through `qs_host_init`, enables PCI bus mastering, and activates the host with `qs_intr`.

Before command prep, `qs_qc_prep` forces register mode. Non-DMA commands are left to libata SFF. DMA commands fill a 64-byte command packet: a host control block with flags, byte count, PRD count, and PRD DMA address; a device control block with PIO/DMA and LBA48 flags; and a register FIS from `ata_tf_to_fis`. Issue switches DMA commands to packet mode, clears channel errors, flushes memory writes, writes the run-packet command FIFO, and otherwise uses `ata_sff_qc_issue`.

Interrupt handling first drains packet completions from the host status FIFO, decoding valid entries for device status, host status, and port number. Successful or device-error packet statuses switch the port back to register mode and complete or abort/freeze through `qs_do_or_die`. Then MMIO-mode interrupts scan all ports, tolerate known spurious interrupts when no command is active by reading status, and route real active commands through `ata_sff_port_intr`.

## State And Persistence
Per-port state is the coherent packet/PRD allocation, the packet DMA address programmed into channel CPB base registers, and the `qs_state_mmio`/`qs_state_pkt` mode flag. Persistent hardware state includes global interrupt enable, global reset, PHY enable, per-channel register-vs-packet mode, channel/device reset bits, FIFO thresholds, CPB separation factor, command FIFO, status FIFO, SCR registers, and bus-width information. Host stop disables interrupts and asserts global reset.

## Dependencies And Integration Points
The driver depends on PCI managed resource mapping, DMA mask APIs, libata SFF helpers and EH, SCSI host templates, ATA FIS construction, and QStor/PDC PCI IDs. It integrates with libata through custom `qc_prep`/`qc_issue`, SCR callbacks, prereset/error-handler hooks that force register mode, and an IRQ handler that combines packet FIFO and normal SFF interrupt processing.

## Risks And Edge Cases
ATAPI DMA is explicitly unsupported and `qs_qc_issue` treats `ATAPI_PROT_DMA` as a bug. Packet mode/MMIO mode transitions are fragile and can generate spurious interrupts that the driver deliberately acknowledges. `qs_fill_sg` writes 64-bit addresses and lengths but advances by 16 bytes per PRD, so packet layout and `QS_MAX_PRD` sizing must match hardware. Host status FIFO decoding depends on valid/empty bits; mishandling can drop completions or spin. The DMA mask must match the bridge-visible bus width even though packet fields are always 64-bit.

## Test Signals
Useful tests include four-port probe with BAR4 MMIO descriptors, 32-bit and 64-bit DMA-mask selection, host/channel reset and FIFO setup, DMA packet issue/completion with status FIFO host status 0 and 3, device-error abort versus host-error freeze, MMIO fallback for PIO/no-data commands, spurious no-active-command interrupts, SCR read/write bounds, prereset forcing register mode, and host stop disabling interrupts plus global reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_qstor.c -->
