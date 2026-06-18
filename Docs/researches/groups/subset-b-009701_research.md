# subset-b-009701 research

Grouped research for NFS-Ganesha MainNFSD QoS, reaper, callback, callback simulator, RPC dispatcher, and legacy TCP socket manager sources. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_qos.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_qos.c

## Purpose

This file implements the optional NFSv4 QoS engine for NFS-Ganesha. It applies configured bandwidth, token, IOPS, and data-server controls to NFS read/write and compound paths, suspends work that exceeds configured limits, and resumes deferred work from dedicated QoS threads. It supports per-export, per-client, and per-export-per-client policy modes.

The file is guarded by the `ENABLE_QOS` build path through `nfs_qos.h` and integrates with NFSv4 read/write callbacks (`nfs4_qos_read_cb`, `nfs4_qos_write_cb`, `nfs4_qos_compound_cb`), export/client lifetime hooks, global runtime config, TI-RPC socket suspension/resumption, and optional monitoring gauges.

## Important APIs, types, and functions

The exported entry points are `qos_init`, `shutdown_qos`, `qos_process`, `qos_process_iops`, `qos_perexport_insert`, `qos_free_mem`, `qos_drain_bw_ios`, `qos_drain_iops_ios`, `copy_gsh_qos_conf`, and `pepc_get_client_from_list`. They are the public lifecycle, request gating, config insertion, cleanup, and config-copy interfaces.

Core state comes from `nfs_qos.h`: `qos_block_config_t` stores global/per-export configuration; `qos_class_t` represents an export or client QoS class; `qos_bucket_t` stores read/write accounting and wait queues; `timer_entry_t` stores delayed callbacks; `qos_client_entry_t` groups token-exhausted I/O by client and transport; `qos_status_t`, `qos_class_type_t`, and `qos_op_type_t` describe suspension status, class kind, and read/write operation kind.

Global state includes `qos_block_config`, `g_qos_config`, `qos_bits`, `g_qos_iopath_lock`, `g_qos_config_lock`, and two `qos_thread` workers. `QOS_THREAD_RUNNABLE` controls worker lifecycle. The locking comment near the globals is important: config updates use `g_qos_config_lock`, IO-path lazy creation also uses `g_qos_iopath_lock`, producers manipulate bucket queues with `bucket->lock`, and PEPC consumer paths can hold export and client bucket locks while moving entries between queues.

Allocation and list helpers include `allocate_qos_class`, `allocate_client`, `alloc_clientdetails_pe`, `alloc_qos_cb_args`, `create_timer_entry`, `insert_timer_entry_sorted`, `insert_timer_entry`, `resume_timer_entry`, `release_wait_ios`, and `execute_qos_expired_timers`. `get_qos_resume_func` maps `QOS_READ`/`QOS_WRITE` to the appropriate NFSv4 resume callback; `qos_cb_str` is debug-only callback labeling.

Config application is centered on `set_class_values`, `update_class_token_values`, `update_class_bw_values`, `update_class_ds_values`, `update_class_iops_values`, `setNode_pe`, and `setNode_pc`. These copy numeric limits into read/write buckets, choose combined read/write mode by using the write bucket as the combined bucket, drain queues when features are disabled or switched, and optionally register metrics through `register_qos_metrics`.

Request processing is split by policy: `qos_process_pe`, `qos_process_pc`, and `qos_process_pepc` feed `qos_check_pe_pc` or `qos_check_pepc` for token and bandwidth decisions. IOPS processing is similarly split through `qos_process_iops_pe`, `qos_process_iops_pc`, and `qos_process_iops_pepc`, with `qos_iops_check` and `qos_iops_suspend_task` doing the bucket accounting.

The consumer side is handled by `qos_thread_func`, `resume_io`, `refresh_qos_token`, `resume_bw_io`, `resume_bw_io_pepc`, `pepc_reschedule_bw_io`, `resume_ops_io`, `resume_iops_pepc`, and `pepc_reschedule_iops`. Iterator callbacks (`ps_io_control_iter`, `pc_io_control_iter`, `pepc_io_control_iter`, `ps_token_control_iter`, `pc_token_control_iter`, `pepc_token_control_iter`) traverse the global export/client registries.

## Control flow

Startup calls `qos_init`, which initializes the two global mutexes and calls `qos_thread_init` if QoS is enabled. `qos_thread_init` sets `QOS_THREAD_RUNNABLE` and creates one read worker and one write worker. Each worker loops while the flag is set, calls `resume_io(op_type)` to release expired BW/IOPS work, and the write worker periodically calls `refresh_qos_token` every `TOKEN_REFRESH_DELAY` loop iterations.

On the producer path, NFS read/write code calls `qos_process(size, caller_data, data, op_type, is_ds)`. The function returns immediately if QoS is globally disabled or data-server control is not enabled for DS operations. It dispatches by `g_qos_config->qos_type`: per-export lazily creates `op_ctx->ctx_export->qos_class`; per-client lazily creates `op_ctx->client->qos_class`; PEPC lazily creates the export class and then per-client sub-classes in the export's `clients` list.

For per-export and per-client, `qos_check_pe_pc` takes the class lock, checks token availability, potentially enqueues token-exhausted work, consumes tokens, and then applies bandwidth control. For PEPC, `qos_check_pepc` finds or creates the sub-client class, checks export and client token limits, consumes both, and if client bandwidth control is enabled queues the operation into the client bucket for later rescheduling to the export bucket.

Token exhaustion uses `qos_token_exausted_suspend_task`. It creates a callback arg with `NON_RATELIMITING_IO`, calculates a wakeup time bounded by token refresh time and `TOKEN_NFS_ERR_DELAY_DEFAULT`, groups waits under a `qos_client_entry_t`, and after `SUSPEND_SOCKET_IO_LIMIT` pending operations suspends socket receive with `svc_rqst_qos_suspend_socket`. `refresh_qos_client` later releases expired or token-refresh-unblocked operations and calls `svc_rqst_qos_resume_socket` when the client entry drains.

Bandwidth control uses a virtual last-departure timestamp (`bw_ldct`) and `required_time = bytes * 1000000 / max_bw_allowed`. If the computed schedule is in the future, `qos_process_bw` queues a timer entry; otherwise it accounts consumption and lets the operation continue. PEPC bandwidth first queues to client buckets, then `pepc_reschedule_bw_io` moves eligible entries into export buckets sorted by expiry, and `resume_bw_io_pepc` releases export-bucket entries subject to export-level pacing.

IOPS control uses compound operation count (`data->argarray_len`) rather than byte count. `qos_iops_check` sets `IS_QOS_IOPS_ACCOUNTED`, advances `iops_ldct`, and either accounts immediately or queues a compound callback. PEPC IOPS enqueues at the client bucket immediately; the QoS thread later reschedules to the export bucket and resumes entries.

Shutdown calls `shutdown_qos`. It clears the runnable bit under `g_qos_iopath_lock`, disables `g_qos_config->enable_qos`, joins both worker threads, drains all pending QoS I/O through `stop_qos_io`, and destroys the global mutexes.

## State and persistence behavior

The QoS state is runtime-only and attached to live `gsh_export` and `gsh_client` objects. Per-export config may allocate `gsh_export->qos_block` and `gsh_export->qos_class`; per-client config uses `gsh_client->qos_class`; PEPC stores per-client `qos_class_t` instances in an export class `clients` list. There is no on-disk persistence in this file.

Each bucket persists rate-control accounting across operations: `bw_ldct`, `data_consumed`, `iops_ldct`, `iops_consumed`, `token_ldct`, `tokens_consumed`, maximum limits, metric handles, and wait-list length. Token buckets reset `tokens_consumed` only when the consumed amount is at or over the limit and the renew time has elapsed.

Timer entries own callback arguments allocated by `alloc_qos_cb_args`; `resume_timer_entry` calls the stored callback, unlinks the timer, and frees only the timer entry. The resume callback is therefore responsible for finishing or freeing its argument chain. Token-exhausted client entries are freed when their wait list drains.

Runtime config update paths can drain queues and mutate class flags. `copy_gsh_qos_conf` propagates export QoS config during export copy/reexport flows and re-applies PEPC client node values under the export class lock. Runtime enablement is partially supported by lazy class creation, while the comment near `qos_init` says full runtime enable/disable is not supported except through a separate thread-init path.

## Dependencies and integration points

The file depends on NFS-Ganesha core context (`op_ctx`, `compound_data_t`, `gsh_export`, `gsh_client`, export/client iterators), NFSv4 callback hooks, the Ganesha list and memory APIs, pthreads and atomics, monotonic time, TI-RPC request transport functions, and optional monitoring (`nfs_metrics.h`, `monitoring__register_gauge`, `monitoring__gauge_set`, `sprint_sockip`).

It integrates with export/client lifetime through `qos_free_mem`, `pe_stop_iter`, and `pc_stop_iter`; with export reconfiguration through `qos_perexport_insert`, `qos_perclientinsert`, and `copy_gsh_qos_conf`; with the request path through `qos_process` and `qos_process_iops`; and with shutdown through `shutdown_qos`.

The monitoring integration labels metrics by export path, client address, or export-client pair. Metrics are registered lazily when the class feature is enabled and reset when queues are drained or tokens refresh.

## Risks and edge cases

There are several subtle arithmetic and synchronization risks. Bandwidth and IOPS scheduling divide by configured maxima, so validation must guarantee nonzero values. Combined read/write mode redirects to the write bucket; switch-over paths must drain the correct queues or read-bucket entries can remain stuck. In `update_class_bw_values`, the combined-mode branch checks `wbucket->io_waitlist_qos_bc` but releases `rbucket->io_waitlist_qos_bc`, which looks suspicious and should be tested carefully.

PEPC locking is delicate. `qos_check_pepc` checks token availability on the sub-client before taking the export class lock and does not lock the sub-client class around all token operations. The design comment says export-level locking protects runtime disablement while bucket locks protect consumer manipulation, but PEPC token and class list interactions are a high-risk concurrency area.

Token availability uses `tokens_consumed <= max_available_tokens`, not `tokens_consumed + rsize <= max_available_tokens`. This allows an operation that crosses the limit to pass and only blocks later operations. That may be intentional burst semantics, but tests should encode it.

`qos_get_time_to_tokenrefresh` assumes a non-NULL token bucket; callers only use it after token checks, but malformed state could dereference NULL. `release_wait_ios` and `execute_qos_expired_timers` decrement both counters blindly, and some callers pass dummy counters initialized to `UINT32_MAX`, which is safe only because the dummy is intentionally ignored.

The shutdown path disables global QoS and joins threads before draining queues. Any producer still entering the QoS path during shutdown could interact with destroyed mutexes if lifecycle ordering is wrong. The socket-suspend path also stores `SVCXPRT *` in token client entries and later resumes it after freeing the entry, so transport lifetime assumptions matter.

## Test signals

Useful signals are unit or integration tests that exercise `qos_process` return values, token exhaustion and refresh, bandwidth/IOPS queueing and release, combined read/write mode, PE/PC/PEPC lazy class creation, data-server bypass behavior, export/client cleanup, shutdown draining, and socket suspend/resume thresholds.

Runtime tests should inspect that delayed callbacks are eventually invoked, counters return to zero after drain, no operation stays queued after disabling a QoS feature, and PEPC client queues are rescheduled to export queues in sorted expiry order. Monitoring builds should verify gauges are registered once per class/bucket and reset on drain or token refresh. Stress tests should include concurrent request producers, runtime export config updates, and export/client destruction while queues contain entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_reaper_thread.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_reaper_thread.c

## Purpose

This file implements the NFSv4 reaper looper. Its job is to periodically expire stale NFSv4 client IDs, reap delayed client cleanup lists, release cached open owners after their close-pending grace window, and optionally call `malloc_trim` to reduce heap fragmentation.

The reaper is implemented as a `fridgethr` single-thread looper named `reaper`. It is part of MainNFSD lifecycle startup/shutdown and maintains NFSv4 lease health by walking confirmed and unconfirmed client-id hash tables.

## Important APIs, types, and functions

`reaper_init` creates and starts the looper. `reaper_wake` wakes it early if `reaper_fridge` exists. `reaper_shutdown` stops it with a 120-second sync command and cancels on timeout.

`reaper_run` is the periodic worker callback. It invokes `nfs_maybe_start_grace`, tries to lift grace with `nfs_try_lift_grace` unless `admin_shutdown` is set, logs state dumps in debug builds, reaps delayed cleanup, walks both client-id hash tables, reaps expired open owners, and optionally trims malloc fragmentation.

`reap_hash_table` iterates a `hash_table_t` partition-by-partition, takes each partition write lock, walks the red-black tree, checks each `nfs_client_id_t` under `cid_mutex`, skips valid leases and already delayed cleanup, references the client id, drops the partition lock, expires the client with `nfs_client_id_expire`, and restarts the current partition walk because expiration may mutate the tree.

`reap_expired_open_owners` walks the global `cached_open_owners` list under `cached_open_owners_lock`, stops at the first non-expired owner because the list is ordered by expiration, and calls `uncache_nfs4_owner` for expired entries.

On non-Apple platforms, `get_current_rss` reads `/proc/self/statm` and `reap_malloc_frag` calls `malloc_trim(0)` when current RSS exceeds a dynamic threshold derived from `nfs_param.core_param.malloc_trim_minthreshold`.

## Control flow

Initialization sets `reaper_delay` to the default 10 seconds unless the NFSv4 lease lifetime is less than 20 seconds, in which case it uses half the lease lifetime. `reaper_init` fills `fridgethr_params` with one minimum and maximum thread, `fridgethr_flavor_looper`, and the selected delay, initializes the fridge, and submits `reaper_run` with `reaper_state`.

Each `reaper_run` tick first manages grace-period state. It then logs a "checking clients" message only when prior work was nonzero or the message has not been logged yet, with optional SAL state dumps when `DEBUG_SAL` is enabled and the previous count was zero.

Client expiration first drains `reap_expired_client_list(NULL)`, then `reap_hash_table(ht_confirmed_client_id)`, then `reap_hash_table(ht_unconfirmed_client_id)`. Inside `reap_hash_table`, if an expired client is found, the function obtains a client-id reference, releases the partition lock, locks the client record, expires the client, unlocks, drops the reference, and restarts the partition from the root. This avoids continuing an iterator across a tree modified by expiration.

Open-owner reaping follows client-id reaping. It repeatedly inspects the first cached owner and stops as soon as it sees a future expiration time, relying on insertion/order semantics of `cached_open_owners`.

Shutdown sends `fridgethr_comm_stop`. If that times out, the reaper fridge is canceled. Other nonzero return codes are logged and returned to the caller.

## State and persistence behavior

The file owns `reaper_delay`, `reaper_fridge`, and `reaper_state`. `reaper_state.count` carries the amount of work from the previous run for logging decisions, and `reaper_state.logged` suppresses repetitive idle debug logs.

Persistent server state is external: confirmed/unconfirmed client-id hash tables, the expired client list, cached open-owner list, grace-period flags, client records, and global NFS parameters. The reaper mutates those external structures by expiring clients, uncacheing owners, and potentially triggering delayed cleanup paths.

Memory trimming state is maintained in a static `trim_threshold` inside `reap_malloc_frag`. It starts at the configured minimum, drops if current RSS is much lower, and after trimming becomes 1.5x the current RSS or the configured minimum.

## Dependencies and integration points

This file depends on `fridgethr`, NFSv4 state and lease APIs (`valid_lease`, `nfs_client_id_expire`, `inc_client_id_ref`, `dec_client_id_ref`, `display_client_id_rec`), SAL state owner APIs (`cached_open_owners`, `uncache_nfs4_owner`, `display_owner`), NFS core parameters, logging, pthread locks, and hash-table/red-black tree internals.

It integrates directly with NFSv4 grace handling (`nfs_maybe_start_grace`, `nfs_try_lift_grace`) and the global shutdown flag (`admin_shutdown`). The `/proc/self/statm` and `malloc_trim` path is Linux/glibc-oriented and compiled out on Apple.

## Risks and edge cases

The hash-table reaper intentionally drops and reacquires locks during expiration, so restart behavior is essential. Removing the `goto restart` pattern or keeping iterators across expiration would risk use-after-free or missing entries.

`reap_hash_table` takes partition write locks even though it is scanning, because expiration can mutate table state. This can block client-id operations; long expiration work is therefore moved outside the partition lock, but the per-partition restart can be expensive if many clients expire.

The open-owner cache assumes entries are ordered by expiration and not moved while cached. If that invariant breaks, `reap_expired_open_owners` can leave expired owners behind after the first future-dated entry.

`reaper_delay` can become zero if lease lifetime is less than two seconds because integer division is used. The surrounding configuration likely prevents such a lease value, but validation should ensure the looper delay remains usable.

`get_current_rss` returns zero on several failures. `reap_malloc_frag` treats zero as a very low RSS and may adjust thresholds downward; logs help identify `/proc` parsing failures but the behavior is intentionally nonfatal.

## Test signals

Useful tests include hash tables containing valid, expired, delayed-cleanup, confirmed, and unconfirmed clients; expiration paths that mutate the table; delayed cleanup list saturation; cached open owners ordered by expiration; early wake behavior; shutdown timeout behavior; and `malloc_trim` threshold evolution with mocked RSS.

Integration signals are logs showing grace lift attempts, client expiration counts, no leaked client references, no partition-lock deadlocks, and timely removal of expired owners. Stress tests should create many client IDs expiring at once and verify the restart loop terminates and the server remains responsive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_reaper_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback.c

## Purpose

This file implements NFSv4 callback/backchannel RPC client management. It creates callback channels for NFSv4.0 clients from SETCLIENTID callback addresses, creates NFSv4.1 backchannel clients on established sessions/transports, dispatches `CB_COMPOUND` calls asynchronously, tests callback reachability with `CB_NULL`, manages v4.1 callback slots, and handles callback authentication.

The public API serves delegation/layout recall and other NFSv4 callback users through `nfs_rpc_cb_single`, while startup/shutdown code uses `nfs_rpc_cb_pkginit` and `nfs_rpc_cb_pkgshutdown`. GSS callback support is compiled under `_HAVE_GSSAPI`.

## Important APIs, types, and functions

Public functions include `nfs_rpc_cb_pkginit`, `nfs_rpc_cb_pkgshutdown`, `nfs_rpc_cb_set_gss_status` when GSS is enabled, `nfs_set_client_location`, `nfs_rpc_create_chan_v40`, `nfs_rpc_create_chan_v41`, `nfs_rpc_get_chan`, `nfs_rpc_destroy_chan`, `alloc_rpc_call`, `free_rpc_call`, `nfs_rpc_call`, `nfs41_release_single`, `nfs_test_cb_chan`, and `nfs_rpc_cb_single`.

`netid_nc_table` and `nfs_netid_to_nc` translate NFS network IDs such as `tcp`, `tcp6`, `udp`, `udp6`, `rdma`, and `rdma6` to internal `nc_type` values. `setup_client_saddr` parses NFSv4.0 universal address strings into `sockaddr_t` storage in `clientid->cid_cb.v40.cb_addr`.

NFSv4.0 channel creation uses `nfs_clid_connected_socket`, `clnt_vc_ncreatef` for TCP, `clnt_dg_ncreatef` for UDP, and authentication setup from the client credential. Supported auth flavors are `RPCSEC_GSS`, `AUTH_SYS`, and `AUTH_NONE`; GSS setup uses `nfs_rpc_callback_setup_gss`.

NFSv4.1 channel creation uses `nfs_rpc_create_chan_v41`. It locks `session->cb_chan.chan_mtx`, destroys an existing channel if it belongs to a different transport, creates an RPC client from the service transport with `clnt_vc_ncreate_svc` or `clnt_rdma_ncreatef`, selects `AUTH_NONE` or `AUTH_SYS` from `callback_sec_parms4`, and sets `session_bc_up`.

RPC call lifecycle is represented by `rpc_call_t`/`struct _rpc_call` and `struct clnt_req`. `alloc_rpc_call` increments `nfs_health_.enqueued_reqs`; `nfs_rpc_call` fills the request for `CB_COMPOUND`; `nfs_rpc_call_process` handles auth refresh retry, marks the call finished, invokes the completion hook, and releases the call; `nfs_rpc_call_free` frees the enclosing `rpc_call_t` and increments `dequeued_reqs`.

NFSv4.1 callback construction uses `construct_v41`, `release_v41`, `find_cb_slot`, and `release_cb_slot`. Every v4.1 single-op callback is wrapped in a two-op compound with `CB_SEQUENCE` followed by the requested callback operation.

## Control flow

Package initialization sets up the GSS credential cache machinery and validates mechanisms when GSS is compiled in. Package shutdown clears and destroys GSS callback resources.

For NFSv4.0, `nfs_set_client_location` records the client's callback netid and address. `nfs_rpc_create_chan_v40` validates the auth flavor, opens and connects a socket to that address, creates a libntirpc client, attaches an auth handle, and leaves the channel in `clientid->cid_cb.v40.cb_chan`. `nfs_rpc_v40_single` refuses calls if the callback channel is marked down, obtains or creates a channel, constructs a one-op `CB_COMPOUND`, and dispatches it with `nfs_rpc_call`.

For NFSv4.1, session setup calls `nfs_rpc_create_chan_v41` when a backchannel is negotiated. Later, `nfs_rpc_get_chan` scans the client's v4.1 session list under `cid_mutex` and returns the first session whose `session_bc_up` flag is set. `nfs_rpc_v41_single` walks those sessions, reserves a callback slot, gets a stable session reference, drops `cid_mutex`, constructs the call with `CB_SEQUENCE`, dispatches it, and returns success if dispatch started. On dispatch failure it clears `session_bc_up`, releases the slot without advancing the sequence, drops the session reference, and retries with another session; after one full pass it retries once with a short slot wait.

`nfs_rpc_call` serializes access to the channel with `chan_mtx`, fills the client request with XDR functions for `CB_COMPOUND4args` and `CB_COMPOUND4res`, configures asynchronous completion, and calls `CLNT_CALL_BACK`. If setup or dispatch fails, it destroys the channel and marks the call aborted. Successful async completion flows later through `nfs_rpc_call_process`.

`nfs_test_cb_chan` ensures a channel exists, verifies client and auth handles, sends `CB_NULL` with `rpc_cb_null`, and retries once if the result is `RPC_INTR`. A failed null call destroys the channel so the next attempt can recreate it.

## State and persistence behavior

The file persists callback channel state inside `nfs_client_id_t` for v4.0 and `nfs41_session_t` for v4.1. Channels contain a libntirpc client handle, auth handle, type, source pointer, GSS security parameters, `chan_mtx`, and `last_called`. Destroying a channel tears down auth and client handles and resets `last_called`.

V4.1 backchannel state includes `session_bc_up`, `cb_mutex`, `cb_cond`, `bc_slots[]`, slot sequence numbers, and session references. `find_cb_slot` increments the sequence when reserving a slot; `release_cb_slot(..., sent=false)` rolls it back if the call was never sent. Completion hooks must call `nfs41_release_single` for v4.1 calls to release the slot and session reference.

GSS callback enablement is global process state protected by `gss_callback_status.lock`. Disabling GSS clears the credential cache; enabling GSS initializes the callback credential directory and refreshes machine credentials.

`alloc_rpc_call`/`nfs_rpc_call_free` update health counters, and request allocation is tied to libntirpc completion. `free_rpc_call` frees callback arg/result arrays and releases the `clnt_req`; final object memory is freed by the request free callback.

## Dependencies and integration points

The file depends on libntirpc client APIs (`clnt_vc_ncreatef`, `clnt_dg_ncreatef`, `clnt_vc_ncreate_svc`, `CLNT_CALL_BACK`, `CLNT_CALL_WAIT`, `clnt_req_*`), NFSv4 XDR structures, SAL client/session data, GSS credential cache helpers, pthread locks/condition variables, socket APIs, and Ganesha memory/logging helpers.

It integrates with NFSv4 client ID setup (`nfs_set_client_location`), session creation, delegation/layout recall users via `nfs_rpc_cb_single`, callback simulator code, state referral tracking through `struct state_refer`, and server health counters.

## Risks and edge cases

NFSv4.0 universal-address parsing is fragile by nature: `setup_client_saddr` splits on the last two dots to extract port bytes, then passes the remaining string to `inet_pton`. Malformed addresses silently leave zeroed socket state except for warnings, and unsupported netids later fail channel creation.

V4.0 UDP channel creation sets `raddr.maxlen/len` to `sizeof(struct sockaddr_in6)` regardless of actual address family, while TCP uses `sizeof(struct sockaddr_in)`. This should be validated because IPv6 TCP and IPv4 UDP sizes can be mismatched.

GSS callback support only formats host principals for `RPC_CHAN_V40`; v4.1 RPCSEC_GSS callback security parameters are explicitly skipped. Deployments requiring v4.1 GSS callbacks will fail to select that auth path.

The async call ownership contract is easy to violate. V4.1 callers must provide a completion callback and eventually call `nfs41_release_single`; the code calls `LogFatal` if no completion hook is provided because slot/session leaks would otherwise occur. V4.0 calls do not have the same slot-release requirement.

`nfs_rpc_get_chan` returns a v4.1 channel pointer after releasing `cid_mutex`; correctness depends on session/channel lifetime being protected by subsequent call code obtaining a session reference in `nfs_rpc_v41_single`. Direct external use of the returned pointer would be riskier.

Channel failure policy is coarse: most failed calls destroy the channel or clear `session_bc_up`. This avoids repeated use of broken paths but can amplify transient errors into callback unavailability until reestablishment.

## Test signals

Test signals should cover address parsing for IPv4/IPv6 universal addresses, unsupported netids, TCP/UDP v4.0 channel creation, auth flavor selection, GSS enable/disable behavior, failed and successful `CB_NULL`, v4.1 channel replacement when a new transport is supplied, RDMA compiled/uncompiled behavior, and security parameter fallback order.

V4.1 tests should verify slot reservation, highest-slot calculation, sequence rollback on unsent failure, release on completion, retry with short wait, session reference balancing, and clearing `session_bc_up` on dispatch errors. Async call tests should verify completion hook invocation, auth-refresh retry, health counter balance, channel destruction on failure, and no leaks of `CB_SEQUENCE` referral allocations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback_simulator.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback_simulator.c

## Purpose

This file implements a DBus-exposed callback simulator for NFS-Ganesha. It lets operators or tests list confirmed NFSv4.0 client IDs, list NFSv4.1 session IDs, test a callback backchannel, and issue a fake `CB_RECALL` against a selected client ID.

The simulator is diagnostic and test-oriented. It is inspired by an upcall simulator and does not implement production delegation policy; it manually constructs callback operations and dispatches them through the callback subsystem in `nfs_rpc_callback.c`.

## Important APIs, types, and functions

`nfs_rpc_cbsim_pkginit` registers the DBus path `CBSIM` with interface `org.ganesha.nfsd.cbsim`. `nfs_rpc_cbsim_pkgshutdown` is a no-op placeholder.

DBus methods are described by `cbsim_get_client_ids`, `cbsim_get_session_ids`, and `cbsim_fake_recall`. Their method functions are `nfs_rpc_cbsim_get_v40_client_ids`, `nfs_rpc_cbsim_get_session_ids`, and `nfs_rpc_cbsim_fake_recall`.

`nfs_rpc_cbsim_get_v40_client_ids` walks `ht_confirmed_client_id`, appends a timestamp, and returns an array of `uint64_t` client IDs. `nfs_rpc_cbsim_get_session_ids` walks `ht_session_id`, base64-encodes each `NFS4_SESSIONID_SIZE` session ID with `b64_ntop`, and returns an array of strings.

`cbsim_test_bchan` gets a confirmed client ID with `nfs_client_id_get_confirmed` and invokes `nfs_test_cb_chan`. `cbsim_fake_cbrecall` obtains the client, gets a callback channel, constructs a fake `CB_RECALL`, dispatches it with `nfs_rpc_call`, and uses `cbsim_completion_func` for logging.

`cbsim_free_compound` is marked unused. It shows how to free a constructed callback compound and specifically handles freeing `CB_RECALL` file-handle storage before `cb_compound_free`.

## Control flow

Initialization builds static DBus descriptors and registers the path. There is no dynamic simulator thread or background state; DBus method calls execute the relevant table scan or callback dispatch path.

For `get_client_ids`, the method initializes a DBus reply, appends the current timestamp with `gsh_dbus_append_timestamp`, opens an array container, and for each hash partition takes the partition write lock, walks the red-black tree, appends `cid_clientid`, and unlocks.

For `get_session_ids`, the flow is the same except it walks `ht_session_id`, base64-encodes `session_data->session_id`, and appends strings. The buffer is stack-allocated with `alloca(2 * NFS4_SESSIONID_SIZE)`.

For `fake_recall`, the DBus method defaults to client ID `9315` if no valid uint64 argument is supplied, then calls `cbsim_test_bchan` and `cbsim_fake_cbrecall` regardless of the test result. `cbsim_fake_cbrecall` validates the confirmed client record, verifies the channel, client handle, and auth handle, allocates an RPC call, initializes a v4.0 one-op callback compound tagged `brrring!!!`, fills a synthetic `CB_RECALL4args`, and calls `nfs_rpc_call`.

The completion function logs success or abort status and, for successful calls, logs the RPC result status. It does not free simulator-specific data because the active fake recall path intentionally leaves the fake file-handle string to the call cleanup path and comments that it leaks.

## State and persistence behavior

This file owns no persistent mutable state beyond static DBus descriptors. It reads global NFS client/session hash tables and can trigger callback-channel side effects through `nfs_test_cb_chan`, `nfs_rpc_get_chan`, and `nfs_rpc_call`.

The fake recall allocates a transient `rpc_call_t` and callback compound. On immediate dispatch failure it calls `free_rpc_call`; on async completion the callback subsystem releases the call. The fake file handle is allocated with `gsh_strdup`, and the in-source comment says it leaks, so repeated simulator use can create diagnostic-only memory growth.

DBus replies include a timestamp, so output is intentionally time-varying. There is no durable storage or configuration mutation.

## Dependencies and integration points

The simulator depends on DBus support (`gsh_dbus_*`), NFSv4 client and session hash tables, red-black tree/hash-table internals, SAL lookup functions, callback channel APIs, XDR NFSv4 callback structures, and Ganesha memory/logging helpers.

It integrates with the callback package as a consumer of `nfs_test_cb_chan`, `nfs_rpc_get_chan`, `alloc_rpc_call`, `cb_compound_init_v4`, `cb_compound_add_op`, and `nfs_rpc_call`. It is most useful when combined with a live server, active NFSv4 clients, and DBus administrative tooling.

## Risks and edge cases

The hash-table scans take write locks even though they only read entries, which can block concurrent client/session table operations more than necessary. The scans do not take per-client or per-session references, so they rely on partition locks preventing object removal during iteration.

The `get_session_ids` DBus descriptor declares the output array as `at` even though the method appends strings. That type-signature mismatch is a likely DBus API bug or stale descriptor.

`cbsim_fake_recall` is v4.0-oriented: it calls `nfs_rpc_get_chan` and constructs a callback compound with minor version 0 and a v4.0 callback identifier. It does not use `nfs_rpc_cb_single`, so it bypasses the v4.1 `CB_SEQUENCE` and slot-management path.

The fake recall uses a hard-coded default client ID and returns DBus success even if the test or recall fails internally. That is acceptable for a rough simulator but weak for automated diagnostics.

The synthetic `stateid.other` initializer uses escaped text that may not represent the intended raw bytes, and the fake file handle is a string rather than a real Ganesha file handle. The code itself notes a leak for the fake file-handle allocation.

## Test signals

Useful tests include DBus introspection/type validation, listing clients/sessions from controlled hash tables, base64 session ID formatting, error behavior for unknown client IDs, callback-channel test failures, fake recall dispatch success/failure, and memory accounting after repeated fake recalls.

Because this code is diagnostic, operational test signals are DBus method availability under `/org/ganesha/nfsd/CBSIM`, timestamp shape, array element types, logs from `cbsim_completion_func`, and no server crash when methods are called with missing, wrong-type, or stale client IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback_simulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_dispatcher_thread.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_dispatcher_thread.c

## Purpose

This file initializes and wires NFS-Ganesha's libntirpc service side. It allocates UDP/TCP/VSOCK/RDMA sockets, binds them to configured ports, creates `SVCXPRT` transports, registers service programs with rpcbind when enabled, creates TI-RPC event channels, dispatches rendezvous callbacks for each protocol, allocates/free per-request objects, and manages per-transport NFS custom data.

Despite the filename, the current implementation is event-channel and transport setup code rather than a hand-written dispatcher thread loop. It is the front door for NFS, MOUNT, NLM, RQUOTA, NFSACL, VSOCK NFS, and NFS/RDMA depending on build and runtime options.

## Important APIs, types, and functions

Public startup/shutdown functions include `nfs_Init_netconfig`, `nfs_Init_svc`, `Create_SVCXPRTs`, `Bind_sockets`, `Clean_RPC`, `nfs_Get_netconfig`, and `nfs_get_evchannel_id`.

Global transport state includes `rpc_evchan[EVCHAN_SIZE]`, `pdata[P_COUNT]`, four `netconfig_*` pointers, `udp_socket[P_COUNT]`, `tcp_socket[P_COUNT]`, `udp_xprt[P_COUNT]`, `tcp_xprt[P_COUNT]`, and runtime flags `v6disabled`, `vsock`, and `rdma`.

Protocol gating is handled by `nfs_protocol_enabled`. RPC unregistration uses `unregister` and `unregister_rpc`. Socket lifecycle uses `Allocate_sockets`, `Allocate_sockets_V4`, `alloc_socket_setopts`, `enable_udp_listener`, optional `allocate_socket_vsock`, `Bind_sockets_V6`, `Bind_sockets_V4`, optional `bind_sockets_vsock`, and `close_rpc_fd`.

Transport creation uses `Create_udp`, `Create_tcp`, and optional `Create_RDMA`. UDP rendezvous callbacks are listed in `udp_dispatch`; TCP/RDMA callbacks are listed in `tcp_dispatch`. Each callback sets `xprt->xp_dispatch.process_cb` to the relevant validator (`nfs_rpc_valid_NFS`, `nfs_rpc_valid_MNT`, `nfs_rpc_valid_NLM`, `nfs_rpc_valid_RQUOTA`, `nfs_rpc_valid_NFSACL`, `nfs_rpc_valid_NFS_RDMA`) and returns the libntirpc status/receive result.

Per-transport data hooks are `nfs_rpc_alloc_user_data`, `nfs_rpc_free_user_data`, and `nfs_rpc_unref_user_data`. Per-request hooks supplied to `svc_init` are `alloc_nfs_request` and `free_nfs_request`.

Rpcbind registration is guarded by `RPCBIND` and uses `__Register_program`/`Register_program` plus `UDP_REGISTER` and `TCP_REGISTER` macros.

## Control flow

`nfs_Init_netconfig` must run before registration. It obtains `udp`, `tcp`, optional `udp6`, and optional `tcp6` entries from `/etc/netconfig`, logging fatal errors for missing IPv4 UDP/TCP and informational messages for missing IPv6 entries.

`nfs_Init_svc` configures `svc_init_params` from `nfs_param.core_param.rpc`: maximum connections, max events, send buffer, number of event channels, idle timeout, IOQ thread bounds, GSS context cache settings, optional pthread stack size, and optional RDMA limits. It calls `svc_init`, creates `EVCHAN_SIZE` event channels with `svc_rqst_new_evchan`, allocates sockets, binds them, unregisters stale rpcbind mappings, creates listening transports, and registers services with rpcbind when compiled in.

Socket allocation prefers IPv6 unless disabled by platform/runtime failure. For each enabled protocol, it optionally creates a UDP socket if `enable_udp_listener` permits it and always creates a TCP socket. `EAFNOSUPPORT` on IPv6 causes fallback to IPv4. `alloc_socket_setopts` applies `SO_REUSEADDR`, TCP keepalive options, UDP nonblocking mode, and optional `SO_BINDTODEVICE`.

Binding uses either IPv6 or IPv4 based on `v6disabled`, fills `proto_data` sockaddr/netbuf/t_bind structures, and binds each enabled protocol socket to `nfs_param.core_param.bind_addr` and `nfs_param.core_param.port[p]`. VSOCK binding is separate and nonfatal on failure.

Transport creation wraps sockets in libntirpc service transports. UDP uses `svc_dg_create` and registers with `UDP_UREG_CHAN`. TCP uses `svc_vc_ncreatef` with close/listen flags and registers with `TCP_UREG_CHAN`. RDMA uses `svc_rdma_create` with `rpc_rdma_xa`. All transports install `SVCSET_XP_FREE_USER_DATA`; TCP NFS connections additionally allocate NFS user data, install `SVCSET_XP_UNREF_USER_DATA`, initialize the connection manager, and set a `remote_addr_set_cb`.

Incoming request allocation is performed by libntirpc through `alloc_nfs_request`. It allocates `nfs_request_t`, references the transport, records XDR and transport pointers, initializes request reference count and duplicate-request queue linkage, increments health and metrics counters, and returns `&reqdata->svc`. `free_nfs_request` logs decode status, frees the request, releases the transport, increments dequeue counters, and records RPC completion metrics.

Shutdown through `Clean_RPC` unregisters programs, closes/destroys sockets and transports, and frees netconfig entries. The comment says it must be called only from the shutdown thread.

## State and persistence behavior

All state is process runtime state. Socket file descriptors and transport pointers are global arrays keyed by `protos`. Netconfig entries are cached globally until `Clean_RPC`. Event-channel IDs are cached in `rpc_evchan` and exposed by `nfs_get_evchannel_id`.

Per-transport custom data is attached to `SVCXPRT` internals through `init_custom_data_for_xprt`, duplicate request cache storage in `xp_u2`, connection-manager state, and later dissociation/destruction hooks. `nfs_rpc_free_user_data` releases any duplicate request cache with `nfs_dupreq_put_drc`, marks the connection finished, and destroys custom data.

Per-request state is allocated per decoded RPC request and persists until libntirpc calls the free hook. Health counters (`nfs_health_.enqueued_reqs`, `dequeued_reqs`) and monitoring counters track in-flight RPCs and completions.

RDMA configuration mutates the global `rpc_rdma_xa`, including assigning `port` with `strdup` and setting credits from config. There is no corresponding free in this file, so it is effectively process-lifetime state.

## Dependencies and integration points

This file depends heavily on libntirpc service APIs, rpcbind/netconfig APIs, POSIX sockets, protocol-specific NFS validators and dispatch functions, NFS core parameters, duplicate request cache code, transport custom-data helpers, connection manager hooks, LTTng tracepoints, and metrics.

Compile-time integration is broad: `_USE_NFS3`, `_USE_NLM`, `_USE_RQUOTA`, `USE_NFSACL3`, `RPC_VSOCK`, `_USE_NFS_RDMA`, `RPCBIND`, `__APPLE__`, and `__FreeBSD__` alter protocol lists, socket options, registration, and platform behavior.

Runtime integration is controlled by `NFS_options`, `nfs_param.core_param.enable_*` flags, UDP listener bitmasks, port arrays, bind address, RPC buffer sizes, TCP keepalive settings, max connection limits, and RDMA settings.

## Risks and edge cases

IPv4 binding code reuses members named `netbuf_udp6`, `bindaddr_udp6`, and `si_udp6` for IPv4 addresses. That is intentional storage reuse but confusing and error-prone; log messages in some IPv4 paths also mention `udp6`.

IPv6 fallback is global. Once one protocol observes `EAFNOSUPPORT`, `v6disabled` becomes true and later protocols allocate IPv4 sockets. Mixed IPv4/IPv6 behavior is not attempted.

`close_rpc_fd` closes raw sockets and then destroys transports, but `svc_vc_ncreatef` uses `SVC_CREATE_FLAG_CLOSE`; ownership assumptions must be correct to avoid double close. The existing order is longstanding but should be verified when changing libntirpc ownership flags.

`alloc_socket_setopts` applies `SO_BINDTODEVICE` only to TCP sockets, not UDP sockets. If interface binding is expected for UDP services too, this is a behavioral gap.

VSOCK bind failure is logged as major but startup continues. Deployments that requested VSOCK may need explicit health checks to notice that no VSOCK listener exists.

Rpcbind registration failure is fatal for v3-era services through `Register_program` but nonfatal for the optional v4 registration path using `__Register_program`. That matches NFSv4 rpcbind optionality but can surprise tests expecting uniform failure behavior.

Request health metrics depend on every allocated request reaching `free_nfs_request`. Decoder or transport paths that bypass the free hook would leave in-flight counts elevated.

## Test signals

Useful tests include netconfig lookup failures, IPv6 success and fallback to IPv4, UDP listener bitmask combinations, TCP keepalive option application, interface binding, socket bind failures, VSOCK requested/unavailable behavior, RDMA enabled/disabled behavior, rpcbind registration success/failure, and `Clean_RPC` resource cleanup.

Runtime integration tests should assert that each enabled protocol has the expected UDP/TCP transports, event channels are created and registered, `process_cb` is set to the correct validator after rendezvous, connection-manager hooks run on TCP NFS connections, duplicate request cache user data is freed, and request metrics balance enqueued/dequeued counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_dispatcher_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_tcp_socket_manager_thread.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_tcp_socket_manager_thread.c

## Purpose

This file is a legacy placeholder for the old TCP socket manager thread implementation. Its header comment says it once contained the `rpc_tcp_socket_manager_thread` routine and related support code, but the active body contains only includes and an `#if 0` comment noting the routine was used in a prior rendezvous-request design that spawned a dedicated thread for each client connection.

In the current tree, TCP socket and transport management lives in `nfs_rpc_dispatcher_thread.c` and libntirpc event-channel machinery, not in this file.

## Important APIs, types, and functions

There are no functions, exported symbols, global variables, or active types defined in this source file. The included headers (`hashtable.h`, `log.h`, `nfs23.h`, `nfs4.h`, `mount.h`, `nfs_core.h`, `nfs_exports.h`, `nfs_proto_functions.h`, `nfs_file_handle.h`) are unused by active code.

The only active preprocessor construct after includes is `#if 0`, containing a historical note. No code inside it is compiled.

## Control flow

There is no runtime control flow. If compiled, this translation unit contributes no executable behavior beyond satisfying build-system expectations for the source file's presence.

## State and persistence behavior

The file owns no state and mutates no persistent or runtime structures. It has no side effects.

## Dependencies and integration points

The practical integration point is the build system: this file may remain listed among MainNFSD sources for compatibility or to preserve historical layout. Any actual TCP RPC dispatch integration should be researched in `nfs_rpc_dispatcher_thread.c`, `xprt_handler`, `connection_manager`, and libntirpc event-channel setup.

Because the file includes many project headers without using their declarations, changes in those headers can still affect compilation time or warning behavior for this otherwise empty translation unit.

## Risks and edge cases

The main risk is confusion. Developers may search for the TCP socket manager thread and land here, but the implementation has been removed. Adding new logic here would likely duplicate or conflict with the event-driven dispatcher model.

If the build enables strict warnings for unused includes or empty translation units, this file could become noisy. Otherwise it is low-risk.

## Test signals

There are no direct behavioral tests for this file. Build success is the only meaningful signal. Any tests for TCP listener allocation, accepted connections, event-channel registration, and request dispatch should target `nfs_rpc_dispatcher_thread.c` and libntirpc integration instead.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_tcp_socket_manager_thread.c -->
