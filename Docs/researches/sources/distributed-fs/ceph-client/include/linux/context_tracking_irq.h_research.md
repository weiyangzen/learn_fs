## sources/distributed-fs/ceph-client/include/linux/context_tracking_irq.h

Purpose: This small header declares IRQ and NMI context-tracking hooks.

Important APIs, types, and functions: Under `CONFIG_CONTEXT_TRACKING_IDLE`, it declares `ct_irq_enter`, `ct_irq_exit`, `ct_irq_enter_irqson`, `ct_irq_exit_irqson`, `ct_nmi_enter`, and `ct_nmi_exit`. Disabled builds provide no-op inline stubs.

Control flow: Low-level IRQ/NMI entry code calls enter hooks before handling an interrupt and exit hooks afterward. The `_irqson` variants are for contexts where interrupts are enabled. NMI hooks track nesting separately from regular IRQs.

State and persistence: The hooks update per-CPU context tracking nesting/state in implementation files; this header stores no state.

Dependencies and integration points: It integrates with architecture IRQ/NMI entry code, RCU idle tracking, and `context_tracking_state.h`.

Risks and test signals: Risks include unbalanced enter/exit pairs, using the wrong IRQ-enabled variant, and nesting counter corruption in NMI paths. Test signals are IRQ storm tests, NMI watchdog paths, RCU idle debug, lockdep entry instrumentation, and disabled-config compile tests.
