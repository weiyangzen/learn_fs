# sources/distributed-fs/ceph-client/sound/soc/sti/Kconfig

Purpose: defines the STi ASoC platform support switch.

Important entry: `menuconfig SND_SOC_STI` is a tristate gated by `SND_SOC` and `ARCH_STI || COMPILE_TEST`, selecting `SND_SOC_GENERIC_DMAENGINE_PCM`.

Control flow and integration: enabling the symbol builds the composite STi uniperipheral DAI driver from the sibling Makefile. The menu text identifies STIH416-class platforms and covers all STi uniplayer/unireader instances.

State and persistence: no runtime state. The symbol controls whether the STi platform DAI and DMA PCM registration code exists in the kernel.

Dependencies: ASoC core, STi architecture or compile-test, and generic dmaengine PCM. The C files also depend on syscon/regmap, pinctrl, clocks, IRQs, and ALSA IEC958 controls, but those are not explicit Kconfig dependencies here.

Risks: hidden dependencies may surface in unusual randconfig builds if selected helpers are not otherwise enabled. The single symbol builds all supported player/reader variants, so it cannot trim unused variants by compatible.

Test signals: run randconfig with `COMPILE_TEST`, build as module and built-in, and verify top-level sound/soc Kconfig includes the STi menu only in intended contexts.
