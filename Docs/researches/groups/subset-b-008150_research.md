# subset-b-008150 research

Grouped research for the DAOS engine Argobots/dRPC tests, engine ULT utilities, and pool client/RPC protocol files. Each section is source-tree aligned for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/abt_perf.c -->
# sources/object-store/daos/src/engine/tests/abt_perf.c

Purpose: standalone Argobots microbenchmark for DAOS developers. It measures ULT creation rate, ULT scheduling/yield rate, and creation/free rates for ABT mutexes, rwlocks, condition variables, and eventuals.

Important APIs and functions: `main()` parses `-t`, `-n`, `-s`, and `-S`, initializes DAOS logging and Argobots, obtains the current xstream main pool, and dispatches by test id. `abt_ult_create_rate()` keeps at most `opt_concur` ULTs in flight and measures recursive ULT creation through `abt_thread_1()`. `abt_sched_rate()` creates `opt_concur` workers using `abt_thread_2()` and counts lock/yield cycles. `abt_lock_create_rate()` repeatedly creates and frees the ABT synchronization primitive selected by `opt_cr_type`. `abt_current_ms()` wraps `CLOCK_MONOTONIC`.

Control flow: setup creates one global ABT pool, condition, mutex, and optional thread attribute with a stack size in KiB. Creation tests drive a loop until `opt_secs` elapses, then wait for outstanding ULTs to drain. Scheduling tests start all ULTs before timing. Primitive creation tests run one worker ULT and wait on `abt_cond` for completion.

State and persistence: all state is process-local globals: counters, concurrency, `abt_exiting`, `abt_waiting`, ABT handles, and selected options. There is no persisted state. The synchronization contract depends on `abt_lock` protecting `abt_cntr`, `abt_ults`, and exit/wait flags.

Dependencies and integration: depends on Argobots, DAOS/GURT logging, and `daos_srv/daos_engine.h` for error formatting. It is a test executable rather than library code.

Risks: `opt_secs` is required for creation/scheduling but not explicitly validated for primitive creation paths, so a zero duration can reach division by zero. Some paths use `assert()` rather than DAOS error unwinding. Recursive ULT creation can stress scheduler and stack behavior by design. Timing is coarse millisecond wall-clock and suitable for relative perf checks, not exact benchmarking.

Test signals: the file is itself a manual/perf test. Useful signals are successful ABT init/finalize, no deadlock in the wait/broadcast loop, printed per-second creation progress, and final rates for selected test ids `c`, `s`, `m`, `w`, `e`, and `d`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/abt_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/abt_stack.c -->
# sources/object-store/daos/src/engine/tests/abt_stack.c

Purpose: standalone Argobots stack stress test. It creates one ULT with optional stack size and repeatedly allocates on that ULT stack until SIGSEGV, then reports apparent stack consumption.

Important APIs and functions: `main()` parses `--on-pool`, `--unnamed-thread`, `--check-overflow`, `--stack-size`, and `--var-size`, initializes DAOS logging and ABT, registers an alternate signal stack, and creates the test ULT either on the last pool or current xstream. `stack_fill()` records ABT-reported stack size and repeatedly calls `alloca(var_size)`. `handler_segv()` prints SIGSEGV details and exits success or failure depending on `g_check_overflow`. `signal_register()` configures `sigaltstack()` and `sigaction()`.

Control flow: after creating the ULT, `main()` yields once and expects `stack_fill()` to run until a signal terminates the process. The final `D_ASSERT(false)` should be unreachable. The signal path intentionally handles stack overflow on an alternate signal stack.

State and persistence: process-local globals record stack size, accumulated allocation, stack start/end addresses, and overflow-check mode. No persistent storage is used.

Dependencies and integration: depends on Argobots stack-introspection APIs, POSIX signals, `alloca`, and DAOS/GURT assertion/logging helpers. It is a destructive/manual test process intended to crash into the SIGSEGV handler.

Risks: `create_on_pool` is not initialized before option parsing, so omitting `-p` can leave undefined branch selection. Pointer subtraction uses `void *` arithmetic as a compiler extension. The test intentionally overflows stack and should not be run as part of generic unit tests without isolation.

Test signals: success is the handler printing stack allocation details and exiting. With `--check-overflow`, exceeding the ABT-reported stack size exits failure, allowing scripts to detect guard behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/abt_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_client_tests.c -->
# sources/object-store/daos/src/engine/tests/drpc_client_tests.c

Purpose: cmocka unit tests for engine-to-agent dRPC client helpers. The tests validate dRPC call failure handling and the protobuf payloads sent by readiness, pool service update, and RAS cluster-event notifications.

Important APIs and functions: test mocks provide `crt_self_uri_get()`, `crt_self_incarnation_get()`, `crt_group_rank()`, `get_module_info()`, and scheduler stubs expected by engine notification code. `drpc_client_test_setup()` initializes socket syscall mocks and `drpc_init()`. `unpack_sendmsg_drpc_call()` decodes the mocked `sendmsg` buffer after the dRPC header. Verification helpers inspect `Srv__NotifyReadyReq` and `Shared__ClusterEventReq` protobuf messages. Tests call `dss_drpc_call()`, `drpc_notify_ready()`, `ds_notify_pool_svc_update()`, and `ds_notify_ras_event()`.

Control flow: each test sets mock syscall return values or a valid dRPC response, invokes a notification helper, and inspects return codes, close counts, send counts, and unpacked protobuf fields. Negative tests force chmod/connect/send failures and invalid pool service update arguments.

State and persistence: all state is mock global state: fake socket paths, hostname, dss xstream counts, mock CART URI/incarnation/rank, and captured socket buffers. No durable state is modified.

Dependencies and integration: includes `drpc_internal.h`, generated `srv.pb-c.h` and `event.pb-c.h`, dRPC module IDs, DAOS test mocks, and engine globals. It verifies the protocol contract between DAOS engine notification code and the control-plane agent over a Unix-domain dRPC socket.

Risks: because the test decodes the raw `sendmsg` mock buffer, it is sensitive to dRPC framing changes. The mocked `get_module_info()` allocates one module-info object and relies on teardown freeing it. The tests cover successful packing and selected syscall errors, but not malformed dRPC responses or retry timing.

Test signals: suite name `engine_drpc_client`; expected coverage includes socket close on failures, no send for invalid pool service update or empty RAS messages, correct readiness fields (`uri`, `nctxs`, listener socket, instance index, target count), and correct cluster-event metadata/defaults.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_client_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_comm_tests.c -->
# sources/object-store/daos/src/engine/tests/drpc_comm_tests.c

Purpose: cmocka integration tests for the user-facing dRPC communication stack using a simplified in-process test listener. It verifies basic, large single-chunk, and chunked request/response traffic.

Important APIs and functions: `run_hello_test()` connects with `drpc_connect()`, creates a call with `drpc_call_create()`, packs a `Hello__Hello` protobuf body, issues `drpc_call(ctx, R_SYNC, ...)`, unpacks `Hello__HelloResponse`, and compares it with `get_greeting()`. `gen_str()` creates deterministic long names. `DRPC_COMM_TEST` runs each test with `drpc_listener_setup()` and `drpc_listener_teardown()`.

Control flow: each test starts a temporary listener, connects a client to its socket, sends a greeting request, validates `DRPC__STATUS__SUCCESS`, verifies response payload, frees protobuf/dRPC resources, and closes the client context. The long tests size inputs around `UNIXCOMM_MAXMSGSIZE` to exercise chunk boundaries.

State and persistence: per-test state is `struct drpc_test_state` owned by the listener helper. Temporary socket directory and socket path are created under `/tmp` and removed during teardown.

Dependencies and integration: depends on public dRPC APIs, generated `drpc_test.pb-c.h`, `drpc_test_listener.[ch]`, and DAOS test logging. It validates end-to-end framing, chunking, protobuf body preservation, and synchronous call behavior.

Risks: tests rely on `/tmp`, pthread scheduling, and local Unix sockets, so they are more integration-like than pure unit tests. `gen_str()` assumes `len > 0`. The listener helper assumes a simple single-threaded client model.

Test signals: suite name `drpc_comms`; important signals are success for normal name, name of size `CHUNK_SIZE / 2`, and name of size `CHUNK_SIZE`, with successful cleanup of call, response, dRPC context, socket, and directory.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_comm_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_handler_tests.c -->
# sources/object-store/daos/src/engine/tests/drpc_handler_tests.c

Purpose: cmocka unit tests for the dRPC handler registry and message dispatch layer.

Important APIs and functions: helper `create_handler_list()` builds null-terminated arrays of `struct dss_drpc_handler`; dummy handlers provide distinct function pointers. Tests exercise `drpc_hdlr_init()`, `drpc_hdlr_fini()`, `drpc_hdlr_register()`, `drpc_hdlr_unregister()`, `drpc_hdlr_register_all()`, `drpc_hdlr_unregister_all()`, `drpc_hdlr_get_handler()`, and `drpc_hdlr_process_msg()`.

Control flow: setup initializes the registry and dRPC handler mocks for most tests. Registration tests validate bad input, duplicate module IDs, invalid module IDs, multiple handlers, and unchanged registry entries after failed operations. Dispatch tests create a `Drpc__Call` and `Drpc__Response`, register or omit a mock handler, and validate handler invocation or `DRPC__STATUS__UNKNOWN_MODULE`. Uninitialized tests intentionally skip setup.

State and persistence: registry state is process-local and reset by setup/teardown. Handler arrays are heap allocated only inside helper tests and freed before return.

Dependencies and integration: uses generated `drpc.pb-c.h`, dRPC module IDs, DAOS mocks, and `drpc_handler.h`. It defines the expected semantics for engine modules that register dRPC control handlers.

Risks: bulk registration with a duplicate expects earlier entries to remain registered, so callers must treat `-DER_EXIST` as partial failure. Tests do not cover concurrent registration or unregister during dispatch. The helper assumes module IDs start at zero for its generated lists.

Test signals: suite name `engine_drpc_handler`; strong signals include null handler rejection, duplicate protection, invalid ID rejection, idempotent unregister of missing IDs, all-list operations, successful dispatch copying mock response fields, unknown-module status, and `-DER_UNINIT` behavior before initialization.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_handler_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_listener_tests.c -->
# sources/object-store/daos/src/engine/tests/drpc_listener_tests.c

Purpose: cmocka unit tests for engine dRPC listener initialization and finalization.

Important APIs and functions: mocks capture `dss_ult_create()` parameters, `drpc_progress_context_create()` listener details, and `drpc_progress_context_close()` calls. Tests call `drpc_listener_init()` and `drpc_listener_fini()` while syscall and ABT mocks simulate socket, bind/listen, mutex, thread join/free, and unlink behavior.

Control flow: initialization tests validate socket creation failure, successful socket path construction (`dss_socket_dir/daos_engine_<pid>.sock`), unlink before listen, progress context creation with `drpc_hdlr_process_msg`, mutex creation, and listener ULT creation on target/xstream 0. Failure paths cover progress-context allocation, ABT mutex creation, and ULT creation cleanup. Finalization tests cover successful thread join/free/mutex free and each ABT failure mapping to DAOS errors.

State and persistence: the test owns mock globals and may allocate `drpc_listener_socket_path`; teardown frees leftover path and test progress context. No durable state is intended, but the real code path would create and unlink a Unix socket path.

Dependencies and integration: includes `drpc_internal.h`, DAOS test mocks, and ABT stubs. It verifies the integration boundary between listener socket setup, dRPC progress context, handler dispatch, and Argobots listener ULT lifecycle.

Risks: tests use stubs for `drpc_progress()` and handler lookup/dispatch, so they do not validate actual progress behavior. The captured `dss_ult_create_stream_id` stores the target argument, not the full ULT type, so the test focuses on target zero and stack/handle outputs. Cleanup must avoid double-freeing the listener pointer after failure.

Test signals: suite name `engine_drpc_listener`; expected signals are correct socket path/unlink/listen, non-null mutex and ULT handle pointer, context close on ULT creation failure, and precise DAOS return mapping for ABT join/free/mutex failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_listener_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_progress_tests.c -->
# sources/object-store/daos/src/engine/tests/drpc_progress_tests.c

Purpose: cmocka unit tests for the dRPC progress loop that polls listener/session fds, accepts sessions, receives calls, spawns handler ULTs, sends bad-call responses, and cleans up dead sessions.

Important APIs and functions: local helpers create `struct drpc_progress_context`, add session nodes, set mock `poll` revents, and assert session presence/removal. The mock `dss_ult_create()` captures scheduling parameters and frees call context ownership on successful spawn. Tests call `drpc_progress()`, `drpc_progress_context_create()`, and `drpc_progress_context_close()`.

Control flow: validation tests reject null context/listener/session/comm. Poll tests cover zero and negative timeouts, timeout return, poll failure, listener accept success/failure, bad message response, valid message dispatch to a system ULT, recv failure cleanup, `-EAGAIN` no-data propagation without close, session `POLLERR`/`POLLHUP` cleanup, ULT creation failure cleanup, and listener error/hangup failures. Context-close tests verify listener and session close counts.

State and persistence: in-memory dRPC contexts and intrusive lists are allocated/freed per test. Mock globals capture poll fds, recv/send buffers, close counts, accepted fds, and ULT arguments. There is no persistence.

Dependencies and integration: depends on dRPC internals, ABT type declarations, DAOS test mocks, and generated dRPC call/response helpers. It validates the engine listener loop's resource ownership rules and error classification.

Risks: the mock `dss_ult_create()` frees call context when spawn succeeds, so tests do not execute the real handler ULT body. Some errors are intentionally swallowed after per-session cleanup, so regressions can hide if only return codes are checked without close/list membership assertions. Poll fd ordering is part of expectations: sessions before listener.

Test signals: suite name `engine_drpc_progress`; key signals include correct poll timeout/fd setup, accepted session inserted, `-DER_TIMEDOUT` on poll timeout, `FAILED_UNMARSHAL_CALL` response for bad payloads, valid calls spawning `DSS_XS_SYS` ULTs with self-freeing handles, and deterministic cleanup behavior for recv, poll, hangup, and ULT failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_progress_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_test_listener.c -->
# sources/object-store/daos/src/engine/tests/drpc_test_listener.c

Purpose: simplified dRPC listener used by `drpc_comm_tests.c` to run integration-style communication tests without the full DAOS engine stack.

Important APIs and functions: `get_greeting()` formats `"Hello <name>"`. `hello_handler()` validates hello module/method, unpacks `Hello__Hello`, packs `Hello__HelloResponse`, and fills the dRPC response body. `drpc_listener_setup()` creates a temporary directory/socket path and starts the listener. `drpc_listener_teardown()` stops the pthread listener, closes dRPC progress context, removes socket and directory, and frees state. `dss_ult_create()` is stubbed to execute the function synchronously.

Control flow: setup creates `/tmp/drpc_test.XXXXXX`, starts `drpc_listen()` with `hello_handler`, wraps it in `drpc_progress_context_create()`, marks the listener running, and launches a pthread running `run_test_listener()`. The thread loops on `drpc_progress(..., 500)` until `listener_running` is cleared, ignoring `-DER_TIMEDOUT`. Teardown clears the flag, joins the thread, closes dRPC state, and removes filesystem artifacts.

State and persistence: `struct drpc_test_state` owns the progress context, temp directory, socket path, pthread, mutex, and running flag. Filesystem state is temporary under `/tmp` and removed on teardown. Synchronization uses a pthread mutex around the running flag.

Dependencies and integration: depends on pthreads, Argobots type compatibility, dRPC internals, DAOS test logging, and generated hello protobuf code. It bridges public dRPC client calls to real `drpc_progress()` behavior in tests.

Risks: the synchronous `dss_ult_create()` stub collapses production ULT concurrency into direct calls, so it cannot expose scheduling races. `pthread_create()` is checked with `< 0`, but POSIX returns nonzero positive error codes, so failure detection is incomplete. Teardown assumes setup reached a valid listener state.

Test signals: used by `drpc_comm_tests.c`; signals are successful temporary directory/socket creation, listener thread progress, correct hello response packing, clean stop/join, and removal of socket and temp directory.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_test_listener.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_test_listener.h -->
# sources/object-store/daos/src/engine/tests/drpc_test_listener.h

Purpose: header declaring the simplified dRPC test listener contract shared by `drpc_comm_tests.c` and `drpc_test_listener.c`.

Important APIs and types: `struct drpc_test_state` holds `struct drpc_progress_context *progress_ctx`, temporary directory and socket path strings, a listener pthread, a mutex, and a boolean running flag. Public helper declarations are `get_greeting()`, `drpc_listener_setup()`, and `drpc_listener_teardown()`.

Control flow: cmocka tests use the setup/teardown functions as per-test fixtures. The state struct carries the socket path used by the dRPC client and the listener thread/progress context used by teardown.

State and persistence: defines ownership fields but does not allocate itself. The implementation owns lifecycle and temporary `/tmp` artifacts.

Dependencies and integration: includes pthread and `drpc_internal.h` for progress context definitions. Integrated directly by dRPC communication tests.

Risks: the header exposes internal listener state to tests, so tests can depend on implementation details. It includes dRPC internals rather than a narrow public forward declaration.

Test signals: compile-time signal is that the shared fixture shape matches the implementation and communication tests; runtime signals come from the `.c` implementation.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/drpc_test_listener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/mock_abt.c -->
# sources/object-store/daos/src/engine/tests/mock_abt.c

Purpose: tiny Argobots mock object for tests that need `ABT_thread_yield()` at link time but do not need real Argobots scheduling.

Important APIs and functions: exports `int ABT_thread_yield(void)` returning `0`.

Control flow: no internal control flow beyond immediate success.

State and persistence: stateless and non-persistent.

Dependencies and integration: used by unit-test link targets where production code references Argobots yield but the test uses mocks/stubs. It avoids bringing in full ABT behavior.

Risks: tests linked against this mock cannot validate yield scheduling, fairness, or ABT error handling. It should only be used where yield side effects are irrelevant.

Test signals: successful link and tests that do not require real ABT progression.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/tests/mock_abt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/ult.c -->
# sources/object-store/daos/src/engine/ult.c

Purpose: DAOS server Argobots utility layer for collective execution across server xstreams, targeted ULT/task creation, offload execution, chore queues, and deep-stack wrappers for VOS pool create/open.

Important APIs and functions: collective APIs include `dss_task_collective_reduce()`, `dss_thread_collective_reduce()`, `dss_task_collective()`, `dss_thread_collective()`, and `dss_build_coll_bitmap()`. Scheduling helpers include `sched_ult2xs_multisocket()`, `sched_ult2xs()`, `ult_create_internal()`, `dss_ult_create()`, `dss_ult_periodic()`, `dss_ult_execute()`, `dss_ult_create_all()`, `dss_offload_exec()`, and `dss_main_exec()`. Chore APIs include `dss_chore_register()`, `dss_chore_deregister()`, `dss_chore_diy()`, `dss_chore_queue_init()`, `dss_chore_queue_start()`, `dss_chore_queue_stop()`, and `dss_chore_queue_fini()`. VOS wrappers are `dss_vos_pool_create()` and `dss_vos_pool_open()`.

Control flow: collectives allocate one stream argument per target, create an ABT future with an extra aggregator slot, optionally allocate per-stream reduce arguments, schedule tasklets or ULTs on each target xstream, set skipped or failed streams into the future, wait, reduce failures and custom aggregate data, then free future/stream state. ULT creation maps an xstream type and target id to an actual xstream, optionally creates stack attributes, and calls scheduler creation APIs. `dss_ult_execute()` wraps a function in a future for synchronous calls or invokes a user callback for asynchronous calls. Chore queues enqueue work on helper xstreams with credit accounting; without helper xstreams, each chore gets its own I/O-forwarding ULT.

State and persistence: uses global DAOS engine topology (`dss_tgt_nr`, `dss_sys_xs_nr`, `dss_tgt_offload_xs_nr`, NUMA sizing, helper pool flags) and global `dss_chore_credits`. Per-queue state lives in `struct dss_chore_queue` inside xstreams: list, mutex, condition, stop flag, credits, and ULT. State is runtime-only.

Dependencies and integration: depends on Argobots futures, mutexes, conditions, thread attributes, DAOS scheduler functions (`sched_create_thread`, `sched_create_task`, `sched_cond_wait_for_business`), xstream lookup, VOS pool APIs, and DAOS error conversion. It is a central integration point for server modules that need cross-xstream fan-out, offload, I/O forwarding, or deep stacks.

Risks: collective code must set every future slot exactly once, including skipped targets and schedule failures, or wait can hang. Async `dss_ult_execute()` requires non-null callbacks and frees state in the spawned ULT. Xstream selection depends on global topology and asserts heavily; bad topology can abort rather than return an error. Chore callbacks may free their own chore when returning `DSS_CHORE_DONE`, so queue code must not touch it afterward. Credit underflow is allowed temporarily for priority chores and needs careful accounting. Deep-stack wrappers pass stack-local argument structs but wait synchronously, which is safe only because `dss_ult_execute()` blocks in synchronous mode.

Test signals: direct tests are not in this subset, but dRPC listener/progress tests mock `dss_ult_create()` contracts. Runtime signals include successful collectives returning failure counts or first error, no future deadlocks, chore queues starting/stopping cleanly, correct `-DER_CANCELED` when no xstreams/shutdown, and VOS create/open avoiding stack overflow via `DSS_DEEP_STACK_SZ`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/ult.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/util.c -->
# sources/object-store/daos/src/engine/util.c

Purpose: server utility file currently providing registration of native DAOS dbtree classes used by server modules.

Important APIs and functions: `dss_register_dbtree_classes()` registers `DBTREE_CLASS_KV`, `DBTREE_CLASS_IV`, `DBTREE_CLASS_IFV`, `DBTREE_CLASS_NV`, `DBTREE_CLASS_UV`, and `DBTREE_CLASS_EC` with their operation tables and feature flags.

Control flow: registration is sequential. On the first `dbtree_class_register()` failure, it logs the class-specific failure and returns the error. There is no rollback for classes already registered.

State and persistence: modifies process-global dbtree class registry state. The comment explicitly notes unregistering is currently unsupported. There is no file persistence.

Dependencies and integration: depends on DAOS btree class APIs and operation tables (`dbtree_kv_ops`, `dbtree_iv_ops`, `dbtree_ifv_ops`, `dbtree_nv_ops`, `dbtree_uv_ops`, `dbtree_ec_ops`). Included headers also tie the file to server internals, dRPC internals, placement, TLS, and telemetry, though this function only uses dbtree registration and logging.

Risks: partial registration can remain after a later class fails because no unregister path exists. Repeated calls may depend on dbtree registry semantics for duplicate registration. The broad include set can hide unnecessary coupling and rebuild impact.

Test signals: startup or module-init tests should expect all classes registered once and clear error logs identifying the failed class if registration fails.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/cli.c -->
# sources/object-store/daos/src/pool/cli.c

Purpose: libdaos client-side implementation of DAOS pool APIs. It manages client pool handles, pool map and placement updates, replicated-service endpoint selection, connect/disconnect, query/map refresh, target updates, container listing/filtering, target queries, pool attributes, service stop, metrics, and local/global handle conversion.

Important APIs and functions: lifecycle and handle helpers include `dc_pool_init()`, `dc_pool_fini()`, `dc_pool_alloc()`, `dc_hdl2pool()`, `dc_pool_hdl_link()`, `dc_pool_hdl_unlink()`, `dc_pool_get()`, and `dc_pool_put()`. Connection APIs include `dc_pool_connect()`, `dc_pool_disconnect()`, `dc_pool_local2global()`, `dc_pool_global2local()`, and `dc_pool_hdl2uuid()`. Map/rsvc helpers include `dc_pool_choose_svc_rank()`, `dc_pool_map_update()`, `process_query_reply()`, `pool_rsvc_client_complete_rpc()`, `dc_pool_query()`, `dc_pool_create_map_refresh_task()`, and `dc_pool_abandon_map_refresh_task()`. Administration/data APIs include `dc_pool_exclude()`, `dc_pool_reint()`, `dc_pool_drain()`, `dc_pool_exclude_out()`, `dc_pool_list_cont()`, `dc_pool_filter_cont()`, `dc_pool_map_version_get()`, `dc_pool_query_target()`, `dc_pool_list_attr()`, `dc_pool_get_attr()`, `dc_pool_set_attr()`, `dc_pool_del_attr()`, `dc_pool_stop_svc()`, `dc_pool_get_redunc()`, `dc_pool_tgt_idx2ptr()`, and `dc_pool_mark_all_slave()`.

Control flow: most public task functions follow the same asynchronous pattern: validate task args, create or reuse `pool_task_priv`, look up or initialize `struct dc_pool`, choose an rsvc endpoint, create a CRT RPC with `dc_pool_req_create()`, fill request-specific fields and bulk handles, add an RPC reference for the completion callback, register a completion callback, and send with `daos_rpc_send()`. Completion callbacks pass CRT and service return codes through `pool_rsvc_client_complete_rpc()` or `rsvc_client_complete_rpc()`, reinitialize tasks with backoff on replica/retry conditions, process replies, clean bulk/RPC/pool/task-private resources, and complete or reschedule.

State and persistence: `struct dc_pool` is reference-counted through the DAOS handle hash and stores pool UUID, pool handle UUID, capabilities, management system attachment, rsvc client, pool map, known map version, pool map size, container list, map/client/container locks, metrics pointer, redundancy-factor cache, disconnect/slave flags, and active map-refresh task. `struct pool_task_priv` stores retry backoff and request HLC time. TLS state tracks per-thread pool metrics under `dc_pool_module_key`. Global state includes `dc_pool_proto_version` and `warmup_lock`. Persistent server state is changed indirectly by RPCs; local client state is in memory only.

Dependencies and integration: integrates DAOS task scheduler, CART/CRT RPC, rsvc client, management system attach/find, security credential acquisition, pool map and placement map APIs, telemetry, DAOS metrics, security, bulk transfer, HLC/client UUID, and pool RPC definitions from `rpc.h`. Agent integration occurs through `dc_mgmt_notify_pool_connect()` and disconnect notification. Optional warmup pings targets with `POOL_TGT_WARMUP`.

Risks: resource ownership is complex; each path must balance pool refs, RPC refs, bulk handles, task-private state, credentials, and management-system/rsvc-client lifecycles across normal and reinit paths. `process_query_reply()` assumes property replies are present when caching redundancy factor, so callers must pass compatible property data. Map refresh relies on a single active task plus passive dependency tasks; stale `dp_map_task` handling can block refreshes if unregister is missed. The local/global buffer format has explicit endian swapping for the fixed header/pool map but embeds encoded rsvc and management-system data after it. Attribute operations duplicate names/values because memory registration can fault on caller storage; callback cleanup order is important. `warmup()` is serialized by a global mutex and can add connection startup cost when `D_POOL_WARMUP` is enabled.

Test signals: expected signals include protocol registration against v6/v7, successful connect updating map and linking handle, disconnect rejecting open containers and unlinking handle, retries on `-DER_TRUNC` and rsvc rechoose, map refresh falling back to `dc_pool_query()` after serious target-query failures, correct bulk cleanup for list/filter/attr paths, and telemetry metrics refcounts returning to zero at TLS teardown.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/cli_internal.h -->
# sources/object-store/daos/src/pool/cli_internal.h

Purpose: internal declarations for the pool client implementation shared across pool client compilation units.

Important APIs and types: declares `dc_pool_hdl_link()`, `dc_pool_hdl_unlink()`, `dc_pool_alloc()`, and `dc_pool_map_update()`. Defines `struct dc_pool_tls` with a mutex and list for per-thread pool metrics. Declares `dc_pool_module_key` and inline `dc_pool_tls_get()` to retrieve pool TLS via DAOS module-key TLS.

Control flow: `dc_pool_tls_get()` obtains DAOS thread-local storage for the module key tags, asserts it exists, and returns the module-specific data pointer.

State and persistence: defines TLS structure only; runtime ownership is in `cli.c` initialization/finalization callbacks. No persistence.

Dependencies and integration: depends on `struct dc_pool`, `struct pool_map`, DAOS TLS, DAOS module key, pthread mutexes, and DAOS intrusive lists. It is tightly coupled to `cli.c` metrics and map update internals.

Risks: `dc_pool_tls_get()` asserts on missing TLS rather than returning NULL, so callers must only use it after module/TLS registration. The header exposes internal handle and map update functions, so misuse outside intended pool client internals could bypass lifecycle rules.

Test signals: compile-time signal is that pool client files share the same internal prototypes; runtime metrics tests should show valid TLS after `dc_pool_init()` when client metrics are enabled.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/cli_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/rpc.c -->
# sources/object-store/daos/src/pool/rpc.c

Purpose: implementation of pool RPC protocol serialization formats and common pool RPC helper routines shared by client and server pool code.

Important APIs and functions: `dc_pool_op_str()` maps pool operation enums to strings. Custom CRT processors serialize `struct pool_target_addr`, `struct rsvc_hint`, and `daos_pool_cont_filter_t` parts. `CRT_RPC_DEFINE()` instantiates all pool RPC formats. `pool_proto_fmt_v6` and `pool_proto_fmt_v7` expose protocol format tables. Helper functions include `pool_query_bits()`, `pool_query_reply_to_info()`, `list_cont_bulk_create()`, `list_cont_bulk_destroy()`, `map_bulk_create()`, and `map_bulk_destroy()`.

Control flow: RPC format arrays are generated from `POOL_PROTO_CLI_RPC_LIST()` and `POOL_PROTO_SRV_RPC_LIST()` macros. Filter serialization allocates nested filter-part arrays while decoding and frees partial allocations on failure or during FREEING. `pool_query_bits()` maps requested `daos_pool_info_t` bits and property entries into server query-bit flags. Bulk helpers allocate/register pool map or container buffers with CRT and clean both CRT bulk and local buffers.

State and persistence: global protocol descriptors are static/global process state. Bulk helper allocations are per call. No durable state is changed directly.

Dependencies and integration: depends on DAOS RPC/CART, pool map buffers, property definitions, rsvc hints, and `rpc.h` macro declarations. It is the serialization backbone for `cli.c` and server pool handlers.

Risks: protocol list ordering must remain consistent with `enum pool_operation` and registered handler arrays. `pool_query_bits()` intentionally falls through from `DAOS_PROP_PO_REDUN_FAC` to include `DAOS_PROP_PO_EC_PDA`; this must be deliberate or documented because it broadens queries. Filter-part decode must free nested allocations on all failures to avoid leaks. `map_bulk_destroy()` assumes a valid bulk handle, unlike `list_cont_bulk_destroy()` which tolerates `CRT_BULK_NULL`.

Test signals: protocol registration should succeed for v6/v7, op string mapping should return enum names, query-bit tests should verify every property flag, and serialization tests should cover filter decoding/freeing and bulk helper cleanup on CRT failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/rpc.h -->
# sources/object-store/daos/src/pool/rpc.h

Purpose: canonical pool RPC protocol definition shared by DAOS pool client and server. It declares operation codes, protocol version behavior, request/reply field sequences, generated RPC types, inline field accessors, and request creation helpers.

Important APIs and types: `POOL_PROTO_CLI_RPC_LIST(ver)` and `POOL_PROTO_SRV_RPC_LIST(ver)` define all client-facing and server/internal pool RPCs and their handlers. `enum pool_operation` derives from those lists. Core field sequences include `DAOS_ISEQ_POOL_OP`/`DAOS_OSEQ_POOL_OP`, create/connect/disconnect/query/query-info, target update/extend/evict/service stop/target disconnect/query, properties, ACLs, list/filter containers, ranks, upgrade, target-query-map, rebuild, self-heal, and recovery-container RPCs. Inline accessors pack/unpack fields such as connect credentials/bulk/version, query bulk/bits, target update arrays, attributes, properties, ACLs, list/filter containers, and request creation.

Control flow: macro lists feed both enum generation and `rpc.c` format arrays, so adding an RPC in one list updates opcode ordering and registration. `pool_req_create_common()` encodes an opcode with module/protocol version, maps endpoint tag through `daos_rpc_tag()`, creates the CRT request, fills UUIDs, optionally assigns client UUID and HLC request time, and returns the request. `dc_pool_req_create()` uses negotiated `dc_pool_proto_version`; `ds_pool_req_create()` obtains the server protocol from `ds_pool_rpc_protocol()`.

State and persistence: declares external `pool_proto_fmt_v6`, `pool_proto_fmt_v7`, and `dc_pool_proto_version`. The header itself defines protocol shape, not runtime storage. Request helpers mutate CRT request input structs and may initialize caller-provided request time.

Dependencies and integration: depends on DAOS RPC macros, rsvc hints, pool maps, pool properties, UUIDs, CRT contexts/endpoints, and server handler symbols referenced by macro lists. It is included by client `cli.c`, protocol implementation `rpc.c`, and server pool handlers.

Risks: any field change requires a DAOS pool protocol version bump and v6/v7 compatibility handling. The RPC input/output structures must avoid compiler-generated padding by construction. Inline accessors assert protocol version `POOL_PROTO_VER_WITH_SVC_OP_KEY` for many client RPCs, so older versions are unsupported on those paths. Macro ordering changes are ABI/protocol-sensitive. `pool_req_create_common()` overwrites endpoint tag with DAOS pool request tag mapping, so callers must pass logical tag values.

Test signals: build-time generation of all `CRT_RPC_DECLARE` types is the first signal. Runtime signals include client protocol negotiation selecting v6 or v7, all `*_in_set_data()`/`*_in_get_data()` round-tripping fields, request creation filling pool UUID/handle/client/time correctly, and server/client format arrays matching `POOL_PROTO_CLI_COUNT` and protocol versions.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/rpc.h -->
