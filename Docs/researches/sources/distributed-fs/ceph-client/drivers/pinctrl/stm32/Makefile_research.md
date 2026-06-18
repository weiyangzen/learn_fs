# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Makefile

## Purpose
This Makefile maps STM32 pinctrl Kconfig symbols to the common core, SoC-specific pin table drivers, and the HDP driver.

## Important APIs, types, and functions
`obj-$(CONFIG_PINCTRL_STM32)` builds `pinctrl-stm32.o`. The STM32F/MP SoC symbols build their corresponding pin table objects, such as `pinctrl-stm32mp257.o`. `obj-$(CONFIG_PINCTRL_STM32_HDP)` builds `pinctrl-stm32-hdp.o`.

## Control flow
Kbuild includes object files according to Kconfig values. SoC drivers depend on the common core for exported `stm32_pctl_probe()` and PM helpers; HDP is independent and does not link against the common STM32 pinctrl core.

## State and persistence behavior
There is no runtime state. Build output determines which platform drivers can bind at runtime.

## Dependencies and integration points
This file integrates with `drivers/pinctrl/stm32/Kconfig`. Its layout mirrors the code structure: common core plus generated/static SoC pin description files, with HDP as a standalone driver.

## Risks
If a SoC symbol is enabled without the common core selection, unresolved references to `stm32_pctl_probe()` or PM helpers would occur; Kconfig selections guard this. Adding new SoC files requires both a Kconfig symbol and an object line.

## Test signals
Build tests should inspect object inclusion for all STM32 pinctrl symbols and verify module linking for MP257 and HDP. Static checks should ensure every SoC object selected here has matching OF compatible data and Kconfig entry.
