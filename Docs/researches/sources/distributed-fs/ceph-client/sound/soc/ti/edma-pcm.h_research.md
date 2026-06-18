# sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.h

## Purpose
Exposes the EDMA PCM registration helper and provides a disabled-provider stub.

## Important APIs/types/functions
When `CONFIG_SND_SOC_TI_EDMA_PCM` is enabled it declares `edma_pcm_platform_register`; otherwise a static inline stub returns 0.

## Control flow
Enabled callers reach the implementation in `edma-pcm.c`; disabled callers compile and continue without registering EDMA PCM.

## State, dependencies, integration, risks, tests
No state is defined. It is used by DaVinci ASP and McASP drivers and relies on Kconfig selecting EDMA where needed. Risk is a successful no-op when real PCM registration was expected. Test builds with provider enabled/disabled and runtime PCM device creation when selected.
