# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.h

## Purpose
This header defines the register map, bit fields, constants, SoC data, and private state structures for the Tegra186/Tegra264 ASRC driver.

## Important APIs, types, and functions
It declares stream register offsets from `TEGRA186_ASRC_CFG` through sample buffer config registers, global offsets through `TEGRA186_ASRC_CYA`, default threshold and compensation constants, fractional precision selections, ratio source values (`ARAD` and `SW`), stream stride/count/limit, and ARAM start addresses for Tegra186 and Tegra264. `struct tegra186_asrc_lane` stores userspace-programmable lane values. `struct tegra_asrc_soc_data` carries the SoC-specific ARAM start address. `struct tegra186_asrc` owns SoC data, six lanes, and a regmap pointer.

## Control flow
There is no executable flow. The `.c` file uses the offset macros to generate per-stream register addresses and regmap access policy, and uses the structures as its private driver state.

## State and persistence
The header describes the persistent software state used to restore hardware after runtime PM. Lane fields mirror ALSA controls and are replayed in `hw_params()` and runtime resume.

## Dependencies and integration points
It is private to the Tegra ASRC implementation and assumes Linux types such as `struct regmap` are available from source includes. The ARAM address constants couple the generic driver to Tegra186/Tegra264 memory maps.

## Risks and edge cases
All stream register arithmetic depends on `TEGRA186_ASRC_STREAM_STRIDE`, `STREAM_MAX`, and `STREAM_LIMIT` staying consistent with hardware. A wrong ARAM start address would cause transfer failures after PM resume. Expanding to more lanes requires resizing `lane[]`, updating DAI/control declarations, and revisiting regmap ranges.

## Test signals
Compile-time use in `tegra186_asrc.c` is the first check. Runtime validation should include verifying register offsets against hardware documentation, regmap access ranges, and PM restore behavior on both SoC data variants.
