<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/irq.h

## Purpose
`irq.h` defines m68k IRQ namespace sizing and the common IRQ-controller entry points used by machine ports.

## Important APIs, Types, and Functions
`NR_IRQS` is selected per platform family, from 8 on small classic systems to 256 on ColdFire. Classic CPU configs define `IRQ_SPURIOUS`, `IRQ_AUTO_1` through `IRQ_AUTO_7`, and `IRQ_USER`. The file declares `m68k_irq_startup()`, `m68k_irq_shutdown()`, auto/user interrupt setup, `m68k_setup_irq_controller()`, `irq_canonicalize()`, `do_IRQ()`, and `irq_err_count`.

## Control Flow, State, and Persistence
There is no local runtime flow. The declarations connect machine initialization to generic IRQ descriptor management. `irq_err_count` persists interrupt error accounting.

## Dependencies and Integration Points
It depends on atomic/linkage headers and generic irq data/chip/desc types. Machine-specific interrupt code for Atari, Mac, Q40, VME, Sun, ColdFire, and virtual machines consumes these definitions.

## Risks
Undersized `NR_IRQS` breaks platforms with high interrupt numbers, while oversizing wastes descriptor memory. `irq_canonicalize()` only exists as a real function on classic MMU CPUs.

## Test Signals
Build each major machine config and verify high-numbered IRQ registration, autovector delivery, spurious IRQ counting, and canonicalization on platforms with cascaded interrupt controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irq.h -->
