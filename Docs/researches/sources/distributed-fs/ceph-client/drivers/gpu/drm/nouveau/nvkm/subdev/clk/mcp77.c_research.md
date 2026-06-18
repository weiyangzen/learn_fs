# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/mcp77.c

## Purpose
Implements MCP77 integrated-chipset clock reading and reclocking for core, shader, host, and vdec domains using a mix of fixed HREF-derived clocks, NVPLL/SPLL, and dividers.

## Important APIs, types, and functions
Exports `mcp77_clk_new()`. Important helpers are `mcp77_clk_read()`, `mcp77_clk_calc()`, `mcp77_clk_prog()`, `read_pll()`, `calc_pll()`, and `calc_P()`. It reuses `gt215_clk_pre()` and `gt215_clk_post()`.

## Control flow
Read paths decode master clock mux bits in `0x00c054`, PLL post dividers, host sources, and VDEC divider source. Calculation chooses HCLKx4 or NVPLL for core, href/NVPLL/SPLL for shader, and core or fixed 500 MHz for VDEC, printing the chosen strategy. Programming switches temporarily to safe href clocks, writes PLL coefficients and post dividers, waits for requested PLL lock bits, writes the final master mux, and disables unused PLLs/dividers.

## State and persistence
`struct mcp77_clk` caches selected sources and register values for core/shader/vdec. Persistent state is in master mux `0x00c054`, PLL coefficient/control registers, post-divider registers, and VDEC divider register.

## Dependencies and integration points
Depends on BIOS PLL limits, `nv04_pll_calc()`, GT215 pre/post FIFO gating, and common NVKM pstate logic.

## Risks
Integrated-chipset muxes are tightly encoded; a bad `mast` value can route clocks to invalid sources. PLL lock wait failure falls through to resume cleanup, so partial programming must remain safe.

## Test signals
Strategy debug logs, PLL lock bits in `0x004080`, clock readback for core/shader/vdec, and reclock tests that choose both fixed-source and PLL-source paths.
