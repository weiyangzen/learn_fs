# sources/distributed-fs/ceph-client/include/clocksource/pxa.h

Purpose: declaration for PXA non-device-tree timer initialization.

Important APIs/types/functions: `pxa_timer_nodt_init(int irq, void __iomem *base)`.

Control flow: board/platform setup calls the init routine with an IRQ and mapped OST base; implementation registers clocksource/clockevent handlers.

State and persistence: no state in the header; implementation owns mapped timer state.

Dependencies and integration points: integrates with legacy PXA platform setup and clocksource registration.

Risks: invalid IRQ/base inputs break early timer setup and boot scheduling.

Test signals: PXA board boot tests and legacy non-DT timer initialization coverage.
