# subset-b-005330 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dfs.c

## Purpose

`qla_dfs.c` implements the qla2xxx driver's debugfs interface. It exposes per-adapter diagnostics under a shared `qla2xxx` debugfs root, per-remote-port state under each host's `rports` directory, firmware resource counts, target counters, target session and port-database snapshots, FCE trace control/dump access, and a target multi-queue `naqp` knob on supported adapters.

This file is diagnostic and control-plane oriented. It does not submit normal SCSI I/O, but it can issue mailbox commands, pause and re-enable firmware event tracing, alter target queue-pair selection, and change NVMe remote-port `dev_loss_tmo`.

## Important APIs, Types, And Functions

- `qla2x00_dfs_setup()` creates the global debugfs root once, creates the per-HBA directory named by `vha->host_str`, initializes `ha->fce_mutex`, and installs files such as `fw_resource_count`, `tgt_counters`, `tgt_port_database`, `fce`, `tgt_sess`, optional `naqp`, and `rports`.
- `qla2x00_dfs_remove()` removes all per-host files, recursively removes `vha->dfs_rport_root`, decrements `qla2x00_dfs_root_count`, and removes the global root when the last host leaves.
- `qla2x00_dfs_create_rport()` and `qla2x00_dfs_remove_rport()` maintain per-`fc_port` directories named `pn-%016llx`, with read-only state files and an NVMe-only read/write `dev_loss_tmo`.
- `qla_dfs_rport_get()`/`qla_dfs_rport_set()` implement the only writable rport attribute, guarding it with `NVME_FLAG_REGISTERED` and `CONFIG_NVME_FC`.
- `qla2x00_dfs_tgt_sess_show()`, `qla2x00_dfs_tgt_port_database_show()`, `qla_dfs_fw_resource_cnt_show()`, and `qla_dfs_tgt_counters_show()` are `seq_file` producers for target/session, name-list, firmware resource, and aggregate counter data.
- `qla2x00_dfs_fce_open()`, `qla2x00_dfs_fce_show()`, `qla2x00_dfs_fce_write()`, and `qla2x00_dfs_fce_release()` form a custom `file_operations` implementation for Fibre Channel event tracing.
- `qla_dfs_naqp_show()`/`qla_dfs_naqp_write()` expose and alter `ha->tgt.num_act_qpairs` for selected multi-queue capable adapters.

## Control Flow

Probe or host setup calls `qla2x00_dfs_setup()`. Unsupported adapter families return without creating entries. Supported families create the root if needed, the host directory if absent, then unconditionally create the normal diagnostic files. Each remote `fc_port` can later call `qla2x00_dfs_create_rport()` once its host has an `rports` root; removal mirrors this path and nulls the stored dentries.

Most reads are direct snapshots. Target sessions are printed while holding `ha->tgt.sess_lock`. Target port database output allocates a coherent GID-list buffer, waits for `qla24xx_gidlist_wait()`, and prints each firmware loop ID through `qla24xx_print_fc_port_id()`. Firmware resource counts call `qla24xx_res_count_wait()` and optionally add driver-side IOCB/exchange usage across queue pairs. Target counters aggregate `qpair->tgt_counters`, DIF stats, host error counters, and per-rport link-down counters.

The `fce` node has active side effects. Opening it disables FCE tracing when currently enabled so the buffer can be read consistently. Releasing it reinitializes and re-enables tracing if the buffer still exists. Writing a non-zero value allocates FCE buffers if needed, adjusts firmware dump allocation, marks `user_enabled_fce`, and enables tracing. Writing zero disables tracing and frees the FCE trace buffer.

The `naqp` write path validates adapter family, multi-queue availability, and the requested count against `ha->max_qpairs`; a change updates `ha->tgt.num_act_qpairs` and clears the target queue-pair table.

## State And Persistence Behavior

The file persists only debugfs dentries and driver diagnostic state. Global state is `qla2x00_dfs_root` plus `qla2x00_dfs_root_count`; per-HBA state lives in `ha->dfs_*`, `ha->tgt.dfs_*`, `vha->dfs_rport_root`, and each `fc_port->dfs_rport_dir`. Removing nodes sets these pointers back to `NULL`.

FCE state changes are persistent driver/runtime changes until explicitly changed, adapter reset, or host removal: `ha->flags.user_enabled_fce`, `ha->flags.fce_enabled`, `ha->fce`, `ha->fce_dma`, `ha->fce_mb`, and `ha->fce_bufs` are modified under `ha->fce_mutex`. `dev_loss_tmo` writes persist in the NVMe FC remote-port object. `naqp` writes persist in `ha->tgt.num_act_qpairs` until changed or the adapter is reinitialized.

## Dependencies And Integration Points

The file depends on `qla_def.h`, debugfs, `seq_file`, NVMe FC remote-port helpers, target-mode structures, qla mailbox helpers, qpair accounting, and firmware trace helpers declared elsewhere. It integrates with `qla_gbl.h` through exported prototypes for debugfs setup/removal and rport directory creation/removal. It also relies on target-mode support functions such as `qlt_clr_qp_table()` and firmware helpers such as `qla24xx_res_count_wait()`.

## Risks And Edge Cases

- Debugfs creation is mostly best-effort. Several `debugfs_create_file()` results are stored without `IS_ERR()` handling; cleanup tolerates `NULL` but not every failed dentry path reports an error.
- `qla2x00_dfs_setup()` can recreate files on repeated calls if `ha->dfs_dir` already exists but individual file pointers are not checked first.
- `qla_dfs_fw_resource_cnt_show()` intentionally reads IOCB/exchange counters without locking, so its driver-side usage values are estimates.
- `qla_dfs_naqp_write()` uses `simple_strtoul()` and creates `naqp` with mode `0400` despite wiring a write handler, making writability dependent on debugfs mode behavior and worth checking.
- FCE open/release changes firmware tracing around a read. Concurrent writes, host teardown, or firmware reset paths must respect `ha->fce_mutex` and buffer lifetime.
- Per-rport debugfs fields read live `fc_port` members with minimal locking. They are diagnostic snapshots and can race with discovery/session teardown unless callers remove rport directories before freeing `fc_port`.

## Test Signals

Useful tests include building with `CONFIG_DEBUG_FS`, `CONFIG_NVME_FC`, target mode, and EDIF/FCE-capable adapter support enabled. Runtime validation should confirm debugfs tree creation/removal across multiple HBAs, per-rport directory lifetime during discovery and deletion, successful and rejected `dev_loss_tmo` writes for registered and unregistered NVMe ports, FCE enable/read/disable flows, firmware resource count reads during I/O, and `naqp` validation on supported and unsupported hardware. Teardown tests should verify that no stale debugfs dentries remain after host removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dsd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dsd.h

## Purpose

`qla_dsd.h` defines the qla2xxx data segment descriptor helpers used when building firmware IOCBs from Linux scatter-gather lists. It provides the two wire formats the firmware consumes: 32-bit descriptors and 64-bit descriptors.

## Important APIs, Types, And Functions

- `struct dsd32` is an 8-byte descriptor containing little-endian 32-bit DMA address and little-endian 32-bit length.
- `append_dsd32()` writes `sg_dma_address()` and `sg_dma_len()` into the current descriptor with unaligned little-endian stores, then advances the descriptor pointer.
- `struct dsd64` is a packed 12-byte descriptor containing little-endian 64-bit DMA address and little-endian 32-bit length.
- `append_dsd64()` performs the equivalent operation for 64-bit DMA addresses.

## Control Flow

The header has no standalone runtime flow. IOCB builders include it, allocate or point at an array of DSD slots in a request or continuation IOCB, then repeatedly call `append_dsd32()` or `append_dsd64()` while walking a mapped scatterlist. The caller owns DMA mapping, descriptor capacity, IOCB continuation allocation, and final doorbell submission.

## State And Persistence Behavior

There is no global or persistent software state. The helpers mutate only the caller-provided descriptor pointer and the memory backing the firmware request. The written descriptor contents persist in the request ring or DMA buffer until firmware consumes them or the driver reuses the buffer.

## Dependencies And Integration Points

The header includes `<linux/unaligned.h>` and depends on Linux scatterlist DMA accessors. `qla_fw.h` includes this header and embeds `struct dsd64` in many firmware request definitions, including SCSI command, CT, ELS, verify-chip, and access-chip IOCBs. The helpers are part of the low-level contract between qla IOCB builders and firmware.

## Risks And Edge Cases

- `append_dsd32()` truncates `sg_dma_address()` to 32 bits by design. Callers must use it only for hardware/IOCB paths that support 32-bit DMA addresses.
- The helpers do not validate descriptor array capacity. IOCB builders must correctly calculate continuation entries before appending.
- The helpers assume `sg_dma_address()`/`sg_dma_len()` are valid, so callers must map the scatterlist first and unwind DMA mappings on later failures.
- `struct dsd64` is packed because the firmware layout is 12 bytes; removing packing or using normal structure assignment could change layout or alignment assumptions.

## Test Signals

Build-time checks should cover all qla IOCB builders that include `qla_fw.h`. Targeted unit or instrumentation checks can validate `sizeof(struct dsd32) == 8`, `sizeof(struct dsd64) == 12`, descriptor pointer advancement, little-endian encoding, and correct behavior with unaligned descriptor addresses. Runtime I/O tests with multi-segment scatterlists and DMA addresses above 4 GiB exercise the 64-bit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dsd.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.h

## Purpose

`qla_edif.h` contains the in-kernel EDIF definitions shared by the qla2xxx EDIF implementation and the rest of the driver. It defines the application identity, SA control object, doorbell and PUREX queue state, SA update IOCB wire layout, pending ELS event structures, and convenience macros for EDIF session state checks.

## Important APIs, Types, And Data

- `EDIF_APP_ID` and `EDIF_MAX_INDEX` define the expected userspace application identifier and maximum SA index space.
- `struct edif_sa_ctl` tracks a single SA update/delete request, including list linkage, index fields, state bits, owning `fc_port`, optional BSG job, and copied `qla_sa_update_frame`.
- `struct pur_core` holds the pending unsolicited receive event queue (`head`), lock, and active flag.
- `struct edif_dbell` holds the doorbell event queue, lock, active flag, pending long-poll BSG job, and expiration.
- `struct sa_update_28xx` describes firmware IOCB type `0x71`, including nport handle/completion status, VP index, port ID, flags, key material, salt, SPI, SA control, SA index, and old/new SA info fields.
- `struct enode`, `struct purexevent`, and `struct pur_ninfo` describe copied PUREX authentication ELS payloads awaiting userspace retrieval.
- `EDIF_SESSION_DOWN()`, `EDIF_NEGOTIATION_PENDING()`, `EDIF_SESS_DELETE()`, and `EDIF_CAP()` centralize common EDIF capability and session-state predicates.

## Control Flow

This header has no executable control flow, but its structures define the state machines used by `qla_edif.c`. Userspace SA commands are copied into `edif_sa_ctl`, formatted into `sa_update_28xx`, submitted to firmware, then completed back into the same per-port SA tracking. PUREX ELS frames become `enode` entries on `pur_core.head`; doorbell notifications become `edb_node` entries on `edif_dbell.head`; long-poll BSG jobs wait in `edif_dbell.dbell_bsg_job`.

## State And Persistence Behavior

The structures declared here are embedded in long-lived host and port objects or allocated per event/request. `edif_sa_ctl` entries persist from BSG SA request acceptance until firmware completion and cleanup. `pur_core` and `edif_dbell` queues persist for the host lifetime but are active only while the EDIF app is started. The firmware SA indexes represented in `sa_update_28xx` persist in adapter firmware until an invalidate IOCB, session teardown, or reset.

## Dependencies And Integration Points

The header depends on qla core types supplied before inclusion: `fc_port`, `scsi_qla_host`, `qla_sa_update_frame`, `port_id_t`, `bsg_job`, and list/spinlock primitives. It is included by `qla_edif.c` and indirectly tied to `qla_fw.h` command/status definitions, `qla_edif_bsg.h` userspace ABI structures, and `qla_gbl.h` prototypes.

## Risks And Edge Cases

- `struct sa_update_28xx` is a firmware ABI. Field sizes, endian annotations, packing expectations, and bit definitions must match firmware exactly.
- `struct edif_sa_ctl` carries both list state and BSG/firmware request state; double completion or double removal would corrupt per-port lists.
- `EDIF_CAP()` gates support on both module parameter `ql2xsecenable` and `IS_QLA28XX()`. Any new EDIF-capable hardware requires this macro and call sites to be reviewed.
- Macros such as `EDIF_SESSION_DOWN()` dereference nested session fields and assume valid `vha` and initialized EDIF state.

## Test Signals

Compile tests should catch layout users and missing type dependencies across EDIF-enabled and disabled builds. Runtime validation should indirectly exercise every state bit in `edif_sa_ctl`, active/inactive transitions for `pur_core` and `edif_dbell`, firmware SA update IOCB formatting, and capability gating through `EDIF_CAP()` on 28xx and non-28xx adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif_bsg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif_bsg.h

## Purpose

`qla_edif_bsg.h` defines the userspace BSG ABI for qla2xxx EDIF. It specifies vendor subcommands, authentication ELS request/reply envelopes, application registration messages, FC session info/stat replies, SA update input, doorbell event payloads, SA completion AENs, and authentication completion commands.

## Important APIs, Types, And Data

- `enum auth_els_sub_cmd` defines ELS operations: `SEND_ELS`, `SEND_ELS_REPLY`, and `PULL_ELS`.
- `struct extra_auth_els`, `qla_bsg_auth_els_request`, and `qla_bsg_auth_els_reply` extend generic FC BSG ELS requests/replies with exchange address, control flags, version, and reserved fields.
- `struct app_id` carries `EDIF_APP_ID` and ABI version. Most commands embed it so the driver can reject unknown applications.
- `struct app_start`, `app_start_reply`, and `app_stop` define app lifecycle messages.
- `struct app_pinfo_req`, `app_pinfo_reply`, and `app_pinfo` return per-port WWPN, port ID, remote type, remote online state, and EDIF auth state.
- `struct app_sinfo_req`, `app_stats_reply`, and `app_sinfo` return rekey and byte counters.
- `struct qla_sa_update_frame` is the userspace SA update/delete command, including flags, SA index hint field, salt, SPI, key bytes, WWNs, and port ID.
- `QL_VND_SC_*` constants define vendor subcommands dispatched by `qla_edif_app_mgmt()`.
- `struct edif_read_dbell`, `edif_app_dbell`, `edif_sa_update_aen`, `auth_complete_cmd`, and `aen_complete_cmd` define doorbell read, SA completion event, auth success/failure, and event-ack payloads.

## Control Flow

Userspace opens the FC BSG path and sends vendor commands identified by `QL_VND_SC_*`. The driver first validates `app_id`, then dispatches to the EDIF app management flow. `APP_START` activates doorbells; `READ_DBELL` either returns queued `edif_app_dbell` records or parks the BSG job until an event or timeout; `SA_UPDATE` installs or deletes keys in firmware; `AUTH_OK`/`AUTH_FAIL` resolves pending login authentication; `GET_FCINFO` and `GET_STATS` copy variable-length arrays back to userspace. Authentication ELS traffic uses the separate request/reply wrappers around FC BSG ELS commands.

## State And Persistence Behavior

This header only defines ABI data. Persistence is in the kernel objects that consume these messages and in firmware SA tables. Reserved arrays in most structures preserve ABI size and forward-compatibility room. Flexible arrays in `app_pinfo_reply` and `app_stats_reply` require the caller and driver to agree on `num_ports` and transfer lengths.

## Dependencies And Integration Points

The header depends on FC BSG request/reply types, `port_id_t`, endian definitions, and `WWN_SIZE`. It is consumed by `qla_edif.c` and by userspace EDIF authentication tooling. It must remain synchronized with command dispatch in `qla_edif_app_mgmt()` and payload copies in all EDIF BSG handlers.

## Risks And Edge Cases

- This is a UAPI-like contract even though it lives in the driver tree. Changing structure layout, packing, constants, or version semantics can break existing authentication applications.
- `app_pinfo_req.remote_pid` uses endian-conditional byte layout. Cross-architecture userspace/kernel expectations should be tested.
- Variable-length replies depend on userspace-provided counts and buffer sizes. The driver must avoid copying more elements than requested or returning uninitialized padding.
- `qla_sa_update_frame.fast_sa_index` is a 10-bit bitfield inside a packed structure, which can be fragile across compilers or ABI consumers if not mirrored exactly.
- Key length flags (`SAU_FLG_KEY128`/`SAU_FLG_KEY256`) and GMAC/delete flags are security-sensitive; ambiguous combinations need deterministic handling.

## Test Signals

ABI tests should assert structure sizes, offsets, packing, command numbers, auth-state values, and endian-specific port ID layout on little- and big-endian builds. Integration tests should send every vendor subcommand with valid and invalid `app_id`, short buffers, oversized reply buffers, zero-port and multi-port queries, SA update/delete variants, doorbell reads with empty and populated queues, and auth completion by both WWPN and D_ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_edif_bsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_fw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_fw.h

## Purpose

`qla_fw.h` is the qla2xxx firmware interface definition header. It defines mailbox status values, firmware option bits, NVRAM/init-control-block layouts, firmware request and response IOCB formats, hardware register maps, flash layout records, NPIV and virtual-port IOCBs, FCP priority data, and chip-family-specific constants for 24xx, 25xx, 81xx, 83xx, 84xx, and 28xx-era adapters.

The file is not executable logic; it is the binary contract used by qla initialization, mailbox, IOCB, interrupt, flash, debug, target, NVMe, and EDIF paths.

## Important APIs, Types, And Data

- Firmware configuration structures include `port_database_24xx`, `get_name_list_extended`, `vp_database_24xx`, `nvram_24xx`, `init_cb_24xx`, `nvram_81xx`, `init_cb_81xx`, and MID/NPIV init structures.
- SCSI and transport IOCBs include `cmd_bidir`, `cmd_type_6`, `cmd_type_7`, `cmd_type_crc_2`, `sts_entry_24xx`, marker, CT, PUREX, ELS, mailbox, login/logout, task management, abort, and ABTS entries.
- EDIF-relevant firmware bits include command type 6 flags `CF_EN_EDIF` and `CF_NEW_SA`, status union field `edif_sa_index`, ELS `ECF_SEC_LOGIN`, and the included `dsd64` descriptor layouts.
- Hardware register definitions include `struct device_reg_24xx` with flash/NVRAM access, queue pointers, interrupt registers, host command/control, GPIO, mailbox, and I/O window fields.
- Trace, firmware, and flash constants define FCE/EFT mailbox controls, flash addresses, flash description/layout table records, hardware event codes, and FCP priority table formats.
- Virtualization support includes MID config entries, VP control/config/report IOCBs, and virtual fabric exchange parameters.
- Chip-family sections define 84xx verify/access-chip IOCBs, 81xx/83xx mailbox and flash access constants, and 25xx/81xx/83xx/28xx flash region addresses.

## Control Flow

Control flow is external and table/structure driven. Initialization code reads NVRAM structures, populates init control blocks, writes request/response queue addresses, and executes firmware. IOCB builders allocate request-ring entries using the structures here, fill little-endian fields, append DSDs, advance queue pointers, and ring hardware doorbells. Interrupt handlers parse response entries by `entry_type`, then dispatch status, ELS, ABTS, VP, or SA update completions using these layouts. Flash and mailbox paths use the register and FLT/FDT definitions to locate firmware, VPD, NVRAM, hardware event logs, and priority configuration.

## State And Persistence Behavior

The header defines persistent hardware/firmware state rather than owning memory itself. NVRAM structures represent nonvolatile adapter configuration. Flash layout and FDT records represent persistent flash content. Init control blocks and IOCBs are DMA-visible transient state consumed by firmware. Register structures map memory or I/O BAR state that persists until hardware reset or driver writes. Response entries are transient firmware-to-host records, but their fields update long-lived driver state such as port login state, resource usage, EDIF SA state, queue pointers, and VP identity.

## Dependencies And Integration Points

The header includes NVMe FC definitions and `qla_dsd.h`. It requires qla core constants such as `WWN_SIZE`, request-entry sizing, endian types, and bit macros. It is included throughout the qla2xxx driver and is central to `qla_iocb.c`, `qla_mbx.c`, `qla_isr.c`, `qla_init.c`, `qla_sup.c`, target support, NVMe support, and EDIF support. Any change here can affect firmware ABI across many source files.

## Risks And Edge Cases

- Structure layout is firmware ABI. Padding, packing, endian annotations, and field widths must match hardware specifications exactly.
- Several comments document big-endian subfields inside otherwise little-endian structures, especially WWNs, PRLI service parameters, SCSI LUNs, and DIF error data.
- The same union fields carry different meanings by context, such as completion status versus nport handle, NVMe response payload length versus EDIF SA index, and ELS request versus response fields.
- Flash addresses differ by chip family and sometimes by word versus byte addressing. Mixing 24xx/25xx/81xx/83xx/28xx constants can read or overwrite the wrong flash region.
- Request-ring IOCB entry counts and embedded DSD capacities must match builders; off-by-one errors can corrupt continuation entries.
- This header includes EDIF and NVMe fields in common status/command structures, so feature-specific changes can regress normal FCP paths.

## Test Signals

Build coverage should include all qla2xxx supported chip families and feature combinations: target mode, NPIV, NVMe FC, DIF, FCP priority, flash update, and EDIF. Static checks should assert key `sizeof()` values, offsets for firmware ABI structures, packed descriptor sizes, and endianness conversions in IOCB builders/parsers. Runtime tests should cover adapter initialization, NVRAM parsing, firmware load, mailbox commands, normal SCSI I/O, ELS/CT passthrough, ABTS/task management, VP enable/disable, flash reads, FCE tracing, and EDIF SA update/status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gbl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gbl.h

## Purpose

`qla_gbl.h` is the qla2xxx driver's global declaration hub. It collects cross-file function prototypes, global module parameters, exported data objects, interrupt handlers, mailbox helpers, IOCB builders, discovery helpers, target hooks, debugfs entry points, BSG handlers, flash/minidump support, NVMe hooks, EDIF hooks, and statistics APIs.

The file has no implementation logic, but it defines much of the driver's internal linkage contract.

## Important APIs, Types, And Data

- Initialization and adapter control prototypes cover PCI config, reset, diagnostics, ring setup, NVRAM config, firmware option updates, firmware load, loop resync, abort/quiesce, firmware dump allocation, and thermal reads.
- Discovery/session prototypes cover fabric login/logout, async login/logout/ADISC/PRLI/GNL/GPDB/GPSC/GFFID/GFPNID work, RSCN handling, fcport allocation/state, relogin, session deletion, and host map updates.
- IOCB and SCSI prototypes cover DSD/continuation building, SCSI start paths, DIF paths, markers, async SRB setup, IOCB allocation, SA replace issue, and SP release/timeout helpers.
- Mailbox and firmware service prototypes cover load/dump RAM, execute firmware, get/set options, port databases, link status, SFP reads/writes, trace enable/disable, flash update, remote registers, resource counts, and no-op mailboxes.
- Interrupt prototypes cover legacy and MSI-X handlers, response queue processing, SP lookup by handle, completed request processing, PUREX queueing, and PURLs handling.
- Support/debug/GS/attribute sections declare flash/NVRAM/optrom access, firmware dump routines, name-server commands, FDMI helpers, sysfs attributes, loopback/echo tests, and FCP priority config.
- EDIF declarations include SADB pool/release, SA delete pending checks, BSG app and ELS processing, doorbell/enode lifecycle, EDIF SCSI start, SA IOCB formatting/completion, auth ELS handling, and app-data cleanup.
- Global module parameters include logging, login retry, firmware loading, DIF, NVMe, queue, secure/EDIF, IOCB limit, and target options such as `ql2xsecenable` and `ql2xenforce_iocb_limit`.

## Control Flow

This header does not drive control flow directly. Instead, it enables qla source files to call each other across subsystem boundaries. For example, debugfs code calls mailbox and trace helpers declared here; EDIF code calls discovery, BSG, IOCB, target, and workqueue helpers; ISR code calls response and PUREX handlers; initialization code calls firmware, flash, and queue setup helpers. The organization by source file comments mirrors the driver's rough runtime phases: init, OS/workqueue, MID/NPIV, IOCB submission, mailbox services, interrupt handling, support/flash, debug, name server, attributes, debugfs, multi-queue, chip-family support, BSG, EDIF, NVMe, and stats.

## State And Persistence Behavior

The header declares state but does not own it. Extern module parameters persist for the module lifetime and influence behavior across initialization, discovery, I/O, and diagnostics. Extern caches such as `srb_cachep` and `qla_tgt_plogi_cachep` persist while the driver is loaded. Function prototypes manipulate persistent adapter, host, queue, port, firmware, flash, and EDIF state in their implementation files.

## Dependencies And Integration Points

The header includes `<linux/interrupt.h>` and depends on prior qla type definitions from `qla_def.h` and related headers. It is included broadly by qla2xxx implementation files, making it a central integration point. It also exposes interfaces to Linux SCSI, FC transport, BSG, NVMe FC, target mode, PCI error handling, debugfs, sysfs, mailbox, and firmware dump subsystems.

## Risks And Edge Cases

- Because this is a broad global header, adding prototypes here can mask poor subsystem boundaries and increase rebuild/review surface.
- Prototype drift between declarations and definitions will compile-fail, but semantic drift in ownership, locking, or completion expectations is harder to detect.
- Many functions operate on shared objects such as `scsi_qla_host_t`, `qla_hw_data`, `fc_port_t`, `srb_t`, request queues, and response queues. Callers must know locking and lifetime rules that are not encoded in prototypes.
- Duplicate or near-duplicate declarations exist for some functions, such as async abort and host attribute allocation, which increases maintenance noise.
- Module parameters declared here affect security and behavior globally, including EDIF enablement, firmware loading, NVMe enablement, queueing, logging, and reset behavior.

## Test Signals

The main validation signal is full-driver compile coverage across feature matrices and chip families. ABI-like internal tests should verify that every declared EDIF/debugfs/BSG/NVMe/target function has one definition and expected call sites. Runtime smoke tests should exercise initialization, discovery, SCSI I/O, mailbox, interrupt, debugfs, sysfs, BSG, target mode, NVMe, EDIF, firmware dump, flash access, and stats paths so declaration-level coupling is covered by real cross-file calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gbl.h -->
