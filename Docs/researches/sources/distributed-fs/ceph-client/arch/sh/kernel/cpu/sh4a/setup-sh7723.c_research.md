# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7723.c

Purpose: registers SH7723 platform devices and interrupt tables, including serial, multimedia, timers, RTC, USB host, and I2C.

Important APIs, types, and functions: `sh7723_devices_setup()` reserves memory for VPU and two VEU blocks and calls `platform_add_devices()`. `plat_early_device_setup()` registers SCIF/SCIFA, CMT, and TMU devices early. `l2_cache_init()` enables L2 cache by writing `L2_CACHE_ENABLE` to `RAMCR`. `plat_irq_setup()` registers `intc_desc`.

Control flow: static devices cover SCIF0-2, SCIFA3-5, VPU5, VEU2H0/1, CMT, TMU0/1, RTC, `r8a66597_hcd`, and IIC. Early device setup enables console/timekeeping before normal platform registration. Interrupt vectors include external IRQs, DMA, video, USB, MMC, SCIF/SCIFA, FLCTL, I2C, SDHI, CMT, SIU, TMU, VEU, LCDC, VPU, and JPU-style sources.

State and persistence: device metadata is static; reserved memory resources for UIO blocks are filled at init. `l2_cache_init()` persists by changing the RAM/cache control register.

Dependencies and integration points: depends on serial SCI, UIO, SH timer, USB `r8a66597`, I2C mobile, RTC, SuperH cache/MMIO, and INTC core.

Risks: L2 cache enable is a bare register write without runtime probing. SCIFA and SCIF resource ranges differ, so clock and pin mappings must agree. USB IRQ trigger flags must match board wiring.

Test signals: verify early serial on all configured ports, L2 cache enable behavior, USB host enumeration, VPU/VEU UIO memory and IRQ delivery, CMT/TMU operation, and I2C transfers.
