# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650-lpass-lpi.c

## Purpose
This file describes the SM8650 LPASS LPI GPIO pin controller for low-power audio pins. It is a variant table for the shared LPASS LPI pinctrl core and binds to `qcom,sm8650-lpass-lpi-pinctrl`.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` extends the SM8550 LPASS set with `qca_swr_clk` and `qca_swr_data`. `sm8650_lpi_pins` defines 23 pins, and function group arrays define legal placements for DMIC, I2S, SoundWire TX/RX, WSA SoundWire, QCA SoundWire, Slimbus, ext MCLK1, and GPIO. `sm8650_groups` has 23 `LPI_PINGROUP()` entries; most SoundWire-capable pins use slew offset 11 because this variant stores slew control in the same per-pin configuration register. `sm8650_functions` exposes 41 functions. `sm8650_lpi_data` sets `.flags = LPI_FLAG_SLEW_RATE_SAME_REG`.

## Control Flow
The platform driver is registered with `module_platform_driver()`. OF match data points the common `lpi_pinctrl_probe()` to `sm8650_lpi_data`. Because `LPI_FLAG_SLEW_RATE_SAME_REG` is set, the shared probe does not require a second slew MMIO resource; slew programming writes the per-pin TLMM config register instead. Probe then registers generic pinctrl groups, pinmux, pinconf, and a gpiochip for 23 LPASS pins.

## State And Persistence
This file contains only static SoC data. Runtime state is maintained by the common LPASS driver: MMIO base, clocks named `core` and `audio` when available, mutex-protected register updates, pinctrl descriptor, gpiochip, and the first-GPIO-use glitch-avoidance bitmap. Hardware register contents persist until reset or reconfiguration.

## Dependencies And Integration Points
It integrates with `pinctrl-lpass-lpi.c` through `struct lpi_pinctrl_variant_data`. Audio consumers use these groups for I2S0-I2S4, DMIC1-DMIC4, SoundWire TX/RX, WSA/WSA2 SoundWire, QCA SoundWire on GPIO19/GPIO20, Slimbus on GPIO19/GPIO20, and external MCLK1 routes on GPIO5, GPIO9, GPIO13, GPIO14, and GPIO22. It uses platform/OF matching and gpiolib through the shared driver.

## Risks
The most important SM8650-specific risk is the same-register slew flag. If a board binding or register layout expects a separate slew resource, slew writes would target the wrong place; conversely, without the flag probe would fail or program the wrong register bank. Function ordering remains mux-value-sensitive. GPIO19 and GPIO20 carry both Slimbus and QCA SoundWire functions, so consumer pin states must choose the intended bus explicitly.

## Test Signals
Useful signals include successful probe with only the TLMM MMIO resource, registration of 23 GPIOs, correct muxing of QCA SoundWire on GPIO19/GPIO20, continued Slimbus support on the same pins, slew-rate pinconf writes affecting the per-pin config register, DMIC/I2S/WSA SoundWire route tests, and GPIO get/set/direction checks via the shared LPASS gpiochip.
