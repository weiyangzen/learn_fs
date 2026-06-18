# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_mbdrc.h

## Purpose
Defines Tegra210 MBDRC register offsets, bitfields, RAM-control constants, band parameter structures, and exported helper prototypes used by the OPE parent driver and MBDRC implementation.

## Important APIs, Types, And Functions
Key types are `struct tegra210_mbdrc_band_params`, which mirrors per-band hardware layout for thresholds, ratios, gains, time constants, and biquad coefficients, and `struct tegra210_mbdrc_config`, which aggregates global compressor configuration plus three band parameter blocks. The header exports `tegra210_mbdrc_regmap_init()`, `tegra210_mbdrc_component_init()`, and `tegra210_mbdrc_hw_params()`.

## Control Flow
This header has no executable control flow. Its constants drive register validation, control encoding, default programming, and RAM access sequencing in `tegra210_mbdrc.c`.

## State And Persistence
The structures define the shape of software-provided defaults and RAM payloads. Register and coefficient persistence is handled by regmap cache and hardware RAM, not by this header.

## Dependencies And Integration Points
Includes platform device and ASoC component declarations. It is included by `tegra210_mbdrc.c` and by `tegra210_ope.c` so the OPE parent can initialize and invoke the MBDRC submodule.

## Risks
The comment says structure element order and size must track hardware RAM layout, so ABI-like layout drift is risky. Field macros for thresholds and ratios are used by packing code; any mismatch between shifted masks and expected unshifted ALSA values can silently corrupt compressor parameters.

## Test Signals
Build coverage catches prototype and macro drift. Runtime coverage should validate all exposed controls against documented MBDRC register fields, especially threshold packing, ratio arrays, and coefficient RAM sizes.
