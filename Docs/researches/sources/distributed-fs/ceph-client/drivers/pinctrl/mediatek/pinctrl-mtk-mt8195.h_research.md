# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8195.h

## Purpose
This header is the MT8195 SoC pin description table for the MediaTek Paris pinctrl framework. It includes `pinctrl-paris.h` and defines `static const struct mtk_pin_desc mtk_pins_mt8195[]`, a contiguous 165-pin catalogue from GPIO0 through GPIO164. Each entry binds a Linux pin number/name to its EINT line, drive group, and legal mux values. The table is consumed by an MT8195 platform driver through an `mtk_pin_soc` descriptor in companion code, then the shared Paris driver builds one pinctrl group per pin and validates devicetree `pinmux` function numbers against this per-pin function list.

## Important APIs, Types, And Data
The file is data-only and exports no functions. It relies on Paris macros: `MTK_PIN()`, `MTK_EINT_FUNCTION()`, `MTK_FUNCTION()`, plus drive groups `DRV_GRP4` and `DRV_FIXED`. The table covers high-density multimedia and platform I/O functions: MSDC0/MSDC2, SPI, I2C, UART, PWM, TDM/I2S, DMIC, DPI/DGI display pins, GBE pins, SCP/SSPM/MD32 sideband GPIOs, debug monitor functions, PCIe/USB sideband signals, and clock outputs. Most pins use `DRV_GRP4`; the final fixed/special pins use `DRV_FIXED` and often expose only `MTK_FUNCTION(0, NULL)`.

## Control Flow And Integration
There is no executable control flow in this header. At runtime a board devicetree supplies encoded `pinmux` cells, `mtk_pctrl_dt_subnode_to_map()` in `pinctrl-paris.c` decodes pin/function numbers, and `mtk_pctrl_is_function_valid()` walks the `funcs` array in this table before allowing a mux map. `mtk_pmx_set_mux()` later writes `PINCTRL_PIN_REG_MODE` using the selected `muxval`. GPIO request paths switch the same pin to `soc->gpio_m`, and GPIO/IRQ operations use the `eint` descriptors from this file.

## State And Persistence
The header has no mutable state. Its data is compiled into kernel rodata. Runtime state lives in the shared Paris `struct mtk_pinctrl`, gpiochip registration, EINT controller state, and hardware registers. Pin mux, direction, bias, input enable, and drive strength persist only as SoC register values until reset or suspend/resume restoration by platform code.

## Dependencies
The table depends on the Paris/common-v2 schema matching the SoC driver's register calculators. The number of table entries must match `npins`, and pin numbers are assumed to be valid indexes by Paris code paths such as `hw->soc->pins[pin]`. EINT values must match MT8195 interrupt-controller wiring and devicetree binding expectations.

## Risks
The main risk is silent board malfunction from table inaccuracies: an incorrect mux value can route a peripheral to the wrong pad; an incorrect EINT number can break interrupts or wake sources; an incorrect drive group can expose invalid drive-strength behavior. Pins near the end of the table with `NULL` function names are intentionally limited, but they are risky because debug output and function validation must tolerate unnamed function zero. Because Paris uses one pin per group, any non-contiguous or duplicate pin number would corrupt group creation; this file appears contiguous from 0 to 164.

## Test Signals
Useful tests are DT binding compilation for MT8195 pinmux cells, boot probing of the companion MT8195 pinctrl driver, `debugfs` pinctrl dumps via `mtk_pctrl_show_one_pin()`, GPIO request/direction tests on representative pins, peripheral smoke tests for MSDC/I2C/SPI/UART/audio/display/GBE functions, and IRQ/debounce tests for EINT-backed pins. Build coverage should include `COMPILE_TEST` or MT8195 defconfig coverage so macro/schema drift is caught.
