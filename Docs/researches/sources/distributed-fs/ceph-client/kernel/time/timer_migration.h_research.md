# sources/distributed-fs/ceph-client/kernel/time/timer_migration.h

## Purpose

`timer_migration.h` defines the private data model and public hooks for the kernel's migratable timer hierarchy. It supplies group and CPU state structures used by `timer_migration.c`, encodes the compact active/migrator state word, and provides no-op stubs when timer migration is not built.

## Important APIs, types, and functions

- `TMIGR_CHILDREN_PER_GROUP` is fixed at 8 and must remain a power of two because child masks are single bits in an 8-bit field.
- `struct tmigr_event` represents a queued child event. It contains a `timerqueue_node`, the CPU whose timer should be expired, and an `ignore` flag for lazy invalidation.
- `struct tmigr_group` is an internal hierarchy node with a raw spinlock, parent pointer, group event, reliable `next_expiry`, child timer queue, atomic migration state, hierarchy metadata, child count, child mask, and setup list node.
- `struct tmigr_cpu` stores per-CPU membership and runtime state: lock, availability, idle/remote flags, parent group, mask in parent, cached wakeup expiry, and CPU event.
- `union tmigr_state` packs the active-child bitmap, selected migrator mask, and sequence counter into an atomic `u32`.
- Public hooks are declared for SMP + `CONFIG_NO_HZ_COMMON`: `tmigr_handle_remote()`, `tmigr_requires_handle_remote()`, `tmigr_cpu_activate()`, `tmigr_cpu_deactivate()`, `tmigr_cpu_new_timer()`, and `tmigr_quick_check()`.
- Stub functions are provided when timer migration is unavailable. Only the `void` and boolean hooks are stubbed here; callers for the `u64` hooks are expected to be compiled only when the feature is available.

## Control flow

The header does not execute logic, but it describes the control contract. CPUs become active via `tmigr_cpu_activate()`, become inactive via `tmigr_cpu_deactivate(nextevt)`, update their idle global timer via `tmigr_cpu_new_timer(nextevt)`, and use `tmigr_quick_check(nextevt)` as a pre-idle forecast. Active migrator CPUs call `tmigr_requires_handle_remote()` and, if needed, `tmigr_handle_remote()` to process expired global timers for idle CPUs.

## State and persistence behavior

All structures in this header are long-lived kernel state. `tmigr_group` objects persist after creation and are not destroyed on CPU offline. `tmigr_cpu` is per-CPU state. `tmigr_event` nodes may remain queued after becoming obsolete; the `ignore` bit allows lazy removal under the relevant group lock. `union tmigr_state` intentionally avoids endian-dependent writes by requiring updates through the named fields before atomically publishing the full `state`.

The `parent` pointer comment documents an important persistence rule: once set it is not removed, but it may be updated when a new hierarchy level is added. Lockless single reads are acceptable for conservative abort/wakeup decisions; repeated reads within one action must be protected to avoid inconsistent decisions.

## Dependencies and integration points

The types rely on kernel `timerqueue`, raw spinlock, atomic, list, and time definitions from surrounding includes in implementation files. The function declarations are consumed by timer idle and softirq code. The compile-time guard ties the feature to SMP and `NO_HZ_COMMON`, matching the intended use on tickless multiprocessor systems.

## Risks and edge cases

- Bit-width assumptions are central: active and migrator masks are `u8`, so increasing group capacity without changing state layout would break masks.
- `groupmask` must never be zero for a real child, because zero cannot identify a bit in the state masks.
- The header documents subtle parent-pointer rules. Re-reading `parent` locklessly during a multi-step action can observe hierarchy growth inconsistently.
- The stubs cover only some hooks; build configurations must ensure `tmigr_cpu_deactivate()`, `tmigr_cpu_new_timer()`, and `tmigr_quick_check()` are not referenced when the declarations are omitted.

## Test signals

Compile coverage across `CONFIG_SMP`, `CONFIG_NO_HZ_COMMON`, and non-SMP/non-NOHZ configurations validates the header contract. Runtime validation comes from timer migration tracepoints, CPU hotplug tests, and nohz idle tests that exercise `ignore`, `remote`, and `wakeup` fields under concurrent idle entry/exit.
