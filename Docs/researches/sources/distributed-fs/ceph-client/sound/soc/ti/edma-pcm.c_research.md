# sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.c

## Purpose
TI EDMA dmaengine PCM registration helper for DaVinci ASP/McASP and related TI ASoC drivers.

## Important APIs/types/functions
Defines `edma_pcm_hardware`, `edma_dmaengine_pcm_config`, and exports `edma_pcm_platform_register`. Hardware supports mmap, pause/resume, no-period-wakeup, interleaved streams, 128 KiB buffers, 32-byte minimum periods, 64 KiB max periods, and up to 19 periods.

## Control flow
For DT devices, registration uses the static config. For non-DT devices, it allocates a config copy, sets legacy channel names `"tx"`/`"rx"`, and registers devm dmaengine PCM.

## State, dependencies, integration, risks, tests
Static PCM config is immutable; non-DT config persists via devm. Dependencies are ASoC, ALSA PCM, dmaengine PCM, and TI DAI callers. Risks are bounds not fitting all EDMA users, legacy channel mismatches, and period-count assumptions. Test DT/non-DT paths, boundary period sizes, pause/resume, and no-period-wakeup.
