# subset-b-001041 ATA low-level driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sc1200.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_sc1200.c

## Purpose
`pata_sc1200.c` is a libata PCI driver for the National Semiconductor/AMD SC1200 IDE controller. It provides PIO, MWDMA, and UDMA timing programming, works around the controller's shared MWDMA/UDMA selection bit, and serializes command issue across the two channels.

## Important APIs, Types, and Functions
Key callbacks are `sc1200_set_piomode()`, `sc1200_set_dmamode()`, `sc1200_qc_issue()`, `sc1200_qc_defer()`, and `sc1200_init_one()`. `sc1200_clock()` reads chipset I/O ports `0x903c`, `0x903d`, and `0x901e` to select 33/48/66 MHz timing tables. The driver registers `sc1200_port_ops`, `sc1200_sht`, and a PCI table matching `PCI_DEVICE_ID_NS_SCx200_IDE`.

## Control Flow, State, and Persistence
Probe builds a single `ata_port_info` with PIO4, MWDMA2, UDMA2, slave support, and BMDMA ops, then calls `ata_pci_bmdma_init_one()`. Mode-setting callbacks write PCI config timing dwords under the per-channel base `0x40 + 0x10 * port_no`. Command issue consults `ap->private_data` as the previous device and reloads DMA timings when switching between a UDMA and non-UDMA peer. `qc_defer` first applies standard libata deferral, then delays if the opposite channel has active commands.

## Dependencies and Integration Points
The driver depends on PCI config access, legacy x86-style I/O port reads, libata BMDMA helpers, SCSI host registration through `ATA_BASE_SHT`, and dumb PRD preparation via `ata_bmdma_dumb_qc_prep`. It integrates with libata cable/mode negotiation through fixed 40-wire cable reporting and timing callbacks.

## Risks and Test Signals
Risks include wrong clock detection from magic chipset ports, stale `ap->private_data` causing timing reload omissions, unsafe mixed MWDMA/UDMA operation, and throughput loss from host-wide serialization. Useful tests are boot/probe on SC1200 revisions, PIO0-4 and MWDMA/UDMA mode changes on master/slave pairs, alternating UDMA and MWDMA commands, simultaneous activity on both channels, suspend/resume with timing restoration, and dmesg/libata trace checks for deferred commands and DMA errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sc1200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sch.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_sch.c

## Purpose
`pata_sch.c` supports Intel SCH PATA controllers such as AF82US15W/L and AF82UL11L. It is a compact BMDMA libata PCI driver that programs per-device timing registers documented by the SCH datasheet.

## Important APIs, Types, and Functions
The important callbacks are `sch_set_piomode()`, `sch_set_dmamode()`, and `sch_init_one()`. Register definitions include `D0TIM`, `D1TIM`, masks for PIO/MWDMA/UDMA fields, `PPE` prefetch/post enable, and `USD` synchronous DMA. Static objects include `sch_pata_ops`, `sch_port_info`, `sch_sht`, `sch_pci_tbl`, and `sch_pci_driver`.

## Control Flow, State, and Persistence
Probe prints the driver version and calls `ata_pci_bmdma_init_one()` with one port-info block allowing PIO4, MWDMA2, UDMA5, and slave devices. PIO setup selects `D0TIM` or `D1TIM`, clears PIO and prefetch bits, writes the requested PIO mode, and enables `PPE` only for ATA disk devices. DMA setup reads the same register, sets `USD` and the UDMA field for UDMA, or clears `USD` and writes the MWDMA field for multiword DMA.

## Dependencies and Integration Points
This file depends on PCI config access, standard libata BMDMA port operations, SCSI host setup through `ATA_BMDMA_SHT`, and libata mode negotiation. Cable detection is reported as unknown, leaving libata policy to constrain final modes where needed.

## Risks and Test Signals
Risks include incorrect register bit masking between PIO, MWDMA, UDMA, and prefetch fields; enabling prefetch for ATAPI devices; and mode negotiation beyond a real board's cabling. Tests should cover disk and ATAPI devices, PIO and DMA transitions on both master/slave slots, UDMA5 limiting, suspend/resume through generic PCI ATA hooks, and config-space register inspection after each negotiated mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_serverworks.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_serverworks.c

## Purpose
`pata_serverworks.c` drives ServerWorks/RCC OSB4, CSB5, CSB6, CSB6IDE2, and HT1000 PATA controllers. It handles chipset errata, revision-specific UDMA limits, OEM cable detection, and different BMDMA scatter-gather capabilities for OSB4 versus CSB-class controllers.

## Important APIs, Types, and Functions
Important mode and policy callbacks are `serverworks_cable_detect()`, `serverworks_osb4_filter()`, `serverworks_csb_filter()`, `serverworks_set_piomode()`, and `serverworks_set_dmamode()`. Probe/fixup helpers include `serverworks_fixup_osb4()`, `serverworks_fixup_csb()`, `serverworks_fixup_ht1000()`, `serverworks_fixup()`, `serverworks_init_one()`, and resume-only `serverworks_reinit_one()`. `csb_bad_ata100[]` lists Seagate models whose UDMA5 is disabled.

## Control Flow, State, and Persistence
Probe enables the PCI device, applies chipset fixups, selects one of four port-info profiles, and initializes BMDMA through libata. OSB4 fixup locates the companion bridge, disables a 600 ns interrupt mask, and enables UDMA/33 support or falls back to a no-UDMA profile if the bridge cannot be found. CSB fixup configures third-channel or RAID-function side registers, enables DMA in register `0x5a`, and returns a mode selector indicating whether UDMA5 is available. Timing callbacks write PIO bytes at `0x40+offset`, CSB PIO mode nibbles at `0x4a`, MWDMA bytes at `0x44+offset`, UDMA per-port nibbles at `0x56+port`, and UDMA enable bits in `0x54`.

## Dependencies and Integration Points
The driver depends on libata BMDMA and PCI helpers, PCI companion-device discovery via `pci_get_device()`, OEM subsystem IDs for Dell/Sun cable detection, and SCSI host templates that distinguish dumb OSB4 DMA from normal CSB DMA. It integrates with libata `mode_filter` to suppress unsafe OSB4 disk UDMA and model-specific CSB5 UDMA5.

## Risks and Test Signals
Risks include fragile NDA/errata-derived register programming, PCI companion bridge lookup failures, wrong cable detection on non-Dell/Sun OEM systems, model-string filtering that misses affected drives, and resume paths failing to replay fixups. Tests should cover each PCI device ID and revision class, UDMA4 versus UDMA5 selection, listed Seagate models, OSB4 fallback without bridge, CSB6 third-channel dummy-port handling, Dell/Sun subsystem cable bits, suspend/resume, and sustained DMA stress with error-handler recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_serverworks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sil680.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_sil680.c

## Purpose
`pata_sil680.c` is a Silicon Image/CMD SiI 680 PATA controller driver. It programs device timing registers, supports 100/133 MHz clock variants, optionally uses MMIO on selected PowerPC Cell systems, and falls back to PCI I/O-port BMDMA initialization otherwise.

## Important APIs, Types, and Functions
Register selectors `sil680_selreg()` and `sil680_seldev()` map logical offsets into PCI config space. Core callbacks are `sil680_cable_detect()`, `sil680_set_piomode()`, `sil680_set_dmamode()`, `sil680_sff_exec_command()`, `sil680_sff_irq_check()`, `sil680_init_chip()`, `sil680_init_one()`, and resume-only `sil680_reinit_one()`. `sil680_port_ops` inherits `ata_bmdma32_port_ops`.

## Control Flow, State, and Persistence
Probe enables PCI, initializes the chip, selects UDMA6 or slower UDMA5 caps based on clocking, and either configures MMIO BAR 5 manually or calls `ata_pci_bmdma_init_one()`. `sil680_init_chip()` adjusts cache-line and clock config, writes default timing registers for both channels, and rejects disabled clocking. PIO setup writes per-device data timings, shared taskfile timing using the slowest peer PIO mode, and IORDY/mode bits in config register `0x80 + 4 * port`. DMA setup programs MWDMA or UDMA timing words and mode bits, selecting a UDMA timing table based on 100/133 MHz clock state.

## Dependencies and Integration Points
This driver integrates with libata SFF/BMDMA helpers, PCI managed MMIO mapping, DMA mask setup, PPC `machine_is(cell)` conditional MMIO behavior, and ATA IRQ checking through a controller-specific config-space status bit. Its `sff_exec_command` flushes PCI posting by reading BMDMA command space.

## Risks and Test Signals
Risks include clock misconfiguration, wrong UDMA table selection, shared taskfile timing too fast for the peer device, config-space versus MMIO path differences, and disabled-clock probe rejection. Tests should exercise PIO peer speed mixing, MWDMA and UDMA0-6 programming, cable-detect behavior, both MMIO and I/O-port paths where hardware allows, interrupt status handling, resume reinitialization, and long DMA transfers on 100 MHz and 133 MHz clock configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sil680.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sis.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_sis.c

## Purpose
`pata_sis.c` supports a broad set of SiS PATA controllers, from pre-UDMA chips through ATA133 variants and concealed SiS5518/965/966-style IDs. It selects generation-specific timing ops, cable detection, mode masks, and register mapping at probe time.

## Important APIs, Types, and Functions
Core helpers include `sis_old_port_base()`, `sis_port_base()`, `sis_133_cable_detect()`, `sis_66_cable_detect()`, `sis_pre_reset()`, `sis_set_fifo()`, generation-specific `sis_*_set_piomode()` and `sis_*_set_dmamode()` callbacks, `sis_133_mode_filter()`, `sis_fixup()`, `sis_init_one()`, and `sis_reinit_one()`. `struct sis_chipset` maps host bridge IDs to `ata_port_info`; `struct sis_laptop` lists machines with short ATA40 cable quirks. `sis_info133_for_sata` is exported for the SiS180 SATA driver.

## Control Flow, State, and Persistence
Probe enables PCI, discovers the backing SiS bridge by scanning known IDs or temporarily unmasking concealed IDs, selects a chipset profile, applies generation fixups, and hands the device to `ata_pci_bmdma_init_one()` with the chipset pointer as host private data. Reset validates per-port enable bits in config register `0x4a` and clears FIFO settings before standard SFF probing. PIO and DMA callbacks write different config-space layouts depending on generation: old two-byte timing registers, ATA100 byte layouts, early ATA133 UDMA bytes, or later ATA133 dword timing registers at `0x40` or `0x70` selected by register `0x54`.

## Dependencies and Integration Points
The file depends on PCI bridge discovery, libata BMDMA/SFF reset helpers, exported SiS SATA integration, cable and laptop DMI/subsystem quirks, and mode filtering derived from controller register state. It also uses `host->private_data` on resume to replay fixups.

## Risks and Test Signals
Risks include concealed-ID probing side effects, a likely-sensitive register write in `sis_133_set_piomode()` where a dword timing value is written through a byte accessor, incomplete MWDMA support for some ATA100/early ATA133 paths, laptop cable quirks masking real 80-wire capability, and incorrect mapping between bridge ID and timing layout. Tests should cover every chipset family table bucket, concealed 5518/0180/1180 IDs, register remap at `0x70`, UDMA6 filtering when ATA133 is disabled, port-enable probing, FIFO behavior for ATA versus ATAPI, resume fixups, and libata mode negotiation under 40-wire and 80-wire cable reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sl82c105.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_sl82c105.c

## Purpose
`pata_sl82c105.c` drives the Winbond/SL82C105 PATA controller. It handles shared PIO/DMA timing registers by switching timings at DMA start and stop, and it resets the DMA engine around every DMA transfer per errata.

## Important APIs, Types, and Functions
Important callbacks and helpers are `sl82c105_pre_reset()`, `sl82c105_configure_piomode()`, `sl82c105_set_piomode()`, `sl82c105_configure_dmamode()`, `sl82c105_reset_engine()`, `sl82c105_bmdma_start()`, `sl82c105_bmdma_stop()`, `sl82c105_qc_defer()`, `sl82c105_sff_irq_check()`, `sl82c105_bridge_revision()`, `sl82c105_fixup()`, and `sl82c105_init_one()`. Control bits live in PCI config register `0x40`.

## Control Flow, State, and Persistence
Probe enables PCI, locates function 0 to determine the Winbond 553 bridge revision, disables DMA on missing or early bridge revisions, applies controller enable/fifo fixup bits, and registers through `ata_pci_bmdma_init_one()`. Reset suppresses absent secondary ports by checking config enable bits. PIO mode writes the shared timing word at `0x44 + 8*port + 4*dev`. DMA start delays, resets the DMA engine through register `0x7e`, writes DMA timing, then starts BMDMA. DMA stop stops BMDMA, resets the engine, delays, and restores PIO timing for the device.

## Dependencies and Integration Points
The driver uses libata BMDMA callbacks, config-space IRQ status checking, PCI slot lookup for bridge revision, 40-wire cable policy, and host-wide command serialization through `qc_defer` to avoid the reset bug across channels.

## Risks and Test Signals
Risks include DMA enablement on unsafe bridge revisions, missed timing restoration after abnormal completion, host-wide serialization assumptions, config-space IRQ status mistakes, and secondary-port enable handling. Tests should include early and later bridge revisions, DMA and PIO fallback profiles, timeout/error-handler DMA stop paths, alternating PIO/DMA commands, simultaneous channel attempts, suspend/resume fixup replay, and stress tests with ATAPI and disk DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_sl82c105.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_triflex.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_triflex.c

## Purpose
`pata_triflex.c` supports the Compaq TriFlex IDE controller used in older Compaq workstations. It programs per-device timing words and reloads timing on DMA start/stop because PIO and DMA timing requirements do not share a stable register setup.

## Important APIs, Types, and Functions
Important functions are `triflex_prereset()`, `triflex_load_timing()`, `triflex_set_piomode()`, `triflex_bmdma_start()`, `triflex_bmdma_stop()`, `triflex_init_one()`, and the suspend-specific `triflex_ata_pci_device_suspend()`. The port ops inherit `ata_bmdma_port_ops`, override BMDMA start/stop and prereset, and force 40-wire cable detection.

## Control Flow, State, and Persistence
Probe registers a single PIO4/MWDMA2/slave-capable profile through `ata_pci_bmdma_init_one()`. Prereset checks per-channel enable bits in PCI config register `0x80`. `triflex_load_timing()` maps PIO, SWDMA, and MWDMA modes to 16-bit timing values and writes the master or slave half of config dword `0x70` or `0x74`. PIO setup loads initial PIO timing; DMA start switches to DMA timing before `ata_bmdma_start()`; DMA stop stops BMDMA and restores PIO timing.

## Dependencies and Integration Points
The file integrates with libata BMDMA/SFF reset helpers, PCI config timing registers, and generic PCI remove/resume. Its suspend path deliberately saves PCI state without powering down or disabling the device because legacy APM BIOS code may require IDE access.

## Risks and Test Signals
Risks include unsupported or unexpected transfer mode reaching `BUG()`, timing not restored after DMA error recovery, legacy suspend behavior conflicting with modern PM expectations, and hardcoded 40-wire policy limiting performance. Tests should cover enable-bit absent ports, all PIO and MWDMA modes, DMA timeout/error paths, master/slave timing independence, suspend/resume on affected platforms, and dmesg checks for libata fallback when DMA is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_triflex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_via.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_via.c

## Purpose
`pata_via.c` is a VIA PATA driver covering many southbridge generations from MWDMA-only devices through UDMA133 and SATA/PATA combined configurations. It discovers the real bridge model, applies generation quirks, computes timings with libata timing helpers, and works around device-register loss after control writes.

## Important APIs, Types, and Functions
Important data includes `via_isa_bridges[]`, DMI quirk tables, `struct via_port`, and flags such as `VIA_BAD_PREQ`, `VIA_BAD_CLK66`, `VIA_SET_FIFO`, `VIA_BAD_AST`, `VIA_NO_ENABLES`, and `VIA_SATA_PATA`. Main functions are `via_cable_detect()`, `via_pre_reset()`, `via_do_set_mode()`, `via_set_piomode()`, `via_set_dmamode()`, `via_mode_filter()`, `via_tf_load()`, `via_port_start()`, `via_config_fifo()`, `via_fixup()`, `via_init_one()`, and `via_reinit_one()`.

## Control Flow, State, and Persistence
Probe enables PCI, finds the matching VIA ISA bridge by vendor/device/revision, checks enabled channels unless the bridge lacks enable bits, chooses a port-info profile by UDMA capability, applies FIFO/clock fixups, and initializes BMDMA with the bridge config as host private data. Timing setup computes ATA timing from the requested PIO/DMA mode, merges peer 8-bit timing, optionally writes address setup, writes PIO active/recover registers, and programs UDMA control bytes according to UDMA generation. `via_port_start()` allocates `struct via_port`; `via_tf_load()` caches the device/head byte and rewrites it after control-register changes to counter hardware behavior.

## Dependencies and Integration Points
This file depends on PCI bridge discovery, DMI matching, libata timing math, BMDMA and SFF helpers, ACPI cable fallback, and libata mode filtering. Some IDs use `via_port_ops_noirq` with 32-bit data transfer for controllers that cannot tolerate IRQ unmasking.

## Risks and Test Signals
Risks include bridge misidentification because VIA reused IDE PCI IDs, incorrect cable results on SATA/PATA combined ports, unsafe ATAPI DMA on known-bad boards, PREQ/FIFO and 66 MHz clock errata regressions, and stale cached device register state. Tests should cover all UDMA mask classes, bridge revisions and single-channel IDs, DMI cable/ATAPI quirks, Transcend SSD UDMA filtering, LBA48 taskfile loading after `nIEN` changes, suspend/resume fixups, and hotplug or ACPI cable-detect behavior on SATA/PATA combined hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_via.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pdc_adma.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pdc_adma.c

## Purpose
`pdc_adma.c` drives the Pacific Digital/PDC 0x1841 two-port ADMA controller. It supports ATA disk DMA through a single command parameter block and PRD packet, while using SFF/MMIO-style issue paths for non-DMA commands and rejecting ATAPI DMA.

## Important APIs, Types, and Functions
Important types are `enum adma_state_t` and `struct adma_port_priv` containing the coherent packet, DMA address, and state. Core functions are `adma_reset_engine()`, `adma_reinit_engine()`, `adma_qc_prep()`, `adma_fill_sg()`, `adma_qc_issue()`, `adma_intr_pkt()`, `adma_intr_mmio()`, `adma_intr()`, `adma_port_start()`, `adma_port_stop()`, `adma_host_init()`, and `adma_ata_init_one()`.

## Control Flow, State, and Persistence
Probe allocates a two-port host, maps MMIO BAR 4, sets a 32-bit DMA mask, lays out ATA register windows, resets/locks the ADMA engine, and activates the host with a custom interrupt handler. Each port allocates a coherent packet containing a CPB and PRDs, stores it in `ap->private_data`, initializes FIFO thresholds and CPB pointers, and resets engine state. DMA `qc_prep` builds CPB register writes, LBA48 fields, command byte, and PRDs; DMA `qc_issue` marks `adma_state_pkt` and starts the packet engine. Non-DMA commands mark `adma_state_mmio` and go through `ata_sff_qc_issue()`. Interrupt handling first processes packet-status interrupts, then MMIO status completion, completing or freezing/aborting the port based on ADMA status and CPB response flags.

## Dependencies and Integration Points
The driver uses MMIO register access, coherent DMA allocation, libata SFF port ops without standard BMDMA, custom host interrupts, `ATA_FLAG_PIO_POLLING`, and libata EH freeze/thaw/reset callbacks. It relies on `LIBATA_MAX_PRD` and 32-bit DMA addresses in the ADMA packet format.

## Risks and Test Signals
Risks include PRD length/address truncation, packet alignment constraints, race-prone `state` transitions between packet and MMIO modes, incomplete ATAPI support, CPB response interpretation bugs, and missed error recovery after host-bus errors. Tests should cover DMA read/write with many SG entries, LBA48 commands, non-DMA internal commands, simultaneous two-port interrupts, host-bus and device-error injection, freeze/thaw/prereset reinitialization, port stop cleanup, and verification that ATAPI DMA is consistently disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pdc_adma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_dwc_460ex.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_dwc_460ex.c

## Purpose
`sata_dwc_460ex.c` is a platform driver for the Synopsys DesignWare SATA core as used by AMCC 460EX-class systems. It combines SFF-style ATA register access with SATA SCR support, a DMAEngine-backed AHB DMA path, optional legacy DesignWare DMA probing, PHY management, and limited NCQ handling.

## Important APIs, Types, and Functions
Important structures are `struct sata_dwc_regs`, `struct sata_dwc_device`, and `struct sata_dwc_device_port`. Core functions include `dma_dwc_xfer_setup()`, `dma_dwc_xfer_done()`, `sata_dwc_scr_read()`, `sata_dwc_scr_write()`, `sata_dwc_isr()`, `sata_dwc_error_intr()`, `sata_dwc_dma_xfer_complete()`, `sata_dwc_qc_complete()`, `sata_dwc_port_start()`, `sata_dwc_exec_command_by_tag()`, `sata_dwc_bmdma_setup/start()`, `sata_dwc_qc_issue()`, `sata_dwc_hardreset()`, `sata_dwc_probe()`, and `sata_dwc_remove()`.

## Control Flow, State, and Persistence
Probe allocates a one-port ATA host and private controller state, maps platform MMIO, identifies DesignWare registers and FIFO DMA address, sets up ATA/SCR windows, enables SATA interrupts, obtains an IRQ, optionally initializes old DW DMA, initializes an optional PHY, and calls `ata_host_activate()`. Port start allocates per-port state, requests a DMA channel, powers on the PHY, initializes command state arrays, clears DMAC bits, sets burst sizes, clears SError, and stores private data. `qc_issue` prepares DMA descriptors for DMA protocols, handles NCQ by setting `SCR_ACTIVE` and issuing by tag, or delegates non-NCQ to `ata_bmdma_qc_issue()`. The ISR distinguishes error, NEWFP DMA setup FIS, non-NCQ completion, and NCQ completion using `sactive_issued`, `SCR_ACTIVE`, per-tag command state, and a two-interrupt DMA completion counter.

## Dependencies and Integration Points
The driver depends on OF platform probing, DMAEngine slave channels named `sata-dma`, optional old DW DMA glue, generic PHY APIs, libata SFF/BMDMA callbacks, SATA SCR access, tracepoints, and hardreset helpers. It sets `ATA_FLAG_SATA | ATA_FLAG_NCQ` but the SCSI template notes queue depth is effectively constrained because NCQ handling is not fully correct.

## Risks and Test Signals
Risks include fragile two-interrupt DMA completion accounting, NCQ tag-mask races, stale `active_tag` updates, missing cleanup when `phy_power_on()` succeeds but later paths fail, old-DMA versus DMAEngine differences, and error interrupts that always map to host-bus reset. Tests should cover non-NCQ DMA and PIO, NCQ with queue depth one and stress attempts above one, DMA callback/IRQ ordering permutations, SError injection, hardreset register reinitialization, PHY init/power/remove paths, missing DMA channel probe failure, and 8K DMA boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_dwc_460ex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_fsl.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_fsl.c

## Purpose
`sata_fsl.c` drives Freescale/PQ 3.0 Gbps SATA controllers. It implements a one-port-per-controller queued command engine with command headers/descriptors, NCQ, PMP, asynchronous notification, sysfs interrupt coalescing and RX watermark controls, and controller-specific hard/soft reset flows.

## Important APIs, Types, and Functions
Important structures are `struct cmdhdr_tbl_entry`, `struct command_desc`, `struct prde`, `struct sata_fsl_port_priv`, and `struct sata_fsl_host_priv`. Main functions include `fsl_sata_set_irq_coalescing()`, sysfs show/store methods, `sata_fsl_setup_cmd_hdr_entry()`, `sata_fsl_fill_sg()`, `sata_fsl_qc_prep()`, `sata_fsl_qc_issue()`, `sata_fsl_qc_fill_rtf()`, `sata_fsl_scr_read/write()`, `sata_fsl_freeze/thaw()`, `sata_fsl_port_start/stop()`, `sata_fsl_hardreset()`, `sata_fsl_softreset()`, `sata_fsl_error_intr()`, `sata_fsl_host_intr()`, `sata_fsl_interrupt()`, `sata_fsl_init_controller()`, and `sata_fsl_probe()`.

## Control Flow, State, and Persistence
Probe maps controller registers, derives SSR/CSR bases, configures RX watermark for non-MPC8315 variants, allocates host private data, obtains IRQ and data-snoop mode, initializes the controller offline with interrupts masked, activates libata, and creates `intr_coalescing` and `rx_watermark` sysfs files. Port start allocates coherent command-slot and command-descriptor memory, writes CHBA, and brings the controller online with PHY reset. `qc_prep` converts taskfiles to CFIS, copies ATAPI CDBs, builds PRDTs including one indirect extension segment when direct entries overflow, and writes command headers. `qc_issue` writes PMP target and queues the tag in `CQ`. Completion reads `CC`, clears completed bits, and calls `ata_qc_complete_multiple()`; error paths classify fatal, PHYRDY, SNotification, and per-device errors before freezing or aborting links.

## Dependencies and Integration Points
The driver depends on OF platform resources, libata PMP/NCQ infrastructure, coherent DMA memory, sysfs device attributes, controller-specific HCR/SSR/CSR registers, `sata_pmp_error_handler()`, and ATA reset helpers. It exposes module parameters for interrupt coalescing defaults and persists user-tuned coalescing/watermark values in hardware registers until reconfigured.

## Risks and Test Signals
Risks include command-tag reuse if `CQ` state and libata tags diverge, PRD indirect-chain mistakes, sysfs cleanup gaps after partial probe failure, PMP error attribution, hardreset timing assumptions, and data-length mismatch errata masking real ATAPI errors. Tests should cover NCQ queue depth 16, PMP attach/detach and per-link errors, ATAPI commands including length mismatch workaround, sysfs read/write validation, interrupt coalescing thresholds, hardreset/softreset with and without signature update, suspend/resume CHBA restoration, SG lists crossing direct-entry limits, and fatal/PHYRDY/SNotification interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_fsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.c

## Purpose
`sata_gemini.c` controls the Cortina Systems Gemini SATA bridge that connects SATA adapters to Faraday FTIDE010 ATA controllers. It is not a libata host driver itself; it is a platform bridge driver exporting helper APIs used by the Gemini FTIDE010 path.

## Important APIs, Types, and Functions
The key state container is `struct sata_gemini`, holding device, MMIO base, mux mode, feature booleans, and SATA0/SATA1 PCLK handles. Exported APIs are `gemini_sata_bridge_get()`, `gemini_sata_bridge_enabled()`, `gemini_sata_get_muxmode()`, `gemini_sata_start_bridge()`, and `gemini_sata_stop_bridge()`. Probe helpers include `gemini_sata_setup_bridge()`, `gemini_sata_bridge_init()`, `gemini_setup_ide_pins()`, `gemini_sata_probe()`, and `gemini_sata_remove()`.

## Control Flow, State, and Persistence
Probe allocates singleton state, maps bridge registers, obtains the global syscon, optionally initializes SATA bridge clocks and reads bridge IDs, optionally enables IDE pins, validates and stores the DT mux mode, writes global IDE mux bits through regmap, selects the IDE pinctrl state when requested, sets platform drvdata, and publishes `sg_singleton`. Starting a bridge enables its PCLK, waits, programs SATA0/1 control bits including slave mode for mux modes 2 or 3, waits up to one second for PHY-ready status, and disables the clock again on failure. Stop disables the selected bridge clock.

## Dependencies and Integration Points
The file depends on platform/OF properties, syscon regmap, common clock framework, pinctrl, MMIO register access, and exported GPL symbols consumed by the Gemini ATA host driver. Device-tree properties include `cortina,gemini-enable-sata-bridge`, `cortina,gemini-enable-ide-pins`, and `cortina,gemini-ata-muxmode`.

## Risks and Test Signals
Risks include singleton ordering causing `-EPROBE_DEFER` loops, mux modes disconnecting an ATA controller from SATA unexpectedly, clock prepare/enable imbalance, missing cleanup if IDE pin selection fails after clocks are prepared, and no explicit bridge disable register write on stop. Tests should cover all four mux modes, SATA-only, IDE-only, and mixed configurations, deferred consumers before bridge probe, PHY-ready timeout, clock failure paths, remove/unprepare behavior, and DT validation for missing syscon or illegal mux mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.h -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.h

## Purpose
`sata_gemini.h` declares the public bridge interface for Gemini SATA support. It lets other ATA code hold an opaque `struct sata_gemini *`, query mux/enable state, and start or stop a selected bridge.

## Important APIs, Types, and Functions
The header forward-declares `struct sata_gemini`, defines `enum gemini_muxmode` values `GEMINI_MUXMODE_0` through `GEMINI_MUXMODE_3`, and declares `gemini_sata_bridge_get()`, `gemini_sata_bridge_enabled()`, `gemini_sata_get_muxmode()`, `gemini_sata_start_bridge()`, and `gemini_sata_stop_bridge()`.

## Control Flow, State, and Persistence
This header has no runtime flow or storage itself. Its declarations represent bridge state owned by `sata_gemini.c`; callers receive an opaque pointer, query whether a given ATA controller is bridged to SATA, and bracket hardware use with start/stop calls.

## Dependencies and Integration Points
The declarations are shared between the Gemini bridge platform driver and ATA host drivers that need to coordinate muxing and bridge clocks. The header uses standard kernel C types such as `bool`, relying on includers to have basic type definitions available.

## Risks and Test Signals
Risks include callers treating the opaque pointer as always available instead of handling `ERR_PTR(-EPROBE_DEFER)`, mismatching bridge indexes with mux mode semantics, and forgetting to stop a bridge after start. Build coverage should include both the bridge driver and its consumers; runtime tests should validate all exported symbol users handle absent or deferred bridge state and correctly honor mux-mode enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_highbank.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_highbank.c

## Purpose
`sata_highbank.c` is the Calxeda Highbank AHCI platform driver. It extends generic AHCI with Calxeda combo-PHY lane programming, repeated hardreset workarounds for flaky Gen3 link bring-up, and SGPIO enclosure LED message bit-banging.

## Important APIs, Types, and Functions
Important types are `struct phy_lane_info` and `struct ecx_plat_data`. SGPIO helpers include `ecx_parse_sgpio()`, `ecx_led_cycle_clock()`, `ecx_transmit_led_message()`, and `highbank_set_em_messages()`. PHY helpers include combo-PHY read/write routines, `highbank_cphy_disable_overrides()`, `cphy_override_tx_attenuation()`, `cphy_override_rx_mode()`, `highbank_cphy_override_lane()`, and `highbank_initialize_phys()`. AHCI integration centers on `ahci_highbank_hardreset()`, `ahci_highbank_probe()`, suspend/resume, and `ahci_highbank_ops`.

## Control Flow, State, and Persistence
Probe obtains memory and IRQ resources, allocates AHCI and Calxeda private data, maps MMIO, initializes PHY lane mapping from `calxeda,port-phys`, saves AHCI config, enables NCQ/PMP flags based on controller caps, sets up SGPIO LED support, allocates ports, marks disabled ports dummy, resets and initializes AHCI, and activates the host. Hardreset stops the AHCI engine, clears D2H FIS state, repeatedly disables PHY overrides, performs SATA hardreset, reapplies lane overrides, and retries up to 100 times when presence is detected but the link is not online. LED messages update a cached SGPIO bit pattern and bit-bang clock/load/data GPIO lines under a spinlock.

## Dependencies and Integration Points
The driver depends on generic AHCI internals, OF properties for PHY lane and LED ordering, GPIO descriptors for SGPIO, platform resources, global static PHY/SGPIO locks, and libata enclosure management flags. It uses `ahci_host_activate()` and overrides only hardreset and LED message transmission relative to generic AHCI.

## Risks and Test Signals
Risks include global `port_data` lifetime across multiple instances, unbounded-looking busy waits if PHY registers never clear, PHY phandle mapping leaks or partial setup, SGPIO GPIO acquisition failures that still leave LED flags enabled, hardreset retry latency, and suspend refusal when AHCI flags disallow it. Tests should cover multi-port AHCI activation, disabled port maps, Calxeda PHY DT parsing, Gen3 hardreset retries, SGPIO LED activity/locate/fault states and port ordering, suspend/resume, NCQ/PMP capability flags, and error paths for missing GPIO or PHY mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_highbank.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_inic162x.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_inic162x.c

## Purpose
`sata_inic162x.c` drives Initio 162x SATA controllers using their IDMA packet engine. The file explicitly warns that the driver has common data-corruption issues and should not be used in production; nevertheless it implements two-port SATA, DMA-assisted PIO/ATAPI handling, custom hardreset, and error recovery.

## Important APIs, Types, and Functions
Important packet types are `struct inic_cpb`, `struct inic_prd`, `struct inic_pkt`, `struct inic_host_priv`, and `struct inic_port_priv`. Core functions include `inic_port_base()`, `inic_reset_port()`, `inic_scr_read/write()`, `inic_stop_idma()`, `inic_host_err_intr()`, `inic_host_intr()`, `inic_interrupt()`, `inic_check_atapi_dma()`, `inic_fill_sg()`, `inic_qc_prep()`, `inic_qc_issue()`, `inic_tf_read()`, `inic_qc_fill_rtf()`, `inic_freeze/thaw()`, `inic_hardreset()`, `inic_error_handler()`, `init_port()`, `inic_port_start()`, `init_controller()`, resume support, and `inic_init_one()`.

## Control Flow, State, and Persistence
Probe prints a corruption warning, allocates a two-port host and private state, enables PCI, selects PCI BAR 5 or CardBus BAR 1, maps MMIO, caches `HOST_CTL`, describes port windows, sets a 32-bit DMA mask, resets the controller, unmasks global port IRQs, sets bus master, and activates libata. Port start allocates coherent `inic_pkt` and CPB lookup table memory, stores addresses in controller registers, and keeps them in `ap->private_data`. `qc_prep` clears and fills the CPB, copies taskfile/LBA48 fields, builds an ATAPI CDB PRD when needed, fills data PRDs, and points CPB table entry 0 at the packet. `qc_issue` starts IDMA by writing host and port control registers and queuing the CPB FIFO. Interrupts dispatch by port, clear IRQ status, inspect IDMA status and CPB response flags, complete successful commands, or freeze/abort on hotplug, PCI, CPB, ATA, spurious, or data over/underflow errors.

## Dependencies and Integration Points
The driver depends on PCI managed MMIO mapping, coherent DMA allocations, libata SATA port ops, SCSI host limits, custom SCR mapping, hardreset via controller IDMA reset rather than standard SControl/SRST signatures, and generic PCI suspend/resume helpers. It constrains DMA boundary and maximum segment size to avoid known hard lockups.

## Risks and Test Signals
Risks are unusually high: documented data corruption, bogus result taskfile sector data, IDMA lockups on 64 KiB PRDs, ATAPI DMA limitations, fragile CPB response interpretation, and controller-specific reset requirements. Tests should be limited to non-production media and include read/write verify under SG boundary stress, LBA48, ATAPI read versus write filtering, hotplug/offline/online interrupts, CPB error injection, hardreset classification, suspend/resume controller reinit, CardBus versus PCI BAR selection, and confirmation that the boot warning remains visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_inic162x.c -->
