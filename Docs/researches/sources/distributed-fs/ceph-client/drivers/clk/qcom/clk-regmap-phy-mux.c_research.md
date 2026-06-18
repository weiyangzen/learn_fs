# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.c

## Purpose
Implements a tiny PHY pipe/symbol clock mux abstraction that models the PHY source as enabled and a reference/safe source as disabled. It lets PHY drivers switch a clock source around GDSC power transitions using normal CCF enable/disable calls.

## Important APIs, Types, And Functions
Exports `clk_regmap_phy_mux_ops`. Internal callbacks are `phy_mux_is_enabled()`, `phy_mux_enable()`, `phy_mux_disable()`, and `to_clk_regmap_phy_mux()`. Hardware values are `PHY_MUX_PHY_SRC` and `PHY_MUX_REF_SRC` under `PHY_MUX_MASK`.

## Control Flow
Enable writes the mux field to the PHY-provided source. Disable writes the reference source. Is-enabled reads the mux field, warns if it is neither expected value, and reports true only when the PHY source is selected.

## State And Persistence
No software cache is kept. The mux register persists whether the clock is sourced from the PHY or reference clock.

## Dependencies And Integration Points
Depends on regmap, CCF, bitfield helpers, and `clk-regmap-phy-mux.h`. It is intended for PHY pipe clocks and some UFS symbol clocks where clock source selection must track PHY/GDSC power sequencing.

## Risks And Edge Cases
Unexpected register values trigger a warning but still report disabled unless equal to the PHY value. The implementation assumes fixed two-bit encodings and is not a generic parent mux.

## Test Signals
PHY power-on/off sequences, GDSC transitions, UFS symbol clock use, and invalid raw mux value warnings are useful signals.
