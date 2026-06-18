# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/dmic.c

## Purpose
`dmic.c` is a generic platform ASoC codec driver for digital microphones with no codec register map. It models a capture-only DMIC endpoint and optionally controls a DMIC enable GPIO and `vref` regulator around DAPM power events. It also exposes wakeup and mode-switch delays from device properties or module parameters.

## Important APIs, Types, and Functions
The driver state is `struct dmic`, containing optional `gpio_en`, optional `vref`, `wakeup_delay`, and `modeswitch_delay`. `dmic_component_probe()` allocates this state, obtains optional regulator/GPIO resources, reads `wakeup-delay-ms` and `modeswitch-delay-ms`, applies module parameter overrides, clamps mode-switch delay to `MAX_MODESWITCH_DELAY`, and stores drvdata. `dmic_aif_event()` powers the external DMIC resources for DAPM `POST_PMU` and disables them for `POST_PMD`. `dmic_daiops_trigger()` delays after `SNDRV_PCM_TRIGGER_STOP` when requested. `dmic_dev_probe()` optionally clones the DAI driver to restrict `channels_max` from `num-channels`.

## Control Flow
Platform probe registers a component and a single capture DAI named `dmic-hifi`. If DT supplies `num-channels`, the probe validates 1..8, allocates a private DAI copy, and adjusts the advertised maximum capture channels. Component probe handles resource discovery after ASoC instantiates the component. During capture path power-up, DAPM turns on `DMIC AIF`, calls `dmic_aif_event()`, sets the enable GPIO high, enables `vref`, then sleeps for the configured wakeup delay. Power-down reverses the GPIO and regulator. PCM stop can add a mode-switch delay after stop to satisfy DMIC mode timing.

## State and Persistence
No persistent codec register state exists. Runtime state is entirely devm-managed platform resources plus integer delays. Module parameters `wakeup_delay` and `modeswitch_delay` override per-device properties globally. GPIO state and regulator enable count are external side effects owned by DAPM path activity.

## Dependencies and Integration Points
The driver depends on platform devices, OF match `dmic-codec`, gpiod consumer API for `dmicen`, regulator consumer API for `vref`, and ASoC DAPM. Machine drivers connect CPU DAI capture to `dmic-hifi` and may supply `num-channels` and delay properties.

## Risks
The global module parameters can unexpectedly override all instances. `modeswitch_delay` uses `mdelay()`, so large values would busy-wait; it is clamped to 70 ms but still blocks CPU on stop. Regulator enable happens after GPIO assertion on power-up and disable after GPIO deassertion on power-down; boards with different sequencing needs must encode that outside this generic driver. The DAI advertises continuous rates and many PCM/DSD formats, so the actual constraints must come from CPU DAI or machine driver if hardware is narrower.

## Test Signals
Probe with and without optional GPIO/regulator, DT `num-channels` boundary tests, DAPM capture start/stop verifying GPIO and regulator transitions, delay property/module-parameter behavior, and capture stream negotiation across S16/S24/S32 and DSD formats are useful signals. Negative cases include invalid `num-channels`, regulator probe deferral, and GPIO acquisition errors.
