# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-audio-s3c64xx.c

Purpose: static platform devices and GPIO mux setup for S3C64xx audio controllers.

Important APIs/types/functions: `s3c64xx_i2s_cfg_gpio()`, platform devices such as `s3c64xx_device_iis0` and sibling audio devices, resource arrays, and exported device symbols.

Control flow: board code registers these platform devices. The I2S GPIO callback selects pin banks/functions based on controller ID and returns `-EINVAL` for invalid IDs.

State and persistence: platform resources define MMIO ranges and DMA masks; GPIO configuration mutates pin mux registers.

Dependencies and integration points: integrates ASoC Samsung I2S/PCM/AC97 drivers, S3C IRQ/map constants, and GPIO config helpers.

Risks: wrong controller ID or pin function breaks audio routing. Static devices are legacy ATAGS-era and absent on DT-only platforms.

Test signals: ASoC device probe, I2S0/1/2 pinmux, playback/capture, and invalid-ID logging.
