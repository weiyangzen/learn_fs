# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250-lpass-lpi.c

## Purpose
Defines the SM8250 LPASS LPI GPIO pin controller variant data. Unlike the TLMM files, this targets the low-power audio subsystem pins and feeds `pinctrl-lpass-lpi` with 14 pins, SoundWire, DMIC, I2S, MI2S, WSA SoundWire, and GPIO mux options for compatible `qcom,sm8250-lpass-lpi-pinctrl`.

## Important APIs, Types, and Functions
The file defines `enum lpass_lpi_functions` values consumed by `LPI_PINGROUP()` and `LPI_FUNCTION()` macros from `pinctrl-lpass-lpi.h`. `sm8250_lpi_pins[]` lists GPIO0-GPIO13. Per-function group arrays list which GPIO names can provide each audio function. `sm8250_groups[]` maps each pin to up to four mux alternatives and a slew register selector or `LPI_NO_SLEW`. `sm8250_functions[]` exposes 21 non-GPIO functions. `sm8250_lpi_data` is the `struct lpi_pinctrl_variant_data` passed indirectly through OF match data to `lpi_pinctrl_probe()`.

## Control Flow
The `module_platform_driver()` macro registers `lpi_pinctrl_driver`. A device-tree node matching `qcom,sm8250-lpass-lpi-pinctrl` supplies `&sm8250_lpi_data` as match data. The shared LPASS LPI core performs probe, registers the pinctrl/GPIO provider, and handles mux/config operations using the static pins, groups, functions, and slew metadata. Remove delegates to `lpi_pinctrl_remove()`.

## State and Persistence Behavior
The file contains only static variant data. Runtime state, MMIO mappings, GPIO chip registration, and pinctrl state are owned by the LPASS LPI core. Slew support is per-pin: pins with numeric slew offsets can expose slew programming, while pins marked `LPI_NO_SLEW` intentionally do not. Hardware register contents, not this file, hold active mux and electrical state.

## Dependencies and Integration Points
Depends on Linux GPIO, module, platform-device APIs, and `pinctrl-lpass-lpi.h`. It integrates with audio device-tree pinctrl states for SoundWire TX/RX, WSA SoundWire, DMIC1-3, I2S1/I2S2, and QUA MI2S pins. The GPIO fallback is part of the enum but normal function registration lists only the audio functions; the common LPI driver handles GPIO mode.

## Risks
Function enum names must line up with `LPI_PINGROUP()` macro expansion. Group string names must match `PINCTRL_PIN()` names exactly (`gpio0` through `gpio13`). Some pins share functions across buses, such as GPIO5 serving both SoundWire TX/RX data alternatives, so board pinctrl states must avoid impossible simultaneous use. Incorrect slew offset values can silently program the wrong LPASS register.

## Test Signals
Compile with the LPASS LPI core, probe a `qcom,sm8250-lpass-lpi-pinctrl` node, inspect pinctrl debugfs for 14 pins and 21 functions, apply representative SoundWire, DMIC, I2S, MI2S, WSA, and GPIO states, verify pins with `LPI_NO_SLEW` do not attempt unsupported slew writes, and remove/unbind the platform device without leaking pinctrl/GPIO state.
