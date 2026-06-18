# sources/distributed-fs/ceph-client/drivers/soc/cirrus/Kconfig

Purpose: Kconfig entry for Cirrus Logic EP93xx SoC support.

Important configuration: under `ARCH_EP93XX`, `EP93XX_SOC` defaults to yes and selects `SOC_BUS` and `AUXILIARY_BUS`. Help text describes locked syscon register access and auxiliary devices for reset, pinctrl, and clock functionality.

Control flow and integration: this option enables `soc-ep93xx.o`, which registers SoC metadata and auxiliary devices backed by syscon/regmap access.

State and persistence: build-time only.

Risks and test signals: risks are missing framework selects for auxiliary devices or SoC bus registration. Test signals are EP93xx defconfig coverage and build/link success with auxiliary bus enabled.
