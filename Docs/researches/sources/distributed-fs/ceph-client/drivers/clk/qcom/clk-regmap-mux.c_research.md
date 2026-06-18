# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.c

## Purpose
Provides a simple regmap-backed mux clock with closest-rate parent selection. It decodes and writes source select fields in shared Qualcomm clock registers.

## Important APIs, Types, And Functions
Exports `clk_regmap_mux_closest_ops`. Internal callbacks are `mux_get_parent()`, `mux_set_parent()`, and `to_clk_regmap_mux()`.

## Control Flow
Get-parent reads the configured register field, applies shift and width mask, and either maps the raw value through `parent_map` or returns it directly. Set-parent maps the CCF parent index to raw hardware config when needed and updates the masked register field. Determine-rate is delegated to `__clk_mux_determine_rate_closest`.

## State And Persistence
No software cache is kept. Hardware stores the selected parent in the register field; descriptor fields define the bit layout and optional mapping.

## Dependencies And Integration Points
Depends on regmap, CCF mux helpers, `clk-regmap.h`, and `common.h` parent maps. It is used by MSM8996 SMUXes and many simple SoC muxes.

## Risks And Edge Cases
Incorrect parent maps silently produce wrong parent indices. The ops table always uses closest-rate selection, which may not be right for muxes needing exact or table-driven behavior.

## Test Signals
Parent get/set with and without parent maps, mask boundary values, and closest-rate parent selection are useful tests.
