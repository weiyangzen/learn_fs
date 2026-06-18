# sources/distributed-fs/ceph-client/kernel/time/timer_migration.c

## Purpose

`timer_migration.c` implements the Linux timer migration hierarchy used on SMP `NO_HZ` systems to let active CPUs handle migratable timers for idle CPUs. It builds a persistent tree of `tmigr_group` nodes, keeps per-CPU `tmigr_cpu` state, selects migrator children at each hierarchy level, queues next migratable timer expiries in per-group `timerqueue` instances, and integrates with CPU hotplug and CPU isolation so idle CPUs can avoid unnecessary wakeups without losing global timer expiries.

The file is not Ceph-specific; in this source tree it is imported kernel infrastructure that distributed filesystems depend on indirectly through scheduler, timer, and block/network timing behavior.

## Important APIs, types, and functions

- Public timer migration hooks exported through `timer_migration.h`: `tmigr_cpu_activate()`, `tmigr_cpu_deactivate()`, `tmigr_cpu_new_timer()`, `tmigr_quick_check()`, `tmigr_requires_handle_remote()`, and `tmigr_handle_remote()`.
- Setup and hotplug entry points: `tmigr_init()` early initcall, `tmigr_cpu_prepare()`, `tmigr_set_cpu_available()`, `tmigr_clear_cpu_available()`, and `tmigr_isolated_exclude_cpumask()`.
- Core state walkers: `walk_groups()`, `__walk_groups()`, and `__walk_groups_from()` apply callback functions while moving bottom-up through the hierarchy.
- State transitions: `tmigr_active_up()` marks a child active and possibly assigns it as migrator; `tmigr_inactive_up()` clears activity, chooses a replacement migrator, and updates queued events.
- Event maintenance: `tmigr_update_events()`, `tmigr_new_timer()`, `tmigr_next_groupevt()`, `tmigr_next_expired_groupevt()`, and `tmigr_next_groupevt_expires()`.
- Remote expiry: `tmigr_handle_remote_up()` finds expired group events and calls `tmigr_handle_remote_cpu()`, which marks a remote idle CPU as being serviced, calls `timer_expire_remote()`, fetches the remote CPU's next timer interrupt, and re-propagates the result.
- Isolation support: `tmigr_is_isolated()`, `tmigr_init_isolation()`, `tmigr_cpu_isolate()`, and `tmigr_cpu_unisolate()` coordinate with housekeeping/cpuset isolation.
- Data structures come from the header: `struct tmigr_cpu`, `struct tmigr_group`, `struct tmigr_event`, and `union tmigr_state`. This file adds `struct tmigr_walk`, a transient context object used while walking groups.

## Control flow

Initialization starts in `tmigr_init()`. It skips UP systems, allocates `tmigr_available_cpumask`, estimates the number of hierarchy levels from possible CPUs and NUMA nodes, allocates one list head per level, and registers CPU hotplug callbacks for prepare and online/offline. `tmigr_cpu_prepare()` initializes the per-CPU event and calls `tmigr_add_cpu()`, which may create or connect groups using `tmigr_setup_groups()`. Groups are allocated with `kzalloc_node()`, attached to level lists, and never destroyed during normal CPU offline.

When a CPU exits idle, `tmigr_cpu_activate()` locks its `tmigr_cpu`, clears `idle`, sets its CPU event to ignored, clears the cached wakeup, and walks upward through `tmigr_active_up()`. Each group atomically sets the child bit active, may assign a migrator if the group had none, increments the sequence counter, and marks the group event as ignored because an active child will handle its own group.

When a CPU enters idle, `tmigr_cpu_deactivate()` calls `__tmigr_cpu_deactivate()`, which marks the CPU event usable if there is a migratable timer, then walks upward through `tmigr_inactive_up()`. That callback atomically removes inactive children, reassigns the migrator to another active child or `TMIGR_NONE`, increments the sequence, and calls `tmigr_update_events()` to insert, remove, or refresh the child event in the parent queue. If the whole top-level hierarchy is idle, the earliest global expiry is returned to the local CPU so it can arm hardware in time.

When an idle CPU gets a new migratable timer, `tmigr_cpu_new_timer()` checks the cached `wakeup` value and, if the CPU event changed, uses `tmigr_new_timer()` to enqueue the new expiry through the group hierarchy. `tmigr_quick_check()` is a fast pre-idle forecast: it only walks while the current CPU is the migrator or the group is otherwise lonely, returning `KTIME_MAX` if another active migrator should cover the hierarchy.

Remote handling is split into a cheap predicate and a full handler. `tmigr_requires_handle_remote()` runs with interrupts disabled and checks whether this CPU should process expired remote events, reading `next_expiry` locklessly on 64-bit and under the group lock on 32-bit. `tmigr_handle_remote()` then walks through migrator-owned groups and repeatedly dequeues expired events. For each event, `tmigr_handle_remote_cpu()` expires that CPU's timers, refetches its next global timer while honoring timer-base lock ordering, and walks the hierarchy again so sibling events are not stranded behind an already-consumed group event.

## State and persistence behavior

The timer migration topology persists for the lifetime of the boot. `tmigr_group` objects are built when CPUs are first prepared or when a new root is required; they are intentionally not freed on CPU offline to avoid expensive lifetime races. Per-CPU `tmigr_cpu` objects are static percpu storage. Runtime state is protected by a mix of raw spinlocks, `tmigr_mutex`, `tmigr_available_mutex`, cpuhotplug serialization, RCU-like publish ordering, and atomic compare/exchange on `union tmigr_state`.

`union tmigr_state` packs `active`, `migrator`, and `seq` into an atomic `u32`. The sequence counter is critical: it prevents stale bottom-up propagation from overwriting newer active/migrator state when CPUs enter and exit idle concurrently. `next_expiry` is kept reliable for lockless remote-expiry checks, with 32-bit reads protected by locks. Event `ignore` flags are deliberately used as lazy invalidation so active paths can avoid parent locks; ignored entries are removed when a group queue is next examined.

Persistent global state includes `tmigr_root`, `tmigr_level_list`, hierarchy level counts, `tmigr_available_cpumask`, and the static key `tmigr_exclude_isolated`.

## Dependencies and integration points

This file depends on kernel timer internals (`tick-internal.h`, `timerqueue`, remote timer base helpers), CPU hotplug (`cpuhp_setup_state()` with `CPUHP_TMIGR_PREPARE` and `CPUHP_AP_TMIGR_ONLINE`), NUMA topology, housekeeping/isolation APIs, raw spinlocks, percpu storage, and timer migration tracepoints (`trace/events/timer_migration.h`). It also uses `timer_expire_remote()`, `fetch_next_timer_interrupt_remote()`, `timer_lock_remote_bases()`, and `timer_base_is_idle()` from the timer core.

The integration surface is intentionally small: the timer idle path calls activate/deactivate/new-timer/quick-check hooks, and timer softirq logic calls the remote predicate and handler. CPU isolation and cpuset code can call `tmigr_isolated_exclude_cpumask()` to remove or restore CPUs in the hierarchy.

## Risks and edge cases

- The hierarchy is highly concurrency-sensitive. Incorrect memory ordering around parent publication, sequence-counter changes, or child/group state reads can lose timers or cause unnecessary wakeups.
- Lock ordering matters: timer base locks must precede timer migration locks, and child locks must precede parent locks. Violations can deadlock timer softirq, idle, or hotplug paths.
- Lazy `ignore` handling intentionally permits benign stale remote expiry; bugs here could either miss a timer or cause repeated unnecessary remote processing.
- Root changes during CPU hotplug require careful activation propagation from the old root. The code contains many `WARN_ON_ONCE()` checks around root/child masks because a bad mask would corrupt the active/migrator bitmap.
- Isolation handling deliberately excludes domain-isolated CPUs but keeps nohz_full kernel-noise housekeeping interactions nuanced. The tick CPU is protected from being isolated in ways that would leave no global migrator.
- `tmigr_requires_handle_remote()` has different 32-bit and 64-bit read strategies; tests should cover both atomicity assumptions.

## Test signals

Useful signals include boot logs from `tmigr_init()`, CPU hotplug stress, nohz/tick idle behavior, cpuset isolation changes, timer migration tracepoints, and timer torture/RCU torture runs that combine CPU offline/online with idle transitions. Failure indicators include missed timer expiries, repeated early wakeups, warnings from group-mask/root assertions, lockdep complaints, remote timer handling loops, or hotplug stalls.
