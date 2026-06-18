<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.c

## Purpose
Shared TI UDMA PCM registration helper for newer TI ASoC drivers. It wraps DMAengine PCM registration with broad hardware limits suitable for UDMA.

## APIs, Types, and Functions
Defines `udma_pcm_hardware`, `udma_dmaengine_pcm_config`, and exported `udma_pcm_platform_register(struct device *dev)`. The hardware configuration supports mmap, pause/resume, no-period-wakeup, interleaved access, 32-byte minimum periods, 64 KiB maximum periods, `SIZE_MAX` buffer bytes, and `UINT_MAX` periods.

## Control Flow, State, and Persistence
The only runtime path is `udma_pcm_platform_register()`, which registers the static DMAengine PCM config with no special flags. Persistent data is managed by the devm PCM registration.

## Dependencies and Integration
Depends on ALSA DMAengine PCM helpers and is intended for TI drivers using UDMA channel bindings with standard DMAengine lookup.

## Risks and Test Signals
Risks include extremely large advertised buffer/period counts relying on lower layers to constrain allocations and no preallocated buffer size. Test signals are successful DMAengine PCM registration, ALSA constraint reporting, mmap playback/capture with UDMA, pause/resume, and large-buffer rejection or acceptance by the final DMA/memory stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.c -->
