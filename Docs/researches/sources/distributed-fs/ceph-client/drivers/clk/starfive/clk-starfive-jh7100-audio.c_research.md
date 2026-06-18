# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100-audio.c

## Purpose
This driver registers the JH7100 audio clock controller, covering ADC/DAC/I2S/PDM/SPDIF/PWMDAC/USB audio-domain clocks.

## Important APIs, Types, And Functions
The clock table `jh7100_audclk_data[]` uses shared `JH71X0_*` macros to encode gate, divider, mux-divider, and inverter clocks. `jh7100_audclk_probe()` allocates `jh71x0_clk_priv`, maps registers, converts internal and external parent IDs into `clk_parent_data`, registers each `clk_hw`, and publishes `jh71x0_clk_get()` as the OF provider. The platform driver is module-capable.

## Control Flow
Probe iterates from `0` to `JH7100_AUDCLK_END`, derives ops from each entry's encoded `max` field via `starfive_jh71x0_clk_ops()`, resolves parents to either local `priv->reg[]` hardware or firmware names such as `audio_src`, `audio_12288`, and `dom7ahb_bus`, then registers the clock.

## State And Persistence
State is in the audio clock control registers, accessed by the shared JH71x0 read-modify-write helpers. The driver-private allocation persists for the module lifetime and stores the base pointer, lock, and per-clock structs.

## Dependencies And Integration Points
It depends on `CLK_STARFIVE_JH7100`, the shared JH71x0 core, and `dt-bindings/clock/starfive-jh7100-audio.h`. External parent clocks come from the main JH7100 clock generator or board inputs.

## Risks
Parent mapping only handles three external IDs even though several external constants are declared for iopad clocks; table entries that use unsupported IDs would register with empty parent data. Audio bit-clock and LR-clock mux/divider setup is sensitive to parent order.

## Test Signals
Probe success, clock summary parent/rate checks, I2S ADC/DAC playback/capture, PDM/SPDIF operation, and module load/unload coverage are useful signals.
