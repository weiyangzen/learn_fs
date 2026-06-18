# sources/distributed-fs/ceph-client/sound/soc/sprd/Kconfig

Purpose: Kconfig menu for Spreadtrum/Unisoc ASoC platform support.

Important APIs/types: `SND_SOC_SPRD` enables the SoC audio platform and selects compressed audio support. `SND_SOC_SPRD_MCDT` enables multi-channel data transfer support and depends on the base Spreadtrum ASoC platform.

Control flow/state: no runtime state.

Dependencies/integration: used by Spreadtrum PCM DMA/compress and MCDT source files in the same directory.

Risks/test signals: build tests should cover `SND_SOC_SPRD` with and without `SND_SOC_SPRD_MCDT`, including COMPILE_TEST on non-SPRD architectures.
