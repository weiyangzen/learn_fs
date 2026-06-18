# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.c

## Purpose
Tegra dmaengine PCM helper. It provides common PCM hardware limits, platform registration, component callbacks, DMA slave configuration, pointer reporting, and fixed-buffer allocation.

## Important APIs/types/functions
Exports `tegra_pcm_platform_register`, `devm_tegra_pcm_platform_register`, `tegra_pcm_platform_register_with_chan_names`, `tegra_pcm_platform_unregister`, `tegra_pcm_open`, `tegra_pcm_close`, `tegra_pcm_hw_params`, `tegra_pcm_pointer`, and `tegra_pcm_new`.

## Control flow
Registration passes a static dmaengine config, optionally with channel names and parent DMA device. `open` skips no-pcm links, installs hardware and period-byte constraints, requests the named DMA channel, opens dmaengine PCM, and sets a 500 ms wait time. `hw_params` builds a DMA slave config, fills source/destination address and bursts, and calls `dmaengine_slave_config`. `new` allocates a fixed write-combine DMA buffer with an older-DT IOMMU fallback.

## State, dependencies, integration, risks, tests
No mutable global state; per-stream state is ALSA runtime and dmaengine channel ownership. Dependencies are ASoC, ALSA PCM, dmaengine PCM, OF, and CPU DAI DMA data. Risks are channel-name mismatches, fixed burst assumptions, 32-bit DMA mask limits, and IOMMU fallback errors. Test open/close, hw_params, mmap allocation, no-pcm links, and error cleanup.
