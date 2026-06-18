# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.h

## Purpose
Exposes Tegra PCM helper callbacks and registration functions to Tegra audio controller drivers.

## Important APIs/types/functions
Declares `tegra_pcm_new/open/close/hw_params/pointer`, basic and devm platform registration, channel-name registration, and unregister.

## Control flow
No executable logic. ASoC components wire the callbacks into component drivers, and platform DAIs call registration helpers from probe.

## State, dependencies, integration, risks, tests
No state is defined; callers provide runtime/substream and DMA config storage. It depends on ALSA and dmaengine PCM headers. Risks are callback signature drift and caller-provided config lifetime problems. Compile all Tegra users and run playback/capture smoke tests.
