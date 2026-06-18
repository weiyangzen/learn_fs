# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8135-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8135-pinfunc.h` defines MediaTek MT8135 pin function constants for device-tree pinmux properties. The file was read as a complete 1294-line header. It maps every SoC GPIO pad to the numeric mux values accepted by the MT8135 pinctrl driver.

The header exports 1079 `#define` macros for GPIO pins 0 through 202, with no gaps in the pin number range. Values are encoded as `(MTK_PIN_NO(pin) | function)`. GPIO mode is selector 0 where present, and alternate selectors use 1 through 7. A few pins have only GPIO definitions, while many early and midrange pins expose six to eight total mux choices.

## Important APIs, Types, and Functions

There are no functions, structs, or enums. The public interface is the macro namespace `MT8135_PIN_<n>_<pad>__FUNC_<function>`. Examples include `MT8135_PIN_0_MSDC0_DAT7__FUNC_MSDC0_DAT7`, `MT8135_PIN_0_MSDC0_DAT7__FUNC_EINT49`, `MT8135_PIN_4_MSDC0_CMD__FUNC_USB_TEST_IO_0`, `MT8135_PIN_5_MSDC0_CLK__FUNC_MSDC0_CLK`, and high-numbered MSDC3/I2C/PWM/clock macros such as `MT8135_PIN_202_MSDC3_DAT0__FUNC_SCL3`.

The file's function families include MSDC0-MSDC4, EINT lines, I2S input/output, DAC, PCM1, SPI1, NAND-style signals, USB test/drive signals, display/DPI, PWM, clock monitor/output, DSP/test bus signals, touch/keypad, I2C, UART, HDMI/CEC-adjacent signals, and multimedia debug/test functions.

## Control Flow

There is no runtime control flow inside the header. Device-tree preprocessing substitutes macro names with encoded pin/function integers. The MT8135 pinctrl driver decodes those values and uses its descriptor/register data to set the hardware mux mode for each pin in a selected state.

The compile-time flow is strict: macros must be visible before DTS pin state definitions are preprocessed, and the packed values must stay compatible with the common MediaTek decode helpers. The runtime flow is delegated entirely to the pinctrl subsystem.

## State and Persistence Behavior

The header declares no mutable state and performs no persistence. It contributes to the persistent board hardware description because generated DTBs contain the encoded pinmux values. Renaming macros breaks source-level DTS compatibility; changing numeric encodings can silently break existing DTBs rebuilt from the same source.

The include guard `__DTS_MT8135_PINFUNC_H` prevents repeated definition. The header carries GPL-2.0-only licensing and MediaTek copyright/authorship metadata from 2014.

## Dependencies and Integration Points

The direct dependency is `dt-bindings/pinctrl/mt65xx.h`, especially `MTK_PIN_NO()`, `MTK_GET_PIN_NO()`, and `MTK_GET_PIN_FUNC()`. The runtime integration is through the MT8135 pinctrl driver selected by `CONFIG_PINCTRL_MT8135`, including `drivers/pinctrl/mediatek/pinctrl-mt8135.c` and `pinctrl-mtk-mt8135.h`, where the driver maintains pin descriptors and register fields.

The header also integrates with ARM MediaTek board DTS files that describe MT8135 pin states. Its macro names include both pad identity and mux function, which lets DTS reviewers see whether a pin state selects a primary peripheral path, an interrupt line, or a test/debug function.

## Risks and Edge Cases

The largest risk is silent hardware misconfiguration from a wrong selector. MT8135 pins often have dense 0-7 mux sets; shifting a selector by one can change storage, external interrupt, audio, display, or test-bus behavior without a compiler error. Test and USB diagnostic functions are interleaved with normal peripheral functions, so board pin states should avoid accidentally selecting factory/test modes.

A small number of pins have only one macro in this header, which is expected for pads with only GPIO exposure in this binding. Reviewers should avoid "filling in" apparent gaps unless the SoC datasheet and driver register tables are updated together. The header's SoC-prefixed namespace reduces cross-header collision risk but differs from newer generic `PINMUX_GPIO...` style headers.

## Test Signals

Compile-time coverage should include MT8135 DTS/DTSI builds and DTC preprocessing with this header. Static checks can verify macro name pin numbers against `MTK_PIN_NO()` arguments, selector bounds within the low nibble decoded by `MTK_GET_PIN_FUNC()`, and stable include guards. Hardware or integration signals include successful pinctrl probe, working MSDC storage, I2C/SPI/UART, EINT wake/interrupt lines, audio I2S/PCM/DAC, display/DPI, USB-related pins, and lack of unexpected test/debug muxing in board pin states.
