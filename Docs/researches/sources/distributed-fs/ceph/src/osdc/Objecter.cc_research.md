# sources/distributed-fs/ceph/src/osdc/Objecter.cc

## Purpose

`Objecter.cc` implements Ceph's client-side OSD request engine. It is the component that maps object, PG, watch/notify, pool, statfs, and OSD command requests onto current OSDMap state, sends the matching wire messages, tracks in-flight state, processes replies, and resubmits or fails operations when maps, sessions, pool state, or backoff state change.

The file is not a persistent-storage implementation itself. Its persistent view of the cluster is derived from OSDMap, pool metadata, and monitor replies; its own state is volatile per-client request/session state. It is central to librados and higher clients because most object operations pass through `Objecter::op_submit()`, `Objecter::_calc_target()`, `Objecter::_send_op()`, and `Objecter::handle_osd_op_reply()`.

## Important APIs, Types, and Functions

- `Objecter::init()`, `start()`, `shutdown()`, destructor: lifecycle, perf counter registration, admin socket registration, config observer setup, tick scheduling, session/request cleanup, and invariant checks.
- `Objecter::op_submit()`, `_op_submit_with_budget()`, `_op_submit()`: public-to-internal OSD op submission. They enforce throttle budget, optional timeout, split-read handling, target calculation, session assignment, map-check setup, and first send.
- `Objecter::_calc_target(op_target_t*, bool)`: maps an object locator and flags to pool, PG, acting set, primary or replica OSD, pause/full status, erasure-coded shard identity, and resend decisions.
- `Objecter::_prepare_osd_op()` and `_send_op()`: build `MOSDOp`, set flags, snap context, priority, retry attempt, tracing, data metrics, honor OSD backoff ranges, and send on the session connection.
- `Objecter::handle_osd_op_reply()` and `complete_op_reply()`: validate reply connection and retry attempt, handle redirects and `-EAGAIN`, copy or claim output data, run per-subop handlers, update metrics, serialize completions by object hash, and retire the op.
- `Objecter::handle_osd_map()` and `_scan_requests()`: apply full or incremental OSD maps, emit blocklist events, prune PG mapping cache, close stale sessions, move/resend/fail ops, linger ops, and command ops, and release callbacks waiting on map epochs.
- `LingerOp` paths: `linger_register()`, `linger_watch()`, `linger_notify()`, `_linger_submit()`, `_send_linger()`, `_linger_commit()`, `_linger_reconnect()`, `_send_linger_ping()`, `handle_watch_notify()`, and `_linger_cancel()` implement watch/notify registration, reconnect, ping validity checks, disconnect delivery, and cancellation.
- Monitor-side operations: pool snapshots and pools use `PoolOp` via `pool_op_submit()` and `handle_pool_op_reply()`; stats use `PoolStatOp` and `StatfsOp`; command paths use `CommandOp`, `submit_command()`, `_calc_command_target()`, `_send_command()`, and `handle_command_reply()`.
- Listing/enumeration: `list_nobjects()`, `_nlist_reply()`, `enumerate_objects<T>()`, `_issue_enumerate<T>()`, and `_enumerate_reply<T>()` implement PG listing and range-bounded bitwise object enumeration for librados and neorados entry types.
- Session helpers: `_get_session()`, `close_session()`, `_reopen_session()`, `_kick_requests()`, `_session_*_assign/remove()` manage `OSDSession` ownership, connection private data, homeless reassignment, and resend queues.
- Diagnostic APIs: `dump_requests()`, `dump_ops()`, `dump_linger_ops()`, `dump_command_ops()`, pool/stat dump helpers, and `RequestStateHook` expose active request state through the `objecter_requests` admin socket command.

## Control Flow

Normal object operation flow:

1. A caller builds an `Op` from an `ObjectOperation` and calls `op_submit()`.
2. `_op_submit_with_budget()` validates vector sizes, takes throttle budget, arms an OSD timeout if configured, and lets `SplitOp::create()` split qualifying direct/replica reads.
3. `_op_submit()` calculates the target unless direct read targeting was already calculated, handles pool DNE/EIO preconditions, obtains or creates an `OSDSession`, accounts metrics, assigns a TID, stores the op in the session, installs Asio cancellation support, sends immediately if not paused/homeless, and sends a monitor map-version check when pool existence is uncertain.
4. `_send_op()` checks OSD backoff intervals before building and sending `MOSDOp`.
5. `handle_osd_op_reply()` finds the session from `Connection::get_priv()`, rejects stale/stray attempts, redrives redirects and retryable `-EAGAIN`, fills caller output buffers/results, runs subop handlers, and completes the op.

OSDMap update flow:

1. `ms_dispatch2()` routes `CEPH_MSG_OSD_MAP` to `handle_osd_map()`.
2. Incremental maps are preferred; full maps are used for first maps or gaps. Missing untrimmed epochs trigger `_maybe_request_map()`, while trimmed gaps mark `skipped_map`.
3. After each applied epoch, `_scan_requests()` recalculates linger, normal op, and command targets. Changed, skipped, unpaused, full-state, split/merge, pool-DNE, and pool-EIO cases are separated into resend, map-check, failure, or unregister paths.
4. Sessions whose OSD is down or whose address changed are closed; outstanding work is moved to the homeless session until remapped.
5. Resend lists are reattached to current sessions and resent unless paused, homeless, or explicitly non-resendable.

Watch/notify flow:

1. `linger_register()` allocates a stable `linger_id` and cookie-compatible pointer tracking entry.
2. `linger_watch()` or `linger_notify()` stores ops, snap context, callbacks, and a budget, then `_linger_submit()` maps and assigns the linger op to a session.
3. `_send_linger()` sends either the first registration op or a reconnect watch op and records `register_tid`.
4. Watch disconnects, notify completions, and notify events arrive as `MWatchNotify`; the objecter normalizes delete/reconnect races into `ENOTCONN` and dispatches user callbacks on the proper executor or finish strand.
5. `tick()` pings active registered watches; ping replies update `watch_valid_thru` or report watch failure.

Monitor operation flow:

Pool, pool-stat, and statfs requests are stored in maps by TID, sent to the monitor, retried by `resend_mon_ops()` after monitor reconnect, optionally timed out, and completed when matching replies arrive. Pool-op callbacks may be deferred until the client has reached the reply's required OSDMap epoch.

## State and Persistence Behavior

The primary volatile state is protected by `rwlock` plus per-session shared mutexes:

- `osdmap`: current client view of cluster topology, pool flags, PG mapping, pause/full flags, and feature flags.
- `osd_sessions`: active OSD sessions keyed by OSD id. `homeless_session` stores ops that cannot currently be mapped to an up OSD. `splitop_session` stores parent split operations.
- `OSDSession::{ops, linger_ops, command_ops}`: in-flight normal ops, watch/notify registrations, and OSD commands.
- `pool_ops`, `poolstat_ops`, `statfs_ops`: monitor-directed in-flight operations.
- `check_latest_map_ops`, `check_latest_map_lingers`, `check_latest_map_commands`: operations waiting for monitor-confirmed latest map bounds before concluding pool/OSD DNE.
- `waiting_for_map`: callbacks blocked on reaching specific OSDMap epochs.
- `linger_ops` and `linger_ops_set`: global linger lookup by id and cookie/pointer validation.
- `pg_mapping` cache accessed through `lookup_pg_mapping()`, `update_pg_mapping()`, and `prune_pg_mapping()` to avoid repeated OSDMap PG acting calculations.
- Counters and budget fields: `last_tid`, `max_linger_id`, `num_in_flight`, `inflight_ops`, `num_homeless_ops`, throttles, timeout events, and perf counters.

No request state is durable across process restart. Persistence enters through messages and maps from mons/OSDs: OSDMap epochs, pool metadata, snap metadata, stats versions, and object operation results. Timers, callbacks, sessions, throttle budgets, and backoff tables are in-memory and are explicitly cleaned up at shutdown.

## Dependencies and Integration Points

- OSD topology and placement: `OSDMap`, `pg_pool_t`, `PastIntervals`, CRUSH locality, pool flags, PG split/merge helpers, erasure-coded shard helpers.
- Wire protocol: `MOSDOp`, `MOSDOpReply`, `MOSDBackoff`, `MOSDMap`, `MWatchNotify`, `MPoolOp`, `MPoolOpReply`, `MGetPoolStats`, `MStatfs`, `MCommand`, and monitor command messages.
- Messaging: `Messenger`, `Connection`, `Dispatcher::ms_dispatch2()`, connection reset/connect/refused callbacks, and connection private `OSDSession` references.
- Monitors: `MonClient` subscriptions, `get_version("osdmap")`, monitor message sends, and fsid validation.
- Async and callback execution: Boost.Asio executors, strands, cancellation slots, `ceph::async::waiter`, timer callbacks, and deferred completions.
- Client layers: `ObjectOperation`, `Filer`, `Striper`, librados list/scrub types, neorados enumeration entries, and `SplitOp` for split direct reads.
- Observability: Ceph perf counters, admin socket `objecter_requests`, tracing/Zipkin/OpenTelemetry context propagation, and debug inject config options.

## Risks and Edge Cases

- Locking is intricate. Many paths hold `rwlock` and then session locks; map handling deliberately moves operations between sessions while holding the write lock. Any new callback or lock acquisition must avoid lock inversion with session locks, `watch_lock`, timer callbacks, and admin-socket dumps.
- Reply validity depends on both TID and connection/session incarnation. Stale replies, retry-attempt mismatches, redirects, and reset races are explicitly filtered; bypassing those checks risks duplicate or out-of-order completion.
- Pool deletion and pool-never-existed handling are intentionally delayed until a latest-map bound is known. Returning `ENOENT` too early can mis-handle races with map delivery.
- Full, pause, EIO, epoch barrier, and pool full flags affect whether ops are sent, resent, failed, or left homeless. Write paths especially must respect `honor_pool_full` and `respects_full()`.
- Replica/direct read behavior is subtle: balanced/localized reads may go to replicas, `-EAGAIN` clears direct-read and forced-OSD flags unless `FAIL_ON_EAGAIN` is set, and split reads use `splitop_session`.
- Watch/notify callbacks race with reconnect, delete, disconnect, cancel, and duplicate notify completion. `last_error`, `register_gen`, `watch_valid_thru`, and one-shot callback nulling are safety-critical.
- Backoff ranges suppress sends without moving ops out of the session. Unblock handling must resend only contained operations and preserve OSD backoff IDs/ranges.
- Completion handlers can throw; `process_op_reply_handlers()` maps handler failures into operation completion errors and updates per-op result pointers.
- Timeout cancellation and normal completion both retire ops; `_finish_op()`, `_finish_command()`, and monitor finish helpers must cancel timers only when appropriate and return budgets exactly once.
- Enumeration depends on `CEPH_OSDMAP_SORTBITWISE`; list paths must restart or adjust cursors when PG count or sort order changes.

## Test Signals

Useful signals for tests and debugging include:

- Perf counters: `op_active`, `op_send`, `op_resend`, `op_reply`, `op_latency`, `op_inflight`, linger/pool/statfs/command active and resend counters, map full/inc counters, OSD session open/close, replica-read counters, and `split_op_reads`.
- Admin socket: `objecter_requests` should show active ops, linger ops, pool ops, statfs ops, pool-stat ops, and command ops with TIDs, targets, ages, attempts, and session OSDs.
- Map-change scenarios: OSD down/up, address change, PG split/merge, missing map epoch, pool deletion, pool EIO flag, pause/full flags, and epoch barrier should cause expected homeless assignment, map subscriptions, resends, or completion errors.
- Reply scenarios: stale retry attempts should be ignored, redirect replies should resubmit with redirected locator flags, retryable `-EAGAIN` should redrive to primary unless fail-on-EAGAIN is requested, and handler exceptions should produce completion errors.
- Watch/notify scenarios: registration, reconnect, ping timeout/error, object delete, disconnect notification, duplicate notify completion, cancellation, and pool deletion should produce one user-visible callback path.
- Monitor reconnection should trigger `resend_mon_ops()` for pool/statfs/pool-stat and latest-map checks.
- Shutdown tests should leave sessions and operation maps empty, release budgets, remove perf counters/admin socket hooks, cancel tick events, and satisfy destructor assertions.
