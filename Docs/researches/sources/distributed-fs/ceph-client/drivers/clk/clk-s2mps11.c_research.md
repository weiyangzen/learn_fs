<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-s2mps11.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-s2mps11.c

### Purpose
`clk-s2mps11.c` exposes 32.768 kHz PMIC clocks for Samsung S2MPG10, S2MPS11, S2MPS13, S2MPS14, and S5M8767 devices. It registers AP, CP, and BT clocks where present and controls enable bits in the PMIC RTC/control register.

### Important APIs, Types, And Functions
`struct s2mps11_clk` stores PMIC device pointer, clocks child node, `clk_hw`, legacy `clk`, clkdev lookup, mask, and register. Clock ops are `s2mps11_clk_prepare()`, `s2mps11_clk_unprepare()`, `s2mps11_clk_is_prepared()`, and `s2mps11_clk_recalc_rate()`. Probe uses `s2mps11_clk_parse_dt()`, device ID based register selection, `devm_clk_register()`, `clkdev_hw_create()`, and `of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe allocates three clock slots and onecell data, selects the PMIC register for the matched platform ID, finds the parent MFD `clocks` child node, applies optional `clock-output-names`, registers each supported clock, creates clkdev lookups, fills onecell hardware pointers, and publishes the provider. S2MPS14 skips the CP clock. Remove deletes the provider, releases the child-node reference, and drops clkdev lookups. Hardware state persists as PMIC enable bits.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include Samsung MFD core, per-device PMIC register headers, platform device IDs from the parent MFD, OF child node `clocks`, and clkdev users. Risks include global mutation of the static `s2mps11_clks_init` names across devices, `of_clk_add_hw_provider()` return value ignored, unprepare writing `~mask` as value relying on regmap masking semantics, and missing hardware variants. Test signals include all PMIC ID probes, S2MPS14 CP omission, OF and clkdev lookups, prepare/unprepare bit transitions, custom clock names, and provider cleanup on remove/error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-s2mps11.c -->
