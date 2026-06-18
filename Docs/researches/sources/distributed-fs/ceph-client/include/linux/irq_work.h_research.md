# sources/distributed-fs/ceph-client/include/linux/irq_work.h

## Purpose
`irq_work.h` defines deferred callback work that can be queued from hard IRQ, NMI, or other atomic contexts and executed later through architecture IRQ work support.

## Important APIs, types, and functions
It provides initializers `IRQ_WORK_INIT`, `IRQ_WORK_INIT_LAZY`, `IRQ_WORK_INIT_HARD`, `DEFINE_IRQ_WORK`, `init_irq_work`, state queries `irq_work_is_pending`, `irq_work_is_busy`, `irq_work_is_hard`, queue APIs `irq_work_queue` and `irq_work_queue_on`, plus `irq_work_tick`, `irq_work_sync`, `irq_work_run`, `irq_work_needs_cpu`, `irq_work_single`, and `arch_irq_work_raise`.

## Control flow
Callers initialize a `struct irq_work`, queue it locally or to a CPU, and the architecture raises or checks IRQ work so the callback runs. `irq_work_sync` waits for busy callbacks to finish.

## State and persistence
State lives in `struct irq_work.node` atomic flags, callback pointer, and `rcuwait`; it is runtime-only.

## Dependencies and integration points
It depends on `irq_work_types.h`, SMP call-single infrastructure, RCU wait, and architecture `asm/irq_work.h` support.

## Risks and test signals
Risks include requeueing while pending/busy, missing CPU wakeups for lazy work, teardown without sync, and config stubs hiding missing callbacks. Tests should cover hard/lazy work, cross-CPU queueing, NMI-safe queueing, sync during callback, and disabled `CONFIG_IRQ_WORK` builds.
