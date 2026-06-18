# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8365.h

## Purpose
This header is the MT8365 pin descriptor table for the older MediaTek pinctrl common framework, not the Paris/common-v2 schema. It includes `pinctrl-mtk-common.h` and defines `static const struct mtk_desc_pin mtk_pins_mt8365[]`, a 156-pin contiguous table from GPIO0 to BIAS1_MSDC1. Each entry maps a `PINCTRL_PIN()` descriptor to an EINT function and a list of legal mux functions for MT8365 pads.

## Important APIs, Types, And Data
The central type is `struct mtk_desc_pin`, which wraps a `struct pinctrl_pin_desc`, `struct mtk_desc_eint`, and a null-terminated `struct mtk_desc_function` list. The file uses the legacy `MTK_PIN(_pin, _pad, _chip, _eint, ...)` macro shape. The table covers display DPI pins, PWM, I2S/TDM/audio, external modem/UART-like signals, CONN MCU and wireless pins, debug monitor outputs, MSDC0/MSDC1/MSDC2, SPI, I2C, APU/ADSP/UDI/DFD, antenna and connectivity control, DMIC, TDM TX, and reset/bias pins. The final region includes `TESTMODE`, `SYSRSTB`, and BIAS_* pins that generally expose only GPIO/function zero.

## Control Flow And Integration
This file has no executable code. Legacy MediaTek SoC driver code includes it in platform driver data, registers the pin descriptions with the old common pinctrl implementation, and uses the per-pin function list to validate mux selections from board pinctrl states. GPIO, pinconf, and EINT operations are implemented by the older common driver and hardware-specific register tables in the companion C file.

## State And Persistence
All contents are immutable compile-time data. Runtime state is handled by the legacy MediaTek common driver and SoC registers. Pin mode, GPIO direction/value, bias, input-enable, Schmitt, and drive strength settings persist only in hardware register state and are re-established by driver probe or board pinctrl state application.

## Dependencies
The table depends on the legacy `pinctrl-mtk-common.h` macro and type layout. It must align with companion MT8365 devdata: total pin count, EINT count, register offsets, drive tables, IES/SMT tables, special pull-up/down tables, and devicetree binding values. Function names and mux numbers must match datasheet and binding documentation.

## Risks
Legacy schema differences are a risk: code expecting `struct mtk_pin_desc` from Paris cannot consume this table. Mux-value mistakes can be hard to detect because many pins carry debug or alternate subsystem signals in high mux values. The final bias/reset pins have limited functions and can be mistaken for normal GPIOs. EINT numbers are simple and mostly one-to-one, so any exception in silicon wiring needs explicit review in companion data.

## Test Signals
Validation should include compiling the MT8365 pinctrl driver, DT pinctrl state checks for major peripherals, GPIO request/direction/value tests, EINT tests on several GPIO and special pins, and peripheral bring-up for DPI, I2S/TDM, MSDC, SPI/I2C/UART, connectivity, and PWM. Static checks should preserve 156 `MTK_PIN()` entries and contiguous pin numbers 0 through 155.
