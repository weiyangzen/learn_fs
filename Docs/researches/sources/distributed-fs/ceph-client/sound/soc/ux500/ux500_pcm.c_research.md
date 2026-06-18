# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.c

## Purpose
Generic DMAengine PCM platform glue for Ux500 MSP DAIs. It registers an ASoC DMAengine PCM device and adapts ALSA hw_params into DMA slave configuration for MSP transmit/receive.

## Important APIs, Types, and Functions
Exports `ux500_pcm_register_platform()` and `ux500_pcm_unregister_platform()`. The main callback is `ux500_pcm_prepare_slave_config()`, installed in `ux500_dmaengine_of_pcm_config`.

## Control Flow, State, and Persistence
Register calls `snd_dmaengine_pcm_register()` with a prepare callback. During hw_params, the prepare callback retrieves CPU DAI DMA data, translates hw_params with `snd_hwparams_to_dma_slave_config()`, forces 4-burst and 2-byte bus widths, and sets either destination or source address to the MSP data register. Unregister removes the DMAengine PCM platform.

## Dependencies and Integration Points
Depends on ALSA SoC, PCM params, DMAengine PCM helpers, and DMA data initialized by `ux500_msp_dai_of_probe()`. It is registered from `ux500_msp_drv_probe()`.

## Risks and Test Signals
Risks include fixed 2-byte bus width despite stream format negotiation, hard-coded maxburst of 4, no custom channel filter, and reliance on CPU DAI DMA data existing. Test signals are DMA slave config for playback/capture, working cyclic DMA through MSP data register, buffer/period limits from generic DMAengine, and clean register/unregister on platform probe/remove.
