# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280-lpass-lpi.c

## Purpose
This file describes the SC7280/SM8350 LPASS LPI audio pin controller, separate from the main TLMM controller. It exposes 15 low-power audio GPIOs and their audio-specific mux functions to the shared `pinctrl-lpass-lpi` core. The functions cover SoundWire TX/RX/WSA signals, DMIC clocks/data, I2S1/I2S2, and quad MI2S signals.

## Important APIs, Types, And Functions
The file uses `enum lpass_lpi_functions`, `struct pinctrl_pin_desc`, `struct lpi_pingroup`, `struct lpi_function`, and `struct lpi_pinctrl_variant_data` from `pinctrl-lpass-lpi.h`. `LPI_PINGROUP()` entries define each GPIO's slew register index or `LPI_NO_SLEW` plus up to four mux functions. `LPI_FUNCTION()` binds each function name to the corresponding group array. `sc7280_lpi_data` is the variant descriptor passed through OF match data to the generic `lpi_pinctrl_probe()`.

## Control Flow
The module uses `module_platform_driver(lpi_pinctrl_driver)`. OF matching accepts both `qcom,sc7280-lpass-lpi-pinctrl` and `qcom,sm8350-lpass-lpi-pinctrl`, each with `.data = &sc7280_lpi_data`. Probe and remove are not local functions; they are `lpi_pinctrl_probe` and `lpi_pinctrl_remove` from the LPI common driver. Once bound, the LPI core exposes pinctrl and GPIO behavior based on the variant data.

## State And Persistence
The file itself has only immutable static tables. Runtime mux, GPIO, and low-power audio pad state is held in LPASS LPI hardware and managed by the common LPI pinctrl core. The slew entries distinguish pads with programmable slew from pads marked `LPI_NO_SLEW`.

## Dependencies And Integration Points
The driver depends on platform driver registration, gpiolib headers, module infrastructure, and `pinctrl-lpass-lpi.h`. It integrates with audio DT nodes that select SoundWire, DMIC, and I2S pinctrl states on SC7280 and SM8350-class LPASS blocks. It is independent from `pinctrl-sc7280.c`, which describes the main TLMM controller.

## Risks And Test Signals
Risk is in function-to-pad mapping and the shared compatible data. A wrong group list can swap audio data/clock/word-select routing and produce silent audio failures. Reusing the SC7280 data for SM8350 should be validated against both SoCs. Pads with `LPI_NO_SLEW` should not expose unsupported slew programming. Test signals include module autoload for both compatibles, pinctrl state selection for SoundWire TX/RX/WSA, DMIC1-3, I2S1/I2S2, quad MI2S, GPIO fallback operation on the 15 pins, and audio capture/playback across suspend or low-power transitions.
