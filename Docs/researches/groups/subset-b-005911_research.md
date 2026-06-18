# subset-b-005911 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcupdate_trace.h -->
# sources/distributed-fs/ceph-client/include/linux/rcupdate_trace.h

## Purpose

This header exposes the Tasks Trace RCU read-side API used by tracing, BPF, ftrace, and other code that may need to protect instruction-patching or profiling-hook state while normal task scheduling and tracing constraints apply. It adapts the generic SRCU fast paths to the `rcu_tasks_trace_srcu_struct` domain and provides build-time stubs when `CONFIG_TASKS_TRACE_RCU` is disabled.

## Important APIs, Types, and Functions

The exported state is `rcu_tasks_trace_srcu_struct` under `CONFIG_TASKS_TRACE_RCU`. `rcu_read_lock_trace_held()` reports lockdep state through `srcu_read_lock_held()` when both lockdep and Tasks Trace RCU are enabled; otherwise it returns true so generic checks compile away.

The low-level pair `rcu_read_lock_tasks_trace()` and `rcu_read_unlock_tasks_trace()` return and accept a `struct srcu_ctr __percpu *` cookie from `__srcu_read_lock_fast()`. The higher-level pair `rcu_read_lock_trace()` and `rcu_read_unlock_trace()` stores that cookie in `current->trc_reader_scp` and tracks nesting in `current->trc_reader_nesting`, allowing nested trace read sections without repeated SRCU acquisition.

Grace-period and callback APIs are wrappers over SRCU: `call_rcu_tasks_trace()` calls `call_srcu()`, `synchronize_rcu_tasks_trace()` calls `synchronize_srcu()`, `rcu_barrier_tasks_trace()` calls `srcu_barrier()`, and `rcu_tasks_trace_expedite_current()` calls `srcu_expedite_current()`. `DEFINE_LOCK_GUARD_0(rcu_tasks_trace, ...)` provides cleanup-attribute guard support.

## Control Flow

The direct `rcu_read_lock_tasks_trace()` path acquires the SRCU read counter, records a lockdep acquisition, and conditionally issues `smp_mb()` unless `CONFIG_TASKS_TRACE_RCU_NO_MB` promises the architecture does not need the fallback barrier. Unlock mirrors this with a barrier before `__srcu_read_unlock_fast()` and a lockdep release.

The task-nesting path first increments the current task nesting count. If already nested, it returns immediately after lockdep acquisition. On the first entry it orders the nesting update before publishing `trc_reader_scp`, enters the SRCU domain, and optionally issues the memory barrier. Unlock reads the stored cookie, orders that read before decrementing nesting, and only exits the SRCU read side when the outermost reader ends.

When Tasks Trace RCU is disabled, the BPF JIT still needs symbol addresses to exist, so the small inline stubs call `BUG()` rather than silently accepting use.

## State and Persistence Behavior

State is per-task and in the global SRCU domain. `trc_reader_nesting` and `trc_reader_scp` persist only for the duration of the current task's nested read-side critical section. Callback state is held by SRCU until the trace grace period elapses. There is no storage across reboot or module lifetime beyond normal kernel objects.

## Dependencies and Integration Points

The header depends on `sched.h`, `rcupdate.h`, and `cleanup.h`, plus SRCU internals exposed through the RCU headers. It integrates with lockdep through `dep_map`, with BPF/ftrace code through the trace read lock names, and with architecture instrumentation policy through `CONFIG_TASKS_TRACE_RCU_NO_MB` and `ARCH_WANTS_NO_INSTR` assumptions described in comments.

## Risks

Incorrect nesting handling can strand a task in a trace read-side section or unlock the SRCU domain too early. Missing barriers on architectures that can trace code while RCU is not watching can break grace-period ordering. Calling the API when `CONFIG_TASKS_TRACE_RCU` is disabled intentionally crashes through `BUG()`, so configuration assumptions must be explicit. Misusing the cookie-returning low-level API without matching the exact cookie to unlock can corrupt SRCU accounting.

## Test Signals

Useful tests include lockdep coverage for nested `rcu_read_lock_trace()` use, BPF/ftrace attach-detach stress while callbacks are queued through `call_rcu_tasks_trace()`, grace-period tests that verify `synchronize_rcu_tasks_trace()` waits for active readers, and config-build tests with and without `CONFIG_TASKS_TRACE_RCU`, `CONFIG_DEBUG_LOCK_ALLOC`, and `CONFIG_TASKS_TRACE_RCU_NO_MB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcupdate_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcupdate_wait.h -->
# sources/distributed-fs/ceph-client/include/linux/rcupdate_wait.h

## Purpose

This header provides helper infrastructure for waiting on one or more RCU grace-period domains concurrently. It wraps callback-based RCU APIs into completion-backed waits and exposes small helpers for rescheduling or detecting blocked readers inside RCU read-side sections.

## Important APIs, Types, and Functions

`struct rcu_synchronize` combines an `rcu_head`, a `completion`, and debug old-state tracking in `struct rcu_gp_oldstate`. `wakeme_after_rcu()` is the callback used to complete a wait after a grace period. `__wait_rcu_gp()` is the implementation entry point taking an array of `call_rcu_func_t` functions and matching `rcu_synchronize` objects.

The macros `_wait_rcu_gp()`, `wait_rcu_gp()`, `wait_rcu_gp_state()`, and `synchronize_rcu_mult()` build stack arrays from variadic callback functions. `synchronize_rcu_mult()` can wait for multiple RCU flavors, such as normal RCU and tasks RCU, in parallel.

`cond_resched_rcu()` drops and reacquires a normal RCU read lock around `cond_resched()` on debug atomic sleep builds or non-preemptible RCU builds. `has_rcu_reader_blocked()` checks `current->rcu_node_entry` under `CONFIG_PREEMPT_RCU`.

## Control Flow

A caller passes callback-queueing functions such as `call_rcu_hurry` or a wrapper around `call_srcu()`. The macro creates one `rcu_synchronize` object per domain, calls into `__wait_rcu_gp()`, and sleeps in the requested task state until all callbacks run. Tiny RCU can skip normal RCU waits in `synchronize_rcu_mult()` because the calling context is already considered a grace period there.

`cond_resched_rcu()` uses the safe sequence `rcu_read_unlock(); cond_resched(); rcu_read_lock();` only where needed. `has_rcu_reader_blocked()` is a read-only state probe.

## State and Persistence Behavior

All wait objects are stack-local to the macro expansion. The only persistent state touched is the global state of whichever RCU domains receive callbacks. Debug oldstate values help diagnose grace-period ordering but are not persisted.

## Dependencies and Integration Points

The header depends on `rcupdate.h`, `completion.h`, and `sched.h`. It is used by code that needs to wait on multiple RCU domains without serializing the grace periods. SRCU users integrate by providing a wrapper function with the same shape as `call_rcu_func_t`.

## Risks

The variadic macro stores arrays on the caller's stack, so extremely large lists would be inappropriate. Passing plain `call_rcu()` instead of `call_rcu_hurry()` under lazy RCU can add multi-second delay. The `cond_resched_rcu()` helper must only be used when dropping the read lock temporarily is semantically valid.

## Test Signals

Tests should cover waits over one and multiple RCU domains, interrupted task states through `wait_rcu_gp_state()`, Tiny RCU builds, lazy callback behavior, and lockdep/debug atomic sleep checks around `cond_resched_rcu()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcupdate_wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcuref.h -->
# sources/distributed-fs/ceph-client/include/linux/rcuref.h

## Purpose

`rcuref.h` defines an RCU-aware reference counter for objects that can be looked up locklessly while their memory remains stable under RCU. It provides reference acquisition, release, dead-state detection, and saturation zones designed to tolerate races around final put operations.

## Important APIs, Types, and Functions

The counter type is `rcuref_t`, defined elsewhere as an atomic wrapper. Encoded zones include `RCUREF_ONEREF`, `RCUREF_MAXREF`, `RCUREF_SATURATED`, `RCUREF_RELEASED`, `RCUREF_DEAD`, and `RCUREF_NOREF`. The stored atomic value is one less than the public reference count for normal live counts.

`rcuref_init()` initializes the count. `rcuref_read()` reports live references and returns zero for released/dead zones. `rcuref_is_dead()` detects counters that have passed the final-release transition. `rcuref_get()` increments unless the object is already being released or dead, delegating rare saturation/dead-zone cases to `rcuref_get_slowpath()`.

`rcuref_put_rcusafe()` and `rcuref_put()` release a reference and return true only when the caller may deconstruct or schedule deconstruction. `rcuref_put()` disables preemption around the common implementation so an RCU grace period cannot pass during the race-sensitive slow path; `rcuref_put_rcusafe()` requires the caller to already be in an RCU-safe or atomic context.

## Control Flow

The get path unconditionally adds one with relaxed ordering. Normal nonnegative results succeed immediately; negative results indicate saturation or death-zone values and are repaired or rejected by the slow path.

The put path subtracts one with release ordering. A nonnegative result means other references remain. Negative results include the final drop and special zones; `rcuref_put_slowpath()` determines whether the counter can be moved to released/dead state or whether a concurrent get/put race prevents final deconstruction.

## State and Persistence Behavior

All state is the encoded atomic counter. The counter can move from live counts to saturation on overflow and to released/dead/no-reference zones near object teardown. It does not persist beyond the lifetime of the protected object, but its state determines when the object can be freed after RCU grace periods.

## Dependencies and Integration Points

The header depends on atomic operations, lockdep RCU checks, preemption control, and RCU read-side state. It integrates with `lib/rcuref.c` slow paths and is intended for objects using RCU or equivalent lifetime stabilization during lockless lookup.

## Risks

Calling `rcuref_get()` without a guarantee that object memory is stable can race with free. Calling `rcuref_put_rcusafe()` outside an RCU read-side or otherwise atomic context trips `RCU_LOCKDEP_WARN()` and can allow a grace period to pass during final-put races. Ignoring a false `rcuref_put()` return can prematurely deconstruct an object. Saturation leaks are deliberate protection against wraparound but can hide reference leaks.

## Test Signals

Stress tests should race `rcuref_get()` and `rcuref_put()` around the last reference under RCU lookup, verify dead-state detection, exercise saturation/overflow warning paths, and run with lockdep/preemption debugging to catch unsafe `rcuref_put_rcusafe()` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcuref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcutiny.h -->
# sources/distributed-fs/ceph-client/include/linux/rcutiny.h

## Purpose

This header declares and inlines the Tiny RCU implementation interface used on uniprocessor or size-constrained builds. It presents the same public shape as tree RCU where possible, but many operations collapse to simple no-ops because there is only one CPU and quiescent-state detection is trivial.

## Important APIs, Types, and Functions

`struct rcu_gp_oldstate` contains only `rgos_norm`, and `NUM_ACTIVE_RCU_POLL_FULL_OLDSTATE` is two. The full-state helpers map only normal grace-period state: `same_state_synchronize_rcu_full()`, `get_state_synchronize_rcu_full()`, `start_poll_synchronize_rcu_full()`, `poll_state_synchronize_rcu_full()`, and `cond_synchronize_rcu_full()`.

Expedited helpers alias normal polling/synchronization. `synchronize_rcu_expedited()` calls `synchronize_rcu()`. `rcu_qs()` is the core quiescent-state function, and `rcu_softirq_qs()` delegates to it. `rcu_note_context_switch()` reports a quiescent state and a Tasks RCU quiescent state. CPU hotplug hooks are defined as `NULL` and `rcutree_report_cpu_starting()` is empty.

## Control Flow

Tiny RCU's control flow removes distributed tree coordination. Context switches and softirq quiescent states call `rcu_qs()`. Conditional synchronization helpers call `might_sleep()` but do not need to wait because, in this model, eligible call sites already imply a grace period or no extra CPU coordination is required.

## State and Persistence Behavior

The exposed grace-period old state is a single unsigned long. Most watcher, stall, deferred quiescent-state, virtualization, and hotplug functions carry no persistent state in this header. Scheduler boot state is represented by `rcu_scheduler_starting()` plus inlines that treat in-kernel boot as ended and RCU as watching.

## Dependencies and Integration Points

The header includes `asm/param.h` for `HZ` and relies on RCU core declarations from surrounding includes. It is selected instead of `rcutree.h` by kernel configuration and must match the interfaces expected by generic scheduler, hotplug, stall-check, and RCU wait code.

## Risks

The simplifications are only valid for Tiny RCU configurations. Code that assumes tree-RCU expedited state exists would misread `rgos_norm`-only old states. Because hotplug callbacks are `NULL`, code must not assume runtime CPU set changes are handled through tree callbacks in Tiny builds.

## Test Signals

Build tests should cover Tiny RCU configurations, especially generic code that calls full old-state helpers, hotplug hook variables, `synchronize_rcu_expedited()`, and `rcu_note_context_switch()`. Runtime smoke tests should verify callbacks drain and quiescent states are reported during context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcutiny.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcutree.h -->
# sources/distributed-fs/ceph-client/include/linux/rcutree.h

## Purpose

`rcutree.h` declares the tree-based RCU implementation interface for SMP/preemptible kernels. It exposes scheduler, hotplug, expedited, polling, boot, and callback-migration hooks consumed by generic kernel code.

## Important APIs, Types, and Functions

Core hooks include `rcu_softirq_qs()`, `rcu_note_context_switch()`, `rcu_needs_cpu()`, `rcu_cpu_stall_reset()`, `rcu_request_urgent_qs_task()`, `synchronize_rcu_expedited()`, `rcu_barrier()`, and `rcu_momentary_eqs()`. `rcu_virt_note_context_switch()` wraps `rcu_note_context_switch(false)` and requires interrupts disabled.

`struct rcu_gp_oldstate` has normal and expedited fields, `rgos_norm` and `rgos_exp`, with `NUM_ACTIVE_RCU_POLL_FULL_OLDSTATE` set to four. Full old-state helpers compare both fields and have external implementations for get/start/poll/conditional normal and expedited synchronization.

The header declares preempt RCU hooks, boot state (`rcu_scheduler_starting()`, `rcu_scheduler_active`, `rcu_end_inkernel_boot()`, `rcu_inkernel_boot_has_ended()`, `rcu_is_watching()`), CPU hotplug callbacks, callback migration, and CPU-dead reporting.

## Control Flow

Tree RCU coordinates grace periods across CPUs and RCU nodes in implementation files. This header exposes call points: scheduler context switches report quiescent states, IRQ exit may check preempt state under `CONFIG_PROVE_RCU`, CPU hotplug calls prepare/online/offline/dead/dying hooks, and callback migration moves callbacks away from a CPU being removed.

Polling flows use old-state tokens: callers get or start a grace period, poll until complete, or conditionally wait only if the old state is still incomplete. Normal and expedited streams are tracked separately.

## State and Persistence Behavior

The header itself stores no state except declarations, but its APIs manipulate global tree RCU state, per-CPU callback queues, boot/scheduler state, and CPU hotplug membership. Old-state tokens are opaque snapshots valid only for grace-period comparison and polling.

## Dependencies and Integration Points

It integrates with the scheduler, softirq/IRQ exit paths, CPU hotplug core, virtualization context switches, arm64 early secondary boot failure handling, lockdep/prove-RCU, and generic RCU polling/wait APIs. `struct task_struct` is forward-declared for deferred quiescent-state and urgent-QS APIs.

## Risks

Misplacing context-switch or hotplug calls can stall grace periods or lose callbacks. Treating `struct rcu_gp_oldstate` fields as meaningful outside RCU helpers breaks opacity assumptions. `rcu_virt_note_context_switch()` requires interrupts disabled; violating that can race quiescent-state accounting.

## Test Signals

Signals include RCU torture tests on SMP and preemptible configurations, CPU hotplug stress, expedited grace-period tests, callback migration tests, boot-state checks, stall warning tests, and lockdep/prove-RCU coverage for IRQ exit and read-side misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcutree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcuwait.h -->
# sources/distributed-fs/ceph-client/include/linux/rcuwait.h

## Purpose

`rcuwait.h` provides a minimal wait primitive for cases that need one waiting task pointer protected by RCU-style access rather than a full wait queue. It is used where wakeup paths need to safely observe a blocked task while external locking serializes waiter setup and teardown.

## Important APIs, Types, and Functions

`__RCUWAIT_INITIALIZER()` and `rcuwait_init()` initialize the embedded `struct rcuwait` task pointer to `NULL`. `rcuwait_active()` uses `rcu_access_pointer()` to test whether a task is registered, explicitly without serialization guarantees. `prepare_to_rcuwait()` stores `current` with `rcu_assign_pointer()`. `finish_rcuwait()` and `rcuwait_wake_up()` are external implementation functions.

The waiting macros are `rcuwait_wait_event()`, `rcuwait_wait_event_timeout()`, and the internal `___rcuwait_wait_event()`. They combine `prepare_to_rcuwait()`, `set_current_state()`, signal checks, `schedule()` or `schedule_timeout()`, and `finish_rcuwait()`.

## Control Flow

A caller holding the appropriate lock calls a wait macro. The macro publishes `current`, sets the task state in a loop, checks the condition, handles pending signals for interruptible states by returning `-EINTR`, schedules, and finally removes the task from the wait object. The wake side calls `rcuwait_wake_up()`, whose barriers pair with the `set_current_state()` barrier documented in the macro.

## State and Persistence Behavior

The only state is the wait object's RCU-protected task pointer and the current task state while waiting. The pointer is transient and must be serialized by caller-owned locking around wait preparation and finish.

## Dependencies and Integration Points

The header depends on RCU pointer helpers, scheduler signal state, and kernel types. It is suitable for low-overhead one-waiter synchronization in core kernel subsystems where a full `wait_queue_head_t` is unnecessary.

## Risks

`rcuwait_active()` is only a hint, so using it as a synchronization guarantee can lose wakeups. Callers must lock around waiter setup/finish and condition updates. The condition expression is reevaluated after task-state publication; side effects in the condition can be surprising. Timeout callers must handle the standard zero/remaining-time conventions.

## Test Signals

Tests should race waiter registration, wakeup, signals, timeout expiry, and condition changes under the caller's lock. Lockdep and scheduler instrumentation should verify no sleeps occur in invalid contexts and that wakeups are not lost under high contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcuwait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcuwait_api.h -->
# sources/distributed-fs/ceph-client/include/linux/rcuwait_api.h

## Purpose

This one-line compatibility header includes `linux/rcuwait.h`. It exists so users that include the `_api` name receive the same `rcuwait` declarations without duplicating definitions.

## Important APIs, Types, and Functions

It defines no symbols directly. All APIs, including `struct rcuwait`, `rcuwait_init()`, `rcuwait_wake_up()`, `rcuwait_wait_event()`, and timeout helpers, come from `rcuwait.h`.

## Control Flow

There is no control flow in this file beyond preprocessing include resolution.

## State and Persistence Behavior

The file has no state. Runtime behavior is entirely inherited from `rcuwait.h`.

## Dependencies and Integration Points

Its only dependency and integration point is `#include <linux/rcuwait.h>`. It is useful for source compatibility where include naming changed or generated imports target the API wrapper.

## Risks

The only practical risk is assuming this header is an independent API surface. Any semantic change comes from `rcuwait.h`.

## Test Signals

Build coverage that includes `rcuwait_api.h` instead of `rcuwait.h` is sufficient; runtime testing belongs to `rcuwait.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcuwait_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reboot-mode.h -->
# sources/distributed-fs/ceph-client/include/linux/reboot-mode.h

## Purpose

This header declares the reboot-mode framework interface. Drivers can register a small object that writes a platform-specific magic value before reboot so firmware, bootloaders, or PMIC logic can distinguish normal, recovery, bootloader, panic, or other reboot reasons.

## Important APIs, Types, and Functions

`struct reboot_mode_driver` contains a `struct device *`, list node, `write()` callback taking an unsigned magic value, and a `notifier_block` used to observe reboot notifications. Registration APIs are `reboot_mode_register()`, `reboot_mode_unregister()`, `devm_reboot_mode_register()`, and `devm_reboot_mode_unregister()`.

## Control Flow

A platform driver initializes the structure and registers it. During reboot notification, the core selects the configured magic value and invokes the driver's `write()` callback. The devm variants bind unregister cleanup to device lifetime.

## State and Persistence Behavior

Kernel state is the registered driver list and notifier entry. Persistent state is platform-specific and written by the callback, often into a retained register, SRAM cell, PMIC register, or similar storage that survives reset.

## Dependencies and Integration Points

The structure references `struct device`, `struct list_head`, and `struct notifier_block`; those are expected to be available through the including context or other headers. It integrates with reboot notifiers and platform/firmware reboot reason mechanisms.

## Risks

The callback usually runs late in reboot, so it must be reliable and avoid sleeping or complex dependencies if its underlying bus is no longer available. Writing the wrong magic can boot the wrong mode. Forgetting devm or explicit unregister can leave stale notifier/list entries on driver removal.

## Test Signals

Tests should validate registration/unregistration, devm cleanup, each configured reboot mode's magic write, behavior during panic/restart paths if supported, and persistence across an actual reset on the target platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reboot-mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reboot.h -->
# sources/distributed-fs/ceph-client/include/linux/reboot.h

## Purpose

`reboot.h` is the kernel-facing system restart, halt, power-off, emergency-restart, and sys-off handler interface. It centralizes reboot modes/types, notifier registration, architecture-specific machine hooks, ordered shutdown helpers, and hardware-protection emergency actions.

## Important APIs, Types, and Functions

System event constants are `SYS_DOWN`, `SYS_RESTART`, `SYS_HALT`, and `SYS_POWER_OFF`. `enum reboot_mode` covers cold, warm, hard, soft, and GPIO reboot modes; `enum reboot_type` covers architecture/firmware mechanisms such as keyboard controller, BIOS, ACPI, EFI, and CF9 variants. Global policy variables include `reboot_mode`, `panic_reboot_mode`, `reboot_type`, `reboot_default`, `reboot_cpu`, and `reboot_force`.

Notifier and restart APIs include `register_reboot_notifier()`, `unregister_reboot_notifier()`, `devm_register_reboot_notifier()`, `register_restart_handler()`, `unregister_restart_handler()`, and `do_kernel_restart()`. Machine hooks include `migrate_to_reboot_cpu()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `machine_shutdown()`, and `machine_crash_shutdown()`.

The sys-off API defines priorities, `enum sys_off_mode`, `struct sys_off_data`, `register_sys_off_handler()`, `unregister_sys_off_handler()`, devm variants, and platform power-off registration. Higher-level commands include `kernel_restart_prepare()`, `kernel_restart()`, `kernel_halt()`, `kernel_power_off()`, `kernel_can_power_off()`, `ctrl_alt_del()`, `orderly_poweroff()`, `orderly_reboot()`, `hw_protection_trigger()`, and `emergency_restart()`.

## Control Flow

Normal restart/poweroff flows notify registered clients, prepare devices and architecture state, optionally migrate to the selected reboot CPU, and call architecture machine operations or sys-off handlers by mode and priority. `SYS_OFF_MODE_*_PREPARE` handlers may sleep; final `POWER_OFF` and `RESTART` handlers must not.

`hw_protection_trigger()` funnels to `__hw_protection_trigger()` with a default action that can be configured to shutdown or reboot. `emergency_restart()` is the interrupt-safe path and includes architecture emergency restart support.

## State and Persistence Behavior

Runtime state includes global reboot policy variables, notifier chains, restart handlers, sys-off handler registrations, and platform power-off hooks. Persistent behavior is external: firmware, platform reset causes, reboot-mode storage, or hardware protection state may survive reset, but this header only declares the entry points.

## Dependencies and Integration Points

The header depends on `linux/notifier.h`, UAPI reboot constants, `struct device`, `pt_regs`, and architecture `asm/emergency-restart.h`. It integrates with driver core devm cleanup, architecture shutdown code, panic/crash paths, orderly userspace shutdown, PMIC/power controller drivers, and thermal/hardware protection code.

## Risks

Wrong priority or mode selection can run handlers in an unsafe context. Sleeping in final sys-off handlers is invalid. Reboot notifiers and restart handlers may execute after many subsystems are quiescing, so bus and allocation assumptions are fragile. Emergency restart bypasses orderly cleanup. Hardware-protection triggers must avoid delaying beyond the damage-prevention window.

## Test Signals

Validation includes registration ordering tests, devm cleanup, restart/poweroff mode coverage, panic reboot behavior, emergency restart smoke tests, hardware-protection forced timeout behavior, and platform tests proving final handlers actually reset or power off the system.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reciprocal_div.h -->
# sources/distributed-fs/ceph-client/include/linux/reciprocal_div.h

## Purpose

This header provides precomputed reciprocal division helpers for fast division by a runtime-invariant 32-bit divisor. It replaces repeated division with multiplication and shifts, based on the Granlund-Montgomery invariant integer division algorithm.

## Important APIs, Types, and Functions

`struct reciprocal_value` stores multiplier `m` and shifts `sh1`/`sh2`. `reciprocal_value(u32 d)` computes this slow-path representation. `reciprocal_divide(u32 a, struct reciprocal_value R)` performs the fast-path division using a 64-bit multiply high and correction shifts.

`struct reciprocal_value_adv` stores multiplier `m`, shift `sh`, exponent `exp`, and `is_wide_m`. `reciprocal_value_adv(u32 d, u8 prec)` computes a more JIT-friendly representation for generated code paths that can trade setup cost for fewer emulated operations.

## Control Flow

Callers compute the reciprocal once for a divisor that remains stable, then use `reciprocal_divide()` for each dividend. The advanced flow handles special divisors, may pre-shift even divisors when the multiplier is wide, and then emits either a simple shift, wide-multiplier correction sequence, or multiply/shift sequence in generated code.

## State and Persistence Behavior

The only state is the caller-owned reciprocal structure. It is deterministic for the divisor and precision and can be cached anywhere the divisor is cached. No global state is modified.

## Dependencies and Integration Points

The header depends on fixed-width kernel types. It integrates with networking, hashing, schedulers, BPF/JIT or emulation code, and other hot paths that repeatedly divide by the same 32-bit value.

## Risks

Using a reciprocal computed for one divisor with another divisor gives silent wrong results. Divisor zero must be rejected before computation. The advanced helper excludes the `d > 1U << 31` case described in comments and requires careful handling around powers of two, wide multipliers, and precision.

## Test Signals

Exhaustive or randomized tests should compare reciprocal results against hardware division across divisors, including 1, powers of two, large values near `2^31`, odd/even divisors, and maximum dividends. JIT tests should verify emitted sequences match `n / d` for the documented exceptional cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reciprocal_div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ref_tracker.h -->
# sources/distributed-fs/ceph-client/include/linux/ref_tracker.h

## Purpose

`ref_tracker.h` declares optional debugging infrastructure for tracking reference acquisitions and releases. It helps detect leaked, untracked, or double-freed references by keeping active and quarantined tracker records with stack depot support.

## Important APIs, Types, and Functions

`struct ref_tracker_dir` contains real fields only under `CONFIG_REF_TRACKER`: a spinlock, quarantine capacity, `untracked` and `no_tracker` refcounts, a dead flag, active and quarantine lists, and a static class string. Without the config, the struct is empty.

`ref_tracker_dir_init()` initializes lists, lock, quarantine count, counters, class, debugfs, and stack depot. Other active APIs include `ref_tracker_dir_exit()`, `ref_tracker_dir_print_locked()`, `ref_tracker_dir_print()`, `ref_tracker_dir_snprint()`, `ref_tracker_alloc()`, and `ref_tracker_free()`. Debugfs helpers are active only under `CONFIG_DEBUG_FS`.

## Control Flow

Tracked users initialize a directory, allocate a tracker on each reference acquisition, and free the tracker on each reference release. Active trackers stay on the directory list; freed trackers can move to quarantine for postmortem diagnostics. Directory exit reports or validates remaining active entries.

With `CONFIG_REF_TRACKER` disabled, all functions are inline no-ops returning success or zero, allowing instrumentation to remain compiled in callers without runtime cost.

## State and Persistence Behavior

Runtime state is per-directory active/quarantine lists, counters, stack depot handles in implementation-private tracker objects, and optional debugfs entries. There is no persistent storage beyond kernel runtime.

## Dependencies and Integration Points

The header depends on `refcount.h`, spinlocks, list handling, stack depot, debugfs, and GFP allocation flags. It integrates with subsystems that want reference lifecycle diagnostics without changing production behavior when disabled.

## Risks

Forgetting to free trackers creates diagnostic leaks. Calling alloc/free after `ref_tracker_dir_exit()` can race the dead flag or list teardown. Class strings must be static. In no-op builds, bugs are intentionally invisible, so tests that rely on tracker diagnostics need the config enabled.

## Test Signals

Tests should exercise balanced alloc/free, leaked references at dir exit, double-free/untracked paths, quarantine limits, debugfs output, and disabled-config build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ref_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/refcount.h -->
# sources/distributed-fs/ceph-client/include/linux/refcount.h

## Purpose

`refcount.h` defines the kernel's saturating reference-count API. It provides a safer subset of atomic operations for object lifetimes, preventing overflow wraparound into use-after-free and warning on underflow, zero-to-nonzero increments, and leak-prone decrements.

## Important APIs, Types, and Functions

The type is `refcount_t` from `refcount_types.h`. Constants include `REFCOUNT_INIT(n)`, `REFCOUNT_MAX`, and `REFCOUNT_SATURATED`. Saturation warning reasons are enumerated by `enum refcount_saturation_type`, reported through `refcount_warn_saturate()`.

Set/read APIs are `refcount_set()`, `refcount_set_release()`, and `refcount_read()`. Increment/add APIs include `refcount_add_not_zero()`, `refcount_add_not_zero_acquire()`, `refcount_add()`, `refcount_inc_not_zero()`, `refcount_inc_not_zero_acquire()`, and `refcount_inc()`, plus internal variants that return the old value.

Decrement APIs include `refcount_sub_and_test()`, `refcount_dec_and_test()`, and `refcount_dec()`. External helpers handle lock-coupled final drops: `refcount_dec_if_one()`, `refcount_dec_not_one()`, `refcount_dec_and_mutex_lock()`, `refcount_dec_and_lock()`, and `refcount_dec_and_lock_irqsave()`.

## Control Flow

Not-zero add/inc operations use `atomic_try_cmpxchg_*()` loops to avoid acquiring references from zero. Plain add/inc use relaxed fetch-add then warn and saturate on zero or overflow. Decrement-and-test uses release fetch-sub and, on the one-to-zero transition, an acquire barrier via `smp_acquire__after_ctrl_dep()` before returning true to allow object free.

`refcount_dec()` is for cases where zero is not expected; if the old value is one or less it warns and saturates/leaks instead of allowing underflow. Acquire variants are intended for reused memory such as `SLAB_TYPESAFE_BY_RCU` where secondary validation must happen after the refcount is taken.

## State and Persistence Behavior

State is a single `atomic_t refs` in each object. Counters can become saturated at `REFCOUNT_SATURATED` and stay there, intentionally leaking the object rather than risking wraparound. There is no persistent state outside object lifetime.

## Dependencies and Integration Points

The header depends on atomic operations, compiler annotations, limits, spinlock and mutex types, and `refcount_types.h`. It is a common primitive for kernel object lifetimes, RCU-safe lookup patterns, lock-coupled deletion, and driver resource management.

## Risks

Using `refcount_inc()` on a possibly zero counter is a use-after-free bug and triggers warnings. Using relaxed increments without an external lifetime guarantee can expose stale object state. Misusing `refcount_dec()` when final free is expected causes warnings/leaks; final-release callers need `refcount_dec_and_test()` or lock-coupled helpers. Large batched adds can stress the saturation safety assumptions.

## Test Signals

Tests should cover normal inc/dec lifecycles, zero-to-nonzero attempts, overflow saturation, underflow saturation, acquire/release ordering under `SLAB_TYPESAFE_BY_RCU`, and lock helper behavior with mutex/spinlock final drops. KUnit or LKDTM-style tests can assert warnings and leak protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/refcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/refcount_api.h -->
# sources/distributed-fs/ceph-client/include/linux/refcount_api.h

## Purpose

This compatibility wrapper includes `linux/refcount.h`, exposing the full refcount API through an `_api` include name.

## Important APIs, Types, and Functions

It defines no direct symbols. The available APIs are those from `refcount.h`: `refcount_set()`, `refcount_inc*()`, `refcount_dec*()`, saturation constants, and lock-coupled helpers.

## Control Flow

There is no runtime control flow in this file. It affects preprocessing only.

## State and Persistence Behavior

No state is introduced here; all state belongs to `refcount_t` objects declared by users of the included API.

## Dependencies and Integration Points

The only dependency is `#include <linux/refcount.h>`. It exists to satisfy include paths that distinguish API wrappers from type headers.

## Risks

The wrapper can obscure that all semantics come from `refcount.h`. Semantic risks are those of the underlying refcount operations.

## Test Signals

Compilation of users including `refcount_api.h` is the relevant signal; runtime behavior should be tested through `refcount.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/refcount_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/refcount_types.h -->
# sources/distributed-fs/ceph-client/include/linux/refcount_types.h

## Purpose

This header defines the storage type for Linux saturating reference counters without pulling in the full operation API.

## Important APIs, Types, and Functions

`typedef struct refcount_struct { atomic_t refs; } refcount_t;` is the sole type. It stores an `atomic_t` counter and is documented as saturating at `REFCOUNT_SATURATED` when used through the API in `refcount.h`.

## Control Flow

There is no executable control flow. Operation semantics are implemented by `refcount.h` and its C helpers.

## State and Persistence Behavior

Each `refcount_t` embeds one atomic counter in its containing object. Its lifetime and persistence match that object. Saturation behavior is not implemented here but is part of the type contract.

## Dependencies and Integration Points

The header depends on `linux/types.h`, which must provide `atomic_t` through the include environment. It is included by structures that need a `refcount_t` field without the full inline operation definitions.

## Risks

Directly manipulating `refs` with atomic operations bypasses saturation and warning semantics. Users should include `refcount.h` for operations and treat the field as private.

## Test Signals

Build checks should ensure structures can include `refcount_t` without dependency cycles. Runtime tests belong to `refcount.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/refcount_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regmap.h -->
# sources/distributed-fs/ceph-client/include/linux/regmap.h

## Purpose

`regmap.h` declares the generic register-map framework used by device drivers to access hardware registers through a common abstraction across I2C, SPI, MMIO, SPMI, SoundWire, MDIO, FSI, and other buses. It also exposes register caching, range translation, field access, polling helpers, and generic regmap-backed IRQ chips.

## Important APIs, Types, and Functions

Core data definitions include `enum regcache_type`, `struct reg_default`, `struct reg_sequence`, `struct regmap_range`, `struct regmap_access_table`, `struct regmap_config`, `struct regmap_range_cfg`, `struct regmap_sdw_mbq_cfg`, and `struct regmap_bus`. `regmap_config` is the central device-side contract: register/value bit widths, stride/shift/base, access callbacks/tables, default values, cache type, endian policy, raw I/O limits, locking policy, hardware spinlock configuration, no-increment access, single/bulk/multi-write behavior, and paged ranges.

Initialization macros wrap lockdep-keyed internal functions: `regmap_init*()` and `devm_regmap_init*()` variants exist for generic bus contexts plus I2C, MDIO, SCCB, SlimBus, SPI, SPMI base/ext, 1-Wire, MMIO with optional clock, AC97, SoundWire, SoundWire MBQ, I3C, SPI AVMM, and FSI. Runtime access APIs include `regmap_read()`, `regmap_write()`, raw/bulk/noinc/multi read-write, async writes, `regmap_update_bits_base()`, inline `regmap_update_bits*()`, `regmap_set_bits()`, `regmap_clear_bits()`, `regmap_assign_bits()`, `regmap_test_bits()`, and polling macros.

Cache APIs include `regcache_sync()`, `regcache_sync_region()`, `regcache_drop_region()`, `regcache_cache_only()`, `regcache_cache_bypass()`, `regcache_mark_dirty()`, and `regcache_reg_cached()`. Field APIs include `struct reg_field`, `REG_FIELD`, `REG_FIELD_ID`, allocation/free/devm/bulk helpers, and `regmap_field_*()`/`regmap_fields_*()` operations. IRQ support is described by `struct regmap_irq_type`, `struct regmap_irq`, `struct regmap_irq_chip`, registration/deletion APIs, and virtual IRQ/domain lookup helpers.

## Control Flow

A driver defines a `regmap_config`, initializes a map through the appropriate bus/devm macro, then performs register operations through the generic API. The framework formats register addresses and values, applies masks and endian conversions, checks readable/writeable/volatile/precious/noinc ranges, serializes access using mutex/spinlock/custom/hwspinlock policy, consults or updates cache state, and calls bus-specific operations.

`regmap_update_bits*()` performs read-modify-write unless a custom bus `reg_update_bits` path exists. Polling macros repeatedly call `regmap_read()` or `regmap_field_read()` until the caller's condition or timeout. Range configs implement indirect/paged register access by updating a selector register before using a window. IRQ chips read status registers, apply mask/unmask/ack/wake/type config policy, and map regmap IRQ descriptors into Linux IRQ domains.

When `CONFIG_REGMAP` is disabled, most APIs become warning stubs returning `-EINVAL`, `NULL`, or safe default values, allowing generic code to build while detecting invalid runtime use.

## State and Persistence Behavior

Runtime state lives in opaque `struct regmap`: bus context, device pointer, lock state, cache, async queue, range/page state, clock attachment, and optional IRQ chip data. Cache state can intentionally diverge from hardware during cache-only or bypass modes and must be synchronized explicitly. Register writes may persist in hardware across driver lifetime, suspend, or reset depending on the device.

## Dependencies and Integration Points

The header depends on device model types, lockdep, lists, rbtrees, fwnode, delays, polling, and bus-specific forward declarations. It is a major integration point for MFD, regulator, clock, GPIO, audio, PMIC, networking PHY, SoundWire, and interrupt-controller drivers. Regulator helpers in `regulator/driver.h` frequently use regmap-backed selector, enable, bypass, discharge, ramp, and current-limit operations.

## Risks

Incorrect register bit widths, endian settings, stride/shift/base, cache defaults, or volatile/precious markings can corrupt hardware state or return stale values. Relaxed MMIO requires explicit barriers when ordering matters. Disabling locking is only safe with external serialization. Cache-only and bypass modes can lose writes if dirty/sync handling is wrong. Clear-on-read status registers must be marked precious or handled carefully. Regmap IRQ inversion and mask/unmask polarity fields are easy to misconfigure.

## Test Signals

Tests should cover bus-specific init, lockdep keys, raw/bulk/noinc limits, endian formatting, range access, cache sync/drop/bypass/cache-only behavior, update-bits change reporting, async completion, polling timeouts, field allocation and per-id fields, disabled-`CONFIG_REGMAP` build stubs, and regmap IRQ masking/acking/type/wake behavior using mock devices or regmap KUnit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regset.h -->
# sources/distributed-fs/ceph-client/include/linux/regset.h

## Purpose

`regset.h` defines the architecture-neutral interface for exposing user-mode machine state to ptrace, core dumps, and related process inspection APIs. It models CPU or ABI state as register sets with get/set/active/writeback callbacks.

## Important APIs, Types, and Functions

`struct membuf` and helpers `membuf_zero()`, `membuf_write()`, `membuf_at()`, and `membuf_store()` provide bounded kernel-buffer output for regset getters. Callback types include `user_regset_active_fn`, `user_regset_get2_fn`, `user_regset_set_fn`, and `user_regset_writeback_fn`.

`struct user_regset` describes one register set: slot count, slot size, alignment, bias, ELF core note type/name, and callbacks. `USER_REGSET_NOTE_TYPE()` fills note metadata from `NT_*`/`NN_*` symbols. `struct user_regset_view` groups regsets for an ABI view and supplies ELF machine flags, machine ID, and OS ABI.

Runtime APIs include `task_user_regset_view()`, `user_regset_copyin()`, `user_regset_copyin_ignore()`, `regset_get()`, `regset_get_alloc()`, `copy_regset_to_user()`, and inline `copy_regset_from_user()`.

## Control Flow

Inspection code obtains a task's native `user_regset_view`, selects a regset by index, and invokes get/set helpers. Getters write into `struct membuf` with truncation-aware helpers. Setters receive byte offsets and counts that the caller has already validated for alignment and size. Copy-in helpers advance position/count and either copy from kernel buffers or user buffers with `__copy_from_user()`.

Regset callbacks must be called only for the current thread or stopped/traced inactive targets, with `wait_task_inactive()` synchronization as documented. Optional writeback callbacks flush hardware-backed or user-memory-backed register windows immediately or before the next context switch.

## State and Persistence Behavior

The header defines descriptors, not storage. Actual state is architecture thread state, FPU/vector state, TLS/GDT-like state, or user-memory-backed register windows. Core-dump note metadata determines how much state persists into core files.

## Dependencies and Integration Points

It depends on compiler annotations, uaccess, task structures, ELF note constants, and architecture implementations of regset views. It integrates with ptrace, coredump generation, signal/user context handling, and process memory access code.

## Risks

Callbacks are not responsible for validating alignment or bounds, so callers must enforce the documented preconditions. Accessing a running target can capture inconsistent or corrupted state. `membuf_store()` requires proper alignment for scalar stores. User copies can fault. Backward compatibility requires padding/default data for inactive parts of variable-sized regsets.

## Test Signals

Tests should cover ptrace get/set for each architecture regset, partial offset/count copies, inactive/default regset areas, core note generation, compat ABI views, user-copy faults, writeback behavior, and stopped-task synchronization under SIGKILL races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/act8865.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/act8865.h

## Purpose

This header provides platform-data IDs and initialization structures for Active-Semi ACT8600, ACT8865, and ACT8846 PMU regulator drivers.

## Important APIs, Types, and Functions

It defines regulator ID enums for ACT8600 rails (`DCDC1` through `SUDCDC4` and `LDO5` through `LDO10`), ACT8865 rails (`DCDC1` through `DCDC3`, `LDO1` through `LDO4`, `ACT8865_REG_NUM`), and ACT8846 regulators (`REG1` through `REG12`, `ACT8846_REG_NUM`). A chip enum distinguishes `ACT8600`, `ACT8865`, and `ACT8846`.

`struct act8865_regulator_data` carries a regulator ID, name, `regulator_init_data`, and optional OF node. `struct act8865_platform_data` carries the number of regulators and an array pointer.

## Control Flow

Board or legacy platform code populates the platform data before probe. The driver iterates the regulator entries, matches IDs to descriptors, applies constraints/init data, and registers each rail with the regulator core.

## State and Persistence Behavior

The header defines static platform configuration only. Runtime rail enable/voltage state is managed by the ACT88xx driver, hardware registers, and regulator core constraints.

## Dependencies and Integration Points

It depends on `regulator/machine.h` for `regulator_init_data` and references `struct device_node`. It integrates with legacy platform data and device-tree-aware regulator registration.

## Risks

Wrong IDs or counts can bind constraints to the wrong rail. Missing init data can leave supplies unavailable. OF node and platform data duplication must remain consistent.

## Test Signals

Probe tests should verify each chip variant's ID table, platform-data counts, OF node association, regulator names, and constraint application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/act8865.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/arizona-ldo1.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/arizona-ldo1.h

## Purpose

This header defines platform data for the Cirrus/Wolfson Arizona codec LDO1 regulator.

## Important APIs, Types, and Functions

`struct arizona_ldo1_pdata` contains a single `const struct regulator_init_data *init_data` pointer for LDO1 regulator constraints and consumer mapping.

## Control Flow

The parent Arizona MFD or platform code passes the pdata to the LDO1 regulator driver, which uses the init data during regulator registration.

## State and Persistence Behavior

No runtime state is defined here. It is static configuration; actual regulator state is in hardware and regulator core objects.

## Dependencies and Integration Points

It forward-declares `struct regulator_init_data` and integrates with Arizona MFD platform-data plumbing.

## Risks

Null or stale init data can leave LDO1 unconstrained or unavailable to consumers.

## Test Signals

Build/probe tests should validate that Arizona LDO1 registration receives expected constraints and consumer supplies through this structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/arizona-ldo1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/arizona-micsupp.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/arizona-micsupp.h

## Purpose

This header defines platform data for the Arizona microphone-supply regulator.

## Important APIs, Types, and Functions

`struct arizona_micsupp_pdata` contains `const struct regulator_init_data *init_data` describing regulator constraints and consumers for the microphone supply.

## Control Flow

The Arizona parent driver supplies this structure to the micsupp regulator child, which registers the regulator with the core using the init data.

## State and Persistence Behavior

The header has no runtime state. Hardware enable/voltage behavior belongs to the regulator driver and codec hardware.

## Dependencies and Integration Points

It forward-declares `regulator_init_data` and integrates with Arizona MFD platform data.

## Risks

Incorrect constraints can affect microphone bias/supply sequencing and audio capture reliability.

## Test Signals

Probe tests should verify micsupp constraints, enable behavior, and consumer supply lookup on boards using platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/arizona-micsupp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/consumer.h

## Purpose

`consumer.h` declares the regulator framework API used by device drivers that consume power rails. It covers supply acquisition, enable/disable, voltage/current/load/mode control, bulk operations, notifier registration, suspend configuration, OF lookup, and stubs for builds without regulator support.

## Important APIs, Types, and Functions

Generic modes are `REGULATOR_MODE_FAST`, `NORMAL`, `IDLE`, and `STANDBY`; error flags describe under-voltage, over-current, regulation failure, general failure, over-temperature, and warning variants. `struct pre_voltage_change_data` is notifier payload. `struct regulator_bulk_data` pairs supply names with acquired consumer handles and initial load.

Acquisition APIs include `regulator_get()`, `devm_regulator_get()`, exclusive and optional variants, `devm_regulator_get_enable*()`, OF variants, supply alias registration, and bulk get helpers. Control APIs include `regulator_enable()`, disable/force/deferred disable, `regulator_is_enabled()`, voltage list/map/set/get/sync/time/tolerance helpers, current limit APIs, power budget APIs, mode/load/bypass/error APIs, hardware VSEL/regmap queries, and hardware enable.

Notification and metadata APIs include notifier register/unregister/devm helpers, suspend voltage/enable/disable helpers, drvdata get/set, bulk supply-name helpers, and `regulator_is_equal()`. When `CONFIG_REGULATOR` is disabled, stubs return success for many optional operations, `NULL` for normal get, `ERR_PTR(-ENODEV)` for optional/exclusive get, or negative errors for queries that cannot be faked.

## Control Flow

A consumer gets one or more supplies, optionally sets load or voltage/current constraints, enables supplies before hardware access, and disables/frees them during shutdown. Bulk helpers perform these steps over arrays and unwind on errors in implementation. Notifier users subscribe to events from the regulator core. OF helpers resolve supplies from a given device node.

Voltage convenience helpers first try a target-only range and then a wider fallback range (`regulator_set_voltage_triplet()` and `_tol()`).

## State and Persistence Behavior

Consumer handles track open/use counts, enable votes, voltage/current/load requests, bypass requests, and notifier registrations in regulator core state. The requested state affects hardware rail configuration and can persist while consumers are bound or, depending on hardware and bootloader, across suspend/reset.

## Dependencies and Integration Points

The header depends on `err.h`, suspend types, regulator UAPI/internal event definitions, OF device nodes, regmap, and device model types. It is used by most device drivers that need named supplies from DT, ACPI, board data, or regulator aliases.

## Risks

Ignoring `ERR_PTR()` from optional/exclusive gets, assuming disabled-config stubs reflect real hardware, mismatching enable/disable calls, or setting voltage/current outside board constraints can break devices. Bulk operations need proper unwind. Query functions can return negative errno and should not be treated as physical zero. Load/mode requests affect DRMS and shared rail efficiency.

## Test Signals

Tests should cover supply resolution, optional-vs-required behavior, enable count balancing, bulk get/enable unwind, voltage/current constraint enforcement, notifiers, bypass/load/mode behavior, OF bulk get, and disabled-`CONFIG_REGULATOR` build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/coupler.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/coupler.h

## Purpose

This header declares the regulator coupler API used to coordinate voltage changes across rails that must maintain a bounded voltage relationship, such as CPU/core SRAM rail pairs.

## Important APIs, Types, and Functions

`struct regulator_coupler` contains a list node and callbacks: mandatory `attach_regulator()`, optional `detach_regulator()`, and optional `balance_voltage()`. Registration and core helpers include `regulator_coupler_register()`, `regulator_check_consumers()`, `regulator_check_voltage()`, `regulator_get_voltage_rdev()`, `regulator_set_voltage_rdev()`, and `regulator_do_balance_voltage()`. Disabled regulator builds provide no-op or `-EINVAL` stubs.

## Control Flow

The core calls `attach_regulator()` when coupled regulators are created, then calls `balance_voltage()` during voltage changes while all involved regulator consumer locks are held. If no custom balancer exists, generic balancing is used. The coupler validates consumer min/max requirements and updates coupled rails in a safe order.

## State and Persistence Behavior

Coupling state is held in regulator core objects and the registered coupler list. Actual voltage state persists in hardware according to regulator driver behavior. This header does not define storage beyond the coupler object.

## Dependencies and Integration Points

It depends on errno, suspend state, and regulator core forward declarations. It integrates with `struct coupling_desc` in `driver.h`, board constraints such as `max_spread`, and suspend-state voltage programming.

## Risks

Bad balancing can violate maximum spread, brown out a rail, or deadlock if lock ordering is wrong. Attach callbacks returning the wrong code can bind unrelated regulators or leave required rails uncoupled. Disabled-config stubs hide coupling behavior.

## Test Signals

Tests should exercise attach/detach, multi-rail voltage increases/decreases, suspend-state balancing, max-spread enforcement, consumer constraint conflicts, and deadlock detection under ww-mutex locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/coupler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/da9121.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/da9121.h

## Purpose

This header defines platform data for Dialog/Renesas DA9121-family buck converters, including single-channel dual-phase and dual-channel single-phase variants.

## Important APIs, Types, and Functions

IDs are `DA9121_IDX_BUCK1`, `DA9121_IDX_BUCK2`, and `DA9121_IDX_MAX`. `struct da9121_pdata` carries `num_buck`, optional regulator-enable GPIO descriptors `gpiod_ren[]`, OF regulator nodes `reg_node[]`, and per-buck `regulator_init_data *`.

## Control Flow

Platform code or the parent driver fills the array entries before probe. The regulator driver uses `num_buck` to decide how many rails to register, applies GPIO external enable controls if present, maps OF nodes, and registers each buck with the regulator core.

## State and Persistence Behavior

The pdata is static configuration. Runtime state includes GPIO enable state, PMIC register state, and regulator core constraints.

## Dependencies and Integration Points

It depends on `regulator/machine.h`, `struct gpio_desc`, and OF nodes. It integrates with GPIO descriptor and regulator core initialization.

## Risks

Mismatched `num_buck` and array contents can register missing or invalid rails. Incorrect enable GPIO polarity/ownership can prevent power sequencing.

## Test Signals

Probe tests should cover each supported chip topology, external REN GPIO behavior, OF node mapping, and constraint application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/da9121.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/da9211.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/da9211.h

## Purpose

This header supplies platform data and chip IDs for the DA9211/DA9212/DA9213/DA9223/DA9214/DA9224/DA9215/DA9225 regulator family.

## Important APIs, Types, and Functions

`DA9211_MAX_REGULATORS` is two. `enum da9211_chip_id` identifies chip variants. `struct da9211_pdata` contains `num_buck`, optional per-regulator enable GPIO descriptors, OF nodes, and `regulator_init_data` pointers.

## Control Flow

During probe, the driver interprets chip ID and `num_buck` to register one four-phase buck or two two-phase bucks, using per-rail GPIO and init data if supplied.

## State and Persistence Behavior

Configuration is platform-provided and static. Runtime enable/voltage and phase behavior is managed by the regulator driver and hardware.

## Dependencies and Integration Points

It depends on regulator machine data, GPIO descriptors, and OF nodes. It integrates with board/platform data for Dialog PMIC rails.

## Risks

Wrong phase/topology selection can expose the wrong number of regulators or unsafe current capability. Incorrect GPIO or OF mapping can break enable sequencing.

## Test Signals

Variant-specific probe tests should verify rail count, phase mode, constraints, GPIO enable handling, and device-tree/platform-data parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/da9211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/db8500-prcmu.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/db8500-prcmu.h

## Purpose

This header enumerates DB8500 PRCMU-managed power domain regulators and switches.

## Important APIs, Types, and Functions

`enum db8500_regulator_id` lists voltage regulators (`VAPE`, `VARM`, `VMODEM`, `VPLL`, `VSMPS1-3`, `VRF1`) and switch regulators for DSP/APIPE/SGA/B2R2/MCDE/ESRAM domains, ending with `DB8500_NUM_REGULATORS`.

## Control Flow

Drivers use the enum IDs to index descriptor tables and register PRCMU-controlled rails/switches with the regulator core.

## State and Persistence Behavior

No state is defined here. Runtime state resides in PRCMU firmware/hardware and regulator core objects.

## Dependencies and Integration Points

This header is standalone. It integrates with ST-Ericsson DB8500 platform regulator drivers and consumer supply mappings.

## Risks

Changing enum order breaks descriptor indexing and board data. Mistaking switch domains for voltage regulators can expose unsupported operations.

## Test Signals

Build/probe tests should ensure every ID has a descriptor, correct operation capabilities, and expected consumer mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/db8500-prcmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/driver.h

## Purpose

`driver.h` declares the regulator provider-side API. It is used by PMIC, fixed, GPIO, and SoC regulator drivers to describe rails, implement operations, register regulators, use common regmap helpers, report hardware errors, and participate in coupling.

## Important APIs, Types, and Functions

Status and severity enums include `enum regulator_status` and `enum regulator_detection_severity`. Voltage helper macros wrap `LINEAR_RANGE`. `struct regulator_ops` is the main operation table: list/map/set/get voltage, current and input current limits, protection thresholds, active discharge, enable/disable/is_enabled, mode, error flags, enable/ramp/settling timing, soft start, status, optimum mode/load, bypass, suspend settings, resume, and pull-down.

`struct regulator_desc` is the static descriptor: names, OF matching/parsing callbacks, IDs, ops, IRQ, type, owner, voltage/current tables and linear ranges, regmap registers/masks for selectors/enables/bypass/discharge/soft-start/pull-down/ramp, enable/off-on timing, polling timing, and OF mode mapping. `struct regulator_config` supplies runtime data: device, init data, private driver data, OF node, regmap, and enable GPIO.

Runtime core structures include `struct regulator_err_state`, `struct regulator_irq_data`, `struct regulator_irq_desc`, `struct coupling_desc`, and the core-owned `struct regulator_dev`. Registration and helper APIs include `regulator_register()`, `devm_regulator_register()`, `regulator_unregister()`, notifier calls, IRQ helpers, `rdev_get_*()`, mapping/listing helpers, regmap-backed get/set/enable/bypass/discharge/current/ramp helpers, `regulator_find_closest_bigger()`, and `regulator_sync_voltage_rdev()`.

## Control Flow

A provider defines descriptors and ops, builds a `regulator_config`, and registers each rail. The core combines descriptor capabilities with board constraints from machine/OF data, creates `regulator_dev`, handles consumer requests, serializes operations through regulator mutexes, and calls provider ops or common regmap helpers. Error IRQ helpers map hardware status to regulator events/errors and may disable/re-enable IRQs, retry reads, or invoke a protection callback/poweroff on repeated fatal failures.

Regmap helper flows use descriptor registers and masks to map selectors, enable bits, bypass bits, discharge bits, ramp delay tables, and current-limit tables into hardware writes. Coupled regulators coordinate voltage changes through `coupling_desc` and coupler callbacks.

## State and Persistence Behavior

`struct regulator_dev` carries core runtime state: exclusive/open/use/bypass counts, global and consumer lists, coupling, notifier chain, ww mutex owner, module owner, device objects, constraints, supply tree link, regmap, delayed disable work, driver data, debugfs, enable GPIO state, last-off timestamp, cached errors, and power budget accounting. Hardware register state may persist through suspend/reset depending on PMIC behavior.

## Dependencies and Integration Points

The header depends on device model, linear ranges, notifier, consumer API, ww mutexes, GPIO descriptors, regmap, debugfs, workqueues, and module ownership. It integrates provider drivers with consumers, OF constraints, machine constraints, regmap, IRQ core, poweroff protection, suspend/resume, and coupling.

## Risks

Descriptor mistakes are high impact: wrong masks/registers, voltage tables, selector ranges, enable polarity, ramp units, or timing can damage hardware or break boot. Provider ops must respect constraints and return negative errno consistently. IRQ helper callbacks must initialize error/notification fields correctly. Direct access to `regulator_dev` outside the core is forbidden except narrowly documented notification injection. Coupling and ww mutex use can deadlock if bypassed.

## Test Signals

Tests should cover provider registration/unregistration, descriptor validation, voltage mapping/listing/set/get, regmap enable/disable/bypass/discharge/ramp/current helpers, suspend states, delayed disable/off-on timing, notifier/event mapping, IRQ retry/fatal behavior, coupling balance, debugfs, and consumer API integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/fan53555.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/fan53555.h

## Purpose

This header defines platform data for the Fairchild FAN53555 buck regulator.

## Important APIs, Types, and Functions

VSEL IDs are `FAN53555_VSEL_ID_0` and `_1`. Slew-rate enums encode rates from 64 mV/us down to 0.5 mV/us. `struct fan53555_platform_data` supplies regulator init data, selected slew rate, and sleep VSEL ID.

## Control Flow

The driver reads platform data during probe, programs the selected slew rate and sleep selector, and registers the regulator using the supplied constraints.

## State and Persistence Behavior

The header is static configuration. Runtime voltage selector and slew-rate registers are hardware state.

## Dependencies and Integration Points

It forward-relies on `regulator_init_data` from including contexts and integrates with legacy board data for FAN53555.

## Risks

Incorrect slew rates can violate rail settling assumptions. Wrong sleep VSEL selection can program unsafe suspend voltage.

## Test Signals

Probe and suspend/resume tests should validate slew-rate programming, active/sleep VSEL selection, and voltage transition timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/fan53555.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/fixed.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/fixed.h

## Purpose

`fixed.h` declares platform data and helper registration for fixed-voltage regulators, including always-on dummy fixed supplies.

## Important APIs, Types, and Functions

`struct fixed_voltage_config` contains supply name, input supply, output microvolts, startup/off-on delays, boot enable state, and regulator init data. `regulator_register_always_on()` registers an always-on fixed regulator when regulator support is enabled; otherwise it returns `NULL`. `regulator_register_fixed()` is a macro alias using the `"fixed-dummy"` name and zero microvolts.

## Control Flow

Board code can create a platform device for an always-on or fixed dummy supply. The fixed regulator driver consumes the config, registers a regulator with fixed voltage and optional startup timing, and exposes it to consumers.

## State and Persistence Behavior

The header defines static config. Runtime state includes platform device lifetime, regulator core state, optional GPIO/driver state in implementation, and boot-on/always-on constraints.

## Dependencies and Integration Points

It uses `regulator_init_data`, `regulator_consumer_supply`, and platform devices. It integrates with board files and fixed regulator consumers.

## Risks

Using a dummy fixed regulator can mask missing real supply modeling. Wrong microvolt values or boot-on flags can cause consumers to skip required sequencing.

## Test Signals

Tests should verify always-on registration, consumer mapping, fixed voltage reporting, startup/off-on delays, and disabled-regulator stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/fixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/gpio-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/gpio-regulator.h

## Purpose

This header defines platform data for regulators whose voltage or current is selected by GPIO pin states.

## Important APIs, Types, and Functions

`struct gpio_regulator_state` maps a value in microvolts or microamps to a GPIO bitfield. `struct gpio_regulator_config` includes supply/input names, boot enable state, startup delay, GPIO flags and count, available states, regulator type (`REGULATOR_CURRENT` or `REGULATOR_VOLTAGE`), and init data.

## Control Flow

The GPIO regulator driver uses the state table to map requested voltage/current values to GPIO output patterns. During probe it configures GPIOs with initial flags, applies boot/init constraints, and registers a regulator with the core.

## State and Persistence Behavior

Static state is the value-to-GPIO table. Runtime state is GPIO output levels, regulator core constraints, and hardware rail behavior driven by the GPIO pins.

## Dependencies and Integration Points

It depends on GPIO descriptor flags and regulator machine/type definitions. It integrates with board files and systems where external regulator selection pins are controlled directly by the SoC.

## Risks

Wrong bitfield ordering or GPIO flags can select the wrong voltage/current. Missing states can make valid consumer requests fail. Boot state must match actual pin/hardware state to avoid glitches.

## Test Signals

Tests should verify value-to-GPIO mapping, boot initial state, enable sequencing, voltage/current request failures for unsupported states, and polarity/flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/gpio-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/lp3971.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/lp3971.h

## Purpose

This header defines regulator IDs and platform data for the National/TI LP3971 PMIC.

## Important APIs, Types, and Functions

IDs cover `LP3971_LDO1` through `LDO5`, `DCDC1` through `DCDC3`, with `LP3971_NUM_REGULATORS` equal to eight. `struct lp3971_regulator_subdev` pairs an ID with init data. `struct lp3971_platform_data` provides count and subdevice array.

## Control Flow

The driver iterates platform subdevices, maps IDs to descriptors, and registers the specified rails with constraints.

## State and Persistence Behavior

No runtime state is defined here. PMIC register state and regulator core objects carry runtime behavior.

## Dependencies and Integration Points

It depends on regulator machine data and integrates with LP3971 board/platform data.

## Risks

Wrong IDs or array counts can misapply constraints or omit rails.

## Test Signals

Probe tests should ensure all eight IDs map correctly and platform constraints are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/lp3971.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/lp3972.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/lp3972.h

## Purpose

This header defines regulator IDs and platform data for the LP3972 PMIC.

## Important APIs, Types, and Functions

IDs cover five LDOs and three DCDCs, with `LP3972_NUM_REGULATORS` set to eight. `struct lp3972_regulator_subdev` pairs ID and init data, and `struct lp3972_platform_data` carries count plus an array pointer.

## Control Flow

The LP3972 regulator driver uses the platform-data array at probe to register configured rails.

## State and Persistence Behavior

This file contains static board configuration only. Runtime state belongs to the PMIC driver and regulator core.

## Dependencies and Integration Points

It depends on regulator machine data and integrates with legacy platform data.

## Risks

ID/order mistakes can map constraints to the wrong PMIC output.

## Test Signals

Probe tests should validate all rail IDs, counts, and constraint application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/lp3972.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/lp872x.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/lp872x.h

## Purpose

This header defines platform data for TI LP8720/LP8725 regulator PMICs, including regulator IDs, enable delays, DVS configuration, and GPIO controls.

## Important APIs, Types, and Functions

`LP872X_MAX_REGULATORS` is nine. Enable delays are `LP8720_ENABLE_DELAY` and `LP8725_ENABLE_DELAY`. `enum lp872x_regulator_id` covers LP8720 LDO1-5 plus buck, and LP8725 LDO1-5, LILO1-2, BUCK1-2. `enum lp872x_dvs_sel` selects V1 or V2 DVS.

`struct lp872x_dvs` carries a GPIO descriptor, DVS selector, and initial GPIO state. `struct lp872x_regulator_data` pairs an ID with init data. `struct lp872x_platform_data` carries general config, an update flag, regulator data array, optional DVS data, and enable GPIO.

## Control Flow

Probe code can update the general config register, set up enable and DVS GPIOs, select DVS behavior for buck voltage control, and register each populated regulator entry.

## State and Persistence Behavior

Static config is in platform data. Runtime state includes PMIC general configuration, GPIO enable/DVS levels, and regulator core rail state.

## Dependencies and Integration Points

It depends on regulator machine data, platform devices, and GPIO descriptors. It integrates board-specific GPIO-driven DVS with regulator registration.

## Risks

Wrong DVS selector or initial state can select an unintended buck voltage. Updating the general config register without accurate board data can change PMIC behavior globally. Enable-delay mismatches can cause premature consumer access.

## Test Signals

Tests should cover LP8720 vs LP8725 ID mapping, enable delay, general-config update, DVS GPIO state, enable GPIO behavior, and registration of all regulator data entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/lp872x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/machine.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/machine.h

## Purpose

`machine.h` declares board/platform-side regulator constraints and initial data. It tells regulator providers and consumers which voltage/current/mode/status operations are allowed on a specific machine, what ranges are safe, how rails behave in suspend, and how supplies map to consumers.

## Important APIs, Types, and Functions

Operation flags include `REGULATOR_CHANGE_VOLTAGE`, `CURRENT`, `MODE`, `STATUS`, `DRMS`, and `BYPASS`. Suspend enable policy values are `DO_NOTHING_IN_SUSPEND`, `DISABLE_IN_SUSPEND`, and `ENABLE_IN_SUSPEND`. `enum regulator_active_discharge` controls initial discharge policy.

`struct regulator_state` describes suspend voltage/range/mode and enable policy. `struct notification_limit` stores protection/error/warn thresholds. `struct regulation_constraints` is the central policy object: voltage/current ranges, offsets, input voltage, power budget, system load, coupled max spread, max voltage step, valid modes/ops, suspend states, notification limits, timing, active discharge, and flags such as always-on, boot-on, apply-uV, soft-start, pull-down, system-critical, and protection/detection enables.

`struct regulator_consumer_supply` maps a supply name to a device name, with `REGULATOR_SUPPLY()` initializer. `struct regulator_init_data` combines parent supply name, constraints, consumer mappings, and opaque driver data. `regulator_has_full_constraints()` informs the core that all board constraints are known.

## Control Flow

Board data or OF parsing builds `regulator_init_data` for each rail. During provider registration, the regulator core applies constraints, may enable boot-on/always-on rails, enforce valid operation masks for consumers, set initial mode/state, and configure protection/detection limits where provider ops support them. Consumer lookup uses the supply mapping for non-DT platform data.

## State and Persistence Behavior

The structures are configuration inputs. Once applied, corresponding policy is held in regulator core constraints and can drive persistent hardware state such as voltage, mode, suspend behavior, protection thresholds, soft-start, pull-down, and active discharge.

## Dependencies and Integration Points

It depends on the consumer API and suspend state types. It integrates board files, device tree parsing, regulator providers, consumer supply lookup, suspend/resume, protection event handling, and coupled regulator balancing.

## Risks

Constraints are safety-critical. Too-wide ranges can let consumers request damaging settings; too-narrow ranges break devices. Marking always-on/boot-on incorrectly can leave rails off or prevent power saving. Invalid operation masks can allow unsupported changes. Coupled `max_spread` arrays must match coupled rail counts.

## Test Signals

Tests should validate constraint parsing/application, operation-mask enforcement, boot-on/always-on behavior, suspend-state programming, notification thresholds, power budgets, consumer mappings, and full-constraints behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max1586.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/max1586.h

## Purpose

This header defines platform data for the Maxim MAX1586 regulator.

## Important APIs, Types, and Functions

Rail IDs are `MAX1586_V3` and `MAX1586_V6`. Precalculated V3 gain constants model external resistor configurations. `struct max1586_subdev_data` pairs regulator ID, name, and init data. `struct max1586_platform_data` supplies subdevice count/array and `v3_gain`, scaled by 1e6.

## Control Flow

The driver registers V3 and/or V6 from the subdevice array and uses `v3_gain` to calculate the V3 output range for voltage operations.

## State and Persistence Behavior

Platform data is static. Hardware voltage configuration and constraints are runtime state.

## Dependencies and Integration Points

It depends on regulator machine data and integrates with board-specific resistor-divider configuration.

## Risks

Wrong `v3_gain` makes voltage calculations inaccurate and can over/under-voltage consumers. Subdevice ID mistakes misapply constraints.

## Test Signals

Tests should compare calculated V3 voltages for each gain constant, rail registration, and constraint enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max1586.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8649.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/max8649.h

## Purpose

This header declares platform data for the Maxim MAX8649 regulator, including external clock, VID mode, ramp timing, and ramp-down policy.

## Important APIs, Types, and Functions

External clock enums cover 26 MHz, 13 MHz, and 19.2 MHz. Ramp enums cover 32 mV/us down to 0.25 mV/us. `struct max8649_platform_data` carries regulator init data and bitfields for VID mode, external clock frequency/use, ramp timing, and ramp-down enable.

## Control Flow

The driver reads pdata during probe, programs clock/ramp behavior and mode bits, then registers the regulator with supplied constraints.

## State and Persistence Behavior

Static config influences hardware registers that may persist while the PMIC remains powered. Runtime rail state belongs to hardware and regulator core.

## Dependencies and Integration Points

It depends on regulator machine data and integrates board-specific clock/ramp configuration with the MAX8649 driver.

## Risks

Wrong external clock frequency or ramp timing can break voltage transition timing. Incorrect VID mode can select the wrong control pins/state.

## Test Signals

Tests should verify clock enum programming, ramp timing, ramp-down behavior, VID mode selection, and voltage transition timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8649.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8660.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/max8660.h

## Purpose

This header defines platform data for Maxim MAX8660/MAX8661 regulators.

## Important APIs, Types, and Functions

Rail IDs are `MAX8660_V3` through `MAX8660_V7`, ending at `MAX8660_V_END`. `struct max8660_subdev_data` pairs ID, name, and init data. `struct max8660_platform_data` supplies subdevice count/array and `en34_is_high`, indicating that EN34 being high prevents software enable/disable of some regulators.

## Control Flow

The driver registers configured subdevices and uses `en34_is_high` to decide enable-control capabilities.

## State and Persistence Behavior

Configuration is static. Runtime enable control may be constrained by external EN34 pin state and hardware registers.

## Dependencies and Integration Points

It depends on regulator machine data and board wiring information.

## Risks

Wrong `en34_is_high` exposes unsupported enable/disable operations or hides valid ones. ID mismatches misconfigure rails.

## Test Signals

Probe tests should validate all rail IDs, EN34 behavior, and operation masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8952.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/max8952.h

## Purpose

This header declares platform data for Maxim MAX8952 DVS-capable regulator.

## Important APIs, Types, and Functions

DVS mode enums cover four modes. Voltage selector enums enumerate 770 mV through 1400 mV in 10 mV steps. Sync frequency enums cover 26 MHz, 13 MHz, and 19.2 MHz. Ramp enums cover 32 mV/us down to 0.25 mV/us. `MAX8952_NUM_DVS_MODE` is four. `struct max8952_platform_data` supplies default DVS mode, per-mode DVS selector values, sync frequency, ramp speed, and init data.

## Control Flow

The driver programs DVS mode voltages, default mode, sync frequency, and ramp speed at probe, then registers the regulator. Runtime DVS mode selection uses the preprogrammed values.

## State and Persistence Behavior

Platform data seeds hardware DVS registers. Runtime state includes active mode, selected voltage, and regulator core constraints.

## Dependencies and Integration Points

It depends on regulator machine data and integrates with board-specific DVS wiring/control.

## Risks

Incorrect DVS voltage entries or default mode can immediately select an unsafe voltage. Ramp/sync settings affect dynamic voltage scaling stability.

## Test Signals

Tests should validate selector-to-voltage mapping, all DVS modes, default-mode programming, sync frequency, ramp speed, and DVFS transition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8952.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8973-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/max8973-regulator.h

## Purpose

This header defines control flags and platform data for the Maxim MAX8973/MAX77621 step-down regulator family.

## Important APIs, Types, and Functions

Control flags enable remote sense, falling slew, active discharge, bias, pull-down, frequency shift, clock-advance trip levels, and inductor value compensation. `struct max8973_regulator_platform_data` contains regulator init data, ORed control flags, junction temperature warning threshold, external enable-control selection, and default DVS state.

## Control Flow

The driver reads control flags during probe, programs device control registers, configures thermal warning if applicable, selects external vs register enable control, applies DVS default state, and registers the regulator.

## State and Persistence Behavior

Platform flags become hardware control state. Thermal warning and external enable behavior persist while the PMIC remains configured.

## Dependencies and Integration Points

It integrates board electrical configuration with the MAX8973 regulator driver and regulator core init data.

## Risks

Wrong control flags can misconfigure remote sense, compensation, discharge, or enable control, potentially causing unstable regulation. Unsupported thermal thresholds must be rejected or mapped carefully.

## Test Signals

Tests should verify each control flag's register programming, external enable behavior, DVS default state, thermal warning thresholds, and voltage/ramp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/max8973-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6311.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6311.h

## Purpose

This header enumerates MediaTek MT6311 regulators and chip revision codes.

## Important APIs, Types, and Functions

`MT6311_MAX_REGULATORS` is two. Regulator IDs are `MT6311_ID_VDVFS` and `MT6311_ID_VBIASN`. Chip ID codes identify E1, E2, and E3 revisions.

## Control Flow

The driver uses IDs to index regulator descriptors and revision codes to handle chip-specific behavior.

## State and Persistence Behavior

No state is defined here. Runtime behavior is in PMIC registers and regulator core.

## Dependencies and Integration Points

The header is standalone and integrates with the MT6311 regulator driver.

## Risks

Wrong revision handling can apply invalid register programming. ID order changes break descriptor tables.

## Test Signals

Tests should cover revision detection, descriptor indexing, and both rail registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6311.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6315-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6315-regulator.h

## Purpose

This header defines MediaTek MT6315 regulator IDs and register constants needed by its regulator driver.

## Important APIs, Types, and Functions

Package/type constants include `MT6315_RP`, `PP`, and `SP`. Regulator IDs cover `MT6315_VBUCK1` through `VBUCK4`, ending at `MT6315_VBUCK_MAX`. Register macros define top key/protection registers, buck top control/ELR registers, debug registers for each buck, and a four-phase analog config register. Protection key values are `PROTECTION_KEY_H` and `PROTECTION_KEY`.

## Control Flow

The driver uses the register constants to unlock protected areas, identify package mode, configure buck topology, and read/write debug or voltage-related registers.

## State and Persistence Behavior

No C state is defined. The constants address PMIC hardware state that can persist until reset or power loss. Protection-key writes gate access to sensitive registers.

## Dependencies and Integration Points

The header is standalone and integrates with MediaTek PMIC/regmap driver code.

## Risks

Incorrect register addresses or protection-key sequencing can fail writes or modify protected PMIC state incorrectly. Package constants must match hardware variants.

## Test Signals

Tests should validate register-map accesses against datasheet addresses, protected write unlock sequences, package-specific topology, and all four buck descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6315-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6323-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6323-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6323 PMIC.

## Important APIs, Types, and Functions

The enum lists buck/LDO rails such as `VPROC`, `VSYS`, `VPA`, `VTCXO`, connectivity/camera/IO/USB/memory/SIM/vibrator/RF rails, ending with `MT6323_ID_RG_MAX`. `MT6323_MAX_REGULATOR` aliases that max value.

## Control Flow

The driver uses the enum values to index descriptor tables and expose named regulators to the core.

## State and Persistence Behavior

No state is defined. Runtime rail configuration is in PMIC registers and regulator core objects.

## Dependencies and Integration Points

The header is standalone and integrates with MT6323 PMIC regulator descriptors and consumer mappings.

## Risks

Changing enum order breaks descriptor and DT supply compatibility. Sparse explicit value `MT6323_ID_VIO28 = 9` must be preserved.

## Test Signals

Tests should ensure every ID maps to a descriptor, max count matches arrays, and all DT supplies resolve to expected rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6323-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6331-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6331-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6331 PMIC.

## Important APIs, Types, and Functions

The enum groups buck rails (`VDVFS11` through `VCORE2`, `VIO18`) and LDO rails including TCXO, audio, auxiliary, camera, memory, SIM, MIPI, vibrator, USB, SRAM, RTC, and digital rails, ending with `MT6331_ID_VREG_MAX`.

## Control Flow

The regulator driver uses IDs to index descriptors and register rails.

## State and Persistence Behavior

No runtime state is defined. Rail state is managed through PMIC registers and regulator core.

## Dependencies and Integration Points

The header is standalone and integrates with MT6331 regulator driver tables and DT supply names.

## Risks

Enum order is an ABI-like contract with driver arrays and bindings. Mislabeling buck vs LDO rails can expose wrong capabilities.

## Test Signals

Tests should validate descriptor coverage, supply lookup, and operation capabilities for each ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6331-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6332-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6332-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6332 PMIC.

## Important APIs, Types, and Functions

The enum defines buck rails `VDRAM`, `VDVFS2`, `VPA`, `VRF1`, `VRF2`, `VSBST`, and LDO rails `VAUXB32`, `VBIF28`, `VDIG18`, `VSRAM_DVFS2`, `VUSB33`, ending with `MT6332_ID_VREG_MAX`.

## Control Flow

Driver descriptor arrays use these IDs for regulator registration and consumer mapping.

## State and Persistence Behavior

No state is defined in the header. PMIC register and regulator core state implement runtime behavior.

## Dependencies and Integration Points

It is standalone and integrates with MT6332 regulator driver code.

## Risks

ID ordering changes break descriptor indexing and bindings. Boost/RF/memory rails have different capabilities and must be mapped correctly.

## Test Signals

Tests should cover descriptor coverage, DT supply matching, and per-rail voltage/enable capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6332-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6357-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6357-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6357 PMIC.

## Important APIs, Types, and Functions

The enum lists buck rails (`VCORE`, `VMODEM`, `VPA`, `VPROC`, `VS1`) and many LDO rails for audio, camera, connectivity, DRAM, eFuse, eMMC, front-end, vibrator, IO, memory card, RF, SIM, SRAM, USB, and XO domains, ending with `MT6357_ID_RG_MAX`. `MT6357_MAX_REGULATOR` aliases the max.

## Control Flow

The driver uses these IDs to index descriptors and register all PMIC rails.

## State and Persistence Behavior

No state is defined here. Runtime state is in PMIC registers and core regulator objects.

## Dependencies and Integration Points

The header is standalone and integrates with MT6357 PMIC regulator tables and DT bindings.

## Risks

ID ordering and max value must stay aligned with descriptors. Similar connectivity rails (`VCN33_BT` vs `VCN33_WIFI`) must not be swapped.

## Test Signals

Tests should verify descriptor coverage, supply names, and capabilities for every ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6357-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6358-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6358-regulator.h

## Purpose

This header enumerates regulator IDs for MediaTek MT6358 and MT6366 PMIC variants.

## Important APIs, Types, and Functions

`enum` blocks define MT6358 IDs from `VDRAM1` through `VSIM2`, ending with `MT6358_ID_RG_MAX`, and MT6366 IDs with a similar but variant-specific rail set ending with `MT6366_ID_RG_MAX`. Max macros expose both counts.

## Control Flow

The regulator driver selects the appropriate enum/descriptor table for the detected PMIC variant and registers rails by ID.

## State and Persistence Behavior

No runtime state is in the header. Hardware registers and regulator core objects hold rail state.

## Dependencies and Integration Points

It is standalone and integrates with MT6358/MT6366 regulator drivers and bindings.

## Risks

Variant-specific enum differences can cause descriptor mismatches if the wrong table is selected. Explicit numbering around `MT6358_ID_VDRAM2 = 9` must be preserved.

## Test Signals

Tests should cover both variants, descriptor counts, supply matching, and rail capability differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6358-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6359-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6359-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6359 PMIC.

## Important APIs, Types, and Functions

The enum covers system bucks (`VS1`, GPU, modem, VPU, core, VPA, processors), LDO rails for audio, SIM, vibrator, RF, USB, SRAM, IO, camera, connectivity, eFuse, XO, UFS, VM, battery backup, and sensor-hub aliases. It ends with `MT6359_ID_RG_MAX`; `MT6359_MAX_REGULATOR` aliases that count.

## Control Flow

The driver indexes descriptor arrays with these IDs and uses aliases such as `MT6359_ID_VGPU11_SSHUB = MT6359_ID_VCORE_SSHUB` where hardware shares control.

## State and Persistence Behavior

No state is defined here. Runtime behavior is in PMIC registers and regulator core.

## Dependencies and Integration Points

It is standalone and integrates with MT6359 bindings, descriptor tables, and consumer supply names.

## Risks

Aliased IDs and explicit numbering can break array assumptions. Connectivity BT/WIFI rails and SRAM processor rails require accurate mapping to avoid powering the wrong domain.

## Test Signals

Tests should validate descriptor coverage, alias handling, DT supply resolution, and per-rail capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6359-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6363-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6363-regulator.h

## Purpose

This header defines MediaTek MT6363 regulator register addresses, bit positions, and masks used by the MT6363 regulator driver.

## Important APIs, Types, and Functions

It includes `linux/bits.h` and defines a large set of register constants. These cover top/trap/key registers, buck enable and low-power control registers, buck voltage selector registers and masks, watchdog/debug VOSEL registers, efuse masks, operation-enable and hardware low-power mode registers, sensor-hub alternate controls, forced PWM/FCCM bits, LDO enable/LP/op-enable registers, LDO voltage selector/calibration registers, and current-sink controls.

No C structs or functions are declared; the API is the macro register map.

## Control Flow

The driver uses these constants with regmap operations to enable/disable bucks and LDOs, set low-power modes, program voltage selectors and calibration fields, unlock protected areas, select debug/watchdog values, and control isink channels.

## State and Persistence Behavior

The header itself has no state. The addressed PMIC registers are hardware state and may persist until PMIC reset or power loss. Some registers are protected or debug-oriented and require careful write sequencing.

## Dependencies and Integration Points

It depends on `GENMASK()` from `linux/bits.h` and integrates tightly with the MT6363 PMIC regmap and regulator descriptor tables.

## Risks

Register-address or mask errors directly affect hardware power rails. Shared registers with multiple bitfields, debug VOSEL paths, protected key registers, and sensor-hub aliases are high risk. Incorrect LP/enable bit selection can leave domains powered incorrectly during suspend.

## Test Signals

Tests should verify every descriptor's enable, mode, and voltage fields against these macros, check regmap read/write traces, validate suspend low-power mode programming, and compare constants against the PMIC datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6363-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6380-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6380-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6380 PMIC.

## Important APIs, Types, and Functions

The enum lists `MT6380_ID_VCPU`, `VCORE`, `VRF`, `VMLDO`, `VALDO`, `VPHYLDO`, `VDDRLDO`, `VTLDO`, ending with `MT6380_ID_RG_MAX`. `MT6380_MAX_REGULATOR` aliases the max value.

## Control Flow

The regulator driver uses IDs to index descriptors and register rails.

## State and Persistence Behavior

No state is declared. Runtime state resides in PMIC registers and regulator core.

## Dependencies and Integration Points

The header is standalone and integrates with MT6380 regulator driver tables.

## Risks

The include guard uses lowercase `mt6380` in the macro name; changing it can affect duplicate-include behavior. ID order must match descriptors and bindings.

## Test Signals

Tests should validate descriptor coverage, max count, and consumer supply mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6380-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6397-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/mt6397-regulator.h

## Purpose

This header enumerates regulator IDs and chip ID constants for the MediaTek MT6397 PMIC.

## Important APIs, Types, and Functions

The enum lists CPU/SRAM/core/GPU/DRAM/IO/TCXO/camera/USB/memory-card/general-purpose/vibrator rails, ending with `MT6397_ID_RG_MAX`. `MT6397_MAX_REGULATOR` aliases the max. Chip ID constants are `MT6397_REGULATOR_ID97` and `MT6397_REGULATOR_ID91`.

## Control Flow

The driver indexes descriptor tables by enum ID and may use chip ID constants to select variant behavior.

## State and Persistence Behavior

No state is defined in the header. Hardware and regulator core manage runtime rail state.

## Dependencies and Integration Points

It is standalone and integrates with MT6397 PMIC regulator descriptors and board/DT supply mappings.

## Risks

Explicit `MT6397_ID_VIO18 = 7` and subsequent ordering must match descriptor arrays. Chip ID selection must not confuse MT6397 variants.

## Test Signals

Tests should cover chip ID detection, descriptor count, rail registration, and supply mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/mt6397-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/of_regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/of_regulator.h

## Purpose

This header declares OpenFirmware/device-tree helper APIs for regulator initialization data and child regulator matching.

## Important APIs, Types, and Functions

`struct of_regulator_match` contains a regulator node name, driver data, parsed `regulator_init_data`, matched OF node, and optional regulator descriptor. Active APIs are `of_get_regulator_init_data()` and `of_regulator_match()` when `CONFIG_OF` is enabled; otherwise they return `NULL` or zero.

## Control Flow

Provider drivers call `of_regulator_match()` on a parent node and match table to find child regulator nodes, parse their constraints, attach driver data/descriptors, and later register regulators. `of_get_regulator_init_data()` parses one node against a descriptor.

## State and Persistence Behavior

The helpers allocate or return initialization data derived from device tree. Runtime state moves into regulator core constraints after registration. The header itself has no persistent state.

## Dependencies and Integration Points

It forward-declares `struct regulator_desc` and relies on device/OF/regulator init data types from including contexts. It integrates device-tree bindings with regulator provider registration.

## Risks

Disabled-OF stubs returning success/NULL can hide missing parsing in non-OF builds. Match names must align with DT child node names. Parsed constraints must be validated against descriptor capabilities.

## Test Signals

Tests should cover child-node matching, init-data parsing, descriptor association, absent optional nodes, disabled-OF builds, and invalid constraint rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/of_regulator.h -->
