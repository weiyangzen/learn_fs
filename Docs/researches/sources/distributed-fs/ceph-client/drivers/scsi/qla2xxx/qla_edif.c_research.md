<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.c

## Purpose

`qla_edif.c` implements Encrypted Data In Flight support for qla2xxx, mainly for 28xx-class adapters with FC-SP security enabled. It connects a userspace authentication application to the driver through BSG vendor commands, passes authentication ELS frames between firmware and userspace, manages per-port Security Association database indexes, issues SA update/delete IOCBs to firmware, raises doorbell events to userspace, and enables EDIF-aware SCSI command submission.

The file is a coordination layer spanning discovery, target session teardown, firmware request rings, response processing, timers, and userspace ABI structures from `qla_edif_bsg.h`.

## Important APIs, Types, And Functions

- `qla_edif_app_mgmt()` dispatches vendor subcommands: SA update, app start/stop, auth success/failure, FC info, stats, AEN completion, and read-doorbell.
- `qla_edif_process_els()` handles BSG ELS send/reply/pull operations for authentication traffic.
- `qla24xx_auth_els()` consumes firmware PUREX authentication ELS IOCBs, validates length/capability/app state, copies payloads, queues pending ELS nodes, and creates doorbell events.
- `qla24xx_sadb_update()` accepts userspace `struct qla_sa_update_frame`, finds the `fc_port`, allocates or reuses an SA index, handles RX delayed delete rules, builds an SRB, and starts an SA update IOCB.
- `qla24xx_sa_update_iocb()` and `qla24xx_sa_replace_iocb()` format firmware `sa_update_28xx` IOCBs for normal update/delete and delayed RX replace/delete.
- `qla28xx_sa_update_iocb_entry()` processes firmware completions, updates per-port EDIF state, frees SA controls and indexes, cancels delayed delete timers, raises SA completion doorbells, and schedules session deletion for some firmware failures.
- `qla28xx_start_scsi_edif()` builds command type 6 EDIF SCSI IOCBs, including FCP_CMND DMA buffers, DSDs, `CF_EN_EDIF`, and per-port EDIF byte counters.
- `qla_edb_eventcreate()`, `qla_edb_stop()`, `qla_edb_init()`, and `qla_edif_timer()` implement the doorbell event queue and long-poll timeout behavior.
- `qla_enode_init()`, `qla_enode_stop()`, `qla_pur_get_pending()`, and related helpers manage pending PUREX ELS payloads for userspace retrieval.
- SADB helpers such as `qla_edif_sadb_get_sa_index()`, `qla_edif_sadb_delete_sa_index()`, `qla_edif_sadb_build_free_pool()`, and `qla_edif_sadb_release()` manage RX/TX SA index maps and per-nport two-slot SPI/index tracking.

## Control Flow

The normal lifecycle starts with host initialization calling `qla_enode_init()`, `qla_edb_init()`, and building SADB free pools. Userspace registers with `QL_VND_SC_APP_START`; `qla_edif_app_start()` activates `vha->e_dbell`, resets relevant FC-SP sessions, initializes per-port SA counters, and triggers relogin or link reset depending on topology. When secure login requires authentication, firmware delivers AUTH ELS frames as PUREX entries. `qla24xx_auth_els()` copies valid payloads to an `enode`, queues it, and raises a `VND_CMD_AUTH_STATE_ELS_RCVD` doorbell. Userspace long-polls `QL_VND_SC_READ_DBELL`, pulls the ELS with `PULL_ELS`, sends replies through `qla_edif_process_els()`, and reports `AUTH_OK` or `AUTH_FAIL`.

SA updates are initiated by userspace through `QL_VND_SC_SA_UPDATE`. The driver finds the matching `fc_port`, validates host/app state and loop ID, maps SPI/direction to an SA index, records an `edif_sa_ctl`, and submits an SA update IOCB. RX updates are tracked in `fcport->edif.edif_indx_list` so later RX deletes can be delayed until traffic using the new SA index is observed. RX deletes normally arm a timer and store `delete_sa_index`; read completions or target CTIO completions call `qla_chk_edif_rx_sa_delete_pending()`/`qlt_chk_edif_rx_sa_delete_pending()`, which schedule a replace/delete work item after a filter count. If traffic never arrives, `qla2x00_sa_replace_iocb_timeout()` forces the delete.

Firmware completions enter `qla28xx_sa_update_iocb_entry()`. Success marks `tx_sa_set` or `rx_sa_set`, clears pending flags, enables EDIF for the port, and queues an SA completion doorbell. Deletes free SA controls and return SA indexes to the free pool. Failures queue failure AEN data and may delete the session for EDIF-unavailable or logout statuses. Once both RX and TX SAs are set and userspace reports auth OK, `qla_edif_app_authok()` posts PRLI work so discovery can continue.

EDIF SCSI I/O uses `qla28xx_start_scsi_edif()`. It allocates an outstanding handle, maps the SCSI SG list, reserves firmware IOCB/exchange resources, obtains a buffer for FCP_CMND, validates CDB length alignment, writes a command type 6 IOCB, sets transfer direction and `CF_EN_EDIF`, emits data DSDs and continuation IOCBs, records the SRB in `req->outstanding_cmds`, advances the request ring, and rings the hardware doorbell.

App stop calls `qla_edif_app_stop()`, which stops enode and doorbell queues, marks FC-SP sessions for deletion, and causes future security traffic to be rejected or terminated. Session down and app-data cleanup paths generate shutdown events and clear queued ELS/doorbell entries for a port.

## State And Persistence Behavior

EDIF state is distributed across `scsi_qla_host`, `qla_hw_data`, and `fc_port`. Host-level state includes `vha->e_dbell` for doorbell activity, queued `edb_node` events, a pending BSG long-poll job, and expiration time; `vha->pur_cinfo` for pending PUREX ELS payloads; and DPC flags used to restart login flows. Hardware-level state includes RX/TX SA index bitmaps, SADB RX/TX index lists, `sadb_lock`, `sadb_fp_lock`, and EDIF firmware capability flags. Per-port state includes EDIF counters, pending/set flags, auth state, app session flags, `tx_sa_list`, `rx_sa_list`, and the RX delayed-delete index list.

State persists for the lifetime of the adapter/session unless explicitly freed during app stop, session deletion, SADB release, or free-pool release. Firmware SA state persists until SA delete IOCBs complete or firmware/session reset clears it. Doorbell events persist until consumed by `QL_VND_SC_READ_DBELL`, cleared for a port, or dropped during `qla_edb_stop()`.

## Dependencies And Integration Points

The file includes `qla_def.h` and `qla_edif.h`, and uses BSG, SCSI, DMA pool, kthread/timer, qla workqueue, discovery, target, firmware IOCB, and mailbox infrastructure. It depends on `qla_edif_bsg.h` ABI structures via common definitions included by qla headers. Important external integration points include `qla2x00_get_sp()`, `qla2x00_start_sp()`, `qla2x00_bsg_job_done()`, `qla_els_pt_iocb()`, `__qla_copy_purex_to_buffer()`, `qla24xx_post_prli_work()`, `qlt_schedule_sess_for_deletion()`, `qla2x00_post_work()`, `qla2x00_post_aen_work()`, and request-ring helpers.

## Risks And Edge Cases

- The userspace ABI is security-sensitive. Incomplete payload length validation around `sg_copy_to_buffer()` inputs can leave partially initialized stack structures if userspace supplies short buffers.
- Doorbell long-polling stores a raw `bsg_job` pointer in `vha->e_dbell`. Races between app stop, timeout, and new events depend on `db_lock` plus disciplined completion through `qla_edif_dbell_bsg_done()`.
- RX SA delete delay is complex. It depends on matching firmware-reported `edif_sa_index`, timer shutdown, two-slot SADB tracking, and port loop ID stability. Session teardown or loop ID changes can create mismatches that the code logs but must still survive.
- `qla_edif_find_sa_ctl_by_index()` walks SA lists without taking `sa_list_lock`, while writers use that lock. Callers need external serialization or this path is race-prone.
- `qla28xx_start_scsi_edif()` has a failure path that calls `qla_put_buf()` even when `qla_get_buf()` failed before `SRB_GOT_BUF` was set, so buffer-release assumptions should be reviewed.
- App start resets sessions and can trigger ISP abort or N2N link reset. This is intentional but disruptive, and tests must include live discovery and target-mode interactions.
- EDIF state spans initiator and target paths; target CTIO completion and initiator SCSI status both feed delayed RX SA deletion.

## Test Signals

Compile coverage should include BSG, FC transport, target mode, NVMe FC, and 28xx EDIF-capable configurations. Runtime tests should cover app start/stop, doorbell long-poll timeout and immediate completion, AUTH ELS receive/pull/send-reply, auth OK/fail by WWPN and D_ID, FC info and stats queries, RX/TX SA update success, TX delete, RX delayed delete by traffic observation, RX delete timeout, forced RX delete, session teardown cleanup, and firmware failure completions such as EDIF unavailable/logout. I/O tests should verify EDIF SCSI reads and writes set `CF_EN_EDIF`, update byte counters, handle large SG lists, reject misaligned long CDBs, and unwind DMA/resources on queueing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.c -->
