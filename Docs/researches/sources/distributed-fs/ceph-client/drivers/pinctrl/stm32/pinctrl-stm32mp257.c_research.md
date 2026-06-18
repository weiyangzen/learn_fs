# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp257.c

## Purpose
This file provides STM32MP257 pin and package data plus platform-driver registration for the common STM32 pinctrl implementation. It covers the main MP257 pin controller and a Z-bank controller, and unlike the older MP135/MP157 units it is module-friendly through `module_platform_driver` and an OF module device table.

The main `stm32mp257_pins[]` table covers 162 main-bank entries over PA-PK with GPIO numbers 0-45, 48-125, and 128-167. The `stm32mp257_z_pins[]` table covers PZ0-PZ9 with GPIO numbers 400-409. Entries use `STM32_PIN_PKG(...)` with MP257 package masks `STM32MP_PKG_AI`, `STM32MP_PKG_AK`, and `STM32MP_PKG_AL`. Alternate functions reflect newer MP257 peripherals such as SPI5-SPI8, USART/LPUART, I2C/I3C, MDF/ADF, ETH1/ETH2/ETH3, DCMI/PSSI/DCMIPP, LCD, FMC, FDCAN, timers, eventout, debug triggers, MCO, and analog.

## Important APIs, Types, And Data
- `stm32mp257_pins[]`: main MP257 pin/function/package matrix.
- `stm32mp257_z_pins[]`: Z-bank pin/function/package matrix for PZ0-PZ9.
- `stm32mp257_match_data` and `stm32mp257_z_match_data`: both set `.io_sync_control = true`, `.secure_control = true`, and `.rif_control = true` in addition to `.pins` and `.npins`. Those flags opt the common STM32 driver into MP257-specific synchronization, security, and resource isolation handling.
- `stm32mp257_pctrl_match[]`: OF table for `st,stm32mp257-pinctrl` and `st,stm32mp257-z-pinctrl`; exported via `MODULE_DEVICE_TABLE(of, ...)`.
- `stm32_pinctrl_dev_pm_ops`: uses common late sleep callbacks.
- `stm32mp257_pinctrl_driver`: shared-probe platform driver registered by `module_platform_driver`.

## Control Flow
Module or built-in initialization registers the platform driver. Matching a devicetree pinctrl node selects either main or Z-bank match data. `stm32_pctl_probe` then initializes the common STM32 pinctrl device with the selected table and feature flags. The common driver interprets flags to handle IO synchronization, secure-control, and RIF policy around register access.

This file contains no custom mux logic. The pin matrix and match flags are the control inputs consumed by shared STM32 code and by board DTS pin state declarations.

## State And Persistence
Static arrays and match data are immutable. Runtime mux, GPIO, IO sync, secure, and RIF state lives in the common driver and SoC registers. The PM ops hook opts the MP257 driver into common late suspend/resume state preservation.

## Dependencies And Integration Points
- Depends on `pinctrl-stm32.h`, Linux module/platform/OF infrastructure, and the common STM32 pinctrl implementation.
- Integrates with devicetree through `st,stm32mp257-pinctrl` and `st,stm32mp257-z-pinctrl`.
- Package masks control availability across AI/AK/AL packages.
- The `.io_sync_control`, `.secure_control`, and `.rif_control` flags integrate this static data with common-driver support for MP257 isolation and synchronization features.
- Peripheral integration spans Ethernet, camera/display, serial buses, memory bus, audio, timers, and GPIO consumers.

## Risks
- MP257 has several dense alternate-function rows; duplicate or mistaken alternate-function numbers can create ambiguous or wrong mux selection. For example, adjacent high-speed camera/display/Ethernet functions share many banks.
- Feature flags mean this table is coupled to firmware/security configuration. A board may fail to apply pin states if secure/RIF ownership does not match Linux expectations.
- Main-bank numbering skips PC14/PC15 and PH0/PH1-style holes relative to a simple contiguous package assumption; users must follow the explicit table.
- Module support adds aliasing expectations: the OF module table must stay in sync with compatible strings.

## Test Signals
- Compile and module alias generation should validate the module-platform registration path.
- DT binding validation should cover compatible strings, package-visible pins, and pinmux references.
- Runtime signals include successful probe as built-in or module, no secure/RIF access denials, correct pin state activation for I3C/I2C/SPI/UART/Ethernet/display/camera/FMC consumers, GPIO visibility, and suspend/resume restoration.
