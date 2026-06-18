# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_target.c

## Purpose

`qla_target.c` is the target-mode lower-level driver layer for the QLogic/Marvell `qla2xxx` Fibre Channel adapters. It translates firmware ATIO/CTIO/ELS/ABTS events into Linux target-core fabric callbacks supplied by `tcm_qla2xxx`, and translates target-core command, data, status, task-management, and session lifecycle decisions back into ISP24xx-style firmware IOCBs.

The file owns the main target-mode runtime machinery:

- target registration/removal for physical and NPIV virtual ports;
- target-session discovery, PLOGI/PRLI/LOGO handling, conflict resolution, delayed deletion, and lport registration;
- ATIO queue dispatch for SCSI commands and task-management commands;
- CTIO response construction, DMA mapping, DIF/PI CRC context construction, and completion handling;
- ABTS and Sequence Retransmission Request handling;
- queue-full throttling, exchange termination, target-mode NVRAM/init-cb setup, and module-level caches/workqueues.

## Important APIs, Types, and Data

The public entry points exported to the rest of the driver and target fabric include `qlt_add_target()`, `qlt_remove_target()`, `qlt_lport_register()`, `qlt_lport_deregister()`, `qlt_enable_vha()`, `qlt_stop_phase1()`, `qlt_stop_phase2()`, `qlt_rdy_to_xfer()`, `qlt_xmit_response()`, `qlt_abort_cmd()`, `qlt_send_term_exchange()`, `qlt_xmit_tm_rsp()`, `qlt_async_event()`, `qlt_24xx_process_atio_queue()`, `qlt_24xx_config_rings()`, NVRAM configuration helpers, `qlt_mem_alloc()`, `qlt_mem_free()`, `qlt_init()`, and `qlt_exit()`.

Core types are declared in `qla_target.h` and `qla_def.h`:

- `struct qla_tgt` is the per-target host object. This file initializes its `vha`, `ha`, session counters, waitqueue, session-work list, SRR list/work item, qpair hints, and LUN-to-qpair btree.
- `struct qla_tgt_cmd` is the per-SCSI-command object allocated through `ha->tgt.tgt_ops->get_cmd()`. This file fills in ATIO, CDB pointer/length, LUN, qpair, DMA direction, state, reset generation, EDIF flag, timing fields, and trace flags.
- `struct qla_tgt_mgmt_cmd` carries task-management work, ABTS responses, original IOCB snapshots, target-core `se_cmd`, selected qpair, reset count, and ownership flags.
- `struct qla_tgt_func_tmpl` is the integration contract with `tcm_qla2xxx`: `handle_cmd`, `handle_data`, `handle_tmr`, session lookup/update/free hooks, command reference hooks, DIF helpers, and target add/remove hooks.
- `struct qla_tgt_srr` records paired SRR immediate-notify and CTIO state until retransmission can be accepted, rejected, or terminated.
- `struct qlt_plogi_ack_t` tracks deferred PLOGI/PRLI notify-ack state while session deletion or creation resolves WWN, S_ID, and loop-id conflicts.

Global resources are `qla_tgt_mgmt_cmd_cachep`, `qla_tgt_plogi_cachep`, `qla_tgt_mgmt_cmd_mempool`, `qla_tgt_wq`, `qla_tgt_mutex`, and `qla_tgt_glist`. Module parameters are `ql2xtgt_tape_enable`, `qlini_mode`, and `ql2xuctrlirq`; parsed initiator mode is stored in `ql2x_ini_mode`.

## Control Flow

Initialization starts in `qlt_init()`: it validates CTIO structure sizes, parses `qlini_mode`, and, when target mode is enabled, allocates the management command slab, PLOGI ack slab, management mempool, and `qla_tgt_wq`. Per-HBA setup flows through `qlt_probe_one_stage1()`, `qlt_mem_alloc()`, `qlt_vport_create()`, and `qlt_add_target()`, which creates `struct qla_tgt`, initializes qpair hints and the LUN qpair btree, installs the target into `vha->vha_tgt.qla_tgt`, and calls the fabric `add_target` hook when present.

Incoming I/O starts with `qlt_24xx_process_atio_queue()`, which walks the ATIO ring until processed signatures are seen. It rejects corrupted FCP frames with `qlt_send_term_exchange()` and dispatches valid entries through `qlt_24xx_atio_pkt_all_vps()` so NPIV packets are routed to the correct `scsi_qla_host`. Unknown D_ID ATIOs are saved in `unknown_atio_list` by `qlt_queue_unknown_atio()` and retried later by `qlt_unknown_atio_work_fn()`.

`qlt_24xx_atio_pkt()` handles ATIO payloads. Normal FCP commands are throttled by `qlt_chk_qfull_thresh_hold()` and then passed to `qlt_handle_cmd_for_atio()`. That function validates target state and session presence, takes a session reference, allocates/fills a `qla_tgt_cmd` via `qlt_get_tag()`, adds it to `qla_cmd_list`, and queues `qlt_do_work()` on the selected CPU/workqueue. `__qlt_do_work()` derives task attribute, data direction, bidirectional state, and data length, then calls `tgt_ops->handle_cmd()`. Task-management ATIOs use `qlt_handle_task_mgmt()` and `qlt_issue_task_mgmt()` to queue `qlt_do_tmr_work()`, which calls `tgt_ops->handle_tmr()`.

The target-core data path calls back into `qlt_rdy_to_xfer()` for data-out and `qlt_xmit_response()` for data-in/status. Both map scatterlists with `qlt_pci_map_calc_cnt()`, reserve request-ring entries with `qlt_check_reserve_free_req()`, build CTIO packets through `qlt_24xx_build_ctio_pkt()` or `qlt_build_ctio_crc2_pkt()`, load DSDs with `qlt_load_data_segments()`, and start IOCBs. Completion returns via `qlt_response_pkt_all_vps()` and `qlt_response_pkt()`, then `qlt_do_ctio_completion()`, which detaches the handle with `qlt_ctio_to_cmd()`, unmaps DMA, interprets CTIO status, advances data-out commands into `tgt_ops->handle_data()`, or frees completed commands through `tgt_ops->free_cmd()`.

Session and ELS control is mostly in `qlt_handle_imm_notify()`, `qlt_24xx_handle_els()`, and `qlt_handle_login()`. PLOGI/PRLI can create sessions through `qla24xx_post_newsess_work()` or `qlt_create_sess()`, defer notify acks through `qlt_plogi_ack_find_add()` and `qlt_plogi_ack_link()`, and invalidate conflicting sessions with `qlt_find_sess_invalidate_other()`. LOGO/PRLO/TPRLO and fabric resets flow through `qlt_reset()`, `qlt_schedule_sess_for_deletion()`, `qlt_unreg_sess()`, and `qlt_free_session_done()`.

ABTS handling is split between `qlt_24xx_handle_abts()`, `__qlt_24xx_handle_abts()`, `qlt_do_tmr_work()`, `qlt_build_abts_resp_iocb()`, `qlt_24xx_send_abts_resp()`, and `qlt_handle_abts_completion()`. If the session is missing, `qlt_sched_sess_work()` and `qlt_abort_work()` can attempt local session discovery before rejecting the ABTS.

SRR handling is deliberately two-phase. `qlt_prepare_srr_imm()` stores the immediate notify in process context, while `qlt_prepare_srr_ctio()` stores the CTIO-side SRR completion. `qlt_handle_srr_work()` pairs both sides. `qlt_handle_srr()` accepts status, data-in, or data-out retransmission only when command state, timeout, offset, reset generation, and buffer availability permit; otherwise it rejects the SRR and may terminate the exchange or advance the command with an error.

Shutdown uses `qlt_stop_phase1()` to set `tgt_stop`, schedule session deletion, flush pending session work, wait for `sess_count` to hit zero, and disable target mode if necessary. `qlt_stop_phase2()` marks the target stopped and may request a chip reset to restore initiator mode. `qlt_release()` removes qpair hints, btree entries, global list state, optional vport target state, and finally frees `struct qla_tgt`.

## State and Persistence Behavior

No durable on-disk state is written. Persistence here is in-kernel runtime state and firmware/NVRAM initialization state.

Important mutable state includes:

- per-target stop state: `tgt_stop`, `tgt_stopped`, `sess_count`, `tgt_global_resets_count`, expected notify/ABTS counters, link-reinit IOCB, SRR/session work lists, and LUN-to-qpair map;
- per-session state: `se_sess`, `sess_kref`, `disc_state`, `fw_login_state`, `deleted`, `free_pending`, `login_gen`, `rscn_gen`, `loop_id`, `d_id`, `logout_on_delete`, `keep_nport_handle`, `logo_ack_needed`, `conf_compl_supported`, EDIF auth state, and PLOGI ack links;
- per-command state: command state machine (`NEW`, `NEED_DATA`, `DATA_IN`, `PROCESSED`, `DONE`), `cmd_sent_to_fw`, `aborted`, `sent_term_exchg`, `rsp_sent`, scatterlist mapping flags, SRR offset, CDB allocation, timing fields, and trace flags;
- per-HBA target state: ATIO ring/dma, qfull lists and counters, exchange starvation counters, saved firmware/NVRAM option snapshots, target ops pointer, and qpair maps.

NVRAM helper functions modify initialization control blocks and NVRAM images before firmware startup. They save original exchange count and firmware options once in `ha->tgt.saved_*`, then enable target or dual mode, target PRLI control, optional FC tape support, P2P topology preferences, node-name override, and class-2 capabilities. `qlt_config_nvram_with_fw_version()` disables FC tape/SRR support for known-bad firmware versions.

## Dependencies and Integration Points

This file depends on the wider `qla2xxx` driver for firmware IOCB allocation/start (`qla2x00_alloc_iocbs()`, `__qla2x00_alloc_iocbs()`, `qla2x00_start_iocbs()`), mailbox and async operations, FC port discovery, GPDB/GID list lookups, firmware dumps, chip reset/DPC signaling, NPIV host lookup, EDIF helpers, and DMA pools. It uses kernel primitives including spinlocks, mutexes, workqueues, mempools, slab caches, DMA mapping, btrees, krefs, waitqueues, and module parameters.

The most important external boundary is `ha->tgt.tgt_ops`, implemented by `tcm_qla2xxx`. This driver owns firmware-facing mechanics and session-command bookkeeping, while target-core owns SCSI command execution, fabric sessions, TMR semantics, DIF tag policy, and command references. The file also integrates with SCSI host active mode (`MODE_TARGET`, `MODE_INITIATOR`, `MODE_DUAL`), FC transport class reporting through `qlt_rff_id()`, and configfs lport registration via `qlt_lport_register()`.

## Risks and Edge Cases

- Lock ordering is delicate. Many functions require `hardware_lock`, qpair locks, `sess_lock`, `cmd_list_lock`, `atio_lock`, or `tgt_mutex`, and several paths explicitly note that helper calls may drop and reacquire hardware locks.
- Firmware handle reuse and duplicate CTIO completions are guarded by `qlt_ctio_to_cmd()` checks against command type and exchange address. Any regression here risks completing or freeing the wrong command.
- Session login/logout races are complex. PLOGI/PRLI acks may be deferred while stale sessions are deleted; `keep_nport_handle`, `logout_on_delete`, PLOGI link refcounts, and conflict sessions must remain consistent to avoid leaked firmware nport handles or dropped logins.
- Queue-full and exchange-starvation recovery relies on bounded `q_full_list` allocation and reset thresholds. Dropping too many QFull commands can leak exchanges until the driver forces a chip reset.
- SRR support has many state gates: it is disabled for known-bad firmware, rejects protected nonzero-offset retransmission, times out after 30 seconds of retry activity, and must coordinate independent immediate notify and CTIO events.
- DIF/PI support builds CRC2 IOCBs, DMA CRC contexts, protection SG lists, and sense responses. Failures must clear outstanding handles and unmap data correctly to avoid memory leaks, stale DMA mappings, or silent data-integrity errors.
- Reset-generation checks (`chip_reset`, `reset_count`, generation ticks) are central to avoiding work from a previous firmware life. Missing a check can send stale IOCBs after reset.
- Target stop/unload still allows some request processing to drain stuck exchanges. Incorrect early returns in stop paths can leave firmware exchanges active.
- EDIF-specific login and CTIO error handling can reject unauthenticated logins or track encrypted byte counts; it depends on external app/auth state being current.

## Test Signals

Useful validation signals are mostly integration and fault-injection oriented:

- Build coverage with target mode enabled should compile all exported symbols, IOCB layout `BUILD_BUG_ON()` checks, and DIF/SRR branches.
- Target-mode smoke test: register a `tcm_qla2xxx` lport, confirm `qlt_lport_register()` matches WWPN, enable target mode, and verify RFF_ID advertises target or dual FC-4 features.
- Session lifecycle test: PLOGI/PRLI/LOGO/PRLO/TPRLO flows should create sessions, defer and complete notify acks, update `fcport_count`, and drop `sess_count` to zero during stop.
- Normal I/O test: read/write/no-data commands should pass through ATIO, `handle_cmd`, `qlt_rdy_to_xfer()` or `qlt_xmit_response()`, CTIO completion, DMA unmap, and `free_cmd()` without pending-command counter leaks.
- Queue pressure test: exceed `Q_FULL_THRESH_HOLD()` and confirm BUSY/TASK_SET_FULL CTIOs, qfull allocation counters, and exchange-starvation reset behavior.
- TMR/ABTS test: LUN reset, target reset, abort task, and ABTS should call `handle_tmr()`, abort matching queued commands, emit CTIO/ABTS responses, and free management commands.
- SRR test: inject SRR status, data-in, and data-out requests with valid and invalid offsets, missing CTIO/IMM half, reset-generation mismatch, timeout, and protected I/O to verify accept/reject/terminate behavior.
- DIF test: protection insert/strip/pass operations should build CTIO_CRC2 packets, map/unmap data and protection SGs, populate CRC contexts, and return expected guard/app/ref tag sense data on firmware DIF errors.
- Reset/unload test: chip reset while commands, SRRs, ABTS, unknown ATIOs, and session deletion are pending should not leak command refs, DMA mappings, work items, qpair handles, or sessions.
