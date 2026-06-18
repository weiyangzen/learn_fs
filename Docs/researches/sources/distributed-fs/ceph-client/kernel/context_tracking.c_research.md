# sources/distributed-fs/ceph-client/kernel/context_tracking.c

## Purpose
`context_tracking.c` records high-level CPU execution-context transitions among kernel, user, guest, idle, IRQ, and NMI contexts. Its main job is to let RCU and virtual time accounting know when a CPU has entered or left an extended quiescent state, especially for nohz-full and idle CPUs where the periodic tick can be stopped.

## Important APIs, types, and functions
The key state is the per-CPU exported `struct context_tracking context_tracking`, whose fields include atomic context state, nesting, NMI nesting, recursion, and active tracking flags. Idle/interrupt entry points include `ct_idle_enter()`, `ct_idle_exit()`, `ct_irq_enter()`, `ct_irq_exit()`, `ct_irq_enter_irqson()`, `ct_irq_exit_irqson()`, `ct_nmi_enter()`, and `ct_nmi_exit()`. User/guest entry points include `__ct_user_enter()`, `ct_user_enter()`, `user_enter_callable()`, `__ct_user_exit()`, `ct_user_exit()`, `user_exit_callable()`, `ct_cpu_track_user()`, and optionally `context_tracking_init()`.

Internal helpers `ct_kernel_exit_state()` and `ct_kernel_enter_state()` update the atomic RCU-watching state with ordering guarantees. `ct_kernel_exit()` and `ct_kernel_enter()` handle nesting, tracepoints, deferred RCU quiescent states, task-RCU idle markers, and NMI nesting normalization. `context_tracking_recursion_enter()` prevents re-entrant user/guest tracking from corrupting state.

## Control flow
Idle entry calls `ct_kernel_exit(false, CT_RCU_WATCHING + CT_STATE_IDLE)` with IRQs already disabled, decrementing nesting and, at the outermost transition, marking RCU as no longer watching. Idle exit saves IRQ flags, calls `ct_kernel_enter(false, CT_RCU_WATCHING - CT_STATE_IDLE)`, and restores IRQs.

IRQ tracking is a thin wrapper around the NMI machinery: `ct_irq_enter()` and `ct_irq_exit()` require disabled IRQs and delegate to `ct_nmi_enter()` and `ct_nmi_exit()`. NMI entry checks whether RCU is currently watching; if not, it marks the CPU watching before the handler runs and increments `nmi_nesting` by one. If already watching, it increments by two so the outermost interrupt of an RCU-idle CPU can be distinguished on exit. NMI exit reverses that encoding and may re-enter RCU-idle state.

User and guest transitions use `__ct_user_enter()` and `__ct_user_exit()` with interrupts disabled. They first enter the recursion guard, compare the current tracked state, and either perform full RCU/vtime work when `ct->active` is true or only maintain state for inactive CPUs. Active user entry may trace/vtime-enter, request an RCU irq-work reschedule, then call `ct_kernel_exit(true, CT_RCU_WATCHING + state)`. Exit calls `ct_kernel_enter(true, CT_RCU_WATCHING - state)` before any kernel-side RCU usage and then runs vtime/trace exit for real user state.

## State and persistence behavior
All persistent state is per-CPU runtime state. `ct->state` encodes RCU watching plus context bits and is updated atomically with ordering requirements because other CPUs and RCU grace-period machinery observe it. `ct->nesting` and `ct->nmi_nesting` track nested idle/IRQ/NMI transitions and are written with `WRITE_ONCE()` to avoid tearing. `ct->active` is enabled by `ct_cpu_track_user()`, which also increments the `context_tracking_key` static branch and may seed `TIF_NOHZ` into `init_task`. No disk or user-visible persistent files are written.

## Dependencies and integration points
The file integrates with RCU (`rcu_is_watching_curr_cpu()`, `rcu_preempt_deferred_qs()`, `rcu_irq_work_resched()`, `rcu_irq_enter_check_tick()`), vtime accounting, lockdep, tracepoints for RCU and context tracking, architecture low-level entry/exit code, task-RCU idle markers, and nohz-full configuration. Many functions are `noinstr` and deliberately bracket trace/vtime calls inside `instrumentation_begin()` and `instrumentation_end()`.

## Risks and edge cases
The main risks are unbalanced nesting, calling entry/exit routines with the wrong IRQ state, using RCU in noinstr windows after RCU has been marked idle, and incorrect arch integration around user/guest entry. The obsolete callable wrappers use `local_irq_save/restore()` and are documented as unsafe for strict noinstr tracing/lockdep rules. NMI nesting uses a non-obvious one-versus-two increment encoding; regressions can lead to false RCU idle state or RCU stall reports. `CONFIG_CONTEXT_TRACKING_IDLE`, `CONFIG_CONTEXT_TRACKING_USER`, and nohz options substantially change behavior.

## Test signals
Useful test signals include booting with `CONFIG_RCU_EQS_DEBUG=y`, exercising idle entry/exit, NMI-in-idle, IRQ-in-idle, syscall/user transitions on nohz-full CPUs, guest entry/exit if present, migration after user exceptions, and tracing `rcu_watching`/context-tracking events. Stress cases should include nested interrupts, obsolete callable paths, full-dynticks CPUs, and RCU stall detection under high interrupt rates.
