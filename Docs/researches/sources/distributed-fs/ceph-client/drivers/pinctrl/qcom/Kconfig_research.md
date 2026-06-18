# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Kconfig

## Purpose
Defines the Qualcomm pinctrl Kconfig menu, including the TLMM core, PMIC GPIO/MPP drivers, LPASS LPI core, and LPASS LPI SoC variants.

## Important APIs, Types, And Functions
Primary symbols are `PINCTRL_MSM`, `PINCTRL_QCOM_SPMI_PMIC`, `PINCTRL_QCOM_SSBI_PMIC`, `PINCTRL_LPASS_LPI`, and LPASS variants such as `PINCTRL_MILOS_LPASS_LPI`, `PINCTRL_SC7280_LPASS_LPI`, `PINCTRL_SDM660_LPASS_LPI`, `PINCTRL_SM8250_LPASS_LPI`, `PINCTRL_SM8550_LPASS_LPI`, and `PINCTRL_SM8650_LPASS_LPI`. It also sources `drivers/pinctrl/qcom/Kconfig.msm` for many SoC TLMM symbols.

## Control Flow
The menu is visible under `ARCH_QCOM` or `COMPILE_TEST`. Selecting symbols pulls in required pinmux, pinconf, gpiolib, irqchip, regmap, SPMI, SSBI, OF, and Qualcomm SCM dependencies. Makefile object rules consume these symbols to build the matching drivers.

## State And Persistence
Only build-time `.config` state is persisted. Runtime state is created by the selected driver objects, not this file.

## Dependencies And Integration Points
Integrates Qualcomm pinctrl with OF, GPIOLIB, hierarchical IRQ domains, QCOM SCM, SPMI/SSBI PMIC buses, and the qcom Makefile. `PINCTRL_MSM` is the common TLMM core dependency for SoC-specific entries sourced from `Kconfig.msm`.

## Risks
Dependency mistakes can expose drivers without required bus or IRQ infrastructure. LPASS variants depend on the LPASS core symbol, so missed dependencies hide variants. The sourced `Kconfig.msm` file must stay aligned with Makefile object names.

## Test Signals
`allmodconfig`, `COMPILE_TEST`, Qualcomm defconfig builds, menu visibility checks, and dependency-cycle checks are useful signals.
