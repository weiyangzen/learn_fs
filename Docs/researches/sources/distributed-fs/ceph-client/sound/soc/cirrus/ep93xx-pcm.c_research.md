# sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.c

Purpose: EP93xx ALSA SoC PCM platform helper built on generic dmaengine PCM. It defines EP93xx PCM hardware limits and exports a devm registration function for CPU DAI drivers.

Important APIs, types, and functions: `ep93xx_pcm_hardware` advertises mmap, interleaved, block-transfer PCM with 128 KiB max buffer, 32..32768 byte periods, 1..32 periods, and FIFO size 32. `ep93xx_dmaengine_pcm_config` references those limits and preallocates 128 KiB. `devm_ep93xx_pcm_platform_register()` wraps `devm_snd_dmaengine_pcm_register()` and is exported GPL.

Control flow: the only runtime function is called by an EP93xx controller probe, registers a managed dmaengine PCM component for the device, and lets generic dmaengine callbacks handle PCM operation.

State and persistence: static hardware/config structs plus managed ALSA/dmaengine allocations. No driver-private persistent runtime state.

Dependencies and integration: depends on Linux dmaengine and ALSA generic dmaengine PCM. Used by `ep93xx-i2s.c` after DAI registration.

Risks: correctness depends on DAI drivers supplying valid `snd_dmaengine_dai_dma_data`. The static limits must match EP93xx DMA capabilities. The exported helper can create module dependencies if Kconfig/Makefile constraints are weakened.

Test signals: compile as built-in and module, call from EP93xx I2S probe, run playback/capture DMA with minimum and maximum period sizes, and verify preallocated buffer sizing.
