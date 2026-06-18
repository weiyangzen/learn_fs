<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm53573-ilp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm53573-ilp.c

Purpose: This early clock provider implements the BCM53573 ILP low-power clock, including enable/disable programming and rate measurement from PMU registers.

Important APIs, types, and functions: `bcm53573_ilp` wraps `clk_hw` and a parent syscon `regmap`. Clock ops are `bcm53573_ilp_enable()`, `bcm53573_ilp_disable()`, and `bcm53573_ilp_recalc_rate()`. Initialization is `bcm53573_ilp_init()`, registered with `CLK_OF_DECLARE(..., "brcm,bcm53573-ilp", ...)`.

Control flow: Init allocates the clock object, resolves its parent name, gets the parent node's syscon regmap, registers the clock, and adds a simple OF provider. Enable writes fixed PMU values to `PMU_SLOW_CLK_PERIOD` and offset `0x674`; disable clears them. Recalc enables measurement via `PMU_XTAL_FREQ_RATIO`, samples up to 20 changing ratio values or gives up after repeated identical reads, disables measurement, averages the ratio, and returns `parent_rate * 4 / avg`.

State and persistence behavior: Hardware state is in PMU registers. Software keeps only the regmap and clock object. Measurement is transient and disabled afterward to save power.

Dependencies and integration points: It depends on syscon/regmap for the parent PMU, a parent clock in DT, and early registration because architecture code needs the clock before the full device model.

Risks and test signals: Risks include division by zero if measurement returns no usable sample, magic register value fragility, busy-loop measurement latency, and inaccurate averages under unstable hardware. Test signals include early boot success on BCM53573, plausible ILP rate reporting, enable/disable register effects, and no PMU measurement timeout-like stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm53573-ilp.c -->
