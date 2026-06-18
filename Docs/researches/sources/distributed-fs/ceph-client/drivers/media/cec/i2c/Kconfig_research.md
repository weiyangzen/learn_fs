# sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Kconfig

Purpose: This file exposes I2C-attached CEC controller driver choices for CH7322 and NXP TDA9950/TDA998x.

Important APIs, types, and functions: `CEC_CH7322` is a tristate driver depending on `I2C`, selecting `REGMAP`, `REGMAP_I2C`, and `CEC_CORE`. `CEC_NXP_TDA9950` is a tristate driver depending on `I2C`, selecting `CEC_NOTIFIER` and `CEC_CORE`, and defaulting to `DRM_I2C_NXP_TDA998X`.

Control flow and state: Selecting either symbol causes the corresponding object to be compiled by the CEC I2C Makefile and selects core/helper features needed by the driver.

State and persistence behavior: Only `.config` build state.

Dependencies and integration points: Integrates I2C CEC devices with regmap for CH7322 and notifier-based HDMI physical-address propagation for TDA9950.

Risks and edge cases: TDA9950’s default ties it to a DRM encoder config, so build coverage should include both standalone and glue use. CH7322 requires regmap selection or probe-time register access cannot compile.

Test signals: Kconfig/build tests for both drivers as built-in and modules, with and without the related DRM TDA998x symbol.
