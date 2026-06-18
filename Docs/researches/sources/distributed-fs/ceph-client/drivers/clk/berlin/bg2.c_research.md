# sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2.c

## Purpose
Registers the Berlin2/Berlin2CD global clock tree: reference inputs, simple PLLs, AVPLL VCOs/channels, bypass muxes, audio/video muxes, composite divider cells, leaf gates, and fixed-factor TWD clock.

## Important APIs, Types, And Functions
The main entry is `berlin2_clock_setup`, declared with `CLK_OF_DECLARE` for `marvell,berlin2-clk`. Static data includes register offsets, `clk_names`, `bg2_pll_map`, `default_parent_ids`, `bg2_divs`, and `bg2_gates`. It calls `berlin2_pll_register`, `berlin2_avpll_vco_register`, `berlin2_avpll_channel_register`, `clk_hw_register_mux`, `berlin2_div_register`, `clk_hw_register_gate`, and `clk_hw_register_fixed_factor`.

## Control Flow
Setup allocates onecell data, maps the parent global-register node, optionally replaces default reference names from DT, registers SYS/MEM/CPU PLLs, selects AVPLL scramble quirks for Berlin2, registers AVPLL A and B VCO/channel trees, creates PLL bypass muxes and audio/video muxes, registers all divider and gate cells into binding-indexed onecell slots, adds the fixed TWD clock, checks leaf clock errors, and adds the OF provider.

## State And Persistence
Global static `clk_data`, `gbase`, and `lock` persist after early setup. The onecell array stores only public leaf clocks by binding index; intermediate PLLs/muxes are registered by name for parent resolution.

## Dependencies And Integration Points
Depends on Berlin clock bindings, common Berlin helper files, OF parent/global register mapping, CCF registration, and DT-compatible selection. Consumers use the dt-binding indexes.

## Risks And Edge Cases
Failure cleanup only unmaps `gbase`; registered earlier clocks and allocated onecell data are not fully unwound. Some audio/video parent PLLs are documented as assumptions or unknown. Error checks only inspect onecell leaf slots, not every intermediate registration result beyond immediate `IS_ERR` checks.

## Test Signals
Boot with Berlin2 and Berlin2CD compatibles, verify AVPLL quirk selection, provider indexes for all `CLKID_*` leaves, bypass mux parent names, gate bits under `REG_CLKENABLE`, and TWD fixed factor from CPU/3.
