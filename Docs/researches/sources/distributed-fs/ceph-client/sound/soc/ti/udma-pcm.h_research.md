<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.h

## Purpose
Public helper header for TI UDMA PCM platform registration.

## APIs, Types, and Functions
Declares `udma_pcm_platform_register(struct device *dev)` when `CONFIG_SND_SOC_TI_UDMA_PCM` is enabled. Otherwise provides a stub returning success.

## Control Flow, State, and Persistence
No runtime state is held here. The disabled-config stub allows callers to continue probing without registering a UDMA PCM platform, unlike the sDMA helper stub.

## Dependencies and Integration
Used by TI ASoC drivers targeting UDMA-capable SoCs. The helper implementation depends on DMAengine PCM.

## Risks and Test Signals
Risk is silent success when the helper is disabled, which can hide missing PCM platform registration until stream creation fails elsewhere. Test signals are builds with the config enabled/disabled and probe/runtime behavior of UDMA-based DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/udma-pcm.h -->
