# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.c

## Purpose
`clk-phase.c` implements Meson phase-control clock ops. It supports a simple single phase bitfield, an audio triphase clock where three phase fields must stay synchronized, and a special serial-clock word-select inverter where the word-select bit is the inverse of the phase bit.

## Important APIs, Types, And Functions
The exports are `meson_clk_phase_ops`, `meson_clk_triphase_ops`, and `meson_sclk_ws_inv_ops`. Helpers convert between register values and degrees using `phase_step(width)`. Single-phase callbacks read/write `ph`. Triphase callbacks synchronize `ph1` and `ph2` to `ph0` during init and update all three on set. SCLK word-select callbacks synchronize/write `ws` to the inverse of the phase value.

## Control Flow
Single phase get/set is direct field read/write. Triphase init calls `clk_regmap_init()`, reads phase 0, writes that value to phases 1 and 2, and later reports phase 0 as authoritative. SCLK WS inverter init calls `clk_regmap_init()`, reads `ph`, and writes `ws` as `!ph`; set-phase repeats that paired update.

## State, Persistence, And Dependencies
State persists in the phase and word-select register fields described by the corresponding header structs. Dependencies include `clk-regmap.h`, `clk-phase.h`, `parm.h`, common-clock phase callbacks, and `DIV_ROUND_CLOSEST()`.

## Integration Points
Audio clock-controller descriptions use these ops to expose I2S/TDM phase controls through the common clock framework. The triphase abstraction intentionally presents one phase knob even though hardware has multiple output/input phase fields.

## Risks And Edge Cases
`phase_step(width)` uses integer division of 360 by `2^width`, so unsupported widths that do not evenly divide 360 would lose precision. `degrees_to_val()` wraps a rounded 360-degree request back to zero. The SCLK WS helper assumes a binary phase field; wider fields would make `val ? 0 : 1` too coarse unless hardware semantics match.

## Test Signals
Tests should verify degree/value conversion for supported widths, 360-degree wraparound, triphase init synchronization, triphase set writing all fields, and word-select inversion on init and set-phase.
