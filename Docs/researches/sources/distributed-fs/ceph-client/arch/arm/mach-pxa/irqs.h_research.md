<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irqs.h

Purpose: PXA interrupt number map and IRQ helper declarations.

Important definitions: `PXA_IRQ(x)` offsets internal IRQs after legacy IRQs; names cover SSP, USB, GPIO, PMU, audio, LCD, I2C, UARTs, MMC, DMA, OS timer, RTC, PXA3xx peripherals, wakeup IRQs, and GPIO IRQ base. `PXA_GPIO_TO_IRQ(x)` maps built-in GPIOs after internal IRQs; `PXA_NR_IRQS` ends at `IRQ_BOARD_START`.

Control flow and integration: used by platform-device resource tables, SoC wake functions, GPIO IRQ code, and machine descriptors. Declares mask/unmask and IRQ entry functions implemented in `irq.c`.

State and persistence: none; this is a static ABI-like numbering contract for legacy PXA.

Dependencies: includes `asm/irq.h` for `NR_IRQS_LEGACY`.

Risks and test signals: overlapping symbolic IRQs reflect different SoC meanings, so consumers must use correct CPU guards. Test with all SoC builds and peripheral IRQ delivery for devices registered in `devices.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irqs.h -->
