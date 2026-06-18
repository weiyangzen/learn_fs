# subset-b-006047 research

Grouped research for the subset B work item. Each section preserves the source path in its title and is wrapped with the exact reconciliation markers requested.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_nocb.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/tree_nocb.h

## Purpose
`tree_nocb.h` implements the tree-RCU no-callbacks (NOCB) path used when CPUs offload RCU callback processing to per-CPU callback kthreads and per-group grace-period kthreads. It covers boot-time selection of NOCB CPUs, callback enqueue bypassing, lazy callback flushing, deferred wakeups, runtime offload/deoffload of offline CPUs, kthread creation, and diagnostic dumps. When `CONFIG_RCU_NOCB_CPU` is disabled, the file supplies stubs so the rest of tree RCU can call the same helpers without conditional code.

## Important APIs, Types, and Functions
- Boot/module controls: `rcu_nocb_setup()`, `parse_rcu_nocb_poll()`, `nocb_nobypass_lim_per_jiffy`, and `rcu_nocb_gp_stride` configure offloaded CPUs, polling mode, bypass thresholds, and GP-kthread grouping.
- Lock helpers: `rcu_nocb_lock()`, `rcu_nocb_unlock()`, `rcu_nocb_unlock_irqrestore()`, `rcu_nocb_bypass_lock()`, and `rcu_lockdep_assert_cblist_protected()` centralize NOCB locking rules around `rdp->nocb_lock` and `rdp->nocb_bypass_lock`.
- Enqueue/bypass path: `rcu_nocb_try_bypass()`, `rcu_nocb_flush_bypass()`, `rcu_nocb_do_flush_bypass()`, `nocb_bypass_needs_flush()`, `call_rcu_nocb()`, and `__call_rcu_nocb_wake()` decide whether callbacks go directly to `rdp->cblist` or through `rdp->nocb_bypass`.
- Worker paths: `nocb_gp_wait()`, `rcu_nocb_gp_kthread()`, `nocb_cb_wait()`, and `rcu_nocb_cb_kthread()` drive grace-period waiting and callback invocation for offloaded CPUs.
- Runtime toggling: `rcu_nocb_cpu_offload()`, `rcu_nocb_cpu_deoffload()`, `rcu_nocb_cpu_toggle_offload()`, `rcu_nocb_rdp_offload()`, and `rcu_nocb_rdp_deoffload()` change NOCB state for offline CPUs.
- Lazy RCU hooks: `rcu_set_jiffies_lazy_flush()`, `rcu_get_jiffies_lazy_flush()`, `lazy_rcu_shrink_count()`, and `lazy_rcu_shrink_scan()` expose testable lazy flush timing and memory-pressure flushing.
- Initialization/diagnostics: `rcu_init_nohz()`, `rcu_boot_init_nocb_percpu_data()`, `rcu_spawn_cpu_nocb_kthread()`, `rcu_organize_nocb_kthreads()`, `rcu_bind_current_to_nocb()`, and `show_rcu_nocb_state()`.

## Control Flow
At boot, `rcu_nocbs=`, `rcu_nocb_poll`, `CONFIG_RCU_NOCB_CPU_DEFAULT_ALL`, and `nohz_full` determine `rcu_nocb_mask`. `rcu_init_nohz()` allocates or merges masks, registers the lazy shrinker when enabled, marks selected per-CPU segmented callback lists as `SEGCBLIST_OFFLOADED`, and calls `rcu_organize_nocb_kthreads()` to assign each CPU to a GP representative.

On `call_rcu()`, the NOCB caller enters `call_rcu_nocb()`. `rcu_nocb_try_bypass()` first handles non-offloaded and early-boot cases, then rate-limits direct `cblist` enqueues. High-rate or lazy callbacks use `nocb_bypass`; old or full bypass queues are flushed into `cblist`. If a formerly empty queue receives work, `__call_rcu_nocb_wake()` wakes the GP kthread immediately or schedules a deferred wakeup timer depending on IRQ state, polling mode, and whether callbacks are lazy-only.

The GP kthread loops in `nocb_gp_wait()`. It scans the NOCB group list, flushes bypass lists when age/size thresholds require, advances segmented callback lists when grace periods complete, wakes per-CPU callback kthreads when callbacks are ready, waits for the earliest needed grace period, and processes pending offload/deoffload toggles. The callback kthread waits on `nocb_cb_wq`, invokes `rcu_do_batch()`, advances callbacks again if possible, and sleeps when no ready callbacks remain.

Runtime offload/deoffload requires the target CPU to be offline. Deoffload performs `rcu_barrier()`, parks the callback kthread, verifies empty lists, asks the GP kthread to remove the `rdp` from the group list, and clears `SEGCBLIST_OFFLOADED`. Offload performs the reverse list/flag transition and unparks the callback kthread.

## State and Persistence
State is in per-CPU `struct rcu_data`: `cblist`, `nocb_bypass`, `lazy_len`, `nocb_*_kthread`, `nocb_gp_rdp`, wait queues, wakeup timers, sleep flags, group list nodes, and bypass rate counters. Global state includes `rcu_nocb_mask`, `rcu_nocb_poll`, `rcu_state.nocb_is_setup`, `rcu_state.nocb_mutex`, and lazy shrinker registration. There is no filesystem persistence; configuration persists only through boot parameters, module parameters, and in-memory kernel state.

## Dependencies and Integration Points
The file is included by the tree-RCU implementation and depends on RCU segmented callback lists, per-CPU `rcu_data`, `rcu_node` grace-period sequencing, kthreads, timers, swait queues, CPU hotplug locking, cpumasks, `NO_HZ_FULL`, shrinkers, tracepoints, and lockdep. It integrates with `tree_plugin.h` through `rcu_rdp_is_offloaded()`, with stall diagnostics through `show_rcu_nocb_state()`, with memory reclaim through the lazy shrinker, and with callback enqueue/core GP code through `call_rcu_nocb()` and deferred wakeup flushing.

## Risks
The central risks are ordering and wakeup races. Bypass callbacks must not be stranded when `cblist` is empty, `cblist.len` must continue to account for bypass entries, lazy and non-lazy callbacks must retain ordering, and deferred timer wakeups must not leave GP kthreads asleep. Runtime toggling is sensitive to offline CPU preconditions, `rcu_barrier()` completion, parked kthreads, and stable `SEGCBLIST_OFFLOADED` reads. Locking is split across `nocb_lock`, `nocb_bypass_lock`, `nocb_gp_lock`, CPU hotplug state, and `rcu_state.nocb_mutex`, so incorrect call context can create deadlocks or lockdep splats.

## Test Signals
Useful signals include boot logs showing NOCB CPU masks, `rcu_nocb_poll`, and GP stride grouping; tracepoints from `trace_rcu_nocb_wake()`; `show_rcu_nocb_state()` output in stall dumps; rcutorture NOCB/lazy scenarios; hotplug tests that offload and deoffload offline CPUs; memory pressure that triggers lazy shrinker scans; and lockdep warnings from unsafe offloaded-state reads or unprotected callback-list access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_nocb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_plugin.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/tree_plugin.h

## Purpose
`tree_plugin.h` supplies configuration-dependent tree-RCU behavior, especially the differences between preemptible RCU and non-preemptible RCU. It implements blocked-reader tracking, RCU read-side entry/exit, context-switch quiescent-state reporting, deferred quiescent states, priority boosting, callback kthread priority setup, and NO_HZ_FULL helper policy. It is a private include for tree RCU rather than a standalone translation unit.

## Important APIs, Types, and Functions
- Offload state check: `rcu_rdp_is_offloaded()` validates that callers read NOCB state only under safe synchronization.
- Boot announcement: `rcu_bootup_announce_oddness()` and `rcu_bootup_announce()` report selected RCU features and non-default tuning.
- Preemptible RCU path: `rcu_preempt_ctxt_queue()`, `rcu_note_context_switch()`, `__rcu_read_lock()`, `__rcu_read_unlock()`, `rcu_preempt_deferred_qs_irqrestore()`, `rcu_read_unlock_special()`, `exit_rcu()`, and `dump_blkd_tasks()` maintain blocked-reader state.
- Non-preemptible path: `rcu_qs()`, `rcu_all_qs()`, `rcu_note_context_switch()`, and `rcu_read_unlock_strict()` provide quiescent-state reporting without blocked-reader lists.
- Boosting: `rcu_boost()`, `rcu_boost_kthread()`, `rcu_initiate_boost()`, `rcu_preempt_boost_start_gp()`, and `rcu_spawn_one_boost_kthread()` implement priority boosting for tasks blocking RCU grace periods.
- Kthread/NO_HZ helpers: `rcu_cpu_kthread_setup()`, `rcu_is_callbacks_kthread()`, `rcu_nohz_full_cpu()`, and `rcu_bind_gp_kthread()`.

## Control Flow
In preemptible builds, `__rcu_read_lock()` increments the current task nesting counter and `__rcu_read_unlock()` decrements it. If the outermost unlock sees special work, `rcu_read_unlock_special()` either handles it immediately or defers it through softirq, scheduler reschedule, or IRQ work depending on interrupt, softirq, and expedited-GP conditions.

When a task context-switches inside an RCU read-side critical section, `rcu_note_context_switch()` queues the task into the leaf `rcu_node->blkd_tasks` list via `rcu_preempt_ctxt_queue()`. That queueing chooses list position based on whether normal and/or expedited grace periods are already blocked. Later, `rcu_preempt_deferred_qs_irqrestore()` removes the task from blocked lists, advances `gp_tasks`, `exp_tasks`, and `boost_tasks`, reports unblocked quiescent states, and drops artificial boost mutex ownership if needed.

In non-preemptible builds, context-switch and clock-tick paths only report CPU quiescent states because readers cannot be preempted into `blkd_tasks`. `rcu_all_qs()` handles urgent quiescent-state requests and can force a momentary extended quiescent state when the core asks for a heavy QS.

Boosting starts when a GP has waited past `boost_time`, when callback overload or strict GP mode demands it, or when an expedited GP is blocked. The boost kthread fabricates an `rt_mutex` held by the blocked task, locks it to donate priority, and relies on the task to release/deboost when it exits the read-side critical section.

## State and Persistence
State is in current task fields (`rcu_read_lock_nesting`, `rcu_read_unlock_special`, `rcu_node_entry`, `rcu_blocked_node`), per-CPU `rcu_data` (`cpu_no_qs`, deferred QS irq_work state, callback kthread task/activity), and `rcu_node` fields (`blkd_tasks`, `gp_tasks`, `exp_tasks`, `boost_tasks`, `boost_time`, boost kthread state, `qsmask`, `expmask`). There is no durable persistence; all state is scheduler/RCU runtime state.

## Dependencies and Integration Points
This code integrates tightly with the scheduler (`rcu_note_context_switch()`), lockdep, irq_work, softirq processing, task exit, RCU grace-period core, expedited GP code, NOCB callback threads, `rtmutex_common.h`, CPU isolation/housekeeping, and tracepoints. Exported read-lock/unlock functions are used by the kernel-wide RCU API, while private helpers are called from `tree.c` and other RCU internals.

## Risks
The highest risks are incorrect blocked-reader list placement, missed deferred quiescent-state reporting, lock ordering around `rcu_node->lock`, and stale task state during boosting. False positives in expedited handling are tolerated, but false negatives can stall grace periods. Boosting uses artificial rtmutex ownership and must stay synchronized with task exit and unlock paths. Non-preemptible and preemptible variants share names with different semantics, so configuration-specific test coverage is important.

## Test Signals
Signals include rcutorture preemptible/non-preemptible scenarios, expedited GP torture, lockdep warnings from read-side misuse, RCU boost kthread activity, traces for `rcu_preempt_task` and unlock events, scheduler context-switch warnings for voluntary switches inside RCU read-side sections, and stall reports that include blocked task lists or boost counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_plugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_stall.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/tree_stall.h

## Purpose
`tree_stall.h` implements normal tree-RCU CPU stall detection, reporting, panic policy, sysctl/sysfs controls, forward-progress diagnostics, and optional stall notifier chains. It tracks grace-period start and stall deadlines, detects self and remote stalls, prints CPU/task/kthread state, and kicks RCU machinery to recover.

## Important APIs, Types, and Functions
- Controls: sysctls `panic_on_rcu_stall` and `max_rcu_stall_to_panic`, module parameters such as `csd_lock_suppress_rcu_stall` and `sysrq_rcu`, and sysfs `rcu_stall_count`.
- Timeout helpers: `rcu_jiffies_till_stall_check()` and `rcu_exp_jiffies_till_stall_check()` clamp configured timeouts; `record_gp_stall_check_time()` records GP deadlines.
- Suppression and panic: `rcu_sysrq_start()`, `rcu_sysrq_end()`, `rcu_panic()`, `panic_on_rcu_stall()`, and `rcu_cpu_stall_reset()`.
- Detection/reporting: `check_cpu_stall()`, `print_cpu_stall()`, `print_other_cpu_stall()`, `print_cpu_stall_info()`, `rcu_dump_cpu_stacks()`, and `rcu_print_task_stall()`.
- Kthread diagnostics: `rcu_check_gp_kthread_starvation()`, `rcu_check_gp_kthread_expired_fqs_timer()`, `show_rcu_gp_kthreads()`, and `rcu_fwd_progress_check()`.
- Optional notifier API: `rcu_stall_chain_notifier_register()`, `rcu_stall_chain_notifier_unregister()`, and `rcu_stall_notifier_call_chain()`.

## Control Flow
At each grace-period start, `record_gp_stall_check_time()` snapshots `gp_start`, computes `jiffies_stall`, and records force-QS counters. Periodic RCU clock/softirq paths call `check_cpu_stall()`, which first suppresses warnings when requested, rejects false positives using ordered reads of `gp_seq`, `jiffies_stall`, and `gp_start`, and then uses `cmpxchg()` on `jiffies_stall` so only one CPU reports a given stall.

If the current CPU is part of the outstanding `qsmask`, `print_cpu_stall()` emits a self-detected stall. Otherwise, after a rat delay, `print_other_cpu_stall()` reports CPUs and tasks blocking the GP. Both paths print queue length, online CPU count, GP sequence, per-CPU idle/softirq/FQS data, stack traces, GP-kthread starvation information, and optional ftrace dumps, then either force quiescent states or request rescheduling.

For preemptible RCU, blocked task reporting walks `rnp->gp_tasks` through `blkd_tasks`, grabs task references, and optionally calls `sched_show_task()`. Forward-progress checks used by rcutorture call `show_rcu_gp_kthreads()` during active GPs or `rcu_check_gp_start_stall()` when requested GPs fail to start.

## State and Persistence
State is runtime-only in `rcu_state` (`gp_start`, `jiffies_stall`, `gp_activity`, `gp_req_activity`, `gp_flags`, `n_force_qs`, `gp_kthread`, `gp_state`), per-CPU `rcu_data` (`ticks_this_gp`, `softirq_snap`, `rcu_iw_pending`, cputime snapshots), and per-node masks/task pointers. Sysctl and sysfs values persist only as live kernel tunables.

## Dependencies and Integration Points
This file depends on printk/nbcon emergency sections, sysctl, sysfs, panic notifiers, KVM guest pause detection, BPF scheduler stall handling, CSD-lock diagnostics, softirq and IRQ statistics, RCU task and NOCB diagnostics, sysrq, ftrace dumping, and optional stall notifier infrastructure. It integrates with grace-period initialization, FQS loops, scheduler clock paths, rcutorture, and exported debug entry points.

## Risks
Risks include false stall reports from stale jiffies, VM pauses, slow consoles, expired timers, or GP sequence races; the file counters these with memory barriers, suppression flags, KVM pause checks, and deadline rewriting. Diagnostic printing occurs under emergency conditions and must avoid hard lockups while holding RCU-node locks. Panic-on-stall policy can intentionally crash systems, so sysctl bounds and count thresholds matter. Notifier users can suppress or alter warning behavior and are intentionally warned as risky.

## Test Signals
Signals include sysctl clamping behavior, `/sys/kernel/rcu_stall_count`, generated stall warnings, rcutorture forward-progress checks, sysrq `y` dumps when enabled, panic notifier suppression during panic, ftrace dumps on stall, and output from `show_rcu_gp_kthreads()` showing GP state, qsmasks, boost/task blockers, NOCB state, and callback counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_stall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/update.c -->
# sources/distributed-fs/ceph-client/kernel/rcu/update.c

## Purpose
`update.c` provides common public RCU update-side infrastructure: boot/runtime mode transitions, expedited-vs-normal policy, lazy callback urgency controls, lockdep read-side queries, synchronous grace-period waiting helpers, debug object hooks for `rcu_head`, torture/test exports, stall-warning module parameters, and early boot self tests. It includes `tasks.h` to bring in Tasks RCU support.

## Important APIs, Types, and Functions
- Mode controls: `rcu_gp_is_normal()`, `rcu_gp_is_expedited()`, `rcu_expedite_gp()`, `rcu_unexpedite_gp()`, `rcu_async_should_hurry()`, `rcu_async_hurry()`, `rcu_async_relax()`, `rcu_end_inkernel_boot()`, and `rcu_set_runtime_mode()`.
- Lockdep queries: `debug_lockdep_rcu_enabled()`, `rcu_read_lock_held()`, `rcu_read_lock_bh_held()`, `rcu_read_lock_sched_held()`, and `rcu_read_lock_any_held()`.
- Grace-period wait helpers: `wakeme_after_rcu()`, `__wait_rcu_gp()`, `finish_rcuwait()`, and `get_completed_synchronize_rcu()`.
- Debug/test exports: `init_rcu_head()`, `destroy_rcu_head()`, `init_rcu_head_on_stack()`, `destroy_rcu_head_on_stack()`, `do_trace_rcu_torture_read()`, `torture_sched_setaffinity()`, `synchronize_rcu_trivial_preempt()`, `rcu_early_boot_tests()`, and `rcupdate_announce_bootup_oddness()`.
- Tunables: `rcu_expedited`, `rcu_normal`, `rcu_normal_after_boot`, stall-warning parameters, and `rcu_self_test`.

## Control Flow
During early boot, expedited and hurry nesting atomics start nonzero so early RCU operations avoid long delays. `rcu_set_runtime_mode()` runs as a core initcall, executes synchronous primitive self tests when prove-RCU is enabled, marks `rcu_scheduler_active` as running, frees scheduler-running callbacks, and retests. Later `rcu_end_inkernel_boot()` unexpedites, relaxes async callbacks, optionally forces normal mode after boot, and marks boot complete for torture users.

Callers that need to wait for several RCU flavors use `__wait_rcu_gp()`. It initializes on-stack `rcu_head` objects, deduplicates identical callback functions, queues `wakeme_after_rcu()` callbacks, waits for completions in the requested task state, and destroys stack debug objects. Lockdep query functions first call `rcu_read_lock_held_common()` to account for disabled lockdep, idle/non-watching CPUs, and offline CPUs, then inspect lock maps or preempt/softirq state.

When `CONFIG_DEBUG_OBJECTS_RCU_HEAD` is enabled, the file registers debug object operations for stack and heap/static `rcu_head` lifetime validation. With prove-RCU self tests enabled, early boot queues normal RCU, SRCU, and `kfree_rcu()` callbacks, then verifies barriers and poll cookies at late init.

## State and Persistence
State is in module parameters and in-memory globals: expedited/normal mode flags, `rcu_async_hurry_nesting`, `rcu_expedited_nesting`, `rcu_boot_ended`, lockdep maps, stall-warning tunables, early self-test counters, and static SRCU state for tests. There is no durable persistence beyond live boot/module parameters.

## Dependencies and Integration Points
The file depends on core RCU headers, scheduler state, lockdep, debugobjects, SRCU, Tasks RCU, torture modules, module parameters, completions, kprobes-safe tracing, and memory allocation. It exports many symbols used by drivers, kernel subsystems, torture tests, and RCU internals.

## Risks
Reference-count-like nesting APIs (`rcu_expedite_gp()`/`rcu_unexpedite_gp()` and async hurry/relax) can underflow or leave global policy unexpectedly expedited/lazy if callers are imbalanced. `__wait_rcu_gp()` must deduplicate callback functions correctly to avoid double waiting or double stack-object destruction. Lockdep helpers must avoid false positives while the scheduler, lockdep, CPU online state, or RCU watching state is not stable. Early boot self tests depend on callback execution ordering and SRCU cleanup.

## Test Signals
Signals include boot logs from `rcu_test_sync_prims()`, prove-RCU self-test callback counts, lockdep warnings from invalid RCU read-side use, module parameter behavior for normal/expedited/stall settings, torture tests that call exported affinity and trace helpers, and debugobjects reports for invalid `rcu_head` lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/reboot.c -->
# sources/distributed-fs/ceph-client/kernel/reboot.c

## Purpose
`reboot.c` implements the generic kernel reboot, halt, poweroff, orderly shutdown, emergency restart, sys-off handler, reboot syscall, reboot tunable, and hardware-protection shutdown logic. Architecture code supplies the final machine-specific restart/halt/poweroff operations, while this file coordinates notifiers, device shutdown, syscore shutdown, CPU migration, usermode helper shutdown, and user/kernel control surfaces.

## Important APIs, Types, and Functions
- Restart/halt/poweroff APIs: `emergency_restart()`, `kernel_restart_prepare()`, `kernel_restart()`, `kernel_halt()`, `kernel_power_off()`, `do_kernel_restart()`, `do_kernel_power_off()`, and `kernel_can_power_off()`.
- Notifier APIs: `register_reboot_notifier()`, `unregister_reboot_notifier()`, `devm_register_reboot_notifier()`, `register_restart_handler()`, and `unregister_restart_handler()`.
- Sys-off APIs: `struct sys_off_handler`, `register_sys_off_handler()`, `unregister_sys_off_handler()`, `devm_register_sys_off_handler()`, `devm_register_power_off_handler()`, `devm_register_restart_handler()`, `register_platform_power_off()`, and `unregister_platform_power_off()`.
- User entry points: `SYSCALL_DEFINE4(reboot)`, `ctrl_alt_del()`, `orderly_poweroff()`, and `orderly_reboot()`.
- Hardware protection: `__hw_protection_trigger()`, `hw_failure_emergency_schedule()`, `hw_failure_emergency_action_func()`, and `hw_protection_setup()`.
- Configuration surfaces: `reboot_setup()` parses `reboot=`, sysfs under `/sys/kernel/reboot` exposes mode/type/force/cpu/hw_protection, and sysctls expose `kernel.poweroff_cmd` and `kernel.ctrl-alt-del`.

## Control Flow
Emergency restart is the shortest path: dump emergency kmsg, set `SYSTEM_RESTART`, and call `machine_emergency_restart()` without normal shutdown. Clean restart calls reboot notifiers, sets system state, disables usermode helpers, shuts down devices, runs restart-prepare handlers, migrates to the reboot CPU, shuts down syscore, dumps shutdown kmsg, and calls `machine_restart()`.

Halt and poweroff share `kernel_shutdown_prepare()` for reboot notifiers, system state, usermodehelper disable, and device shutdown. Poweroff additionally runs power-off prepare handlers and calls `machine_power_off()`, which is expected to call `do_kernel_power_off()` if needed. The generic poweroff handler chain can include new sys-off handlers and a temporary legacy `pm_power_off` adapter.

The reboot syscall checks namespace capability, validates magic values, delegates child pid namespaces to `reboot_pid_ns()`, falls back from poweroff to halt when no poweroff handler exists, serializes transitions with `system_transition_mutex`, and dispatches restart, CAD toggles, halt, poweroff, `RESTART2`, kexec, or hibernation. Orderly reboot/poweroff schedule work that invokes `/sbin/reboot` or configurable `/sbin/poweroff`; forced paths call `emergency_sync()` and then kernel restart/poweroff if usermode execution fails.

Hardware protection triggers only once via an atomic guard, logs the reason, schedules a delayed forced action, and starts orderly reboot or forced orderly poweroff. If the delayed backup fires, it tries kernel restart/poweroff and finally `emergency_restart()`.

## State and Persistence
Important state includes `C_A_D`, `cad_pid`, `reboot_mode`, `panic_reboot_mode`, `reboot_default`, `reboot_cpu`, `reboot_type`, `reboot_force`, `poweroff_fallback_to_halt`, `pm_power_off`, notifier chains, sys-off handler allocations, `system_transition_mutex`, `poweroff_cmd`, `poweroff_force`, hardware-protection action, and delayed work. Values are in memory; boot parameters and sysfs/sysctl writes configure live state but are not persistent across reboot.

## Dependencies and Integration Points
The file integrates with architecture machine operations, kexec, hibernation, pid namespaces, capabilities, device core shutdown, syscore operations, kmsg dumpers, usermode helper execution, workqueues, notifier chains, devres, sysfs, sysctl, CPU hotplug/affinity, and platform/driver poweroff or restart providers.

## Risks
System transition paths are destructive by design. Risks include handlers registered at incorrect priority, legacy `pm_power_off` coexistence, poweroff fallback to halt surprising callers, missed serialization around concurrent transitions, CPU migration to an offline or unsuitable reboot CPU, usermode helper failure in orderly paths, and forced hardware-protection actions preempting normal shutdown. Sys-off platform priority permits only one platform handler; misuse returns `-EBUSY`.

## Test Signals
Signals include syscall return codes for invalid magic/capability/commands, sysfs/sysctl read/write behavior, notifier registration/unregistration and priority ordering, orderly shutdown fallback logs, kmsg dump reasons, `Power down`/`Restarting system`/halt emergency messages, hardware-protection delayed work behavior, and architecture-level confirmation that machine restart/halt/poweroff callbacks are invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/regset.c -->
# sources/distributed-fs/ceph-client/kernel/regset.c

## Purpose
`regset.c` provides small common helpers for fetching architecture-defined `user_regset` data from a target task into kernel memory or userspace. It is used by ptrace/core-dump-style code paths that consume `struct user_regset_view` without duplicating allocation, size clamping, and copy logic.

## Important APIs, Types, and Functions
- `__regset_get()` is the internal helper. It validates the `regset_get` callback, clamps requested size to `regset->n * regset->size`, allocates a zeroed buffer when the caller does not provide one, invokes the regset callback with a `struct membuf`, and returns bytes produced.
- `regset_get()` fetches data into caller-provided storage.
- `regset_get_alloc()` allocates storage and returns it through `void **data`.
- `copy_regset_to_user()` resolves a regset by index from a `user_regset_view`, obtains an allocated buffer, copies produced bytes to a user pointer, and frees the buffer.

## Control Flow
The common path enters `__regset_get()`. If the architecture regset has no getter, it returns `-EOPNOTSUPP`. The requested size is capped to the architectural maximum. If no buffer was supplied, it allocates with `kvzalloc()`. The regset callback writes through `struct membuf`, whose remaining length is returned as `res`; negative values abort and free any internal allocation. Success stores the buffer pointer and returns `size - res`.

`copy_regset_to_user()` uses `regset_get_alloc()`, treats positive returns as byte counts, copies exactly those bytes to userspace, maps copy failures to `-EFAULT`, frees with `kvfree()`, and returns either zero or the error.

## State and Persistence
The file has no global mutable state. Allocation is transient per call. The target task and regset callback own the actual register state; this helper only stages a snapshot in kernel memory.

## Dependencies and Integration Points
It depends on `linux/regset.h`, task structures, `struct user_regset`, `struct user_regset_view`, `struct membuf`, `kvzalloc()`, `kvfree()`, and `copy_to_user()`. Architecture code supplies regset definitions and callbacks.

## Risks
The main risks are incorrect size calculations in regset definitions, callbacks returning malformed remaining lengths, usercopy failures, and callers misunderstanding positive byte counts versus zero success in `copy_regset_to_user()`. The helper clamps oversize requests and frees only internally allocated buffers, which avoids freeing caller-owned storage.

## Test Signals
Signals include ptrace/regset tests across architectures, requests with zero/oversized sizes, missing getter callbacks returning `-EOPNOTSUPP`, allocation failure paths returning `-ENOMEM`, usercopy fault injection producing `-EFAULT`, and validation that returned byte counts match callback-filled data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/relay.c -->
# sources/distributed-fs/ceph-client/kernel/relay.c

## Purpose
`relay.c` implements the generic relay channel API for high-volume kernel-to-userspace data transfer through per-CPU or global ring-like buffers exposed as files. It handles buffer allocation, vmalloc-backed mmap, sub-buffer switching, reader wakeups, hotplug buffer creation, file operations, and channel lifetime management.

## Important APIs, Types, and Functions
- Channel/buffer lifecycle: `relay_open()`, `relay_close()`, `relay_reset()`, `relay_flush()`, `relay_prepare_cpu()`, `relay_create_buf()`, `relay_destroy_buf()`, and `relay_close_buf()`.
- Buffer operations: `relay_buf_full()`, `relay_switch_subbuf()`, `relay_subbufs_consumed()`, `relay_stats()`, and callback wrapper `relay_subbuf_start()`.
- Mapping/allocation: `relay_alloc_buf()`, `relay_mmap_prepare_buf()`, `relay_buf_fault()`, and `relay_file_mmap_ops`.
- File operations: `relay_file_open()`, `relay_file_poll()`, `relay_file_mmap_prepare()`, `relay_file_read()`, `relay_file_release()`, and exported `relay_file_operations`.
- Read helpers: `relay_file_read_consume()`, `relay_file_read_avail()`, `relay_file_read_subbuf_avail()`, `relay_file_read_start_pos()`, and `relay_file_read_end_pos()`.

## Control Flow
`relay_open()` validates sizes and callbacks, allocates `struct rchan` plus a per-CPU pointer array, initializes channel metadata, and under `relay_channels_mutex` opens buffers for online CPUs. `relay_open_buf()` creates a buffer, optionally asks the client to create a relay file, initializes buffer state with `__relay_reset()`, and handles global-channel sharing. CPU hotplug calls `relay_prepare_cpu()` to add missing buffers for existing channels.

Writers reserve space through higher-level relay helpers and eventually call `relay_switch_subbuf()` when a sub-buffer is complete or an event does not fit. The function records padding, increments produced counts, updates inode size or early byte counts, uses a memory barrier before waking readers via deferred `irq_work`, calls the client `subbuf_start` callback for the next sub-buffer, and returns zero if the buffer is full or the event is too large.

Readers open relay files to get a buffer reference, poll on `read_wait`, mmap through vm fault translation from vmalloc addresses to pages, or read through `relay_file_read()`. Reads are serialized by the inode lock, skip padding, consume complete sub-buffers, handle overwritten data by advancing consumed counters, copy available bytes to userspace, and update file position modulo the circular buffer.

Closing a channel removes it from the global list, marks each buffer finalized, synchronizes pending wakeup irq work, calls client `remove_buf_file`, and drops krefs. Buffer destruction unmaps vmap memory, frees pages and padding, clears the per-CPU pointer, and drops the channel kref.

## State and Persistence
Global state is `relay_channels` protected by `relay_channels_mutex`. Channel state includes sub-buffer size/count, allocation size, base filename, parent dentry, callbacks, private data, per-CPU buffer pointers, global-channel flag, and kref. Buffer state includes vmapped pages, page array, padding array, produced/consumed counters, bytes consumed, current data pointer and offset, dentry, waitqueue, irq work, stats, finalized flag, CPU number, early byte count, and kref. Data lives in memory and is exposed through relay files; it is not durable.

## Dependencies and Integration Points
The file depends on relay API structures and client callbacks, debugfs or another filesystem chosen by `create_buf_file`, vmalloc/vmap and page allocation, mmap VM operations, wait queues, irq_work, poll/read file operations, CPU hotplug, per-CPU allocation, krefs, usercopy, and inode sizing. Users include tracing and instrumentation subsystems that need efficient streaming to userspace.

## Risks
Risks include buffer size overflow, allocation failure across many CPUs, races with CPU hotplug and channel close, readers seeing overwritten data, incorrect padding accounting, wakeups from scheduler-sensitive contexts, mmap faults after buffer teardown, and callback misuse. The code mitigates some hazards with `relay_channels_mutex`, krefs, inode read locking, irq_work-deferred wakeups, size validation, and finalized checks, but clients must still coordinate reset/close with active writers.

## Test Signals
Signals include relay open failure on invalid sizes or missing callbacks, per-CPU file creation during CPU hotplug, read/poll behavior when sub-buffers are produced, mmap page faults over the whole allocation, `relay_stats()` full/big counters, overwrite/consume behavior under slow readers, reset/flush semantics with active mappings, and kref cleanup after file release and channel close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/relay.c -->
