# sources/distributed-fs/ceph-client/drivers/clk/clk-twl.c

Purpose: platform CCF driver for TWL6030/TWL6032 32 kHz clocks. It registers `clk32kg` and `clk32kaudio` as onecell clocks and controls their PM receiver state through TWL I2C register helpers.

Important APIs/types/functions: `struct twl_clock_info` stores device pointer, TWL type, base register, and clock hardware. `twlclk_read()`/`twlclk_write()` wrap `twl_i2c_read_u8()` and `twl_i2c_write_u8()`. `twl6032_clks_ops` implements prepare/unprepare/recalc_rate. `twl_clks_probe()` allocates `clk_hw_onecell_data`, registers both clocks, and adds the OF provider. `twl_clks_id` distinguishes `twl6030-clk` and `twl6032-clk`.

Control flow: probe counts the static clock table, allocates onecell data and per-clock state, fills each `twl_clock_info` with base address and type from platform ID, registers each clock, then publishes a onecell provider. prepare writes PM receiver state: TWL6030 reads the clock's group register and writes group-shifted ON state, while TWL6032 writes ON directly. unprepare writes OFF, using all groups for TWL6030. recalc_rate always returns 32768.

State and persistence: persistent state is in TWL PM receiver VREG_STATE/VREG_GRP registers. Software state is devm-managed per-clock data and onecell provider. Clocks are flagged `CLK_IGNORE_UNUSED` to avoid common clock cleanup disabling them.

Dependencies and integration: depends on TWL MFD/platform devices, TWL I2C helper APIs, CCF onecell provider, and platform IDs. Consumers use the provider's clock indices rather than named clkdev aliases.

Risks: unprepare logs but cannot propagate write failure. TWL6030 prepare uses the current group register, so bad firmware/group setup affects enable behavior. Both clocks share identical ops and fixed rate with no parent. Platform ID must be present; otherwise dereferencing `platform_get_device_id(pdev)` would fail.

Test signals: probe for both platform IDs, prepare/unprepare register writes on TWL6030 versus TWL6032, onecell index lookup, fixed 32768 rate, and behavior on TWL I2C read/write errors. No direct tests are present.
