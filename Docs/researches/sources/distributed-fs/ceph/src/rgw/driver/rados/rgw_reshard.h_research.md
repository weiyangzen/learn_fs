# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.h

## Purpose
This header declares the RADOS RGW bucket resharding interfaces. It separates per-bucket reshard execution, the persistent reshard queue processor, and a wait helper used by callers that must pause while resharding blocks index access.

## Important APIs, Types, And Functions
- `ReshardFaultInjector` is a `FaultInjector<std::string_view>` used to force specific state-machine failures.
- `RGWBucketReshardLock` stores a `RadosStore`, lock oid, ephemeral flag, cls lock object, duration, start time, and renew threshold. Its public API is `lock()`, `unlock()`, `renew()`, and `should_renew()`.
- `RGWBucketReshard` exposes `execute()`, `get_status()`, `cancel()`, `renew_lock_if_needed()`, `clear_resharding()`, prime-shard helpers, `calculate_preferred_shards()`, and `should_zone_reshard_now()`. Private helpers calculate target shard assignment and process source entries.
- `RGWReshard` exposes queue operations (`add`, `update`, `get`, `remove`, `list`) and processor operations (`process_entry`, `process_single_logshard`, `process_all_logshards`, `start_processor`, `stop_processor`).
- `RGWReshard::ReshardWorker` is a `Thread` and `DoutPrefixProvider` wrapper around periodic queue scans.
- `RGWReshardWait` supports blocking and coroutine waits with stop-time cancellation.

## Control Flow
Callers create `RGWBucketReshard` for an already loaded bucket and call `execute()` with a target shard count, fault injector, max entries per operation, and initiator. Background resharding is driven through `RGWReshard`, which hashes bucket names into queue shards and processes them under locks. Code that encounters an active reshard can use `RGWReshardWait::wait()` to delay and retry, and shutdown calls `stop()` to wake all waiters.

## State And Persistence Behavior
The header identifies the objects whose state is persisted by implementation: bucket layout and attrs inside `RGWBucketInfo`, cls lock records in the reshard pool, queue entries of type `cls_rgw_reshard_entry`, bucket instance reshard status entries, and retained log generations. `RGWBucketReshard::max_bilog_history` caps retained old log generations for multisite safety.

## Dependencies And Integration Points
The declarations depend on librados, cls rgw types, cls lock client, Ceph time/yield, intrusive lists, Boost.Asio timers, fault injection, `RGWBucketInfo`, and `rgw::sal::RadosStore`. They are consumed by the RADOS store, bucket index guard paths, admin operations, and background service initialization.

## Risks And Edge Cases
The destructor of `RGWReshardWait` asserts that `stop()` was called, so lifecycle ordering matters. Lock duration and renewal thresholds must align with long-running copy batches. The prime helper list is finite and returns zero for requests above the supported max when asking for greater-or-equal, so callers must handle fallback. Queue processing and per-bucket resharding share lock renewal assumptions; outer lock duration must be at least as long as the bucket lock duration.

## Test Signals
Tests should instantiate prime helper edge cases, lock renewal threshold behavior, queue shard oid hashing stability, `RGWReshardWait` cancellation for coroutine and blocking callers, public cancel behavior for non-resharding buckets, and compile-time coverage of the worker thread prefix/cct/subsys methods.
