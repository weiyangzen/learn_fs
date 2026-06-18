# sources/distributed-fs/lustre-release/lnet/include/lock.h

## Purpose
This internal LNet header declares a CPU-partition lock abstraction for data that is usually updated per CPU partition but occasionally needs global exclusion.

## Important APIs, Types, And Functions
`CFS_PERCPT_LOCK_EX` requests exclusive locking across all private locks. `struct cfs_percpt_lock` stores the CPT table, exclusive state, and per-partition spinlock table. Public APIs are `cfs_percpt_lock_create()`, `cfs_percpt_lock_free()`, `cfs_percpt_lock()`, and `cfs_percpt_unlock()`. `cfs_percpt_lock_num()` reports the number of private locks. `cfs_percpt_lock_alloc()` wraps creation with a static `lock_class_key` array for lockdep.

## Control Flow
Callers create a lock for a `cfs_cpt_table`, lock either a single partition index or the exclusive sentinel, update protected data, then unlock the same scope. The allocation macro uses static lockdep keys when the CPT count fits `CFS_PERCPT_LOCK_KEYS`, otherwise it falls back to no explicit key array.

## State, Persistence, And Dependencies
The lock object owns spinlock storage and records whether it is exclusively locked. There is no persistence beyond kernel memory. It depends on libcfs CPT APIs, spinlocks, and lockdep key types.

## Integration Points
LNet code uses this pattern for per-CPT structures with rare global mutation, matching the topology used by schedulers, network data, and routing/peer tables.

## Risks
Deadlock risk exists if callers mix partition and exclusive locking in inconsistent order or unlock with a different index. Lockdep class coverage is limited to 256 CPTs by the macro. The header exposes only declarations, so implementation correctness is in the corresponding C file.

## Test Signals
Concurrency tests should cover per-partition parallel access, exclusive exclusion against all partitions, lock/unlock balance, CPT counts above and below 256, and lockdep warnings under stress.
