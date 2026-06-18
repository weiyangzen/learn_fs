# sources/distributed-fs/ceph-client/rust/kernel/id_pool.rs

## Purpose
`id_pool.rs` implements a dynamic bitmap-backed ID allocator. It lets callers find, acquire, release, grow, and shrink numeric IDs while separating allocation of replacement bitmaps from mutation of the pool.

## Important APIs, Types, and Functions
`IdPool` owns a `BitmapVec`. `ReallocRequest` records a target capacity, and `PoolResizer` owns a preallocated replacement bitmap. `IdPool::new`, `with_capacity`, `capacity`, `find_unused_id`, `release_id`, `grow_request`, `grow`, `shrink_request`, and `shrink` form the API. `UnusedId` represents a discovered free bit and exposes `as_usize`, `as_u32`, and consuming `acquire`.

## Control Flow
Clients call `find_unused_id(offset)`, inspect the result if needed, and must call `acquire` to set the bit. If no free bit exists, clients can request a grow, drop locks, allocate a `PoolResizer`, reacquire locks, and call `grow`; `grow` rechecks whether the new bitmap is still larger. Shrink follows a similar request/realloc/apply pattern and rechecks that the last set bit still permits shrinking.

## State and Persistence
The bitmap records allocated IDs in memory only. Capacity starts inline or at requested size, doubles on grow requests, and shrinks by half or to inline size when usage is in the first quarter or empty. The API itself is not synchronized; callers provide locking for shared pools.

## Dependencies and Integration Points
The module depends on `BitmapVec` and allocation flags. It is intended for kernel subsystems needing compact integer handles while allowing allocation outside spinlocks.

## Risks
`UnusedId` does not reserve the bit until `acquire`; callers must not drop it without understanding the ID remains available. `release_id` does not validate ownership and can clear an already-free or out-of-range bit if misused. Grow/shrink are robust to races only if callers serialize actual pool mutation.

## Test Signals
Exercise full allocation to capacity, release/reuse, offset search, grow under contention with stale resizers, shrink when empty and when high bits remain set, max-capacity refusal, and `as_u32` bounds assumptions.
