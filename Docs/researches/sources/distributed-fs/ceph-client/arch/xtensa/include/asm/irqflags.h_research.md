<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irqflags.h

## Purpose
Implements local IRQ flag save, disable, enable, restore, and disabled checks for Xtensa.

## Important APIs, Types, And Functions
Provides `arch_local_save_flags`, `arch_local_irq_save`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`, and `arch_irqs_disabled`.

## Control Flow
Functions read/write the processor status register (`ps`) and use `rsil`, `wsr`, and `rsync` to raise/lower interrupt level. `XTENSA_FAKE_NMI` configurations preserve debug-level behavior and include safety diagnostics for lock/debug levels.

## State And Persistence
State is the CPU `ps` register interrupt level and exception bits. No software persistence.

## Dependencies And Integration Points
Depends on processor level constants, fake-NMI Kconfig, lockdep/trace IRQ flags, and generic interrupt control callers.

## Risks And Edge Cases
Restoring invalid PS bits can leave interrupts masked or enable them too early. Fake-NMI configurations are sensitive to `LOCKLEVEL`, `TOPLEVEL`, and debug level overlap. `rsync` ordering is required after status writes.

## Test Signals
Run interrupt enable/disable tracing, lockdep IRQ tests, fake-NMI perf IRQ tests, and nested interrupt stress on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irqflags.h -->
