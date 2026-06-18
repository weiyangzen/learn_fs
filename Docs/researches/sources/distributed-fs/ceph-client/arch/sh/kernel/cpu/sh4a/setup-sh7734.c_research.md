# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7734.c

Purpose: registers SH7734 serial, RTC, I2C, and timer devices and defines the SH7734 interrupt controller including selectable external IRQ/IRL pin modes.

Important APIs, types, and functions: `plat_early_device_setup()` adds SCIF0-5 and TMU0-2 as early devices. `plat_irq_setup()` programs default IRL/IRQ masking and registers `intc_desc`. `plat_irq_setup_pins()` selects `IRQ_MODE_IRQ3210`, `IRQ_MODE_IRL3210`, or `IRQ_MODE_IRL3210_MASK`. Interrupt descriptors are declared with `DECLARE_INTC_DESC` and `DECLARE_INTC_DESC_ACK`.

Control flow: unlike many setup files, platform devices are collected in arrays but this file has no visible normal `arch_initcall` for `sh7734_devices`; early devices are explicitly registered. Interrupt setup disables IRQ/IRL lines, selects IRL mode by default, then registers the main descriptor. Board code can call `plat_irq_setup_pins()` to enable external pin modes.

State and persistence: static platform data persists in registered devices. INTC state is set through MMIO registers such as ICR0, INTMSK/INTMSKCLR, and descriptor-driven mask/prio/sense/ack registers.

Dependencies and integration points: integrates with `sh-sci`, `sh-rtc`, `i2c-sh7734`, `sh-tmu`, PFC/GPIO for pin modes, and SuperH INTC. SCIF uses BRG register type and one port enables timeout interrupts.

Risks: SCIF5 resource appears to reuse the `0xffe43000` base while carrying a different interrupt, which may be intentional muxing or a collision risk. The lack of a normal device-registration initcall means non-early devices depend on other registration paths. Pin mode defaults can mask external interrupts until board code selects a mode.

Test signals: confirm all intended platform devices appear, SCIF ports do not conflict, TMU timers run, I2C probes as `i2c-sh7734`, and each supported IRQ/IRL pin mode generates and masks interrupts correctly.
