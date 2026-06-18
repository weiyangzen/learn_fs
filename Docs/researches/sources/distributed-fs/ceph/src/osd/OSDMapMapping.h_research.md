# sources/distributed-fs/ceph/src/osd/OSDMapMapping.h

## Purpose
`OSDMapMapping.h` declares the cache and work-queue interfaces used to precompute PG placement for an `OSDMap`. It separates generic parallel PG/range processing (`ParallelPGMapper`) from the concrete `OSDMapMapping` table that stores up/acting mappings and reverse acting membership.

## Important APIs, Types, and Members
`ParallelPGMapper::Job` is the unit of asynchronous mapping work. It tracks start/finish time, outstanding shard count, the source `OSDMap`, abort state, a completion `Context`, locking, and a condition variable. Subclasses implement `process(const std::vector<pg_t>&)`, `process(int64_t poolid, unsigned ps_begin, unsigned ps_end)`, and `complete()`. The public methods `set_finish_event()`, `is_done()`, `get_duration()`, `wait()`, `wait_for()`, `abort()`, `start_one()`, and `finish_one()` define the lifecycle.

`ParallelPGMapper::Item` carries either an explicit vector of PGs or a pool/range shard. `WQ` is a `ThreadPool::WorkQueue<Item>` that owns enqueue/dequeue/process hooks and delegates actual work to a `Job`.

`OSDMapMapping::PoolMapping` stores one fixed-width row per PG slot. `row_size()` reserves columns for acting primary, up primary, acting count, up count, acting vector, and up vector. `get()` decodes optional outputs from a row; `set()` writes counts and vector values, truncating counts to pool size as a defensive bound. `OSDMapMapping` exposes `get()`, `get_primary_and_shard()`, `get_osd_acting_pgs()`, `update(map, pgid)`, `start_update()`, `get_epoch()`, and `get_num_pgs()`.

## Control Flow
Callers can build the cache synchronously via the private testing-only `update(const OSDMap&)` or asynchronously via `start_update()`. `start_update()` constructs a `MappingJob`, which initializes table dimensions immediately, then queues all pool ranges in a `ParallelPGMapper`. Each worker range calls `_update_range()`. When all ranges finish, `MappingJob::complete()` calls `_finish()` to build reverse maps and stamp the epoch.

Read APIs assume the mapping is already built for the target epoch. `get()` finds the pool mapping and row by `pgid.pool()` and `pgid.ps()`. `get_primary_and_shard()` also resolves the EC shard id by finding the acting primary's vector position; replicated pools use the plain `spg_t(pgid)`.

## State and Persistence
This header declares only in-memory cache structures. `pools` maps pool id to fixed row tables; `acting_rmap` maps OSD id to the PGs for which that OSD is in the acting set; `epoch` indicates which OSDMap epoch the cache reflects; and `num_pgs` totals mapped PG slots. `ParallelPGMapper` owns a queue of heap-allocated `Item`s and relies on work-queue finish hooks to delete them.

## Dependencies and Integration Points
The header uses `osd_types.h` for PG and shard identifiers, Ceph `ThreadPool::WorkQueue`, `Context`, `Cond`, and Ceph time helpers. It is a direct consumer of `OSDMap` placement but only forward-declares `OSDMap` to keep the header lightweight. Tests use friendship through `OSDMapTest`.

## Risks
`PoolMapping` has fixed row capacity based on pool size; any mapping result larger than size is truncated. Read APIs use `ceph_assert()` for pool and `ps` validity, so callers must not query stale or mismatched maps. `Job` lifetime is external to `ParallelPGMapper`; `start_update()` returns a `unique_ptr<MappingJob>` that must outlive queued work. Abort/wait semantics depend on every started shard eventually calling `finish_one()`.

## Test Signals
Header-level tests should check lifecycle transitions in `Job`, finish-context immediate completion after work is done, timeout behavior in `wait_for()`, abort completion status, row encoding/decoding, EC primary shard resolution, and reverse-map access bounds. Integration tests should validate asynchronous rebuilds against direct OSDMap mappings under pool changes.
