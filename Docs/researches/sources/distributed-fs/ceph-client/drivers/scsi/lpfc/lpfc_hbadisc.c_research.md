# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_hbadisc.c

## Purpose

`lpfc_hbadisc.c` is the LPFC driver's host bus adapter discovery and link lifecycle coordinator. It owns the worker-thread dispatch path for deferred discovery work, handles link-up/link-down mailbox completions, drives Fibre Channel and FCoE discovery, registers and unregisters remote ports with SCSI/NVMe transports, tracks node state transitions, and manages SLI4 FCF selection/failover. It is the glue between hardware mailbox/link events, the LPFC discovery state machine, Linux `scsi_transport_fc`, and FC-NVMe/NVMET integration.

## Important APIs, Types, And Functions

- Worker and deferred events: `lpfc_do_work()`, `lpfc_work_done()`, `lpfc_work_list_done()`, `lpfc_workq_post_event()`, `lpfc_alloc_fast_evt()`, `lpfc_send_fastpath_evt()`, and `lpfc_free_fast_evt()` serialize interrupt/timer/mailbox follow-up through `phba->work_waitq`, `phba->work_list`, `phba->work_ha`, and `vport->work_port_events`.
- Link lifecycle: `lpfc_linkdown()`, `lpfc_linkup()`, `lpfc_linkdown_port()`, `lpfc_linkup_port()`, `lpfc_port_link_failure()`, `lpfc_cleanup_rpis()`, `lpfc_mbx_cmpl_read_topology()`, `lpfc_mbx_process_link_up()`, `lpfc_mbx_issue_link_down()`, `lpfc_enable_la()`, and `lpfc_issue_clear_la()` turn READ_TOPOLOGY/CLEAR_LA/config-link results into HBA/vport state changes.
- Discovery start and timeout: `lpfc_disc_start()`, `lpfc_disc_timeout()`, `lpfc_disc_timeout_handler()`, `lpfc_set_disctmo()`, `lpfc_can_disctmo()`, `lpfc_disc_list_loopmap()`, `lpfc_setup_disc_node()`, and `lpfc_cleanup_discovery_resources()` build discovery work from name-server, RSCN, point-to-point, and loop-map inputs.
- Node lifecycle: `lpfc_nlp_init()`, `lpfc_nlp_get()`, `lpfc_nlp_put()`, `lpfc_nlp_release()`, `lpfc_nlp_set_state()`, `lpfc_enqueue_node()`, `lpfc_dequeue_node()`, `lpfc_drop_node()`, `lpfc_cleanup_node()`, `lpfc_findnode_did()`, `lpfc_findnode_wwpn()`, `lpfc_findnode_rpi()`, and `lpfc_find_vport_by_vpid()` allocate, find, reference-count, transition, and finally release `struct lpfc_nodelist` objects.
- Transport registration: `lpfc_nlp_reg_node()`, `lpfc_nlp_unreg_node()`, `lpfc_register_remote_port()`, `lpfc_unregister_remote_port()`, `lpfc_terminate_rport_io()`, and `lpfc_dev_loss_tmo_callbk()` bridge LPFC node state with `fc_remote_port_add/delete`, SCSI devloss callbacks, FC-NVMe port registration, and NVMET reference ownership.
- Mailbox completion paths: `lpfc_mbx_cmpl_reg_login()`, `lpfc_mbx_cmpl_fabric_reg_login()`, `lpfc_mbx_cmpl_ns_reg_login()`, `lpfc_mbx_cmpl_fc_reg_login()`, `lpfc_mbx_cmpl_fdmi_reg_login()`, `lpfc_mbx_cmpl_reg_vfi()`, `lpfc_init_vfi_cmpl()`, `lpfc_init_vpi_cmpl()`, `lpfc_mbx_cmpl_reg_vpi()`, `lpfc_mbx_cmpl_unreg_vpi()`, and `lpfc_mbx_cmpl_read_sparam()` continue login, VFI/VPI, NameServer, FDMI, and service-parameter sequences.
- FCoE/FCF selection: `lpfc_mbx_cmpl_fcf_scan_read_fcf_rec()`, `lpfc_mbx_cmpl_fcf_rr_read_fcf_rec()`, `lpfc_mbx_cmpl_read_fcf_rec()`, `lpfc_register_fcf()`, `lpfc_unregister_fcf_rescan()`, `lpfc_unregister_fcf()`, `lpfc_unregister_unused_fcf()`, `lpfc_sli4_fcf_rr_next_proc()`, and helpers such as `lpfc_match_fcf_conn_list()`, `lpfc_sli4_fcf_record_match()`, `lpfc_sli4_fcf_pri_list_add()`, and `lpfc_sli4_clear_fcf_rr_bmask()` scan FCF records, rank candidates, register FCFI, and fail over after FLOGI or devloss.
- FCoE config parsing: `lpfc_parse_fcoe_conf()`, `lpfc_get_rec_conf23()`, `lpfc_read_fcoe_param()`, and `lpfc_read_fcf_conn_tbl()` parse config region 23 records into VLAN, FC-MAP, and FCF connection-list state.
- VMID maintenance: `lpfc_check_inactive_vmid()`, `lpfc_check_inactive_vmid_one()`, and `lpfc_check_vmid_qfpa_issue()` are worker-driven maintenance hooks for VMID idle deregistration and QFPA issuance.

Key data structures come from adjacent LPFC headers: `struct lpfc_hba`, `struct lpfc_vport`, `struct lpfc_nodelist`, `struct lpfc_work_evt`, `struct lpfc_fast_path_event`, `struct lpfc_fcf_rec`, `struct lpfc_fcf_pri`, and config-region FCoE records. The file heavily manipulates bit flags such as `FC_DISC_TMO`, `FC_NDISC_ACTIVE`, `FC_RSCN_MODE`, `FC_VFI_REGISTERED`, `NLP_RPI_REGISTERED`, `NLP_XPT_REGD`, `SCSI_XPT_REGD`, `NVME_XPT_REGD`, `FCF_AVAILABLE`, `FCF_REGISTERED`, `FCF_IN_USE`, `FCF_REDISC_FOV`, `FCF_TS_INPROG`, and `FCF_RR_INPROG`.

## Control Flow

Interrupts, timers, and mailbox completions do minimal direct work and push follow-up into the LPFC worker. `lpfc_disc_timeout()` sets `WORKER_DISC_TMO` under `vport->work_port_lock` and wakes `lpfc_do_work()`. `lpfc_work_done()` drains HBA attentions, mailbox events, link attentions, SLI4 asynchronous events, VMID maintenance bits, per-vport worker flags, slow-ring work, and then `phba->work_list` events. This worker serialization is the main protection against discovery state machine reentrancy.

Link-up begins when READ_TOPOLOGY completes in `lpfc_mbx_cmpl_read_topology()`. For link-up attention it logs topology, copies ALPA data, updates event tags and stats, then calls `lpfc_mbx_process_link_up()`. That routine updates topology/link speed, prepares loop or fabric addressing, calls `lpfc_linkup()` to reset vport discovery flags and node state, reads service parameters, and either issues `CONFIG_LINK` for FC or starts SLI4 FCoE FCF scanning. FC discovery proceeds through FLOGI/FDISC, fabric REG_LOGIN, NameServer registration, CT registration commands, SCR/EDC/RDF, and GID_FT/GID_PT queries before `lpfc_disc_start()` issues ADISC/PLOGI to candidate nodes.

Link-down flows through `lpfc_mbx_issue_link_down()` and `lpfc_linkdown()`. It blocks SCSI I/O, clears FLOGI/deferred state, marks `LPFC_LINK_DOWN`, notifies every vport, flushes RSCN and ELS commands, transitions nodes to recovery/removal through the discovery state machine, updates NVMe local or target ports, clears timers, and unregisters default RPIs where legacy SLI paths require it.

Node discovery is represented by `struct lpfc_nodelist` objects on `vport->fc_nodes`. `lpfc_setup_disc_node()` either creates a node and marks `NLP_NPR_2B_DISC`, skips it because an RSCN payload does not cover it, or moves an existing node to NPR so rediscovery can issue. `lpfc_nlp_set_state()` updates state counters, list membership, retry timers, transport registration, and RPI cleanup. Moving into mapped/unmapped states registers SCSI and/or NVMe transports; moving out unregisters them unless ADISC recovery deliberately defers unregister.

Devloss is split between transport callback and worker execution. `lpfc_dev_loss_tmo_callbk()` detaches stale `fc_rport` pointers, clears SCSI transport flags, marks `NLP_IN_DEV_LOSS`, gets an ndlp reference, and queues `LPFC_EVT_DEV_LOSS`. `lpfc_work_list_done()` calls `lpfc_dev_loss_tmo_handler()`, releases the worker reference, and for SLI4 calls `lpfc_sli4_post_dev_loss_tmo_handler()` so the last device leaving an FCF can trigger FCF unregister/rescan.

FCoE discovery scans the adapter FCF table through READ_FCF mailbox callbacks. Each record is parsed from non-embedded DMA memory, checked against FIP availability/validity, connection-table filters, VLAN, fabric name, switch name, MAC provider mode, boot preference, and priority. The best candidate becomes `phba->fcf.current_rec`; equal-priority records use reservoir-style random selection. During FLOGI failure or fast failover, a priority list and round-robin bitmap choose alternate FCF indexes, unregister the current FCF, copy `failover_rec` into `current_rec`, register FCFI, and restart VFI/FLOGI.

## State And Persistence Behavior

This file is stateful but does not persist data to disk. Its persistent-in-memory state is in `phba`, `vport`, and `ndlp` objects:

- `phba->link_state`, `fc_topology`, `fc_linkspeed`, `fc_eventTag`, `link_events`, `fcf`, `hba_flag`, `bit_flags`, `work_ha`, `work_list`, and mailbox queues track hardware-level and worker-level progress.
- `vport->port_state`, `fc_flag`, `fc_myDID`, `fc_prevDID`, `gidft_inp`, `fc_ns_retry`, `fc_nodes`, state counters, discovery timers, and VPI/VFI flags track each physical or NPIV port.
- `ndlp->nlp_state`, `nlp_flag`, `save_flags`, `fc4_xpt_flags`, `nlp_rpi`, `nlp_DID`, `nlp_sid`, `rport`, timers, and kref own remote-node lifetime and transport registration state.
- `phba->fcf.current_rec`, `failover_rec`, `fcf_pri_list`, `fcf_rr_bmask`, `fcf_conn_rec_list`, `valid_vlan`, `vlan_id`, and `fc_map` store SLI4 FCoE candidate, filtering, and failover state.

Reference counts are a major correctness boundary. `lpfc_nlp_init()` creates the initial node reference; worker events, rports, NVMe transport registrations, NVMET target ownership, mailbox contexts, and devloss recovery paths take and drop additional references. The `NLP_DROPPED`, `NLP_IN_DEV_LOSS`, and `NLP_IN_RECOV_POST_DEV_LOSS` flags prevent double-dropping the initial reference during racing devloss and fabric recovery. `lpfc_nlp_release()` is the final cleanup point: it aborts ELS, cancels timers, sanitizes mailbox references, cleans RRQs, frees SLI4 RPI IDs, clears node fields, and returns memory to the mempool.

Timer state is also persistent across asynchronous boundaries. `fc_disctmo` is armed by `lpfc_set_disctmo()`, canceled by `lpfc_can_disctmo()`, and converted into worker work by `lpfc_disc_timeout()`. Node retry timers are initialized per ndlp and canceled on state changes or release. FCF rediscovery and delayed discovery timers are coordinated outside this file but are set/cleared through flags and helper calls here.

## Dependencies And Integration Points

The file depends on core kernel primitives (`kthread`, wait queues, timers, spinlocks, krefs, mempools, lists, atomics, percpu data), PCI channel state, and SCSI/FC transport interfaces (`fc_remote_port_add`, `fc_remote_port_delete`, `fc_remote_port_rolechg`, `fc_host_post_event`, `fc_host_post_vendor_event`, `fc_vport_create`). It integrates with LPFC mailbox helpers from `lpfc_crtn.h`/SLI code (`lpfc_read_sparam`, `lpfc_config_link`, `lpfc_reg_fcfi`, `lpfc_unreg_fcfi`, `lpfc_unreg_login`, `lpfc_init_vfi`, `lpfc_init_vpi`, `lpfc_sli_issue_mbox`, `lpfc_sli4_mbox_cmd_free`), ELS/CT code (`lpfc_initial_flogi`, `lpfc_initial_fdisc`, `lpfc_issue_els_scr`, `lpfc_issue_els_edc`, `lpfc_ns_cmd`, `lpfc_els_disc_adisc`, `lpfc_els_disc_plogi`), SLI queue/abort code, and NVMe/NVMET hooks.

External call-in points include the FC transport callbacks wired in `lpfc_attr.c` (`lpfc_dev_loss_tmo_callbk()` and `lpfc_terminate_rport_io()`), the vport discovery timer setup in initialization code, READ_TOPOLOGY mailbox completions from link attention handling, and FLOGI failure handling that calls `lpfc_sli4_fcf_rr_next_proc()` from ELS code.

## Risks And Edge Cases

- Node reference imbalance is the highest-risk area. Devloss callbacks, unload paths, SCSI rport deletion, NVMe registration, NVMET no-upcall behavior, mailbox contexts, and `NLP_DROPPED` all interact; a missed `lpfc_nlp_put()` leaks nodes, while an extra put can free an ndlp still visible to callbacks.
- Many state transitions depend on bit flags under different locks (`hbalock`, `host_lock`, `fc_nodes_list_lock`, `ndlp->lock`, `work_port_lock`). Any new path must preserve lock ordering and avoid sleeping while holding spinlocks.
- FCF failover has several interleaved states: table scan in progress, round-robin FLOGI retry, fast failover, rediscovery pending/event, devloss-triggered unregister, and link-down abort. Incorrect flag clearing can leave the port stuck with no FCF, repeatedly unregistering an active FCF, or retrying FLOGI against an invalid record.
- SLI generation differences matter. Several branches are SLI3-only (`CLEAR_LA`, default RPI unregister, VPI registration) or SLI4-only (VFI, RPI allocation/free, FCF/FCFI, SLI4 queue draining). Changes must not collapse these paths.
- Discovery timeout recovery is intentionally aggressive: it may abort ELS, restart link initialization, clear LA, or mark vports ready. Bugs here can turn a transient NameServer delay into unnecessary link reset or a stuck `FC_DISC_TMO`.
- Transport integration must respect `cfg_enable_fc4_type`. SCSI rport operations are skipped for NVMe-only mode, while NVMe remote ports are registered only for SLI4 and relevant FC4 types.
- The FCoE config-region parser trusts TLV lengths enough to walk records but bounds by the supplied size. Any future parser change should preserve size checks and endian conversion.
- VMID inactivity scanning drops and reacquires the vport VMID lock around switch deregistration commands; iteration safety depends on hash entry handling and flags remaining consistent.

## Test Signals

- Link-up tests should verify READ_TOPOLOGY completion leads to service-parameter read, CONFIG_LINK or FCF scan, FLOGI/FDISC, NameServer registration, CT registrations, and final discovery without leaked mailbox buffers.
- Link-down tests should verify SCSI I/O is blocked, ELS/RSCN queues are flushed, nodes transition to recovery/removal, timers are canceled, NVMe local/target port updates occur, and SLI3/SLI4 RPI/VPI/VFI cleanup diverges correctly.
- Devloss tests should cover stale rport callbacks, duplicate callbacks, unload-time callbacks, mapped-node recovery, fabric-node recovery after devloss, NVMe-registered nodes, and final FCF unregister only after no nodes/RPIs remain in use.
- FCoE tests should exercise valid and invalid FCF records, connection-table filters, VLAN bitmap selection, boot-preferred records, equal-priority random selection, round-robin FLOGI failover, pending FCoE events during scan, devloss-triggered FCF rescan, and link-down during FCF discovery.
- Node lifecycle tests should track `fc_*_cnt` counters, `NLP_XPT_REGD`/`SCSI_XPT_REGD`/`NVME_XPT_REGD` flags, rport `dd_data->pnode`, RPI allocation/free, mailbox cleanup for pending REG_LOGIN, and no use-after-free under rapid RSCN/link bounce.
- Timeout tests should cover `LPFC_LOCAL_CFG_LINK`, `LPFC_FLOGI`/`LPFC_FDISC`, `LPFC_FABRIC_CFG_LINK`, `LPFC_NS_QRY`, `LPFC_DISC_AUTH`, and ready-state RSCN timeout behavior.
- Observability signals include LPFC log message IDs, debugfs discovery traces, FC transport events (`FCH_EVT_LINKDOWN`, vendor fastpath events), vport states, `phba->nport_event_cnt`, FCF flags, and kernel sanitizers/lockdep for timer, list, kref, and locking defects.
