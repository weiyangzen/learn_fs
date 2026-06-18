# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7343.c

Purpose: describes SH7343 on-chip platform devices and interrupt controller data. It is the SoC setup file that turns fixed hardware blocks into Linux platform devices and INTC descriptors.

Important APIs, types, and functions: `sh7343_devices_setup()` allocates contiguous memory placeholders for VPU/VEU/JPU and calls `platform_add_devices()`. `plat_early_device_setup()` registers early SCIF, CMT, and TMU devices. `plat_irq_setup()` registers `intc_desc`. Data types include `plat_sci_port`, `uio_info`, `sh_timer_config`, `platform_device`, `resource`, `intc_vect`, `intc_group`, mask/prio/sense/ack registers, and `intc_desc`.

Control flow: static resources define SCIF0-3, IIC0-1, VPU4, VEU, JPU, CMT, and TMU0. Early setup exposes serial/timer devices for console and timekeeping; the arch initcall adds the full device list. Interrupt setup separately maps event codes for IRQ0-7, DMA, VIO, USB, MMC, SCIF, I2C, timers, JPU, LCDC, and related groups.

State and persistence: device and interrupt metadata are static `__initdata` or static structures. Runtime state lives in platform drivers and INTC MMIO registers. UIO multimedia devices receive reserved memory via `platform_resource_setup_memory()`.

Dependencies and integration points: integrates with `sh-sci`, `i2c-sh_mobile`, `uio_pdrv_genirq`, `sh-cmt-32`, `sh-tmu`, platform early devices, SuperH clock names, and the SH INTC core.

Risks: interrupt tables and resource addresses are hand-maintained and must match silicon. Multimedia UIO memory reservations can fail or conflict. `force_enable` and `force_disable` sentinel entries must align with mask table usage.

Test signals: boot should register all listed devices, early console/timekeeping should work, UIO devices should expose memory and IRQs, I2C transfers should use correct IRQ ranges, and `/proc/interrupts` should reflect mapped event codes.
