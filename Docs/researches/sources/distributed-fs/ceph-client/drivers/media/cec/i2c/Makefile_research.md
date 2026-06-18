# sources/distributed-fs/ceph-client/drivers/media/cec/i2c/Makefile

Purpose: This Kbuild file maps I2C CEC config symbols to object files.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_CH7322) += ch7322.o` and `obj-$(CONFIG_CEC_NXP_TDA9950) += tda9950.o`.

Control flow and state: Kbuild compiles each driver when the matching tristate is enabled.

State and persistence behavior: Build-only; no runtime state.

Dependencies and integration points: Consumed by the parent CEC Makefile and Kconfig selections.

Risks and edge cases: New I2C CEC drivers must be added here and to Kconfig. Object names must match source files exactly for module builds.

Test signals: Build with each symbol as `m` and `y` to validate module names and built-in linking.
