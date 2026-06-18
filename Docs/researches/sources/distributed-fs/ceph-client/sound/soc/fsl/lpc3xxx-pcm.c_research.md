# sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-pcm.c

## Purpose
DMA-engine PCM registration helper for LPC3xxx/LPC32xx I2S.

## APIs, Types, and Functions
Defines `lpc3xxx_pcm_config` with `SNDRV_DMAENGINE_PCM_FLAG_COMPAT` and a compatibility DMA channel filter. Exports `lpc3xxx_pcm_register(struct platform_device *pdev)`, which calls `devm_snd_dmaengine_pcm_register()`.

## Control Flow, State, and Persistence
No private state is maintained. Registration delegates PCM device creation and DMA channel management to the generic DMA-engine PCM framework for the lifetime of the platform device.

## Dependencies and Integration
Depends on ASoC DMA-engine PCM APIs. Called from `lpc32xx_i2s_probe()` after DAI component registration.

## Risks and Test Signals
Risks are limited to DMA channel compatibility matching and platform DT/resource mismatches. Test signals are PCM device creation, DMA channel allocation for both directions, and successful audio transfer through the I2S DAI.
