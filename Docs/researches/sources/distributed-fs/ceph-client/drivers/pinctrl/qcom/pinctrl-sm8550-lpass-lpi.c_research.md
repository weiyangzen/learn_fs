# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550-lpass-lpi.c

## Purpose
This file describes the SM8550 LPASS LPI GPIO pin controller, a small audio-subsystem pin controller separate from main TLMM. It binds to `qcom,sm8550-lpass-lpi-pinctrl` and supplies LPASS pin/function/group tables to the shared `pinctrl-lpass-lpi` implementation.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` defines mux IDs for DMIC, I2S, SoundWire, Slimbus, external MCLK, GPIO, and placeholder functions. `sm8550_lpi_pins` declares 23 pins, `gpio0` through `gpio22`. Per-function group arrays map each audio function to legal pin groups. `sm8550_groups` contains 23 `LPI_PINGROUP()` descriptors; each records the pin number, a SoundWire slew-rate bit offset or `LPI_NO_SLEW`, and up to four alternate functions after GPIO. `sm8550_functions` uses `LPI_FUNCTION()` to expose 39 functions to pinctrl. `sm8550_lpi_data` packages those tables as `struct lpi_pinctrl_variant_data`.

## Control Flow
The module uses `module_platform_driver()`. When OF matching finds `qcom,sm8550-lpass-lpi-pinctrl`, the shared `lpi_pinctrl_probe()` receives `sm8550_lpi_data` through `.data`. The shared driver maps TLMM and, for this variant, a separate slew-rate resource because no `LPI_FLAG_SLEW_RATE_SAME_REG` flag is set. It then registers pinctrl groups, pinmux functions, pinconf handlers, and a gpiochip. Runtime mux changes select the function's index within each group's `funcs` list and write the LPASS GPIO configuration register.

## State And Persistence
This source has only static descriptor state. Runtime mutable state is in `struct lpi_pinctrl` in the shared implementation, including MMIO bases, optional clocks, a mutex, the gpiochip, and an `ever_gpio` bitmap used to avoid output glitches when first muxing a line back to GPIO. Register state is hardware-resident and persists until reset or reconfiguration.

## Dependencies And Integration Points
It depends on `pinctrl-lpass-lpi.h`, the common LPASS LPI pinctrl implementation, platform/OF matching, gpiolib, and optional LPASS clocks/resources consumed by the common probe path. It integrates with audio drivers through pinctrl states for DMIC clocks/data, I2S0-I2S4, SoundWire TX/RX, WSA and WSA2 SoundWire, Slimbus, and five external MCLK1 routes.

## Risks
The SM8550 table uses a separate slew register layout with per-pin offsets such as 0, 2, 4, 8, 10, 12, 16, 18, 20, and 22 for selected SoundWire-capable pins. Incorrect offsets affect slew programming rather than muxing, so failures may appear as signal-integrity issues. Function lists are positional; a wrong order changes mux values written by the shared driver. The file has no wake IRQ map and no main TLMM GPIO semantics, so consumers must use the LPASS compatible and pin names.

## Test Signals
Expected signals include successful probe with 23 GPIOs, pinctrl group creation for all 23 pins, valid muxing of I2S, DMIC, Slimbus, SoundWire, and ext MCLK routes, GPIO direction/value behavior through the common LPASS gpiochip, successful use of the second MMIO resource for slew programming, and debugfs output showing the selected function index, drive strength, and pull state for representative pins.
