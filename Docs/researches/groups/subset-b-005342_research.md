# subset-b-005342 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_target.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_target.h

Purpose: shared qla2xxx Fibre Channel target-mode contract. It defines firmware IOCB layouts, target command/session state, task-management constants, and the callback table used by `qla_target.c` to call into `tcm_qla2xxx.c`.

Important APIs/types: `struct qla_tgt_func_tmpl`, `struct qla_tgt`, `struct qla_tgt_cmd`, `struct qla_tgt_mgmt_cmd`, `struct qla_tgt_srr`, ATIO/CTIO/NACK/ABTS layouts, and exported `qlt_*` prototypes. Inline helpers validate/correct ATIO7 FCP command size, extract data length, test initiator/target/dual mode, convert S_ID to a btree key, and free offset-adjusted scatterlists.

Control flow: firmware response entries arrive as ATIO, CTIO completion, immediate notify, SRR, or ABTS packets and are decoded with these packed structs. `qla_target.c` owns low-level queue processing, while the TCM module fills `qla_tgt_func_tmpl` callbacks for command allocation, submission, session lookup, DIF policy, task management, and teardown.

State and persistence: state is in memory only: target stop flags, session counts, wait queues, SRR lists, reset generation counts, command flags, DIF metadata, trace flags, and hardware exchange identifiers. Persistent behavior is indirect through hardware queues and target-core sessions.

Dependencies and integration: depends on `qla_def.h`, `qla_dsd.h`, target-core types, qla2xxx hardware structures, DMA scatterlists, and Fibre Channel wire formats. Build-time `BUILD_BUG_ON` checks in the TCM module rely on these packet sizes.

Risks: packed hardware ABI drift, endian mistakes, handle-bit collisions, stale session lookup during teardown, SRR retry loops, and DIF metadata mismatch. Test signals include target-mode login/logout, ATIO corruption handling, ABTS/TMR responses, SRR accept/reject, DIF error injection, queue full/retry, and structure-size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_target.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.c

Purpose: executes 27xx firmware-dump templates to capture adapter registers, RAM, queues, trace buffers, shadow pointers, and firmware/driver metadata into qla2xxx dump buffers.

Important APIs/functions: public entry points are `qla27xx_fwdt_calculate_dump_size()`, `qla27xx_fwdt_template_size()`, `qla27xx_fwdt_template_valid()`, `qla27xx_mpi_fwdump()`, and `qla27xx_fwdump()`. The private dispatcher maps entry types 0, 255, and 256-278 to handlers for reads, writes, RAM dumps, queues, FCE/EFT buffers, scratch records, remote registers/RAM, PCI config, conditional entries, and PEP register access.

Control flow: validation checks template type and checksum. Size calculation walks entries with `buf == NULL`, increasing `len` without touching hardware side effects. Capture copies the template into the output buffer, edits timestamp/driver/firmware fields, then walks entries with a live buffer. Entries may modify the copied template, skip unsupported regions by setting `DRIVER_FLAG_SKIP_ENTRY`, or abort by returning `INVALID_ENTRY`.

State and persistence: dumps update `fw_dump_len`, `fw_dumped`, `mpi_fw_dump_len`, `mpi_fw_dumped`, and `num_mpi_reset`, then post a firmware-dump uevent. Captured data persists only in allocated in-kernel dump buffers until userspace consumes or clears it.

Dependencies and integration: uses qla2xxx register accessors, mailbox RAM dump helpers, queue maps, target-mode ATIO rings, PCI config reads, `jiffies`, hardware locks, and uevents. Target-mode queue capture is gated by `QLA_TGT_MODE_ENABLED()`.

Risks: template size/checksum trust boundaries, insufficient output sizing, buffer pointer arithmetic, hardware side effects from write/pause/reset entries, lock misuse, and stale template entries for missing queues or buffers. Test signals include valid/invalid checksum templates, no-buffer paths, repeated MPI dumps using spare space, missing FCE/EFT buffers, RAM dump mailbox failures, and residual-size logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.h

Purpose: declares the packed on-flash/in-memory 27xx firmware dump template format consumed by `qla_tmpl.c`.

Important APIs/types: `struct qla27xx_fwdt_template` contains template type, entry offset, template size, entry count, timestamp, checksum, driver info, saved state, and firmware version fields. `struct qla27xx_fwdt_entry` is a tagged entry with a common header and unions for entry types 0, 255, and 256-278. Defines enumerate entry kinds, RAM areas, queue types, host buffer types, and capture/driver flags.

Control flow: the executor reads `entry_offset`, starts with `entry_count`, advances by each entry header `size`, and dispatches on `hdr.type`. Fields in each union drive the hardware access pattern: register width/count, bank selection, RAM address ranges, queue type, buffer length, conditional operands, or PEP command/data addresses.

State and persistence: the header contains fields that are overwritten in the copied dump template during capture, including timestamp, driver info, firmware version, dynamic RAM ranges, queue counts, buffer sizes, and skip flags. No standalone state exists in the header.

Dependencies and integration: depends on qla2xxx register layout via `IOBASE_ADDR`, Linux bit macros, endian types, and packed hardware ABI semantics. The structures must match firmware-authored template data exactly.

Risks: flexible `t275.buffer[]` bounds, untrusted template size/count, packed alignment, endian conversion omissions, and adding entry types without updating the executor dispatch table. Test signals include template checksum validation, bounds truncation for write-buffer entries, unknown-entry skip behavior, and ABI size/layout review against firmware template documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_version.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_version.h

Purpose: central qla2xxx driver version constants.

Important APIs/types: `QLA2XXX_VERSION` is `"10.02.10.100-k"` and numeric components are exposed as `QLA_DRIVER_MAJOR_VER`, `QLA_DRIVER_MINOR_VER`, `QLA_DRIVER_PATCH_VER`, and `QLA_DRIVER_BETA_VER`.

Control flow: no runtime control flow. Other files include or reference these constants for module/version reporting, target fabric version strings, firmware dump driver info parsing, and diagnostics.

State and persistence: no mutable state. Persistence is release metadata embedded into compiled objects and visible to userspace through module/configfs/sysfs reporting.

Dependencies and integration: consumed by qla2xxx core and `tcm_qla2xxx.c`; `qla_tmpl.c` also parses `qla2x00_version_str` to encode driver information into firmware dumps.

Risks: inconsistent string/numeric version updates can make diagnostics misleading. Numeric constants with leading zero formatting should be treated as display metadata. Test signals are build success, module version output, target configfs version output, and firmware dump driver-info fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.c

Purpose: LIO/target-core fabric module for qla2xxx Fibre Channel target mode, including NPIV support. It translates qla2xxx target callbacks into target-core command, session, TPG, and configfs operations.

Important APIs/functions: WWN parsers/formatters; command lifecycle helpers `tcm_qla2xxx_get_cmd()`, `handle_cmd()`, `write_pending()`, `queue_data_in()`, `queue_status()`, `handle_data()`, and release/free callbacks; task management translation in `handle_tmr()`; session maps by FC S_ID and loop ID; TPG/lport creation, enabling, and dropping; fabric ops `tcm_qla2xxx_ops` and `tcm_qla2xxx_npiv_ops`.

Control flow: qla2xxx receives ATIO/TMR events and calls the registered `qla_tgt_func_tmpl`. Normal SCSI commands allocate a pre-tagged `qla_tgt_cmd`, attach it to the session command list, initialize a target-core `se_cmd`, submit it, and later call qla low-level transmit functions for XFER_RDY, DATA_IN, or status. WRITE completions are queued to a workqueue before target execution. Configfs lport/TPG creation registers the qla target lport; NPIV creation creates an FC vport before binding the target lport.

State and persistence: keeps per-session command lists, krefs, dynamic NodeACL/session maps in a 24-bit S_ID btree and 16-bit loop-id array, configfs attributes, TPG enable flags, and a reclaim workqueue. User-created configfs objects are persistent only while configured in target-core/configfs.

Dependencies and integration: depends on target-core fabric APIs, qla target APIs, SCSI/FC transport, btree, workqueues, `utsname`, and packed IOCB ABI from `qla_target.h`.

Risks: session map races during logout/update, command freeing while firmware owns CTIO, queue-full retry interactions with aborted commands, NPIV host reference balancing, and DIF option mismatches. Test signals include configfs create/drop for qla2xxx and qla2xxx_npiv, demo-mode ACL sessions, login/logout storms, TMR/ABTS translation, WRITE with DIF errors, aborted command paths, and module init `BUILD_BUG_ON` layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.h

Purpose: private data model for the qla2xxx target-core fabric module.

Important APIs/types: defines `TCM_QLA2XXX_NAMELEN`, `TCM_QLA2XXX_DEFAULT_TAGS`, `struct tcm_qla2xxx_nacl`, `struct tcm_qla2xxx_tpg_attrib`, `struct tcm_qla2xxx_tpg`, `struct tcm_qla2xxx_fc_loopid`, and `struct tcm_qla2xxx_lport`.

Control flow: these structures are allocated by configfs lport/TPG creation, populated during session setup, queried by target-core callbacks, and cleaned during TPG/lport removal. The lport contains both lookup structures needed by incoming firmware events: S_ID btree and loop-id array.

State and persistence: state includes WWPN/WWNN values, formatted WWN strings, NodeACL to `fc_port` links, target portal attributes, TPG enabled bit, pointer to qla VHA, and TPG=1 shortcut for physical mode. It persists for the lifetime of configfs fabric objects and active sessions.

Dependencies and integration: includes target-core base, Linux btree, and `qla_target.h`, tying fabric-level state to qla low-level target command/session structs.

Risks: fixed name buffer length, large vmalloc loop-id map allocation, stale `fc_port` pointers, TPG=1 assumption for non-NPIV mode, and synchronization requirements around lookup maps. Test signals include WWN formatting/parsing, lport allocation failure cleanup, session lookup by S_ID and loop ID, and configfs attribute visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Kconfig

Purpose: declares the `SCSI_QLA_ISCSI` tristate for QLogic ISP4XXX, ISP82XX, and ISP83XX iSCSI host adapters.

Important APIs/types: the option depends on `PCI`, `SCSI`, and `NET`, and selects `SCSI_ISCSI_ATTRS` plus `ISCSI_BOOT_SYSFS`. Help text identifies supported 40xx, 8022, and 8032 families.

Control flow: no runtime logic; it controls whether the qla4xxx module and its transport/sysfs integration are built.

State and persistence: build configuration only. It influences kernel/module availability and generated config state.

Dependencies and integration: ties this driver to PCI probing, SCSI midlayer, networking, iSCSI transport attributes, and iSCSI boot sysfs.

Risks: missing selected transport features would break attribute/boot paths; family help text must stay in sync with PCI IDs and source support. Test signals are Kconfig dependency resolution, module build under `m` and `y`, and boot sysfs/iSCSI attribute registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Makefile -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Makefile

Purpose: builds the qla4xxx iSCSI host adapter driver object list.

Important APIs/types: `qla4xxx-y` aggregates OS glue, init, mailbox, IOCB, ISR, NX/8xxx support, NVRAM, debug, attributes, BSG, and 83xx support objects. `obj-$(CONFIG_SCSI_QLA_ISCSI)` emits `qla4xxx.o`.

Control flow: no runtime flow; object ordering controls linked driver composition.

State and persistence: build artifact state only.

Dependencies and integration: integrates all qla4xxx implementation files behind the Kconfig symbol. The inclusion of `ql4_attr.o`, `ql4_bsg.o`, and `ql4_83xx.o` makes sysfs, BSG vendor commands, and 83xx reset paths part of every qla4xxx build.

Risks: omitting an object causes unresolved symbols or missing runtime features; adding chip-specific files unconditionally can expose compile dependencies across adapter families. Test signals are clean module build, modpost, and probe-time availability of sysfs/BSG/83xx ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.c

Purpose: ISP83xx/8042 hardware support for qla4xxx, covering direct/indirect CRB access, flash reads, IDC driver locks and reset ownership, reset-template execution, firmware restart, mailbox/interrupt routing, pause-frame configuration, and detach detection.

Important APIs/functions: register accessors `qla4_83xx_rd_reg*`/`wr_reg*`; flash lock/read helpers; `qla4_83xx_drv_lock()`/`drv_unlock()` with lock recovery; reset ownership `qla4_83xx_can_perform_reset()`; IDC reset flow `qla4_83xx_need_reset_handler()` and `qla4_83xx_isp_reset()`; reset template load/execute; `qla4_83xx_start_firmware()`; interrupt and mailbox helpers; `qla4_83xx_disable_pause()`; `qla4_83xx_is_detached()`.

Control flow: indirect register access programs a per-function window then reads/writes the wildcard register. Reset begins by marking `DEV_NEED_RESET`, electing a reset owner based on active NIC/iSCSI/FCoE functions, waiting for other functions to ACK through IDC registers, bootstrapping firmware, executing flash-provided stop/init/start reset-template sequences, copying bootloader from flash, and checking command PEG state.

State and persistence: adapter state lives in CRB registers, flash, `ha->flags`, `dpc_flags`, `reset_tmplt`, timeouts, completions, interrupt-on bits, and IDC control bits. Flash content and reset templates persist on device; driver fields are runtime only.

Dependencies and integration: relies on `ql4_def.h`, 8xxx common helpers, mailbox and minidump paths, PCI MMIO, vmalloc, completions, and qla4xxx `isp_operations`.

Risks: IDC lock deadlock/recovery correctness, reset-owner election with multifunction devices, unchecked flash template trust, endian/alignment mistakes in reset templates, mailbox interrupt races, and reset suppression via `ql4xdontresethba`. Test signals include indirect register readback, flash misalignment failures, lock recovery after held locks, reset owner/non-owner paths, checksum failures, minidump collection, interrupt enable/disable idempotence, and detach detection when `DRV_ACTIVE` drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.h

Purpose: register map, constants, and packed template/minidump structures for ISP83xx/8042 qla4xxx support.

Important APIs/types: defines CRB/flash/IDC/reset/mailbox register offsets, flash command/timeouts, reset-template opcodes, `struct qla4_83xx_reset_template_hdr`, entry headers, poll/RMW/list entries, minidump entry variants, IDC info, and PEX-DMA descriptor formats.

Control flow: `ql4_83xx.c` interprets these opcodes to run stop/start/init reset sequences from flash. Register constants drive indirect access, lock handling, firmware boot, pause-frame setup, link state, and mailbox interrupt configuration.

State and persistence: describes persistent flash-resident templates and device registers, plus runtime `qla4_83xx_reset_template` fields for offsets, sequence index, saved array values, and sequence completion/error flags.

Dependencies and integration: included by `ql4_def.h`, so these definitions are globally available to qla4xxx source. Minidump structures integrate with common qla8xxx minidump headers.

Risks: register offset mistakes can wedge hardware; packed structure changes must match firmware; checksum/version constants must track flash templates; PEX-DMA descriptor bit fields need precise layout. Test signals include reset-template signature/version validation, opcode coverage, minidump parsing, PEX-DMA read sizing, and register access smoke tests on 8032/8042 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_attr.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_attr.c

Purpose: qla4xxx sysfs exposure for firmware dumps and read-only SCSI host adapter attributes.

Important APIs/functions: `qla4_8xxx_sysfs_read_fw_dump()`, `qla4_8xxx_sysfs_write_fw_dump()`, `qla4_8xxx_alloc_sysfs_attr()`, `qla4_8xxx_free_sysfs_attr()`, show methods for firmware version, serial, iSCSI/option ROM versions, board ID, firmware state, physical port/function counts, model, timestamps, load source, and uptime, plus `qla4xxx_host_groups`.

Control flow: `fw_dump` binary reads return data only when dump-reading is enabled. Writes at offset zero parse commands: `0` clears dump-reading/dumped flags and reloads the template, `1` makes an existing dump readable, and `2` requests reset/dump collection under IDC lock when the device is ready and this function can own reset. Host attributes mostly format cached fields; a few refresh firmware state/uptime first.

State and persistence: manipulates `AF_82XX_DUMP_READING`, `AF_82XX_FW_DUMPED`, `AF_8XXX_RST_OWNER`, `AF_FW_RECOVERY`, firmware dump buffers, and device state registers. Attribute values reflect runtime adapter state and firmware metadata.

Dependencies and integration: uses SCSI host kobjects, sysfs binary attributes, qla4xxx firmware helpers, IDC lock ops, and qla4xxx chip-family predicates.

Risks: write-command semantics can trigger disruptive reset recovery; `buf[1] = 0` assumes sufficient write count; some show paths return `-ENOSYS` for 40xx; `fw_load_src` may print NULL for unknown values. Test signals include sysfs create/remove, fw_dump read/clear/trigger, reset-active interactions, unsupported-adapter returns, and attribute formatting for every chip family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.c

Purpose: handles iSCSI BSG host-vendor commands for qla4xxx management operations.

Important APIs/functions: `qla4xxx_bsg_request()` dispatches `ISCSI_BSG_HST_VENDOR` to `qla4xxx_process_vendor_specific()`. Vendor handlers cover flash read/update, ACB state, NVRAM read/update, restore defaults, get ACB, generic diagnostic mailbox commands, and loopback diagnostics with pre/post port configuration.

Control flow: each operation obtains the `scsi_qla_host`, rejects offline PCI channels or reset-active adapters, validates adapter family and payload length, copies data between BSG scatterlists and coherent DMA buffers when needed, calls firmware/mailbox helper APIs, sets `DID_OK`, `DID_ERROR`, or `DID_TIME_OUT`, and completes the BSG job. Loopback diagnostics temporarily set internal/external loopback, wait for IDC and link completions, execute mailbox diagnostics, then restore DCBX/default port config.

State and persistence: flash/NVRAM/default updates persist on the adapter. Runtime state includes `flash_state`, reset flags, loopback flags, IDC/link completion flags, firmware state, and reply payload lengths.

Dependencies and integration: depends on iSCSI BSG request/reply layouts, SCSI host private data, PCI DMA, qla4xxx mailbox and flash/NVRAM/ACB helpers, 83xx port config helpers, and qla4xxx reset-state predicates.

Risks: vendor command fields are trusted as offsets/options, concurrent flash state is only guarded by `flash_state`, mailbox diagnostics can be disruptive, loopback restore failures schedule adapter reset, and all paths must call `bsg_job_done()` exactly when ownership completes. Test signals include invalid command dispatch, short payload rejection, reset-active `-EBUSY`, DMA allocation failure, max NVRAM bounds, flash operation serialization, diagnostic mailbox replies, and loopback timeout/restore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.h

Purpose: shared vendor command numbers for qla4xxx iSCSI BSG handling.

Important APIs/types: defines command IDs `QLISCSI_VND_READ_FLASH` through `QLISCSI_VND_DIAG_TEST`, plus diagnostic subcommands for DDR, on-chip memory, NVRAM, flash ROM, internal/external loopback, DMA transfer, and self-tests.

Control flow: `ql4_bsg.c` switches on these constants in the first vendor command word and diagnostic subcommand words to choose management operations.

State and persistence: no state; constants identify operations that may read or modify persistent flash/NVRAM and runtime adapter configuration.

Dependencies and integration: must match userspace management tools and qla4xxx firmware mailbox expectations.

Risks: ABI number changes would break userspace; comments note some diagnostics are ISP4XXX-only, so dispatch must keep adapter-family checks. Test signals are userspace BSG command compatibility and invalid subcommand rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.c

Purpose: debug dump helpers for qla4xxx buffers, legacy registers, mailbox registers, page-selected registers, and 8xxx PEG halt state.

Important APIs/functions: `qla4xxx_dump_buffer()`, `qla4xxx_dump_registers()`, and `qla4_8xxx_dump_peg_reg()`.

Control flow: buffer dump prints hex bytes in 16-byte rows. Register dump branches by adapter family: 8022 mailbox registers, 4010 register pages, or 4022/4032 register pages with page selection via `ctrl_status`. PEG dump reads halt-status registers and, for 8022, PEG network program counters.

State and persistence: no persistent state, but register dump briefly writes page-select values for 4022/4032 debug output. Output goes to kernel log.

Dependencies and integration: depends on `ql4_def.h`, chip predicates, register structures, `readw/readl/writel`, qla8xxx direct register reads, and debug macros.

Risks: register dumping during unstable hardware/reset can fault or produce stale values; page selection side effects should not race with normal access; high-volume printk output can flood logs. Test signals include dump output on each supported family, reset-time PEG dump, and ensuring debug paths are gated by logging settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.h

Purpose: compile-time and runtime debug macro controls for qla4xxx.

Important APIs/types: `DEBUG`, `DEBUG2`, `DEBUG2_3`, `DEBUG3`, `DEBUG4`, `DEBUG5`, `DEBUG7`, and `DEBUG9`. `QL_DEBUG_LEVEL_2` is enabled by default, but `DEBUG2` only emits when `ql4xextended_error_logging == 2`; `DEBUG2_3` emits unconditionally when level 2 is compiled.

Control flow: macros either execute the supplied statement block or compile to no-op depending on compile-time defines and runtime logging level.

State and persistence: no direct state except dependency on the external `ql4xextended_error_logging` variable. Logging persists in kernel logs.

Dependencies and integration: included by most qla4xxx files and wraps `ql4_printk`/`pr_info` diagnostics.

Risks: side effects inside disabled debug arguments will not run; enabled verbose levels can flood logs; `DEBUG2_3` being unconditional under level 2 means some messages are always compiled and executed. Test signals include builds with different debug defines and runtime extended logging value checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_def.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_def.h

Purpose: central qla4xxx definitions header: kernel includes, PCI IDs, constants, queues, command/session state, adapter state, operation vectors, inline predicates, and lock/reset helpers.

Important APIs/types: `struct qla4xxx_cmd_priv`, `struct srb`, `struct mrb`, AEN log structs, `struct ddb_entry`, DDB discovery tuples, `struct isp_operations`, `struct ipaddress_config`, CHAP/boot structs, `struct scsi_qla_host`, task/endpoint/connection structs, chip-family predicates, adapter state helpers, flash/NVRAM/driver lock wrappers, and `ql4xxx_reset_active()`.

Control flow: this header supplies the adapter-wide state machine vocabulary used by all implementation files. `isp_operations` virtualizes chip-specific operations for interrupts, firmware start/reset, register access, IDC locks, ROM recovery, mailbox queueing, and mailbox interrupt processing. Inline helpers route register/lock access by adapter family and gate I/O through `adapter_up()` and `ql4xxx_reset_active()`.

State and persistence: `struct scsi_qla_host` is the main runtime state container: flags, DPC flags, queues, DMA memory, mailbox status, DDB maps, firmware info, timers, workqueues, dump buffers, CHAP/boot/sysfs state, flash state, 8xxx register windows, reset template, completions, and saved ACB. Persistent device configuration is represented through flash/NVRAM/CHAP/DDB/boot metadata but cached in memory.

Dependencies and integration: bridges Linux PCI, SCSI, iSCSI transport, BSG, networking, qla firmware/NVRAM/NX/83xx headers, and driver implementation files.

Risks: global header coupling, flag-bit collisions, large mutable host state races, chip-family conditional mistakes, reset-active false negatives, and lock wrapper misuse. Test signals include all-family compile coverage, probe/remove, interrupt/mailbox paths, reset/recovery, BSG/sysfs operations, iSCSI session relogin, DDB state transitions, and sparse/lockdep review of host-state access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_def.h -->
