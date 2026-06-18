# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4250-lpass-lpi.c

## Purpose
Supplies SM4250 LPASS low-power-island pin, group, and function data for the reusable `pinctrl-lpass-lpi` driver. It covers audio-domain GPIOs rather than main TLMM pins, exposing SoundWire, MI2S/I2S, DMIC, SLIMbus, external master clocks, QUP IO, and sync output muxes for `qcom,sm4250-lpass-lpi-pinctrl`.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` defines LPI mux IDs ending in `LPI_MUX_gpio` and `LPI_MUX__`. `sm4250_lpi_pins[]` declares pins `gpio0` through `gpio26`. Function group arrays bind each function name to one or more GPIO group names. `sm4250_groups[]` uses `LPI_PINGROUP(pin, slew_offset, f1, f2, f3, f4)`; several low-numbered audio pins have explicit slew offsets, while many digital microphone and QUP/sync pins use `LPI_NO_SLEW`. `sm4250_functions[]` exposes `LPI_FUNCTION(...)` entries. `sm4250_lpi_data` is the `struct lpi_pinctrl_variant_data` consumed by `lpi_pinctrl_probe()`.

## Control Flow
`module_platform_driver()` registers a simple variant driver. On OF match, the generic LPASS LPI probe fetches `.data`, maps the LPASS TLMM and optional slew resources, registers generic per-pin groups, pinctrl operations, and a sleeping GPIO chip. This file contributes only the variant arrays that tell the generic driver which mux values and slew offsets are legal for each pin.

## State And Persistence
No local mutable state exists. Hardware state persists in LPASS LPI registers configured by `pinctrl-lpass-lpi.c`. Pins 0-23 and 25-26 have group entries; pin 24 is declared as a pin and appears only as part of the `sync_out_groups[]` function list, so consumers must rely on the generic driver handling pins without explicit mux group entries carefully.

## Dependencies And Integration Points
Depends on `pinctrl-lpass-lpi.h` macros, the LPASS LPI generic probe/remove functions, gpiolib, and platform DT resources/clocks expected by the generic driver. Integrates with ASoC/audio DT pin states for SoundWire TX/RX/WSA, MI2S/quad MI2S, DMIC, SLIMbus, external clocks, and QUP IO pins used by low-power audio firmware or peripherals.

## Risks
Function membership must match hardware mux values exactly; audio pins often share pads across SoundWire, MI2S, DMIC, and external clocks, so a wrong selector can silently break capture/playback. The declared-but-not-explicitly-grouped gpio24 is a notable audit point. Slew offsets are sparse and variant-specific; using `LPI_NO_SLEW` incorrectly can make high-speed audio signaling marginal. Because this is module-driven, missing compatible or resource names produce a full LPASS audio pinctrl probe failure.

## Test Signals
Probe with `qcom,sm4250-lpass-lpi-pinctrl`, debugfs function/group visibility, GPIO request/set/get for LPASS pins, audio playback/capture over SoundWire and MI2S, DMIC capture on listed pins, external MCLK output, QUP IO pin states, sync output on GPIO19-26, and pinconf readback for slew-capable pins. Source size reviewed: 236 lines.
