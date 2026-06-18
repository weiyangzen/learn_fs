# sources/distributed-fs/ceph-client/fs/btrfs/locking.h

## Purpose
`locking.h` declares Btrfs tree-locking primitives, lockdep wait-event annotations, transaction-state lockdep maps, lock nesting subclasses, and the DREW lock structure. The source was read as a complete 251-line header.

## Important APIs, Types, and Functions
Constants `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` encode path lock kinds. `enum btrfs_lock_nesting` defines the normal, COW, left/right sibling, split, and new-root subclasses constrained by `MAX_LOCKDEP_SUBCLASSES`. `enum btrfs_lockdep_trans_states` names transaction state wait maps.

Macros include `btrfs_might_wait_for_event()`, `btrfs_lockdep_acquire()`, `btrfs_lockdep_release()`, inode-lock handoff annotations for io_uring encoded I/O, transaction-state wait annotations, and lockdep map initializers. Inline helpers wrap normal read/write tree lock acquisition, tree unlock by lock kind, and debug assertions. `struct btrfs_drew_lock` contains reader/writer atomics and waitqueues.

## Control Flow
The header provides inline call paths from generic tree code into the nested lock implementations in `locking.c`. The lockdep annotation macros model wait-event conditions as rwsem dependencies so lockdep can reason about threads that wait for ordered extents or transaction states without holding the concrete wakeup condition.

## State and Persistence Behavior
No persistent state is defined. Runtime state includes lockdep maps embedded in owning structures, extent-buffer rwsems, path lock arrays, and DREW reader/writer counters.

## Dependencies and Integration Points
The header includes Linux atomic, waitqueue, lockdep, percpu-counter support, and Btrfs `extent_io.h`. It is included widely by Btrfs tree, transaction, ordered extent, snapshot, and io_uring code.

## Risks and Edge Cases
The nesting enum consumes all currently allowed lockdep subclasses; adding values without raising limits trips the static assertion. Annotation misuse can either create noisy lockdep reports or fail to model a real wait dependency. `btrfs_tree_unlock_rw()` BUGs on invalid lock kind, so path lock bookkeeping must be exact.

## Test Signals
All Btrfs builds exercise prototype consistency. Lockdep builds with snapshot, tree balance, relocation, qgroup, and ordered-extent wait tests are the strongest coverage. io_uring encoded read tests cover the inode-lock annotation path.
