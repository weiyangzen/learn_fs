# sources/distributed-fs/ceph-client/include/linux/plist.h

## Purpose
the priority-sorted list helper API. It layers priority ordering on top of Linux list heads and is
used when callers need deterministic insertion by integer priority.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PLIST_H_`, `PLIST_HEAD_INIT`, `PLIST_HEAD`, `PLIST_NODE_INIT`,
`plist_for_each`, `plist_for_each_continue`, `plist_for_each_safe`, `plist_for_each_entry`,
`plist_for_each_entry_continue`, `plist_for_each_entry_safe`, `plist_next`, `plist_prev`. Types:
none visible in this header. Declared or inline functions: `INIT_LIST_HEAD`, `plist_add`,
`plist_del`, `plist_requeue`, `list_empty`, `WARN_ON`, `container_of`, `plist_node_init`,
`plist_head_empty`, `plist_node_empty`, `plist_first`, `plist_last`.

## Control flow
Callers initialize a `plist_head`, initialize embedded `plist_node` objects with priorities, insert
them with `plist_add()`, and remove or iterate them through list-style helpers. Insertions maintain
priority order while preserving node linkage in ordinary kernel lists.

## State and persistence
State lives in caller-owned `struct plist_head` and `struct plist_node` objects. Ordering is in-
memory only and must be protected by the caller's lock discipline when shared between CPUs.

## Dependencies and integration points
It includes `linux/container_of.h`, `linux/list.h`, `linux/plist_types.h`, `asm/bug.h`. Direct
source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/mm/swapfile.c`, `sources/distributed-fs/ceph-client/lib/plist.c`, `sources/distributed-
fs/ceph-client/kernel/sched/sched.h`, `sources/distributed-fs/ceph-client/kernel/futex/core.c`,
`sources/distributed-fs/ceph-client/kernel/futex/requeue.c`, `sources/distributed-fs/ceph-
client/kernel/futex/waitwake.c`, `sources/distributed-fs/ceph-client/init/init_task.c`,
`sources/distributed-fs/ceph-client/include/linux/pm_qos.h`. It integrates with the Linux driver
core and in-kernel helper libraries that include this header.

## Risks and test signals
Risks include priority ordering regressions, double-add or double-delete of nodes, iteration while
mutating without proper locking, and callers confusing equal-priority FIFO behavior with strict
sorting. Test signals include plist selftests, lockdep on caller locks, empty/list singleton cases,
duplicate priorities, and removal during iteration.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/plist.h` completely for this pass (291 lines, 8797 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/plist.h_research.md`.
