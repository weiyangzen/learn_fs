# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.h

## Purpose
Declares the PHY mux descriptor and documents its CCF semantics for pipe and symbol clocks.

## Important APIs, Types, And Functions
`struct clk_regmap_phy_mux` stores the mux register and embedded `clk_regmap`. The header exports `clk_regmap_phy_mux_ops`.

## Control Flow
PHY or clock controller drivers instantiate the descriptor and register it. CCF enable selects the PHY source, disable parks the clock on the reference source, and is-enabled reflects that source choice.

## State And Persistence
Static descriptor state identifies the register. Hardware persists the selected source.

## Dependencies And Integration Points
Includes `clk-regmap.h`. The comment explains integration with PHY drivers and GDSC sequencing.

## Risks And Edge Cases
This is intentionally specialized; using it for a normal mux would invert expectations because disabled means reference source rather than no clock.

## Test Signals
Clock enable/disable around PHY/GDSC transitions validates the contract.
