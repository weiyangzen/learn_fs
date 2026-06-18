<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_types.h -->
# sources/distributed-fs/ceph-client/include/linux/lockdep_types.h

## Purpose
This header defines the core data types used by lockdep. It separates structural definitions from the larger lockdep API so lock primitives can embed maps and keys without pulling in all lockdep functions.

## Important APIs, Types, and Functions
It defines `enum lockdep_wait_type`, `enum lockdep_lock_type`, `struct lockdep_subclass_key`, `struct lock_class_key`, `struct lock_class`, `struct lock_time`, `struct lock_class_stats`, `struct lockdep_map`, `struct pin_cookie`, and `struct held_lock` when lockdep is enabled. Disabled builds define empty `lock_class_key`, `lockdep_map`, and `pin_cookie`. Constants include `MAX_LOCKDEP_SUBCLASSES`, `LOCK_TRACE_STATES`, `NR_LOCKDEP_CACHING_CLASSES`, `MAX_LOCKDEP_KEYS`, and `INITIAL_CHAIN_KEY`.

## Control Flow
There is no runtime control flow in the header. The fields support lockdep's graph building, class caching, held-lock stack accounting, IRQ context separation, and lock-stat timing.

## State and Persistence Behavior
The types carry runtime diagnostic state in lock instances, class tables, and task held-lock stacks. They do not persist. Disabled builds intentionally erase most storage footprint.

## Dependencies and Integration Points
It depends on `linux/types.h`. It is embedded by spinlocks, mutexes, rwsems, local locks, wait override maps, and lockdep internals.

## Risks and Test Signals
Risks include ABI/layout-sensitive changes, exhausting key/class bit limits, incorrect wait-type classification, and assuming fields exist under `!CONFIG_LOCKDEP`. Test signals are allmodconfig builds, lockdep selftests, lock-stat builds, and compile coverage for disabled lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_types.h -->
