# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7724.c

Purpose: provides the large SH7724 SoC setup: DMA engines, serial ports, RTC, I2C, multimedia UIO blocks, timers, cache enable, interrupt controller, and reset-standby save/restore.

Important APIs, types, and functions: `sh7724_devices_setup()`, `plat_early_device_setup()`, `l2_cache_init()`, `plat_irq_setup()`, `sh7724_pre_sleep_notifier_call()`, `sh7724_post_sleep_notifier_call()`, and `sh7724_sleep_setup()` are the major functions. Data includes two DMA engine devices, extensive DMA slave/channel tables, platform devices, INTC descriptors, and sleep notifier blocks.

Control flow: boot registers early SCIF0-5, CMT, and TMU0/1, then the arch initcall reserves memory for VPU, VEU0/1, JPU, SPU0/1 and registers the full device array. The interrupt setup maps a broad multimedia-heavy vector set. `l2_cache_init()` writes cache-enable bits to RAMCR. The sleep init registers pre/post notifiers on SH-Mobile sleep notifier chains.

State and persistence: persistent hardware state includes DMA controller registers, interrupt mask/prio registers, cache-control bits, and reset-standby saved state. `sh7724_rstandby_state` snapshots BCR, INTC, RWDT, and CPG registers before `SUSP_SH_RSTANDBY`, then restores them afterward.

Dependencies and integration points: integrates with `sh-dma-engine`, `sh-sci`, `sh-rtc`, `i2c-sh_mobile`, UIO generic IRQ driver, CMT/TMU timers, SH-Mobile sleep notifier lists, and SuperH INTC. DMA slave IDs cover SCIF, USB, SDHI, SIU, FLCTL, and I2C-style requesters.

Risks: the sleep save/restore list is manual and easy to miss when adding hardware. RWDT writes require key bits and could disturb watchdog state. DMA tables and multimedia memory reservations have high board-specific risk. Cache enable is unconditional.

Test signals: suspend/reset-standby resume should restore interrupts, CPG, bus-control, and watchdog state; DMA clients should transfer correctly; multimedia UIO blocks should receive IRQs; early console/timers, I2C, RTC, and L2 cache behavior should be verified.
