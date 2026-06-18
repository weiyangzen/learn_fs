# sources/distributed-fs/ceph-client/kernel/irq_work.c

## Purpose
`irq_work.c` implements the IRQ-work framework for NMI-safe enqueueing of callbacks that run from hardirq-like context, timer tick fallback, remote CPU IPI delivery, or per-CPU threads on PREEMPT_RT.

## Important APIs, types, and functions
Per-CPU state includes `raised_list`, `lazy_list`, `irq_workd`, and SMP `irq_work_wakeup`. Public functions are `irq_work_queue()`, `irq_work_queue_on()`, `irq_work_needs_cpu()`, `irq_work_single()`, `irq_work_run()`, `irq_work_tick()`, and `irq_work_sync()`. Architecture integration is through weak `arch_irq_work_raise()` and `arch_irq_work_has_interrupt()`.

## Control flow
Queueing atomically claims work with `IRQ_WORK_CLAIMED`, `IRQ_WORK_PENDING`, and `CSD_TYPE_IRQ_WORK`, then places it on the local raised or lazy list depending on flags and PREEMPT_RT rules. Remote queueing uses `__smp_call_single_queue()` and, on PREEMPT_RT for non-hard work, queues a hard wakeup item to wake the target CPU's `irq_work/%u` thread. Running drains lockless lists, clears pending, invokes callbacks under lockdep IRQ-work annotations, clears busy state, and wakes synchronizers when needed. Tick fallback drains work when no arch interrupt exists and wakes the RT thread for lazy work.

## State and persistence
State is per-CPU lockless-list membership plus atomic flags embedded in each `struct irq_work`. `irq_work_sync()` waits for busy state using `rcuwait` plus RCU synchronization in threaded/fallback modes or spins when hard IRQ delivery is available. No state persists beyond queued work lifetime.

## Dependencies and integration points
It depends on llist, atomic bit flags, SMP call-single queues, tick/nohz, hardirq/preempt state, lockdep, KASAN aux stack recording, RCU wait, smpboot per-CPU threads, trace IPI events, and architecture IRQ-work interrupt support. Many kernel subsystems use irq_work to defer NMI/hardirq-unsafe work.

## Risks and test signals
Risks include double queueing, callbacks freeing work before busy clears, remote queue attempts to offline CPUs, NMI use of non-NMI-safe remote IPI backends, lazy work starvation without ticks, PREEMPT_RT hard-vs-lazy context mistakes, and sync deadlocks if called with IRQs disabled. Test signals include local and remote queueing, requeue while callback is running, nohz tick-stopped lazy work, architectures without IRQ-work interrupts, PREEMPT_RT threaded execution, CPU hotplug flushing, `irq_work_sync()` before freeing memory, and lockdep/KASAN reports.
