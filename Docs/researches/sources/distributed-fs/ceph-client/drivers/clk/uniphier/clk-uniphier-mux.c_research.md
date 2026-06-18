# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mux.c

Purpose: UniPhier regmap-backed mux clock implementation using per-parent masks and values.

Important APIs/types/functions: `uniphier_clk_register_mux()`, `uniphier_clk_mux_set_parent()`, `uniphier_clk_mux_get_parent()`, and `uniphier_clk_mux_ops`. State is `struct uniphier_clk_mux`.

Control flow: registration stores parent names, register offset, mask array, and value array, then registers a `CLK_SET_RATE_PARENT` mux. Set-parent writes the selected parent's value under its mask. Get-parent reads the register and returns the first parent whose masked value matches.

State and persistence: hardware selector fields persist in syscon registers. Driver state references static mask/value arrays embedded in clock data.

Dependencies/integration: used by SD and SoC-glue clock data; depends on regmap and CCF mux determine-rate.

Risks: overlapping masks or values can make `get_parent()` return the first matching parent, so table order matters. Set-parent trusts index bounds from CCF. Regmap read errors are returned through a `u8` callback, which can truncate negative errors.

Test signals: parent switching for SD and SATA reference muxes, readback matching after writes, and validation of overlapping mask/value tables.
