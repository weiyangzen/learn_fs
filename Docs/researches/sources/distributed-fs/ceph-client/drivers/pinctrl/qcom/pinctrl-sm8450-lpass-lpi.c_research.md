# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450-lpass-lpi.c

## Purpose
Defines the SM8450 LPASS LPI pin controller variant data for the shared LPASS LPI pinctrl driver. It covers 23 low-power audio GPIO pins and 38 audio-oriented functions, including SoundWire, WSA/WSA2 SoundWire, DMIC1-4, I2S1-4, QUA MI2S, SLIMbus, external MCLK alternatives, and GPIO fallback for compatible `qcom,sm8450-lpass-lpi-pinctrl`.

## Important APIs, Types, and Functions
The `enum lpass_lpi_functions` values are referenced by the LPI macros. `sm8450_lpi_pins[]` lists GPIO0-GPIO22. Per-function group arrays define the valid pin names for each function. `sm8450_groups[]` uses `LPI_PINGROUP()` to bind each pin to mux alternatives and a slew offset or `LPI_NO_SLEW`. `sm8450_functions[]` exports the non-GPIO functions. `sm8450_lpi_data` is the `struct lpi_pinctrl_variant_data` attached to the OF match entry and consumed by `lpi_pinctrl_probe()`.

## Control Flow
`module_platform_driver(lpi_pinctrl_driver)` registers the driver. On OF match with `qcom,sm8450-lpass-lpi-pinctrl`, the platform core calls `lpi_pinctrl_probe()`, which reads the match data and registers the LPASS LPI pinctrl/GPIO provider. Runtime mux and configuration operations are implemented in `pinctrl-lpass-lpi`, while this file only supplies the SM8450 variant tables. Remove delegates to `lpi_pinctrl_remove()`.

## State and Persistence Behavior
All variant information is static const data. The common LPI core owns runtime state, MMIO mappings, GPIO registration, and active pinctrl states. Pins with numeric slew offsets have per-pin slew programming support; pins with `LPI_NO_SLEW` intentionally omit it. The active mux, GPIO, and electrical state lives in LPASS LPI hardware registers rather than in this file.

## Dependencies and Integration Points
Depends on Linux GPIO, module, platform-device APIs, and `pinctrl-lpass-lpi.h`. Integrates with audio subsystem device-tree pinctrl states for SoundWire TX/RX, WSA and WSA2 amplifiers, DMICs, I2S buses, QUA MI2S, SLIMbus, and external master clock routes. Group names must match pin names exactly because the common pinctrl core resolves functions by string groups.

## Risks
The SM8450 table has many overlapping audio functions on the same pins, so board-level pinctrl states must avoid conflicting simultaneous selections. Enum ordering, group-array names, and `LPI_PINGROUP()` macro expansion are tightly coupled. Small formatting or naming mistakes in group strings can make functions invisible to consumers. Incorrect slew offsets, especially around added pins 14-22, would program the wrong LPI register or expose unsupported slew controls.

## Test Signals
Build with the LPASS LPI core, probe `qcom,sm8450-lpass-lpi-pinctrl`, inspect debugfs for 23 pins and 38 functions, apply SoundWire TX/RX, WSA/WSA2, DMIC1-4, I2S1-4, QUA MI2S, SLIMbus, external MCLK, and GPIO states, verify slew behavior only on supported pins, and unbind/rebind the platform device to exercise remove/probe cleanup.
