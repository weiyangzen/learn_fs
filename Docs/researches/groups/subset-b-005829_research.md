# Research: subset-b-005829

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8183-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8183-pinfunc.h

## Purpose

This header is the MediaTek MT8183 Device Tree pin-function binding table. It gives DTS authors symbolic constants for each legal alternate function on GPIO0 through GPIO179. Each constant expands to the pin number encoded by `MTK_PIN_NO(pin)` ORed with a hardware function selector from 0 through 7. The values are consumed through `pinmux = <...>;` style pinctrl properties, letting board files name signals such as `I2S3_BCK`, `SPI2_CLK`, `MSDC0_DAT0`, `USB_DRVVBUS`, `UFS_*`, `ANT_SEL*`, modem interrupts, JTAG/debug routes, and GPIO mode without open-coding numeric mux values.

The file contains 927 `PINMUX_GPIO...__FUNC_...` macros over 180 pins. Selector 0 is consistently the plain GPIO function for each pin. Later selectors expose peripheral-specific alternate functions and are intentionally sparse where a pin lacks a hardware route for a given selector.

## Important APIs, Types, and Macros

There are no C functions or data structures. The exported API is the macro namespace:

- `PINMUX_GPIO<N>__FUNC_GPIO<N>` maps pin `<N>` to GPIO mode using selector 0.
- `PINMUX_GPIO<N>__FUNC_<SIGNAL>` maps pin `<N>` to one alternate signal using selectors 1 through 7.
- `MTK_PIN_NO(x)` is imported from `dt-bindings/pinctrl/mt65xx.h`; that common binding shifts the pin number into the high byte.
- `MTK_GET_PIN_NO(x)` and `MTK_GET_PIN_FUNC(x)` in the common header decode the same values, with the low nibble reserved for the function selector.

Representative MT8183 groups include early audio/SPI/PCM mappings on GPIO0-GPIO7, display interface and SPI blocks around GPIO13-GPIO36, MSDC/eMMC and UFS-related pins in the mid-range, and connectivity/modem/debug/JTAG alternatives spread across the table. The most frequent signal families in the full file are `DBG`, `ANT`, `CONN`, `SCP`, `TP`, `MD`, `BPI`, `SSPM`, `PWM`, DBPI/display, I2S, TDM, MSDC, USB, and UFS.

## Control Flow

This file has no runtime control flow. During kernel build or Device Tree compilation, the C preprocessor substitutes symbolic pinmux macros with numeric constants. At boot, the MediaTek pinctrl driver receives those numeric constants from the flattened Device Tree and programs SoC mux registers according to the decoded pin number and function selector. The important data flow is therefore:

1. DTS includes the MT8183 pin-function header.
2. Board pinctrl nodes reference selected `PINMUX_GPIO...` macros.
3. The preprocessor emits encoded constants.
4. The MTK pinctrl driver decodes pin/function values and writes pinmux hardware state.

## State and Persistence Behavior

The header itself stores no state and performs no persistence. Its constants describe hardware state that becomes persistent only as compiled Device Tree data in firmware/kernel artifacts. Runtime persistence depends on the pinctrl core and the MT8183 pinctrl driver: pin states are applied at probe time, device activation, suspend/resume, or explicit state transitions such as `default`, `sleep`, and peripheral-specific pinctrl states. Because the constants are ABI-facing Device Tree bindings, renaming or changing an existing macro value can break old DTS sources even though no C state is held here.

## Dependencies and Integration Points

The header uses include guards and includes `<dt-bindings/pinctrl/mt65xx.h>`. It depends on the shared MediaTek encoding contract in that file, especially the low-nibble function selector layout. Integration points are Device Tree source files for MT8183 boards, the Device Tree compiler/preprocessor path, Linux pinctrl generic parsing, and the MT8183-specific pin controller implementation that knows the register layout for each pin and selector.

Although this repository snapshot did not show direct in-tree DTS includes for this exact header, it remains a public binding surface for MT8183 board descriptions. Consumers must match this header with MT8183 pinctrl driver tables and SoC documentation; the header alone does not validate whether electrical settings, pulls, drive strength, or voltage domains are appropriate.

## Risks and Test Signals

The main risk is ABI drift. Any changed selector value can route a live board signal to the wrong peripheral. Copy/paste errors are also high impact because adjacent pins often expose similarly named but position-sensitive signals such as clock/data/chip-select lines. MT8183 also has many debug, modem, RF antenna, UFS, USB, and JTAG alternatives; accidentally selecting one can interfere with boot media, radio, low-power handshakes, or debug access.

Useful validation signals include `dtbs_check`/DTC preprocessing success, pinctrl driver probe logs, boot-time absence of mux errors, and peripheral smoke tests for each referenced bus. For board changes, inspect the compiled DTB to confirm each `pinmux` cell decodes to the expected pin and selector, then test the affected hardware path: I2C/SPI transfer, I2S audio clocking, MSDC enumeration, USB ID/VBUS behavior, UFS link bring-up, modem interrupt delivery, or JTAG/debug availability depending on the selected macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8183-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8186-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8186-pinfunc.h

## Purpose

This header is the MediaTek MT8186 pin-function binding table for Device Tree pinctrl nodes. It names the legal mux functions for GPIO0 through GPIO184 and encodes each one as `MTK_PIN_NO(pin) | selector`. MT8186 exposes a broad set of application-processor, subsystem, display, audio, storage, connectivity, and debug routes, and this file turns those routes into stable DTS symbols.

The file contains 976 pinmux macros over 185 pins. Selector 0 is the GPIO function for every pin. Selectors 1 through 7 cover alternate hardware routes such as I2S, TDM, PCM, SPI instances, SCP and SSPM interfaces, ADSP and SPM JTAG, DPI display signals, camera clock/reference pins, MSDC, SPINOR, UDI/DFD debug, GPS and antenna control, connectivity control pins, and SPMI.

## Important APIs, Types, and Macros

The API is a generated-style macro set rather than executable C:

- `PINMUX_GPIO<N>__FUNC_GPIO<N>` is the selector-0 GPIO value.
- `PINMUX_GPIO<N>__FUNC_<SIGNAL>` is a board-usable mux token for a concrete MT8186 pad function.
- The header includes `"mt65xx.h"`, which supplies the MediaTek pin encoding helpers.
- `MTK_PIN_NO(x)` shifts the pin number left by eight bits; `MTK_GET_PIN_FUNC(x)` later extracts the low nibble.

The full table is dense but not uniform. Early pins are audio and SPI heavy, for example I2S0/I2S2 and SPI0/SCP_SPI0 around GPIO0-GPIO3, I2S3/I2S1 and SPI1 around GPIO6-GPIO9, and SPM/SCP/ADSP/CONN JTAG selections around GPIO10-GPIO14. Mid-file regions include TDM receive, PCM, DPI, I2C-style `SCL`/`SDA`, PWM, camera clocks and resets, keypad rows/columns, GPS, antenna selects, and multiple SCP SPI/I2C/UART/JTAG choices. Late pins include audio data lanes, connectivity top/BT/Wi-Fi controls, UDI/DFD debug, and SPMI pins at GPIO183-GPIO184. The most common families are `SCP`, `DBG`, `TP`, `CONN`, `I2S2`, `DPI`, `I2S1`, `ANT`, `PGD`, `ADSP`, `UDI`, `DFD`, `I2S3`, `I2S0`, `SSPM`, and `AUD`.

## Control Flow

There is no runtime branch or call graph in this header. The control path is preprocessing and pinctrl data consumption:

1. MT8186 board DTS files include this binding.
2. Pinctrl states use the macro constants in `pinmux` arrays.
3. Device Tree preprocessing resolves macros to integer cells.
4. The MediaTek pinctrl driver decodes the pin number and selector and writes the matching mux registers when the state is selected.

Any apparent ordering in the file is a hardware-description ordering by GPIO number, not an execution order.

## State and Persistence Behavior

The header has no mutable state, no static storage, and no persistence logic. The persistent artifact is the compiled Device Tree containing the encoded constants. Runtime state is maintained by the kernel pinctrl subsystem and MT8186 pinctrl driver, which may switch between default, sleep, idle, or peripheral-specific pin states. Because DTS files can be built outside this repository, the macro names and numeric values form a binding ABI; stability matters even when no local C callers exist.

## Dependencies and Integration Points

This file depends on the common `mt65xx.h` binding and on the convention that MediaTek pin mux selectors fit in the low nibble. It integrates with the Linux Device Tree build, MT8186 board DTS/DTSI files, the generic pinctrl bindings, and MT8186 driver data that maps each pin/selector pair to actual register fields. It also indirectly integrates with peripheral drivers that request named pinctrl states, such as audio, SPI, I2C, display, storage, camera, connectivity, and low-power subsystem drivers.

This snapshot did not expose direct DTS references to the MT8186 header, but the file is still an exported hardware binding. Consumers need the matching SoC pinctrl driver and electrical configuration data; the pin-function macro only chooses the mux path and does not configure pull-up, pull-down, drive strength, input enable, or power domain requirements.

## Risks and Test Signals

The risk profile is mostly hardware routing correctness. A wrong selector can silently move a bus line to a different function, especially where related signals appear on repeated pins or alternate instance suffixes such as `_A`, `_B`, SCP variants, ADSP variants, or debug-monitor variants. Debug and DFD/UDI/JTAG functions can collide with production peripherals. SPM, SCP, SSPM, SPMI, and connectivity pins can affect suspend/resume and power-management behavior. Display DPI and audio/TDM/I2S groups must be complete and ordered consistently to avoid partial bus bring-up failures.

Test signals include DTC preprocessing with the intended macro names, `dtbs_check` coverage for pinctrl nodes, successful probe of the MT8186 pinctrl driver, and targeted hardware tests for each group referenced by board DTS. For display, verify DPI output and panel timing. For audio, verify clock, bit-clock, frame-sync, and data pins together. For storage and SPI/SPINOR, verify enumeration and transfer integrity. For low-power and subsystem pins, verify suspend/resume, wake, and SCP/SPM communication paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8186-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8192-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8192-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8195-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8195-pinfunc.h -->
