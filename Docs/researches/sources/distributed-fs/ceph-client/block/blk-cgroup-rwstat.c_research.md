# sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.c

## Purpose

`blk-cgroup-rwstat.c` implements legacy blkcg read/write stat helpers enabled by `CONFIG_BLK_CGROUP_RWSTAT`. It backs older policy statistics with per-CPU counters and auxiliary dead-child counters, and provides printing and recursive sum helpers.

## Important APIs, Types, And Functions

The exported functions are `blkg_rwstat_init()`, `blkg_rwstat_exit()`, `__blkg_prfill_rwstat()`, `blkg_prfill_rwstat()`, and `blkg_rwstat_recursive_sum()`.

## Control Flow, State, And Persistence

Initialization creates one per-CPU counter per rwstat category and zeros aux counters. Exit destroys those counters. Printing resolves the blkg device name and emits `Read`, `Write`, `Sync`, `Async`, `Discard`, and `Total` lines. Recursive sum takes the queue lock, walks the target blkg and online descendants under RCU, locates the rwstat in policy data or the blkg, and sums local plus aux counters.

## Dependencies And Integration Points

The file depends on `blk-cgroup-rwstat.h`, blkcg descendant traversal, policy data lookup, `seq_file`, `percpu_counter`, and atomic counters. It is explicitly legacy and not intended for new code; current generic I/O stats use the rstat path in `blk-cgroup.c`.

## Risks And Test Signals

Recursive sum must be called with the queue lock held for valid online tests. Aux counters carry dead-child stats into recursive results but are excluded from local snapshots. Test init failure, printing format, recursive online/offline descendant behavior, aux propagation, and lockdep assertions.
