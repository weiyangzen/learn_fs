# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7763.c

Purpose: defines SH7763 platform devices and interrupt controllers for serial, RTC, USB host/function, and timers.

Important APIs, types, and functions: `sh7763_devices_setup()` registers SCIF0-2, RTC, OHCI, SH UDC, and TMU0/1. `plat_early_device_setup()` exposes serial and timers early. `plat_irq_setup()` registers the main descriptor. `plat_irq_setup_pins()` supports combined IRQ mode and IRL7654/3210 modes with optional mask descriptors.

Control flow: device arrays split normal and early registration. Interrupt setup initially disables IRQ and IRL groups, selects IRL mode, and registers the base descriptor. Board code can choose external pin mode later.

State and persistence: static platform resources include SCIF FIFO-data register type, RTC IRQs, USB MMIO/IRQ resources, and timer channels. INTC mask/prio/sense/ack state is hardware-backed.

Dependencies and integration points: integrates with `sh-sci`, `sh-rtc`, `ohci-platform`, `sh_udc`, `sh-tmu`, PFC-selected external IRQ pins, and SuperH INTC.

Risks: USB host and function controllers share SoC USB resources and need board-level power/PHY setup outside this file. Direct IRQ-mode writes assume specific ICR0 layout. No `plat_mem_setup()` is present for extra nodes.

Test signals: verify SCIF FIFO operation, USB OHCI and gadget modes, RTC interrupts, TMU clocksource/events, and external interrupt behavior in IRQ and IRL modes.
