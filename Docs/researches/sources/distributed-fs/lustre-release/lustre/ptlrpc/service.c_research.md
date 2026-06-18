# sources/distributed-fs/lustre-release/lustre/ptlrpc/service.c

## Purpose

`service.c` is the server-side core of Lustre PTLRPC. It registers and unregisters RPC services on LNet portals, owns per-service CPU partition state, allocates and posts receive buffers, transforms incoming network messages into `ptlrpc_request` objects, schedules them through normal and high-priority NRS queues, runs service kthreads that invoke target request handlers, manages adaptive timeout early replies, tracks client export deadlines for eviction, and drains "difficult" reply states after client ACK or transaction commit.

The file is infrastructure rather than a filesystem operation handler. Concrete services supply `struct ptlrpc_service_conf` and `srv_ops` callbacks, especially `so_req_handler`, optional thread init/done hooks, and optional high-priority request classification. This file supplies the common concurrency, timeout, buffer, reply, and lifecycle machinery around those callbacks.

## Important APIs, Types, And Functions

Public service lifecycle APIs are `ptlrpc_register_service()`, `ptlrpc_unregister_service()`, `ptlrpc_service_health_check()`, and `ptlrpc_server_get_timeout()`. `ptlrpc_register_service()` validates configuration, selects CPU partitions, allocates `struct ptlrpc_service` plus `struct ptlrpc_service_part` instances, initializes adaptive-timeout arrays and request buffers, registers sysfs/debugfs/lprocfs/NRS state, sets the LNet request portal lazy, and starts service threads. `ptlrpc_unregister_service()` marks the service stopping, removes it from `ptlrpc_all_services`, stops timers and threads, unlinks posted request buffers, purges queues and reply states, cleans NRS and debug/sysfs state, then frees memory.

Request-buffer management is handled by `ptlrpc_alloc_rqbd()`, `ptlrpc_free_rqbd()`, `ptlrpc_grow_req_bufs()`, `ptlrpc_server_post_idle_rqbds()`, `ptlrpc_check_rqbd_pool()`, and teardown helpers. `struct ptlrpc_request_buffer_desc` instances move among idle, posted, and history lists; each owns a large LNet receive buffer and an embedded request for the common path.

Reply ACK and commit handling uses `struct ptlrpc_reply_state`, `struct ptlrpc_hr_service`, `struct ptlrpc_hr_partition`, `struct ptlrpc_hr_thread`, and `struct rs_batch`. `ptlrpc_save_lock()` marks reply states difficult by saving LDLM lock handles that must be decref'd after ACK/commit. `ptlrpc_dispatch_difficult_reply()`, `ptlrpc_schedule_difficult_reply()`, `ptlrpc_commit_replies()`, and `ptlrpc_handle_rs()` move committed or ACKed reply states to dedicated reply-handler threads and release network MDs, export refs, reply refs, and saved locks.

Incoming request preparation is split from execution. `ptlrpc_server_handle_req_in()` dequeues raw requests from `scp_req_incoming`, unwraps security, unpacks Lustre message headers and PTLRPC body, validates request type/opcode/export/security flavor, updates export timers, computes deadlines, initializes request session context, registers the request in adaptive-timeout tracking, captures reply match bits, and adds the request to NRS queues through `ptlrpc_server_request_add()`. `ptlrpc_server_handle_request()` later fetches a scheduled request, updates stats, revalidates export state, drops expired requests, binds the request session to the executing thread, calls `svc->srv_ops.so_req_handler(request)`, records timing, and finalizes active request accounting.

High-priority scheduling is implemented by `ptlrpc_hpreq_handler()`, `ptlrpc_server_hpreq_init()`, `ptlrpc_server_hpreq_fini()`, `ptlrpc_server_allow_high()`, `ptlrpc_server_allow_normal()`, `ptlrpc_server_request_pending()`, and `ptlrpc_server_request_get()`. High-priority classification is service- and request-op specific; reconnect/ping-like operations can use `ptlrpc_hpreq_common`, and services can provide `so_hpreq_handler`.

Adaptive timeout support centers on `ptlrpc_at_add_timed()`, `ptlrpc_at_remove_timed()`, `ptlrpc_at_set_timer()`, `ptlrpc_at_timer()`, `ptlrpc_at_check_timed()`, and `ptlrpc_at_send_early_reply()`. Requests are bucketed by deadline in a circular `ptlrpc_at_array`; timer expiry sends early replies for near-deadline work, extends server/client deadlines, and requeues requests when successful.

Export timeout and eviction helpers include `ptlrpc_export_timeout()`, `ptlrpc_export_prolong_timeout()`, `ptlrpc_export_pinger_timeout()`, `ptlrpc_export_extra_timeout()`, and `ptlrpc_update_export_timer()`. They combine adaptive service estimates, reverse-import network latency, ping intervals, reconnect time, and recovery state to refresh export deadlines or trigger the ping evictor.

Thread management uses `ptlrpc_server_nthreads_check()`, `ptlrpc_start_threads()`, `ptlrpc_start_thread()`, `ptlrpc_main()`, `ptlrpc_svcpt_stop_threads()`, `ptlrpc_stop_all_threads()`, `ptlrpc_thread_should_stop()`, and watchdog helpers. Dedicated difficult-reply workers are initialized by `ptlrpc_hr_init()`, started by `ptlrpc_start_hr_threads()`, stopped by `ptlrpc_stop_hr_threads()`, and finalized by `ptlrpc_hr_fini()`.

## Control Flow

Service registration begins with a configuration-derived topology. `ptlrpc_register_service()` chooses the CPT table, parses an optional CPT pattern, allocates a variable-sized service object with one part per selected partition, fills portal/buffer/reply/thread fields, rounds buffer and reply limits to powers of two, and initializes each service part. `ptlrpc_service_part_init()` creates all queue heads and locks, allocates adaptive-timeout bucket arrays sized from `at_max`, initializes AT estimates, sets `scp_service`, and preallocates request buffers without posting them. After sysfs/debugfs/NRS setup, `ptlrpc_start_threads()` creates initial kthreads per service part.

Each service thread runs `ptlrpc_main()`. Startup binds to the configured CPU partition if requested, clears supplementary groups, runs service-specific thread initialization, allocates a Lustre environment, initializes a server context, posts all idle receive buffers to LNet, allocates one idle reply-state buffer, transitions from `SVC_STARTING` to `SVC_RUNNING`, and arms the watchdog. Its main loop waits for stop, incoming raw requests, scheduled NRS requests, idle buffers to post, or adaptive-timeout checks.

The service loop prioritizes fast intake. After wakeup, it checks request-buffer pressure, may spawn an additional thread if active work consumes the pool, resets/refills the LU environment, processes one incoming raw request, handles adaptive-timeout early replies, processes one scheduled request, reposts idle buffers, and self-stops if thread limits were reduced. A small counter lets the loop continue handling bursts of raw incoming requests up to a flood limit before moving to execution work.

Incoming requests are produced by the LNet receive callback path outside this file and placed on `scp_req_incoming`. `ptlrpc_server_handle_req_in()` converts one such entry into a schedulable request. Errors before scheduling go through `ptlrpc_server_finish_request()` so AT links, HP/export lists, refs, and request-buffer state are unwound consistently. Successful requests are added to export RPC lists and NRS queues in `ptlrpc_server_request_add()`, which also handles duplicate `MSG_RESENT` XIDs, increasing-XID slot obsolescence for server builds, LDLM cancel duplicate-scan avoidance, deadline transfer to an already-processing original, and export RPC accounting.

Scheduled execution starts with `ptlrpc_server_request_get()`. Under `scp_req_lock`, high-priority work is preferred when allowed, but `srv_hpreq_ratio`, current active counts, HP throttling, normal throttling, and reserved idle thread capacity prevent HP work from starving normal requests or consuming all threads. The selected request increments active counters and export RPC accounting, then `ptlrpc_server_handle_request()` invokes the service callback. Completion removes the request from NRS active state, decrements active counts and export RPC accounting, finalizes NRS state, performs HP cleanup, and drops the request reference.

Adaptive timeouts run concurrently with normal request processing. `ptlrpc_at_add_timed()` inserts AT-capable requests into deadline buckets unless AT is disabled, the request expects no reply, or the message lacks AT support. `ptlrpc_at_check_timed()` is triggered by `scp_at_timer`, extracts all requests whose deadline falls within `at_early_margin`, temporarily takes references, sends early replies outside the AT lock, re-adds requests whose early reply succeeded, and drops the temporary references. `ptlrpc_at_send_early_reply()` clones enough request state to pack and send a `LPRFL_EARLY_REPLY`, obtains an export from the request handle, sends through the normal reply path, and updates the original request deadline and early-reply count.

Difficult replies are decoupled from service threads. Commit callbacks call `ptlrpc_commit_replies()` to batch reply states whose transaction number is covered by `exp_last_committed`; client ACK or other notification paths call `ptlrpc_dispatch_difficult_reply()` or `ptlrpc_schedule_difficult_reply()`. Batches are assigned to reply-handler threads by service-part CPT affinity when possible, otherwise round-robin across HR partitions. `ptlrpc_hr_main()` drains queued reply states and calls `ptlrpc_handle_rs()`, which removes uncommitted/export-list links, unlinks network MDs when needed, decrefs saved LDLM locks, drops export and reply-state refs once the reply is off the network, and wakes service teardown if the last difficult reply drains.

Teardown reverses startup in a strict order. `ptlrpc_unregister_service()` marks stopping first so new threads and service loops exit. It deletes AT timers, stops all service kthreads, clears the lazy portal and unlinks posted receive MDs, waits for LNet to release posted buffers, schedules active difficult reply states, purges incoming and NRS-queued requests, waits for shared-portal posted buffers to disappear, frees idle request buffers and idle reply states, then tears down NRS, debug/sysfs registration, AT arrays, service parts, CPT pattern arrays, and the service object.

## State And Persistence Behavior

The file manages volatile kernel state only; it does not write filesystem metadata directly. Its durable effects happen through target handlers called via `so_req_handler()` or through LDLM/export side effects. State is nevertheless long-lived at runtime: global `ptlrpc_all_services`, per-service portal and thread configuration, per-service-part queues and counters, request-buffer pools, NRS queues, adaptive-timeout arrays, difficult-reply lists, export RPC lists, and reply-handler partitions.

Request-buffer descriptors persist across many RPCs. After all requests referencing an rqbd are dropped, the rqbd moves into history (`scp_hist_rqbds`) so recent requests remain inspectable. History is bounded by `srv_hist_nrqbds_cpt_max`; culling removes request history entries, tracks `scp_hist_seq_culled`, frees per-request memory, and either recycles or frees the rqbd depending on posted count, configured maximum, and `test_req_buffer_pressure`.

Request lifetime is refcounted. `ptlrpc_server_drop_request()` removes session context, unlinks adaptive-timeout state, drops export references, attaches the request back to its rqbd, and frees or preserves it through history depending on rqbd refcount and preallocated reply-state pressure. It deliberately avoids freeing reply state before request refs are gone because debug paths inspect reply state while a valid request ref exists.

Export state is updated but owned elsewhere. Requests carry export refs from `class_conn2export()` or `class_export_get()`, are linked into `exp_reg_rpcs` or `exp_hp_rpcs`, set or clear `exp_used_slots` bits for tagged requests, increment/decrement export RPC counters, and refresh `exp_deadline` in the OBD timed-export chain. Stale or invalid replay/transno conditions call `class_fail_export()`, while eviction timing may wake the ping evictor.

Adaptive timeout state is per service part: `scp_at_estimate` records service-time estimates, `scp_at_array` maps deadlines to lists and counts, and `scp_at_timer` schedules early-reply scans. Early replies mutate in-memory deadlines and update the AT estimate via `obd_at_measure()` unless recovery rules apply. No AT state is persisted across service restart.

Thread state is dynamic. Service thread counts can grow under load up to `srv_nthrs_cpt_limit` and shrink when thread limits are reduced. `scp_nthrs_running`, `scp_nthrs_starting`, `scp_thr_nextid`, and contiguous IDs are guarded by `scp_lock`. Watchdog delayed work stores the last touch time and emits stack traces for long-running or stuck service threads.

## Dependencies And Integration Points

The file depends on Linux kernel kthreads, wait queues, timers, delayed work, spinlocks, mutexes, atomics, CPU topology, rate limiting, groups/credentials, and LNet MD unlink/register APIs. Lustre dependencies include `lustre_net.h`, `obd_class.h`, `obd_support.h`, `lu_object.h`, `ptlrpc_internal.h`, security policy wrappers, request capsules/message accessors, NRS scheduling, LDLM locks, adaptive timeout helpers, lprocfs counters, sysfs/debugfs registration, and OBD export/import timeout state.

`ptlrpc_register_rqbd()` and reply send/unlink behavior integrate with `niobuf.c` and LNet callbacks. `sptlrpc_svc_unwrap_request()`, `sptlrpc_svc_ctx_addref()`, `sptlrpc_svc_ctx_decref()`, and `sptlrpc_target_export_check()` integrate with PTLRPC security policies. `ptlrpc_nrs_*()` calls integrate with request scheduling policies such as regular/HP, TBF, ORR, and CRR. `lustre_pack_reply_flags()`, `ptlrpc_send_reply()`, `target_send_reply()`, `ptlrpc_error()`, and `ptlrpc_req_drop_rs()` integrate with the common reply path.

Service owners integrate by supplying `struct ptlrpc_service_conf`: buffer portal IDs and sizes, thread naming/count policy, CPT affinity, watchdog factor, context tags, and operation callbacks. The file exports `ptlrpc_save_lock()`, `ptlrpc_schedule_difficult_reply()`, `ptlrpc_hpreq_handler()`, service lifecycle APIs, and health-check APIs for other Lustre modules.

Test and fault-injection integration is pervasive through `CFS_FAIL_CHECK`, `CFS_FAIL_PRECHECK`, `CFS_FAIL_TIMEOUT`, and named failpoints such as request drops, resend races, HP timeout behavior, thread over-creation, replay reconnect, and enqueue resend. Several warning strings are explicitly referenced by Lustre test scripts in comments.

## Risks And Edge Cases

Lock ordering is critical. Reply batching explicitly warns about spinlock ordering across export uncommitted-reply locks, service-part reply locks, and reply-state locks. Request scheduling crosses `scp_lock`, `scp_req_lock`, export `exp_rpc_lock`, request `rq_lock`, and AT locks. Changes that add callbacks or allocations while holding these locks can introduce deadlocks or long interrupt-disabled sections.

Request refcount and rqbd history interactions are fragile. A request can be represented by an embedded rqbd request or separately allocated cache request; freeing must match that distinction. AT timeout scanning takes temporary refs with `atomic_inc_not_zero()` because completion can race timer processing. Duplicate resend handling updates the original request's deadline and match bits while avoiding slot cleanup on the duplicate by marking it obsolete.

Adaptive timeout behavior has several boundary cases: messages without `MSGHDR_AT_SUPPORT`, zero client timeout, requests marked `rq_no_reply`, deadlines already in the past, AT disabled per OBD, recovery replay timing, and inability to extend beyond adaptive maximum. Failure to re-add or remove timed entries correctly can either leak timer-list entries or stop early replies.

High-priority handling can starve normal work if ratios and active counts are wrong. Conversely, too strict HP gating can delay reconnects, pings, or lock-cancel flows that are needed for recovery. The code reserves thread capacity and resets `scp_hreq_count` on normal work; tests should cover mixed HP/normal queues under throttling and fail-injected cancel resend.

Service teardown must account for shared portals. `ptlrpc_service_purge_all()` waits for posted rqbd lists to empty because another target sharing the portal may still reference a request buffer. Incorrect teardown ordering could free buffers still visible to LNet callbacks or leave difficult replies holding export refs.

Thread scaling has ID-contiguity assumptions. `ptlrpc_start_thread()` serializes thread creation because some modules require unique contiguous IDs, and dynamic stopping only stops the highest-numbered thread. Races during service stop, failed `kthread_run()`, or limit reduction need to preserve `scp_nthrs_starting`, `scp_nthrs_running`, and list membership.

Health checks are intentionally non-aggressive and can return healthy for idle services even after long idle periods. They inspect only pending queued requests and compare request wait/service wait against adaptive max and `at_unhealthy_factor`, skipping unhealthy status during recovery.

## Test Signals

Useful coverage includes service registration/unregistration with and without CPT affinity, invalid CPU-bind or CPT pattern inputs, buffer-size rounding, request-buffer allocation failure, LNet post/unlink failure paths, shared-portal teardown waits, and `test_req_buffer_pressure` behavior.

Request-path tests should cover valid requests, bad message type, failed security unwrap, illegal security flavor, unknown or failed export, old connection count, invalid replay/transno outside recovery, zero timeout, bulk read/write opcode classification, `OBD_CONNECT2_REP_MBITS`, duplicate `MSG_RESENT` XID while original is active, increasing-XID slot obsolescence, LDLM cancel duplicate-scan bypass, and normal error reply generation.

Scheduling tests should exercise NRS normal and HP queues, HP ratio enforcement, throttling hooks, dynamic thread creation under load, thread shrink after lowering limits, and service-specific `so_hpreq_handler` or request `hpreq_check` returning normal, HP, stale, and error outcomes.

Adaptive-timeout tests should verify timer arming/disarming, bucket wraparound, early reply send success, early reply allocation failure, no-AT clients, AT disabled, `rq_no_reply`, already-expired requests, recovery replay early reply spacing, requeue after successful early reply, and warning output when early replies are late.

Difficult-reply tests should cover reply ACK dispatch, transaction commit batching up to `MAX_SCHEDULED`, lock decref after commit/ACK, races with send completion and MD unlink, `rs_unlinked` final cleanup, service teardown waiting for `scp_nreps_difficult`, and CPT-affine HR thread selection.

Operational signals include lprocfs counters for wait time, queue depth, active requests, timeout estimate, request-buffer availability, per-op latency, console watchdog warnings, slow `req_in` warnings, late early-reply warnings, and health-check warnings/errors.
