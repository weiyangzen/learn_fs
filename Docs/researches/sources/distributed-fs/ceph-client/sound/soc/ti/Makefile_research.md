# sources/distributed-fs/ceph-client/sound/soc/ti/Makefile

## Purpose
Maps TI ASoC Kconfig symbols to Kbuild object aggregates for PCM providers, CPU DAIs, and machine drivers.

## Important APIs/types/functions
Defines aggregates such as `snd-soc-ti-edma-y`, `snd-soc-davinci-asp-y`, `snd-soc-davinci-mcasp-y`, OMAP DAI objects, and board objects including `snd-soc-davinci-evm-y` and `snd-soc-ams-delta-y`. `obj-$(CONFIG_...)` lines attach them to config symbols.

## Control flow
No runtime control flow. Kbuild expands selected config symbols to built-in or module objects.

## State, dependencies, integration, risks, tests
Build state is controlled by `.config` and output directories. The file must stay aligned with Kconfig and source names. Risks are stale object names, missing aggregate entries, and module-name churn. Test representative builds and inspect module output.
