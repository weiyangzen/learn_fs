# sources/distributed-fs/ceph-client/drivers/clk/clk-hi655x.c

Purpose: clock provider for the Hi655x PMIC 32.768 kHz clock. It exposes one clock through the common clock framework and controls it through the parent PMIC regmap.

Important APIs, types, and functions: `struct hi655x_clk` links `struct hi655x_pmic` to `struct clk_hw`. `hi655x_clk_recalc_rate()` returns the fixed 32768 Hz rate. `hi655x_clk_enable()` updates `HI655X_CLK_SET` at `HI655X_CLK_BASE`; prepare/unprepare wrap it. `hi655x_clk_probe()` gets parent driver data, optional `clock-output-names`, registers the clock, and adds an OF provider.

Control flow: module platform probe allocates managed state, reads the parent MFD device data, initializes `clk_init_data`, registers with `devm_clk_hw_register()`, and exposes `of_clk_hw_simple_get()`. Runtime clock prepare/unprepare maps directly to regmap update calls.

State and persistence: hardware state is a PMIC register bit. Software state is devm-managed and tied to the platform device lifetime. The rate is constant and not persisted elsewhere.

Dependencies and integration points: depends on the Hi655x MFD/PMIC parent, regmap, platform driver infrastructure, OF properties on the parent node, and common clock provider APIs.

Risks and test signals: `hi655x_clk_is_prepared()` tests `val & HI655X_CLK_BASE`, which is suspicious because the enable mask is `HI655X_CLK_SET`; this may misreport prepared state. Probe assumes parent driver data is present. Test signals should include prepare/unprepare register updates, `is_prepared()` correctness, and provider lookup from PMIC child nodes.
