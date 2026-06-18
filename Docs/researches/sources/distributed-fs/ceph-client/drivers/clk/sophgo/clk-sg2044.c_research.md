# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044.c

## Purpose
This is the SG2044 main clock-controller driver. It models non-PLL clocks as divider, mux, and gate objects, registers them against the MMIO clock-controller block, and exposes a onecell provider for `sophgo,sg2044-clk`.

## Important APIs, Types, And Functions
Internal types are `sg2044_div_internal`, `sg2044_mux_internal`, `sg2044_gate_internal`, `sg2044_clk_common`, `sg2044_div`, `sg2044_mux`, `sg2044_gate`, `sg2044_clk_ctrl`, and `sg2044_clk_desc_data`. Divider callbacks are `sg2044_div_recalc_rate()`, `sg2044_div_determine_rate()`, `sg2044_div_set_rate()`, and gateable divider enable/disable/is_enabled functions. Mux safety uses `sg2044_mux_notifier_cb()`. Registration is handled by `sg2044_clk_init_ctrl()` and `sg2044_clk_probe()`.

Declaration macros define gateable dividers, plain dividers, parent-data dividers, read-only dividers, muxes, and gates. Static common arrays group all dividers, muxes, and gates for descriptor-driven registration.

## Control Flow
Probe maps MMIO resource 0, retrieves match descriptor data, allocates onecell storage sized to divider + mux + gate counts, and calls `sg2044_clk_init_ctrl()`. Initialization registers dividers first, then muxes, then gates. Muxes are registered with `devm_clk_hw_register_mux_parent_data_table()` and non-read-only muxes get notifiers that switch to parent index 0 before parent rate changes and restore the saved parent after. Gates are registered after resolving their parent `clk_hw` pointers through the already-filled onecell table.

Divider set-rate asserts the divider, writes a new factor and selects the register factor source, then deasserts. Gateable dividers also expose branch enable/disable via bit 4. Read-only dividers report rates from either hardware factor or default `initval`.

## State And Persistence
Static clock objects describe all SG2044 divisors, muxes, and gates. Probe writes the shared MMIO base and lock into each common object. Hardware state lives in clock divider/gate/mux registers, with divider reset/factor-source/branch-enable bits and gate enable bits persisted until hardware reset.

## Dependencies And Integration Points
The driver depends on PLL parent clocks exposed by `clk-sg2044-pll.c` through firmware names (`fpll0`, `mpll0`, `dpll0`, etc.), CCF generic gate and mux helpers, CCF divider helpers, cleanup guard macros, and dt-binding IDs from `sophgo,sg2044-clk.h`. It integrates with platform probing and Device Tree clock consumers.

## Risks
`ctrl->data.num` is set to the count of registered clocks, not necessarily the highest dt-binding ID plus one. If IDs are sparse or larger than the count, onecell lookup can be wrong or out of bounds. `sg2044_div_internal.flags` mixes divider flags with `CLK_IS_CRITICAL` in several declarations; CCF flags belong in `common.hw.init->flags`, not divider flags, so critical policy may not apply as intended for those gateable dividers. Parent fix-up warns when a parent ID has not been registered, making registration order critical. Mux notifiers assume parent index 0 is the safe fixed parent.

## Test Signals
Boot SG2044 and check that every dt-binding ID resolves, especially high-valued or sparse IDs. Inspect `clk_summary` for AP/RP/TPU/NOC, DDR0-7, VC, CXP, timers, UART, GPIO, SD/eMMC, Ethernet, and PKA clocks. Exercise divider rate changes, gateable divider enable/disable, non-read-only mux parent rate changes, and late unused-clock cleanup to validate critical-clock policy.
