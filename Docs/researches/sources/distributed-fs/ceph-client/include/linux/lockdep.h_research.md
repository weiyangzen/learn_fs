<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep.h -->
# sources/distributed-fs/ceph-client/include/linux/lockdep.h

## Purpose
This header declares the runtime locking correctness validator API. It lets lock primitives register classes, report acquire/release events, assert contexts, collect lock statistics, and compile to low-overhead stubs when lockdep is disabled.

## Important APIs, Types, and Functions
It defines lock dependency graph records such as `struct lock_list` and `struct lock_chain`, and APIs including `lockdep_init`, `lockdep_reset`, `lockdep_free_key_range`, `lockdep_register_key`, `lockdep_init_map_type`, `lockdep_set_class*`, `lock_acquire`, `lock_release`, `lock_sync`, `lock_is_held_type`, `lock_pin_lock`, `lock_repin_lock`, `lock_unpin_lock`, and lock-stat hooks. Macros map spinlock, rwlock, mutex, rwsem, seqcount, and generic lock-map events to these primitives.

## Control Flow
Lock initialization maps an instance to a key/class/subclass. On acquire, lockdep records a held-lock stack entry, updates dependency chains, and validates ordering. Release removes the held entry. Assertion macros query current task lock state or IRQ/preemption tracking. Disabled builds replace most operations with stubs and assumptions for static analysis.

## State and Persistence Behavior
Runtime state includes per-task recursion/depth fields, lock classes, dependency graph edges, chain caches, held locks, pin cookies, and optional timing statistics. It is diagnostic state only and does not persist across boot.

## Dependencies and Integration Points
It depends on `lockdep_types.h`, SMP/per-CPU data, debug locks, stack traces, interrupt state tracking, and all lock primitive implementations that embed `dep_map`.

## Risks and Test Signals
Risks include unregistered dynamic keys, false class sharing, missing acquire/release annotations, recursion disabling left on, and different semantics between enabled and disabled configs. Test signals are `CONFIG_PROVE_LOCKING`, lockdep splats, lock-stat data, selftests, IRQ/preemption assertion failures, and absence of false positives after correct subclassing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep.h -->
