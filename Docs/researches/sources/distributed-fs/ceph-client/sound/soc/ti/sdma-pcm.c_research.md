<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.c

## Purpose
Shared TI sDMA PCM registration helper for ASoC CPU DAIs. It supplies common PCM hardware constraints and adapts optional named DMA channels to `devm_snd_dmaengine_pcm_register()`.

## APIs, Types, and Functions
Defines `sdma_pcm_hardware`, `sdma_dmaengine_pcm_config`, and exported `sdma_pcm_platform_register(struct device *dev, char *txdmachan, char *rxdmachan)`. The hardware config supports mmap, pause/resume, no-period-wakeup, interleaved access, 32-byte minimum periods, 64 KiB maximum periods, 128 KiB buffers, and 2-255 periods.

## Control Flow, State, and Persistence
If both channel names are NULL, registration uses standard `tx`/`rx` DMA channel names and the static config. If one or both custom names are supplied, it allocates a per-device config, copies defaults, sets half-duplex when one direction is absent, normalizes the single direction into `chan_names[0]`, and registers DMAengine PCM. Persistent state is owned by devm and DMAengine PCM.

## Dependencies and Integration
Depends on ALSA DMAengine PCM helpers and is called by OMAP McBSP, McPDM, DMIC, and HDMI drivers. Channel names such as `tx`, `rx`, `dn_link`, `up_link`, and `audio_tx` are supplied by callers and DT DMA bindings.

## Risks and Test Signals
Risks include caller confusion over single-direction channel normalization, fixed 128 KiB preallocation limiting large buffers, and half-duplex flags when only capture/playback is requested. Test signals are full-duplex default registration, named duplex registration, named half-duplex registration, DMA channel lookup from DT, and buffer/period constraint visibility in ALSA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.c -->
