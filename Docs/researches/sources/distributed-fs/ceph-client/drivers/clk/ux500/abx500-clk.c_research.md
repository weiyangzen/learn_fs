<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/abx500-clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/abx500-clk.c

## Purpose

`abx500-clk.c` registers clocks sourced from the AB8500/AB8505 companion PMIC for Ux500 systems. It exposes sysclk buffer outputs, an ultra-low-power clock, an internal clock mux, and an audio clock through a onecell OF clock provider.

## Important APIs, Types, And Functions

`ab8500_reg_clks()` is the main registration routine. It enables SWAT through `ab8500_sysctrl_set()`, creates `ab8500_sysclk2/3/4` gates with `clk_reg_sysctrl_gate()`, creates fixed-rate `ulpclk` with `clk_reg_sysctrl_gate_fixed_rate()`, creates `intclk` with `clk_reg_sysctrl_set_parent()`, and creates the `audioclk` gate. `abx500_clk_probe()` accepts AB8500 and AB8505 parent devices only.

## Control Flow

`arch_initcall(abx500_clk_init)` registers a platform driver matching `stericsson,ab8500-clk`. Probe obtains the parent MFD state, checks the chip family, registers six clocks into `ab8500_clks[]`, fills `clk_onecell_data`, and calls `of_clk_add_provider()`.

## State And Persistence Behavior

Clock state is stored in AB8500 sysctrl registers. The static `ab8500_clks[]` and `ab8500_clk_data` hold provider-visible runtime references. Parent selection for `intclk` is tracked by the sysctrl helper and committed to hardware when changed.

## Dependencies And Integration Points

The file depends on the AB8500 MFD/sysctrl APIs, `dt-bindings/clock/ste-ab8500.h`, Linux CCF, clkdev, and DT provider helpers. It is consumed by Ux500 audio, low-power, and board clock users.

## Risks And Test Signals

Risks include unsupported parent MFD IDs, AB8500 sysctrl write failures, missing `of_node`, and the single global provider array preventing multiple independent instances. Test by booting AB8500/AB8505 DTs, checking clock-provider registration, toggling sysclk buffers/audio clock, and selecting both `intclk` parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/abx500-clk.c -->
