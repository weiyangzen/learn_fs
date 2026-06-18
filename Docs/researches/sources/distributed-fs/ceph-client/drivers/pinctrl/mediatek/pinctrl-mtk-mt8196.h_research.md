# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8196.h

## Purpose
This header provides the MT8196 pin and EINT description data for the MediaTek Paris pinctrl framework. It defines `mtk_pins_mt8196[]` with 293 contiguous pin descriptors, GPIO0 through virtual EINT-style pins `veint292`, and a matching `eint_pins_mt8196[]` table with 293 `MTK_EINT_PIN()` entries. The data lets the shared Paris driver expose MT8196 pins to the Linux pinctrl, pinmux, pinconf, GPIO, and EINT subsystems.

## Important APIs, Types, And Data
The file is data-only. It depends on `pinctrl-paris.h`, `struct mtk_pin_desc`, and `struct mtk_eint_pin`. `EINT_INVALID_BASE` is defined as `0xff` and used in the EINT table for pins without a valid EINT backing instance. The pin table uses `MTK_PIN`, `MTK_EINT_FUNCTION`, `MTK_FUNCTION`, and `DRV_GRP4`; unlike MT8195 there are no fixed drive groups in the scanned table. Function coverage includes touch, display PWM/DSI/DP, SPI/I2C/UART, audio, MD/MD32/SCP/SSPM/ADSP/SPU, GPS, BPI modem signals, CONN/UDI/debug monitor functions, PCIe sideband, and dual GBE groups. Pins 271 through 292 are named `veint*` and expose only function zero with a `NULL` function name.

## Control Flow And Integration
The runtime flow is mediated by the Paris common driver. During probe, the MT8196 companion driver supplies this table through `device_get_match_data()` as part of `struct mtk_pin_soc`. Paris builds one group per pin, registers pinctrl, enables it, builds EINT with `mtk_build_eint()`, and registers the gpiochip. Devicetree `pinmux` cells are validated against each pin's `funcs` list before `PINCTRL_PIN_REG_MODE` writes are issued. GPIO-to-IRQ and debounce requests use `desc->eint.eint_n`, while `eint_pins_mt8196[]` maps logical EINT pins to EINT instances, indexes, and debounce support.

## State And Persistence
The header contains immutable compile-time SoC data. Runtime state is held in the Paris `struct mtk_pinctrl`, `struct mtk_eint`, gpiochip state, and hardware register fields. EINT mapping is not persisted outside the kernel image; selected mux and GPIO states persist as hardware register state until reset, suspend handling, or explicit reconfiguration.

## Dependencies
The pin table and EINT table must remain index-aligned with the SoC's `npins`. Paris code indexes `hw->soc->pins[pin]` directly, so gaps or duplicate numbers would be unsafe. The companion SoC driver must provide register calculators for mode, direction, input/output, bias, drive, and EINT registers that cover all real and virtual pins. Devicetree bindings must use mux values no larger than the Paris `func0` through `func15` function namespace.

## Risks
The highest risk is mismatched EINT metadata: `EINT_INVALID_BASE` correctly marks unsupported lines, but a wrong instance/index/debounce bit can break IRQ delivery or wake behavior. Virtual `veint` entries need careful treatment because they have `NULL` function names and are probably not normal GPIO pads. Other risks are incorrect mux values for complex shared subsystems like modem/BPI, PCIe, DP, and GBE, and the table size makes off-by-one review errors likely.

## Test Signals
Test signals include successful MT8196 pinctrl probe, complete `debugfs` pin listing including virtual pins, DT validation for typical board pin states, GPIO loopback tests on normal pads, IRQ mapping and debounce tests across all EINT instances, and smoke tests for SPI, I2C, UART, MSDC, PCIe sideband, DP, audio, and GBE. A focused static check should verify 293 `MTK_PIN()` entries and 293 `MTK_EINT_PIN()` entries remain aligned.
