# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.c

## Purpose
`clk-regmap.c` provides generic regmap-backed Meson clock ops for gates, dividers, and muxes, plus initialization logic that discovers and caches the relevant regmap for a `struct clk_regmap`.

## Important APIs, Types, And Functions
The exported initialization function is `clk_regmap_init()`. Exported ops are `clk_regmap_gate_ops`, `clk_regmap_gate_ro_ops`, `clk_regmap_divider_ops`, `clk_regmap_divider_ro_ops`, `clk_regmap_mux_ops`, and `clk_regmap_mux_ro_ops`. Internal helpers implement gate enable/disable/is_enabled, divider recalc/determine/set_rate, and mux get_parent/set_parent/determine_rate.

## Control Flow
Initialization returns early if `clk->map` is already preset. Otherwise it first asks the clock's device for a regmap, then falls back to the parent DT node via `syscon_node_to_regmap()`. Gate enable/disable performs masked `regmap_update_bits()` and honors `CLK_GATE_SET_TO_DISABLE`. Divider callbacks read, mask, and pass encodings through Linux divider helpers; read-only dividers use `divider_ro_determine_rate()` with the current value. Mux callbacks convert between register values and framework parent indices.

## State, Persistence, And Dependencies
The cached `struct regmap *` in `struct clk_regmap` is persistent kernel state after init. Hardware state persists in the target registers. Dependencies include Linux device/regmap/syscon/OF APIs, `clk-provider.h` helpers for dividers and muxes, and local `clk-regmap.h`.

## Integration Points
Almost every Meson SoC clock file uses these ops for simple gates, muxes, and dividers. The implementation bridges SoC-specific static descriptors to both syscon-backed legacy controllers and newer platform-device MMIO controllers.

## Risks And Edge Cases
`clk_regmap_init()` couples clock type initialization to controller topology and contains a FIXME noting this is a temporary design. If neither device nor parent syscon provides a regmap, registration fails with `-EINVAL`. `clk_regmap_mux_get_parent()` returns an `int` error through a `u8` callback type, which can collapse negative errors into large unsigned values; this mirrors common clock callback constraints but makes read failures hard to report cleanly. HIWORD mask flags are documented as ignored.

## Test Signals
Tests should cover init with preset, device, and parent-syscon regmaps; gate polarity with and without `CLK_GATE_SET_TO_DISABLE`; divider recalc/set/determine including read-only mode; mux parent value/index conversion with tables; and probe failure when no regmap is available.
