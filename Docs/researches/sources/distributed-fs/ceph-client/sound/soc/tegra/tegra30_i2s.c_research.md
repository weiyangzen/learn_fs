# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.c

## Purpose
Tegra30/Tegra124 I2S CPU DAI driver. It registers a stereo playback/capture DAI, programs I2S MMIO through regmap, routes audio through Tegra30 AHUB FIFOs, and registers a Tegra dmaengine PCM platform.

## Important APIs/types/functions
Main callbacks are `tegra30_i2s_set_fmt`, `tegra30_i2s_hw_params`, `tegra30_i2s_trigger`, `tegra30_i2s_set_tdm`, and `tegra30_i2s_probe`. Platform lifecycle is `tegra30_i2s_platform_probe/remove`; runtime PM is `tegra30_i2s_runtime_suspend/resume`. SoC CIF behavior is selected with `tegra30_i2s_config` or `tegra124_i2s_config`.

## Control flow
Probe reads `nvidia,ahub-cif-ids`, maps registers, creates a cached regmap, enables runtime PM, allocates/routs AHUB TX/RX FIFOs, registers the DAI, then registers Tegra PCM with named DMA channels. `hw_params` accepts only stereo `S16_LE`, sets clock/timing, programs Audio CIF, and writes data offsets. `trigger` starts/stops AHUB FIFO and I2S transfer bits.

## State, dependencies, integration, risks, tests
State is the private I2S object, FIFO IDs, DMA channel names/data, regmap cache, selected SoC callback, and runtime clock state. It depends on ASoC, dmaengine PCM, Tegra AHUB, PM runtime, regmap, clocks, and DT. Risks are bad CIF IDs, limited format support, clock rounding, and regcache resume failures. Test with probe logs, `aplay`/`arecord`, TDM slot setup, and runtime suspend/resume.
