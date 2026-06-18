# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7780.c

Purpose: registers SH7780 serial, timer, RTC, and two DMA engine devices, plus interrupt setup for internal and external IRQ/IRL sources.

Important APIs, types, and functions: `sh7780_devices_setup()` registers SCIF0-1, TMU0-1, RTC, and DMA0-1. `plat_early_device_setup()` adjusts SCIF clock-enable bits when `CONFIG_SH_TIMER_TMU` is disabled, then registers early devices. `plat_irq_setup()` and `plat_irq_setup_pins()` configure INTC modes.

Control flow: static DMA channel/pdata/resources describe two DMA controllers, one with DMARS and one without. Early setup exposes serial/timer devices; normal init adds all platform devices. Interrupt setup defaults to IRL mode and optional board selection enables IRQ or maskable IRL descriptors.

State and persistence: static platform data persists. The early setup may mutate `scif0_platform_data.scscr` and `scif1_platform_data.scscr` by clearing `SCSCR_CKE1` when TMU is not selected. DMA and INTC state live in MMIO.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh-rtc`, `sh-dma-engine`, and SuperH INTC. Clocking behavior depends on timer configuration.

Risks: conditional SCIF clock-bit mutation can affect serial timing. Shared DMA IRQ resources require careful driver handling. External IRQ pin modes are board-selected and direct-register based.

Test signals: validate serial operation with and without TMU config, DMA transfers on both controllers, RTC interrupts, TMU events, and all external IRQ/IRL mode paths.
