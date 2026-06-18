# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7366.c

Purpose: provides SH7366 platform-device and interrupt setup, based on SH7722 but reduced to the peripherals present on this SoC.

Important APIs, types, and functions: `sh7366_devices_setup()` reserves VPU/VEU memory and registers SCIF0, CMT, TMU0, IIC, USB host, VPU, and two VEU UIO devices. `plat_early_device_setup()` exposes early SCIF/CMT/TMU; `plat_irq_setup()` registers `intc_desc`; `plat_mem_setup()` is a stub noting TODO for Node 1.

Control flow: the file constructs resources for SCIF0, IIC, on-chip `r8a66597_hcd`, VPU5, VEU instances, CMT, and TMU0. Boot first registers early serial/timers, then arch init adds the full device list. Interrupt vectors cover external IRQs, ICB, DMA, VIO, MFI, VPU, USB, MMC, SCIF/SCIFA, DENC/MSIOF, FLCTL, I2C, SDHI, CMT, TSIF, SIU, timers, VEU2, and LCDC.

State and persistence: static platform data describes resources. Reserved multimedia memory persists as platform resources. INTC register state is programmed by the generic INTC core using mask/prio/sense/ack descriptions.

Dependencies and integration points: integrates with `sh-sci`, `i2c-sh_mobile`, `r8a66597_hcd`, UIO generic IRQ driver, timer drivers, and SuperH INTC.

Risks: USB IRQ is marked `IRQF_TRIGGER_LOW` in the resource flags; platform code must agree with the IRQ core. `plat_mem_setup()` is incomplete for Node 1. Device ids are tied to clock lookup names such as `i2c0`.

Test signals: validate early console, CMT/TMU clocksource, USB host enumeration, I2C interrupt operation, multimedia UIO IRQ delivery, and correct interrupt priorities/masks under load.
