# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_utils.h

## Purpose
`rgw_dedup_utils.h` declares shared constants, request types, throttling, stats structures, ETag parsing helpers, byte-size helpers, and urgent control message types for RGW dedup.

## Important APIs, Types, And Functions
The header defines `FULL_DEDUP_SUPPORT`, shard integer types and limits, null shard sentinels, and `MAX_COPIES_PER_OBJ`. `dedup_req_type_t` distinguishes no-op, estimate, and execution modes.

`Throttle` is a simple rate limiter with `set_max_calls_per_sec()`, `disable()`, `is_disabled()`, `acquire()`, and counters for sleep events and time. `dedup_stats_t`, `worker_stats_t`, and `md5_stats_t` collect phase-specific counters and provide aggregation, formatter dumping, and encoding APIs.

`parsed_etag_t` stores MD5 high/low and multipart part count. Size helpers convert bytes to 4 KiB disk blocks and calculate on-disk allocation. `urgent_msg_t`, `op_type_t`, `throttle_action_t`, and `throttle_msg_t` define the watch/notify control payload surface. `dedupable_object()` and `calc_deduped_bytes()` encode the estimate rules.

## Control Flow
The main dedup pipeline uses these types in every phase: work shard ingress fills `worker_stats_t`, MD5 shard processing fills `md5_stats_t`, control messages use `urgent_msg_t`, and throttling is applied around bucket-index and metadata operations. Dedup table estimation calls `calc_deduped_bytes()`.

## State And Persistence Behavior
Stats, throttles, and control messages can be encoded into RADOS xattrs or notification payloads. The `Throttle` runtime token state is intentionally not encoded, only the configured max calls per second. Many counters become admin-observable through shard stats.

## Dependencies And Integration Points
The header depends on Ceph bufferlist, encoding, formatters, `utime_t`, and logging. It is a central include for cluster coordination, store, table, filter, and background dedup code.

## Risks And Edge Cases
`FULL_DEDUP_SUPPORT` is defined directly in this header, so any include enables full-dedup declarations and compile paths unless guarded elsewhere. `Throttle::acquire()` is documented as single-threaded and uses non-atomic counters. `MAX_WORK_SHARD` is 255 while work shard id is stored in 8 bits, so sentinel and hard-limit assumptions must remain aligned.

## Test Signals
Tests should exercise shard limit constants, throttle disabled and limited behavior, all encode/decode helpers, dedupable-object threshold logic, split-head byte estimates, and admin formatting of nonzero failure counters.
