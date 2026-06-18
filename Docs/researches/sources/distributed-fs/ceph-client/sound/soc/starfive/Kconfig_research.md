# sources/distributed-fs/ceph-client/sound/soc/starfive/Kconfig

Purpose: declares build-time configuration for StarFive JH7110 ASoC platform drivers. The menu is enabled for `ARCH_STARFIVE` or compile-test builds and requires common clock support.

Important entries: `SND_SOC_JH7110_PWMDAC` builds the PWM-DAC DAI driver and selects generic dmaengine PCM plus S/PDIF support. `SND_SOC_JH7110_TDM` builds the TDM DAI driver and selects generic dmaengine PCM. Both are tristate options so they can be built-in or modules.

Control flow and integration: these symbols control object inclusion in the sibling Makefile and expose user-visible configuration prompts. They also pull in core ASoC DMA helpers required by the drivers.

State and persistence: Kconfig has no runtime state, but it constrains which runtime integration points exist in a kernel image. Missing selections would surface as unresolved driver helpers or unavailable PCM registration.

Dependencies: `COMPILE_TEST || ARCH_STARFIVE`, `HAVE_CLK`, ASoC core, generic dmaengine PCM, and S/PDIF for the PWM-DAC option.

Risks: the menu-level dependencies do not explicitly depend on `SND_SOC`; these files live under sound/soc, but direct dependency clarity may matter for randconfig. `SND_SOC_JH7110_PWMDAC` selects `SND_SOC_SPDIF` even though the driver itself exposes S16 playback to PWM-DAC, so verify that dependency is intentional rather than inherited from an older design.

Test signals: run `make ARCH=riscv menuconfig` visibility checks, randconfig with `COMPILE_TEST`, module builds for both options, and dependency audit for selected symbols.
