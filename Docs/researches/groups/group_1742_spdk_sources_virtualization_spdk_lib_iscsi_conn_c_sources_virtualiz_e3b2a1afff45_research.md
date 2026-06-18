# Group Research: group_1742_spdk_sources_virtualization_spdk_lib_iscsi_conn_c_sources_virtualiz_e3b2a1afff45

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/conn.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/conn.c

Connection lifecycle, socket integration, poll-group scheduling, and SCSI task completion support for the SPDK iSCSI target. The file owns the global fixed-size connection array (`g_conns_array`), free and active connection lists, connection allocation/freeing, socket-group callback wiring, shutdown polling, logout timers, NOP-In keepalive handling, PDU write submission, and migration of full-feature normal sessions from the acceptor poll group to an idler target poll group.

The connection constructor allocates from the global pool, copies portal and CHAP defaults, initializes per-connection iSCSI parameters, task queues, PDU receive state, addresses, timers, and trace owner state, then posts `iscsi_conn_start` to the first poll group. Login starts on the acceptor thread with a login timeout. Once login reaches full feature, `iscsi_conn_schedule` groups all active connections for a target onto the same poll group and opens every SCSI LUN for normal sessions before adding the socket to the new poll group.

Destruction is deliberately staged. `iscsi_conn_destruct` marks the connection exited, aborts any in-progress PDU task, asks the backend to clean up if there are pending tasks, waits for SCSI device tasks to drain if needed, removes the socket from the poll group, closes the socket, clears transfer tasks, unregisters logout/login timers, frees queued PDUs/tasks, closes LUN descriptors, removes the connection from its session, and returns the object to the free list. Shutdown of the whole connection subsystem requests logout on all active connections and polls until `iscsi_get_active_conns(NULL)` reaches zero before freeing the connection array and notifying iSCSI shutdown completion.

The file is also the bridge from SCSI completion back to iSCSI response generation. `iscsi_task_cpl` dispatches to read or non-read completion paths. Large reads are split into subtasks and, when `DataSequenceInOrder` is enabled, completed subtasks are held in offset order before `iscsi_task_response` sends Data-In or final status. Large write/R2T tasks are accounted through `pending_task_cnt`, `data_out_cnt`, `pending_r2t`, and transfer-task queues owned mostly by `iscsi.c`.

PDU transmission is asynchronous through `spdk_sock_writev_async`. `iscsi_conn_write_pdu` verifies DIF when required, computes header and data CRC32C digests except for login responses, builds iovecs with `iscsi_build_iovs`, stores the PDU on `write_pdu_list`, and submits the socket request. `_iscsi_conn_pdu_write_done` removes completed PDUs, transitions the connection to exiting on socket errors, and either frees the PDU or defers R2T/Data-In PDUs into `snack_pdu_list` when ErrorRecoveryLevel is at least 1.

Important integration points are `iscsi_handle_incoming_pdus`, `iscsi_task_response`, `iscsi_task_mgmt_response`, `iscsi_clear_all_transfer_task`, `iscsi_conn_params_init`, SCSI LUN open/close/hot-remove callbacks, SPDK pollers, SPDK sock groups, global `g_iscsi`, and tracing definitions. Risk-sensitive areas are cross-thread state changes by `spdk_thread_send_msg`, mutex ordering between `g_conns_mutex`, `g_iscsi.mutex`, and target mutexes, shutdown deferral while callbacks still hold task references, SNACK PDU retention lifetime, and the assumption that normal-session poll-group migration can safely re-add an exiting connection for later cleanup.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/conn.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/conn.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/conn.h

Connection and per-connection LUN interface header for the SPDK iSCSI target. It defines negotiation table sizes, address buffer limits, the PDU receive-state enum, `spdk_iscsi_lun`, and the central `spdk_iscsi_conn` structure consumed by `conn.c`, `iscsi.c`, target-node code, and RPC/JSON reporting paths.

`spdk_iscsi_conn` stores the connection identity, portal/poll-group/socket/session pointers, login and connection state, timers, current receive PDU, outgoing and SNACK PDU queues, R2T/Data-In queues, CHAP state, negotiated parameter state, per-connection statistics and flow-control counters, initiator/target names and SCSI ports, session-facing sequence numbers, NOP keepalive state, target transfer tag allocation, partial text negotiation state, and LUN descriptors opened for the connection. The `SPDK_ISCSI_CONNECTION_MEMSET` macro in `conn.c` relies on the layout comment in this header: fields from `portal` onward are reset on allocation, while `id` and `is_valid` persist across pool reuse.

The header also publishes the connection lifecycle API (`initialize_iscsi_conns`, `shutdown_iscsi_conns`, construct/destruct/logout/drop), socket data read helpers, PDU write/free helpers, queued Data-In abort/drive routines, task completion callbacks, and JSON export. It depends on `iscsi/iscsi.h` for core iSCSI types and constants, SPDK queue/cpuset/SCSI headers, and internal trace definitions.

Risk points are mostly structural: changing fields before `portal` or altering reset expectations requires updating the reset macro; adding connection/session negotiation parameters requires updating `MAX_CONNECTION_PARAMS` or `MAX_SESSION_PARAMS`; queue ownership is split between `conn.c` and `iscsi.c`, so lifetime changes need matching task/PDU reference handling.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/conn.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/init_grp.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/init_grp.c

Initiator-group management implementation for SPDK iSCSI access control. It creates, registers, updates, unregisters, destroys, and serializes initiator groups, where each group has a numeric tag, a list of allowed initiator names, and a list of allowed initiator netmasks. The global group registry is `g_iscsi.ig_head`, protected by `g_iscsi.mutex` for public register, unregister, add, delete, and destroy operations.

The file maintains two parallel list element types: `spdk_iscsi_initiator_name` and `spdk_iscsi_initiator_netmask`. Add helpers validate maximum list sizes (`MAX_INITIATOR`, `MAX_NETMASK`), maximum string lengths, duplicate entries, allocation success, and legacy `"ALL"` tokens, which are automatically converted to `"ANY"` with warnings. Delete helpers find exact entries, remove them from their TAILQ, decrement counters, and free storage.

Batch operations are transactional within their local scope. `iscsi_init_grp_add_initiators` and `iscsi_init_grp_add_netmasks` roll back already-added entries if a later entry fails. Deletion batches attempt to restore removed entries on failure; if restoration fails they clear all entries of that type to avoid a partially inconsistent list. `iscsi_init_grp_create_from_initiator_list` creates a new group, adds names and masks, registers it, and destroys it on failure.

Public update APIs (`iscsi_init_grp_add_initiators_from_initiator_list`, `iscsi_init_grp_delete_initiators_from_initiator_list`) look up groups by tag under the global mutex and update both names and netmasks, rolling back the other half when needed. `iscsi_init_grp_unregister` removes a group from the global list but returns it to the caller for later destruction, matching target-node code that may need to check references.

JSON support emits both live information objects and config replay objects using method `iscsi_create_initiator_group`. Important dependencies are `iscsi/init_grp.h`, `iscsi/iscsi.h`, SPDK JSON write APIs, SPDK logging, and global `g_iscsi`. Risk points include exact-string duplicate matching after `"ALL"` to `"ANY"` conversion, all-or-clear rollback behavior on rare rollback allocation failure, and the need for callers to respect reference counts or external target-node bindings before destroying an unregistered group.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/init_grp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/init_grp.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/init_grp.h

Initiator-group type and management API header. It defines list entries for initiator names and initiator netmasks, both sized from the iSCSI connection/name constants, and `spdk_iscsi_init_grp`, which stores counts, TAILQ heads, a reference count, a numeric tag, and linkage into the global initiator-group list.

The exported API covers creation from caller-provided name/netmask arrays, adding and deleting initiator entries from existing groups, registering/unregistering groups in the global registry, lookup by tag, destruction, parser entry point, global destruction, and info/config JSON output. This header ties access-control group code to `iscsi/iscsi.h` and `iscsi/conn.h` for shared limits and address sizing.

The interface contract is small but central to target authorization: target-node configuration and RPC code can bind target nodes to these groups, while login checks later use the configured initiator names and netmasks to decide access. The `ref` field is declared here but managed by related target-node/configuration code rather than by this header itself.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/init_grp.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi.c -->
# File Research: sources/virtualization/spdk/lib/iscsi/iscsi.c

Main iSCSI protocol implementation for the SPDK target. This file owns the global `g_iscsi` object initialization, login negotiation, CHAP authentication, session allocation, iSCSI parameter negotiation hooks, command sequence-number handling, PDU parsing, digest verification, SCSI command dispatch, read/write data movement, task-management commands, logout/text/NOP/SNACK handling, PDU memory management, and the receive state machine entry point used by `conn.c`.

Early utility code provides random challenge generation, ISID conversion, hex/base64 helpers for CHAP, Reject PDU construction, header/data CRC32C calculation, partial data-digest calculation for split receive buffers, and iovec building for outgoing PDUs. DIF metadata support is integrated into both receive and transmit paths: Data-Out can be read into buffers with metadata interleaving, Data-In can strip or account for metadata, and CRC calculations can use SPDK DIF helpers when `pdu->dif_insert_or_strip` is set.

Session setup starts with `create_iscsi_sess`, which allocates a session from `g_iscsi.session_pool`, applies global defaults, creates a connection array, initializes session parameters, and attaches the first connection. `append_iscsi_sess` handles multi-connection session attachment by TSIH after validating portal-group tag, initiator port name, target, and maximum connection count. `iscsi_free_sess` releases parameters, connection storage, initiator SCSI port, and returns the session to its mempool.

Login processing is split into header and payload phases. `iscsi_pdu_hdr_op_login` validates login payload size and prepares a login response PDU. `iscsi_pdu_payload_op_login` parses text keys, initializes the initiator port name and session type, checks normal-session target existence, redirect/destructed/access status, handles duplicate ISID policy, configures target or discovery CHAP/digest policy, creates or appends a session, negotiates parameters, advances CSG/NSG login phases, and transitions the connection to running. Successful full-feature login updates connection/session variables and asks `conn.c` to schedule normal sessions onto a target poll group.

CHAP negotiation supports `AuthMethod=CHAP`, MD5 algorithm `CHAP_A=5`, target challenge generation, initiator response validation, and optional mutual CHAP. It loads secrets through `iscsi_chap_get_authinfo`, supports hex and base64 encoded responses/challenges, and rejects missing secrets, bad phase order, unsupported algorithms, and mutual-CHAP mismatches. Discovery sessions use global discovery auth settings; normal sessions use target-specific auth settings.

Text PDU handling validates final/continue bits and ITT continuity, parses incoming text parameters, negotiates regular keys, implements `SendTargets`, and supports split SendTargets responses using `conn->send_tgt_completed_size` and `conn->params_text` when the negotiated maximum receive segment is too small. Non-SendTargets text commands in a discovery session are treated as fatal. Text completion updates connection parameters.

SCSI command handling builds `spdk_iscsi_task` objects from SCSI request PDUs, rejects discovery-session commands, unsupported bidirectional CDBs, illegal immediate data, oversized transfer fields, and invalid no-data requests. Reads are queued directly when small enough or split into Data-In subtasks for large transfers. Write commands either queue a small immediate write or create an R2T transfer task, send R2T PDUs, aggregate Data-Out buffers into subtasks, and submit SCSI write work as buffers fill or final PDUs arrive.

Response generation covers Data-In PDUs, SCSI response PDUs, R2T PDUs, task-management responses, NOP-In responses, logout responses, rejects, and SNACK retransmissions. `iscsi_task_response` sends read data first and may embed final status in the last Data-In PDU; otherwise it sends a SCSI response with sense data and residual counts. Sequence counters (`StatSN`, `ExpCmdSN`, `MaxCmdSN`, DataSN, R2TSN, acked DataSN/R2TSN) are updated throughout these response paths.

Task management supports abort task, abort task set, logical unit reset, and rejects unsupported functions such as clear task set, clear ACA, warm reset, cold reset, and task reassign. Abort paths first clear queued Data-In or R2T transfer state, then use short pollers to wait until queued Data-In tasks can be aborted before queuing the SCSI management task.

Error recovery support is primarily ErrorRecoveryLevel 1 behavior. Completed Data-In and R2T PDUs can be retained on `snack_pdu_list`; Status SNACK, Data ACK SNACK, Data-In recovery SNACK, and R2T SNACK search retained PDUs or transfer tasks, validate ranges against acknowledged sequence numbers, retransmit retained PDUs, or reject invalid SNACKs. R-Data SNACK is explicitly unsupported.

The receive state machine (`iscsi_read_pdu`) cycles through awaiting a PDU object, reading BHS/AHS/header digest, dispatching header handlers, reading payload and data digest, dispatching payload handlers, recording trace events, and returning the PDU to the pool. It uses nonblocking socket reads and returns fatal errors to `conn.c` for connection teardown. `iscsi_handle_incoming_pdus` limits each callback to `GET_PDU_LOOP_COUNT` parsed PDUs or stops early if the connection migrates poll groups.

Important dependencies are `conn.c` for lifecycle and socket write/read wrappers, `task.c` for iSCSI task allocation/reference handling, `param.c` for key negotiation and variable copying, `tgt_node.c` for target lookup/access/SendTargets, SPDK SCSI device and LUN APIs, SPDK bdev buffer/DIF APIs, SPDK sock APIs, mempools, logging, tracing, MD5, CRC32C, and base64 helpers. Risk-sensitive areas include login phase transitions, sequence-number tolerance for initiator quirks, exact PDU/task reference ownership, retained SNACK PDU lifetime, Data-Out aggregation across two buffers, DIF metadata length calculations, and behavior when LUNs are hot-removed while split read/write tasks are active.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi.h -->
# File Research: sources/virtualization/spdk/lib/iscsi/iscsi.h

Core internal iSCSI target header. It defines SPDK iSCSI defaults and limits, PDU/task buffer constants, timeout defaults, login error codes, digest constants, common structs, global configuration structures, protocol phase constants, utility macros, global symbols, and cross-file function declarations used across the SPDK iSCSI library.

Major limits include initiator/target name sizes, portal and connection caps, default session and connection counts, queue depth, FirstBurstLength, MaxBurstLength, NOP interval, login/logout timeouts, maximum receive segment length, and per-connection Data-Out/Data-In buffer limits. `SPDK_ISCSI_MAX_RECV_DATA_SEGMENT_LENGTH` is fixed at 64 KiB for target receive, and `SPDK_ISCSI_MAX_BURST_LENGTH` derives from that and `MAX_DATA_OUT_PER_CONNECTION`.

`spdk_iscsi_pdu` is the main wire-object container. It embeds the BHS, up to two memory-pool data buffers, digest storage, payload and valid-byte counters, reference count, task association, command sequence number, write offset, DIF context, async socket request and iovec array, AHS storage, and compact sense-data storage. A static assert ensures the socket request and iovec array layout matches SPDK sock expectations.

The header also defines connection/session/auth/global state structures. `spdk_iscsi_sess` tracks connection array, SCSI initiator port, TSIH/ISID, target, negotiated session parameters, command window, and text-command ITT. `spdk_iscsi_poll_group` binds a poller, NOP poller, connection list, socket group, and active-target count. `spdk_iscsi_opts` and `spdk_iscsi_globals` hold configurable defaults, authentication groups, portal/init/target lists, poll groups, mempools, and the session table.

Declared functions cover subsystem init/fini, config JSON, option allocation/copy/free, discovery/auth-group management, task responses, PDU iovec construction, incoming PDU handling, session free, transfer task cleanup, digest calculation, PDU pool get/put, abort helpers, SCSI task queueing, and small inline helpers for data-buffer pool get/put and maximum immediate data sizing. `iscsi_get_max_immediate_data_size` intentionally adds digest and AHS overhead to `FirstBurstLength` for worst-case immediate receive allocation.

This header is the shared contract for `iscsi.c`, `conn.c`, `task.c`, `param.c`, portal/init/target group code, subsystem code, and RPC/config code. Risk points are broad API coupling, constants that shape mempool sizing and protocol validation, and structure fields that have cross-file ownership rules rather than local encapsulation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/iscsi/iscsi.h -->