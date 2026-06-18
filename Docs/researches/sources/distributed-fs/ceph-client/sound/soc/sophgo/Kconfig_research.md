# sources/distributed-fs/ceph-client/sound/soc/sophgo/Kconfig

Purpose: Kconfig menu for Sophgo CV1800B/SG2002 ASoC support.

Important APIs/types: `SND_SOC_CV1800B_TDM` builds the I2S/TDM CPU DAI and selects generic DMAEngine PCM. `SND_SOC_CV1800B_ADC_CODEC` builds the internal RXADC codec DAI. `SND_SOC_CV1800B_DAC_CODEC` builds the internal TXDAC codec DAI. The menu depends on `COMPILE_TEST || ARCH_SOPHGO`.

Control flow/state: no runtime state; controls which platform components are available to Device Tree machine descriptions.

Dependencies/integration: intended for Device Tree/simple-audio-card integration with the Sophgo SoC audio blocks.

Risks/test signals: build matrix should cover each symbol as module and built-in, plus compile-test without ARCH_SOPHGO.
