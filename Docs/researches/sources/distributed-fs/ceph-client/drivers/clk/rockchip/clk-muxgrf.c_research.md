# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-muxgrf.c

## Purpose
Implements Rockchip mux clocks controlled through GRF regmap fields instead of CRU mux registers. It supports normal regmap bit updates and hiword-mask writes.

## Important APIs, Types, and Functions
`struct rockchip_muxgrf_clock` holds CCF hardware, regmap, register, shift, width, and mux flags. `rockchip_muxgrf_get_parent()` reads the raw parent index. `rockchip_muxgrf_set_parent()` writes with hiword-mask `regmap_write()` or `regmap_update_bits()`. `rockchip_clk_register_muxgrf()` validates the regmap and registers the mux.

## Control Flow, State, and Persistence
Persistent state is the allocated mux object. Parent state lives in the GRF field. There is no polling or cached state.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on CCF mux APIs, regmap, and SoC branch tables. Risks include unavailable regmap, raw parent indexes without translation, wrong width/shift masks, and hiword writes to unsupported registers. Test parent switching, get-parent after set-parent, invalid regmap handling, and rate determination across parents.
