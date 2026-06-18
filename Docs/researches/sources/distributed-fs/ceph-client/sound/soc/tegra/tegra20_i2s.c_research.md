# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.c

## Purpose
This is the Tegra20 I2S ASoC controller driver. It provides a stereo playback/capture DAI, programs serial format, sample width, clock/timing, FIFO thresholds, DMA addresses, runtime PM reset/clock sequencing, and optional rate filtering when the audio PLL parent rate is fixed.

## Important APIs, types, and functions
`struct tegra20_i2s` contains the per-device DAI copy, I2S clock, DMA descriptors, regmap, and reset. DAI operations include `tegra20_i2s_set_fmt()`, `tegra20_i2s_hw_params()`, `tegra20_i2s_trigger()`, `tegra20_i2s_startup()`, and `tegra20_i2s_probe()`. Runtime PM uses `tegra20_i2s_runtime_suspend()` and `tegra20_i2s_runtime_resume()`. `tegra20_i2s_filter_rates()` constrains rates to those divisible by the fixed parent clock. Regmap callbacks classify normal, volatile, and precious FIFO registers.

## Control flow
Probe allocates state, copies the DAI template and names it after the device, gets reset and clock, maps registers, creates regmap, fills FIFO DMA addresses, enables runtime PM, registers component/DAI, and registers Tegra PCM. Runtime resume asserts reset, enables clock, waits, deasserts reset, marks regcache dirty, and syncs cached registers; suspend sets cache-only and disables the clock. `set_fmt()` accepts normal bit/frame polarity, master or slave clock provider modes, and DSP_A/DSP_B/I2S/right-justified/left-justified formats. `hw_params()` accepts S16/S24/S32, sets packed FIFO format, computes and sets `i2sclock = rate * channels * sample_size * 2`, writes timing and FIFO thresholds. Triggers enable FIFO1 for playback or FIFO2 for capture.

## State and persistence
Register state is cached across runtime PM. DMA descriptors persist in driver state. The per-device DAI template avoids sharing mutable DAI name across instances. No additional software stream state is tracked beyond hardware and ALSA runtime.

## Dependencies and integration points
It depends on `tegra20_i2s.h`, Tegra PCM helpers, reset/clock providers, regmap MMIO, runtime PM, ASoC DAI/component APIs, and compatible `nvidia,tegra20-i2s`. DAS is selected in Kconfig to route the I2S controller to pins.

## Risks and edge cases
The DAI advertises only S16_LE even though `hw_params()` handles S24/S32, so higher widths may be unreachable without DAI capability changes. Only normal clock polarity is supported. Fixed-parent-rate filtering assumes parent divisibility by `rate * 128`; if no rates match it intentionally filters none. Clock or reset failures during resume disable the clock but leave stream setup to recover. The final hardware `* 2` clock multiplier is Tegra-specific and easy to regress.

## Test signals
Test master/slave formats and all supported serial formats, 8-96 kHz rates, fixed-parent-rate constraints, runtime PM suspend/resume around active controls, DMA playback/capture FIFO enable bits, and whether S24/S32 paths are actually negotiable through ALSA.
