# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.c

## Purpose
This is the Tegra20 SPDIF ASoC transmitter driver. It exposes a playback-only DAI, programs SPDIF packing/bit mode/FIFO trigger level/clock rate, controls TX enable on PCM triggers, manages runtime PM reset/clock/regcache sequencing, and registers Tegra PCM DMA support.

## Important APIs, types, and functions
`struct tegra20_spdif` stores the output clock, DMA descriptors, regmap, and reset. DAI operations are `tegra20_spdif_probe()`, `tegra20_spdif_hw_params()`, `tegra20_spdif_trigger()`, and `tegra20_spdif_startup()`. `tegra20_spdif_filter_rates()` constrains rates for fixed-parent-rate systems. Runtime PM uses `tegra20_spdif_runtime_suspend()` and `tegra20_spdif_runtime_resume()`. Regmap callbacks classify control/status/FIFO/channel/user registers as readable/writeable/volatile/precious.

## Control flow
Probe allocates state, gets reset and `out` clock, maps MMIO, creates regmap, sets playback DMA to `DATA_OUT`, enables devm runtime PM, registers component/DAI, and registers devm Tegra PCM. Startup optionally adds a rate rule when `nvidia,fixed-parent-rate` is present. `hw_params()` accepts only S16_LE, enables packed 16-bit mode, sets TX FIFO attention to four words to match DMA burst safety, maps sample rates to exact SPDIF output clock rates, sets the clock, and warns if the provider returns a different rate. Triggers set or clear `TX_EN`.

## State and persistence
Register state is cached with regcache across runtime PM. Runtime resume resets hardware and syncs cached registers after enabling the output clock. Playback DMA state is stable after probe. The DAI advertises only 32/44.1/48 kHz even though `hw_params()` has mappings for 88.2/96/176.4/192 kHz.

## Dependencies and integration points
It depends on `tegra20_spdif.h`, Tegra PCM helpers, reset/clock providers, regmap MMIO, runtime PM, ASoC, and DT compatible `nvidia,tegra20-spdif`. The fixed-parent-rate comment describes sharing an audio PLL with I2S/HDMI paths.

## Risks and edge cases
Higher sample-rate cases in `hw_params()` are unreachable unless DAI rates are expanded. Only 16-bit packed PCM is supported. Clock mismatch is warning-only, which may still produce bad HDMI/SPDIF audio. Rate filtering only considers 32/44.1/48 kHz. No capture DAI is registered despite header/register support for RX.

## Test signals
Test playback at 32, 44.1, and 48 kHz, verify `DATA_FIFO_CSR` attention level and `CTRL_TX_EN`, check runtime PM restore, validate fixed-parent-rate constraints with concurrent I2S/HDMI use, and test clock mismatch warnings on non-exact providers.
