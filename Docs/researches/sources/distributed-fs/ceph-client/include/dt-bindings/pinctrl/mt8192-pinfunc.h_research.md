# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8192-pinfunc.h

## Purpose

This header defines the MediaTek MT8192 Device Tree pin-function constants. It covers GPIO0 through GPIO219 and provides symbolic names for alternate pinmux routes used by MT8192 boards. Each macro expands to `MTK_PIN_NO(pin) | selector`, so a DTS `pinmux` cell carries both the physical GPIO index and the alternate-function number expected by the MT8192 pinctrl driver.

The file contains 1,111 macros over 220 pins, making it the largest table in this subset. Selector 0 is present for every pin as GPIO mode, while selectors 1 through 7 describe SoC-specific functions. The table includes SPI, I2S, TDM, PCM, DMIC, MSDC, PCIE, USB, antenna/RF, modem interrupt, SCP, SSPM, ADSP, connectivity, DPI/display, camera clock, power-wrapper, RTC, watchdog, audio front-end, and debug monitor routes.

## Important APIs, Types, and Macros

The header exports constants only:

- `PINMUX_GPIO<N>__FUNC_GPIO<N>` selects GPIO mode.
- `PINMUX_GPIO<N>__FUNC_<SIGNAL>` selects a named MT8192 alternate route.
- The included `"mt65xx.h"` supplies `MTK_PIN_NO`, `MTK_GET_PIN_NO`, and `MTK_GET_PIN_FUNC`.
- Function selectors are encoded in the low nibble, with observed selectors 0-7 in this file.

The file starts with SPI6/I2S5/PWM/TDM alternatives on GPIO0-GPIO3, SPI4/I2S2/DMIC/TDM/PCM/USB routes on GPIO4-GPIO7, SRCLKEN/DVFS/keypad/clock output and PCM alternatives around GPIO8-GPIO9, MSDC2/PCIe/USB/antenna pins around GPIO10-GPIO17, and then broad connectivity, display, subsystem, storage, and audio sections later in the file. Frequent families in the complete macro list include `DBG`, `CONN`, `SCP`, `MD`, `TP`, `I2S2`, `BPI`, `PWM`, `ANT`, `I2S9`, `DPI`, `TDM`, `ADSP`, `SPI*`, `PCM1`, `MSDC0`, `MD32`, `AUD`, `SSPM`, `UDI`, `SRCLKENAI0`, and DMIC families.

## Control Flow

There is no executable control flow. The effective flow is build-time macro substitution followed by boot/runtime pinctrl application:

1. Board DTS includes the MT8192 pin-function binding.
2. Board pinctrl states name one or more `PINMUX_GPIO...` macros.
3. The C preprocessor replaces macros with integer values before DTC emits the DTB.
4. At runtime, the pinctrl subsystem asks the MT8192 pinctrl driver to apply those encoded pin/function pairs.

The numeric ordering by GPIO index helps reviewers compare neighboring pads but has no semantic sequencing at runtime.

## State and Persistence Behavior

No state is held inside this header. Its constants become persistent only when baked into a DTB or included Device Tree artifact. Kernel runtime state lives in pinctrl state objects and MT8192 hardware mux registers. Pinctrl state transitions can reprogram the same pin between default and low-power states, but this file only provides the stable identifiers used by those states.

The binding status is important: values are not just internal implementation details. Existing DTS files may rely on both names and numeric encodings. Removing macros or changing their encoded selector would be a Device Tree ABI break unless carefully coordinated with all consumers.

## Dependencies and Integration Points

The only direct include is `"mt65xx.h"`, whose encoding helpers define the contract shared by MediaTek pin-function headers. Integration points include MT8192 board DTS/DTSI files, the Device Tree compiler, the generic Linux pinctrl bindings, the MT8192 pinctrl driver, and peripheral drivers that select pinctrl states for SPI, I2C, I2S/TDM/PCM audio, MSDC, PCIe, USB, camera, display, SCP/SSPM/ADSP, modem, power wrapper, RTC, and watchdog functions.

The repository search did not show direct local DTS references to this header. That does not reduce the risk of changes, because dt-binding headers are commonly consumed by downstream board trees and external build systems.

## Risks and Test Signals

MT8192 has many repeated and overlapping bus-function names, so the largest risk is choosing a plausible but wrong instance or pin group. Examples include multiple SPI instances and suffixes, many I2S instances, duplicated `SRCLKENAI0/1`, PCIe sideband pins, USB ID/VBUS choices, and modem/antenna alternatives. Debug-monitor and JTAG/UDI routes can also conflict with production peripheral routes. Since selectors are sparse, assuming that selector numbers are interchangeable across pins is unsafe.

Validation should include preprocessing/DTC checks for all DTS users, `dtbs_check` where schemas cover the board nodes, and peripheral-specific boot tests. For pin groups, test the whole bus rather than a single macro: SPI clock/chip-select/data, I2S/TDM clock/frame/data, MSDC command/clock/data, PCIe reset/wake/clkreq, USB ID/VBUS, and SCP/SSPM/ADSP communication should all be verified together. For power-related pins such as SRCLKEN, watchdog, power-wrapper, RTC, and wake lines, include suspend/resume and wake-source testing.
