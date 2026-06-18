# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pcm-dma.c

## Purpose
This file provides the DMAengine PCM platform registration used by Atmel SSC audio when the SSC platform data selects DMA instead of PDC. It supplies generic PCM hardware constraints and DMA slave configuration for SSC transmit and receive registers.

## Important APIs, Types, And Functions
The exported API is `atmel_pcm_dma_platform_register(struct device *dev)`. `atmel_pcm_dma_irq()` is an SSC error handler installed into `atmel_pcm_dma_params`; `atmel_pcm_configure_dma()` prepares `dma_slave_config` and sets the handler. `atmel_dmaengine_pcm_config` ties these to `devm_snd_dmaengine_pcm_register()`.

## Control Flow
Registration installs a generic DMAengine PCM component. During `hw_params`, `atmel_pcm_configure_dma()` converts ALSA params to DMA slave config, points DMA to `SSC_THR` and `SSC_RHR`, sets bursts to one, and arms the SSC error callback. When SSC interrupt code reports an overrun/underrun, `atmel_pcm_dma_irq()` disables the direction, stops the stream with xrun, and drains status.

## State And Persistence
No private platform state is allocated here. It mutates shared `struct atmel_pcm_dma_params` owned by the SSC DAI by setting `dma_intr_handler`.

## Dependencies And Integration Points
It depends on `atmel-pcm.h`, `linux/atmel-ssc.h`, DMAengine PCM helpers, and the SSC DAI interrupt fanout. It is selected by `CONFIG_SND_ATMEL_SOC_DMA`.

## Risks And Test Signals
Risk is that the shared handler pointer must be cleared by the caller's stream lifecycle, and xrun recovery must leave SSC status clean. Test signals are DMAengine PCM registration, valid DMA slave addresses, expected xrun logs on injected SSC errors, and successful playback/capture with SSC DMA mode.
