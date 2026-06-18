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
