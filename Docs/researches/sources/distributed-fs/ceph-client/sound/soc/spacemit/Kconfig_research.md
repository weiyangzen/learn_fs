# sources/distributed-fs/ceph-client/sound/soc/spacemit/Kconfig

Purpose: Kconfig menu for SpacemiT K1 I2S ASoC support.

Important APIs/types: `SND_SOC_K1_I2S` is a tristate driver option depending on `DMA_CMA`, selecting generic DMAEngine PCM, and gated by `COMPILE_TEST || ARCH_SPACEMIT` plus clock support.

Control flow/state: no runtime state; controls whether the K1 I2S CPU DAI driver is built.

Dependencies/integration: intended for Device Tree systems with the K1 I2S controller, clocks, reset, and DMA channels.

Risks/test signals: compile-test should verify dependencies are sufficient on non-SpacemiT architectures, and runtime configs should ensure DMA_CMA is enabled.
