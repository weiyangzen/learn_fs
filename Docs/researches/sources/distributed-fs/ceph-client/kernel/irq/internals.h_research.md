# sources/distributed-fs/ceph-client/kernel/irq/internals.h

## Purpose
`internals.h` is the private header for `kernel/irq`. It centralizes internal descriptor state bits, threaded IRQ flags, function prototypes, scoped descriptor lock helpers, irqdata state mutators, stats helpers, PM/debugfs/proc stubs, and optional feature shims used across the IRQ core.

## Important APIs, types, and functions
It defines `MAX_SPARSE_IRQS`, `IRQTF_*` thread bits, `IRQS_*` internal descriptor bits, `IRQ_RESEND`, `IRQ_START_FORCE`, descriptor lock classes/macros `scoped_irqdesc_get_and_lock()` and `scoped_irqdesc_get_and_buslock()`, `irqd_set()/irqd_clear()/irqd_has_set()`, `irq_state_set_disabled()`, `irq_state_set_masked()`, stats helpers, and many prototypes for chip, handle, manage, resend, proc, affinity, PM, debugfs, and pending-move operations.

## Control flow
The header provides inline control helpers rather than standalone runtime flow. Notably, scoped descriptor locks acquire optional chip bus locks then `desc->lock`, and release in reverse order. Feature conditionals replace missing procfs, PM, generic-chip, pending-IRQ, irqdomain hierarchy, and debugfs functionality with no-op stubs.

## State and persistence
It defines names and accessors for state stored in `struct irq_desc` and `struct irq_data`: internal `istate`, thread flags, `IRQD_*` bits, stats, pending masks, and debugfs metadata. The header owns no separate state.

## Dependencies and integration points
Every core IRQ source file depends on this header for shared private contracts. It includes descriptor/stat/PM/scheduler-clock headers, `debug.h`, and `settings.h`, and bridges configuration-specific code paths with inline stubs.

## Risks and test signals
Risks include private state bit collisions, accessor misuse bypassing public IRQ APIs, lock guard lifetime mistakes, feature-stub behavior diverging from compiled implementations, and external inclusion despite the warning. Test signals include sparse and non-sparse builds, procfs/debugfs/PM on-off configs, lockdep coverage of scoped guards, pending migration builds, and compiler warnings when prototypes drift from definitions.
