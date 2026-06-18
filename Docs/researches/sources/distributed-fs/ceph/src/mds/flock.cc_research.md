<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.cc -->
## sources/distributed-fs/ceph/src/mds/flock.cc

`flock.cc` implements CephFS MDS byte-range lock state for `ceph_lock_state_t`, covering held locks, blocked waiters, lock coalescing/splitting, and limited POSIX deadlock detection. The active state is split between persisted `held_locks` plus `client_held_lock_counts`, and runtime-only `waiting_locks`, `client_waiting_lock_counts`, and a file-static `global_waiting_locks` wait graph used only for `CEPH_LOCK_FCNTL`.

Important entry points are `add_lock`, `remove_lock`, `look_for_lock`, `remove_waiting`, `remove_all_from`, `encode`, `decode`, and `dump`. `add_lock` finds overlapping held locks, separates same-owner locks with `split_by_owner`, blocks on conflicting exclusive/shared ranges, optionally checks `is_deadlock`, and otherwise calls `adjust_locks` before inserting the normalized new lock. `remove_lock` trims, splits, or erases same-owner held locks in the requested range and updates client counts. The range helpers treat `length == 0` as "to EOF", so overflow and endpoint logic are central to correctness.

Deadlock detection is intentionally bounded by `MAX_DEADLK_DEPTH` and follows `global_waiting_locks` from owners of conflicting locks to locks they are waiting on. This is process-wide static state, so destructor and removal paths must remove entries to avoid stale wait graph edges. Persistence is narrow: waiting queues are not encoded, so replay restores only granted locks and client held counts.

Dependencies include `include/ceph_fs.h` lock constants and layout, `client_t`, Ceph buffer encoders, `Formatter`, and MDS debug logging. Integration is with client file locking and reconnect/journal paths that serialize `ceph_lock_state_t`.

Risks: off-by-one range math, `uint64_t(-1)` EOF handling, stale global wait entries, blocked waiter loss across failover, and count/map skew when erasing iterators. Test signals are lock encode/decode round trips, overlapping shared/exclusive scenarios, same-owner merge/split coverage, client cleanup, deadlock-chain cases, and replay behavior proving waiting locks are intentionally absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.cc -->
