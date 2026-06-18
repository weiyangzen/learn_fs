# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7770.c

Purpose: supplies SH7770 platform-device setup for ten SCIF ports, three TMU blocks, and interrupt descriptors with selectable external IRQ/IRL modes.

Important APIs, types, and functions: `sh7770_devices_setup()` registers SCIF0-9 and TMU0-2; `plat_early_device_setup()` registers the same early-capable serial/timer set; `plat_irq_setup()` and `plat_irq_setup_pins()` configure the main and external interrupt controllers.

Control flow: SCIF ports use adjacent MMIO blocks `0xff923000-0xff92c000` with event codes `0x9a0-0xac0`; TMU blocks cover `0xffd80000`, `0xffd81000`, and `0xffd82000`. Interrupt setup disables external groups, selects IRL mode by default, registers the main descriptor, then allows board-selected IRQ or IRL descriptors.

State and persistence: platform-device metadata is static. INTC state persists in mask/prio/sense/ack registers. No additional memory node state is registered.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, SH PFC/board pin selection, and SuperH INTC. The external IRL descriptor names include `sh7780-irl*`, likely copied from SH7780.

Risks: many similar SCIF resources increase copy/paste risk. The descriptor names for IRL modes referencing `sh7780` could confuse diagnostics. IRQ mode writes are hard-coded to ICR0 bits.

Test signals: boot should show ten usable serial devices and three timer blocks; external IRQ/IRL board modes should register with expected names and deliver interrupts; timer interrupts should map to correct event codes.
