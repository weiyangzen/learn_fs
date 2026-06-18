# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6797-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6797-pinfunc.h` defines MediaTek MT6797 pin function constants for device-tree pinmux properties. The file was read as a complete 1368-line header. It supplies symbolic names for the SoC's GPIO and alternate-function matrix so board DTS files do not encode raw pin/function integers by hand.

The header exports 1091 `#define` macros for GPIO pins 0 through 261, with all pin numbers present. Every macro expands to `(MTK_PIN_NO(pin) | function)`. GPIO mode is function 0 on each pin, and alternate selectors use the full range 1 through 7.

## Important APIs, Types, and Functions

There are no executable functions or declared types. The exported API is the macro namespace `MT6797_GPIO<n>__FUNC_<name>`. The early pins map CSI camera lanes, for example `MT6797_GPIO0__FUNC_CSI0A_L0P_T0A` through CSI0/CSI1/CSI2 lane macros. Later pins cover SPI, PWM, SCP/CONN/C2K debug signals, MIPI, I2S, PCM, DPI, MSDC, UART, I2C, modem, LTE JTAG, antenna, and diagnostic functions.

Several pins expose the maximum eight alternatives: for example GPIO28 has GPIO, `SPI5_CLK_A`, two MIPI functions, SCP/CONN JTAG, PWM, and C2K debug output selectors. The high-numbered pins 260 and 261 end with LTE/DFD/ANC/SCP/C2K JTAG and trace-related functions.

## Control Flow

The header has no runtime branches or call graph. Its practical flow is preprocessing and consumption by pinctrl: a DTS pin state references `MT6797_GPIO...` macros, the preprocessor emits packed integers, and the MediaTek pinctrl driver decodes those integers into pin number and mux selector when applying a pin state.

Because this is a binding header, correctness depends on the names and numeric selectors matching the separate MT6797 driver pin descriptor/register tables. The file itself does not validate combinations or enforce group membership.

## State and Persistence Behavior

No runtime state is stored. The only state-like behavior is the public ABI represented by macro names and values. Device trees built from this header carry the encoded values into the DTB, so any macro value change can alter boot-time hardware muxing for existing device trees. The include guard `__DTS_MT6797_PINFUNC_H` prevents duplicate definitions.

## Dependencies and Integration Points

The direct dependency is `dt-bindings/pinctrl/mt65xx.h` for `MTK_PIN_NO()` and decode helpers. The integration points are MT6797 board DTS/DTSI files, the MediaTek pinctrl binding, and the `CONFIG_PINCTRL_MT6797` driver path, including `drivers/pinctrl/mediatek/pinctrl-mt6797.c` and the associated pin descriptor header.

The function matrix is especially broad for camera and modem/debug use. Top-level function families visible in the macro names include CSI, C2K, DBG, CONN, MD/MD1, PWM, BPI, I2S0-I2S2, MIPI, PCM0/PCM1, DPI, SPI1/SPI2/SPI4/SPI5, SCP, LTE, UDI, TP, IRTX, MSDC0/MSDC1, UART, I2C, SIM, and antenna selectors. These names are an integration contract with both board authors and subsystem maintainers.

## Risks and Edge Cases

The major risk is a selector mismatch that compiles and boots but routes pins to the wrong peripheral. MT6797 has many debug, modem, connectivity, and camera lane alternatives; confusing similarly named signals such as SCP versus CONN JTAG or C2K debug can break low-level diagnostics or expose unintended hardware functions. Because selectors reach 7, any shared decoder must preserve at least the lower four function bits, as `MTK_GET_PIN_FUNC(x)` does.

The header uses a SoC-prefixed namespace (`MT6797_GPIO...`) rather than the newer generic `PINMUX_GPIO...` pattern. That helps avoid cross-SoC macro collisions but means board files cannot mechanically swap names between MT6797 and newer MediaTek pinfunc headers without translation. The GPL-2.0-only SPDX line also matters when comparing with dual-licensed binding headers.

## Test Signals

Compile-time tests should include all MT6797 DTS targets that include this header and should fail on missing or duplicate macro names. A simple static check can verify that each macro's numeric `MTK_PIN_NO()` argument matches the GPIO number embedded in the macro name and that every function selector stays in the expected 0-7 range. Runtime board signals include pinctrl probe without invalid function warnings, working CSI camera lanes, SPI/I2C/UART, MSDC storage, display/audio pins, modem/connectivity pins, and debug mux states on hardware that exposes them.
