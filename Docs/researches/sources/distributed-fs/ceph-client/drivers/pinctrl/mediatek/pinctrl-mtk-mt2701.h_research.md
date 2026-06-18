# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2701.h

## Purpose
`pinctrl-mtk-mt2701.h` is a legacy SoC pin descriptor header for MT2701. It declares `mtk_pins_mt2701[]`, a 280-entry array mapping each physical pin number to a name, EINT mux/number pair, and alternate function list. The legacy common driver consumes this table through an MT2701 devdata file to expose pin groups and validate device-tree pinmux requests.

## Important APIs, Types, And Data
- The file includes `pinctrl-mtk-common.h` and uses `MTK_PIN()`, `PINCTRL_PIN()`, `MTK_EINT_FUNCTION()`, and `MTK_FUNCTION()` for all entries.
- `mtk_pins_mt2701[]` covers pins 0 through 279.
- Function 0 is generally GPIO/GPI mode. Alternate functions cover PWRAP, SPI, UART, I2S/PCM, JTAG, NAND, IR, I2C, display/HDMI/MHL, MSDC, PWM, Ethernet/ESW, PCIe reset/wake/clock request aliases, debug monitor functions, antenna selection, and RAM buffer/internal interface pins.
- EINT mappings are mixed: many user-visible GPIO pins map to EINT numbers, while internal RAM buffer, AP/DSP, DVP, host/slave, Ethernet, and other pins use `NO_EINT_SUPPORT`.
- Comments document MT7623-specific alternate function aliases for some PCIe reset pins.

## Control Flow
This header does not execute code. During probe, the legacy common driver copies each `pin.pin` descriptor into the Linux pinctrl descriptor and builds one group per pin with the pin name as the group name. During DTS parsing, `MTK_GET_PIN_NO()` and `MTK_GET_PIN_FUNC()` extract a requested pin/function pair; the common driver validates that the function number appears in the selected pin's `functions` list before programming the pinmux register. EINT translation walks this pin array to find a matching EINT number.

## State And Persistence
The array is static const metadata. It persists in kernel memory as SoC description data. Runtime mux, GPIO, and EINT state is maintained by the common driver and hardware registers, not by this header.

## Dependencies And Integration Points
The header depends on the legacy common data model. It must be paired with an MT2701 C driver that provides register offsets, drive tables, pull tables, and EINT hardware parameters. DTS pinmux definitions rely on the exact pin numbers and function mux values listed here.

## Risks
The table is large and manually maintained; off-by-one pin numbers or wrong mux values cause DTS states to validate but select the wrong hardware function. `NO_EINT_SUPPORT` appears frequently; consumers must not request IRQs for those pins. Some pins use `GPIxx` rather than `GPIOxx` for function 0, reflecting input-only or special behavior. MT7623 PCIe aliases use duplicate function names at different mux values. EINT fields are `unsigned char` in the legacy model.

## Test Signals
Compile the MT2701 pinctrl driver that includes this header and verify `ARRAY_SIZE(mtk_pins_mt2701)` matches devdata `npins`. Boot with MT2701 or related DTS pinctrl states for PWRAP, UART, SPI, I2C, I2S/PCM, MSDC, HDMI, PWM, Ethernet, and GPIO. Test GPIO request and EINT mapping for supported pins, and confirm unsupported pins reject GPIO-to-IRQ.
