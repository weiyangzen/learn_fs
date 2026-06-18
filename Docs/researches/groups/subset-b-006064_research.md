# subset-b-006064 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer_migration.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer_migration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer_migration.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer_migration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/vsyscall.c -->
# sources/distributed-fs/ceph-client/kernel/time/vsyscall.c

## Purpose

`vsyscall.c` is the generic kernel-side updater for VDSO/vsyscall time data. It copies timekeeper state into `vdso_k_time_data` so user space can read common clocks without a syscall, while preserving seqlock-style consistency and architecture-specific synchronization.

## Important APIs, types, and functions

- `fill_clock_configuration()` copies clocksource read-base parameters into a `vdso_clock`: cycle base, optional overflow limit, mask, multiplier, and shift.
- `update_vdso_time_data()` updates high-resolution VDSO base times for `CLOCK_MONOTONIC`, `CLOCK_BOOTTIME`, `CLOCK_MONOTONIC_RAW`, and `CLOCK_TAI`.
- `update_vsyscall()` is the main timekeeper update hook. It updates realtime, coarse realtime, coarse monotonic, hrtimer resolution, high-resolution clocks if VDSO-capable, and architecture clock metadata.
- `update_vsyscall_tz()` copies `sys_tz` timezone fields into VDSO data.
- Under `CONFIG_POSIX_AUX_CLOCKS`, `vdso_time_update_aux()` updates an auxiliary timekeeper's VDSO clock slot.
- `vdso_update_begin()` and `vdso_update_end()` let architecture code update arch-specific VDSO data while holding the timekeeper lock and invalidating/restoring the VDSO sequence counter.

## Control flow

`update_vsyscall()` starts with `vdso_write_begin(vdata)`, writes the active VDSO clock mode into the high-resolution/coarse and raw clock slots, updates realtime and coarse basetimes, stores `hrtimer_resolution`, and then only refreshes high-resolution derived clocks if `clock_mode != VDSO_CLOCKMODE_NONE`. It calls `__arch_update_vdso_clock()` for both generic clock slots, ends the sequence with `vdso_write_end()`, and finally calls `__arch_sync_vdso_time_data()`.

`update_vdso_time_data()` performs shifted-nanosecond arithmetic using `tk->tkr_mono.shift`. It normalizes monotonic and boottime nanoseconds by subtracting one shifted second until the value is below a second, copies raw time directly from `tkr_raw`, and computes TAI by adding `tai_offset` to realtime seconds.

`vdso_time_update_aux()` selects the auxiliary clock slot by `tk->id - TIMEKEEPER_AUX_FIRST`, disables VDSO use when `tk->clock_valid` is false, and otherwise fills clock configuration and computes the auxiliary basetime from `monotonic_to_aux`.

`vdso_update_begin()` acquires the timekeeper lock with IRQ save and marks VDSO data inconsistent. `vdso_update_end()` reverses this by marking data consistent, syncing to architecture storage, and releasing the lock/IRQs.

## State and persistence behavior

The persistent target is the global VDSO time data page referenced by `vdso_k_time_data`. Updates are protected by VDSO sequence helpers so concurrent user readers can detect in-progress writes. `hrtimer_res`, timezone fields, clock modes, clocksource conversion parameters, and basetime arrays persist until the next timekeeper update. No dynamic memory is allocated.

## Dependencies and integration points

The file depends on `linux/timekeeper_internal.h`, VDSO datapage/helper APIs, hrtimer resolution, `sys_tz`, architecture hooks (`__arch_update_vdso_clock()` and `__arch_sync_vdso_time_data()`), and internal timekeeping lock helpers from `timekeeping_internal.h`. It is called from core timekeeping update paths and may be used by architecture code for additional VDSO fields.

## Risks and edge cases

- Shifted nanosecond arithmetic must stay normalized; incorrect carry handling would return invalid monotonic or boottime basetimes to user space.
- VDSO writes must be bracketed by sequence updates. Missing `vdso_write_end()` or architecture sync can expose inconsistent or stale data.
- If a clocksource is not VDSO capable, high-resolution fields are intentionally skipped; consumers must fall back to syscalls when `VDSO_CLOCKMODE_NONE` is published.
- Auxiliary clock indexing depends on valid `timekeeper` IDs and `clock_valid`; a bad ID would select the wrong slot.
- `update_vsyscall_tz()` writes timezone values without the main timekeeper sequence wrapper; correctness depends on the architecture/VDSO synchronization contract for these fields.

## Test signals

Test signals include VDSO clock_gettime comparisons against syscall results for realtime, monotonic, boottime, raw, TAI, coarse clocks, timezone update tests, clocksource changes to/from non-VDSO mode, and architecture-specific VDSO synchronization tests. Timekeeping selftests should watch for monotonic regressions, incorrect coarse normalization, and invalid hrtimer resolution exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/vsyscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/torture.c -->
# sources/distributed-fs/ceph-client/kernel/torture.c

## Purpose

`torture.c` provides common infrastructure for in-kernel torture test modules, especially RCU-derived stress tests. It centralizes randomized sleeps, CPU hotplug churn, task shuffling, automatic shutdown, stutter/pause behavior, lifecycle serialization, and generic torture kthread helpers. Client torture modules explicitly call these helpers instead of using this file as an independent module entry point.

## Important APIs, types, and functions

- Module parameters: `disable_onoff_at_boot`, `ftrace_dump_at_shutdown`, `verbose_sleep_frequency`, `verbose_sleep_duration`, and `random_shuffle`.
- Lifecycle state: `FULLSTOP_DONTSTOP`, `FULLSTOP_SHUTDOWN`, `FULLSTOP_RMMOD`, guarded by `fullstop_mutex`.
- Sleep/random helpers: `verbose_torout_sleep()`, `torture_hrtimeout_ns/us/ms/jiffies/s()`, and `torture_random()`.
- CPU hotplug helpers under `CONFIG_HOTPLUG_CPU`: `torture_num_online_cpus()`, `torture_offline()`, `torture_online()`, `torture_onoff_init()`, `torture_onoff_stats()`, and `torture_onoff_failures()`.
- Task shuffling helpers: `torture_shuffle_task_register()`, `torture_shuffle_init()`, and internal `torture_shuffle_tasks()`.
- Shutdown helpers: `torture_shutdown_absorb()`, `torture_shutdown_init()`, reboot notifier `torture_shutdown_notify()`, and cleanup logic.
- Stutter helpers: `stutter_wait()` and `torture_stutter_init()`.
- Test lifecycle: `torture_init_begin()`, `torture_init_end()`, `get_torture_init_jiffies()`, `torture_cleanup_begin()`, `torture_cleanup_end()`, `torture_must_stop()`, and `torture_must_stop_irq()`.
- Thread helpers: `torture_kthread_stopping()`, `_torture_create_kthread()`, and `_torture_stop_kthread()`.

## Control flow

A client module begins with `torture_init_begin(ttype, verbose)`. This serializes against existing torture tests, records the type string, sets normal fullstop state, stores the initialization jiffies, and prints parameters. The client then initializes optional subsystems such as CPU on/off, shuffling, shutdown, and stutter, and calls `torture_init_end()` to release the mutex and register the reboot notifier.

CPU hotplug stress starts with `torture_onoff_init()`, which creates `torture_onoff()` when an interval is configured. That kthread brings all CPUs online, waits for holdoff and boot completion, then repeatedly picks a random CPU and tries to offline it or online it, updating success/failure and timing statistics. Cleanup stops the thread and brings all CPUs online again.

Task shuffling starts with `torture_shuffle_init()`. Registered kthreads are kept in `shuffle_task_list`. The shuffler periodically builds a CPU mask that excludes one CPU, then applies it to registered tasks so each CPU can become idle in turn. With `random_shuffle`, only a random subset of tasks is moved each interval.

Automatic shutdown uses `torture_shutdown_init()`, which creates a thread sleeping until an absolute shutdown time. If the test has not stopped, the thread runs the registered cleanup hook, optionally dumps ftrace, and calls `kernel_power_off()`. An external reboot/shutdown triggers `torture_shutdown_notify()`, which moves fullstop state to shutdown so kthreads can park via `torture_shutdown_absorb()`.

Stuttering uses `torture_stutter()` to periodically set `stutter_till_abs_time`; participating test threads call `stutter_wait()` and sleep until the pause interval ends.

Cleanup starts with `torture_cleanup_begin()`. It detects a shutdown/rmmod race, otherwise sets fullstop to rmmod, stops common helper threads in a safe order, and returns whether the caller should abandon normal teardown. `torture_cleanup_end()` clears `torture_type` after client threads have stopped.

## State and persistence behavior

The file maintains global singleton state for one active torture test: `torture_type`, `verbose`, `fullstop`, and `torture_init_jiffies`. Hotplug, shuffle, shutdown, and stutter each keep static task pointers and configuration. Hotplug statistics persist until module cleanup and are reported through exported stats/failure functions. `shuffle_task_list` owns heap-allocated `shuffle_task` nodes registered for each torture kthread and frees them on shuffle cleanup.

Concurrency is guarded by mutexes for fullstop and shuffle list updates, atomic state for verbose sleeps, `READ_ONCE()`/`WRITE_ONCE()` for lockless stop and timing flags, cpus read locks during affinity changes, and kthread stop synchronization during cleanup.

## Dependencies and integration points

The file depends on generic kernel kthreads, CPU hotplug (`add_cpu()`, `remove_cpu()`, `cpu_is_hotpluggable()`), scheduler affinity, hrtimers, reboot notifiers, freezer/scheduling APIs, RCU torture helpers from `rcu/rcu.h`, trace clock/local clock, and exported declarations in `linux/torture.h`. It exports symbols for client modules such as RCU, lock, refscale, or other kernel torture tests.

## Risks and edge cases

- Only one torture test may run at a time. Mispaired `torture_init_begin/end` or cleanup calls can leave `fullstop_mutex` or `torture_type` in a bad state.
- Shutdown and rmmod are intentionally treated as illegal concurrently; clients must honor `torture_cleanup_begin()` returning true.
- Kthreads must call `torture_kthread_stopping()` before returning, otherwise module text/data may be freed while a thread still runs.
- CPU hotplug operations can fail during early boot due to transient platform restrictions; the code forgives early `-EBUSY` but records other failures.
- Affinity shuffling can fail or be ineffective on one-CPU systems or under cpuset constraints; the code skips the one-online-CPU case.
- The random generator is crude and not cryptographic; it is intended for stress variation only.

## Test signals

Signals include successful creation and stopping of helper kthreads, hotplug success/attempt ratios from `torture_onoff_stats()`, absence of `torture_onoff_failures()`, correct parking during shutdown, full CPU restoration after hotplug cleanup, and no lingering registered shuffle tasks. Kernel logs with `TORTURE_FLAG`, lockdep, CPU hotplug warnings, and ftrace dumps at shutdown are the primary observability path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/torture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/Kconfig

## Purpose

`kernel/trace/Kconfig` defines the configuration surface for the kernel tracing subsystem. It declares architecture capability symbols, core tracing dependencies, user-visible tracer options, dynamic probe/event features, test modules, startup selftests, and the runtime verification tracing submenu.

## Important APIs, types, and functions

This is Kconfig metadata rather than C code. Important symbols include:

- Architecture capability symbols: `HAVE_FUNCTION_TRACER`, `HAVE_FUNCTION_GRAPH_TRACER`, `HAVE_DYNAMIC_FTRACE`, `HAVE_SYSCALL_TRACEPOINTS`, `HAVE_RETHOOK`, `HAVE_FENTRY`, object-tool mcount capabilities, and related dynamic ftrace feature gates.
- Core internal symbols: `TRACING`, `GENERIC_TRACER`, `RING_BUFFER`, `EVENT_TRACING`, `CONTEXT_SWITCH_TRACER`, `TRACE_CLOCK`, `TRACER_MAX_TRACE`, and `TRACING_SUPPORT`.
- User-facing tracer menu: `menuconfig FTRACE`, `FUNCTION_TRACER`, `FUNCTION_GRAPH_TRACER`, `DYNAMIC_FTRACE`, `FUNCTION_PROFILER`, `STACK_TRACER`, `IRQSOFF_TRACER`, `PREEMPT_TRACER`, `SCHED_TRACER`, `HWLAT_TRACER`, `OSNOISE_TRACER`, `TIMERLAT_TRACER`, `MMIOTRACE`, `FTRACE_SYSCALLS`, `TRACER_SNAPSHOT`, branch profiling options, and `BLK_DEV_IO_TRACE`.
- Dynamic events and probe features: `FPROBE`, `FPROBE_EVENTS`, `KPROBE_EVENTS`, `UPROBE_EVENTS`, `EPROBE_EVENTS`, `BPF_EVENTS`, `PROBE_EVENTS_BTF_ARGS`, `DYNAMIC_EVENTS`, and `PROBE_EVENTS`.
- Build tooling choices: `FTRACE_MCOUNT_USE_CC`, `FTRACE_MCOUNT_USE_OBJTOOL`, `FTRACE_MCOUNT_USE_RECORDMCOUNT`, and `BUILDTIME_MCOUNT_SORT`.
- Test/debug options: tracepoint/ring-buffer benchmarks, eval map retention, recursion recording, startup tests, ring buffer delta validation, mmiotrace/preemptirq/synthetic/kprobe test modules, histogram trigger debug, and remote tracing test.
- It sources `kernel/trace/rv/Kconfig` for runtime verification monitors.

## Control flow

The dependency flow starts with architecture symbols selecting capabilities. `TRACING_SUPPORT` requires IRQ flags and stacktrace support, then `FTRACE` opens the tracer menu. Most user-visible tracers select either `GENERIC_TRACER` or `TRACING`, which in turn selects ring buffer, tracepoints, event tracing, trace clock, binary printf, and RCU task support.

Feature-specific options layer on top of those bases. Function tracing requires architecture support and enables kallsyms/context-switch/glob/tasks-RCU dependencies. Dynamic ftrace depends on function tracing and architecture patching support. Function graph tracing depends on function tracing and graph support. Probe events select generic `PROBE_EVENTS` and `DYNAMIC_EVENTS` so common tracing infrastructure is built when any probe provider is enabled.

The file ends with test and debug options and remote tracing symbols inside the `if FTRACE` block, meaning those options disappear unless the tracing menu is enabled.

## State and persistence behavior

Kconfig symbols persist in the generated kernel configuration and shape both build output and runtime behavior. `select` relationships force hidden prerequisites on when a feature is enabled; `depends on` prevents invalid combinations from being offered. Defaults such as `FTRACE=y if DEBUG_KERNEL`, `DYNAMIC_FTRACE=y`, and several probe events defaulting to `y` under their prerequisites affect typical debug kernels.

## Dependencies and integration points

This file integrates with architecture Kconfig files that select `HAVE_*` symbols, with `kernel/trace/Makefile` object selection, with tracefs/debugfs runtime interfaces documented under `Documentation/trace/`, with block tracing (`BLK_DEV_IO_TRACE` selects `RELAY`, `DEBUG_FS`, `TRACEPOINTS`, `GENERIC_TRACER`, and `STACKTRACE`), with BPF/perf/kprobes/uprobes, and with runtime verification through the sourced RV Kconfig.

## Risks and edge cases

- Heavy use of `select` can silently enable substantial tracing infrastructure. Misplaced selects may create circular dependencies or unexpected build/runtime overhead.
- Several options are explicitly dangerous or high overhead (`PROFILE_ALL_BRANCHES`, ring buffer validation, hwlat/osnoise/timerlat on production systems, KPROBE_EVENTS_ON_NOTRACE, `MMIOTRACE_TEST`).
- Build-tool path selection for mcount is mutually constrained by compiler, objtool, and patchable function entry support; architecture capability mistakes can break ftrace patching.
- `BLK_DEV_IO_TRACE` pulls in debugfs and relay and depends on block/sysfs, so enabling it changes both ABI surface and runtime tracepoint registration.
- Startup tests intentionally add boot time and can trigger broad event enable/disable cycles.

## Test signals

Signals include successful `olddefconfig`/`allmodconfig` coverage across architectures, absence of Kconfig dependency warnings, object inclusion matching `Makefile` expectations, tracefs files appearing for enabled tracers, ftrace startup selftest output when configured, ring buffer benchmark/test logs, and probe/tracer runtime smoke tests under `/sys/kernel/tracing`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/Makefile -->
# sources/distributed-fs/ceph-client/kernel/trace/Makefile

## Purpose

`kernel/trace/Makefile` maps tracing Kconfig symbols to object files, controls instrumentation policy for the tracing subsystem itself, and adds a build-time undefined-symbol check for `simple_ring_buffer` users such as pKVM.

## Important APIs, types, and functions

This is kbuild metadata. Important constructs include:

- `ccflags-remove-$(CONFIG_FUNCTION_TRACER) += $(CC_FLAGS_FTRACE)` prevents tracing code from being function-instrumented by default.
- `KCSAN_SANITIZE := n` under function tracing avoids recursion/noise from KCSAN instrumentation in tracing code.
- Special cases re-enable ftrace instrumentation for selftests and `CONFIG_FUNCTION_SELF_TRACING`.
- `KBUILD_CFLAGS += -DDISABLE_BRANCH_PROFILING` disables branch profiling of tracing code when branch tracing is enabled.
- `GCOV_PROFILE := y` under `CONFIG_GCOV_PROFILE_FTRACE`.
- Per-object controls such as `KCOV_INSTRUMENT_trace_preemptirq.o := n`, include paths for `bpf_trace.o`, `trace_benchmark.o`, and `trace_events_filter.o`, and KASAN enabling for `undefsyms_base.o`.
- `obj-$(CONFIG_...)` lines select trace core, tracers, event/probe providers, tests, runtime verification, remote tracing, and block tracing objects.
- `UNDEFINED_ALLOWLIST` and `cmd_check_undefined` implement the `%.o.checked` target used by `always-$(CONFIG_SIMPLE_RING_BUFFER)`.

## Control flow

Kbuild evaluates configuration symbols and adds objects to the trace directory build. Core objects such as `trace.o`, `trace_output.o`, `trace_seq.o`, and `trace_stat.o` are built when `CONFIG_TRACING` is enabled. Function, graph, branch, latency, osnoise, block, event, syscall, BPF, kprobe, uprobe, boot-time, fprobe, and test objects are included according to their symbols.

For `CONFIG_BLOCK=y`, `blktrace.o` is also built when `CONFIG_EVENT_TRACING` is enabled, even if `CONFIG_BLK_DEV_IO_TRACE` is off, because `blktrace.c` contains the generic `blk_fill_rwbs()` helper under `CONFIG_EVENT_TRACING`. Runtime verification descends into `rv/`. `simple_ring_buffer.o` receives an extra `.checked` target that runs `nm -u` and fails the build on unexpected unresolved symbols.

## State and persistence behavior

The Makefile does not maintain runtime state, but it controls the persistent build artifact composition and instrumentation attributes. Build flags persist for the compilation of all objects in this directory unless overridden by per-object variables. The undefined-symbol allowlist is recomputed during the build and influences whether `simple_ring_buffer.o.checked` succeeds.

## Dependencies and integration points

The file integrates directly with `kernel/trace/Kconfig` symbols, kbuild variables (`obj-y`, `obj-m`, `always-*`, `targets`, `if_changed`), compiler instrumentation flags, sanitizer knobs, `nm`, `awk`, and optional subsystems including BPF, perf events, block layer, kgdb/kdb, PM tracepoints, runtime verification, remote tracing, and pKVM hypervisor symbol restrictions.

## Risks and edge cases

- Accidentally instrumenting tracing internals can cause recursion or misleading trace data. The file carefully removes ftrace flags globally and re-adds them only for selftest/debug cases.
- `blktrace.o` is selected by two independent conditions; changes must preserve the reason event tracing needs it even without full blktrace support.
- The undefined-symbol check depends on tool output and the allowlist. Too broad an allowlist can hide hypervisor-incompatible symbols; too narrow can break valid builds.
- Sanitizer/profiling overrides affect diagnostics. Disabling KCSAN/KCOV in some tracing objects is intentional but reduces coverage.
- Object list changes must stay synchronized with Kconfig dependency/select relationships.

## Test signals

Build tests should cover tracing disabled, core tracing, function tracing, self tracing, event tracing with `CONFIG_BLOCK`, full `BLK_DEV_IO_TRACE`, runtime verification, simple ring buffer, and GCOV/KCOV/KCSAN combinations. Useful signals are absence of recursive tracing warnings, successful `.o.checked` generation, expected tracefs features in built kernels, and no missing object or undefined-symbol link failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/blktrace.c -->
# sources/distributed-fs/ceph-client/kernel/trace/blktrace.c

## Purpose

`blktrace.c` implements block I/O tracing. With `CONFIG_BLK_DEV_IO_TRACE`, it provides the legacy debugfs/relayfs blktrace ioctl/sysfs interface, registers block tracepoint probes, records request/bio/remap/plug/unplug/zone/message events, and exposes a `blk` ftrace tracer. With `CONFIG_EVENT_TRACING`, it also provides `blk_fill_rwbs()` for block trace event formatting.

## Important APIs, types, and functions

- Public exported APIs: `blk_trace_setup()`, `blk_trace_startstop()`, `blk_trace_remove()`, `blk_trace_ioctl()`, `blk_trace_shutdown()`, `__blk_trace_note_message()`, `blk_add_driver_data()`, and `blk_fill_rwbs()`.
- Event recorders: `record_blktrace_event()` for v1 `struct blk_io_trace`, `record_blktrace_event2()` for v2 `struct blk_io_trace2`, and `relay_blktrace_event*()` for relayfs output.
- Core logging path: `__blk_add_trace()` maps request operation/flags to blktrace actions, filters by action mask/LBA/pid, writes to either ftrace ring buffer or relay channel, and handles cgroup IDs.
- Setup/teardown: `blk_trace_setup_prepare()`, `blk_trace_setup_finalize()`, `blk_trace_setup()`, `blk_trace_setup2()`, optional `compat_blk_trace_setup()`, `blk_trace_start()`, `blk_trace_stop()`, `blk_trace_cleanup()`, and `blk_trace_free()`.
- User interfaces: ioctl handler `blk_trace_ioctl()`, debugfs files `dropped` and `msg`, relay callbacks, and sysfs attributes `trace/enable`, `act_mask`, `pid`, `start_lba`, and `end_lba`.
- Tracepoint probes: request events (`insert`, `issue`, `merge`, `requeue`, `complete`), bio events (`queue`, `complete`, merges, getrq), plug/unplug, split, remap, zone write plug/unplug, zone append update, and driver data.
- Ftrace output: `fill_rwbs()`, `blk_log_*()` helpers, `what2act`, `print_one_line()`, `blk_trace_event_print()`, `blk_trace_event_print_binary()`, tracer callbacks, `trace_blk_event`, and `blk_tracer`.

## Control flow

For ioctl-based tracing, users call `BLKTRACESETUP` or `BLKTRACESETUP2`. `blk_trace_ioctl()` resolves the request queue and dispatches to setup helpers. `blk_trace_setup_prepare()` rejects concurrent traces on the same queue, allocates `struct blk_trace`, per-CPU sequence counters and message buffers, creates/reuses debugfs directories, creates `dropped` and `msg`, opens a relay channel, and initializes the LBA range. `blk_trace_setup_finalize()` copies the user-visible name, records version/action mask/range/pid, stores `Blktrace_setup`, publishes `q->blk_trace` with RCU, and increments the global probe reference count. The first reference registers block tracepoint callbacks.

`BLKTRACESTART` moves a trace from setup/stopped to running, increments `blktrace_seq`, links the trace on `running_trace_list`, and emits a timestamp note. `BLKTRACESTOP` marks it stopped, removes it from the running list, and flushes relay buffers. Teardown removes `q->blk_trace`, stops tracing, waits for RCU readers, closes relay/debugfs/percpu resources, and unregisters tracepoints when the global reference count drops to zero.

The sysfs path under `/sys/block/.../trace` can lazily create `struct blk_trace` with `blk_trace_setup_queue()` and remove it with `blk_trace_remove_queue()`. This path does not allocate a relay channel and is used with the ftrace `blk` tracer. The implementation explicitly normalizes uninitialized `bt->version == 0` to v2 in the ftrace recording path to avoid zero-length allocation/format mismatches.

Tracepoint callbacks run under RCU, load `q->blk_trace`, derive sector/bytes/op flags/cgroup ID, and call `__blk_add_trace()`. That function adds read/write/sync/readahead/meta/flush/FUA/zone/discard/write-zeroes classification bits, drops v2-only zone operations for v1 traces, filters by action mask, LBA range, and pid, and then writes either to the ftrace ring buffer (`TRACE_BLK`) or relay per-CPU buffer. Relay writes disable local IRQs while reserving per-CPU buffer space and incrementing the per-CPU sequence number.

The ftrace `blk` tracer registers a trace event and tracer during `device_initcall(init_blk_tracer)`, sometimes deferred to `trace_init_wq`. When enabled, `blk_tracer_enabled` diverts events into the tracing ring buffer. Printing uses `what2act` and `blk_log_*()` helpers to render classic or non-classic lines, optional cgroup IDs/names, binary v1-compatible output, and message/remap/PDU data.

## State and persistence behavior

Per-queue state lives in `struct blk_trace` referenced by `request_queue::blk_trace` under RCU. It includes version, trace state, relay channel, percpu sequence counters, percpu message buffers, action mask, LBA range, pid filter, device, debugfs directory, and running-list node. Global state includes `blktrace_seq`, `blk_tr`, `blk_tracer_enabled`, `running_trace_list`, `running_trace_lock`, `blk_probe_mutex`, and `blk_probes_ref`.

`q->blk_trace` publication/removal uses RCU so tracepoint callbacks can run locklessly. Debugfs setup/removal is serialized by the queue debugfs mutex. The running trace list is raw-spinlock protected because notes may be emitted with interrupts disabled. Probe registration is reference-counted so tracepoints are registered only while at least one trace is active/configured.

## Dependencies and integration points

The file depends on block-layer request/bio APIs, `linux/blktrace_api.h`, UAPI blktrace formats, relayfs, debugfs, sysfs device attributes, tracepoints from `trace/events/block.h`, ftrace ring buffer/tracer APIs, cgroup IDs under `CONFIG_BLK_CGROUP`, RCU, per-CPU allocation, compat ioctl support on x86_64, and `../../block/blk.h` queue debugfs helpers.

It is built in two modes: full blktrace under `CONFIG_BLK_DEV_IO_TRACE`, and event-format helper support under `CONFIG_EVENT_TRACING`. Its outputs are consumed by legacy `blktrace` tooling, tracefs `current_tracer=blk`, `trace_pipe`, perf/ftrace event consumers, and block trace event formatters.

## Risks and edge cases

- ABI compatibility is delicate. v1 and v2 trace records differ, and the ftrace path always prefers v2 while binary output can synthesize v1. Incorrect lengths or layouts corrupt trace buffers or user tooling.
- The sysfs path creates a `blk_trace` without relay channel or initialized version; the code contains explicit handling for version zero in `__blk_add_trace()`.
- Concurrent setup is rejected per queue, but callbacks may race teardown; RCU grace periods and probe reference counting are required for safety.
- Relay reservation failures silently drop events; `dropped` reports full-buffer drops but not every possible filtering/drop reason.
- LBA and pid filters can hide expected events; action masks are shifted into action bits and easy to misconfigure.
- Cgroup output changes PDU layout by prepending an ID, so all formatting and binary consumers must agree on `__BLK_TA_CGROUP`/`__BLK_TN_CGROUP`.
- Local IRQ disabling around relay writes protects per-CPU buffers but increases latency on hot block paths.

## Test signals

Useful signals include ioctl setup/start/stop/teardown with legacy blktrace tools, sysfs `trace/enable` toggling, ftrace `blk` tracer output, action-mask string parsing, pid/LBA filtering, cgroup ID/name formatting, request and bio tracepoint coverage, zone operation tracing with v2 and rejection with v1, remap/split/plug/unplug formatting, relay `dropped` accounting, teardown under active I/O, and KASAN/KCSAN/lockdep runs for buffer length and RCU lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/blktrace.c -->
