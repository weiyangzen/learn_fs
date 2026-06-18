<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_32.h

## Purpose
This header defines SPARC32 hard IRQ accounting hooks.

## Important APIs, Types, and Functions
It provides architecture IRQ stack/accounting declarations required by generic interrupt code.

## Control Flow
Interrupt entry/exit updates per-CPU hardirq state through generic mechanisms informed by this header.

## State and Persistence Behavior
Per-CPU interrupt accounting persists in irq/softirq counters outside the header.

## Dependencies and Integration Points
It integrates with generic hardirq, preempt count, and SPARC32 interrupt entry code.

## Risks
Accounting mismatches can break lockdep, preemption, or interrupt nesting diagnostics.

## Test Signals
Boot with lockdep/irq tracing, run interrupt load, and inspect `/proc/interrupts` and preempt count warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hardirq_32.h -->
