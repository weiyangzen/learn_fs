# sources/distributed-fs/ceph-client/kernel/entry/common.c

## Purpose

`common.c` implements generic IRQ/NMI entry and exit helpers plus the loop that completes pending thread work before returning to user mode. It coordinates scheduling, signals, uprobes, livepatch state, resume-user-mode work, architecture-specific work, RSEQ slice extension, RCU/lockdep tracing state, and NMI ftrace state at highly constrained entry boundaries.

## Important APIs, Types, And Functions

- `arch_do_signal_or_restart()` is a weak architecture hook for signal delivery/restart handling.
- `EXIT_TO_USER_MODE_WORK_LOOP`, `TIF_SLICE_EXT_SCHED`, and `TIF_SLICE_EXT_DENY` define which thread flags are handled in the loop and which flags deny RSEQ slice extension.
- `__exit_to_user_mode_loop()` processes pending work while interrupts are enabled, then disables interrupts and rereads flags.
- `exit_to_user_mode_loop()` wraps the loop and retries when `rseq_exit_to_user_mode_restart()` asks for another pass.
- `irqentry_enter()` dispatches between `irqentry_enter_from_user_mode()` and `irqentry_enter_from_kernel_mode()`.
- `raw_irqentry_exit_cond_resched()` conditionally schedules on IRQ exit if preemption state allows it.
- `irqentry_exit()` exits to user or kernel mode based on `user_mode(regs)`.
- `irqentry_nmi_enter()` and `irqentry_nmi_exit()` manage NMI entry/exit state, lockdep, context tracking, KMSAN register state, hardirq tracing, and ftrace NMI hooks.
- Dynamic preemption builds may expose `irqentry_exit_cond_resched` through static calls or static keys.

## Control Flow

Before returning to user mode, `__exit_to_user_mode_loop()` repeatedly enables interrupts and handles thread flags. Reschedule flags either grant an RSEQ slice extension or call `schedule()`. Uprobe, livepatch, signal, notify-resume, and architecture-specific work are handled in order. The loop then disables interrupts, prepares tick/nohz user entry, rereads thread flags, and repeats until no loop-relevant work remains.

`exit_to_user_mode_loop()` adds an outer retry for RSEQ restart handling. IRQ entry checks whether interrupted context was user mode; user entries call the user-mode transition helper and return state with `exit_rcu = false`, while kernel entries go through kernel-mode entry tracking. IRQ exit symmetrically chooses user-mode or kernel-mode exit. Kernel-mode IRQ exit can call `preempt_schedule_irq()` when preempt count is zero, RCU/stack checks pass, and rescheduling is needed.

NMI entry saves lockdep hardirq state, enters NMI/context tracking, marks hardirqs off, unpoisons entry registers for KMSAN inside instrumentation brackets, finishes hardirq-off tracing, and enters ftrace NMI state. NMI exit unwinds ftrace, hardirq tracing/lockdep state, context tracking, and `__nmi_exit()`.

## State And Persistence Behavior

The file mutates per-task thread flags indirectly by servicing work, scheduler state through `schedule()`/`preempt_schedule_irq()`, livepatch per-task patch state, RSEQ state, context tracking, lockdep hardirq state, ftrace NMI state, and tick/nohz state. There is no durable persistence.

## Dependencies And Integration Points

It depends on generic entry headers, scheduler/preemption, RSEQ, uprobes, livepatch, signal handling, resume-user-mode work, arch entry hooks, RCU, lockdep, context tracking, ftrace, KMSAN, tick/nohz, and dynamic preemption infrastructure. The Makefile deliberately suppresses unsafe instrumentation for this code.

## Risks And Edge Cases

- Entry/exit ordering is security- and correctness-sensitive. Enabling interrupts too early or disabling them too late can miss work or violate context tracking rules.
- `noinstr` sections must avoid compiler/tool instrumentation except inside explicit instrumentation regions.
- RSEQ slice extension interacts with scheduling latency, especially under `CONFIG_PREEMPT_RT`.
- NMI paths must preserve lockdep and tracing state exactly or later hardirq state reports become unreliable.
- Architecture hooks can add work; the loop must reread flags after interrupts were enabled because work can change concurrently.

## Test Signals

Useful signals include objtool `noinstr` validation, lockdep/RCU/context-tracking warnings, KMSAN entry-register behavior, syscall/interrupt stress, signal delivery and restart tests, uprobes and livepatch tests, RSEQ tests under reschedule pressure, PREEMPT_DYNAMIC toggles, PREEMPT_RT latency tests, and NMI/ftrace tracing tests.
