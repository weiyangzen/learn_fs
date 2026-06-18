# sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2q.c

## Purpose
Registers the Berlin2Q global clock tree, including system and CPU PLLs, composite divider cells, peripheral gates, CPU fixed-factor clock, and TWD fixed-factor clock.

## Important APIs, Types, And Functions
The main entry is `berlin2q_clock_setup`, declared with `CLK_OF_DECLARE` for `marvell,berlin2q-clk`. Static data includes `clk_names`, `bg2q_pll_map`, `default_parent_ids`, `bg2q_divs`, and `bg2q_gates`. It uses `berlin2_pll_register`, `berlin2_div_register`, `clk_hw_register_gate`, and `clk_hw_register_fixed_factor`.

## Control Flow
Setup allocates onecell data, maps the global register resource and the separate CPU PLL resource, optionally replaces `refclk` from DT, registers SYSPLL and CPUPLL, registers all divider cells with parent names resolved from parent IDs, registers gates, adds fixed CPU and TWD clocks, checks leaf slots for registration errors, then adds the OF provider.

## State And Persistence
Static globals `clk_data`, `gbase`, `cpupll_base`, and `lock` persist after init. Registered clocks and MMIO mappings remain for the lifetime of the system.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/berlin2q.h`, common Berlin divider and PLL helpers, OF address resources from the parent node, and CCF provider APIs.

## Risks And Edge Cases
The file explicitly lacks BG2Q AVPLL and PLL bypass switch support. Failure cleanup unmaps bases but does not unregister clocks already registered. Parent IDs for AVPLL names are present even though AVPLL registration is TODO, so related rates may depend on external or absent parent clocks.

## Test Signals
Boot registration on BG2Q DT, correct mapping of separate CPU PLL base, provider slots for all dividers/gates, fixed CPU and TWD rates, graceful handling of missing AVPLL parents, and error paths for missing resources are useful signals.
