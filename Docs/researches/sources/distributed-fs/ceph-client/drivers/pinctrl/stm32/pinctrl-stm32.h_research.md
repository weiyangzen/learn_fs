# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32.h

## Purpose
This header defines the common STM32 SoC pin-description format and the public common-core entry points used by STM32 pin table drivers.

## Important APIs, types, and functions
Macros encode and decode DT pinmux values: `STM32_PIN_NO(x)`, `STM32_GET_PIN_NO(x)`, and `STM32_GET_PIN_FUNC(x)`. Function constants define GPIO, alternate functions AF0-AF15, analog, reserved, and `STM32_CONFIG_NUM`. Package masks such as `STM32MP_PKG_AA` and `STM32MP_PKG_AL` allow SoC tables to filter pins by package. `struct stm32_desc_function` names one function slot. `struct stm32_desc_pin` combines a `pinctrl_pin_desc`, function table, and package mask. Macros `STM32_PIN`, `STM32_PIN_PKG`, and `STM32_FUNCTION` help build SoC pin arrays. `struct stm32_pinctrl_match_data` passes pin tables and feature flags to the common core. Exported declarations are `stm32_pctl_probe()`, `stm32_pinctrl_suspend()`, and `stm32_pinctrl_resume()`.

## Control flow
SoC files instantiate arrays of `stm32_desc_pin` and match-data records, then call the common probe from their platform-driver probe. The common core reads function tables, package masks, and feature flags to build runtime pin groups and register operations.

## State and persistence behavior
The header itself holds no state. Its structures define persistent contracts for SoC pin tables and PM helper usage. Package masks and function numbering must remain compatible with DT bindings.

## Dependencies and integration points
It depends on Linux pinctrl descriptors and generic pinconf definitions. It is included by the common STM32 core and all STM32 SoC-specific pin table drivers.

## Risks
DT pinmux encoding uses high bits for pin number and low 8 bits for function; mismatched bindings or macros will misroute pins. `STM32_CONFIG_NUM` sizes every function array, so adding new function constants changes table layout. Package filtering treats a zero package mask as generally available unless SoC tables and common code interpret it carefully.

## Test signals
Compile tests should cover all SoC tables using these macros. DT binding tests should verify encoded pinmux values decode to expected pin/function pairs. Package-specific boards should confirm unavailable pins are filtered from the runtime descriptor table.
