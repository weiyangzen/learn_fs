# Research Group: subset-b-007651

This grouped report covers the requested Lustre LNet selftest and lnetconfig source files. Each section is source-tree aligned and bounded by reconciliation markers so it can be split into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/conrpc.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/conrpc.c

## Purpose
`conrpc.c` implements the console-side RPC transaction layer for LNet Selftest. It converts console session, group, batch, test, debug, and statistic operations into `srpc_client_rpc` calls, groups them in `lstcon_rpc_trans` transactions, waits for completion, aggregates per-node results, and manages the session pinger. This file sits between the higher-level console object model in `console.c` and the SRPC transport/framework in `framework.c` and `rpc.c`.

## Important APIs, Types, And Functions
- `struct lstcon_rpc` wraps one SRPC client RPC with console metadata: destination node, owning transaction, posted/finished/unpacked flags, final status, completion timestamp, and an embedded flag for per-node ping RPC storage.
- `struct lstcon_rpc_trans` is the transaction object: operation code, global/owner list links, queued RPC list, wait queue, outstanding counter, and negotiated session feature state.
- `lstcon_rpc_trans_prep()`, `lstcon_rpc_trans_addreq()`, `lstcon_rpc_trans_postwait()`, `lstcon_rpc_trans_abort()`, and `lstcon_rpc_trans_destroy()` are the core transaction lifecycle.
- `lstcon_sesrpc_prep()`, `lstcon_dbgrpc_prep()`, `lstcon_batrpc_prep()`, `lstcon_testrpc_prep()`, and `lstcon_statrpc_prep()` populate request bodies for the framework service types.
- `lstcon_rpc_trans_ndlist()` builds a transaction over a node-link list, using a caller-provided condition callback to skip nodes or reject the operation.
- `lstcon_rpc_trans_stat()` and `lstcon_rpc_trans_interpreter()` convert completed RPCs into `lstcon_trans_stat` counters and user-visible `lstcon_rpc_ent` entries.
- `lstcon_rpc_pinger_start()`, `lstcon_rpc_pinger_stop()`, and `lstcon_rpc_pinger()` maintain the background debug ping/end-session traffic for idle or aging sessions.

## Control Flow
Allocation starts in `lstcon_rpc_prep()`, which reuses `console_session.ses_rpc_freelist` or allocates a new wrapper, then calls `lstcon_rpc_init()` to create an SRPC client RPC through `sfw_create_rpc()`. A caller constructs a transaction with `lstcon_rpc_trans_prep()`, appends requests, and calls `lstcon_rpc_trans_postwait()`. That function posts every RPC with `sfw_post_rpc()`, temporarily releases the session mutex while sleeping on `tas_waitq`, then reacquires the mutex and aborts remaining RPCs on timeout, signal, or shutdown.

Completion is asynchronous. `lstcon_rpc_done()` runs from SRPC completion, records status and a nanosecond timestamp, marks the console RPC complete, decrements `tas_remaining`, and wakes the waiter when the last RPC finishes. Orphaned RPCs with no transaction are released from the callback path.

Reply processing is deferred until stats or interpretation. `lstcon_rpc_get_reply()` unpacks the message once, updates the node timestamp/state from the generic reply session id, and returns either an RPC error or a typed reply pointer. `lstcon_rpc_stat_reply()` then interprets framework statuses according to the transaction opcode, including session feature negotiation for `LST_TRANS_SESNEW`, special handling for `ESRCH` on session queries, and treating `EPERM` as a successful forced stop case for `LST_TRANS_TSBSTOP`.

Test creation uses bulk payloads. For client-side test add transactions, `lstcon_testrpc_prep()` allocates pages in the client RPC bulk descriptor, writes packed destination process ids into them with `lstcon_dstnodes_prep()`, and chooses either legacy bulk v0 parameters or `LST_FEAT_BULK_LEN` v1 parameters. Server-side test add transactions compute the maximum loop count expected from source/destination distribution and do not send a destination bulk.

The pinger timer periodically holds the console mutex, recycles any finished embedded per-node ping RPC, posts debug RPCs to active nodes whose remote timeout midpoint has passed, and if the console session has expired, posts remove-session RPCs to active nodes instead of rescheduling itself.

## State And Persistence Behavior
All state is in kernel memory under `console_session`: active transactions, free RPC wrappers, node state/stamps, the pinger timer, and feature masks. Nothing persists across module unload or session end. `ses_rpc_counter` tracks live initialized console RPCs so `lstcon_rpc_cleanup_wait()` can wait for orphan callbacks before freeing the freelist. Embedded RPCs are stored in `lstcon_node.nd_ping` and reset rather than put on the freelist.

## Dependencies And Integration Points
This file depends on the console data model from `console.h`, timers from `timer.h`, request/reply wire structs from `rpc.h`, and framework helpers from `selftest.h` such as `sfw_create_rpc()`, `sfw_post_rpc()`, `sfw_abort_rpc()`, and `sfw_unpack_message()`. It also uses LNet NID conversion helpers, kernel wait queues, spinlocks, atomics, list heads, page allocation, and `copy_to_user()`/`copy_from_user()` for user result lists.

## Risks And Edge Cases
- Transaction destruction can abandon posted-but-not-callbacked RPCs; the callback later frees them as orphans. This relies on correct `crp_trans = NULL` handling and `ses_rpc_counter` cleanup.
- Timeout handling marks nodes down only when the timeout timestamp is newer than the node's last stamp, protecting against stale completions but making timestamp ordering critical.
- `lstcon_dstnodes_prep()` assumes valid distribution/span values and page capacity; invalid span is rejected, but caller-provided test geometry remains a key risk.
- Feature negotiation is distributed across transaction and session state; mixed node features produce `EPROTO`.
- The pinger reuses embedded RPC storage and manipulates the shared pinger transaction, so list and lock invariants are important during session shutdown.

## Test Signals
Useful validation signals include successful session create/end across multiple nodes, feature mismatch returning `EPROTO`, add-test client bulk payload correctness for wraparound destination spans, transaction timeout changing node state to down, pinger recycling embedded RPCs, and clean `lstcon_rpc_module_fini()` assertions for empty freelist and zero live RPC count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/conrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/conrpc.h -->
# sources/distributed-fs/lustre-release/lnet/selftest/conrpc.h

## Purpose
`conrpc.h` declares the console RPC transaction interface used by `console.c` and implemented in `conrpc.c`. It defines the transaction opcodes, timeout policy, console RPC wrapper, transaction state, callback typedefs, and public preparation/posting/stat/interpreter APIs.

## Important APIs, Types, And Functions
- `LST_TRANS_TIMEOUT`, `LST_TRANS_MIN_TIMEOUT`, and `LST_VALIDATE_TIMEOUT()` bound console transaction waits.
- `LST_PING_INTERVAL` controls the console pinger cadence.
- `struct lstcon_rpc` tracks one console-owned SRPC client RPC, destination node, owner transaction, completion flags, status, reply timestamp, and whether storage is embedded.
- `struct lstcon_rpc_trans` groups RPCs for one console operation and contains global/owner list links, opcode, feature negotiation fields, wait queue, remaining counter, and queued RPCs.
- `LST_TRANS_*` opcodes identify session create/end/query/ping, test batch client/server add/run/stop/query, and stats query operations.
- `lstcon_rpc_cond_func_t` lets callers decide whether a node should receive an RPC.
- `lstcon_rpc_readent_func_t` lets interpreters add operation-specific payload into user result entries.
- Public lifecycle APIs include `lstcon_rpc_trans_prep()`, `lstcon_rpc_trans_ndlist()`, `lstcon_rpc_trans_postwait()`, `lstcon_rpc_trans_destroy()`, `lstcon_rpc_trans_abort()`, and `lstcon_rpc_cleanup_wait()`.

## Control Flow
The header expresses a two-step model: callers prepare individual typed RPCs or ask `lstcon_rpc_trans_ndlist()` to prepare a transaction over a node list, then post and wait with `lstcon_rpc_trans_postwait()`. After completion, callers inspect aggregate stats with `lstcon_rpc_trans_stat()` or fill user entries with `lstcon_rpc_trans_interpreter()`, then destroy the transaction.

## State And Persistence Behavior
The types are in-memory kernel structures only. Transaction state is linked into `console_session.ses_trans_list`; RPC wrappers may be transient allocations, freelist items, or embedded node pings. There is no disk persistence.

## Dependencies And Integration Points
The header includes LNet types, `rpc.h` wire protocol definitions, and `selftest.h` framework types. It forward-declares console objects to avoid circular inclusion. It is consumed primarily by `console.c` for user-facing operations and by `conrpc.c` for implementation.

## Risks And Edge Cases
The private transaction bit (`LST_TRANS_PRIVATE`) is used to prevent conflicting private operations on the same owner list; adding new opcodes must preserve this behavior. Timeout values below the minimum are clamped or normalized, so callers expecting shorter waits need to account for this policy. Callback typedefs use user pointers, so implementations must maintain careful `copy_to_user()` handling.

## Test Signals
Compile-time integration should catch missing forward declarations. Runtime signals are successful transaction creation/destruction, prevention of duplicate private transactions, correct timeout clamping, and clean pinger start/stop behavior through the declared APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/conrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/console.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/console.c

## Purpose
`console.c` implements the kernel-side LNet Selftest console object model and user operation backend. It owns global console session state, groups, nodes, batches, test descriptors, debug/stat query dispatch, the join-session acceptor service, and console initialization/finalization.

## Important APIs, Types, And Functions
- `console_session` is the global `struct lstcon_session`.
- Node helpers: `lstcon_node_find()`, `lstcon_node_put()`, `lstcon_ndlink_find()`, and `lstcon_ndlink_release()` manage global nodes and per-group/per-batch links.
- Group APIs: `lstcon_group_add()`, `lstcon_group_del()`, `lstcon_group_clean()`, `lstcon_group_refresh()`, `lstcon_nodes_add()`, and `lstcon_nodes_remove()`.
- Batch APIs: `lstcon_batch_add()`, `lstcon_batch_run()`, `lstcon_batch_stop()`, `lstcon_batch_del()` via internal destroy behavior, `lstcon_batch_list()`, and `lstcon_batch_info()`.
- Test APIs: `lstcon_test_add()` builds test descriptors and creates server/client test instances on remote nodes.
- Query APIs: `lstcon_test_batch_query()`, `lstcon_group_stat()`, `lstcon_nodes_stat()`, `lstcon_session_debug()`, `lstcon_batch_debug()`, `lstcon_group_debug()`, and `lstcon_nodes_debug()`.
- Session APIs: `lstcon_session_new()`, `lstcon_session_end()`, `lstcon_session_match()`, and `lstcon_session_feats_check()`.
- Service integration: `lstcon_acceptor_handle()` processes remote join requests; `lstcon_console_init()` registers the acceptor SRPC service, netlink, and ioctl notifier.

## Control Flow
Session creation validates feature bits, assigns a new session id from the local LNet NID and current milliseconds, creates the default batch, starts the console RPC pinger, and marks the session active. Session end creates remove-session RPCs for all known nodes, sets shutdown, stops the pinger, posts the end transaction, waits for orphan RPC cleanup, destroys all batches/groups, and returns to `LST_SESSION_NONE`.

Groups are aliases over referenced global nodes. Adding nodes first builds a temporary group from user-supplied NIDs, sends `LST_TRANS_SESNEW` RPCs to invite them into the session, interprets user results, then moves temporary node links into the target group even if individual remote outcomes vary. Removing nodes moves selected links into a temporary group, sends session-end RPCs, then releases them.

Batches hold client/server node lists and test descriptors. `lstcon_test_add()` verifies that the batch is idle and both groups contain active nodes, allocates a variable-length test descriptor, then calls `lstcon_test_nodes_add()`. That function first sends server-add test RPCs to destination nodes and only after success sends client-add RPCs to source nodes with destination bulk payloads generated by `conrpc.c`.

Running/stopping/querying a batch uses `lstcon_batch_op()` or `lstcon_test_batch_query()` to build batch RPC transactions against client node lists. Query results update local idle/running state when no active remote tests remain.

The join acceptor is an SRPC server-side framework service. It unpacks join requests, validates active session and feature compatibility, creates the named group if necessary, inserts the joining peer, marks it active/userland, and returns session name/timeout/status.

## State And Persistence Behavior
State is entirely volatile and rooted in `console_session`: session identity/key/name/features, global node hash/list, group list, batch list, active transaction list, RPC freelist, and pinger timer. Reference counts prevent groups from being modified while tests or other users hold them. Batch ids are generated from `ses_id_cookie`. Shutdown destroys all data structures and asserts list/hash emptiness.

## Dependencies And Integration Points
`console.c` uses `conrpc.c` for transaction construction/execution, `rpc.c`/`framework.c` through SRPC service registration and framework helpers, LNet NID conversions, netlink initialization from another file, and the `lnet_ioctl_list` notifier path. It copies user-provided node IDs and result entries through kernel user access helpers.

## Risks And Edge Cases
- Group and node lifetimes depend on manual refcounts; missed decref paths can leak nodes, while premature decref can invalidate tests.
- `lstcon_verify_group()` returns `-EINVAL` when no active nodes exist but leaves the group reference to be cleaned by the caller path; callers must consistently release partial references.
- Test creation intentionally adds a test to the local batch even when remote framework/RPC errors are recorded, allowing later inspection but making local state a partial reflection of remote state.
- Join acceptor group creation temporarily increments references and must handle busy groups and duplicates.
- Session shutdown calls into transaction cleanup while holding the session mutex in several phases; lock order with pinger and RPC callbacks is critical.

## Test Signals
Strong tests would cover session force-recreate, add/remove/refresh group behavior, duplicate group/batch detection, busy group rejection while tests reference it, partial test-add failures, batch run/stop/query transitions, join requests with wrong session id or unsupported features, and finalization assertions for empty lists and hashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/console.h -->
# sources/distributed-fs/lustre-release/lnet/selftest/console.h

## Purpose
`console.h` defines the in-kernel console data model for LNet Selftest and declares the public console operation functions consumed by ioctl/netlink command handling and module lifecycle code.

## Important APIs, Types, And Functions
- `struct lstcon_node` stores a remote process id, reference count, node state, remote timeout, last reply timestamp, and embedded ping RPC.
- `struct lstcon_ndlink` links a node into global, group, or batch hash/list structures.
- `struct lstcon_group` names a node alias set and owns node link lists, hash buckets, transaction list, refcount, and userland flag.
- `struct lstcon_batch` names a batch, stores its id/index/state/argument, tests, transactions, and client/server node lists/hashes.
- `struct lstcon_test` stores one test's type, source/destination groups, concurrency, loop count, distribution/span, stop behavior, and variable-length parameter payload.
- `struct lstcon_session` is the global console state: mutex, session id/key/name/features, timeout/shutdown flags, pinger, stats, all object lists, global node hash, and console RPC freelist/counter.
- Declared APIs cover sessions, groups, nodes, batches, tests, stats/debug, ioctl entry, console init/fini, and netlink init/fini.

## Control Flow
The header establishes the ownership hierarchy: one console session contains groups, batches, global nodes, and transactions; groups/batches/tests hold links or references to global nodes; tests reference source/destination groups; console RPC transactions execute against node lists and update the shared transaction stats.

## State And Persistence Behavior
These structures represent runtime state only. The session mutex serializes user-visible console operations, while `ses_rpc_lock` protects RPC freelist/counter and feature update paths. `LST_SESSION_NONE` and `LST_SESSION_ACTIVE` distinguish lifecycle state; batch state is `LST_BATCH_IDLE` or `LST_BATCH_RUNNING`.

## Dependencies And Integration Points
The header includes kernel user access, libcfs, LNet types, `selftest.h`, and `conrpc.h`. It exposes `console_session` for implementation files and is central to `console.c`, `conrpc.c`, module lifecycle, and command entry points.

## Risks And Edge Cases
Flexible arrays in `lstcon_group` and `lstcon_test` require exact allocation sizes. Node states are bitmask-like in some cleaning paths, so new state constants must remain compatible. Public functions accept user pointers and must be implemented with careful bounds and copy checks.

## Test Signals
Compile and structure-layout checks are important because these types are shared across many files. Runtime validation should include object lifecycle, refcount behavior, state transitions, and session cleanup assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/framework.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/framework.c

## Purpose
`framework.c` implements the server-side LNet Selftest framework and test orchestration layer. It handles framework SRPC services, remote session creation/removal/debug/stat requests, batch control, test instance creation, client test loops, feature/endian unpacking, and registration of test services such as BRW and ping.

## Important APIs, Types, And Functions
- `LST_INVALID_SID` is the exported invalid large-NID session id.
- Module parameters `session_timeout` and `rpc_timeout` control remote session expiry and outgoing test/framework RPC expiry.
- `sfw_data` tracks the active session, zombie sessions/RPCs, registered test cases, active framework server RPC, and shutdown state.
- `sfw_startup()` registers BRW/ping test services and framework services; `sfw_shutdown()` stops services, deactivates sessions, and frees zombies.
- Session handlers: `sfw_make_session()`, `sfw_remove_session()`, `sfw_debug_session()`, `sfw_get_stats()`, `sfw_add_session_timer()`, `sfw_deactivate_session()`, and `sfw_session_expired()`.
- Test orchestration: `sfw_add_test()`, `sfw_add_test_instance()`, `sfw_run_batch()`, `sfw_stop_batch()`, `sfw_query_batch()`, `sfw_run_test()`, and `sfw_test_rpc_done()`.
- Public helpers: `sfw_create_rpc()`, `sfw_create_test_rpc()`, `sfw_post_rpc()`, `sfw_abort_rpc()`, `sfw_alloc_pages()`, and `sfw_unpack_message()`.

## Control Flow
Startup initializes global framework state, registers BRW and ping test cases, adds their SRPC services, then registers six framework services: debug, query stats, make session, remove session, batch, and test. Framework services use `sfw_handle_server_rpc()` as the common handler, with test service also using `sfw_bulk_ready()` for destination-list bulk transfers.

On each framework request, `sfw_handle_server_rpc()` removes the active session timer to avoid expiry while mutating state, stores the active server RPC, unpacks headers/body, validates feature compatibility for most operations, dispatches to the service-specific handler, writes reply feature bits, restores the session timer, and clears the active pointer.

Remote session creation accepts a matching existing session, rejects different sessions unless forced, validates feature bits, and allocates a new `sfw_session`. Forced creation first deactivates the old session, moving it to zombie state and stopping active batches. Session removal decrements the session refcount and deactivates only when the last reference is gone.

Adding tests validates loop/concurrency/destination counts, session id, service id, and registered test case. Server-side test instances reserve request buffers for the target test service. Client-side test instances wait for bulk destination data, unpack test parameters, create one `sfw_test_unit` per destination/concurrency pair, and initialize the test client ops.

Batch run schedules each client test unit on a CPT-affine test workqueue. Each work item prepares a test RPC through the test-specific client ops, posts it, and completion either reschedules the unit for the next loop or marks the unit/instance/batch complete. Forced stop marks instances stopping and aborts active RPCs.

## State And Persistence Behavior
Framework state is volatile. A single active session is allowed, but deactivated sessions can remain as zombies until all active batches drain. Session timers are held in `stt_timer`. Test instances own free/active RPC lists for RPC reuse. Counters for BRW/ping errors and active batches are reported through stat replies.

## Dependencies And Integration Points
The file depends on SRPC transport from `rpc.c`, timer services from `timer.c`, workqueues from `module.c`, test service definitions from BRW and ping modules, LNet counters, NID conversion, and UAPI wire structures from `rpc.h`/`lnetst.h`. Console-side `conrpc.c` depends on exported helpers here for RPC creation, posting, aborting, and endian unpacking.

## Risks And Edge Cases
- Session timer removal can race with expiration; handlers drop RPCs with `-EAGAIN` when the timer is already running.
- Zombie session cleanup depends on active batch counters reaching zero.
- Feature negotiation must remain consistent with old peers that may not understand `msg_ses_feats`.
- Test buffer reservation error handling explicitly may remove more buffers than allocated, relying on lazy portals to recover.
- `sfw_unpack_message()` must be kept in sync with every packed wire body and currently unpacks only the fields it knows.

## Test Signals
Signals include session timeout expiry, force session replacement with active batches, stats reporting active batch/zombie counts, adding ping and BRW tests with both bulk parameter formats, batch stop forced vs non-forced behavior, feature mismatch replies, endian-swapped message handling, and clean service shutdown with no zombie sessions/RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/framework.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/module.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/module.c

## Purpose
`module.c` is the LNet Selftest kernel module entry/exit file. It creates workqueues, starts SRPC and framework services, initializes the console, performs wire-layout assertions, and unwinds initialization safely on failure or module exit.

## Important APIs, Types, And Functions
- `enum LST_INIT_*` tracks partial initialization progress.
- `lst_serial_wq` is the ordered framework/serial workqueue exported through `selftest.h`.
- `lst_test_wq` is a per-CPT array of test workqueues.
- `lnet_selftest_structure_assertion()` uses `BUILD_BUG_ON()` to pin wire struct sizes and offsets.
- `lnet_selftest_init()` performs setup in order: libcfs, serial workqueue, per-CPT test workqueues, SRPC startup, framework startup, console init.
- `lnet_selftest_exit()` unwinds in reverse order according to `lst_init_step`.

## Control Flow
The module is initialized through `late_initcall_sync()`, so it starts late in kernel initialization. It first verifies SRPC wire layout, calls `libcfs_setup()`, allocates an ordered serial workqueue, allocates one test workqueue per LNet CPU partition, reserves at least one CPU per partition for LND by reducing worker count, then calls `srpc_startup()`, `sfw_startup()`, and `lstcon_console_init()`. Any failure jumps to the common unwind function.

Exit uses a fallthrough switch keyed by the last successful step. It finalizes console, framework, SRPC, all per-CPT test workqueues, the workqueue pointer array, and the serial workqueue.

## State And Persistence Behavior
State is process/kernel-module local: init step, exported workqueue pointers, and module metadata. No persistent data is written. Cleanup assumes lower layers have drained their work before workqueues are destroyed.

## Dependencies And Integration Points
This file ties together `selftest.h`, `console.h`, libcfs setup, LNet CPT topology, SRPC startup/shutdown, framework startup/shutdown, console init/fini, and Linux module metadata.

## Risks And Edge Cases
- Wire layout assertions are critical because different nodes exchange packed SRPC messages; changing structs without updating these checks can cause runtime protocol corruption.
- Error unwind depends on `lst_init_step` being advanced only after each successful phase.
- Per-CPT workqueue creation must handle partial allocation and destroy only non-null workqueues.

## Test Signals
Build failures from `BUILD_BUG_ON()` indicate wire ABI drift. Runtime signals include successful load/unload, injected failures at each init phase, correct destruction of partial workqueues, and clean shutdown without workqueue use-after-destroy warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/ping_test.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/ping_test.c

## Purpose
`ping_test.c` implements the LNet Selftest ping test service and client operations. It provides a simple request/reply test that stamps sequence numbers and send time, validates replies, counts ping errors in the session, and registers the ping SRPC service.

## Important APIs, Types, And Functions
- `LST_PING_TEST_MAGIC` identifies valid ping test messages.
- Module parameter `ping_srv_workitems` controls server work item count.
- `struct lst_ping_data` holds a lock-protected sequence counter for client requests.
- Client ops: `ping_client_init()`, `ping_client_fini()`, `ping_client_prep_rpc()`, and `ping_client_done_rpc()`.
- Server handler: `ping_server_handle()`.
- Registration helpers: `ping_init_test_client()` and `ping_init_test_service()`.
- Exported objects: `ping_test_client` and `ping_test_service`.

## Control Flow
On client test initialization, the shared sequence counter is reset. Each prepared RPC is created with `sfw_create_test_rpc()` with no bulk, writes magic, atomically assigns a sequence number under `pnd_lock`, and records current real time in the request. Completion verifies transport status, byte-swaps reply fields if necessary, checks magic and sequence, increments `sn_ping_errors` on failures, and logs round-trip latency on success.

The server handler unpacks byte-swapped request fields when needed, validates the request type and magic, echoes sequence/magic in the reply, validates session feature bits, and returns `EPROTO` in the ping reply status when unsupported features are present.

## State And Persistence Behavior
Ping state is volatile. The global sequence counter is reset per client test instance. Per-session error counts are stored in `sfw_session.sn_ping_errors`. There is no persistence after session teardown.

## Dependencies And Integration Points
The ping test plugs into the framework through `struct sfw_test_client_ops` and `struct srpc_service`. It uses SRPC ping request/reply wire structs from `rpc.h`, session state from `selftest.h`, and the framework scheduler/RPC creation path in `framework.c`.

## Risks And Edge Cases
- The sequence counter is global to the module, so concurrent ping client instances would share/reset it; framework behavior likely avoids conflicting runs, but this is a concurrency assumption.
- Time delta uses real-time timestamps, so clock adjustments could affect logged latency.
- Feature mismatch is reported in the reply status while transport status can still be zero; callers must inspect framework/test status.

## Test Signals
Useful tests include valid ping round trips, bad magic rejection, sequence mismatch detection, byte-swapped request/reply handling, nonzero RPC status error counting, and unsupported feature masks returning `EPROTO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/ping_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/rpc.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/rpc.c

## Purpose
`rpc.c` implements the SRPC transport layer for LNet Selftest. It manages LNet lazy portals, passive request buffers, active reply/bulk RDMA operations, client and server RPC state machines, service registration, per-CPT service data, counters, timers, abort/shutdown behavior, and the single LNet event handler.

## Important APIs, Types, And Functions
- `srpc_data` stores global SRPC state, registered services, event handler pointer, counters, and matchbits.
- Service lifecycle: `srpc_add_service()`, `srpc_remove_service()`, `srpc_shutdown_service()`, `srpc_finish_service()`, `srpc_abort_service()`, and internal `srpc_service_init()/fini()`.
- Buffer lifecycle: `srpc_service_add_buffers()`, `srpc_service_remove_buffers()`, `srpc_add_buffer()`, `srpc_service_post_buffer()`, and `srpc_service_recycle_buffer()`.
- Client lifecycle: `srpc_create_client_rpc()`, `srpc_post_rpc()`, `srpc_abort_rpc()`, `srpc_send_rpc()`, `srpc_client_rpc_done()`, and client timeout timer helpers.
- Server lifecycle: `srpc_init_server_rpc()`, `srpc_handle_rpc()`, `srpc_server_rpc_done()`, and `srpc_send_reply()`.
- Bulk helpers: `srpc_alloc_bulk()`, `srpc_init_bulk()`, `srpc_free_bulk()`, `srpc_prepare_bulk()`, and `srpc_do_bulk()`.
- LNet helpers: `srpc_post_passive_rdma()`, `srpc_post_active_rdma()`, `srpc_post_passive_rqtbuf()`, and `srpc_lnet_ev_handler()`.
- Module-level lifecycle: `srpc_startup()` and `srpc_shutdown()`.

## Control Flow
Startup initializes LNet NI, installs lazy portals for framework and test requests, initializes matchbits using current seconds in the high bits, and starts the selftest timer thread. Services are added only while SRPC is running. Each service allocates per-CPT `srpc_service_cd`; framework services use one effective CPT while test services use all LNet CPTs. Server RPC descriptors are preallocated into free lists, and request buffers are posted as passive PUT memory descriptors on the service portal.

Incoming requests arrive through `srpc_lnet_ev_handler()` as `SRPC_REQUEST_RCVD`. The handler validates event status, message length, magic, and type, moves the buffer from posted to active/blocked state, selects a free server RPC if available, initializes it, and schedules `srpc_handle_rpc()`. If no server RPC is free, the buffer waits on `scd_buf_blocked`.

`srpc_handle_rpc()` is a server-side state machine. In `NEWBORN`, it validates message version and calls the service handler. If the handler allocated bulk, it posts active bulk RDMA and waits for completion. After optional `sv_bulk_ready`, it sends a reply by active PUT to the client's reply matchbits. On reply completion, it recycles or frees request buffers, moves the server RPC back to free state or immediately services a blocked buffer, and records drop counters on failure.

Client RPCs are workitems driven by `srpc_send_rpc()`. A new client RPC posts a passive reply buffer, optional passive bulk buffer, and active PUT request. It then waits for request send, reply receive, and optional bulk event in order even though LNet events may arrive in any order. Completion defuses the timer, closes the RPC, and invokes the caller callback. Abort unlinks request/reply/bulk MDs and completes when all expected events have fired.

The LNet event handler maps events back to `srpc_event` owners, records status and LNet event kind, updates counters, schedules the owning workitem, and handles multi-event active GET completion by waiting for unlink/final event.

## State And Persistence Behavior
SRPC state is volatile kernel memory. Counters are atomics exported through `srpc_get_counters()`. Matchbits are monotonic during the module lifetime. Service buffer counts and free/active lists are per-CPT. Client RPC timers use `stt_timer`. No disk persistence exists.

## Dependencies And Integration Points
This file is the transport base for `framework.c`, `conrpc.c`, ping/BRW tests, and module lifecycle. It depends on LNet APIs (`LNetMEAttach`, `LNetMDAttach`, `LNetMDBind`, `LNetPut`, `LNetGet`, lazy portals, NI init/fini), selftest workqueues, libcfs allocation/CPT helpers, kernel spinlocks/atomics/lists, and timer services from `timer.c`.

## Risks And Edge Cases
- Event ordering is asynchronous; client logic explicitly serializes request, reply, and bulk handling, so missing `ev_fired` updates can deadlock completions.
- Shutdown waits for posted buffers to unlink and active RPCs to drain; services must be removed before `srpc_shutdown()` asserts the registry is empty.
- Buffer growth is lazy and error-throttled by `scd_buf_err_stamp`; memory pressure can reduce service availability.
- `srpc_send_reply()` reposts test request buffers before replying to improve throughput, creating subtle lifetime requirements around `rpc->srpc_reqstbuf`.
- Active RDMA failures call `LNetMDUnlink()` and rely on subsequent unlink events for completion.

## Test Signals
Validation should include service add/remove lifecycle, request buffer add/remove under memory pressure, client timeout and abort paths, bad magic/type/length request dropping, reply version mismatch, bulk PUT/GET counters, blocked request buffers when no server RPC is free, service shutdown with active RPCs, and complete module startup/shutdown without leaked services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/rpc.h -->
# sources/distributed-fs/lustre-release/lnet/selftest/rpc.h

## Purpose
`rpc.h` defines the packed SRPC wire protocol for LNet Selftest: service ids, message types, request/reply bodies, test parameter bodies, and the top-level `srpc_msg` envelope. It is shared by console, framework, test, and transport code.

## Important APIs, Types, And Functions
- `enum srpc_service_type` assigns framework and test service ids. Framework services are below `SRPC_FRAMEWORK_SERVICE_MAX_ID`; BRW and ping are test services.
- `enum srpc_msg_type` defines request/reply message type pairs, with the invariant that reply equals request plus one.
- Generic request/reply bodies define the required first fields: reply matchbits, bulk matchbits, reply status, and optional session id.
- Framework wire bodies include make/remove/join/debug session, batch control, stats, and test-add request/reply structures.
- Test wire bodies include ping and BRW request/reply structures.
- `struct srpc_msg` is the packed envelope containing magic, version, type, reserved fields, session feature mask, and body union.
- `srpc_unpack_msg_hdr()` byte-swaps only the envelope header when magic indicates opposite endian.

## Control Flow
Callers set `msg_type` from service ids using helpers in `selftest.h`, fill the corresponding union member, and rely on the first fields of request/reply bodies for generic transport handling of reply/bulk matchbits and status. Receivers unpack the header first, then dispatch to framework/test-specific body unpacking.

## State And Persistence Behavior
There is no runtime state in this header. Its packed structs form the network ABI and must remain compatible across nodes. `SRPC_MSG_MAGIC` and `SRPC_MSG_VERSION` gate message validation.

## Dependencies And Integration Points
The header includes UAPI `lnetst.h` for session ids, batch ids, counters, feature flags, and test parameter types. It is included by `selftest.h`, `conrpc.h`, `framework.c`, `rpc.c`, and test modules.

## Risks And Edge Cases
Packed layout is fragile; field additions or reordering can break cross-node communication. The generic first-field caveat is required by transport code that writes `msg_body.reqst.rpyid` and `bulkid` independent of message type. Endian handling is split between `srpc_unpack_msg_hdr()` and body-specific unpackers, so new message types need both.

## Test Signals
Build-time structure assertions in `module.c` are primary ABI tests. Runtime tests should include version mismatch, magic mismatch, endian-swapped messages, and every service request/reply pair mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/selftest.h -->
# sources/distributed-fs/lustre-release/lnet/selftest/selftest.h

## Purpose
`selftest.h` is the central internal header for LNet Selftest. It defines netlink attributes, shared workitem states, SRPC portals/events/bulk/buffer/client/server/service types, framework session/batch/test structures, helper macros, inline workqueue/RPC initialization helpers, and cross-file function declarations.

## Important APIs, Types, And Functions
- Netlink attribute enums describe session/group/group-node-list properties.
- `enum lsr_swi_state` defines workitem/RPC state names used by client/server state machines.
- Portal constants define request and RDMA portals.
- `srpc_service2request()` and `srpc_service2reply()` map service ids to message types.
- Transport structs: `srpc_event`, `srpc_bulk`, `srpc_buffer`, `swi_workitem`, `srpc_server_rpc`, `srpc_client_rpc`, `srpc_service_cd`, and `srpc_service`.
- Framework structs: `lst_session_id`, `sfw_session`, `sfw_batch`, `sfw_test_client_ops`, `sfw_test_instance`, `sfw_test_unit`, and `sfw_test_case`.
- Inline helpers initialize workitems and client RPCs, schedule/cancel work, destroy client RPCs through kref, detect event pending, and wait for service shutdown.
- Externs declare public APIs implemented by `framework.c`, `rpc.c`, `timer.c`, ping, BRW, and `module.c`.

## Control Flow
The header describes the layering: services receive SRPC server RPCs on request portals, framework code creates and posts client RPCs, workitems run on serial or test workqueues, test client ops prepare/done per-test RPCs, and service shutdown waits through `srpc_wait_service_shutdown()`.

`srpc_init_client_rpc()` is a key inline constructor. It zeroes the variable-sized client RPC, binds it to the CPT-selected test workqueue, initializes lock/refcount/list, stores callbacks/private data, invalidates MD handles, marks all events fired initially, and fills the SRPC envelope magic/version/request type.

## State And Persistence Behavior
The header defines only in-memory state. Reference counts (`kref` for client RPCs, `refcount_t` for sessions), atomics, spinlocks, and list heads govern object lifetime. No persistent format exists beyond the packed wire structs in `rpc.h`.

## Dependencies And Integration Points
It includes Linux refcount/libcfs/LNet headers, UAPI selftest definitions, `rpc.h`, and `timer.h`. It is the primary include for all selftest C files and exposes `lst_serial_wq` and `lst_test_wq` allocated by `module.c`.

## Risks And Edge Cases
- Inline functions encode core invariants; changes affect many files at once.
- `srpc_client_rpc_size()` depends on the embedded flexible `bk_iovs` count and must match allocation/initialization.
- Service/request mapping uses assertions for invalid ids; new services require updates in both `rpc.h` and this mapping.
- Workitem cancellation sets state to done before `cancel_work_sync()`, which callers depend on for shutdown races.

## Test Signals
Compile coverage across all selftest files is essential. Runtime signals include correct service-to-message mappings, client RPC allocation sizes with zero/nonzero bulk iov counts, workitem scheduling on CPT queues, kref cleanup callbacks, and `swi_state2str()` coverage for logged states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/timer.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/timer.c

## Purpose
`timer.c` implements a small selftest timer facility used by framework session expiry, console pinger scheduling, and client RPC timeouts. It maintains a sorted slotted queue and a kernel thread that wakes periodically to execute expired callbacks.

## Important APIs, Types, And Functions
- Slot constants define an 8-second minimum poll interval and 128 slots, covering 1024 seconds before wrap.
- `stt_data` holds the spinlock, previous processed slot, slot lists, shutdown flag, wait queue, and timer-thread count.
- `stt_add_timer()` inserts a timer into the appropriate sorted slot.
- `stt_del_timer()` removes a pending timer and reports whether it was active.
- `stt_expire_list()` runs expired callbacks outside the timer lock.
- `stt_check_timers()` processes all slots from the previous slot through the current slot.
- `stt_startup()` initializes data and starts the `st_timer` thread; `stt_shutdown()` asserts all timers are removed, signals the thread, and waits for it to exit.

## Control Flow
Timers are added with an absolute real-time second expiry and a callback/data pair. The timer thread loops until shutdown, checking timers and then sleeping up to one slot interval on a wait queue. Expiry removes each due timer from its slot, unlocks, invokes the callback, and relocks before continuing. Deletion removes list membership if still queued; if it returns zero, the callback may already be running on another CPU.

## State And Persistence Behavior
All timer state is global kernel memory and is reset on startup. Timers are intrusive list nodes owned by callers. Shutdown requires every slot list to be empty before setting shutdown.

## Dependencies And Integration Points
The implementation uses `struct stt_timer` from `timer.h`, kernel kthreads/wait queues/spinlocks, libcfs time conversion, and `lst_wait_until()` from `selftest.h`. Users include `framework.c`, `conrpc.c`, and `rpc.c`.

## Risks And Edge Cases
- Timer expiry resolution is coarse at eight seconds, so callers must tolerate delayed callbacks.
- Slot wrap logic assumes timers are not scheduled too far beyond the 1024-second coverage window.
- `stt_del_timer()` returning zero is ambiguous between inactive and callback-running, so callers that need quiescence must add their own synchronization.
- Shutdown asserts no outstanding timers; missed cleanup causes a hard assertion.

## Test Signals
Tests should cover ordered expiry within a slot, deletion before expiry, callback-running race behavior, session/RPC timeout integration, and shutdown after all clients have removed timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/timer.h -->
# sources/distributed-fs/lustre-release/lnet/selftest/timer.h

## Purpose
`timer.h` declares the internal selftest timer object and lifecycle APIs implemented by `timer.c`.

## Important APIs, Types, And Functions
- `struct stt_timer` contains an intrusive list node, absolute expiry seconds, callback function, and callback data pointer.
- `stt_add_timer()` queues a timer.
- `stt_del_timer()` removes a queued timer and returns whether it was pending.
- `stt_startup()` initializes timer infrastructure.
- `stt_shutdown()` stops the timer thread after all timers are removed.

## Control Flow
Callers initialize `stt_list`, assign `stt_expires`, `stt_func`, and `stt_data`, then call `stt_add_timer()`. They must call `stt_del_timer()` before object destruction unless the callback owns cleanup.

## State And Persistence Behavior
The timer object is embedded in caller-owned state. No persistent state exists. List membership is the active/inactive indicator.

## Dependencies And Integration Points
The header assumes Linux `list_head` and `time64_t` are available through including contexts. It is included by `selftest.h`, making timers available throughout the selftest subsystem.

## Risks And Edge Cases
Callbacks run asynchronously and may race deletion; callers must understand the `stt_del_timer()` caveat from the implementation. Destroying an object with a still-queued timer will corrupt the timer list.

## Test Signals
Compile integration plus runtime add/delete/startup/shutdown tests are sufficient for the header-level contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/Makefile.am -->
# sources/distributed-fs/lustre-release/lnet/utils/Makefile.am

## Purpose
This Automake file defines the user-space LNet utility build targets and pkg-config installation for the Lustre LNet utilities directory.

## Important APIs, Types, And Functions
- `AM_CFLAGS` and `AM_LDFLAGS` set common utility compiler/linker flags, including PIC, `_GNU_SOURCE`, utility flags, libnl flags, and local link path.
- `SUBDIRS = lnetconfig` builds the `liblnetconfig` subdirectory first.
- `pkgconfig_DATA = lnet.pc` installs the LNet pkg-config file.
- Under `if UTILS`, it builds `routerstat`, `lst`, and `lnetctl`.
- `routerstat_LDADD`, `lst_LDADD`, and `lnetctl_LDADD` link against `lnetconfig/liblnetconfig.la`; `lst` and `lnetctl` also link libnl, yaml, and electric fence when configured.
- Under `if TESTS`, it additionally builds `wirecheck`.

## Control Flow
Automake conditionals decide which utilities are built. The lnetconfig library is a subdir dependency for top-level utilities. Source lists map one main C file per utility target.

## State And Persistence Behavior
The file does not manage runtime state. It affects generated build system outputs and installed pkg-config metadata.

## Dependencies And Integration Points
It depends on Autotools variables from the Lustre configure system, libnl3, yaml, optional libefence, and the lnetconfig library built in the subdirectory.

## Risks And Edge Cases
Missing yaml/libnl flags will break `lst` or `lnetctl` linking. Because `lst_CFLAGS` differs from `AM_CFLAGS` and defines `_LINUX_TIME_H`, changes to common flags may not apply uniformly. Conditional build coverage must be checked for both `UTILS` and `TESTS` configurations.

## Test Signals
Build signals include `make` with utilities enabled/disabled, tests enabled, install of `lnet.pc`, and successful link of `routerstat`, `lst`, `lnetctl`, and `wirecheck`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnet.pc.in -->
# sources/distributed-fs/lustre-release/lnet/utils/lnet.pc.in

## Purpose
`lnet.pc.in` is the pkg-config template for the Lustre Network API/kAPI package. Configure substitutes installation paths and version so external builds can discover LNet include flags, link flags, and Module.symvers location.

## Important APIs, Types, And Functions
- Variables: `prefix`, `exec_prefix`, `libdir`, `includedir`, `version`, and `symversdir`.
- `Cflags` exposes libcfs and lnet include directories.
- `Libs` exposes the library directory and `-llnetconfig`.
- Metadata fields are `Description`, `Name`, and `Version`.

## Control Flow
There is no runtime control flow. Configure expands `@prefix@`, `@exec_prefix@`, `@libdir@`, `@includedir@`, and `@PACKAGE_VERSION@` into the installed `lnet.pc`.

## State And Persistence Behavior
The generated `.pc` file is installed under `${libdir}/pkgconfig` by `Makefile.am`. It persists as build metadata for downstream users.

## Dependencies And Integration Points
Downstream users can run `pkg-config --cflags --libs lnet` for user-space utilities or `pkg-config --variable=symversdir lnet` for kABI/Module.symvers integration.

## Risks And Edge Cases
The package `Name` is `lnet-kapi` while the installed file is `lnet.pc`; downstream scripts must use the file/package name expected by pkg-config. Incorrect include/lib substitutions break external consumers.

## Test Signals
After install, `pkg-config --cflags --libs lnet` should print usable include and link flags, and `pkg-config --variable=symversdir lnet` should resolve to `${prefix}/src/lustre`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnet.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/Makefile.am -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/Makefile.am

## Purpose
This Automake file builds `liblnetconfig.la`, the user-space LNet configuration helper library used by utilities such as `lst`, `lnetctl`, and `routerstat`.

## Important APIs, Types, And Functions
- `lib_LTLIBRARIES = liblnetconfig.la` declares the installed libtool library.
- `liblnetconfig_la_SOURCES` includes core config, LND-specific config, cYAML wrapper, UDSP, and netlink support sources/headers.
- `liblnetconfig_la_CPPFLAGS` enables large-file support, `LUSTRE_UTILS`, libnl flags, and PIC.
- `liblnetconfig_la_LDFLAGS` links against libcfs build output, yaml, math, readline, and sets libtool version info `4:0:0`.
- `liblnetconfig_la_LIBADD` adds `libcfs.la` and libnl libraries.

## Control Flow
Automake compiles all listed sources into a shared libtool library. The parent `lnet/utils/Makefile.am` links user utilities against this library.

## State And Persistence Behavior
The file influences build artifacts and installed library ABI metadata. It has no runtime state.

## Dependencies And Integration Points
Dependencies include libcfs user-space library, libyaml, libm, libreadline, libnl3, and the surrounding Lustre build system.

## Risks And Edge Cases
Adding public functions may require version-info policy review. Missing libyaml or libnl flags break the library and therefore all dependent utilities. Source list omissions can produce link-time failures in downstream utilities.

## Test Signals
Build `liblnetconfig.la`, link parent utilities, run installed-library dependency checks, and verify configurations with and without optional readline/libnl settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.c -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.c

## Purpose
`cyaml.c` implements a small C tree wrapper around libyaml for Lustre LNet configuration utilities. It parses block-style YAML into an n-tree of `struct cYAML`, provides lookup/traversal/free helpers, supports programmatic tree creation, prints/dumps YAML text, and constructs structured YAML error output.

## Important APIs, Types, And Functions
- Internal parse state: `enum cYAML_handler_error`, `enum cYAML_tree_state`, `struct cYAML_tree_node`, and token handler dispatch table.
- Internal list stack: `struct cYAML_ll`, `cYAML_ll_push()`, `cYAML_ll_pop()`, `cYAML_ll_free()`, and `cYAML_ll_count()`.
- Parser functions: `cYAML_load()`, `cYAML_build_tree()`, and internal `cYAML_parser_to_tree()`.
- Token handlers process stream/document starts/ends, block mappings, sequences, keys, values, scalars, entries, and unsupported tokens.
- Tree access: `cYAML_get_object_item()`, `cYAML_get_object_child()`, `cYAML_get_next_seq_item()`, `cYAML_is_sequence()`, and `cYAML_find_object()`.
- Cleanup/traversal: `cYAML_clean_usr_data()`, `cYAML_free_tree()`, and internal recursive walk callbacks.
- Printing: `cYAML_dump()`, `cYAML_print_tree()`, `cYAML_print_tree2file()`, `print_object()`, `print_array()`, `print_string()`, `print_number()`, and `print_simple()`.
- Creation/insertion: `cYAML_create_object()`, `cYAML_create_seq()`, `cYAML_create_seq_item()`, `cYAML_create_string()`, `cYAML_create_number()`, `cYAML_insert_child()`, and `cYAML_insert_sibling()`.
- Error construction: `cYAML_build_error()`.

## Control Flow
Parsing begins in `cYAML_build_tree()` or `cYAML_load()`, which initializes a libyaml parser from file, string block, or stdin. `cYAML_parser_to_tree()` scans tokens until stream end or error, optionally logs debug state, dispatches each token to `dispatch_tbl`, and builds `struct cYAML` nodes using a stack of parent nodes.

The parser supports block mappings and block sequences. Keys create sibling nodes; scalar values assign type/value; block mapping starts create children and push current parent; block ends pop the stack and mark completion at top level. Flow collections, aliases, anchors, tags, and directives are rejected as unsupported.

Type assignment treats `null`, booleans, decimal/scientific numbers, and `0x` hex integers specially; otherwise scalars become strings. Lookup helpers either search recursively (`cYAML_get_object_item()` and `cYAML_find_object()`) or only direct children (`cYAML_get_object_child()`).

Printing builds a dynamically grown buffer and uses a stack rather than direct recursive printing for object/array descent. Programmatic creation allocates nodes, duplicates keys/strings, and inserts children/siblings in append order. Error construction appends command-keyed arrays of entity objects containing `seq_no`, `errno`, and `descr`.

## State And Persistence Behavior
Parsed trees are heap allocated and caller-owned. Nodes may carry caller-owned `cy_user_data`; `cYAML_clean_usr_data()` invokes a callback for those fields before regular tree free. No global mutable parser state exists. Output buffers returned by `cYAML_dump()` are heap allocated and caller-owned.

## Dependencies And Integration Points
The file depends on libyaml, libc, math, Lustre `liblnetconfig.h`, libcfs user-space list helpers, and `cyaml.h`. It is compiled into `liblnetconfig.la` and used by LNet user-space configuration tools to parse and emit YAML command/config data.

## Risks And Edge Cases
- The `ensure()` helper appears to allocate a new buffer whenever `in` is non-null because it compares `curlen <= curlen + len`, which is always true for positive `len`; this is inefficient but preserves content. It also frees the input on allocation failure.
- `cYAML_dump()` allocates a buffer, then sets it to NULL for a NULL node without freeing the initial buffer, creating a small leak on that path.
- `print_string()` temporarily writes NUL bytes into `cy_valuestring` to handle multiline strings, then restores newlines; this mutates tree data during printing and is unsafe if shared.
- Unsupported YAML constructs are intentionally rejected, so valid YAML using flow style, anchors, or tags will fail.
- Some allocation paths duplicate keys/values without checking `strdup()` failure.

## Test Signals
Tests should parse nested block maps, arrays, scalar strings/numbers/hex/bools/null, unsupported flow syntax, malformed state transitions, file-open errors, error-tree creation, direct vs recursive lookup, sequence iteration, user-data cleanup, dump/print round trips, and allocation-failure behavior where practical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.h -->
# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.h

## Purpose
`cyaml.h` declares the public cYAML tree API used by Lustre user-space LNet configuration code. It defines node types, the `struct cYAML` tree node layout, callbacks, parser/dump/free functions, lookup helpers, constructors, insertion helpers, and structured error creation.

## Important APIs, Types, And Functions
- `enum cYAML_object_type` covers false, true, null, number, string, array, and object nodes.
- `struct cYAML` stores sibling links, child pointer, type, string value, integer/double numeric values, key string, and optional user data.
- `cYAML_user_data_free_cb` and `cYAML_walk_cb` define cleanup and tree-walk callbacks.
- Parse/build APIs: `cYAML_load()` and `cYAML_build_tree()`.
- Output APIs: `cYAML_print_tree()`, `cYAML_print_tree2file()`, and `cYAML_dump()`.
- Lifetime APIs: `cYAML_free_tree()` and `cYAML_clean_usr_data()`.
- Lookup/iteration APIs: `cYAML_get_object_item()`, `cYAML_get_object_child()`, `cYAML_get_next_seq_item()`, `cYAML_is_sequence()`, and `cYAML_find_object()`.
- Creation/insertion APIs: `cYAML_create_object()`, `cYAML_create_seq()`, `cYAML_create_seq_item()`, `cYAML_create_string()`, `cYAML_create_number()`, `cYAML_insert_sibling()`, and `cYAML_insert_child()`.
- `cYAML_build_error()` appends standard YAML error data.

## Control Flow
Callers parse YAML into a tree, inspect or mutate nodes through child/sibling links and helper functions, optionally build output trees programmatically, dump/print YAML, then clean user data and free the tree. Sequence iteration uses an external cursor pointer supplied by the caller.

## State And Persistence Behavior
The API is heap-tree based. The caller owns returned trees and dump buffers. User data is opaque and must be freed by caller-provided callbacks if used. No global persistent state is exposed.

## Dependencies And Integration Points
The header requires stdio types for `FILE`, stdint for numeric values, and bool. It is included by `cyaml.c` and user-space lnetconfig sources.

## Risks And Edge Cases
The API exposes raw mutable tree links, so callers can corrupt sibling/child invariants. Function comments contain minor copy/paste inaccuracies, such as repeated `cYAML_create_string` descriptions. Sequence iteration assumes a valid array node and cursor discipline. Constructors accept mutable `char *` keys/values but duplicate them in the implementation.

## Test Signals
Compile tests should cover inclusion from C files needing `FILE`; runtime tests should cover parse/free, constructor insertion order, recursive/direct lookup differences, sequence cursor reset, dump ownership, and user-data cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.h -->
