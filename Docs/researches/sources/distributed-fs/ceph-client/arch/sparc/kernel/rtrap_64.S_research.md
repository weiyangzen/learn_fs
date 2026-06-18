# sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_64.S

Purpose: low-level SPARC V9 return-from-trap path. It atomically handles user work, preemption, signal delivery, saved user windows, FPU restore depth, interrupt state, MMU context restoration, and final `retry`.

Important APIs/symbols: main labels include `rtrap`, `rtrap_irq`, `rtrap_nmi`, `rtrap_xcall`, `rtrap_no_irq_enable`, `to_user`, `to_kernel`, `rt_continue`, `user_rtt_restore`, and `kern_rtt_restore`. It calls `schedule`/`schedule_user`, `fault_in_user_windows`, `do_notify_resume`, `trace_hardirqs_on`, and `preempt_schedule_irq`.

Control flow: on entry it extracts PIL from `tstate`, skips IRQ tracing for NMI/PIL cases, and branches user versus kernel. User returns clear PSTATE interrupt enable while testing `_TIF_USER_WORK_MASK`, repeatedly handling reschedule, signal/notify, and saved windows with IRQs held off until return. It clears/restores FPU state as required, reloads globals/ins/tpc/tnpc/y/tstate, restores primary context nucleus bits, manages window state (`canrestore`, `otherwin`, `wstate`), fills user register windows for 32-bit or 64-bit stacks if needed, and retries. Kernel returns optionally preempt, then restore nested FPU state based on `TI_FPDEPTH`.

State and persistence: mutates privileged registers (`pstate`, `pil`, `tl`, `tstate`, `tpc`, `tnpc`, `wstate`, window control), MMU context registers, per-thread flags/window/FPU depth fields, and trap-frame slots. Runtime only.

Dependencies and integration points: depends on SPARC V9 trap-frame offsets, sun4v/sun_m7/fast-window runtime patch sections, context tracking, IRQ tracing, scheduler/preemption, signal code, MMU context globals, FPU/VIS save areas, and register-window fill fixup handlers elsewhere.

Risks: the user-return work check must be atomic with interrupts disabled or signals/reschedules can be missed until a later interrupt. NMI returns must avoid softirq/tracing/preemption side effects. ADI requires M7 patching of PSTATE.MCDE on certain transitions. Stack-bias and 32-bit window fill paths are ABI-critical.

Test signals: user syscall/IRQ return with concurrent signal/resched, NMI return, kernel preemption on return from IRQ, saved user windows, 32-bit compat window fill, nested FPU/VIS use, sun4v and M7 patch application, and stress under IRQ tracing/context tracking.
