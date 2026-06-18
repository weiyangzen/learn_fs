# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.h

## Purpose
Defines Tegra30 I2S register offsets, masks, and private data structures consumed by `tegra30_i2s.c`.

## Important APIs/types/functions
Constants cover `CTRL`, `TIMING`, `OFFSET`, `CH_CTRL`, `SLOT_CTRL`, CIF, flow, status, and coefficient registers. `struct tegra30_i2s_soc_data` holds the SoC-specific CIF writer. `struct tegra30_i2s` persists the DAI template, clock, AHUB endpoints, DMA data, regmap, and PCM config.

## Control flow
No executable code. The constants drive regmap access validation, DAI format programming, hardware-params timing, TDM slot setup, and transfer enable/disable in the C driver.

## State, dependencies, integration, risks, tests
State is represented by `struct tegra30_i2s`, which links platform probe, DAI callbacks, PM, and cleanup. It depends on `tegra_pcm.h` and AHUB types through the C include chain. Risks are stale offsets, wrong bit shifts, and DMA/AHUB field mismatches. Validate through build coverage, regmap dumps, DT probe, and physical BCLK/LRCK/data timing checks.
