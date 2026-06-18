# sources/distributed-fs/ceph-client/include/soc/sa1100/pwer.h

Purpose: declares SA1100 wake-enable helpers for GPIO and system-controller interrupt sources.

Important APIs/types/functions: exports `sa11x0_gpio_set_wake(unsigned int gpio, unsigned int on)` and `sa11x0_sc_set_wake(unsigned int irq, unsigned int on)`.

Control flow: GPIO, IRQ, or machine code calls these helpers to enable or disable wake capability for a source before entering low-power states.

State and persistence: wake configuration persists in SA1100 power/wakeup registers until changed. The header owns no state.

Dependencies and integration: included by SA1100 IRQ, GPIO, and mach generic code.

Risks: incorrect source numbers or enable flags can prevent wakeup or cause unwanted wake events. Test signals include suspend/resume wake from GPIO and system-controller IRQs on SA1100 platforms.
