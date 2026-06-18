# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.h

## Purpose

`mt8189-afe-clk.h` is the public MT8189 AFE clock-control interface for local platform and DAI code. It defines logical APLL IDs, the full clock-index enum used by `mt8189-afe-clk.c`, APLL widget names, and function prototypes for enabling, disabling, selecting, and initializing audio clocks.

## Important APIs, Types, and Data

`APLL1_W_NAME` and `APLL2_W_NAME` provide stable string names for APLL selection, likely shared with DAPM or controls. The first enum defines logical `MT8189_APLL1` and `MT8189_APLL2`. The second enum defines every clock handle index in `afe_priv->clk`: top muxes, APLL roots, APLL divided clocks, APLL12 dividers for I2S/FMI2S/TDM, per-interface muxes, `clk26m`, and peripheral audio clocks. `MT8189_CLK_NUM` sizes the array.

The API exposes MCLK management (`mt8189_mck_enable`, `mt8189_mck_disable`), APLL lookup (`mt8189_get_apll_rate`, `mt8189_get_apll_by_rate`, `mt8189_get_apll_by_name`), initialization (`mt8189_init_clock`), raw clock wrapper helpers, per-APLL enable/disable, main-clock enable/disable, and register-read/write clock enable/disable.

## Control Flow

The header has no executable control flow. It shapes call flow by requiring consumers to call `mt8189_init_clock()` at platform probe before any other clock operation, then use the narrower helpers around stream and register-access lifetimes. DAI code should enable an APLL and MCLK before programming serial output clocks and disable them when the route is no longer active. Platform PM code should use main and reg-rw helpers when entering or leaving powered states.

## State and Persistence

No state is stored in the header. The enum values are persistent ABI within this driver directory because they index `afe_priv->clk` and the `aud_clks[]` table. Reordering or inserting values without matching `mt8189-afe-clk.c` and device-tree clock names can break every clock operation. Runtime state lives in `struct mt8189_afe_private` from `mt8189-afe-common.h` and the Linux clock framework.

## Dependencies and Integration Points

The header forward-declares `struct mtk_base_afe` and uses `struct clk` in prototypes, so including files can call clock helpers without pulling in implementation details. It integrates with `mt8189-afe-common.h` through `MT8189_MCK_NUM` and `struct mt8189_afe_private`, with `mt8189-afe-clk.c` for implementation, with MT8189 DAI files for stream clocking, and with Kbuild through the platform object list.

## Risks

The clock enum order is fragile. It must match `aud_clks[]` exactly and must remain consistent with any device-tree clock-names binding. Adding a clock requires updating this enum, the string table, and likely binding documentation. The exposed raw enable/disable wrappers make it possible for callers to bypass higher-level sequencing, so usage audits should prefer APLL/MCLK/main/reg-rw helpers where possible. `mt8189_get_apll_by_name()` has no invalid-name status in its signature, which limits caller-side validation.

## Test Signals

Compile tests catch signature mismatches between declarations and definitions. Runtime tests should validate every public helper has at least one exercised caller path: probe for `mt8189_init_clock`, register access paths for reg-rw helpers, playback/capture setup for MCLK helpers, and 44.1/48 kHz-family streams for APLL selection. Static analysis should check that enum additions are reflected in the implementation string table and in `MT8189_CLK_NUM`-sized allocations.
