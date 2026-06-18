# Research: subset-b-009700

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_top.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_top.c

## Purpose
This file implements the top-level FSAL upcall vector used by NFS-Ganesha when a backend FSAL needs to notify the core server about lock availability, pNFS layout/device changes, delegation conflicts, and write-delegation attribute refreshes. It is the bridge from FSAL object handles and backend event keys into NFSv4 state, callback RPCs, delayed retry execution, and export/client lifetime management.

## Important APIs, Types, And Functions
- `struct fsal_up_vector fsal_up_top` is the exported template vector. FSAL exports copy it, set `up_fsal_export`/`up_gsh_export`, and optionally override operations.
- `lock_grant()` and `lock_avail()` rebuild an object handle from an FSAL handle and forward lock wakeups to `grant_blocked_lock_upcall()` or `available_blocked_lock_upcall()`.
- `layoutrecall()` validates a pNFS recall request, builds a `state_layout_recall_file`, sends per-client `CB_LAYOUTRECALL`, and uses `layoutrec_completion()` to retry or revoke/return layouts.
- `notify_device()` sends `CB_NOTIFY_DEVICEID` to all NFSv4.1 clients through `nfs41_foreach_client_callback()`.
- `delegrecall()`, `delegrecall_impl()`, `delegrecall_impl_per_state()`, `delegrecall_one()`, `delegrecall_completion_func()`, and `delegrevoke_check()` implement delegation recall, callback retry, and lease-time-based revocation.
- `cbgetattr_impl()`, `send_cbgetattr()`, `cbgetattr_completion_func()`, and `handle_getattr_response()` query a write-delegation holder for `CHANGE`/`SIZE` and update cached attributes through the upcall `update` method.
- `up_ready_init()`, `up_ready_set()`, `up_ready_cancel()`, and `up_ready_wait()` provide readiness synchronization for upcall-capable modules.

## Control Flow
For layout recall, `layoutrecall()` converts the FSAL handle to an object, locks the state list, and calls `create_file_recall()` to collect matching layout states by layout type, client selector, and overlapping `pnfs_segment`. It then builds callback arguments, converts the object to an NFS file handle, updates each layout stateid under lock, and submits `layoutrecall_one_call()` to the delayed executor. `layoutrecall_one_call()` looks the state back up, installs an operation context, and calls `nfs_rpc_cb_single()`. `layoutrec_completion()` treats `NFS4_OK` as accepted, retries `NFS4ERR_DELAY` with plateau backoff until the lease lifetime expires, handles `NFS4ERR_NOMATCHING_LAYOUT` as a client-side return, and otherwise invokes `nfs4_return_one_state()` with a revoke circumstance.

For delegation recall, `delegrecall()` converts the FSAL handle and `delegrecall_impl()` scans all object states under `STATELOCK`. Per delegation, `delegrecall_impl_per_state()` changes `DELEG_GRANTED` to `DELEG_RECALL_WIP`, captures export/client references, skips same-client lock-conflict cases via `lock_clientid_hint`, reserves the client lease when possible, and sends `CB_RECALL`. Callback completion marks the backchannel down on transport errors, calls `handle_recall_response()`, schedules another recall or a revoke check, or revokes immediately. `eval_deleg_revoke()` decides revocation after one lease following a successful recall send or two leases after first recall attempt.

For `CB_GETATTR`, the caller enters `cbgetattr_impl()` with an object, client, and export. The function transitions the per-file `cbgetattr.state` from `NONE` to `WIP`, reserves the client lease, sends `CB_GETATTR`, then completion updates `cbgetattr.modified`, synthetic change, and size if the client reports changed attributes. It pushes the updated attributes back through `event_func->update()`.

## State And Persistence Behavior
State is primarily in memory: object state lists, layout segment lists, delegation state fields, client reference counts, lease reservations, callback-channel health, and per-file `cbgetattr` attributes. The file does not directly persist to disk; durable effects are mediated through state-layer revocation/return calls and FSAL update hooks. Delayed tasks retain references to client/export/object state through context structs and must release those references on every completion/retry path.

## Dependencies And Integration Points
This code integrates with FSAL export handle creation, SAL/NFSv4 state (`state_t`, state owners, `STATELOCK`), pNFS helpers, NFS callback RPC (`nfs_rpc_cb_single`, `nfs41_release_single`), delayed execution, export lifetime management, server statistics, and MDCACHE-style update/invalidate overrides. It assumes callback operation contexts are set before calling state and FSAL paths that consult `op_ctx`.

## Risks
- `create_file_recall()` contains a suspicious segment validation condition: it rejects when `segment->offset <= UINT64_MAX - segment->length`, which appears inverted for overflow checking and may reject valid ranges.
- Layout recall comments explicitly note possible reference leaks and incomplete revocation infrastructure.
- Callback retry and revoke paths are race-prone because states can disappear between scheduling and delayed execution.
- `notify_device()` allocates `cb_data` but does not free it after `nfs41_foreach_client_callback()`, which should be reviewed.
- `invalidate()`, `invalidate_close()`, and `update()` are no-ops in the top vector, so correctness depends on cached FSALs overriding them where needed.

## Test Signals
Useful signals are delegation conflict tests with callback success, callback transport failure, expired client handling, and same-client lock-conflict suppression; pNFS layout recall tests for exact/complement client selectors, delay retry, `NFS4ERR_NOMATCHING_LAYOUT`, and revoke paths; `CB_GETATTR` tests for unchanged size/change, changed size, failed callback channel, and update hook failure; and stress tests that return/revoke state while delayed recall tasks are queued.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_dispatcher.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_dispatcher.c

## Purpose
This file implements the TCP-side 9P dispatcher and worker queue for Ganesha. It accepts 9P/TCP client connections, reads framed 9P messages, queues requests to a fridgethr worker pool, dispatches each request to the 9P interpreter, and tears down per-connection fid/flush/client state when the socket closes.

## Important APIs, Types, And Functions
- `_9p_worker_init()` initializes request queues, global waiter state, and a fixed-size `fridgethr` worker pool from `_9p_param.nb_worker`.
- `_9p_worker_shutdown()` stops the worker fridge and destroys producer/consumer queues.
- `DispatchWork9P()` is the common enqueue entry for TCP and RDMA 9P requests; it increments the connection refcount before queueing.
- `_9p_dequeue_req()`, `_9p_consume_req()`, and `_9p_enqueue_req()` implement producer/consumer list queues plus waiter signaling.
- `_9p_worker_run()` consumes queued requests, calls `_9p_execute()`, frees transport-owned request data, and increments health dequeue counters.
- `_9p_socket_thread()` owns one TCP connection: polling, message framing, request allocation, flush-hook registration, and connection cleanup.
- `_9p_dispatcher_thread()` owns the listening socket and spawns detached socket-manager threads.

## Control Flow
Startup calls `_9p_worker_init()` before `_9p_dispatcher_thread()`. The dispatcher creates an IPv6 listening socket, falling back to IPv4 if needed, then loops on `accept()`. Every accepted TCP socket gets a detached `_9p_socket_thread()`. The socket thread initializes `_9p_conn`, resolves peer/client state, polls for input, reads the 4-byte 9P size header with `MSG_WAITALL`, reads the rest of the frame, updates transport stats, allocates `_9p_request_data`, records a flush hook keyed by tag/sequence, and calls `DispatchWork9P()`.

Workers wait on a global wait list when all request queues are empty. Enqueue appends to the low-latency producer queue and signals one waiter. Dequeue splices producer into consumer under spinlocks to reduce contention, then returns one request. `_9p_execute()` installs a request operation context and dispatches to `_9p_tcp_process_request()` or `_9p_rdma_process_request()` depending on connection type. `_9p_free_reqdata()` frees TCP message storage and decrements the connection refcount.

## State And Persistence Behavior
All state is process-local: queue lists and sizes, waiter list, connection fids, flush buckets, per-connection `msize`, client references, health counters, and socket descriptors. The file does not persist data; the externally visible behavior is protocol servicing and cleanup on disconnect. Connection teardown waits for `refcount` to reach zero before cleaning fids and releasing the client record.

## Dependencies And Integration Points
This file depends on `9p_req_queue.h` for queue/wait primitives, `fridgethr` for worker management, the 9P protocol implementation for `_9p_tcp_process_request()`, client manager and server stats, RCU registration, and core health counters in `nfs_health_`. `nfs_init.c` starts and `nfs_admin_thread.c` stops the worker pool.

## Risks
- The dispatcher loop never checks global shutdown and the listening thread is not explicitly joined/cancelled here.
- TCP framing casts `_9pmsg` to `uint32_t *` and `u16 *`, so endian/alignment assumptions must match the 9P implementation.
- `_9p_socket_thread()` waits indefinitely for worker refcount drain during teardown; wedged workers can stall connection cleanup.
- `_9p_worker_run()` assigns `reqdata->_9prq_mutex` twice and initializes an unused condition variable, suggesting stale synchronization design.
- Queue size fields are protected by spinlocks but also read atomically elsewhere; consistency depends on the abstract atomic wrappers matching those fields.

## Test Signals
Exercise IPv6 listen and IPv4 fallback, oversized messages, short headers, mid-frame EOF, concurrent clients with many tags, flush hook cleanup, worker shutdown timeout, low-traffic health checks, and disconnect while requests are still executing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_dispatcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_callbacks.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_callbacks.c

## Purpose
This file contains Mooshika RDMA callbacks for 9P/RDMA sends, receives, errors, disconnects, and request execution. It adapts RDMA buffers into the shared 9P request queue used by `9p_dispatcher.c` and returns output buffers to a shared pool after sends complete or fail.

## Important APIs, Types, And Functions
- `_9p_rdma_callback_recv()` allocates `_9p_request_data`, attaches the received `msk_data_t`, records the 9P flush hook, dispatches work, and updates receive stats.
- `_9p_rdma_process_request()` runs in a 9P worker, takes an output RDMA buffer from the outqueue, validates the received frame, calls `_9p_process_buffer()`, reposts the receive buffer, and posts the send buffer.
- `_9p_rdma_callback_send()` and `_9p_rdma_callback_send_err()` return send buffers to the outqueue and update transport stats.
- `_9p_rdma_callback_recv_err()` reposts a receive buffer when the transport remains connected.
- `_9p_rdma_callback_disconnect()` delegates teardown to `_9p_rdma_cleanup_conn()`.

## Control Flow
Mooshika invokes `_9p_rdma_callback_recv()` when a receive completes. The callback increments `nfs_health_.enqueued_reqs`, allocates a request, extracts the 9P tag from the RDMA buffer, installs a flush hook, and enqueues through `DispatchWork9P()`. A worker later calls `_9p_rdma_process_request()`, waits for an available send buffer, treats `req9p->data->data` as the input 9P packet, validates the header size against `data->size`, processes the 9P request into the output buffer, reposts the input buffer, and posts the output send. Send callbacks recycle the output buffer.

## State And Persistence Behavior
State is transient RDMA transport state: Mooshika transport private data, per-connection `_9p_conn`, per-NIC memory registrations, output buffer queue, receive buffers, and request flush hooks. There is no durable persistence. Correctness depends on always returning buffers to either Mooshika receive posting or the outqueue.

## Dependencies And Integration Points
The file integrates Mooshika (`msk_post_recv`, `msk_post_send`), the shared 9P dispatcher (`DispatchWork9P`), the 9P interpreter (`_9p_process_buffer`), server transport stats, health counters, and RDMA setup/cleanup functions from `9p_rdma_dispatcher.c`.

## Risks
- `_9p_rdma_callback_recv()` reads the tag before validating `data->size`, so malformed short packets can lead to out-of-bounds reads.
- `_9p_rdma_process_request()` can block indefinitely waiting for an output buffer.
- Receive-error handling reposts only while `trans->state == MSK_CONNECTED`; disconnected buffers are left to transport cleanup.
- Send errors recycle buffers but do not retry, as noted by the local TODO.
- RDMA request data reuses `_9pmsg` differently from TCP; code paths that assume TCP-owned `_9pmsg` must gate on transport type.

## Test Signals
Use RDMA packet tests with valid frames, short frames, length mismatch, full output pool exhaustion, send failure, receive failure while connected, disconnect during queued work, and flush-hook lifecycle checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_callbacks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_dispatcher.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_dispatcher.c

## Purpose
This file starts and manages the 9P/RDMA listener using Mooshika. It creates global RDMA output pools, per-protection-domain input pools and memory registrations, accepts child transports, initializes `_9p_conn` state, and finalizes accepted connections.

## Important APIs, Types, And Functions
- `_9p_rdma_dispatcher_thread()` configures Mooshika server attributes, binds the RDMA listener, accepts child transports, and spawns `_9p_rdma_thread()` for each child.
- `_9p_rdma_thread()` replaces the accepted transport private data with `_9p_rdma_priv`, initializes a `_9p_conn`, records peer/client state, sets `msize`, and calls `msk_finalize_accept()`.
- `_9p_rdma_setup_global()` allocates shared output buffers, wraps them as linked `msk_data_t` nodes, and initializes `_9p_outqueue`.
- `_9p_rdma_setup_pernic()` registers output and input memory, allocates receive buffers, and posts initial receives.
- `_9p_rdma_cleanup_conn_thread()` waits for request refs to drain, releases client/fids/connection/private data, and destroys the transport.
- `_9p_rdma_cleanup_conn()` is intended to spawn detached cleanup.

## Control Flow
The dispatcher builds `msk_trans_attr_t` from `_9p_param` RDMA backlog, queue depths, port, and disconnect callback. After `msk_init()` and `msk_bind_server()`, it loops on `msk_accept_one()`. The first accepted child triggers global output-pool setup. Each child gets per-NIC setup, inherits the shared outqueue as initial private data, then a detached `_9p_rdma_thread()` finalizes the connection and installs `_9p_rdma_priv`.

Per-NIC setup registers the shared output buffer against the child transport protection domain, allocates and registers input memory, creates one `msk_data_t` per input slot, and posts receive callbacks. Connection cleanup is designed to run asynchronously after disconnect and wait for `_9p_conn.refcount` to reach zero before freeing fids and client state.

## State And Persistence Behavior
All state is in memory and bound to RDMA transports: registered memory regions, input/output pools, outqueue mutex/condvar, `_9p_conn` fids and flush buckets, client references, and transport private data. There is no persistent storage. Output memory is global to the dispatcher, while input memory is per protection domain.

## Dependencies And Integration Points
This file depends on Mooshika for transport lifecycle and memory registration, `9p_rdma_callbacks.c` for receive/send/disconnect callbacks, the shared 9P queue through callback dispatch, client manager, RCU, and `_9p_param` loaded during NFS config initialization.

## Risks
- `_9p_rdma_cleanup_conn()` currently returns immediately before `pthread_create()`, making the asynchronous cleanup path unreachable and likely leaking transports/private data on disconnect.
- `_9p_rdma_dispatcher_thread()` calls `iPTHREAD_ATTR_setdetachstate`, which appears to be a typo unless a macro exists elsewhere.
- `_9p_rdma_thread()` destroys flush-bucket mutexes on normal exit immediately after finalizing accept, while the connection remains active, which is dangerous if callbacks later use those locks.
- `memcpy(&p_9p_conn->addrpeer, addrpeer, MIN(sizeof(*addrpeer), sizeof(p_9p_conn->addrpeer)))` may copy only a generic `struct sockaddr` length, truncating IPv6 addresses.
- The dispatcher has an infinite loop with no shutdown path, matching a TODO in `nfs_init.c`.

## Test Signals
Build with `USE_9P_RDMA`, run compiler checks for the detach-state call, connect/disconnect RDMA clients under leak detection, verify receive posting and send buffer reuse, test IPv6 peer address handling, and stress disconnect while worker requests still hold connection refs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_dispatcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/CMakeLists.txt

## Purpose
This CMake file builds the MainNFSD object library and the shared `ganesha_nfsd` library. It selects core daemon sources, optional 9P/RDMA/QOS/callback simulator sources, FSAL core sources, object-library dependencies, link libraries, sanitizer settings, version-script flags, and install metadata.

## Important APIs, Types, And Functions
- `MainServices_STAT_SRCS` lists daemon service sources such as `nfs_admin_thread.c`, RPC dispatchers, `nfs_init.c`, `nfs_lib.c`, `nfs_metrics.c`, reaper, and client manager.
- `add_library(MainServices OBJECT ...)` compiles the service layer as PIC object files.
- `fsal_CORE_SRCS` brings common FSAL code plus `../FSAL_UP/fsal_up_top.c` and async upcall support into `ganesha_nfsd`.
- `ganesha_nfsd_OBJS` aggregates object libraries for config, logging, RPC, SAL, support, protocol, callbacks, pseudo FSAL, and MDCACHE.
- Conditional blocks add DBus, NLM, RQUOTA, NFSACL, 9P, localfs, ACL mapping, QOS, monitoring, LTTng, and RDMA support.

## Control Flow
CMake first defines compile flags and include directories for DBus/RADOS. It builds the `MainServices` object library from mandatory and feature-selected sources. It then defines FSAL core sources and builds `ganesha_nfsd` as a shared library from object libraries plus FSAL core C sources. Link settings include TIRPC, system libraries, LTTng, Mooshika, optional monitoring and trace symbols, and a Linux/FreeBSD version script. The resulting shared library is installed to `${LIB_INSTALL_DIR}`.

## State And Persistence Behavior
The file controls build artifacts rather than runtime state. Persistent effects are generated object files, shared libraries, sanitizer instrumentation, symbol visibility via version script, and install output. Feature flags determine which code can exist at runtime.

## Dependencies And Integration Points
It integrates MainNFSD sources with FSAL, SAL, NFS protocol, NFSv4 callbacks, MDCACHE, monitoring, DBus, Mooshika, nTIRPC, and LTTng build products. Its conditional source selection must stay aligned with `#ifdef` guards such as `_USE_9P`, `_USE_9P_RDMA`, `_USE_NFS_RDMA`, `USE_DBUS`, and `ENABLE_QOS`.

## Risks
- `nfs_rpc_callback_simulator.c` is appended in two separate `if(USE_CB_SIMULATOR)` blocks, which can duplicate a source.
- RDMA callback/dispatcher sources are compiled only when both `USE_9P` and `USE_9P_RDMA` are enabled, but Mooshika libraries are always in `target_link_libraries`; builds without Mooshika must ensure the variable is empty or valid.
- Version-script flags are Linux/FreeBSD specific; undefined-symbol policy changes under ASAN.
- Since `fsal_up_top.c` is compiled directly into `ganesha_nfsd`, changes there affect all FSAL plugins using the top vector.

## Test Signals
Run configure/build matrices for default, `USE_9P`, `USE_9P_RDMA`, `USE_DBUS`, `ENABLE_QOS`, `USE_MONITORING`, ASAN, and LTTng. Check duplicate object/source warnings, link undefined-symbol behavior, and exported symbols from `libganesha_nfsd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/maketest.conf -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/maketest.conf

## Purpose
This is an older test-runner configuration for a static log/hash library test. It declares one test, its command, and success/failure pattern matching in French-language output.

## Important APIs, Types, And Functions
- `Test Test_libloghash_Static` names the test product and command.
- `Command = ksh ../scripts/run_test_liblog.ksh` invokes the shell test script.
- `Success TestOk` matches `STDOUT` for a passing phrase and `STATUS == 0`.
- Failure blocks classify nonzero exits by output patterns: bad value, bad hash init, bad delete, bad statistics, missing key, and redundant key.

## Control Flow
The external test harness reads this file, runs the configured command, then evaluates the success and failure clauses against exit status and stdout. The first matching rule likely determines the reported result category.

## State And Persistence Behavior
The file has no runtime daemon state. Persistence is limited to test configuration in the source tree and whatever artifacts `run_test_liblog.ksh` creates.

## Dependencies And Integration Points
It depends on a maketest-style harness, `ksh`, and `../scripts/run_test_liblog.ksh`. It is colocated under `MainNFSD` but tests logging/hash behavior rather than the daemon code in this subset.

## Risks
- The file is likely legacy; command paths and expected French output strings may no longer match current scripts.
- Regex matching is brittle if the script output changes.
- It does not cover the MainNFSD startup, admin, 9P, or metrics code in this subset.

## Test Signals
Validation is straightforward: run the maketest harness against this config, verify `ksh` availability, confirm each expected failure pattern can still be emitted, and decide whether this legacy test remains part of active CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/maketest.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_admin_thread.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_admin_thread.c

## Purpose
This file implements Ganesha's admin thread, DBus admin surface, shutdown trigger, and orderly shutdown sequence. It exposes runtime operations such as grace-period control, cache purges, config reload, DRC inspection, malloc tracing/trim controls, and process shutdown.

## Important APIs, Types, And Functions
- `nfs_Init_admin_thread()` initializes the admin mutex/condition and registers DBus paths when enabled.
- `admin_halt()` sets `admin_shutdown` and wakes the admin thread.
- `admin_thread()` waits for shutdown and then runs `do_shutdown()`.
- DBus methods include `get_grace`, `grace`, `shutdown`, `get_drc_info`, `purge_gids`, `purge_netgroups`, `purge_idmapper_cache`, `purge_idmapper_negative_cache`, `init_fds_limit`, `malloc_trace`, `malloc_untrace`, `trim_enable`, `trim_disable`, `trim_call`, `trim_status`, and `reread_config`.
- DBus properties expose release/build metadata, and a heartbeat signal is registered through `admin_interface`.

## Control Flow
At startup, `nfs_Init_admin_thread()` prepares synchronization and DBus registration. `admin_thread()` blocks on `admin_control_cv` until `admin_halt()` is called by DBus shutdown, signal manager, or other subsystem. `do_shutdown()` then stops URL watchers, DBus, delayed executor, optional QOS, async state requests, RPC registration and services, monitoring, reaper, 9P workers, general fridge, pNFS data servers, exports, recovery, callback package, and FSALs. It chooses emergency FSAL cleanup if key thread shutdowns fail.

DBus methods validate argument counts/types, call the appropriate subsystem, and append a standardized status reply. Grace control parses `event[:arg]`, supports IP/node-id variants, and retries on `-EAGAIN` after waiting for grace refs to drain.

## State And Persistence Behavior
Persistent process state includes `admin_shutdown`, DBus method/property registration, global config toggles such as `nfs_param.core_param.malloc_trim`, cache contents in idmapper/uid2grp/netgroup subsystems, and the pid file removed during shutdown. Malloc status writes `malloc_info()` to `/tmp/mallinfo-<host>.<pid>.txt` as a side effect.

## Dependencies And Integration Points
The admin thread coordinates nearly every daemon subsystem: DBus, config URL/RADOS watches, delayed executor, QOS, state async queue, RPC services, monitoring, reaper, 9P workers, general fridge, pNFS DS registry, export manager, NFSv4 recovery, callback RPC, FSAL manager, idmapper, netgroup, uid2grp, duplicate request cache, and config reload.

## Risks
- Shutdown ordering is delicate; stopping services while requests still hold state can force emergency FSAL cleanup.
- DBus `malloc_trace` sets `MALLOC_TRACE` to a caller-provided filename, so deployments should treat this as privileged admin input.
- `trim_call()` and `trim_status()` rely on glibc malloc APIs and are not portable to all platforms.
- Config reload support is intentionally partial and can leave unsupported changes unapplied.
- The admin mutex/condvar are destroyed in `do_shutdown()`, so late calls to `admin_halt()` after teardown would be unsafe.

## Test Signals
Test DBus method argument validation, grace event parsing, cache purge effects, reread-config success/failure, shutdown ordering with active RPC/9P traffic, monitoring shutdown, QOS-enabled shutdown, and malloc trim/trace behavior on Linux and non-Linux builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_admin_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_init.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_init.c

## Purpose
This file owns most daemon initialization and lifecycle state: global parameters, prereq setup, config reload, package initialization, NFSv4 identity setup, service thread startup, capability lowering, malloc trimming, health checks, and the `nfs_start()` top-level service runner.

## Important APIs, Types, And Functions
- Global state includes `nfs_param`, `nfs_health_`, `nfs_init`, boot time/epoch, write verifiers, node identity, thread IDs, config/pid paths, and NFSv4 server owner/scope.
- `nfs_prereq_init()` initializes mutex attributes, logging, crash handlers, and nTIRPC allocators.
- `reread_config()` reparses the config and dynamically updates logging, exports, directory services, limited NFSv4 settings, idmapping, and supported Kerberos transitions.
- `nfs_set_param_from_conf()` loads core, QOS, IP/name, Kerberos, directory-services, NFSv4, 9P, MDCACHE, recovery, and RADOS URL settings.
- `init_server_pkgs()` initializes uid/group, netgroup, MDCACHE, state locks, IP/name cache, idmapper, and connection manager.
- `nfs_Init()` initializes DBus, metrics, ACLs, exports, NFSv4 client/state/session/owner caches, NLM/9P resources, pseudo FS, RPC services, admin thread state, callback package, and Kerberos.
- `nfs_Start_threads()` starts delayed executor, signal manager, optional 9P TCP/RDMA dispatchers, DBus thread, admin thread, reaper, and general fridge.
- `nfs_start()` runs the initialized service until the admin thread exits, then performs cleanup.
- `nfs_health()` checks enqueue/dequeue progress.

## Control Flow
The executable or library path parses config first, then calls `nfs_start()`. `nfs_start()` stores start info, sets umask, creates write verifiers from `get_unique_server_id()`, optionally lowers capabilities, calls `nfs_Init()`, starts threads, schedules periodic malloc trim, marks initialization complete, registers service with FSAL backends, initializes stats time, and joins the admin thread. Shutdown is driven by `admin_thread()` from `nfs_admin_thread.c`, after which `nfs_start()` cleans the init condition state and logging.

`sigmgr_thread()` synchronously waits for `SIGHUP` and `SIGTERM`; SIGHUP calls `reread_config()`, while SIGTERM calls `admin_halt()`. `nfs_init_wait()` and `nfs_init_wait_timeout()` let other components block until initialization completes.

## State And Persistence Behavior
This file initializes and mutates process-global runtime state. Durable effects are indirect: recovery backend initialization, RADOS URL watches, registered RPC ports, service exports, and possible malloc trim scheduling. The health function persists previous enqueue/dequeue snapshots in `healthstats` to detect lack of progress.

## Dependencies And Integration Points
It integrates config parsing, logging, nTIRPC, FSAL/MDCACHE, SAL state, NFS protocols, DBus, QOS, idmapper, uid2grp, netgroup, pNFS, recovery, callback RPC, monitoring metrics, 9P, NLM/NSM, RADOS config URLs, thread fridge, and Linux capabilities/prctl behavior.

## Risks
- Initialization ordering is tightly coupled; exports, FSAL loading, recovery, grace, and RPC startup must occur in the expected sequence.
- `reread_config()` supports only selected dynamic changes; unsupported Kerberos ON-to-ON changes release creds but do not fully reconfigure.
- `nfs_Start_threads()` comments that the 9P/RDMA dispatcher is never cancelled or cleaned up.
- `nfs_health()` can report healthy when only one request is enqueued but not dequeued, so it is a coarse signal.
- Capability lowering and `PR_SET_IO_FLUSHER` behavior vary by Linux permissions/config.

## Test Signals
Use startup matrix tests across NFSv3/v4, 9P, 9P/RDMA, NLM, DBus, monitoring, QOS, Kerberos on/off, and capability-dropping modes. Add config reload tests for log/export/directory/NFSv4 UTF8/Kerberos transitions; signal tests for SIGHUP/SIGTERM; health tests with stalled queues; and shutdown tests after partial initialization failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_lib.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_lib.c

## Purpose
This file provides `nfs_libmain()`, an embedded/library entry point that initializes and starts Ganesha without the standalone daemon CLI, pidfile locking, daemonization, monitoring setup, or full signal manager behavior from `nfs_main.c`.

## Important APIs, Types, And Functions
- `nfs_libmain(const char *ganesha_conf, const char *lpath, const int debug_level)` is the main library initializer.
- `my_nfs_start_info` defaults `drop_caps` to false for embedded use.
- `export_cleanup()` destroys `export_opt_lock`, and `export_cleanup_element` registers it with the cleanup framework.
- Globals `nfs_config_struct` and `nfs_host_name` mirror the standalone entry point.

## Control Flow
`nfs_libmain()` records boot time/epoch, adopts optional config/log paths, resolves the local hostname, initializes prereqs/logging, initializes `nfs_init`, ignores `SIGXFSZ` on Linux, blocks `SIGPIPE`, initializes URL handling, parses config, applies log config, starts FSALs, loads parameters, initializes server packages, reads data servers, initializes NFSv4 recovery and netconfigs, starts and waits for grace enforcement, initializes export option locking, reads exports, reports config errors, frees the parse tree, and calls `nfs_start()`.

## State And Persistence Behavior
It mutates the same global daemon state as standalone startup, including config paths, host name, exports, recovery, netconfigs, grace, FSALs, and runtime threads. It registers cleanup for `export_opt_lock`. It frees library-allocated config/log/host strings after `nfs_start()` returns.

## Dependencies And Integration Points
The library path shares most initialization helpers with `nfs_main.c` and `nfs_init.c`: config parser, logging, FSAL startup, parameter loading, server package initialization, data-server/export loading, recovery, netconfig, grace, and service start.

## Risks
- It blocks only `SIGPIPE`, unlike the standalone daemon which blocks `SIGTERM`, `SIGHUP`, and `SIGPIPE` before logging threads start.
- There is no pidfile locking, daemonization, dynamic metrics startup, Linux `PR_SET_IO_FLUSHER`, or fatal-on-config-warning option.
- `nfs_start()` still joins the admin thread, so library callers must understand that `nfs_libmain()` is a blocking service runner.
- Global names overlap with `nfs_main.c`; both are not meant to be linked as competing entry paths in the same binary.

## Test Signals
Test embedded startup with explicit and default config paths, parse failures, no exports, recovery init failure, `SIGPIPE` behavior, shutdown via `admin_halt()`, cleanup callback execution, and parity with standalone startup for shared subsystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_main.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_main.c

## Purpose
This file is the standalone `nfs-ganesha` daemon entry point. It parses CLI options, prepares signal masks, initializes logging and memory, optionally daemonizes, locks/writes the pid file, parses configuration, starts FSALs and core packages, initializes monitoring and recovery/grace/export state, then hands control to `nfs_start()`.

## Important APIs, Types, And Functions
- `main()` is the executable entry.
- `main_strdup()` wraps `strdup()` with abort-on-failure for early CLI strings.
- `valid_stack_size()` restricts `-S` to known stack sizes.
- `load_lttng()` dynamically loads tracepoint libraries when `USE_LTTNG` is enabled.
- CLI options include version, log path, debug level, config path, pid file, foreground, stack size, default config dump, epoch, node ID, virtual IP, crash trace, fatal config errors, and LTTng loading.

## Control Flow
`main()` blocks `SIGTERM`, `SIGHUP`, and `SIGPIPE` before logging can create threads, sets boot time/epoch, resolves executable and host names, parses options, initializes prereqs/logging and `nfs_init`, optionally daemonizes, ignores `SIGXFSZ`, opens and locks the pid file, writes the current PID, initializes config URL support, parses config, applies log config, starts FSAL modules, loads parameters, applies Linux `PR_SET_IO_FLUSHER` if configured, starts monitoring/dynamic metrics when enabled, initializes server packages, reads data servers, initializes NFSv4 recovery, netconfigs, grace, exports, checks unused blocks and config warnings, frees the parse tree, and calls `nfs_start()`.

## State And Persistence Behavior
Persistent side effects include daemonization, pid file creation/locking/truncation/fsync, optional monitoring listener startup, recovery backend initialization, registered exports, grace state, and runtime global configuration. On fatal startup errors it reports config errors, closes resources it owns, sleeps briefly for journald visibility, and calls `LogFatal()`.

## Dependencies And Integration Points
It coordinates CLI, logging, config parsing, FSAL module loading, core parameter loading, Linux process controls, monitoring, server package initialization, recovery, netconfig, grace, export loading, and the service lifecycle in `nfs_init.c`.

## Risks
- Signal masking must remain before any thread-spawning initialization; moving logging earlier would route signals to arbitrary threads.
- Pid file locking is the primary multiple-instance guard; filesystem semantics matter.
- The deprecated `-R` path exits after printing replacement config.
- ASAN/LTTng dynamic loading and Linux `PR_SET_IO_FLUSHER` have platform-specific behavior.
- Fatal config warnings depend on `-x`, so CI should decide whether harmless warnings are acceptable.

## Test Signals
Run CLI option tests for all flags, invalid debug/stack values, foreground/background startup, pidfile lock contention, missing/invalid config, config warning with and without `-x`, monitoring bind address fallback, LTTng load failure, and SIGTERM/SIGHUP behavior after handoff to service threads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_metrics.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_metrics.c

## Purpose
This file registers and updates built-in NFS metrics for monitoring support. It covers build info, RPC received/completed/in-flight counts, NFSv4 operation latency/count by opcode and status, compound latency and operation count, dropped GSS requests, and dynamic per-request observations for NFSv3/NFSv4.

## Important APIs, Types, And Functions
- `FOREACH_NFS_STAT4` enumerates tracked NFSv4 status codes.
- `enum nfsstat4_index`, `nfsstat4_to_index()`, and `index_to_nfsstat4[]` map sparse protocol status values to dense metric array indexes.
- `register_ganesha_info_metrics()` registers `ganesha_build_info` with version, build time, and server scope labels.
- `nfs_metrics__init()` registers RPC, NFSv4 operation, dropped GSS, and compound metrics.
- `nfs_metrics__nfs4_op_completed()`, `nfs_metrics__nfs4_compound_completed()`, `nfs_metrics__rpc_received()`, `nfs_metrics__rpc_completed()`, `nfs_metrics__rpcs_in_flight()`, and `nfs_metrics__gss_request_dropped()` update metric handles.
- `nfs_metrics__nfs3_request()` and `nfs_metrics__nfs4_request()` feed dynamic request metrics with version, operation, status, export, path, and client IP.

## Control Flow
During daemon initialization, `nfs_metrics__init()` registers global counters/gauges/histograms. If NFSv4 server scope is initialized under monitoring, `register_ganesha_info_metrics()` registers a one-valued build info gauge. Request-processing code later calls update functions to observe latencies and increment counters. NFSv4 operation registration eagerly creates a metric handle for every opcode/status-index pair.

## State And Persistence Behavior
State is held in static metric handles and monitoring registry entries. The file does not persist data itself; persistence/export depends on the monitoring backend. Latencies are converted from nanoseconds to milliseconds before histogram observation.

## Dependencies And Integration Points
It depends on the monitoring API, dynamic metrics API, NFS protocol conversion helpers (`nfsop4_to_str`, `nfsstat4_to_str`, `nfsstat3_to_str`, `nfs_req_result_to_str`), and protocol constants from NFSv4/NFSv3 headers. `nfs_init.c` calls initialization and build-info registration.

## Risks
- Eagerly registering `NFS4_OP_LAST_ONE * NFSSTAT4_INDEX_LAST` histograms and counters can create high metric cardinality at startup.
- Update functions assume metric handles are registered; calling them before `nfs_metrics__init()` would be unsafe.
- Unknown NFSv4 statuses collapse into `NFSSTAT4_INDEX_UNKNOWN_STATUS` with status string for `(nfsstat4)-1`.
- Dynamic metrics include path/client labels, so cardinality can be very high if enabled.

## Test Signals
Check metric registration under monitoring-enabled builds, verify all known NFSv4 statuses map to stable labels, call update functions for known and unknown statuses, validate latency unit conversion, test NFSv3 conditional compilation, and load-test cardinality with dynamic metrics enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_metrics.c -->
