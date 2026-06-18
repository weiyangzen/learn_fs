# sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq_64.c

## Purpose
Implements 64-bit PowerPC lazy interrupt soft-masking, pending-interrupt replay, idle IRQ preparation, SRR1 wake reason conversion, forced external IRQ replay, and the `noirqdistrib` boot option.

## Important APIs, Types, And Functions
Defines `distribute_irqs` and functions `replay_soft_interrupts`, `arch_local_irq_restore`, `prep_irq_for_idle`, `prep_irq_for_idle_irqsoff`, `replay_system_reset`, `irq_set_pending_from_srr1`, and `force_external_irq_replay`. Internal helpers include `next_interrupt`, `irq_happened_test_and_clear`, `__replay_soft_interrupts`, and `replay_soft_interrupts_irqrestore`. It uses PACA bits such as `PACA_IRQ_HARD_DIS`, `PACA_IRQ_HMI`, `PACA_IRQ_DEC`, `PACA_IRQ_EE`, `PACA_IRQ_DBELL`, `PACA_IRQ_PMI`, and `PACA_IRQ_REPLAYING`.

## Control Flow
Soft-masked interrupts set pending bits in PACA. `arch_local_irq_restore(0)` atomically tries to clear the soft mask if nothing is pending; otherwise it hard-disables interrupts, enters IRQ context, replays pending interrupts in priority order, exits IRQ context, and retries if softirq handling created new pending work. Replay synthesizes `pt_regs` and calls HMI, decrementer, external IRQ, doorbell, and PMI handlers. Idle preparation hard-disables interrupts, checks pending work, and either refuses idle or marks interrupts soft-enabled for low-power entry. Book3S idle wakeup converts SRR1 reason bits into pending IRQ bits or immediately handles system reset.

## State And Persistence
State is per-CPU PACA soft-mask and pending-bit fields, `distribute_irqs`, lockdep/tracing IRQ state, and optional KUAP AMR state saved around replay. No durable state exists.

## Dependencies And Integration Points
Depends on `interrupt.c` return preparation, `interrupt_64.S` restart sections, timer/IRQ/doorbell/PMI/HMI handlers, PS3 LV1 firmware side-effect call, KUAP, context tracking through `irq_enter`/`irq_exit`, and Book3S idle wakeup reason definitions.

## Risks And Edge Cases
The main risk is losing or reordering interrupts around transitions between hard-disabled, soft-disabled, and enabled states. Replay must avoid recursion through softirq-enabled sections, preserve KUAP, and prioritize HMI. Idle preparation must not enter low power when a pending interrupt exists. SRR1 reason mapping must match CPU architecture; doorbell wakeup needs `msgclr` to avoid duplicate interrupts.

## Test Signals
Signals include lockdep IRQ trace correctness, interrupt storm while toggling local IRQs, idle wakeup by DEC/EE/doorbell/HMI/system reset, PS3 builds, KUAP debug checks, forced external replay, `noirqdistrib` boot parameter, and softirq recursion stress.
