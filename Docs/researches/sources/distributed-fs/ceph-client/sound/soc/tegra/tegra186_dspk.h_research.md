# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.h

## Purpose
This header defines Tegra186 DSPK register offsets, bit fields, enums, and private driver state used by the DSPK ASoC component.

## Important APIs, types, and functions
Register offsets cover RX status/interrupt/CIF registers, enable/reset/clock-gate/status registers, and core/codec control. Core control fields include channel select, OSR, and LR polarity masks. Constants define RX FIFO depth, OSR base factor, and the 4:1 DSPK interface clock ratio. Enums describe OSR values, channel selection, and LR polarity. `struct tegra186_dspk` stores control state, clock, and regmap.

## Control flow
There is no executable flow. The `.c` file uses these macros for regmap policies, CIF setup, clock-rate computation, and core-control updates.

## State and persistence
The state struct persists mixer-control choices outside hardware and across runtime PM as long as the device instance exists. Regmap persistence is handled by the implementation's cache.

## Dependencies and integration points
It is private to the DSPK driver and assumes `struct clk` and `struct regmap` are available via source includes. Register definitions must align with hardware and the `tegra186_dspk_regmap` access policy.

## Risks and edge cases
Adding new hardware variants or wider FIFO/rate support requires updating constants and validating the clock formula. Enum ordinal values are written directly into hardware fields, so reordering enums would be a behavioral change.

## Test signals
Compile the DSPK driver, verify macro values against hardware docs, and test that enum values program expected `CORE_CTRL` bits for each ALSA control.
