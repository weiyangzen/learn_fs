# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7722.c

Purpose: registers SH7722 platform devices, DMA engine metadata, audio support, timers, multimedia UIO blocks, and the SH7722 interrupt controller.

Important APIs, types, and functions: `sh7722_devices_setup()` reserves VPU/VEU/JPU memory and calls `platform_add_devices()`. `plat_early_device_setup()` registers SCIF0-2, CMT, and TMU0 early. `plat_irq_setup()` registers `intc_desc`; `plat_mem_setup()` is empty. DMA configuration uses `sh_dmae_slave_config`, `sh_dmae_channel`, and `sh_dmae_pdata`.

Control flow: the full device array includes a DMA engine, SCIF0-2, RTC, USB function controller `m66592_udc`, IIC, VPU4, VEU, JPU, CMT, TMU0, and SIU PCM audio. Early setup exposes serial and timers. INTC tables map IRQ0-7 plus DMA, video, USB, MMC, SCIF, SIOF, FLCTL, I2C, CMT, SIU, TMU, JPU, and LCDC sources into mask/prio/sense/ack registers.

State and persistence: static platform resources persist as device metadata after registration. DMA slave/channel tables encode CHCR transfer-size and direction bits. UIO memory resources are filled dynamically by `platform_resource_setup_memory()`.

Dependencies and integration points: integrates with `sh-dma-engine`, `sh-sci`, `sh-rtc`, `m66592_udc`, `i2c-sh_mobile`, `uio_pdrv_genirq`, `sh-cmt-32`, `sh-tmu`, `siu-pcm-audio`, and SuperH INTC. It relies on clock aliases for `sh-sci`, timers, I2C, USBF, and SIU.

Risks: DMA slave IDs, CHCR bits, and DMARS resources must match the DMA engine driver. UIO contiguous-memory placeholders are fragile. Empty `plat_mem_setup()` means no extra memory nodes are registered.

Test signals: exercise DMA-backed SIU/audio, SCIF ports, USB gadget mode, RTC interrupts, I2C, timer tick, multimedia UIO IRQs, and interrupt masking/ack for external IRQs.
