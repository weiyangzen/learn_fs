# Research: subset-b-005326

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_main.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_main.c

Purpose: this is the main PCI/libfc/libfcoe integration file for the QLogic FastLinQ FCoE offload driver. It owns module parameters, PCI probe/remove/recovery, libfc transport templates, FIP/FCoE link bring-up, LL2 receive/transmit, offloaded remote-port session setup, MSI-X completion dispatch, queue/DMA allocation, FC statistics, NPIV vports, devlink/MFW TLV callbacks, and SCSI error handlers.

Important APIs, types, and entry points: the file exports or installs `qedf_probe`, `qedf_remove`, `qedf_shutdown`, `qedf_suspend`, `qedf_init`, `qedf_cleanup`, `qedf_process_cqe`, `qedf_fp_io_handler`, `qedf_ctx_soft_reset`, `qedf_wait_for_upload`, `qedf_schedule_hw_err_handler`, `qedf_get_protocol_tlv_data`, `qedf_get_generic_tlv_data`, and `qedf_stag_change_work`. It binds `qedf_host_template` into the SCSI midlayer, `qedf_lport_template` into libfc, `qedf_fc_transport_fn` and `qedf_fc_vport_transport_fn` into FC transport, `qedf_ll2_cb_ops` into QED LL2, and `qedf_cb_ops` into QED common/FCoE callbacks. State is centered on `struct qedf_ctx`, `struct qedf_rport`, `struct qedf_fastpath`, global queues, BDQ buffers, and the command manager allocated elsewhere.

Control flow: module init validates debug/default priority parameters, obtains `qed_fcoe_ops`, creates debugfs and FC transport templates, creates the global I/O workqueue, and registers the PCI driver. Probe allocates or reuses an `fc_lport`, initializes `qedf_ctx`, probes QED hardware, fills device info, allocates PF queue parameters, registers callbacks, prepares status blocks, starts slowpath and FCoE function, initializes BDQ producer doorbells, derives MAC/WWNN/WWPN, allocates the command manager, attaches the SCSI host, starts LL2, configures the FCoE controller/lport, creates timer/DPC workqueues, advertises driver state, sets link up, and starts FC discovery. Removal reverses that order: mark unloading, log off fabric or link down for recovery, wait for session uploads, stop debugfs/workqueues/LL2/fastpath, destroy SCSI/libfc/libfcoe constructs for normal removal, free command manager and queues, stop QED, unregister devlink, and put the SCSI host.

Link and FIP behavior: QED link/DCBX callbacks drive `qedf_link_update`, `qedf_bw_update`, and `qedf_dcbx_handler`. Link-up waits for DCBX unless bypassed, issues FIP VLAN discovery via repeated `qedf_fcoe_send_vlan_req`, falls back to `qedf_fallback_vlan`, and calls `fcoe_ctlr_link_up`. Link-down can be delayed by `link_down_tmo`; if the link returns before timeout, `qedf_link_recovery` resets the FCoE controller, rediscovers VLAN/FCF, sends FLOGI, waits for completion, and ADISCs existing rports rather than tearing all libfc state down. FLOGI is intercepted by `qedf_elsct_send`/`qedf_flogi_resp` to count failures and set the FCoE data source MAC from granted MAC, selected FCF map, or `fc_fcoe_set_mac`.

I/O and frame flow: `qedf_xmit` is libfc's frame-send path. It filters frames addressed to local NPIV ports, requires selected FCF, LL2 started, and link up, lets FIP controller consume eligible ELS frames, optionally sends ADISC on an offloaded session, appends FCoE CRC/EOF, pushes Ethernet/FCoE headers, applies VLAN priority, updates libfc stats, and calls `qed_ops->ll2->start_xmit`. RX enters through `qedf_ll2_rx`, is deferred to `qedf_ll2_process_skb`, demultiplexes FIP to `qedf_fip_recv` and FCoE to `qedf_recv_frame`. `qedf_recv_frame` validates lport state, strips CRC/EOF, drops data/BLS/LOGO/address-mismatched frames that should not be handled on LL2, routes NPIV frames, and passes accepted frames to `fc_exch_recv`.

Offload and completion flow: libfc rport events call `qedf_rport_event_handler`. On `RPORT_EV_READY`, FCP target ports get a send queue, QED connection handle, firmware offload parameters, source/destination FC IDs/MACs, VLAN, FC tape flags, and are added to `qedf->fcports` with `QEDF_RPORT_SESSION_READY`. LOGO/FAILED/STOP marks an upload in progress, flushes active I/O, destroys/releases the QED connection, frees SQ memory, removes the fcport, and decrements `num_offloads`. MSI-X handlers disable the status block, drain completion queues by copying CQEs into mempool work items, process unsolicited CQEs immediately when fastpath ID matters, and re-enable interrupts only after producer/consumer state is stable. Deferred `qedf_process_cqe` dispatches good/error/cleanup/ABTS/warning/local/dummy completions to specialized handlers in other qedf files and increments `free_sqes`.

State and persistence: persistent runtime state is in kernel memory and firmware/device state, not on disk. Module parameters tune discovery, queue depth, logging, link-down timeout, recovery, and priority. `struct qedf_ctx` holds atomic link/DCBX state, flags such as probing/unloading/recovery/STAG, VLAN/prio, workqueues, mempools, DMA queues, BDQ producer indices, devlink, debug/sysfs/GRC buffers, lport, command manager, and rport list. DMA-coherent allocations back status blocks, completion queues, queue PBLs, send queues, and BDQs. The driver updates MFW driver state and provides TLV snapshots but does not persist configuration itself.

Dependencies and integration points: this file depends heavily on Linux SCSI midlayer, FC transport, libfc, libfcoe, PCI, debugfs/sysfs helpers, workqueues, MSI-X, DMA APIs, `phylink` link modes, and QED common/FCoE/LL2 ops. It integrates with functions declared in other qedf files for FIP send/receive, queuecommand, command manager, completions, ABTS/TMF, sysfs, debugfs, GRC dumps, and protocol-specific offload details.

Risks: the file has many race-sensitive boundaries: link update vs remove, recovery vs normal probe/remove, rport upload vs CQE/frame delivery, NPIV teardown vs base-port teardown, and abort/error handling vs command reference lifetimes. A notable local risk is `qedf_prepare_sb`: the `err:` label returns `0`, so allocation/init failure inside the loop can be reported as success after logging. Cleanup paths rely on paired allocations and labels; missed frees around probe errors would leak DMA memory or workqueues. `qedf_wait_for_upload` waits up to about 60 seconds and then only logs remaining sessions; remove/recovery continues afterward. Frame validation and VLAN fallback are correctness-critical because wrong MAC/VLAN selection can make FCoE discovery fail or misroute frames.

Test signals: meaningful coverage would include module load/unload with and without MSI-X, link up/down with DCBX delayed and bypassed, FIP VLAN response and fallback VLAN, FLOGI retry/STAG reset behavior, NPIV create/delete/disable, rport ready/stop offload lifecycle, SCSI abort/LUN reset/host reset paths, LL2 RX/TX frame filtering, CQE dispatch for all completion types, recovery handler remove/probe cycle, debugfs/sysfs creation, devlink fatal error reporting, and MFW TLV population. Static analysis should inspect the probe error labels, DMA allocation/free symmetry, spinlock/RCU use around `fcports`, and interrupt teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_version.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_version.h

Purpose: this header centralizes the qedf driver version exposed through module metadata, FC host attributes, and QED slowpath parameters.

Important definitions: it defines `QEDF_VERSION` as `8.42.3.0` and the decomposed major/minor/revision/engineering values as `8`, `42`, `3`, and `0`. `qedf_main.c` uses the string in `MODULE_VERSION`, driver banners, FDMI/host symbolic names, and FC host driver version fields. Probe passes the numeric components into `struct qed_slowpath_params` so firmware/common QED code sees the same driver version.

Control flow and state: there is no control flow or mutable state. The file is included by qedf headers/implementation and compiled into consumers as preprocessor constants.

Dependencies and integration points: the values must stay consistent with packaging/release metadata and with the QED common driver expectations. The header is part of the kernel driver ABI visible through sysfs/modinfo-style surfaces rather than a runtime subsystem.

Risks: stale or mismatched version constants can make diagnostics, support scripts, firmware compatibility checks, and FDMI inventory misleading. Because the string and numeric macros are separate, updates must change all five definitions together.

Test signals: build-time inclusion by `qedf_main.c`, `modinfo qedf` reporting the expected version, FC host `driver_version` matching the macro, and probe logs showing matching slowpath version fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/Kconfig

Purpose: this Kconfig entry exposes the QLogic FastLinQ 41000-series iSCSI offload initiator driver as `CONFIG_QEDI`.

Important definitions: `config QEDI` is a tristate named "QLogic QEDI 25/40/100Gb iSCSI Initiator Driver Support". It depends on `PCI`, `SCSI`, `UIO`, and `QED`, and selects `SCSI_ISCSI_ATTRS`, `QED_LL2`, `QED_OOO`, `QED_ISCSI`, and `ISCSI_BOOT_SYSFS`.

Control flow and state: Kconfig does not execute at runtime. Its selected symbols shape compilation and ensure the driver has SCSI/iSCSI transport attributes, QED iSCSI/LL2/offload support, and iSCSI boot sysfs support available.

Dependencies and integration points: the entry integrates the qedi module into the kernel SCSI driver menu and couples it to QED common hardware support. `UIO` is required because qedi exposes user-space networking/control plumbing elsewhere in the driver.

Risks: missing dependencies or selects would produce compile failures or runtime feature holes, especially around QED LL2/iSCSI callbacks and iSCSI boot sysfs. Over-selecting can force support code into kernels that otherwise would not include it.

Test signals: `make menuconfig` should show the option only when dependencies are available; builds for `m`, `y`, and unset should respectively build `qedi.ko`, built-in qedi objects, or no qedi objects. Compile tests should confirm selected QED and iSCSI transport symbols satisfy all included headers and external references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/Makefile

Purpose: this Makefile describes how the qedi kernel module is assembled from its source files.

Important definitions: `obj-$(CONFIG_QEDI) := qedi.o` creates the driver object when Kconfig enables it. `qedi-y` links `qedi_main.o`, `qedi_iscsi.o`, `qedi_fw.o`, `qedi_sysfs.o`, `qedi_dbg.o`, and `qedi_fw_api.o`. `qedi-$(CONFIG_DEBUG_FS)` conditionally adds `qedi_debugfs.o`.

Control flow and state: there is no runtime flow, but the object list determines which subsystems are always present and which are debugfs-gated. The unconditional objects provide PCI/lifecycle, iSCSI transport integration, firmware command/CQE handling, sysfs, logging, and firmware task-context builders.

Dependencies and integration points: the Makefile aligns with `Kconfig` and Linux kbuild conventions. It expects symbols declared in `qedi_gbl.h` to resolve across the listed objects and only includes debugfs file operations when `CONFIG_DEBUG_FS` is set.

Risks: omitting an object produces unresolved symbols or missing callbacks; adding `qedi_debugfs.o` unconditionally would break builds without debugfs support. The build list also means any new qedi source file must be explicitly added here.

Test signals: compile qedi with `CONFIG_QEDI=m/y` and `CONFIG_DEBUG_FS=y/n`; check that `qedi_debugfs.o` is present only when expected and that no unresolved symbols remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi.h

Purpose: this is the central private header for the qedi iSCSI offload driver. It defines constants, queue sizes, DMA data structures, tracing records, UIO/LL2 metadata, task/CID maps, and the top-level `struct qedi_ctx` used across qedi source files.

Important APIs and types: key constants include `QEDI_MAX_ISCSI_TASK`, `QEDI_MAX_ISCSI_CONNS_PER_HBA`, `QEDI_ISCSI_MAX_BDS_PER_CMD`, `QEDI_SQ_SIZE`, `QEDI_CQ_SIZE`, `QEDI_CMDQ_SIZE`, `QEDI_BDQ_NUM`, `QEDI_BDQ_BUF_SIZE`, local port allocation bounds, and link/recovery/shutdown flags. Important structs include `qedi_uio_ctrl`, `qedi_uio_dev`, `qedi_glbl_q_params`, `global_queue`, `qedi_fastpath`, `qedi_io_work`, `iscsi_cid_queue`, `qedi_portid_tbl`, `qedi_itt_map`, `qedi_io_log`, `qedi_bdq_buf`, `qedi_work`, `qedi_percpu_s`, and especially `qedi_ctx`. The inline `qedi_get_task_mem` indexes firmware task-context blocks by TID.

State and persistence: `qedi_ctx` is the per-adapter in-memory root. It stores SCSI/PCI/QED handles, device info, interrupt info, global queues, UIO state, LL2 receive list/thread, error and lifecycle flags, MAC/source IP, BDQ buffers and producer registers, NVM iSCSI image buffer, CID and endpoint tables, task contexts and ITT maps, link state, workqueues for TMF/offload/DPC/recovery, task index bitmap, tracing ring, SGL path counters, boot sysfs kset, and statistics lock. None of this is persisted by this header; it defines runtime structures backed by allocations in implementation files.

Control flow implications: queue and task constants constrain firmware command submission in `qedi_fw.c` and queue allocation in `qedi_main.c`. The `QEDI_NEXT_RX_IDX` macro controls LL2 RX ring wrap behavior. Flags such as `QEDI_IN_RECOVERY`, `QEDI_IN_OFFLINE`, `QEDI_IN_SHUTDOWN`, and `QEDI_BLOCK_IO` are shared synchronization signals across recovery, disconnect, and I/O submission paths.

Dependencies and integration points: the header pulls in SCSI transport iSCSI, libiscsi, SCSI host, UIO, QED common/iSCSI/LL2 interfaces, qedi debug declarations, versioning, NVM iSCSI config, and the qedi hardware software interface. It is included by most qedi implementation files and therefore is a high-blast-radius contract.

Risks: structure layout changes can affect many call sites and firmware assumptions. The driver has several fixed-size tables: 4096 tasks, 1024 connections, 256 BDQ entries, 2048 trace entries, and a firmware max of 255 BDs per command. Scatter-gather splitting and task-ID reuse must not exceed these bounds. Shared flags and lists require disciplined locking; the header documents locks but cannot enforce their use.

Test signals: build coverage for all qedi objects, probe-time allocation of `qedi_ctx` and queues, task index allocation/free stress, high queue-depth I/O with large SGLs, recovery/offline/shutdown flag transitions, debugfs I/O trace dumping, UIO open/close behavior, and static analysis for array bounds against the constants in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.c

Purpose: this file implements qedi's printk-based logging helpers behind the macros declared in `qedi_dbg.h`.

Important functions: `qedi_dbg_err`, `qedi_dbg_warn`, `qedi_dbg_notice`, and `qedi_dbg_info` format messages with function name, source line, PCI device name, and host number when a valid `qedi_dbg_ctx` is present. Warning, notice, and info logs are gated by the global `qedi_dbg_log` bitmask; errors are always printed.

Control flow and state: each helper builds a `va_format` around a varargs list and emits through `pr_err`, `pr_warn`, `pr_notice`, or `pr_info`. If the context or PCI device is unavailable, it prints a placeholder BDF. The file itself owns no persistent state beyond reading `qedi_dbg_log`.

Dependencies and integration points: all qedi sources use `QEDI_ERR`, `QEDI_WARN`, `QEDI_NOTICE`, and `QEDI_INFO` macros, so this file is central for diagnostics. It depends on kernel varargs formatting and `dev_name(&pdev->dev)`.

Risks: logging is often called in interrupt, atomic, or error paths; format strings and arguments must be safe there. Excessive enabled debug masks can flood kernel logs. Passing user buffers or non-NUL strings to these helpers would be unsafe, but normal use passes driver-controlled formats.

Test signals: compile-time format checking, module parameter changes to `qedi_dbg_log`, verifying that each log level is gated as intended, and exercising logging before PCI context initialization to confirm placeholder output is safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.h

Purpose: this header defines qedi debug masks, logging macros, debug context state, and debugfs operation descriptors.

Important APIs and types: `QEDI_LOG_*` bitmasks cover default, info, discovery, LL2, connection, events, timer, middle-path requests, SCSI task management, unsolicited messages, I/O, multi-queue, BSG, debugfs, lport, ELS, NPIV, session, UIO, TID tracking, command-list tracking, notice, and warning logs. `struct qedi_dbg_ctx` stores `host_no`, `pdev`, and optionally a debugfs dentry. The `QEDI_ERR/WARN/NOTICE/INFO` macros inject `__func__` and `__LINE__`. `struct qedi_list_of_funcs` and `struct qedi_debugfs_ops` describe writable debugfs commands. `qedi_dbg_fileops` and `qedi_dbg_fileops_seq` generate file operation initializers.

Control flow and state: the header declares logging functions implemented in `qedi_dbg.c` and debugfs lifecycle functions implemented in `qedi_debugfs.c` when available. It does not mutate state itself but exposes the global `qedi_dbg_log` mask.

Dependencies and integration points: it includes PCI, SCSI transport, filesystem, and QED common headers, and is included by core qedi files for diagnostics. Debugfs declarations integrate with `qedi_gbl.h` arrays and `qedi_main.c` host init/exit paths.

Risks: debug masks are ABI-like for operators and support tooling. Enabling `QEDI_TRACK_TID` or command-list tracking can be expensive and is documented as load-time-only. Macro misuse with a wrong context pointer can degrade logs or crash if the pointer is invalid despite the implementation's null checks.

Test signals: compile with and without `CONFIG_DEBUG_FS`, verify logging macro expansion, toggle module debug masks, create and remove per-host debugfs entries, and inspect that warning/notice high-bit masks do not collide with lower functional masks unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_debugfs.c

Purpose: this file provides qedi's debugfs hierarchy and per-host diagnostic files when `CONFIG_DEBUG_FS` is enabled.

Important functions and data: `qedi_dbg_init` creates the driver root directory, `qedi_dbg_exit` removes it, `qedi_dbg_host_init` creates `host%u` directories and files from `qedi_debugfs_ops`, and `qedi_dbg_host_exit` removes host directories. `qedi_do_not_recover` is a global debug switch exposed through the `do_not_recover` file. `qedi_debugfs_ops` defines `gbl_ctx`, `do_not_recover`, and `io_trace`; `qedi_dbg_fops` binds each to seq or command file operations. `qedi_gbl_ctx_show` dumps CQ producer/consumer context per fastpath. `qedi_io_trace_show` dumps the circular I/O trace ring.

Control flow: host init walks the debugfs ops array and creates one file per named operation. Writing `enable` or `disable` to `do_not_recover` toggles the global flag. Reading `gbl_ctx` takes `hba_lock` per queue and prints status block producer and driver consumer indices. Reading `io_trace` takes `io_trace_lock` and emits all 2048 trace records starting at the current ring index.

State and persistence: debugfs state is transient. `qedi_do_not_recover` is runtime global state that can alter TMF/cleanup behavior in `qedi_fw.c` by suppressing cleanup/abort recovery work. Trace data is stored in `qedi_ctx->io_trace_buf`, not in debugfs.

Dependencies and integration points: the file depends on debugfs, seq_file, uaccess, qedi debug macros, `qedi_ctx`, fastpath queues, status blocks, and the I/O trace ring populated by `qedi_trace_io`.

Risks: debugfs is privileged diagnostics but still must avoid races with teardown. `qedi_gbl_ctx_show` assumes fastpath/status block arrays remain valid while the file is read. The write handler compares the user buffer with command strings via `strncmp` directly on a `__user` pointer, which is a kernel-user access risk in general kernel coding style. `qedi_do_not_recover` can intentionally prevent recovery and should not be enabled in normal operation.

Test signals: mount debugfs, probe qedi, verify `/sys/kernel/debug/qedi/hostN` files, read `gbl_ctx` during I/O, enable `io_tracing` and read `io_trace`, write `enable`/`disable` to `do_not_recover`, remove the device while files are open, and run sparse/smatch for user-pointer and lifetime warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw.c

Purpose: this file is the qedi firmware command and completion path. It maps libiscsi tasks and SCSI commands into firmware SQEs/task contexts, rings doorbells, converts CQEs back into libiscsi PDUs, handles unsolicited PDUs through BDQ buffers, manages TMF/cleanup sequencing, maps/unmaps SCSI scatter-gather lists, and records optional I/O traces.

Important APIs and functions: externally used functions include `qedi_iscsi_send_ioreq`, `qedi_send_iscsi_login`, `qedi_send_iscsi_logout`, `qedi_send_iscsi_tmf`, `qedi_send_iscsi_text`, `qedi_send_iscsi_nopout`, `qedi_iscsi_cleanup_task`, `qedi_cleanup_all_io`, `qedi_clearsq`, `qedi_fp_process_cqes`, `qedi_trace_io`, and `qedi_iscsi_unmap_sg_list`. Internal helpers process each response opcode, manage BDQ buffers, ring doorbells, allocate WQE indices, split BDs, map SGLs, copy CDBs, wait for cleanup, and run abort/TMF work.

Control flow: command submission allocates a qedi task ID, zeros the firmware task context, updates the ITT map, builds an HSI PDU header, prepares TX/RX SGL task params, chooses a send-queue slot via `qedi_get_wqe_idx`, calls the relevant `init_initiator_*` builder from `qedi_fw_api.c`, adds the command to `active_cmd_list` when a response is expected, and rings the connection doorbell. SCSI I/O submission additionally maps DMA SGLs, chooses read/write based on data direction, fills connection parameters from libiscsi session settings, points sense data DMA, and sets CQ RSS number from CPU modulo queue count.

Completion flow: `qedi_fp_process_cqes` validates CQE type and CID, finds the qedi connection, handles data digest errors as libiscsi connection failures, and dispatches solicited, unsolicited, dummy, and cleanup CQEs. Solicited CQEs are associated with the containing `qedi_cmd` work item and then dispatched by opcode to SCSI, login, TMF, text, logout, or NOP handlers. Each handler builds the corresponding libiscsi response header, copies payload/sense data when needed, removes active command list nodes, updates command state to `RESPONSE_RECEIVED` or cleanup states, completes the PDU under `session->back_lock`, and frees or wakes waiting work as needed.

TMF and cleanup behavior: abort task TMFs are handled asynchronously in `qedi_abort_work`. It resolves the referenced task, optionally queues firmware cleanup for the target task, waits for cleanup response, then sends the TMF so libiscsi receives its response. LUN/target reset responses schedule `qedi_tmf_resp_work`, which calls `qedi_cleanup_all_io` to clean affected outstanding commands before completing the TMF response. `qedi_cleanup_all_io` walks `active_cmd_list`, optionally filters by LUN, issues cleanup SQEs, waits for `cmd_cleanup_cmpl`, drains QED and marks sessions missing/available if the first wait times out, and returns failure if cleanup still does not converge.

State and persistence: state is all volatile: task IDs, ITT map entries, firmware task contexts, endpoint SQ producer indices, active command lists, TMF work lists, BDQ producer index, SGL DMA mappings, command states, per-connection cleanup counters, wait queues, and trace ring entries. DMA mappings are created by `dma_map_sg` and released by `qedi_iscsi_unmap_sg_list` on completion.

Dependencies and integration points: the file bridges libiscsi, SCSI midlayer, QED iSCSI ops, qedi endpoint/connection structs from `qedi_iscsi.h`, firmware builders in `qedi_fw_api.c`, HSI definitions, kernel workqueues, wait queues, spinlocks, DMA mapping, and BDQ doorbell registers prepared during probe.

Risks: this is highly concurrency-sensitive. Active command list deletion happens in normal completions, cleanup completions, TMF work, and cleanup-all paths, guarded by `list_lock` but with many edge cases. Task ID reuse and ITT mapping must stay coherent across cleanup, abort, and response paths. `qedi_map_scsi_sg` warns when initial SCSI SG count exceeds firmware max before splitting large segments; split BDs can increase the BD count and must remain within firmware table bounds. BDQ unsolicited payload handling copies at most one local `QEDI_BDQ_BUF_SIZE` buffer in several paths, so multi-BDQ payload assumptions should be checked. Doorbell ordering relies on memory barriers around SQ producer writes. Timeouts in cleanup escalate to session marking/drain and may still fail.

Test signals: run login/logout/text/nop paths, read/write I/O with zero, single cached, fast multi-SGL, slow unaligned, and split >4K SGLs, sense/check-condition completions, data underrun CQEs, unsolicited NOP/async/reject PDUs, data digest errors, abort task TMF, LUN reset and target reset with active I/O, cleanup timeout/recovery paths, connection teardown during outstanding commands, I/O tracing, and stress with concurrent completions and disconnects. Static analysis should target lock ordering, list deletion double paths, user-visible timeouts, BD count bounds, DMA unmap symmetry, and null endpoint handling before SQ access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_api.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_api.c

Purpose: this file translates qedi/libiscsi task descriptions into firmware task contexts and SQEs for the QED iSCSI hardware interface.

Important APIs and functions: exported builders are `init_initiator_rw_iscsi_task`, `init_initiator_login_request_task`, `init_initiator_nop_out_task`, `init_initiator_logout_request_task`, `init_initiator_tmf_request_task`, `init_initiator_text_request_task`, and `init_cleanup_task`. Internal helpers initialize cached SGL context, DIF flags/context, default iSCSI task context, extended CDB context, USTORM state, expected data accounting, local completion markers, and common SQE fields.

Control flow: each exported builder receives an `iscsi_task_params` containing a firmware context pointer, SQE pointer, transfer sizes, connection ID, task ID, and CQ RSS number. It zeros/initializes context state from the PDU header, fills storm-specific context fields, populates SGL metadata when TX/RX buffers exist, computes expected transfer and acknowledged data lengths from connection/session settings, sets DIF context when provided, initializes SQE type/flags/SGE count/content length, and returns 0 or an error for unsupported read/write direction combinations.

State and persistence: this file mutates only caller-owned firmware task contexts and SQEs. It preserves `mstorm_ag_context.cdu_validation` across context zeroing. It performs endian conversions into the little-endian HSI layout and uses firmware field macros. No global state is stored.

Dependencies and integration points: it depends on `qedi_hsi.h`, QED common iSCSI HSI definitions, `qedi_fw_iscsi.h`, and `qedi_fw_scsi.h`. `qedi_fw.c` is the primary caller and supplies PDU headers/SGLs built from libiscsi tasks and SCSI commands.

Risks: field programming must exactly match firmware expectations. Incorrect endian conversion, SGE counts, AHS/CDB length, expected transfer length, `exp_data_acked`, or DIF flags can cause data corruption or stuck tasks. Several paths pass nullable SGL pointers when sizes are zero; helpers assume non-null only when corresponding transfer sizes are nonzero. The slow-SGL decision depends on `small_mid_sge` and threshold constants, so SGL classification in `qedi_fw.c` must match this API's interpretation.

Test signals: firmware bring-up tests for read, write, zero-length/TUR, login, logout, text, NOP-Out, TMF, and cleanup WQEs; SGL tests for cached, fast, and slow I/O; AHS/extended CDB coverage; immediate data and initial-R2T combinations; DIF on/off combinations; and HSI structure dumps compared against firmware documentation or known-good traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_iscsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_iscsi.h

Purpose: this header declares the qedi firmware iSCSI task-builder API used by the command submission path.

Important types and APIs: `struct iscsi_task_params` carries the firmware task context, SQE, TX/RX sizes, connection ICID, initiator task ID, and CQ RSS number. `struct iscsi_conn_params` carries session/connection transfer policy: first burst length, max send PDU length, max burst length, initial R2T, and immediate data. The header declares builders for read/write SCSI tasks, login, NOP-Out, logout, TMF, text, and cleanup tasks.

Control flow and state: the header has no runtime control flow. It defines the call contract between `qedi_fw.c` and `qedi_fw_api.c`: callers prepare libiscsi-derived headers and SGL parameters, then builders fill firmware contexts/SQEs.

Dependencies and integration points: it includes `qedi_fw_scsi.h`, which supplies SGL, DIF, and initiator command parameter structs. It references HSI PDU header types such as `iscsi_cmd_hdr`, `iscsi_login_req_hdr`, and `iscsi_tmf_request_hdr` from the included firmware/common headers.

Risks: this is a narrow but critical ABI within the driver. If prototypes drift from implementation or if callers pass inconsistent TX/RX sizes and SGL pointers, firmware context initialization can be wrong. Connection parameters must mirror negotiated libiscsi settings.

Test signals: compile-time prototype matching, submission tests for every declared task type, and negative testing for unsupported read/write flag combinations in `init_initiator_rw_iscsi_task`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_iscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_scsi.h

Purpose: this header defines SCSI-side parameter structures consumed by the qedi firmware task builders.

Important types: `struct scsi_sgl_task_params` carries an SGL pointer, physical SGL address, total buffer size, SGE count, and `small_mid_sge` slow-path hint. `struct scsi_dif_task_params` describes DIF/protection information, including reference/application tags, block size, host/network DIF placement, guard/protection type, validation/forwarding controls, CRC seed, and error behavior. `struct scsi_initiator_cmd_params` carries an extended CDB SGE and sense data buffer physical address.

Control flow and state: the header is declarative. Its fields are populated by `qedi_fw.c` and interpreted by `qedi_fw_api.c` to fill firmware storm contexts and SQE flags.

Dependencies and integration points: it includes Linux types, byteorder support, `qedi_hsi.h`, and QED interfaces. The structs mirror firmware HSI expectations for SGL and DIF programming.

Risks: DIF flags are numerous and easy to combine incorrectly. `small_mid_sge` must reflect SGL alignment constraints or the firmware may use the wrong SGL path. Sense buffer and extended CDB addresses must be DMA-safe and endian-correct when transferred into firmware context.

Test signals: I/O with no DIF and with supported DIF modes, reads/writes with sense data, extended CDB commands, slow-path SGL alignment cases, and firmware context validation against expected SGL/DIF fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_fw_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_gbl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_gbl.h

Purpose: this header is the cross-file symbol contract for qedi. It declares globals and functions shared between qedi main, iSCSI transport, firmware command handling, debugfs, sysfs, and recovery code.

Important declarations: globals include `qedi_io_tracing`, `qedi_host_template`, `qedi_iscsi_transport`, `qedi_ops`, debugfs operation/file arrays, and SCSI host attribute groups. Under debugfs it exposes `qedi_do_not_recover`; without debugfs this becomes constant zero. Functions cover SQ allocation/free, login/logout/TMF/text/NOP/I/O submission, task index management, cleanup, SG unmap, ITT mapping, iSCSI/TCP error handling, connection recovery, CID lookup, device missing/available marking, MTU reset, all-connection recovery, CQE processing, cleanup-all, I/O tracing, local port ID allocation/free, and SQ clearing.

Control flow and state: the header does not execute but defines how the driver objects call into each other. It is especially important for `qedi_fw.c`, which implements many of the submission and completion functions called through libiscsi transport hooks in other files.

Dependencies and integration points: it includes `qedi_iscsi.h`, so it depends on qedi connection/endpoint command definitions. It links QED operation pointers, SCSI host template, and iSCSI transport registration with firmware-path helpers.

Risks: broad global declarations increase coupling. Signature changes need synchronized edits across multiple files. The `qedi_do_not_recover` macro fallback means code that expects a mutable flag must be aware it is compile-time disabled without debugfs.

Test signals: full qedi build with all objects, compile with and without debugfs, link-time symbol resolution, and runtime coverage of each transport callback that crosses this header boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_gbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_hsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_hsi.h

Purpose: this header is qedi's local hardware software interface shim for common QED iSCSI structures. It includes shared QED HSI headers and defines the iSCSI command queue element shape used by the driver/firmware interface.

Important definitions: it includes `common_hsi.h`, `storage_common.h`, `tcp_common.h`, and `iscsi_common.h`. `struct iscsi_cmdqe` contains a connection ID, invalid-command marker, command header type, reserved words, and 13 dwords of command payload. `enum iscsi_cmd_hdr_type` distinguishes BHS-only, BHS-with-AHS, and AHS command header forms.

Control flow and state: there is no runtime control flow. The struct and enum describe firmware command queue layout consumed by lower-level QED iSCSI code and qedi task/SQE setup.

Dependencies and integration points: this header deliberately defines `__QEDI_HSI__` and relies on shared QED HSI contracts. `qedi.h`, `qedi_fw_scsi.h`, and `qedi_fw_api.c` include it so firmware context and PDU definitions are available.

Risks: HSI layout is firmware ABI. Padding, endian handling, field widths, and enum values must match the firmware and common QED headers. Any local change here can break command submission compatibility.

Test signals: build compatibility with QED HSI headers, firmware command submission smoke tests, structure size/layout checks when available, and hardware validation for BHS-only, BHS-with-AHS, and AHS cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_hsi.h -->
