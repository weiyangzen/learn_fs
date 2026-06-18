# sources/distributed-fs/lustre-release/lnet/lnet/lock.c

Purpose: implements libcfs per-CPU-partition spinlock aggregation used by LNet to reduce cacheline contention while still supporting an exclusive all-partitions lock mode.

Important APIs/types/functions: exported `cfs_percpt_lock_create()` allocates a `struct cfs_percpt_lock` and a per-CPT spinlock array, optionally assigning lockdep classes. `cfs_percpt_lock_free()` frees the lock after asserting no exclusive lock is held. `cfs_percpt_lock()` acquires either one partition lock or all locks for `CFS_PERCPT_LOCK_EX`. `cfs_percpt_unlock()` releases the matching lock set in reverse order for exclusive mode.

Control flow: non-exclusive callers spin while `pcl_locked` is set, then lock only their indexed partition. Exclusive callers lock CPT 0 first, set `pcl_locked` to prevent new private lock attempts, then lock all remaining partitions. Unlock clears `pcl_locked` just before releasing CPT 0 after all higher locks have been released. A one-CPT system maps all lock modes to lock index 0.

State and persistence behavior: the only state is the allocated lock object, per-CPT spinlock array, optional CPT table pointer, and `pcl_locked` flag. It is volatile and freed by `cfs_percpt_lock_free()`.

Dependencies/integration points: depends on libcfs CPT allocation/iteration helpers, spinlocks, lockdep class keys, and LNet code using `lnet_net_lock()`/resource locks over per-CPT data structures.

Risks: the exclusive barrier uses a plain `pcl_locked` flag with busy-waiting, so correctness depends on lock ordering and memory semantics from the spinlock sequence. Exclusive locking can starve if new private lockers repeatedly pass before `pcl_locked` is set, though the code sets it after the first lock to narrow that window. Missing lockdep keys can produce false recursive-lock warnings, called out by the warning. Freeing while any partition lock is held is catastrophic and only guarded by assertions/ownership discipline.

Test signals: create/free with single and multiple CPTs, per-CPT independent locking, exclusive lock excludes private locks, unlock order restores private access, NULL lockdep keys only warn, invalid indexes assert in debug builds, and high-contention stress does not deadlock.
