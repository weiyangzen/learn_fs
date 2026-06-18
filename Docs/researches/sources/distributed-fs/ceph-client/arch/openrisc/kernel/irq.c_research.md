<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/irq.c

## Purpose
Provides OpenRISC interrupt flag save/restore helpers and initializes irqchip support.

## Important APIs, Types, And Functions
`arch_local_save_flags()` returns `SPR_SR_IEE | SPR_SR_TEE` bits from `SPR_SR`. `arch_local_irq_restore()` restores those bits while preserving other SR state. `init_IRQ()` calls `irqchip_init()`.

## Control Flow
Generic IRQ and locking code use save/restore helpers. Boot calls `init_IRQ()` during interrupt subsystem initialization.

## State And Persistence
Mutates SR interrupt-enable bits. No software state is stored.

## Dependencies And Integration Points
Depends on `mfspr/mtspr`, SPR bit definitions, irqchip framework, and exported irqflags API.

## Risks
Restore must not clobber MMU/cache/supervisor bits. Treating tick timer and external interrupt enables as a pair affects timer behavior.

## Test Signals
IRQ enable/disable tracing, timer interrupts, external irqchip probe, and lockdep/irqflags tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/irq.c -->
