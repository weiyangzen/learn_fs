# sources/distributed-fs/ceph-client/sound/soc/img/Kconfig

Purpose: Kconfig menu for Imagination Technologies ASoC platform and codec drivers, gated to MIPS or compile-test builds.

Important APIs/types/functions: options `SND_SOC_IMG_I2S_IN`, `SND_SOC_IMG_I2S_OUT`, `SND_SOC_IMG_PARALLEL_OUT`, `SND_SOC_IMG_SPDIF_IN`, `SND_SOC_IMG_SPDIF_OUT`, and `SND_SOC_IMG_PISTACHIO_INTERNAL_DAC`. The digital interface drivers select `SND_SOC_GENERIC_DMAENGINE_PCM`.

Control flow: selected symbols drive object inclusion in the IMG Makefile.

State and persistence: configuration-time only.

Dependencies/integration: depends on `MIPS || COMPILE_TEST`; each option maps to a platform driver or codec driver.

Risks: DAC option does not select regulator/syscon dependencies because those are framework-level dependencies assumed elsewhere. Help text is platform-generic and does not include compatible strings.

Test signals: kconfig matrix for each symbol as module/built-in, especially compile-test on non-MIPS.
