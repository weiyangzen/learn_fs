# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32mp135.c

## Purpose
This file is the SoC-specific pin description and platform-driver registration unit for the STM32MP135 pin controller. It does not implement generic pinctrl mechanics itself; instead it provides the STM32 pinctrl core with a static `stm32_desc_pin` table for the MP135 package and binds that data to the `st,stm32mp135-pinctrl` devicetree compatible.

The table enumerates 135 physical/logical pins from banks PA through PI, using GPIO numbers 0-126 and 128-135. Each `STM32_PIN(...)` entry supplies a `PINCTRL_PIN(number, name)` plus supported alternate functions such as timers, USART/UART, SPI/I2S, I2C, SAI, SDMMC, FMC, LCD, DCMIPP, ETH1/ETH2, boot strap pins, and analog mode. GPIO function 0 and analog function 17 are common anchors across the entries.

## Important APIs, Types, And Data
- `stm32mp135_pins[]`: the authoritative MP135 pin/function matrix consumed by the STM32 pinctrl core. The array uses macros from `pinctrl-stm32.h` and includes the SoC-specific alternate-function numbers expected by hardware and devicetree pinmux encodings.
- `stm32mp135_match_data`: a `struct stm32_pinctrl_match_data` with `.pins`, `.npins`, and `.secure_control = true`. This tells the generic STM32 probe path that MP135 participates in secure pin configuration handling.
- `stm32mp135_pctrl_match[]`: OF match table with `compatible = "st,stm32mp135-pinctrl"` and `.data = &stm32mp135_match_data`.
- `stm32_pinctrl_dev_pm_ops`: wires late system sleep callbacks to shared `stm32_pinctrl_suspend` and `stm32_pinctrl_resume`.
- `stm32mp135_pinctrl_driver`: platform driver whose `.probe` is the shared `stm32_pctl_probe`.
- `stm32mp135_pinctrl_init()` plus `arch_initcall(...)`: registers the driver early during boot rather than through a module helper.

## Control Flow
At boot, `arch_initcall(stm32mp135_pinctrl_init)` calls `platform_driver_register`. When a devicetree node with `st,stm32mp135-pinctrl` appears, the platform bus invokes `stm32_pctl_probe`. The shared probe reads the OF match data, takes the static pin table and count, maps/registers GPIO/pinctrl state using common STM32 code, and later routes pin configuration, mux selection, GPIO, and suspend/resume calls through the common implementation.

There are no runtime branches in this file apart from platform registration. All pin selection behavior is declarative: the generic driver interprets the table entries and the board devicetree decides which alternate functions to activate.

## State And Persistence
The file defines immutable static data. Runtime state such as selected muxes, GPIO ownership, saved suspend state, and secure-control access decisions is owned by the shared STM32 pinctrl driver and hardware registers. Persistence across suspend is integrated by exposing the common late suspend/resume callbacks; this file only opts the MP135 instance into those callbacks.

## Dependencies And Integration Points
- Depends on Linux platform driver, OF matching, initcall, and the common STM32 pinctrl header.
- Integrates with `drivers/pinctrl/stm32/pinctrl-stm32.c` through `stm32_pctl_probe`, `stm32_pinctrl_suspend`, `stm32_pinctrl_resume`, and `struct stm32_pinctrl_match_data`.
- Integrates with devicetree bindings through `st,stm32mp135-pinctrl`; board DTS pinctrl nodes must use function numbers and pin names compatible with this table.
- The secure-control flag makes this file sensitive to the common driver's secure register access and firmware/SoC privilege model.

## Risks
- Table correctness is the main risk. A wrong alternate-function number or pin name silently routes a peripheral to the wrong pad, which usually appears as peripheral bring-up failure rather than a compile error.
- GPIO numbering gap before PI0 is intentional in the table; consumers must not assume the array index equals the hardware pin number.
- Secure-control behavior can expose integration failures only on systems where secure firmware denies or mediates pin register access.
- `arch_initcall` means the driver is built-in style here; if Kconfig or build rules ever allow modular use, registration style must be reviewed.

## Test Signals
- Build coverage for the STM32 pinctrl driver catches macro/type breakage.
- Devicetree binding validation and board DTS compilation catch compatible and pinctrl-property shape errors, but not every alternate-function mismatch.
- Runtime signals include successful probe of `stm32mp135-pinctrl`, GPIO bank registration, absence of secure-control access errors, correct pin state application for UART/I2C/SPI/ETH/LCD/SDMMC consumers, and successful suspend/resume with pins restored.
