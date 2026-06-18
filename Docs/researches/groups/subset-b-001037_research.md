# Research: subset-b-001037

Grouped research for libata SCSI translation, legacy SFF/BMDMA transport, trace formatting, ATA transport class sysfs objects, ZPODD power handling, and the internal libata interfaces used by those files. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-scsi.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-scsi.c

## Purpose
`libata-scsi.c` is the libata SCSI translation layer. It lets ATA, ZAC, and ATAPI devices appear as SCSI devices by translating block commands into ATA taskfiles, forwarding packet commands to ATAPI devices, synthesizing SCSI inquiry/capacity/mode pages from ATA identify data, managing SCSI device lifecycle for libata ports, and mapping ATA completion/error state back into SCSI status and sense data.

## Important APIs, Types, And Functions
The public entry points include `ata_scsi_queuecmd`, `__ata_scsi_queuecmd`, `ata_scsi_add_hosts`, `ata_scsi_scan_host`, `ata_scsi_sdev_init`, `ata_scsi_sdev_configure`, `ata_scsi_sdev_destroy`, `ata_scsi_ioctl`, `ata_sas_scsi_ioctl`, `ata_scsi_offline_dev`, `ata_scsi_hotplug`, `ata_scsi_user_scan`, `ata_scsi_dev_rescan`, `ata_scsi_media_change_notify`, `ata_scsi_set_sense`, and `ata_scsi_sense_is_valid`. Internal translators include `ata_scsi_rw_xlat`, `ata_scsi_verify_xlat`, `ata_scsi_flush_xlat`, `ata_scsi_start_stop_xlat`, `ata_scsi_pass_thru`, `ata_scsi_var_len_cdb_xlat`, `ata_scsi_write_same_xlat`, `ata_scsi_zbc_in_xlat`, `ata_scsi_zbc_out_xlat`, `ata_scsi_mode_select_xlat`, `ata_scsi_security_inout_xlat`, and `atapi_xlat`.

The file pivots around `struct ata_device`, `struct ata_port`, `struct ata_link`, `struct ata_queued_cmd`, `struct ata_taskfile`, `struct scsi_cmnd`, and `struct scsi_device`. It uses `ata_xlat_func_t` to select translators, a global `ata_scsi_rbuf` protected by `ata_scsi_rbuf_lock` for simulated response buffers and TRIM descriptor formatting, and static default mode page templates for read/write recovery, caching, and control pages.

## Control Flow
Command flow starts in `ata_scsi_queuecmd`, which takes the ATA host lock, maps the SCSI target/channel/LUN to an `ata_device`, and calls `__ata_scsi_queuecmd`. That function validates command length, chooses a translator with `ata_get_xlat_func` for ATA/ZAC devices, uses `atapi_xlat` for ATAPI packet devices, or calls `ata_scsi_simulate` for internally emulated SCSI commands. `ata_scsi_translate` allocates an `ata_queued_cmd`, maps data buffers, calls the translator, then issues the command through `ata_scsi_qc_issue`; commands that finish during translation set SCSI status and call `scsi_done`.

Read/write translation decodes 6/10/16-byte CDB LBAs and transfer lengths, handles FUA and command duration limit descriptor bits, validates passthrough request sizes, computes byte count, then delegates ATA taskfile composition to `ata_build_rw_tf`. VERIFY and FLUSH build no-data taskfiles. START STOP maps stop/start semantics to libata power taskfiles while rejecting unsupported LOEJ and power-condition fields. WRITE SAME with UNMAP rewrites the SCSI payload into ATA DSM TRIM descriptors and selects queued TRIM (`ATA_CMD_FPDMA_SEND`) when supported, otherwise unqueued DSM.

Simulated command flow uses `ata_scsi_rbuf_fill`: clear the shared response buffer, invoke a simulator, copy data to the SCSI scatterlist, set `SAM_STAT_GOOD`, and update residuals. Simulators synthesize INQUIRY standard/VPD pages, MODE SENSE pages and subpages, READ CAPACITY 10/16, REPORT LUNS, MAINTENANCE IN supported opcode reports, TEST UNIT READY, REQUEST SENSE, and other benign no-ops. Unsupported or malformed requests build precise ILLEGAL REQUEST sense with field pointers.

Completion flow is `ata_scsi_qc_complete` for ATA taskfile commands and `atapi_qc_complete` for packet commands. ATA pass-through commands can intentionally return CHECK CONDITION with ATA status descriptors when CK_COND is set. Normal ATA errors are converted by `ata_to_sense_error`, `ata_gen_ata_sense`, `ata_scsi_set_sense_information`, and `ata_scsi_set_passthru_sense_fields`. Deferred command flow uses `ap->deferred_qc`, `ata_scsi_deferred_qc_work`, `ata_scsi_requeue_deferred_qc`, and `ata_scsi_schedule_deferred_qc` to support low-level `qc_defer` policies without letting the SCSI midlayer hide every defer.

Device lifecycle flow creates a `Scsi_Host` per ATA port in `ata_scsi_add_hosts`, links SCSI devices to ATA ports for PM ordering in `ata_scsi_sdev_init`, configures queue limits and device features in `ata_scsi_dev_config`, scans discovered ATA links in `ata_scsi_scan_host`, removes detached SCSI devices after EH in `ata_scsi_hotplug`, and schedules rescans after pass-through or resume changes in `ata_scsi_dev_rescan`.

## State And Persistence
Persistent state lives in libata structures, not on disk. The file mutates `dev->sdev`, device flags such as `ATA_DFLAG_NO_UNLOAD`, `ATA_DFLAG_D_SENSE`, `ATA_DFLAG_CDL_ENABLED`, `ATA_DFLAG_DETACH`, `ATA_DFLAG_RESUMING`, and `ATA_DFLAG_UNLOCK_HPA`, per-device queue depth, max sectors, sector size, security capability, supported media-change events, runtime start/stop policy, and `dev->zpodd`-adjacent power behavior through SCSI device links. It updates EH action masks (`ATA_EH_PARK`, `ATA_EH_RESET`), probe masks, deferred command pointers, unpark deadlines, and SCSI scan/hotplug work.

Mode SELECT can persistently change device behavior by issuing SET FEATURES for write cache enable/disable and command duration limits, while the in-memory D_SENSE flag controls future sense format. Pass-through commands can change the ATA device behind libata; this file therefore queues SCSI rescans to refresh capacity or attributes. `ata_scsi_rbuf` is a transient global scratch buffer serialized by spinlock.

## Dependencies And Integration Points
The file integrates tightly with the SCSI midlayer (`scsi_done`, `scsi_execute_cmd`, `scsi_add_host_with_dma`, `__scsi_add_device`, `scsi_remove_device`, `scsi_rescan_device`, queue limits, sense helpers, device events, and scan mutexes), block layer request metadata, libata core taskfile and EH helpers, ZAC/ZBC constants, ATAPI EH helpers, ACPI PM restart policy, OF child-node assignment, device links, runtime PM, and the ATA transport template declared in `libata-transport.c`.

It also preserves legacy Linux user ABI through HDIO ioctls (`HDIO_GET_32BIT`, `HDIO_SET_32BIT`, `HDIO_GET_IDENTITY`, `HDIO_DRIVE_CMD`, `HDIO_DRIVE_TASK`) and SAT ATA pass-through. Several behavior choices are compatibility-driven, including descriptor-format sense for successful pass-through with CK_COND, filtering SET FEATURES transfer-mode changes, filtering TPM commands unless `libata_allow_tpm` is enabled, and treating some legacy ATAPI inquiry data as modern MMC-compatible.

## Risks And Edge Cases
Translation bugs can corrupt data: LBA/count decoding, 6-byte zero-length semantics, ATA sector-count zero semantics, FUA/DLD handling, TRIM descriptor rewriting, and ZAC endian swizzling are all high-risk. The shared response buffer is safe only while all users take `ata_scsi_rbuf_lock`. Pass-through commands are intentionally powerful and partially filtered, but still allow users with raw privileges to alter device state. MODE SELECT mutates device flags before or while constructing SET FEATURES taskfiles, so failed command handling must keep software state and hardware state coherent.

Lifecycle races are a major concern. `dev->sdev` is protected by the ATA host lock and sometimes by `scan_mutex`; hot unplug, user-initiated SCSI unplug, EH detach, and asynchronous scan can overlap. Deferred commands interact with EH and NCQ failure paths, so stale `ap->deferred_qc` must be completed with `DID_REQUEUE`. ATAPI variable-length transfers can overflow and require drain buffers. ZBC REPORT ZONES rewrites device-provided little-endian structures in-place across scatterlist mappings and must not overrun partial segments.

## Test Signals
Useful signals include SCSI generic READ/WRITE/VERIFY/FLUSH/START STOP command tests across 28-bit, 48-bit, NCQ, FUA, and zero-length boundaries; sg3_utils INQUIRY, VPD, MODE SENSE, MODE SELECT, READ CAPACITY, REPORT LUNS, and REPORT SUPPORTED OPCODES probes; HDIO ioctl compatibility tests; ATA pass-through success/error/CK_COND result descriptor tests; ATAPI optical command forwarding and inquiry fixup tests; TRIM via WRITE SAME/UNMAP for queued and unqueued devices; ZAC/ZBC REPORT ZONES and zone management tests; hotplug, detach, rescan, runtime PM, and system resume tests; lockdep/KASAN runs around SCSI scan and EH paths; and fault injection for queue allocation, drain buffer allocation, `scsi_device_get`, and command timeout/EH recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-sff.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-sff.c

## Purpose
`libata-sff.c` implements libata support for legacy taskfile-style ATA controllers: SFF PIO register access, ATA/ATAPI PIO host-state-machine handling, interrupt handling, reset/classification, PCI SFF resource setup, and optional PCI IDE bus-master DMA (BMDMA). It provides reusable `ata_port_operations` for old PATA/IDE-style controllers and controllers that still expose SFF taskfile registers.

## Important APIs, Types, And Functions
The exported SFF port operations are collected in `ata_sff_port_ops`; BMDMA variants are `ata_bmdma_port_ops` and `ata_bmdma32_port_ops`. Important exported helpers include `ata_sff_check_status`, `ata_sff_pause`, `ata_sff_dma_pause`, `ata_sff_wait_ready`, `ata_sff_dev_select`, `ata_sff_irq_on`, `ata_sff_tf_load`, `ata_sff_tf_read`, `ata_sff_exec_command`, `ata_sff_data_xfer`, `ata_sff_data_xfer32`, `ata_sff_hsm_move`, `ata_sff_queue_work`, `ata_sff_queue_delayed_work`, `ata_sff_queue_pio_task`, `ata_sff_flush_pio_task`, `ata_sff_qc_issue`, `ata_sff_qc_fill_rtf`, `ata_sff_port_intr`, `ata_sff_interrupt`, `ata_sff_lost_interrupt`, `ata_sff_freeze`, `ata_sff_thaw`, `ata_sff_prereset`, `ata_sff_dev_classify`, `ata_sff_wait_after_reset`, `ata_sff_softreset`, `sata_sff_hardreset`, `ata_sff_postreset`, `ata_sff_drain_fifo`, `ata_sff_error_handler`, `ata_sff_std_ports`, PCI helpers, and BMDMA helpers.

Key state types are `struct ata_port`, `struct ata_link`, `struct ata_device`, `struct ata_queued_cmd`, `struct ata_taskfile`, `struct ata_ioports`, `struct ata_host`, `struct pci_dev`, and BMDMA PRD entries. The global `ata_sff_wq` serializes delayed PIO tasks for SFF controllers.

## Control Flow
PIO/nodata issue starts in `ata_sff_qc_issue`. It selects the target device, optionally marks polling mode, writes the taskfile with `ata_tf_to_host`, and initializes the SFF host state machine (`HSM_ST_FIRST`, `HSM_ST`, or `HSM_ST_LAST`). Depending on protocol and flags, the rest is driven by interrupts through `ata_sff_port_intr`/`ata_sff_hsm_move` or by delayed work through `ata_sff_pio_task`.

`ata_sff_hsm_move` is the central state machine. In `HSM_ST_FIRST`, it sends the first ATA PIO data block or ATAPI CDB after validating DRQ/error status. In `HSM_ST`, it transfers ATA sectors or ATAPI byte chunks while watching status, ireason, DRQ, ERR, and DF. In `HSM_ST_LAST`, it validates final status, completes the queued command, and returns to idle. In `HSM_ST_ERR`, it completes with error and may freeze the port so EH can reset. `ata_pio_sector`, `ata_pio_sectors`, `__atapi_pio_bytes`, and `atapi_pio_bytes` implement the scatterlist/page-level PIO transfers.

Interrupt flow enters `ata_sff_interrupt`, which locks the host, checks each port’s active command, skips polling commands, invokes the selected per-port interrupt function, handles spurious shared IRQs by checking optional IRQ-pending hooks, and may retry if clearing status shows an in-flight command is now ready. `ata_sff_lost_interrupt` is an EH-side recovery probe that detects a non-busy command with no IRQ and reuses normal port interrupt handling.

Reset flow uses `ata_sff_prereset` to wait for non-busy status before softreset, `ata_devchk` to detect PATA master/slave presence by writing shadow-register patterns, `ata_bus_softreset` to pulse SRST, `ata_sff_wait_after_reset` to wait for device readiness, `ata_sff_dev_classify` to read taskfile signatures, and `ata_sff_postreset` to restore device control state. `sata_sff_hardreset` wraps SATA link hardreset while still using SFF readiness/classification helpers.

BMDMA flow extends SFF. `ata_bmdma_qc_prep` builds a PRD table, `ata_bmdma_qc_issue` handles DMA protocols by loading the taskfile, programming PRD table/direction through `ata_bmdma_setup`, starting DMA with `ata_bmdma_start`, and then letting `ata_bmdma_port_intr` stop the engine and merge DMA status with the SFF state machine. Error cleanup stops DMA in `ata_bmdma_error_handler` and `ata_bmdma_post_internal_cmd`.

PCI setup flow maps command/control BARs in `ata_pci_sff_init_host`, allocates and prepares two-port hosts in `ata_pci_sff_prepare_host`, requests legacy or native interrupts in `ata_pci_sff_activate_host`, and exposes one-shot helpers `ata_pci_sff_init_one` and `ata_pci_bmdma_init_one`. BMDMA additionally maps BAR4, sets a 32-bit DMA mask, detects simplex mode, and records per-port BMDMA MMIO addresses.

## State And Persistence
The file mutates volatile controller and libata runtime state: taskfile shadow registers, device-control `ATA_NIEN`/`ATA_SRST` bits, `ap->ctl`, `ap->last_ctl`, `ap->hsm_task_state`, `ap->sff_pio_task_link`, active queued-command offsets (`curbytes`, `cursg`, `cursg_ofs`), error masks, EH descriptions/actions, idle IRQ counters, BMDMA PRD memory, port DMA masks, host flags such as `ATA_HOST_SIMPLEX`, and per-port PIO32 flags. Hardware state persists only in controller registers until reset/power changes; no durable storage is written.

Initialization state includes the global SFF workqueue created by `ata_sff_init` and destroyed by `ata_sff_exit`, delayed work initialized per port by `ata_sff_port_init`, and PCI devres-managed BAR/IRQ mappings. BMDMA port startup allocates coherent PRD tables when DMA masks advertise DMA support.

## Dependencies And Integration Points
This file depends on libata core for queued command allocation/completion, EH/reset orchestration, SATA SCR handling, port descriptors, taskfile helpers, and command classification. It integrates with Linux PCI devres, IRQ APIs, DMA coherent allocation, DMA masks, MMIO/PIO register accessors, workqueues, highmem page mapping, scatterlists, tracing (`trace_ata_*`), and SCSI registration through host activation helpers. Low-level drivers inherit these operations and override selected hooks (`sff_check_altstatus`, `sff_set_devctl`, `sff_irq_check`, `bmdma_*`, reset hooks) for chipset quirks.

## Risks And Edge Cases
Timing is fragile. SFF requires 400ns pauses, correct alternate-status reads to avoid clearing shared IRQ status, and a DMA stop transition delay. Incorrect HSM transitions can complete corrupt data, freeze ports unnecessarily, or leave DRQ asserted. PIO transfers must respect page boundaries and alignment assumptions; ATAPI ireason validation catches devices that request the wrong direction or impossible byte counts. Reset/classification handles phantom devices, diagnostic failures, absent pull-down resistors returning `0xff`, and master/slave double-select quirks.

BMDMA has additional risk from 32-bit address truncation, 64K PRD boundary splits, controllers that cannot represent 64K as zero, simplex mode, posted MMIO writes, and error status races. Interrupt handling must cope with shared IRQs, polling commands, spurious IRQ status, and the fact that clearing status can race active completion. PCI helpers assume two-port IDE layout and may mark ports dummy when BARs are disabled.

## Test Signals
Useful signals include boot and I/O tests on PIO-only PATA, PCI IDE BMDMA, legacy-mode PCI IDE, native-mode PCI IDE, ATAPI optical devices, and SATA controllers using SFF-style registers; PIO read/write with odd byte counts and scatterlists crossing page boundaries; ATAPI CDB interrupt and no-CDB-interrupt devices; forced polling mode; lost-interrupt and spurious shared-IRQ injection; softreset/hardreset/classification across master/slave combinations; BMDMA PRD boundary tests at 64K splits and dumb-controller mode; simplex fallback tests; DMA error/timeout conversion; and lockdep/KASAN/trace validation around HSM transitions and workqueue flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-sff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-trace.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-trace.c

## Purpose
`libata-trace.c` supplies trace-event formatting helpers for libata. It turns status bytes, BMDMA status bytes, EH action/error masks, queued-command flags, taskfile flags, and selected ATA subcommands into readable strings consumed by `trace/events/libata.h`.

## Important APIs, Types, And Functions
The exported formatting helpers are `libata_trace_parse_status`, `libata_trace_parse_host_stat`, `libata_trace_parse_eh_action`, `libata_trace_parse_eh_err_mask`, `libata_trace_parse_qc_flags`, `libata_trace_parse_tf_flags`, and `libata_trace_parse_subcmd`. They all write into a `struct trace_seq` and return the pointer obtained from `trace_seq_buffer_ptr`.

## Control Flow
Each parser records the current trace-sequence buffer pointer, appends fixed tokens for every set bit or recognized subcommand, emits a trailing NUL, and returns the original pointer. Bitmask parsers first print a raw hex value for masks where that matters, then append symbolic names inside braces. `libata_trace_parse_subcmd` dispatches by ATA command and then by feature or `hob_nsect` subcommand fields for FPDMA receive/send, NCQ non-data, and ZAC management commands.

## State And Persistence
The file is stateless. It only appends to the caller-provided trace buffer; no global data or hardware state is changed.

## Dependencies And Integration Points
It depends on ATA constants from libata headers, Linux trace sequence helpers, and the tracepoint definitions in `trace/events/libata.h`. SFF/BMDMA and libata core paths use these helpers indirectly when tracepoints such as taskfile load, command issue, BMDMA status, HSM state, and error handling are enabled.

## Risks And Edge Cases
Trace text must stay aligned with current libata flag definitions. Missing bits are silently omitted, which can hide newer flags in traces. The EH action parser checks combined reset bits before individual soft/hard reset branches, making the individual branches unreachable when either reset bit is set through the combined expression; this is trace-only behavior but affects diagnostic clarity. Formatting relies on trace-sequence capacity handling by the tracing core.

## Test Signals
Enable libata tracepoints through ftrace/perf and issue commands that cover normal status bits, BMDMA interrupts/errors, EH reset/park/revalidate actions, NCQ and non-NCQ queued commands, pass-through commands, and ZAC/DSM/NCQ subcommands. Verify rendered trace text includes expected symbolic tokens and remains NUL-terminated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-transport.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-transport.c

## Purpose
`libata-transport.c` implements the ATA transport class representation exposed through the Linux driver model and sysfs. It models ATA ports, links, and devices under the SCSI transport infrastructure, creates and removes those transport devices, publishes read-only attributes for topology and device capability/state, and provides the `ata_scsi_transportt` template used by libata SCSI hosts.

## Important APIs, Types, And Functions
Public entry points are `ata_tport_add`, `ata_tport_delete`, `ata_tlink_add`, `ata_tlink_delete`, `ata_port_classify`, `libata_transport_init`, and `libata_transport_exit`; the global `ata_scsi_transportt` connects SCSI EH and user scan callbacks with ATA transport host attributes. Internal helpers include match/release functions for port/link/device transport objects, sysfs show methods for port/device/link attributes, `ata_tdev_add`, `ata_tdev_delete`, and name conversion helpers generated by `ata_bitfield_name_match` and `ata_bitfield_name_search`.

The three driver-model object classes are `ata_port_class`, `ata_link_class`, and `ata_dev_class`, backed by `struct ata_port`, `struct ata_link`, and `struct ata_device` embedded `tdev` devices. Attribute groups expose port number, PMP link count, idle IRQ count, device class, PIO/DMA/current transfer modes, speed-down count, error ring, IDENTIFY data, PMP GSCR data, TRIM mode, and link speed limits/current speed.

## Control Flow
Initialization registers transport classes for link, port, and device objects, then registers containers for host, link, and device attributes. `ata_tport_add` initializes the port device, binds ACPI port data, adds it to the driver model, enables runtime PM bookkeeping, configures transport attributes, and then adds the host link with `ata_tlink_add`. `ata_tlink_add` initializes the link device below the port and adds all ATA devices on that link with `ata_tdev_add`. Deletion reverses this order: port deletion removes link/device children, removes transport/device registrations, destroys transport devices, and drops references.

Sysfs show flow maps the driver-model `struct device` back to the owning ATA object with container macros, formats state through `sysfs_emit`, `scnprintf`, or ATA name lookup tables, and returns a byte count. Error-ring display walks `ata_ering` entries through `ata_ering_map`, converting jiffies timestamps to seconds/nanoseconds and formatting error masks. Classification flow wraps `ata_dev_classify` and logs the resulting class name when a reset signature is parsed.

## State And Persistence
The file mutates driver-model state by initializing, naming, adding, configuring, removing, and destroying embedded devices. It increments/decrements ATA host references around port transport lifetime and enables runtime PM on port transport devices while forbidding automatic runtime suspend by default. Sysfs attributes reflect live libata state but do not persist it; all attributes in this file are read-only.

## Dependencies And Integration Points
It depends on the Linux SCSI transport class library, device model, sysfs attribute groups, runtime PM, ACPI binding helpers, libata error handling (`ata_scsi_error`), user scan (`ata_scsi_user_scan`), error ring mapping, IDENTIFY/PMP data, SATA speed formatting, and ATA class/transfer/error constants. It is initialized as part of libata module setup and used by `libata-scsi.c` when creating `Scsi_Host` instances.

## Risks And Edge Cases
Lifetime ordering is the main risk. Embedded `tdev` objects must be removed and destroyed in the correct parent/child order, and the port release callback must balance the host reference. `ata_tlink_add` has partial-failure cleanup that walks back already-added devices; pointer arithmetic over `link->device` assumes the iterator is still in that array. Sysfs show functions expose mutable fields without deep locking, so they are best-effort snapshots. Large IDENTIFY/GSCR/error-ring output must stay within sysfs buffer expectations.

## Test Signals
Probe/remove libata hosts with PATA, SATA, PMP, and SAS-host flags; inspect `/sys/class/ata_port`, `/sys/class/ata_link`, and `/sys/class/ata_device`; verify link/device names for host links and PMP links; validate sysfs attributes against known IDENTIFY data and negotiated speed; inject add failures to exercise cleanup; run hotplug/remove cycles under KASAN/refcount debugging; and confirm `ata_scsi_transportt` still routes SCSI EH and user scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-transport.h -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-transport.h

## Purpose
`libata-transport.h` is the small internal header that shares ATA transport-class declarations between libata source files. It avoids exposing transport setup details through the public libata API while letting SCSI and core code reference the transport template and link lifecycle helpers.

## Important APIs, Types, And Functions
The header declares `extern struct scsi_transport_template ata_scsi_transportt`, `int ata_tlink_add(struct ata_link *link)`, `void ata_tlink_delete(struct ata_link *link)`, `__init int libata_transport_init(void)`, and `void __exit libata_transport_exit(void)`. It depends on prior declarations of `struct ata_link` and SCSI transport types from included libata/SCSI headers.

## Control Flow
There is no executable control flow. The declarations support module initialization/exit, SCSI host setup, and port/link device-model lifecycle implemented in `libata-transport.c`.

## State And Persistence
The header owns no state. It declares access to the global `ata_scsi_transportt` template and transport init/exit routines that manage driver-model state elsewhere.

## Dependencies And Integration Points
It is included by `libata-scsi.c` to assign `shost->transportt` and by `libata-transport.c` for self-consistency. The include guard `_LIBATA_TRANSPORT_H` prevents duplicate declarations.

## Risks And Edge Cases
The header is intentionally narrow. Signature drift between this header and `libata-transport.c` would break builds. Because it is internal, adding broad declarations here can increase coupling between libata subsystems.

## Test Signals
Build coverage with `CONFIG_ATA` and SCSI transport enabled is the primary signal. Link-time failures would catch missing `ata_scsi_transportt`, `ata_tlink_add/delete`, or transport init/exit definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-zpodd.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-zpodd.c

## Purpose
`libata-zpodd.c` implements Zero Power Optical Disk Drive support for SATA ATAPI optical drives that firmware/ACPI can power off. It detects supported slot/drawer mechanisms, determines when the drive is zero-power-ready, enables ACPI wake for powered-off runtime suspend, handles ACPI wake notifications, and restores user-visible media polling/eject behavior after power-on.

## Important APIs, Types, And Functions
Public libata-internal entry points are `zpodd_init`, `zpodd_exit`, `zpodd_on_suspend`, `zpodd_zpready`, `zpodd_enable_run_wake`, `zpodd_disable_run_wake`, and `zpodd_post_poweron`. Internal helpers include `eject_tray`, `zpodd_get_mech_type`, `zpready`, `zpodd_wake_dev`, `ata_acpi_add_pm_notifier`, and `ata_acpi_remove_pm_notifier`.

The main private state is `struct zpodd`, containing mechanism type, owning `ata_device`, `from_notify`, `zp_ready`, `last_ready`, `zp_sampled`, and `powered_off`. The module parameter `zpodd_poweroff_delay` controls how long the drive must stay ready before poweroff is allowed.

## Control Flow
Initialization checks whether the ATA transport device has an ACPI companion capable of poweroff, queries the ATAPI removable media feature descriptor with GET CONFIGURATION, accepts only supported slot or drawer mechanisms, allocates `struct zpodd`, installs an ACPI system notify handler, exposes PM QoS flags, and stores the pointer in `dev->zpodd`. Exit removes the notify handler, frees state, and clears the pointer.

Suspend readiness flow calls `zpready`, which issues TEST UNIT READY and REQUEST SENSE through ATAPI EH helpers. A slot drive is considered ready when sense reports no media; a drawer drive additionally requires the no-media/door-closed qualifier. `zpodd_on_suspend` samples this condition and only sets `zp_ready` after it remains true for `zpodd_poweroff_delay` seconds. `zpodd_zpready` returns the cached decision.

Poweroff flow disables SCSI disk events to prevent polling from waking the drive, marks `powered_off`, and enables ACPI wake on the ATA transport device. Wake notification flow handles `ACPI_NOTIFY_DEVICE_WAKE` while the SCSI generic device is runtime suspended: it records `from_notify` and requests runtime resume. Post-poweron flow clears powered-off state, ejects the tray for drawer drives when the wake came from a user button notification, clears readiness sampling flags, and re-enables disk events.

## State And Persistence
All state is in memory and synchronized by the PM core according to the file comments. `struct zpodd` persists for the life of the ATA device. Runtime transitions mutate `from_notify`, `zp_ready`, `last_ready`, `zp_sampled`, and `powered_off`; ACPI wake state and SCSI disk-event polling are changed while the drive is powered down. No disk or firmware persistent settings are written.

## Dependencies And Integration Points
The file depends on ATAPI command execution (`ata_exec_internal`, TEST UNIT READY, REQUEST SENSE), libata device/taskfile helpers, SCSI device disk-event controls, ACPI companion and wake APIs, ACPI notify handlers, runtime PM, PM QoS exposure, jiffies/time helpers, and CD-ROM command definitions. It is compiled behind `CONFIG_SATA_ZPODD`; `libata.h` provides no-op stubs otherwise.

## Risks And Edge Cases
Sense-code interpretation is device-specific and conservative; unsupported or malformed GET CONFIGURATION data disables ZPODD. Drawer wake behavior sends an eject command after link recovery, so failures there should not block resume but affect UX. Notification install/remove assumes a valid ACPI handle once initialization accepted the companion. `zpodd_exit` calls remove unconditionally for initialized devices; callers must only use it after successful init state exists. Delayed readiness avoids rapid power cycling but can leave power savings disabled if media polling or transient sense changes reset sampling.

## Test Signals
Test with ACPI-poweroff-capable slot and drawer optical drives, unsupported optical mechanisms, media present/absent and drawer open/closed states, runtime suspend with `zpodd_poweroff_delay` boundaries, ACPI wake notification from eject button, resume path with tray ejection for drawer drives, media polling suppression/restoration, module parameter changes, and builds with `CONFIG_SATA_ZPODD` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-zpodd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata.h -->
# sources/distributed-fs/ceph-client/drivers/ata/libata.h

## Purpose
`libata.h` is libata’s internal subsystem header. It collects private constants, configuration-dependent stubs, inline helpers, and cross-file function declarations for libata core, SATA, ACPI, SCSI translation, error handling, port multipliers, SFF, and ZPODD. It is the local contract between the libata implementation files rather than the public kernel ATA API.

## Important APIs, Types, And Functions
The header defines `DRV_NAME`, `DRV_VERSION`, the `ATA_DNXFER_*` selector constants, `ATA_PORT_TYPE_NAME`, and helpers such as `ata_sstatus_online`, `ata_dev_is_zac`, and `ata_port_eh_scheduled`. It declares core functions for taskfile/LBA conversion, read/write taskfile construction, internal command execution, readiness waits, IDENTIFY/revalidation/configuration, power state taskfiles, resource freeing, transfer mask limiting, queued-command issue/complete/free, ATAPI DMA checks, byte swapping, link online/offline checks, device/link initialization, ioctl handlers, speed strings, and log-page reads.

Subsystem sections declare optional SATA host helpers, ACPI bind/resume/power helpers with no-op stubs when disabled, SCSI translation and hotplug functions from `libata-scsi.c`, EH functions and reporting helpers, optional SATA PMP helpers with `-EINVAL`/`-EOPNOTSUPP` stubs, optional SFF init/flush helpers, and optional ZPODD functions with stubs when disabled.

## Control Flow
The header has no standalone runtime flow, but it defines compile-time control flow through `#ifdef CONFIG_*` sections. Callers can invoke ACPI, PMP, SFF, or ZPODD helpers without scattering feature checks throughout implementation files; disabled configurations resolve to inline no-ops or error-returning stubs.

## State And Persistence
The header declares global module parameters and shared objects such as `atapi_passthru16`, `libata_fua`, `libata_noacpi`, `libata_allow_tpm`, `ata_port_type`, and `ata_dev_phys_link`. It does not own persistent storage itself. Inline helpers inspect live fields such as SATA status, ATA device class/IDENTIFY data, and port EH flags.

## Dependencies And Integration Points
This file is included by libata implementation units to share private interfaces. It bridges libata core with SCSI (`struct scsi_device`, `struct scsi_cmnd`, `struct Scsi_Host`), block queue limits, ACPI, SATA/PMP, SFF, EH, and ZPODD code. `DRV_VERSION` is consumed by the SCSI VPD ATA information page in `libata-scsi.c`, and `ATA_PORT_TYPE_NAME` is used by the transport class.

## Risks And Edge Cases
Because this is an internal umbrella header, declaration drift can break builds or subtly change feature behavior across many files. Stub return values matter: callers may treat `-EINVAL`, `-EOPNOTSUPP`, `false`, or no-op differently. Inline helper changes can affect hot paths and EH decisions globally. The four-character `DRV_VERSION` constraint is explicitly documented and used in fixed-size response data.

## Test Signals
The main signal is matrix build coverage across `CONFIG_ATA_ACPI`, `CONFIG_SATA_HOST`, `CONFIG_SATA_PMP`, `CONFIG_ATA_SFF`, and `CONFIG_SATA_ZPODD` enabled/disabled combinations. Runtime smoke tests should cover SCSI queueing, EH scheduling, SFF init/exit, PMP absence stubs, ACPI disabled behavior, and ZPODD disabled no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata.h -->
