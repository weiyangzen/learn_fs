# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6795-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6795-pinfunc.h` defines the device-tree pinmux constants for the MediaTek MT6795 pin controller. The file was read as a complete 908-line header. It is a data/ABI header rather than executable code: DTS and DTSI files include it so `pinmux = <...>` properties can name pins and alternate functions symbolically instead of hard-coding packed integers.

The header exports 698 `#define` macros covering GPIO pins 0 through 196 with no gaps in the pin number range. Each macro expands to `(MTK_PIN_NO(pin) | mux_function)`, where `MTK_PIN_NO()` is supplied by `dt-bindings/pinctrl/mt65xx.h` and shifts the pin number into the upper bits. GPIO mode is consistently mux function 0; alternate function selectors in this file use values 1 through 6.

## Important APIs, Types, and Functions

There are no C functions, structs, or enums. The public API is the macro namespace `PINMUX_GPIO<n>__FUNC_<name>`. Important examples include `PINMUX_GPIO0__FUNC_GPIO0`, `PINMUX_GPIO0__FUNC_IRDA_PDN`, `PINMUX_GPIO1__FUNC_SDA4`, `PINMUX_GPIO2__FUNC_SCL4`, `PINMUX_GPIO5__FUNC_PCM1_CLK`, `PINMUX_GPIO9__FUNC_USB_DRVVBUS`, and the final audio-oriented pins `PINMUX_GPIO195__FUNC_I2S0_DO` and `PINMUX_GPIO196__FUNC_I2S0_DI`.

The macro values are part of the kernel device-tree binding contract. MediaTek pinctrl code decodes the packed value through the common helpers `MTK_GET_PIN_NO(x)` and `MTK_GET_PIN_FUNC(x)`, so the exact numeric pin and mux selector must match the SoC pin table and register layout.

## Control Flow

The header has no runtime control flow. At preprocessing time, DTS sources include the header and substitute the symbolic names into numeric pinmux cells. At boot, the device-tree blob already contains those encoded integers; the pinctrl driver reads a pin number and mux selector from each cell and programs the corresponding SoC mode register.

The implicit flow is: board DTS selects one or more `PINMUX_GPIO...` macros, the preprocessor encodes them using `MTK_PIN_NO(pin) | function`, the flattened tree stores the values, and the MediaTek pinctrl driver applies those values while probing pin groups or configuring a device state.

## State and Persistence Behavior

The file holds no mutable state and persists nothing at runtime. Its definitions affect persistent ABI in a different sense: once DTS files and external device trees use these macro names and numeric encodings, changing a pin number or function selector would alter hardware configuration for existing boards. The include guard `__DTS_MT6795_PINFUNC_H` prevents duplicate preprocessing definitions.

## Dependencies and Integration Points

The only direct include is `dt-bindings/pinctrl/mt65xx.h`, which defines `MTK_PIN_NO(x) ((x) << 8)`, `MTK_GET_PIN_NO(x)`, and `MTK_GET_PIN_FUNC(x)`. This header integrates with MT6795 device-tree sources, the generic MediaTek pinctrl binding parser, and the MT6795 pin controller driver selected by `CONFIG_PINCTRL_MT6795`.

The function names expose the major SoC mux domains visible in this header: IRDA, I2S0-I2S3, PCM1, SPI, TDD and LTE modem/JTAG signals, AP/MD debug JTAG, USB VBUS drive, SIM1/SIM2, MSDC0-MSDC3, DPI/display, PWRAP, UART, I2C `SDA`/`SCL`, and baseband `BPI` signals. Those names must stay aligned with the SoC datasheet and with any driver pin descriptors that validate pin/function combinations.

## Risks and Edge Cases

The main risk is ABI drift. A wrong mux selector can still compile cleanly but configure a different electrical function at runtime, causing silent board failures such as dead UART, broken storage, wrong I2C bus ownership, or exposed debug/JTAG pins. Because function selectors are sparse for many pins, adding a missing alternate function requires preserving existing selector numbers rather than renumbering a pin block.

The namespace differs from some older MediaTek headers by using `PINMUX_GPIO...` rather than a SoC-prefixed macro name. That is valid for this generation but increases collision risk if multiple pinfunc headers are included in a single preprocessed DTS translation unit. Another review point is license compatibility: this file uses dual `(GPL-2.0-only OR BSD-2-Clause)` SPDX text, unlike several neighboring MediaTek pinfunc headers that are GPL-only.

## Test Signals

Useful validation is mostly compile-time and board-level. `dtbs_check`/DTC preprocessing should catch missing macro names and include guard problems. Grep or script checks can confirm every macro uses `MTK_PIN_NO(n)` matching the GPIO number in its name, that GPIO mode uses selector 0, and that selectors remain within the 4-bit function field decoded by `MTK_GET_PIN_FUNC(x)`. Runtime signals are successful probe and operation of MT6795 boards using UART, storage, I2C, display/audio, modem, and USB pin states without pinctrl warnings.
