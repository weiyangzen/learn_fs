# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115-lpass-lpi.c

## Purpose
Provides SM6115 LPASS LPI pinctrl variant data for the shared LPASS low-power audio GPIO driver. It describes 19 audio-domain pins and mux functions for SoundWire, quad MI2S, DMIC, I2S1-3, and WSA MCLK under `qcom,sm6115-lpass-lpi-pinctrl`.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` enumerates the variant mux IDs. `sm6115_lpi_pins[]` declares `gpio0` through `gpio18`. Function group arrays define where each audio function can appear. `sm6115_groups[]` maps each pin to a `LPI_PINGROUP` with either explicit slew offsets for SoundWire and WSA MCLK pins or `LPI_NO_SLEW` for many digital audio pins. `sm6115_functions[]` exports function descriptors, and `sm6115_lpi_data` passes pins, groups, and functions to the generic LPI probe.

## Control Flow
The module platform driver binds to its OF compatible and uses generic `lpi_pinctrl_probe` and `lpi_pinctrl_remove`. Probe-time control flow is in `pinctrl-lpass-lpi.c`; this file only supplies the static function/group matrix. Runtime mux or pinconf changes requested by audio drivers are validated against these arrays before the generic driver writes LPASS LPI registers.

## State And Persistence
No mutable local state exists. Hardware state persists in LPASS LPI TLMM and slew registers. All declared pins 0-18 have group entries, and the final pin, gpio18, exposes `wsa_mclk` with explicit slew offset 14.

## Dependencies And Integration Points
Depends on `pinctrl-lpass-lpi.h`, generic LPASS LPI probe/remove, platform resources, optional clocks, gpiolib, and audio subsystem DT pin states. Integrates with SoundWire TX/RX, quad MI2S, DMIC01/23, I2S1/I2S2/I2S3, and WSA clock routing for SM6115 audio hardware.

## Risks
The file has no active logic, so failures are mostly table-contract bugs: wrong mux order, wrong group membership, or wrong slew offset. Several pins multiplex SoundWire and MI2S data, so board-specific states must avoid conflicting active functions. The generic driver has a 32-pin bitmap limit; this 19-pin variant is within it. Missing a function in `sm6115_functions[]` would make an otherwise listed group unusable from device tree.

## Test Signals
Successful probe, debugfs group/function listing, GPIO operations on LPASS pins, SoundWire TX/RX audio playback/capture, DMIC capture, I2S1-3 pin states, quad MI2S routing, WSA MCLK output, and pinconf readback on pins with explicit slew offsets. Source size reviewed: 155 lines.
