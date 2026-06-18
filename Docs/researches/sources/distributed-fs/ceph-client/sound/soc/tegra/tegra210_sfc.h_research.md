# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_sfc.h

## Purpose
Defines Tegra210 SFC RX/TX/global registers, coefficient RAM controls, rate-table size, path enum, and driver private state.

## Important APIs, Types, And Functions
Key constants are RX/TX status/interrupt/CIF/frequency registers, `TEGRA210_SFC_COEF_RAM_DEPTH`, coefficient RAM access bits, and `TEGRA210_SFC_NUM_RATES`. `enum tegra210_sfc_path` indexes RX and TX conversion settings. `struct tegra210_sfc` stores mono/stereo conversion arrays, input/output sample-rate indices, and regmap.

## Control Flow
No executable flow exists. The enum and constants are consumed by control callbacks, rate selection, coefficient RAM programming, and regmap access validation in `tegra210_sfc.c`.

## State And Persistence
The state struct persists selected conversion modes and rate indices between DAI callbacks. Hardware register persistence is handled by regcache; coefficient RAM is restored from static tables when needed.

## Dependencies And Integration Points
Included only by the SFC implementation. Register naming follows Tegra XBAR CIF conventions, enabling consistent DAPM endpoint construction.

## Risks
`TEGRA210_SFC_NUM_RATES` must match both `tegra210_sfc_rates[]` and both dimensions of `coef_addr_table`; any mismatch risks out-of-bounds table access or missing conversion coverage.

## Test Signals
Compile-time array sizing and runtime testing across every rate index are the best signals. Control tests should exercise both `SFC_RX_PATH` and `SFC_TX_PATH` entries.
