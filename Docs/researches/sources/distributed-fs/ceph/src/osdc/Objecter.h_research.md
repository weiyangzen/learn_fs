# sources/distributed-fs/ceph/src/osdc/Objecter.h

## Purpose

`Objecter.h` declares Ceph's client-side OSD operation engine. It is the main interface between higher layers such as librados, the CephFS client, RGW, and the OSD cluster. The header covers operation construction (`ObjectOperation`), target calculation state, per-OSD session tracking, asynchronous completions, linger/watch state, pool/statfs operations, command submission, scatter/gather helpers, throttling hooks, and map-version waiting.

## Important APIs, types, and functions

`ObjectOperation` is the mutable builder for OSD op vectors. It owns a small-vector of `OSDOp` plus parallel output slots: `out_bl`, `out_handler`, `out_rval`, and `out_ec`. It exposes helpers for object IO (`read`, `sparse_read`, `write`, `write_full`, `writesame`, `zero`, `truncate`, `remove`), metadata (`stat`, xattrs, omap keys/values/header, watch/list_snaps/list_watchers), class calls, cache/tier/manifest ops, copy operations, assertions, checksums, and internal version queries. Several callbacks decode wire replies into legacy `int*` outputs or modern `boost::system::error_code*` outputs.

`Objecter` derives from `md_config_obs_t` and `Dispatcher`. Public APIs include `op_submit()`, `mutate()`, `read()`, `pg_read()`, `linger_watch()`, `linger_notify()`, `osd_command()`, `pg_command()`, pool snap/pool create/delete helpers, pool/statfs stats, object listing/enumeration, scatter/gather reads and writes, OSD map waits, blocklist event consumption, and global read/write flag handling. `SplitOp`, `ECSplitOp`, and `ReplicaSplitOp` are friends so the split-read implementation can access `Op`, `osdmap`, `_calc_target()`, `_op_submit()`, reply handlers, and the special split-op session.

Key nested types are `op_target_t`, `Op`, `CommandOp`, `LingerOp`, `OSDSession`, `PoolOp`, `PoolStatOp`, `StatfsOp`, and `NListContext`. `op_target_t` holds the full mapping decision for a logical object or explicit PG: base/target oid and locator, PG ids, acting/up sets, pool flags, target OSD, pause/full state, and replica-use metadata. `Op` is the refcounted in-flight object request, carrying target, op vector, snap context, completion variant, trace, throttling budget, object version pointers, request id, retry bookkeeping, and optional `split_op_tids`.

## Control flow

Callers typically build an `ObjectOperation`, then pass it to `prepare_read_op()`, `prepare_mutate_op()`, `read()`, `mutate()`, or a specialized helper. These functions move the op vector and output handlers into a new `Objecter::Op`, set read/write flags, snap state, mtime, object version pointers, and submit via `op_submit()`. Submission maps the target against the current OSDMap, assigns an `OSDSession`, applies throttling, sends an `MOSDOp`, and later completes through dispatcher callbacks such as `handle_osd_op_reply()`.

Map churn is handled by `_calc_target()`, `_map_session()`, `_scan_requests()`, map-check queues, and wait-for-map callbacks. Linger operations use persistent `LingerOp` state with register, reconnect, ping, notify, and cancellation flows. Command and pool/statfs operations follow parallel submit/reply/cancel paths, but with distinct op types and completion signatures.

`process_op_reply_handlers()` is an important integration seam: it decodes individual OSD op outputs into the user-provided destinations and reports handler failures as `osdc_errc::handler_failed`. Split reads reuse the same reply-handler machinery after manually assembling synthetic `out_ops`.

## State and persistence behavior

This header declares in-memory client state, not durable persistence. Persistent cluster state is represented indirectly through the OSDMap, pool ids, snaps, object versions, and OSD replies. Internally, `Objecter` persists runtime state in maps of sessions, in-flight ops, linger ops, pool ops, statfs ops, map-check queues, `waiting_for_map`, cached PG mappings, blocklist events, and throttling counters. Locking is centered on `rwlock`, session locks, `pg_mapping_lock`, and per-session completion locks. Atomic counters track tids, inflight counts, client incarnation, global flags, and extra read flags.

## Dependencies and integration points

The header depends on Ceph primitives (`bufferlist`, `Context`, `SnapContext`, `OSDMap`, `OSDOp`, `MOSDOp`, `Messenger`, `MonClient`, throttles, tracing, admin socket formatting) and Boost.Asio completion tokens. It integrates with `SplitOp` for balanced/split read optimization, `Striper` through scatter/gather helpers, `osdc/error_code` for objecter-specific errors, and the Messenger dispatcher path for OSD op replies, maps, backoff, and watch notifications.

References in `Objecter.cc` show `Objecter.h` declarations are backed by perf counters for split reads, config tracking for `osd_min_split_replica_read_size`, split op completion/cancellation, pool EIO/DNE handling, reply handler exception conversion, and enumeration precondition checks.

## Risks and edge cases

The major risks are lifetime and concurrency hazards: completions can be legacy `Context*`, function2 callables, or Asio handlers; callback code may throw; sessions hold raw pointers to refcounted operations; and lock ordering across objecter/session/watch locks matters. Output vectors must remain parallel to `ops`; `ObjectOperation::add_op()` asserts this, but manual `dup()`/pass-through logic can still be fragile. Read flag filtering in `get_read_flags()` strips balancing/localization for `RWORDERED`, which is correctness-sensitive. `omap_get_vals(std::optional...)` encodes `filter_prefix ? *start_after : std::string_view{}`; that apparent use of `start_after` under the `filter_prefix` condition deserves review because it can encode the wrong filter or dereference an absent `start_after`.

## Test signals

Useful tests are OSD client integration tests covering read/write/stat/xattr/omap/class calls, watch/notify reconnect, pool DNE/EIO and snapshot errors, map changes during in-flight ops, throttling, cancellation, and split-read fallback/retry. Existing source references show `Objecter.cc` routes `osdc_errc` into these paths and `SplitOp` relies on `process_op_reply_handlers()`. Scatter/gather behavior should be exercised with `Striper::StripedReadResult`, sparse reads, and caller-provided output buffers.
