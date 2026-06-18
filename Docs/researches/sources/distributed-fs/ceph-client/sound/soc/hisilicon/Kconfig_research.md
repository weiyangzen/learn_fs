# sources/distributed-fs/ceph-client/sound/soc/hisilicon/Kconfig

Purpose: Kconfig menu for Hisilicon ASoC platform support.

Important APIs/types/functions: `SND_I2S_HI6210_I2S` tristate selects `SND_SOC_GENERIC_DMAENGINE_PCM`.

Control flow: enabling the symbol builds the HI6210 I2S controller driver and ensures generic dmaengine PCM support.

State and persistence: compile-time configuration only.

Dependencies/integration: paired with `hisilicon/Makefile`; broader sound menu supplies ASoC dependencies.

Risks: help text is terse and does not mention required clocks/syscon/DT compatible. The config symbol lacks architecture gating, so compile-test coverage may depend on all included headers being portable.

Test signals: kbuild with `CONFIG_SND_I2S_HI6210_I2S=m/y` should build `hi6210-i2s.o` and select generic DMA engine PCM.
