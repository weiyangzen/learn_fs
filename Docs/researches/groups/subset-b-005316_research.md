# subset-b-005316 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_transport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_transport.c

Purpose: implements the MPT3SAS driver's Linux SAS transport binding. It translates controller-discovered SAS topology into `sas_phy`, `sas_port`, and `sas_rphy` objects, handles SMP passthrough for expanders and userspace BSG jobs, exposes link/error controls through `sas_function_template`, and keeps the driver-private `_sas_node`, `_sas_port`, `_sas_phy`, `hba_port`, and `_sas_device` state synchronized with the transport class.

Important APIs/types/functions: public entry points are `mpt3sas_transport_done()`, `mpt3sas_transport_port_add()`, `mpt3sas_transport_port_remove()`, `mpt3sas_transport_add_host_phy()`, `mpt3sas_transport_add_expander_phy()`, `mpt3sas_transport_update_links()`, `mpt3sas_transport_add_phy_to_an_existing_port()`, and `mpt3sas_transport_del_phy_from_an_existing_port()`. Internal helpers include `_transport_set_identify()` for SAS Device Page 0 conversion, `_transport_expander_report_manufacture()`, `_transport_get_expander_phy_error_log()`, `_transport_expander_phy_control()`, `_transport_phy_reset()`, `_transport_phy_enable()`, `_transport_phy_speed()`, and `_transport_smp_handler()`. The exported `mpt3sas_transport_functions` connects these operations to the SAS transport layer.

Control flow: discovery code in `mpt3sas_scsih.c` calls the add/update/remove helpers after firmware events and configuration-page reads. Port addition finds the parent host/expander node, populates remote identify data, collects matching phys, creates a transport port, adds phys, allocates the correct end-device or expander rphy, links it into the private node list, and optionally sends SMP Report Manufacturer. Link updates refresh attached handles and link rates, then add or clear phy membership. SAS transport sysfs/BSG calls enter the function template, serialize on `ioc->transport_cmds.mutex`, allocate or map DMA buffers, send firmware SMP/SAS IO Unit commands, wait up to 10 seconds, and may trigger a hard reset on timeout.

State and persistence: topology state is in-memory only and protected primarily by `sas_node_lock` and `sas_device_lock`; transport command state is a single outstanding `ioc->transport_cmds` slot completed by `mpt3sas_transport_done()`. HBA multipath state updates `hba_port` phy masks, virtual phys, and SAS addresses. Link-rate changes for host phys are written to SAS IO Unit Page 1 and can persist in adapter configuration according to firmware behavior; most transport objects are runtime representations rebuilt by discovery.

Dependencies and integration points: depends on SCSI midlayer, SAS transport class, BSG, PCI DMA APIs, MPT3SAS firmware configuration helpers, and internal device/expander lookup and removal routines. `mpt3sas_scsih.c` attaches `mpt3sas_transport_template` to each Scsi_Host and invokes these APIs during discovery, reset recovery, device removal, and event processing.

Risks and test signals: the single transport command slot means concurrent SMP/link-control users must serialize correctly. Several timeout paths issue a forced hard reset, so tests should cover completion, timeout, and `MPT3_CMD_RESET` races. Port removal and multipath/vSES cleanup are list-heavy and sensitive to lock ordering. `_transport_expander_phy_control()` sets `RequestDataLength` using the phy-error-log request size instead of the phy-control request size, which deserves protocol review. Test signals include SAS topology add/remove under expanders, BSG `smp_utils` commands, sysfs link error counters, phy reset/disable/speed controls, host reset during transport operations, and KASAN/lockdep coverage for failed allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.c

Purpose: implements MPT3SAS diagnostic trigger matching and notification. It watches master, firmware event, SCSI sense, and MPI status/loginfo conditions configured elsewhere in the adapter object, releases the trace diagnostic buffer when a trigger fires, records release metadata, and injects a synthetic diagnostic event into the driver's control-event log.

Important APIs/types/functions: `mpt3sas_trigger_master()`, `mpt3sas_trigger_event()`, `mpt3sas_trigger_scsi()`, and `mpt3sas_trigger_mpi()` are the condition-specific matchers. `mpt3sas_process_trigger_data()` performs release bookkeeping for trigger-data events. `_mpt3sas_raise_sigio()` builds an `Mpi2EventNotificationReply_t` carrying `SL_WH_TRIGGERS_EVENT_DATA_T`, calls `mpt3sas_ctl_add_to_event_log()`, frees the temporary event, and clears `ioc->diag_trigger_active`.

Control flow: each trigger path takes `diag_trigger_lock`, rejects events when the trace buffer is not registered, already released, or another trigger is active, then scans the configured trigger list for a match. Master triggers for firmware fault and adapter reset bypass normal trace-buffer checks so notification can still be raised during severe faults. Matching non-master or noncritical master triggers call `mpt3sas_send_trigger_data_event()`; later `mpt3sas_process_trigger_data()` releases the trace buffer via `mpt3sas_send_diag_release()` if needed and stores trigger details in `ioc->htb_rel`.

State and persistence: uses runtime adapter fields: `diag_trigger_master`, `diag_trigger_event`, `diag_trigger_scsi`, `diag_trigger_mpi`, `diag_trigger_active`, `diag_buffer_status[]`, and `htb_rel`. Trigger definitions may originate from sysfs or persistent trigger pages, but this file only consumes in-memory copies and writes no durable storage itself.

Dependencies and integration points: integrates with `mpt3sas_ctl.c` event logging/polling, diagnostic buffer registration/release paths, SCSI error handling and firmware event paths that call the trigger functions, and `mpt3sas_trigger_diag.h` structures. The synthetic event code is `MPI3_EVENT_DIAGNOSTIC_TRIGGER_FIRED`.

Risks and test signals: active-trigger suppression relies on `_mpt3sas_raise_sigio()` always running after a match; failures before that can leave the flag set. Event and MPI matching allow wildcards only in selected fields, so sysfs encoding must be exact. Tests should cover no trace buffer, already released buffer, duplicate simultaneous triggers, master reset/fault bypass, SCSI ASC/ASCQ wildcard matching, MPI loginfo wildcard matching, event-log insertion, and release metadata visible in host trace-buffer status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.h

Purpose: defines the binary diagnostic-trigger ABI used by the MPT3SAS driver for configured trigger lists and fired-trigger event payloads. It is shared by sysfs/control code, trigger matching, and persistent trigger-page translation.

Important APIs/types/functions: constants include `NUM_VALID_ENTRIES`, trigger type IDs `MPT3SAS_TRIGGER_MASTER`, `MPT3SAS_TRIGGER_EVENT`, `MPT3SAS_TRIGGER_SCSI`, `MPT3SAS_TRIGGER_MPI`, sysfs file names, master trigger bitmasks, and the synthetic `MPI3_EVENT_DIAGNOSTIC_TRIGGER_FIRED`. Structures are `SL_WH_MASTER_TRIGGER_T`, `SL_WH_EVENT_TRIGGER_T`, `SL_WH_EVENT_TRIGGERS_T`, `SL_WH_SCSI_TRIGGER_T`, `SL_WH_SCSI_TRIGGERS_T`, `SL_WH_MPI_TRIGGER_T`, `SL_WH_MPI_TRIGGERS_T`, and `SL_WH_TRIGGERS_EVENT_DATA_T`.

Control flow: the header has no direct execution, but its layouts drive trigger configuration and matching. The list wrappers carry `ValidEntries` plus up to 20 entries. Trigger event data stores a type discriminator and union so the event log can report the exact condition that released the diagnostic buffer.

State and persistence: structures are copied into adapter runtime fields and may be serialized through sysfs or firmware persistent trigger pages. The header fixes size and field ordering, so it effectively defines an ABI between userspace tooling, driver memory, and event payload decoding.

Dependencies and integration points: included by `mpt3sas_base.h` users and `mpt3sas_trigger_diag.c`. It uses Linux-style integer aliases including `U8` from the MPT headers/base include environment.

Risks and test signals: because these are binary structures, padding, endian assumptions, and `ValidEntries` bounds are important. Tests should verify sysfs read/write sizes, rejection or clamping above 20 entries, correct wildcard values (`0xFF` and `0xFFFFFFFF`), and compatibility of fired-event payloads consumed by diagnostic utilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_pages.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_pages.h

Purpose: defines MPI extended configuration pages used to store MPT3SAS diagnostic trigger settings persistently in firmware/controller NVRAM. The pages mirror the runtime master, event, SCSI sense, and IOCStatus/loginfo trigger structures.

Important APIs/types/functions: `MPI2_CONFIG_EXTPAGETYPE_DRIVER_PERSISTENT_TRIGGER` selects the extended page type. Page 0 (`Mpi26DriverTriggerPage0_t`) contains validity flags for the following pages. Page 1 stores one master trigger entry, Page 2 stores up to 20 MPI event triggers, Page 3 stores up to 20 SCSI sense triggers, and Page 4 stores up to 20 IOCStatus/loginfo triggers. Version macros are all `0x01`.

Control flow: no runtime flow exists in this header. Configuration helper code reads/writes these page layouts, checks Page 0 validity flags, then maps page entries to the in-memory structures from `mpt3sas_trigger_diag.h`.

State and persistence: unlike `mpt3sas_trigger_diag.c`, these types represent persistent firmware-backed state. Counts (`NumMasterTrigger`, `NumMPIEventTrigger`, `NumSCSISenseTrigger`, `NumIOCStatusLogInfoTrigger`) determine how many fixed-array entries are meaningful.

Dependencies and integration points: includes `mpi/mpi2_cnfg.h` for `MPI2_CONFIG_EXTENDED_PAGE_HEADER` and integer typedefs. It integrates with MPT3SAS config-page accessors and the diagnostic-trigger sysfs/control path.

Risks and test signals: firmware layout compatibility is the main risk; any structure-size or endian mismatch can corrupt persistent trigger settings. Tests should cover reading missing/invalid pages, writing each trigger family, maximum count boundaries, Page 0 flag handling, and cross-boot persistence on controllers that implement the vendor page type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_trigger_pages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_warpdrive.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_warpdrive.c

Purpose: implements WarpDrive direct I/O support for eligible MPT RAID0 volumes. It determines whether a RAID volume can bypass the virtual volume handle and rewrites read/write CDBs to target the correct physical disk member when an I/O falls wholly within one stripe.

Important APIs/types/functions: `mpt3sas_get_num_volumes()` enumerates RAID volume Page 1 handles. `_warpdrive_disable_ddio()` clears `direct_io_enabled` across known RAID devices. `mpt3sas_init_warpdrive_properties()` validates a `_raid_device` and records member handles, stripe/block exponents, maximum LBA, and direct-I/O eligibility. `mpt3sas_setup_direct_io()` maps READ/WRITE(10/16) volume LBAs to member LBAs and sets `scsiio_tracker.direct_io`.

Control flow: initialization returns early unless `ioc->is_warpdrive` is true, physical disks are hidden, exactly one volume exists, and physical disk count/configuration can be read. It rejects volumes with too many members, member LBAs wider than 32 bits, non-RAID0 type, or invalid stripe/block sizes. During command setup, only READ/WRITE(10/16) commands are considered; the code computes I/O size in volume blocks, rejects out-of-range or cross-stripe requests, selects the member with `sector_div()`, updates `DevHandle`, rewrites the CDB LBA, and marks direct I/O.

State and persistence: computed direct-I/O state lives in `_raid_device` fields such as `direct_io_enabled`, `pd_handle[]`, `stripe_exponent`, `block_exponent`, `max_lba`, `stripe_sz`, and `block_sz`. No persistent controller state is written; it is runtime optimization metadata derived from firmware config pages.

Dependencies and integration points: depends on MPT RAID volume and physical disk configuration helpers, SCSI command helpers, unaligned endian accessors, and command-private `scsiio_tracker`. It integrates with the SCSI I/O build path that supplies `Mpi25SCSIIORequest_t` before request submission.

Risks and test signals: correctness depends on stripe math, block exponent derivation, member handle ordering, and CDB rewrite safety. `find_first_bit()` only proves a bit exists, not that stripe/block sizes are powers of two; non-power-of-two values would produce questionable exponents. Tests should cover single and multiple volume enumeration, hidden/exposed disk mode, RAID0 versus non-RAID0, cross-stripe rejection, READ/WRITE(10/16) LBA rewrite, maximum-LBA rejection, and member handle failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_warpdrive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvme147.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvme147.c

Purpose: provides the built-in SCSI host driver for Motorola MVME147 m68k systems using a WD33C93 SCSI core and board PCC DMA/interrupt registers. It allocates a single Scsi_Host, wires WD33C93 callbacks, enables board interrupts, and scans the bus.

Important APIs/types/functions: `mvme147_init()` and `mvme147_exit()` are module lifecycle hooks. `mvme147_intr()` dispatches either WD33C93 SCSI-port interrupts or acknowledges DMA interrupts. `dma_setup()` programs PCC DMA registers from `WD33C93_scsi_pointer(cmd)`, handles cache push/invalidate, and records direction. `dma_stop()` disables DMA. `mvme147_host_template` exposes WD33C93 queueing, abort, host reset, proc info, queue depth, and command-private size.

Control flow: init exits successfully without registering anything on non-MVME147 machines. On MVME147 it allocates hostdata, sets fixed MMIO base and IRQ, initializes WD33C93 register pointers, configures hostdata flags, registers SCSI-port and DMA IRQs, enables PCC SCSI/DMA interrupts, calls `scsi_add_host()`, and scans. Exit removes the host, frees both IRQs, and drops the host reference.

State and persistence: the only global state is `mvme147_shost`. Runtime DMA state is in WD33C93 hostdata and PCC registers; no persistent storage is changed.

Dependencies and integration points: depends on m68k `MACH_IS_MVME147`, `asm/mvme147hw.h`, legacy `virt_to_bus()`, cache management, SCSI midlayer, and the shared `wd33c93` core. Built from the parent SCSI Makefile with `wd33c93.o`.

Risks and test signals: this is board-specific legacy code with fixed physical addresses and manual cache coherency. The error path after second IRQ failure frees only the SCSI-port IRQ, as intended, but an `scsi_add_host()` failure uses the same label and does not free the DMA IRQ, which is a cleanup risk. Test signals are m68k cross-builds, boot on MVME147, IRQ/DMA transfer completion, host reset/abort paths, and fault injection for IRQ and host-add failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvme147.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvme147.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvme147.h

Purpose: small legacy header for the MVME147 built-in SCSI driver. It supplies driver-local declarations and default queue sizing used by `mvme147.c`.

Important APIs/types/functions: declares `mvme147_detect(struct scsi_host_template *)` and `mvme147_release(struct Scsi_Host *)`, which are legacy prototypes not implemented by the current module-style `mvme147.c`. Defines default `CMD_PER_LUN` as 2 and `CAN_QUEUE` as 16 when not already provided.

Control flow: no runtime control flow. Its macros are consumed when constructing the `scsi_host_template`.

State and persistence: no state or persistence.

Dependencies and integration points: includes `linux/types.h` and relies on SCSI types being visible to includers. Integrated only by `mvme147.c` in this source subset.

Risks and test signals: stale prototypes can confuse readers and should be checked before any refactor to avoid resurrecting obsolete detect/release entry points. Compile tests on m68k validate that queue macros and declarations do not conflict with modern SCSI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvme147.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvme16x_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvme16x_scsi.c

Purpose: implements the NCR53C710 SCSI driver for Motorola MVME16x m68k boards using the generic `53c700` core behind a simple platform device/driver wrapper.

Important APIs/types/functions: `mvme16x_scsi_init()` registers the platform driver and synthetic platform device. `mvme16x_probe()` validates board presence/configuration, allocates `NCR_700_Host_Parameters`, fills chip register base and mode flags, calls `NCR_700_detect()`, requests `MVME16x_IRQ_SCSI`, enables PCCchip2 interrupt routing, and scans. `mvme16x_device_remove()` disables interrupts, removes and releases the host, frees hostdata, and releases the IRQ.

Control flow: init first registers the driver, then creates a `mvme16x-scsi` platform device so probe can run even without firmware enumeration. Probe returns `-ENODEV` for non-MVME16x systems or boards configured without a SCSI chip. On success, SCSI scanning begins after IRQ enable. Exit unregisters the device then the driver.

State and persistence: global state is limited to `mvme16x_scsi_device`; per-host state is allocated `NCR_700_Host_Parameters` and the Scsi_Host. No persistent settings are written, though PCCchip2 interrupt-enable bits are modified at probe/remove.

Dependencies and integration points: depends on m68k `asm/mvme16xhw.h`, platform bus, SCSI SPI transport headers, and the generic `53c700` core. The parent SCSI Makefile links `53c700.o` and `mvme16x_scsi.o` for `CONFIG_MVME16x_SCSI`.

Risks and test signals: fixed addresses and board-specific interrupt register writes make hardware testing essential. `NCR_700_release()`/hostdata ownership should be checked carefully because probe error paths and remove free different pieces. Test signals include m68k cross-builds, probing with `MVME16x_CONFIG_NO_SCSICHIP`, IRQ request failure, scan success, and remove/reload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvme16x_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Kconfig

Purpose: defines build-time configuration for the Marvell 88SE64XX/88SE94XX SAS/SATA `mvsas` driver.

Important APIs/types/functions: `SCSI_MVSAS` is a tristate depending on `PCI && HAS_IOPORT` and selecting `SCSI_SAS_LIBSAS` plus `FW_LOADER`. `SCSI_MVSAS_DEBUG` adds debug prints and defaults to enabled when the driver is enabled. `SCSI_MVSAS_TASKLET` optionally defers interrupt work to a tasklet and defaults off.

Control flow: no runtime control flow. Kconfig determines whether the driver is absent, built-in, or modular, and whether `MV_DEBUG` and `CONFIG_SCSI_MVSAS_TASKLET` paths compile.

State and persistence: generated kernel configuration is the only state. No runtime persistence.

Dependencies and integration points: sourced from the main SCSI Kconfig. The selected libsas dependency is required by `mv_init.c` and `mv_sas.c`; firmware loader support is used by broader mvsas firmware/HBA-info code.

Risks and test signals: dependency mistakes surface as missing libsas, PCI, I/O port, or firmware-loader symbols. Build tests should cover `SCSI_MVSAS=m/y`, debug on/off, tasklet on/off, and non-PCI or `HAS_IOPORT=n` configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Makefile

Purpose: declares the Kbuild object composition for the Marvell `mvsas` driver.

Important APIs/types/functions: `ccflags-$(CONFIG_SCSI_MVSAS_DEBUG) := -DMV_DEBUG` enables debug logging. `obj-$(CONFIG_SCSI_MVSAS) += mvsas.o` builds the composite driver, and `mvsas-y` links `mv_init.o`, `mv_sas.o`, `mv_64xx.o`, and `mv_94xx.o`.

Control flow: no runtime behavior. Kbuild resolves the composite object from configuration symbols.

State and persistence: no runtime state. Build output depends on `.config`.

Dependencies and integration points: this file is the directory-level bridge between `Kconfig` and the source files that provide PCI/lifecycle code, libsas glue, and per-chip dispatch implementations.

Risks and test signals: omitting a component breaks dispatch or libsas symbol resolution. Compile/link tests with `CONFIG_SCSI_MVSAS=m` and `=y`, plus debug/tasklet variants, verify object list completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.c

Purpose: provides the Marvell 88SE64xx/SoC hardware implementation behind the shared `mvs_dispatch` interface. It initializes registers and DMA rings, controls phys, handles interrupts, manages SATA register sets, builds PRDs, and implements SPI and interrupt-coalescing hooks for 3 Gb/s-era chips.

Important APIs/types/functions: the exported `mvs_64xx_dispatch` binds chip operations such as `mvs_64xx_init()`, `mvs_64xx_ioremap()`, `mvs_64xx_isr()`, `mvs_64xx_phy_reset()`, `mvs_64xx_phy_disable()/enable()`, `mvs_64xx_assign_reg_set()/free_reg_set()`, `mvs_64xx_make_prd()`, `mvs_64xx_fix_phy_info()`, `mvs_64xx_phy_set_link_rate()`, SPI helpers, `mvs_64xx_fix_dma()`, and `mvs_64xx_tune_interrupt()`.

Control flow: init optionally performs PCI global reset, powers/enables phys, configures PRD request size, applies vendor phy workarounds, programs SAS addresses and DMA ring base addresses, resets each phy, detects SAS/SATA port type, clears and unmasks per-phy interrupts, sets endian mode, resets command queues, configures coalescing, enables TX/RX rings, and unmasks central/SRS interrupts. ISR status filters invalid or absent interrupts; the ISR clears completion, takes `mvi->lock`, and calls common `mvs_int_full()`. SATA register sets are allocated by scanning PCS/MVS_CTL enable bits and freed by clearing those bits.

State and persistence: all state is runtime in `struct mvs_info`, hardware registers, DMA rings, SATA register-set mapping bytes, and phy structures. Link-rate changes and phy disable/enable write hardware control registers but are not driver-persisted.

Dependencies and integration points: depends on `mv_sas.h`, `mv_64xx.h`, `mv_chips.h`, PCI config space, MMIO/I/O port helpers, common interrupt functions, and libsas-facing code in `mv_sas.c`. Selected by `mv_init.c` for chip flavors 6320, 6440, 6485, Areca 1300, and compatible IDs.

Risks and test signals: reset loops and register polling lack broad timeout coverage in several paths. SoC and PCI branches manipulate different register spaces and are easy to regress independently. `mvs_64xx_init()` has dense hardware sequencing with fixed sleeps. Tests should include probe/remove on representative 64xx and SoC devices, phy reset/disable/rate changes, SATA NCQ/SRS stop recovery, PRD generation with max scatterlists, interrupt coalescing sysfs writes, and fault injection for ioremap/DMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.h

Purpose: defines the 88SE64xx hardware register map, PCI config offsets, vendor-specific phy registers, bit fields, scatter-gather limits, PRD layout, and SPI register constants used by `mv_64xx.c` and generic register helpers.

Important APIs/types/functions: `MAX_LINK_RATE` is 3.0 Gb/s. `enum hw_registers` names BAR4 enhanced-mode registers including global control, port control/status, command list, RX FIS, TX/RX rings, interrupt masks/status, per-port serial control, command indirect registers, config ports, and VSR ports. `enum pci_cfg_registers`, `enum sas_sata_vsp_regs`, and `enum chip_register_bits` describe PCI and phy programming. `struct mvs_prd` is a 64-bit address plus length descriptor. SPI constants select peripheral EEPROM access.

Control flow: no direct execution. Values are consumed by `mv_chips.h` inline accessors and `mv_64xx.c` initialization, interrupt, PRD, SPI, and phy-control paths.

State and persistence: describes runtime hardware registers only. SPI constants may be used for EEPROM reads/writes by common code, but this header itself stores no state.

Dependencies and integration points: includes `linux/types.h` and relies on shared bit definitions from `mv_defs.h` for many control bits. Included before `mv_chips.h` so generic helpers bind to this chip's offsets and PRD layout.

Risks and test signals: wrong offsets or bit masks can cause silent hardware malfunction. Compile tests catch structure visibility; hardware tests should verify MMIO access, PRD DMA, SPI command execution, link-rate reporting, and 64xx-specific interrupt paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.c

Purpose: provides the Marvell 88SE94xx/Vanir hardware implementation behind `mvs_dispatch`. Compared with 64xx, it adds 6 Gb/s phy tuning, SGPIO LED support, larger register-set handling, non-specific NCQ error recovery, dual-core interrupt routing, and 94xx SPI access.

Important APIs/types/functions: exported `mvs_94xx_dispatch` binds `mvs_94xx_init()`, ioremap/iounmap, ISR controls, phy controls, register-set allocation, PRD building, identify-frame extraction, link-rate setting, SPI helpers, DMA workaround, interrupt tuning, `mvs_94xx_non_spec_ncq_error()`, and `mvs_94xx_gpio_write()`. Important internal helpers include `set_phy_tuning()`, `set_phy_ffe_tuning()`, `set_phy_rate()`, `mvs_94xx_config_reg_from_hba()`, and `mvs_94xx_sgpio_init()`.

Control flow: init maps per-core register windows, applies revision-specific phy and memory workarounds, programs all-phy VSR settings, resets command/STP state, configures SAS addresses and HBA-info-derived tuning per phy, enables and hard-resets phys, detects port type, unmasks per-phy interrupts, sets endian behavior, starts TX/RX queues, enables central and SRS interrupts, tunes timers for STP/expander performance, and initializes SGPIO. ISR status checks SAS_A/SAS_B bits; the ISR only services the matching core and calls common `mvs_int_full()` under lock. GPIO writes translate libsas SGPIO writes to DCTRL LED bitfields.

State and persistence: runtime state includes `mvi->sata_reg_set`, phy tuning defaults in `hba_info_param`, MMIO windows adjusted per host ID, SGPIO registers, and DMA work buffers. No driver persistence is written, though SPI helpers can support persistent HBA information when called by common code.

Dependencies and integration points: depends on `mv_sas.h`, `mv_94xx.h`, `mv_chips.h`, libsas GPIO APIs, common mvsas interrupt/task/device code, and PCI revision IDs. Selected by `mv_init.c` for 9180, 9480, 9445, 9485, Areca 1320, OCZ RevoDrive/zDrive, and related IDs.

Risks and test signals: revision-specific tuning is fragile and uses many magic constants. `mv_ffc64()`/register-set allocation must handle 64 SATA register sets correctly. `mvs_94xx_fix_dma()` uses `virt_to_phys()` on PRD memory for chained entries on A0/B0, which is architecture/DMA-sensitive. Tests should cover dual-core interrupt routing, SGPIO writes, non-specific NCQ error recovery, phy tuning across revisions, max scatter-gather PRDs, register-set exhaustion, and probe/remove on both single- and dual-host adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.h

Purpose: defines the 88SE94xx hardware contract: register maps, revision IDs, interrupt causes, 6 Gb/s phy configuration bitfields, PRD format, SGPIO registers, SPI registers, and helper macros for SATA register-set enable registers.

Important APIs/types/functions: `MAX_LINK_RATE` is 6.0 Gb/s. `enum VANIR_REVISION_ID` distinguishes A0/B0/C0/C1/C2 tuning paths. `enum hw_registers`, `host_registers`, `pci_cfg_registers`, `sas_sata_vsp_regs`, `chip_register_bits`, and `pci_interrupt_cause` drive MMIO and interrupt handling. `union reg_phy_cfg` packs phy capability fields. `struct mvs_prd_imt` and packed `struct mvs_prd` describe 94xx PRDs. SGPIO enums define LED control. `mv_ffc64()`, `r_reg_set_enable()`, and `w_reg_set_enable()` support register-set allocation.

Control flow: no standalone flow. The constants and inline helper are consumed by `mv_94xx.c` and `mv_chips.h`.

State and persistence: describes hardware register state; no direct driver state. SGPIO and SPI fields target controller-side registers that may affect persistent or enclosure-visible behavior when used by implementation code.

Dependencies and integration points: includes `linux/types.h`, expects common mvsas definitions from `mv_defs.h`/`mv_sas.h`, and exports `mvs_94xx_dispatch` for `mv_init.c`.

Risks and test signals: bitfield layout in `union reg_phy_cfg` and `struct mvs_prd_imt` is endian-sensitive. SGPIO register offsets use host offsets and must match dual-core hardware. Test signals are build coverage on big/little endian, link-rate negotiation to 6 Gb/s, SGPIO LED control, SPI register reads, and max PRD DMA on 94xx adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_chips.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_chips.h

Purpose: provides generic inline register-access and common hardware helper routines shared by the 64xx and 94xx mvsas chip implementations. It abstracts per-port register windows, command indirect registers, interrupt draining, delivery/completion ring pointers, PRD sizing, PCIe link reporting, and max link-rate reporting.

Important APIs/types/functions: macros `mr32`, `mw32`, and `mw32_f` wrap MMIO access through a local `regs` variable; `iow*/ior*` wrap port-I/O style access. Helpers include `mvs_cr32()`, `mvs_cw32()`, per-phy/per-port config/VSR/IRQ accessors, `mvs_phy_hacks()`, `mvs_int_sata()`, `mvs_int_full()`, `mvs_start_delivery()`, `mvs_rx_update()`, `mvs_get_prd_size()`, `mvs_get_prd_count()`, `mvs_show_pcie_usage()`, and `mvs_hw_max_link_rate()`.

Control flow: per-chip files include their register header before this header, so the inline functions compile against the correct offsets and `struct mvs_prd` shape. Interrupt flow in `mvs_int_full()` reads central status, drains RX completions, dispatches per-port events, handles non-specific NCQ and SRS interrupts, and acknowledges central status.

State and persistence: operates on `struct mvs_info` runtime state and hardware registers. No persistent storage is modified directly.

Dependencies and integration points: depends on `mv_sas.h` types, per-chip register constants, common interrupt functions from `mv_sas.c`, and `MVS_CHIP_DISP` dispatch callbacks. Used by both `mv_64xx.c` and `mv_94xx.c`.

Risks and test signals: macros require a correctly named local `regs` variable, so misuse can compile incorrectly or not at all. Port-I/O helper casts are unusual and deserve architecture coverage. Interrupt helper behavior depends on per-chip `non_spec_ncq_error` and `clear_active_cmds` hooks. Tests should include both chip families, interrupt storm handling, SRS interrupts, PCIe status display, and sparse/build checks for MMIO annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_chips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_defs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_defs.h

Purpose: central constants header for mvsas hardware and protocol definitions shared by all Marvell chip variants. It defines chip flavor IDs, queue/ring sizing, hardware limits, register bit masks, port/phy event bits, command-table fields, status/error record bits, PCI config fields, and SAS/STP/SMP protocol encodings.

Important APIs/types/functions: key enums include `chip_flavors`, `driver_configuration`, `hardware_details`, `peripheral_registers`, `hw_register_bits`, `sas_sata_config_port_regs`, `sas_cmd_port_registers`, `mvs_info_flags`, `mvs_event_flags`, `mvs_port_type`, `ct_format`, `status_buffer`, `error_info_rec`, `error_info_rec_2`, `pci_cfg_register_bits`, `open_frame_protocol`, and `datapres_field`. Device IDs for Areca 1300/1320 are also defined.

Control flow: no direct execution. The values are used throughout `mv_init.c`, `mv_sas.c`, `mv_chips.h`, and per-chip files to size DMA memory, parse completion/error state, program hardware, and translate link/device events into libsas notifications.

State and persistence: no state. The constants define the layout and meaning of runtime hardware state.

Dependencies and integration points: included by `mv_sas.h`, making it part of nearly every mvsas source file. It bridges chip-specific register headers with generic libsas/SCSI code.

Risks and test signals: incorrect bit masks can break command issue, completion parsing, or error handling across both chip families. Queue constants interact with allocation sizes and hardware limits. Test signals include compile-time coverage, max queue/scatterlist I/O, error-injection paths for each error bit family, SATA/SAS port detection, and static analysis for shifts and mask widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_init.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_init.c

Purpose: owns PCI probing/removal, Scsi_Host and libsas HA setup, DMA resource allocation, interrupt registration, sysfs attributes, and module lifecycle for the Marvell `mvsas` driver.

Important APIs/types/functions: `mvs_init()`/`mvs_exit()` attach/release the libsas transport and register/unregister the PCI driver. `mvs_pci_init()` performs device enablement, region requests, DMA mask setup, host allocation, per-core `mvs_info` allocation/init, `scsi_add_host()`, `sas_register_ha()`, IRQ registration, interrupt enablement, and scan. `mvs_pci_remove()` unwinds those resources. Helpers include `mvs_alloc()`, `mvs_free()`, `mvs_ioremap()`, `mvs_pci_alloc()`, `mvs_prep_sas_ha_init()`, `mvs_post_sas_ha_init()`, `mvs_phy_init()`, and the shared `mvs_interrupt()` handler. Sysfs exposes `driver_version` and writable `interrupt_coalescing`.

Control flow: module init attaches `mvs_transport_ops` to libsas, then registers `mvs_pci_driver`. Probe chooses a chip descriptor from `mvs_pci_table`, prepares one Scsi_Host with a `sas_ha_struct`, allocates one or two `mvs_info` cores, initializes SAS addresses, calls the chip dispatch `chip_init()`, builds the libsas phy/port arrays, registers SCSI and SAS hosts, requests a shared IRQ, enables interrupts, and scans. The interrupt handler checks status through chip dispatch and either runs per-core ISR directly or schedules a tasklet depending on config.

State and persistence: state is runtime: global `mvs_stt`, module parameter-like `interrupt_coalescing`, PCI drvdata pointing to `sas_ha_struct`, per-core `mvs_info`, DMA rings/buffers/pools, reserved-tag bitmap, and libsas phy/port/device structures. No persistent storage is written; default SAS addresses are synthesized in `mvs_init_sas_add()`.

Dependencies and integration points: depends on PCI, DMA API, SCSI midlayer, libsas, SAS ATA attributes, per-chip dispatch tables, and common `mv_sas.c` task/device operations. The PCI ID table maps Marvell, Areca, Adaptec/TTI, and OCZ devices to 64xx or 94xx chip descriptors.

Risks and test signals: several probe failure paths jump to `err_out_regions` without freeing already allocated HA/core resources, making fault-injection cleanup important. `mvs_free()` destroys `mvi->dma_pool` without a null check. Synthetic SAS addresses are fixed, which can collide across adapters. `interrupt_coalescing_store()` returns `strlen(buffer)` rather than `size`. Tests should cover probe/remove for each chip family, one-core and two-core adapters, tasklet and non-tasklet builds, sysfs coalescing writes including invalid values, DMA allocation failure injection, IRQ sharing, and libsas scan/remove ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_init.c -->
