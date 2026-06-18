# sources/distributed-fs/ceph-client/sound/soc/stm/Kconfig

Purpose: declares STM32 ASoC driver configuration for SAI, I2S, SPDIFRX, and DFSDM audio capture.

Important entries: `SND_SOC_STM32_SAI` selects generic dmaengine PCM, regmap MMIO, and IEC958 PCM support. `SND_SOC_STM32_I2S` selects generic dmaengine PCM and regmap MMIO. `SND_SOC_STM32_SPDIFRX` selects generic dmaengine PCM, regmap MMIO, and S/PDIF codec support. `SND_SOC_STM32_DFSDM` depends on `STM32_DFSDM_ADC` and selects generic dmaengine PCM, DMIC codec, and IIO callback buffers.

Control flow and integration: these symbols are consumed by the sibling Makefile to include controller and sub-block objects. Architecture dependency is `(ARCH_STM32 && OF) || COMPILE_TEST` for register DAIs and `ARCH_STM32 || COMPILE_TEST` for DFSDM.

State and persistence: no runtime state; symbols determine which platform drivers and helper objects are built.

Dependencies: ASoC core, common clock where required, regmap, generic dmaengine PCM, S/PDIF/IEC958 helpers, STM32 DFSDM ADC, and IIO buffer callbacks.

Risks: DFSDM requires IIO callback plumbing; missing or mismatched IIO symbols will break link/build. `COMPILE_TEST` coverage is useful but may mask runtime-only clock/reset/device-tree requirements.

Test signals: randconfig for each symbol, module and built-in builds, dependency closure checks, and DT binding tests for the corresponding compatible strings.
