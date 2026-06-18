# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8195-pinfunc.h

## Purpose

This header is the MediaTek MT8195 Device Tree pin-function binding table. It maps GPIO0 through GPIO143 to symbolic mux constants for MT8195 board descriptions. Each macro follows the common MediaTek pattern `MTK_PIN_NO(pin) | selector`, allowing DTS pinctrl states to describe concrete pad functions without embedding raw pin/function integers.

The file contains 806 macros over 144 pins. Selector 0 is GPIO mode for every pin, and selectors 1 through 7 cover MT8195 alternate routes. Compared with the MT818x/MT8192 headers in this subset, this table has strong display, high-speed I/O, Ethernet, audio, and system-controller flavor: DP/eDP/HDMI sideband signals, DPI/DGI, GBE, I2S output/input families, TDM input, SPDIF, DMIC, MSDC, SPIM/SPIS, SNFI/SPINOR, PCIe-style reset/wake/clock-request pins, USB ID/VBUS variants, SCP, ADSP, MD32, APU/VPU debug, PWRAP, LVTS, and debug monitor functions.

## Important APIs, Types, and Macros

This file exports preprocessor constants and defines no functions or structs:

- `PINMUX_GPIO<N>__FUNC_GPIO<N>` selects GPIO mode.
- `PINMUX_GPIO<N>__FUNC_<SIGNAL>` selects an MT8195 alternate function for that pad.
- The included `"mt65xx.h"` supplies the shared MediaTek pin encoding helpers.
- The low nibble carries the mux selector; the shifted pin number comes from `MTK_PIN_NO`.

The early section maps GPIO0-GPIO7 to touch-panel AO GPIO aliases, MSDC2, TDM input, clock outputs, PCIe/USB sidebands, DMIC, DP/eDP HPD, and UART/I2C alternatives. GPIO8-GPIO17 include I2C, PWM, SPDIF, LVTS, ADSP UART, DMIC, and TDM input choices. GPIO19-GPIO32 include PCIe-style wake/reset/clkreq, SCP I2C, ADSP/MD32 JTAG, camera clocks, HDMI RX sidebands, UART2, and I2C. Mid-file display regions provide DGI/DPI and GBE mappings, while later ranges expose I2S input/output groups, MSDC0/MSDC1/MSDC2, PWRAP SPI, SPLIN/SNFI/SPINOR, SPIM/SPIS, SCP SPI/JTAG, APU/VPU debug, and `DBG_MON` routes. Frequent families are `DBG`, `SCP`, `MD32`, `DPI`, `DGI`, `GBE`, `I2SO1`, `TP`, `I2SIN`, `I2SO2`, `PWM`, `MSDC*`, `TDMIN`, `DMIC`, `AUD`, `ADSP`, `SPINOR`, `SNFI`, `PWRAP`, and PCIe/USB sideband names.

## Control Flow

There is no runtime code path in the header. The practical control/data flow is:

1. MT8195 DTS or DTSI files include this binding.
2. Pinctrl state nodes reference `PINMUX_GPIO...` constants in `pinmux` properties.
3. Preprocessing resolves those references to encoded integers.
4. The MT8195 pinctrl driver decodes the pin index and selector, then programs the mux registers when the state is applied.

Ordering by GPIO number is for hardware description and review only; it does not imply initialization order.

## State and Persistence Behavior

The header has no mutable state and no persistence logic. The encoded constants persist when compiled into a DTB. Runtime state is maintained by the Linux pinctrl framework, the MT8195 pin controller driver, and the SoC mux registers. The same pad can be reconfigured by selecting different pinctrl states during probe, runtime power management, or suspend/resume, but this file remains a pure binding map.

Because these macros are part of a Device Tree binding interface, their names and numeric values should be treated as externally visible. A local rename or selector change can break board DTS files or, worse, compile successfully while routing hardware incorrectly.

## Dependencies and Integration Points

The file depends on `"mt65xx.h"` for the encoding helpers and on the shared MediaTek convention that mux selectors occupy the low nibble. Integration points include MT8195 board Device Trees, the Device Tree compiler, generic pinctrl bindings, the MT8195 pinctrl driver register tables, and many peripheral drivers that select pin states: display, HDMI/DP/eDP, Ethernet, audio, SD/eMMC, SPI/SNFI/SPINOR, USB, PCIe sideband, thermal/LVTS, power-wrapper, SCP, ADSP, APU/VPU, and debug infrastructure.

No direct local DTS include was found in this repository snapshot for this header, so practical consumers may be downstream or outside the checked subset. The header does not configure electrical attributes; pulls, drive strength, Schmitt trigger, input enable, and voltage-domain details come from other pinctrl properties and driver data.

## Risks and Test Signals

The largest risk is board-level misrouting. MT8195 exposes many high-speed and sideband functions with similar names, such as `PERSTN`, `CLKREQN`, `WAKEN`, numbered USB ID/VBUS variants, multiple MSDC instances, multiple I2S input/output groups, and display/Ethernet data buses. Selecting one wrong pin can produce symptoms far from the DTS change: missing PCIe devices, no display hotplug, broken audio clocks, failed Ethernet link, bad boot media enumeration, or nonfunctional wake sources. Debug/JTAG/APU/VPU/SCP alternatives should be handled carefully because they can steal pins from production functions.

Test signals should include successful DTC preprocessing and `dtbs_check`, driver probe without pinctrl errors, and hardware validation for every affected group. Display and Ethernet should be tested as complete buses with sideband pins. Audio should verify master clock, bit clock, word select, and data direction. Storage/SPI/SNFI/SPINOR should verify enumeration and data transfer. USB/PCIe sidebands should be checked with attach, reset, wake, and suspend/resume scenarios.
