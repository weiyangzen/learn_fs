# subset-b-001043 research

Grouped research for selected `drivers/ata`, `drivers/atm`, and `drivers/auxdisplay` source files. Each source file section preserves its source path and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_rcar.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_rcar.c

## Purpose

This is the Renesas R-Car SATA low-level libata driver for OF/platform-attached R-Car SATA IP. It binds `renesas,*sata*` compatible strings, maps the controller MMIO block, initializes generation-specific PHY/register state, exposes one SATA port to libata, and implements the controller-specific SFF/BMDMA taskfile, SCR, interrupt, and PM operations.

## Important APIs, types, and functions

Key state is `enum sata_rcar_type` and `struct sata_rcar_priv`, which carries the MMIO base, interrupt mask, and SoC generation. `sata_rcar_probe()` allocates the host, enables runtime PM, maps resources, calls `sata_rcar_setup_port()` and `sata_rcar_init_controller()`, then activates libata with `sata_rcar_interrupt()`. PHY setup is split into `sata_rcar_gen1_phy_preinit()`, `sata_rcar_gen1_phy_write()`, `sata_rcar_gen1_phy_init()`, and `sata_rcar_gen2_phy_init()`. The libata operations table overrides freeze/thaw, soft reset, SCR read/write, SFF taskfile helpers, PIO data transfer, FIFO drain, DMA PRD preparation, and BMDMA setup/start/stop/status.

## Control flow

Probe gets the IRQ, allocates `sata_rcar_priv`, gets runtime PM, maps BAR-like platform memory, then configures the single `ata_port`. Controller initialization selects the PHY sequence by generation, programs ATAPI/SATA control registers, masks and enables interrupts, and hands the host to `ata_host_activate()`. Command flow uses taskfile writes through 32-bit MMIO registers, builds a PRD table with a controller-specific `SATA_RCAR_DTEND` bit, writes the PRD DMA address, programs direction in `ATAPI_CONTROL1_REG`, issues the ATA command, then starts DMA. Interrupt flow reads `SATAINTSTAT_REG`, acks matching bits, dispatches ATA completion to `ata_bmdma_port_intr()`, and handles SError/hotplug through libata EH freeze or abort.

## State and persistence behavior

Runtime state is purely volatile: MMIO register contents, libata host/port state, runtime-PM references, and the private interrupt mask. Suspend disables interrupts and drops runtime PM; resume or restore reinitializes controller state, with restore rebuilding port addresses first. No persistent storage is written.

## Dependencies and integration points

The file depends on platform devices, OF match data, devm allocation/ioremap, runtime PM, Linux libata SFF/BMDMA helpers, IRQ handling, and ATA EH. Integration points are the DT compatibles, the SCSI host template `sata_rcar_sht`, `ata_host_activate()`, and the libata PM callbacks.

## Risks

The driver depends on exact MMIO ordering and posted-write flushes around resets, DMA starts, and interrupt masks. The PRD code truncates DMA addresses to 32 bits and relies on the advertised DMA mask/boundary matching the hardware. Hotplug/SERR handling freezes based on SError bits; missed ack/mask ordering can cause interrupt storms or lost EH events. The source also contains a duplicated function parameter in `sata_rcar_tf_load()` in the viewed file, which would be a build-stopping syntax risk if present in the active compilation unit.

## Test signals

Build with the R-Car SATA config enabled, boot DT systems for gen1/gen2/gen3 compatibles, run SATA identify and filesystem I/O with PIO and DMA, exercise suspend/resume/restore, hotplug/link reset, and libata EH injection. Useful diagnostics are `ata_port_dbg()` messages for SError/FIFO drain, IRQ counters, dmesg link-state changes, and DMA stress across boundary-sized scatterlists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_rcar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sil.c

## Purpose

This is the libata PCI driver for first-generation Silicon Image SiI 3112/3512/3114 SATA controllers and ATI-branded variants. It maps the controller MMIO BAR, configures two or four SFF/BMDMA ports, applies device/controller errata, handles SATA IRQ quirks, and exposes the devices as SCSI disks through libata.

## Important APIs, types, and functions

The PCI binding is `sil_pci_driver` with `sil_pci_tbl`. `sil_port_info[]` selects flags for 3112, 3512, and 3114 boards, including `SIL_FLAG_NO_SATA_IRQ`, `SIL_FLAG_RERR_ON_DMA_ACT`, and `SIL_FLAG_MOD15WRITE`. `sil_ops` customizes device config, mode programming, DMA setup/start/stop, PRD preparation, freeze/thaw, and SCR access. Important helpers are `sil_fill_sg()`, `sil_set_mode()`, `sil_host_intr()`, `sil_interrupt()`, `sil_dev_config()`, `sil_init_controller()`, `sil_broken_system_poweroff()`, and `sil_init_one()`.

## Control flow

Probe determines port count, applies a DMI poweroff spindown quirk, allocates an ata host, enables and maps BAR5, sets a 32-bit ATA DMA mask, initializes per-port taskfile/BMDMA/SCR addresses from `sil_port[]`, initializes FIFO arbitration and errata bits, then activates the host with `sil_interrupt()`. Command flow uses normal SFF taskfile helpers but uses the second BMDMA register for Large Block Transfer start/stop. Interrupt handling scans every port's `bmdma2` register for DMA completion or SATA IRQ, clears SError immediately on affected chips, validates HSM state, stops DMA on completion, acknowledges BMDMA IRQs, and advances libata HSM.

## State and persistence behavior

State is PCI config/MMIO programming, per-port libata state, global module parameter `slow_down`, and detected drive quirks. It does not persist on disk. Resume calls `ata_pci_device_do_resume()`, re-runs controller initialization, and resumes the ata host.

## Dependencies and integration points

The driver integrates with PCI managed resource helpers, DMI matching, libata BMDMA32/SFF support, SCSI host exposure, and the kernel PCI PM path. Device-specific errata are keyed from IDENTIFY model strings and DMI data.

## Risks

The driver has several hardware errata paths: SATA IRQ masking may not work on some 3112s, R_ERR-on-DMA-activate requires SFIS config changes, Seagate mod15 write workarounds cap requests to 15 sectors, and Maxtor quirks limit UDMA. DMA descriptors truncate to 32-bit addresses. Freeze/thaw must coordinate SIEN, global interrupt mask, DMA enable, and taskfile accessibility. The viewed source contains a stray duplicated comment terminator near `sil_freeze()`, a potential compile risk if not removed in the actual build input.

## Test signals

Build with SiI SATA enabled, enumerate 2-port and 4-port controllers, run DMA read/write stress including large requests, verify Seagate/Maxtor quirk messages with matching model strings, test suspend/resume, SATA link change handling, and DMI spindown behavior. Watch for spurious IRQ rate limiting, HSM errors, and SError clear/freeze paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil24.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sil24.c

## Purpose

This is the libata PCI driver for Silicon Image 3124/3132/3131/3531 SATA-II controllers. Unlike classic SFF controllers, it uses PRB/SGE command blocks, 64-bit command activation registers, NCQ, port multipliers, asynchronous notification, and controller-specific error classification.

## Important APIs, types, and functions

The file defines hardware command structures `struct sil24_prb`, `struct sil24_sge`, `struct sil24_ata_block`, `struct sil24_atapi_block`, `union sil24_cmd_block`, and `struct sil24_port_priv`. `sil24_ops` supplies queue defer, prep, issue, result taskfile fill, reset, PMP attach/detach, freeze/thaw, error handling, internal command cleanup, port start, SCR access, and PM resume callbacks. The central functions are `sil24_qc_defer()`, `sil24_qc_prep()`, `sil24_qc_issue()`, `sil24_error_intr()`, `sil24_host_intr()`, `sil24_interrupt()`, `sil24_init_port()`, `sil24_softreset()`, `sil24_hardreset()`, `sil24_port_start()`, `sil24_init_controller()`, and `sil24_init_one()`.

## Control flow

Probe maps host BAR0 and port BAR2, applies PCI-X completion-IRQ workaround detection, allocates one to four ports from encoded flags, sets a 64-bit DMA mask, optionally enables MSI, initializes ports, and activates the host. Each port start allocates a page-sized coherent command block array for 31 tags. Queue prep fills a PRB FIS and SGEs, with ATAPI CDB storage in a separate layout; issue writes the command block DMA address to the tag's activation register. Interrupts read global host status, dispatch per-port status, complete multiple tags from `PORT_SLOT_STAT`, or analyze attention/error status through command error lookup and libata EH actions.

## State and persistence behavior

Per-port private state tracks the coherent command block DMA base and whether a full port reset is needed. PMP attachment temporarily toggles port-multiplier enable and may disable NCQ for a Marvell 4140 quirk. The module parameter `msi` controls MSI use. All state is runtime-only and is rebuilt on probe/resume.

## Dependencies and integration points

The driver depends on PCI, DMA mapping, libata NCQ/PMP helpers, SCSI queue-depth plumbing, IRQ handling, and optional PM. It exposes NCQ queue-depth controls through the SCSI host template and integrates with SATA PMP error handling through `sata_pmp_error_handler()`.

## Risks

The command block layout must remain exactly page-sized and hardware-aligned. `sil24_qc_defer()` serializes ATAPI/result-taskfile commands to avoid an LRAM read corruption erratum. PMP mode has a DMA context-switch erratum when three or more links are active, forcing reset. Error decoding must map `PORT_CMD_ERR` precisely; unknown or protocol errors freeze/reset. The source duplicates the `SIL24_FLAG_PCIX_IRQ_WOC` enum line in the viewed file, which is another build-surface risk if not preprocessed away.

## Test signals

Build and boot on 3124/3132/3131 variants, run NCQ queue-depth stress, ATAPI packet commands, passthrough commands needing result taskfiles, PMP attach/detach with multiple disks, MSI and INTx modes, suspend/resume, and injected command errors. Expected signals include correct multi-tag completion, reset after injected protocol/PCI errors, no LRAM corruption under exclusive commands, and stable PMP notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sis.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sis.c

## Purpose

This is the libata PCI driver for SiS 180/181/182/965/966/968/680 SATA controllers. It handles controllers that expose SATA SCRs either through PCI config space or IO-mapped BAR5, and it coordinates with `pata_sis` for combined PATA/SATA operating modes.

## Important APIs, types, and functions

The public binding is `sis_pci_driver`; supported IDs are in `sis_pci_tbl`. `sis_port_info` and `sis_ops` provide the base BMDMA SATA port description plus SCR hooks. `get_scr_cfg_addr()` calculates PCI config SCR offsets by port, device ID, PMP index, and combined-mode register state. `sis_scr_read()` and `sis_scr_write()` dispatch to PCI config helpers or MMIO. `sis_init_one()` is the main probe/configuration path.

## Control flow

Probe enables the PCI device, checks `SIS_GENCTL` to decide whether SCRs are IO mapped, forces config-space SCR mode if BAR5 is absent or too small, reads `SIS_PMR`, and selects pure SATA, combined mode, or PATA-backed port info. It prepares a BMDMA ata host, initializes slave links when the SATA mode supports master/slave slots, maps BAR5 if needed, assigns per-port SCR bases, enables bus mastering and INTx, then activates the host with the generic BMDMA interrupt handler.

## State and persistence behavior

State is PCI config bits, selected port flags, SCR address mappings, and libata port state. There is no persistent storage. PM uses generic `ata_pci_device_suspend()` and `ata_pci_device_resume()`.

## Dependencies and integration points

The driver depends on PCI config access, managed PCI BMDMA preparation, libata BMDMA helpers, and `sis_info133_for_sata` declared in `sis.h` and implemented by `pata_sis.c` for PATA-mode ports.

## Risks

SCR_ERROR is unavailable in PCI config SCR mode and returns `-EINVAL`; callers must tolerate that. Combined mode changes port layout and may expose slave devices, so incorrect PMR interpretation can hide devices or select the wrong `ata_port_info`. Changing `GENCTL_IOMAPPED_SCR` on broken BAR layouts is necessary but risky if firmware/hardware assumptions differ.

## Test signals

Compile with both SATA SiS and PATA SiS support, boot SiS 180/182/1182/1183 variants, test pure SATA and combined modes, verify SCR reads in both config and IO-mapped modes, run libata reset/EH, and test suspend/resume. Detection messages in dmesg should match chipset mode and port visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_svw.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_svw.c

## Purpose

This is the ServerWorks/Broadcom/Apple K2 libata SATA driver. It supports four- and eight-port MMIO controllers, maps taskfile/BMDMA/SCR registers with a fixed stride, works around DMA command ordering issues, and provides OF-derived port information on Apple systems.

## Important APIs, types, and functions

Hardware variants are selected by `k2_sata_pci_tbl` and `k2_port_info[]`. `k2_sata_ops` overrides soft/hard reset, taskfile load/read, status read, ATAPI DMA filtering, BMDMA setup/start, and SCR access. Important functions are `k2_sata_check_atapi_dma()`, `k2_sata_softreset()`, `k2_sata_hardreset()`, `k2_sata_tf_load()`, `k2_sata_tf_read()`, `k2_bmdma_setup_mmio()`, `k2_bmdma_start_mmio()`, `k2_sata_show_info()`, `k2_sata_setup_port()`, and `k2_sata_init_one()`.

## Control flow

Probe chooses four or eight ports and BAR position, enables PCI, rejects disabled functions with no BAR length, maps the MMIO BAR, assigns per-port taskfile/BMDMA/SCR addresses, sets a 32-bit ATA DMA mask, clears a Darwin-observed SICR1 bit, clears SATA error state, masks unused SATA interrupts, then activates with `ata_bmdma_interrupt()`. DMA setup writes the PRD address and direction. For ATA DMA, `k2_bmdma_start_mmio()` starts host DMA before issuing the ATA command, avoiding a documented data-corruption window where fast drives return data before the controller sees DMA start.

## State and persistence behavior

State is MMIO controller state, port flags such as `K2_FLAG_NO_ATAPI_DMA`, and live libata state. OF show-info lookup reads device-tree children for diagnostics only. No on-disk persistence exists.

## Dependencies and integration points

The driver depends on PCI, MMIO libata BMDMA helpers, SCSI command opcodes for ATAPI DMA filtering, and Open Firmware node helpers for `show_info`.

## Risks

The ATA DMA ordering workaround is essential for data integrity; changing command issue order can corrupt reads. ATAPI DMA is blocked on some variants and whitelisted only for read/write packet commands on others. Missing BAR resources can reflect firmware-disabled functions and must not be treated as normal mapped ports.

## Test signals

Run build/boot on Apple K2, Frodo, and BCM5785-like controllers, four/eight-port enumeration, DMA read stress with fast disks, ATAPI DMA command coverage, reset while DMA active, and OF show-info output. Monitor for BMDMA lost interrupts, data checksum errors, and link reset stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_svw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sx4.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sx4.c

## Purpose

This is the Promise PDC20621/FastTrak S150 SX4 libata driver. The controller uses local DIMM memory and a single host-DMA copy engine; the driver stages disk data through DIMM, submits controller packet programs, initializes SDRAM over I2C/SPD, and multiplexes the HDMA engine across four SATA ports.

## Important APIs, types, and functions

Key state is `struct pdc_port_priv` with DIMM packet buffers and coherent packet DMA, and `struct pdc_host_priv` with the HDMA active flag and ring queue. `pdc_20621_ops` supplies custom queue prep/issue, reset/EH, freeze/thaw, port start, taskfile command wrappers, and IRQ clear. Core helpers include `pdc20621_dma_prep()`, `pdc20621_nodata_prep()`, `pdc20621_packet_start()`, `pdc20621_push_hdma()`, `pdc20621_pop_hdma()`, `pdc20621_host_intr()`, `pdc20621_interrupt()`, DIMM window helpers, I2C SPD reads, DIMM programming, ECC clearing, `pdc_20621_init()`, and `pdc_sata_init_one()`.

## Control flow

Probe maps MMIO BAR3 and DIMM BAR4, assigns four port taskfile windows, sets a 32-bit ATA DMA mask, initializes DIMM timing/ECC using SPD, resets HDMA, then activates with a custom IRQ handler. DMA prep builds host and ATA packets plus PRD tables in a per-port DIMM window. Writes run host-to-DIMM HDMA first, then ATA write from DIMM; reads run ATA read into DIMM first, then DIMM-to-host HDMA. The interrupt handler reads sequence-mask bits, maps sequence IDs back to ports and HDMA/ATA phases, completes or schedules the next phase, and advances the single HDMA queue.

## State and persistence behavior

Runtime state includes local DIMM contents, HDMA queue producer/consumer counters, in-flight queued commands, MMIO sequence masks, and optional module parameter `dimm_test`. No filesystem persistence occurs, but the driver programs volatile SDRAM/PLL/controller registers at probe.

## Dependencies and integration points

The driver depends on PCI, libata SFF command helpers, Promise packet helper definitions in `sata_promise.h`, DMA mapping, I2C-over-controller SPD access, kernel delay/sleep APIs, and SCSI opcode checks for ATAPI DMA policy.

## Risks

This driver has high state complexity: a single HDMA engine is shared by all ports, and read/write completion alternates between ATA and HDMA phases. Queue corruption or missed sequence bits can deadlock I/O. DIMM SPD parsing and ECC initialization are hardware-sensitive. Several comments still mark HDMA reset/freeze gaps as FIXME. Because ATAPI is mostly disabled and PIO polling is used, changing feature flags can expose untested paths.

## Test signals

Probe with real SX4 hardware and DIMMs of different sizes/speeds, enable `dimm_test`, run parallel four-port DMA read/write stress with data verification, inject errors during each HDMA/ATA phase, run reset/EH while HDMA is queued, and watch sequence-mask, HDMA dump, and DIMM initialization dmesg output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sx4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_uli.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_uli.c

## Purpose

This is the libata PCI driver for ULi/ALi M5289, M5287, and M5281 SATA controllers. It mostly relies on generic SFF/BMDMA setup, with controller-specific mapping for SATA SCR registers in PCI config space and extra port address setup for four-port M5287 hardware.

## Important APIs, types, and functions

`struct uli_priv` stores per-port SCR config-space base offsets. `uli_ops` inherits `ata_bmdma_port_ops`, supplies `uli_scr_read()`/`uli_scr_write()`, and disables hardreset with `ATA_OP_NULL`. `uli_init_one()` chooses two or four ports, initializes generic PCI SFF/BMDMA host state, patches ports 2/3 for M5287, fills SCR bases, and activates the host.

## Control flow

Probe enables PCI, determines port count from `ent->driver_data`, allocates an ata host and private SCR map, initializes the first two ports with generic SFF helpers, initializes BMDMA, then fills variant-specific SCR config offsets. For M5287, ports 2 and 3 are derived from standard BARs with offset taskfile and BMDMA windows. SCR access simply calculates `scr_cfg_addr[port] + sc_reg * 4` and reads/writes PCI config dwords.

## State and persistence behavior

State is limited to the private SCR base array, PCI config registers, and libata host state. There is no persistent state and no custom PM implementation.

## Dependencies and integration points

The file depends on PCI, generic libata SFF/BMDMA host initialization, PCI config access, and managed resource mappings from `ata_pci_sff_init_host()`.

## Risks

The driver suppresses hard reset, so recovery depends on soft/SFF paths. M5287 port 2/3 address derivation is manually encoded and easy to regress; one `ata_port_desc()` call describes `host->ports[2]` twice in the viewed source, likely a diagnostic copy/paste issue. SCR access only supports status/error/control and assumes correct config-space base offsets.

## Test signals

Build and boot each ULi variant, verify two- vs four-port enumeration, SCR read/write through libata link status, BMDMA interrupt I/O, soft reset/EH behavior without hardreset, and port 2/3 resource descriptions on M5287.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_uli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_via.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_via.c

## Purpose

This is the libata PCI driver for VIA VT6420, VT6421, and VT8251 SATA/PATA controllers. It handles multiple register layouts, optional VT6420 hotplug, VT6421 mixed SATA/PATA ports, VT8251 master/slave SATA slots, and known VIA/drive FIFO workarounds.

## Important APIs, types, and functions

`struct svia_priv` records whether the WD FIFO watermark workaround is active. Port operations are split across `svia_base_ops`, `vt6420_sata_ops`, `vt6421_pata_ops`, `vt6421_sata_ops`, and `vt8251_ops`. Important helpers include `svia_scr_read/write()`, `vt8251_scr_read/write()`, `svia_tf_load()`, `svia_noop_freeze()`, `vt6420_prereset()`, `vt6420_bmdma_start()`, VT6421 PATA mode/cable helpers, `vt642x_interrupt()`, `vt6421_error_handler()`, `svia_configure()`, and the three prepare-host functions.

## Control flow

Probe validates BAR sizes, selects a host-preparation path by board ID, allocates `svia_priv`, programs channel enable, interrupt gate, native mode, hotplug, and FIFO workaround bits, then activates with either generic BMDMA IRQ handling or `vt642x_interrupt()` for hotplug-capable paths. VT6420 carefully restricts SCR access to a boot-time prereset sequence to avoid hangs. VT6421 maps two SATA ports and one PATA port from six BARs. VT8251 exposes two channels with slave links and reads SCRs from packed PCI config bytes/dwords.

## State and persistence behavior

Runtime state is PCI config programming, optional module parameter `vt6420_hotplug`, private WD workaround state, and libata port/link state. Resume reapplies the WD workaround when it had been enabled. There is no durable state.

## Dependencies and integration points

The file depends on PCI config access, generic libata BMDMA/SFF helpers, SCSI command metadata for ATAPI DMA workaround, and `linux/string_choices.h` for link-state messages. It integrates mixed PATA/SATA ports under one PCI driver.

## Risks

VT6420 SCR access can hang hardware if used outside the safe sequence; enabling hotplug mutates the shared operations table and should be treated carefully. VT6421 WD-drive errors enable a throughput-reducing FIFO workaround after detecting a specific SError. Interrupt handling reads SError for hotplug only after generic BMDMA returns unhandled. PCI BAR validation is strict and can reject odd firmware layouts.

## Test signals

Exercise all board IDs, VT6420 with and without `vt6420_hotplug`, VT6421 SATA plus PATA timing/cable detection, VT8251 slave-link enumeration, suspend/resume with workaround state, ATAPI burner DMA writes, and hotplug PHYRDY events. Expected signals include safe VT6420 probing, correct link-up/down dmesg, and no machine hangs from SCR access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_via.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_vsc.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_vsc.c

## Purpose

This is the libata PCI driver for Vitesse VSC7174 and compatible Intel 31244 DPA SATA controllers. It maps one MMIO BAR, exposes four SATA ports, customizes taskfile and interrupt handling, optionally enables MSI, and works around cache-line and LED-control hardware behavior.

## Important APIs, types, and functions

`vsc_sata_ops` inherits BMDMA operations but overrides lost-interrupt handling, taskfile load/read, freeze/thaw, and SCR access. Important functions are `vsc_sata_tf_load()`, `vsc_sata_tf_read()`, `vsc_intr_mask_update()`, `vsc_error_intr()`, `vsc_port_intr()`, `vsc_sata_interrupt()`, `vsc_sata_setup_port()`, and `vsc_sata_init_one()`.

## Control flow

Probe allocates four ports, enables PCI, maps BAR0, assigns per-port taskfile/BMDMA/SCR addresses using a 0x200 stride starting at port offset 1, sets a 32-bit DMA mask, fixes a zero PCI cache-line size, enables MSI when possible, clears a shared-activity LED bit, and activates with `vsc_sata_interrupt()`. Taskfile writes use 16-bit paired address registers for LBA48. Interrupt flow reads global status, extracts one byte per port, freezes on PHY-change or major error bits, aborts on other errors, or dispatches normal BMDMA completion.

## State and persistence behavior

State is MMIO interrupt masks, PCI cache-line/LED config, MSI/INTx state, and libata runtime state. There is no persistent storage and no custom suspend/resume path.

## Dependencies and integration points

The driver depends on PCI, DMA mapping, MSI, libata BMDMA/SFF helpers, and SCSI host exposure. Device IDs match both Vitesse and Intel-compatible class/subclass encodings.

## Risks

Interrupt masking is split per port and tied to ATA_NIEN handling rather than standard SFF control writes. Lost-interrupt handling is disabled because the hardware is not standard SFF. Error-bit classification determines freeze versus abort; incorrect classification can either over-reset or miss link recovery. The 32-bit DMA mask reflects poor 64-bit support.

## Test signals

Test VSC7174/Intel 31244 enumeration, MSI fallback, per-port interrupt masking, DMA I/O, induced PHY changes, CRC/error interrupts, LBA48 taskfile correctness, and cache-line-size initialization. Dmesg should not show repeated spurious IRQ or PCI-fault status except on removal/fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_vsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sis.h -->
# sources/distributed-fs/ceph-client/drivers/ata/sis.h

## Purpose

This header is the tiny cross-driver contract between SiS SATA and PATA support. It forward-declares `struct ata_port_info` and declares `sis_info133_for_sata`, which lets `sata_sis.c` use the PATA SiS port description for combined or PATA-mode controller channels.

## Important APIs, types, and functions

There are no functions. The only exported symbol declaration is `extern const struct ata_port_info sis_info133_for_sata;`.

## Control flow

The header has no runtime control flow. It is included by `sata_sis.c` so the compiler can type-check references to the PATA port-info object provided by `pata_sis.c`.

## State and persistence behavior

No state is stored here. It only declares a const data object owned elsewhere.

## Dependencies and integration points

It depends on libata's `struct ata_port_info` type by forward declaration and integrates the SATA and PATA SiS drivers at build/link time.

## Risks

The main risk is link/config mismatch: if `sata_sis.c` references `sis_info133_for_sata` without the provider object being built or exported under compatible configs, linking fails. Changes to the type or constness must match the provider.

## Test signals

Compile configurations with SiS SATA combined/PATA support enabled and disabled, ensuring no unresolved `sis_info133_for_sata` symbol and correct mode selection in `sata_sis.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/atm/Kconfig

## Purpose

This Kconfig file defines the ATM driver submenu and the Solos ADSL2+ PCI multiport card option. It gates ATM hardware drivers behind networking and ATM core support.

## Important APIs, types, and functions

The build-facing symbols are `ATM_DRIVERS` and `ATM_SOLOS`. `ATM_DRIVERS` is a bool menu option depending on `NETDEVICES && ATM`. `ATM_SOLOS` is a tristate depending on `PCI` and selecting `FW_LOADER`.

## Control flow

Kconfig evaluates `ATM_DRIVERS` first. If disabled, the guarded submenu is skipped. If enabled with networking and ATM core support, `ATM_SOLOS` becomes available and can be built in or as a module.

## State and persistence behavior

There is no runtime state. Persistent effects are build configuration choices in `.config`, which determine object inclusion and firmware loader availability.

## Dependencies and integration points

This file integrates the Solos PCI driver with the kernel ATM stack, PCI subsystem, and firmware loading infrastructure.

## Risks

Missing `FW_LOADER` selection would break the driver's flash-upgrade firmware requests. Incorrect dependencies could expose a build without ATM core or PCI support. Since the submenu itself adds no code, tests must verify selected child symbols, not just `ATM_DRIVERS=y`.

## Test signals

Run Kconfig builds for `ATM_DRIVERS=n`, `ATM_DRIVERS=y` with `ATM_SOLOS=m/y`, and dependency-negative configs without PCI/ATM. Confirm `solos-pci.o` is linked only when `CONFIG_ATM_SOLOS` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/atm/Makefile

## Purpose

This Makefile is the Kbuild glue for ATM drivers in this directory. It conditionally builds the Solos PCI driver object when `CONFIG_ATM_SOLOS` is enabled.

## Important APIs, types, and functions

There are no runtime APIs. The only rule is `obj-$(CONFIG_ATM_SOLOS) += solos-pci.o`.

## Control flow

Kbuild expands the conditional object list during build evaluation. Disabled configs add no objects; `m` builds `solos-pci.ko`; `y` links the object into the kernel.

## State and persistence behavior

The file stores no runtime state. Its effect is the build artifact selected by `.config`.

## Dependencies and integration points

It depends on Kbuild syntax and the symbol defined in the sibling Kconfig. It integrates `solos-pci.c` into the kernel build.

## Risks

The risk surface is small: a symbol name mismatch silently omits the driver, while extra objects would alter module composition. It does not list `solos-attrlist.c` because that file is included by the C preprocessor, not compiled separately.

## Test signals

Build `CONFIG_ATM_SOLOS=m` and verify `solos-pci.ko`; build `CONFIG_ATM_SOLOS=n` and verify no Solos object is compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-attrlist.c -->
# sources/distributed-fs/ceph-client/drivers/atm/solos-attrlist.c

## Purpose

This file is an include-time attribute list for `solos-pci.c`. It enumerates Solos modem parameter names once and lets the parent source expand them first into `DEVICE_ATTR` declarations and later into an attribute pointer array.

## Important APIs, types, and functions

There are no functions or standalone data definitions. The file relies on caller-defined macros `SOLOS_ATTR_RO(name)` and `SOLOS_ATTR_RW(name)`. Read-only attributes include version, status, bitrate, line quality, vendor, error, and counter fields. Read-write attributes include `Action`, `ActivateLine`, `HostControl`, `AutoStart`, `Failsafe`, `ShowtimeLed`, `Retrain`, `Defaults`, line/profile settings, noise detection, and SNR/margin controls.

## Control flow

The C preprocessor includes this file twice from `solos-pci.c`: once to emit `static DEVICE_ATTR(...)` objects and once to populate `solos_attrs[]`. At runtime all attributes share `solos_param_show()` and optional `solos_param_store()`, which send command packets to firmware and wait for responses.

## State and persistence behavior

The file itself stores no state. The attributes expose and mutate firmware-side modem state through command packets, so user writes may persist in device firmware depending on firmware semantics.

## Dependencies and integration points

It depends entirely on the macro context supplied by `solos-pci.c` and integrates with sysfs groups named `parameters` on each ATM device.

## Risks

Because names become sysfs ABI, renaming or changing RO/RW status can break userspace. The macro-include pattern is compact but fragile: including the file without defining the macros will not compile, and adding an attribute with invalid identifier characters is impossible through this pattern.

## Test signals

Compile `solos-pci.c`, enumerate `/sys/class/atm/*/parameters/`, confirm every listed attribute appears with expected mode, and test representative read/write commands with firmware responses `OK`, `ERROR`, timeout, and unexpected payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-attrlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-pci.c -->
# sources/distributed-fs/ceph-client/drivers/atm/solos-pci.c

## Purpose

This is the Traverse/Xrio Solos PCI ADSL2+ multiport ATM driver. It maps FPGA config/data RAM, registers one ATM device per port, moves ATM AAL5 PDUs and firmware command packets between Linux and the FPGA using MMIO or DMA, exposes modem parameters and GPIOs through sysfs, and optionally performs FPGA/firmware flash upgrades from named firmware blobs.

## Important APIs, types, and functions

Core protocol types are `struct pkt_hdr`, `struct solos_skb_cb`, `struct solos_card`, and `struct solos_param`. PCI entry points are `solos_pci_init()`, `fpga_probe()`, `fpga_remove()`, and `fpga_driver`. ATM operations are `popen()`, `pclose()`, `psend()`, and `fpga_ops`. Data path functions are `fpga_queue()`, `fpga_tx()`, `solos_irq()`, `solos_bh()`, `find_vcc()`, and `process_status()/process_command()`. Sysfs paths are `solos_param_show/store()`, `console_show/store()`, GPIO/hardware attributes, and the macro-included `solos-attrlist.c`. Firmware upgrade is handled by `flash_upgrade()`.

## Control flow

Probe allocates `solos_card`, enables PCI, sets a 32-bit DMA mask, requests BARs, maps config and data RAM, optionally resets the FPGA, reads FPGA version/port count/flash type, chooses MMIO or DMA transport, initializes locks/waitqueues/tasklet, requests IRQ, enables FPGA IRQs, optionally runs flash upgrades, then registers ATM devices. TX queues are per port: `psend()` prepends a packet header and calls `fpga_queue()`, which sets `tx_mask` and may immediately call `fpga_tx()`. `fpga_tx()` checks FPGA flags, dequeues eligible packets, copies to TX buffers or maps DMA, starts transmission, and completes old skbs. IRQs clear the FPGA IRQ register and schedule `solos_bh()` once ATM devices exist. The tasklet drains TX, receives packets, dispatches data to VCCs, status to link-state updates, and command replies to waiting sysfs callers or console queues.

## State and persistence behavior

Runtime state includes mapped FPGA registers, port count, version, flash type, per-port ATM devices, sk_buff queues, in-flight DMA skbs, bounce buffers, waitqueues, tasklet, tx masks, CLI queues, and pending parameter requests keyed by PID/port. Firmware/FPGA upgrade mode writes device flash and is the only durable behavior; normal sysfs parameter writes may also alter firmware-managed modem configuration. Remove disables IRQs, resets/releases FPGA mode, deregisters ATM devices, unmaps DMA, drains queues, unmaps BARs, and frees memory.

## Dependencies and integration points

The driver depends on PCI, ATM core, sk_buff APIs, DMA mapping, sysfs, firmware loader, waitqueues, tasklets, spinlocks, and global ATM VCC hash/list locking. It declares required firmware names and integrates with `/sys/class/atm`, PCI driver binding, and device firmware command protocols.

## Risks

Concurrency risk is high: TX queue, CLI queue, parameter queue, tasklet, IRQ, sysfs, and VCC close paths share skbs and VCC pointers. `pclose()` uses `tasklet_unlock_wait()` to avoid use-after-free after VCC close. DMA alignment requires bounce buffers. Firmware upgrade loops copy blocks to MMIO and wait on `fw_wq`; bad firmware size/block handling or timeouts can brick devices. `find_vcc()` depends on global ATM internals. The code uses fixed four-element arrays while `nr_ports` is read from hardware, so unexpected port counts would be dangerous. `print_buffer()` uses fixed stack strings and verbose debug paths that deserve care under malformed packet lengths.

## Test signals

Build `CONFIG_ATM_SOLOS`, bind supported PCI IDs, verify BAR mapping/version/port detection, ATM device registration, VCC open/close/send/receive, sysfs parameter read/write timeouts and responses, console queue limits, MMIO and DMA FPGA versions, IRQ/tasklet RX/TX paths, firmware upgrade with safe test images, hot remove, and lockdep/KASAN/KCSAN under concurrent sysfs and traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/Kconfig

## Purpose

This Kconfig file defines auxiliary display driver configuration, including character LCD cores, HD44780-compatible displays, parallel-port panel/keypad options, graphical LCD support, line-display helpers, I2C LED/display controllers, GPIO seven-segment displays, and the ARM Versatile/RealView character LCD driver.

## Important APIs, types, and functions

The central menu symbol is `AUXDISPLAY`. Important child symbols include `CHARLCD`, `HD44780_COMMON`, `HD44780`, `LCD2S`, `PARPORT_PANEL`, many `PANEL_*` tuning options, `PANEL_CHANGE_MESSAGE`, `PANEL_BOOT_MESSAGE`, backlight choice symbols, `KS0108`, `CFAG12864B`, `LINEDISP`, `IMG_ASCII_LCD`, `HT16K33`, `MAX6959`, `SEG_LED_GPIO`, `ARM_CHARLCD`, and deprecated `PANEL`.

## Control flow

Kconfig first gates the submenu on `AUXDISPLAY`. Nested `if PARPORT_PANEL` exposes detailed panel wiring options only for custom profiles. Several symbols select common cores (`CHARLCD`, `HD44780_COMMON`, `LINEDISP`) while concrete drivers add platform dependencies such as `I2C`, `FB`, `PARPORT_PC`, `GPIOLIB`, `PLAT_VERSATILE`, or `COMPILE_TEST`.

## State and persistence behavior

There is no runtime state. The persistent effect is `.config` symbol state, which controls compiled objects and built-in/module selection. Some options also become compile-time defaults for panel dimensions, pin wiring, messages, and refresh rates.

## Dependencies and integration points

This file integrates auxdisplay drivers with Kbuild, framebuffer, input, LED, backlight, regmap, GPIO, I2C, parport, platform, and MFD dependencies. It also preserves a deprecated compatibility symbol `PANEL` that selects the newer menu path.

## Risks

The main risks are dependency/selection drift and user-visible config ABI changes. Incorrect `select` relationships can build concrete drivers without their common cores. Numeric panel options are compile-time hardware ABI for legacy devices; changing defaults can break existing installations. High refresh rates for slow LCDs are explicitly risky.

## Test signals

Run allmodconfig/allyesconfig and targeted configs for each major auxdisplay driver, verify menu visibility with dependencies missing, confirm selected common objects link, and build deprecated `PANEL` configs for compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Makefile -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/Makefile

## Purpose

This Makefile maps auxdisplay Kconfig symbols to Kbuild objects. It is the build composition point for character LCDs, graphical LCDs, line displays, LED controllers, and panel drivers.

## Important APIs, types, and functions

There are no runtime APIs. Rules include `obj-$(CONFIG_ARM_CHARLCD) += arm-charlcd.o`, `CONFIG_CFAG12864B` building both core and framebuffer objects, `CONFIG_CHARLCD`, `CONFIG_HD44780_COMMON`, `CONFIG_HD44780`, `CONFIG_HT16K33`, `CONFIG_IMG_ASCII_LCD`, `CONFIG_KS0108`, `CONFIG_LCD2S`, `CONFIG_LINEDISP`, `CONFIG_MAX6959`, `CONFIG_PARPORT_PANEL`, and `CONFIG_SEG_LED_GPIO`.

## Control flow

Kbuild evaluates each `obj-*` assignment according to `.config`. Built-in values link into the kernel; module values build modules where supported.

## State and persistence behavior

No runtime state is stored. The file affects build artifacts only.

## Dependencies and integration points

It depends on symbols from the sibling Kconfig and integrates source files in `drivers/auxdisplay` into the kernel build.

## Risks

Object-name drift can silently omit a driver or break link. Multi-object entries like `cfag12864b.o cfag12864bfb.o` must stay aligned with code dependencies. Common-core objects must match Kconfig `select` relationships.

## Test signals

Build each auxdisplay symbol as module and built-in where allowed, verify expected `.o`/`.ko` outputs, and run clean rebuilds after renaming or moving driver files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/arm-charlcd.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/arm-charlcd.c

## Purpose

This is the built-in platform driver for the ARM Ltd. character LCD IP found on Versatile/RealView reference boards. It drives an HD44780-like two-line character LCD through a custom MMIO controller and displays `ARM Linux` plus the kernel release.

## Important APIs, types, and functions

`struct charlcd` stores the device pointer, mapped MMIO base, optional IRQ, completion, and delayed init work. `charlcd_interrupt()` completes command readiness. `charlcd_wait_complete_irq()`, `charlcd_4bit_read_char()`, `charlcd_4bit_read_bf()`, `charlcd_4bit_wait_busy()`, `charlcd_4bit_command()`, `charlcd_4bit_char()`, and `charlcd_4bit_print()` implement the HD44780 4-bit protocol over the controller. `charlcd_probe()` maps resources, requests IRQ if present, and schedules `charlcd_init_work()`. PM callbacks blank and restore display-on state.

## Control flow

The builtin platform driver probes compatible `arm,versatile-lcd` devices, maps the MMIO resource, optionally requests an IRQ, stores private state, and schedules delayed work to avoid slowing boot. Initialization sends the fixed HD44780 8-bit-to-4-bit sequence, configures two lines and display-on mode, clears/homes the display, then writes two lines. Busy waits use IRQ completion when available; otherwise they poll `CHAR_RAW` with short delays and clear raw status after each nibble.

## State and persistence behavior

State is only the live LCD controller registers, optional pending completion, and delayed work item. Suspend sends display-control off; resume sends display-control on. No user ABI or persistent storage is implemented.

## Dependencies and integration points

The driver depends on platform devices, OF matching, devm MMIO mapping, optional IRQs, completions, delayed work, polling helpers, generated `UTS_RELEASE`, and PM callbacks. It is built through `CONFIG_ARM_CHARLCD` and `builtin_platform_driver_probe()`.

## Risks

Timing is sensitive because HD44780 initialization cannot initially use busy-flag checks. IRQ and polling paths both manipulate `CHAR_RAW` and must not miss readiness. The probe schedules delayed work but there is no remove path because the driver suppresses bind attributes and is built-in. The viewed source is syntactically clean around the print/init boundary, but this area is structurally fragile because an extra brace would break compilation.

## Test signals

Build `CONFIG_ARM_CHARLCD` on Versatile/RealView configs, boot with and without an IRQ resource, confirm the two display lines, exercise suspend/resume, inject IRQ timeouts or missing raw-valid polling, and inspect dmesg for timeout or spurious IRQ messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/arm-charlcd.c -->
