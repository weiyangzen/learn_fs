# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/Kconfig

## Purpose
This Kconfig fragment defines the STM32 pinctrl family build options, including the common STM32 pinctrl core, multiple SoC pin table drivers, and the separate Hardware Debug Port pinctrl/GPIO driver.

## Important APIs, types, and functions
`PINCTRL_STM32` is the common tristate selected by SoC-specific symbols and selects `PINMUX`, `GENERIC_PINCONF`, `GPIOLIB`, `IRQ_DOMAIN_HIERARCHY`, and `MFD_SYSCON`. SoC symbols include STM32F429/F469/F746/F769/H743/MP135/MP157/MP257 and select the common core. `PINCTRL_STM32_HDP` is a separate tristate selecting `PINMUX`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIO_GENERIC`.

## Control flow
The whole fragment is gated by `ARCH_STM32 || COMPILE_TEST`. Kconfig selection controls Makefile object inclusion. Many MCU/MPU symbols default to their platform machine symbols; MP257 can be tristate and defaults on STM32MP25 or STM32 ARM64. HDP defaults on most STM32 architectures except ARM single-core ARMv7-M.

## State and persistence behavior
There is no runtime state. The selected symbols decide whether core probe helpers, SoC pin tables, PM ops, GPIO IRQ hierarchy support, and HDP support are built.

## Dependencies and integration points
The core depends on OF and syscon/IRQ-domain infrastructure because `pinctrl-stm32.c` parses DT GPIO-bank nodes and may configure a syscfg IRQ mux. HDP depends on OF/HAS_IOMEM and GPIO_GENERIC because it registers an output-only generic gpiochip.

## Risks
Most SoC symbols are bool, while MP257 and HDP are tristate; mixed built-in/module combinations should be checked for exported-symbol availability. HDP has no explicit `STM32_FIREWALL` dependency but uses guarded firewall calls under `IS_ENABLED(CONFIG_STM32_FIREWALL)`. The outer `ARCH_STM32 || COMPILE_TEST` block limits visibility, so cross-architecture build coverage relies on `COMPILE_TEST`.

## Test signals
Build matrix should cover each SoC symbol, HDP enabled alone, common core as built-in and module where possible, and `COMPILE_TEST`. Dependency tests should confirm `PINCTRL_STM32` pulls in IRQ hierarchy and syscon support needed by the core.
