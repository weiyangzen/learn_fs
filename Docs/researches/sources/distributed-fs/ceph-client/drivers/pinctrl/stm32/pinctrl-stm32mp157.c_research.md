# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp157.c

## Purpose
This file supplies STM32MP157-specific pin data and platform-driver registration for the common STM32 pinctrl core. It covers both the main MP157 pin controller and the separate Z-bank controller used by the `st,stm32mp157-z-pinctrl` compatible.

The main `stm32mp157_pins[]` table describes banks PA through PK, 168 entries using GPIO numbers 0-167. The `stm32mp157_z_pins[]` table describes PZ0 through PZ7 using GPIO numbers 400-407. Entries use `STM32_PIN_PKG(...)`, so each pin is annotated with package availability bits such as `STM32MP_PKG_AA`, `STM32MP_PKG_AB`, `STM32MP_PKG_AC`, and `STM32MP_PKG_AD`. Alternate functions include the MP157 peripheral surface: timers, I2C, SPI/I2S, USART/UART, SAI, SDMMC, ETH1 GMII/MII/RGMII/RMII, DCMI, LCD, FMC, trace/HDP, eventout, and analog.

## Important APIs, Types, And Data
- `stm32mp157_pins[]`: main pin/function/package matrix for GPIO banks A-K.
- `stm32mp157_z_pins[]`: separate Z-bank matrix for secure/auxiliary PZ pins. It has its own match data so the common driver can register it independently from the main controller.
- `stm32mp157_match_data` and `stm32mp157_z_match_data`: both provide `.pins` and `.npins`; neither sets MP135/MP257-style secure, RIF, or IO sync flags in this file.
- `stm32mp157_pctrl_match[]`: maps `st,stm32mp157-pinctrl` to the main table and `st,stm32mp157-z-pinctrl` to the Z table.
- `stm32_pinctrl_dev_pm_ops`: delegates late system sleep handling to the shared STM32 suspend/resume operations.
- `stm32mp157_pinctrl_driver`: platform driver with shared `.probe = stm32_pctl_probe`.
- `stm32mp157_pinctrl_init()` and `arch_initcall(...)`: early built-in registration path.

## Control Flow
During architecture init, the driver registers with the platform bus. OF matching selects either the main match data or the Z-bank match data, and `stm32_pctl_probe` consumes the selected table to create the pinctrl device. All pin lookup, mux setting, GPIO range registration, pin configuration, and sleep-state handling are performed by the common STM32 pinctrl implementation.

The file's own control flow is deliberately minimal: its job is to bind static SoC data to the generic driver. Runtime behavior is a function of table contents plus board devicetree pin states.

## State And Persistence
The pin arrays and match data are read-only static configuration. Runtime state is persisted in hardware registers and common-driver software state. The PM ops hook ensures the MP157 instance participates in common late suspend/resume save and restore.

## Dependencies And Integration Points
- Depends on `pinctrl-stm32.h` macros/types and Linux OF/platform driver infrastructure.
- Integrates with board DTS through `st,stm32mp157-pinctrl` and `st,stm32mp157-z-pinctrl`; package metadata matters for validating or filtering pins on package variants.
- The Z-bank split is an important integration point because boards may have separate register regions and security domains for those pins.
- Peripheral drivers depend indirectly on this table when their `pinctrl-0` states request SDMMC, Ethernet, display, camera, UART, or other functions.

## Risks
- Package mask mistakes can expose pins not present on a package or hide valid ones.
- Main-bank and Z-bank numbering are disjoint; consumers must respect the 400-series PZ numbering used by the common STM32 binding.
- Alternate-function table drift against reference manuals or board schematics can create hard-to-debug peripheral failures.
- Because the file has no `MODULE_DEVICE_TABLE` or module helper and uses `arch_initcall`, registration assumes built-in kernel usage.

## Test Signals
- Compile-test and allmodconfig-style coverage catch macro/API drift in the common STM32 pinctrl interface.
- DTS validation and board boot on MP157 variants are the strongest behavioral tests, especially for package-specific pins and the Z-bank compatible.
- Runtime checks include successful pinctrl probe for both compatible strings, correct pin state application for SDMMC/Ethernet/display/camera/serial devices, visible GPIO lines, and clean suspend/resume restoration.
