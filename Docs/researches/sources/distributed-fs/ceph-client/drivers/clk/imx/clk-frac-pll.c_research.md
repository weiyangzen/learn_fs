## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-frac-pll.c

### Purpose
`clk-frac-pll.c` implements the i.MX8M fractional PLL clock type with prepare/unprepare, rate calculation, rate programming, and lock/ack polling.

### Important APIs, Types, And Functions
`struct clk_frac_pll` stores `clk_hw` and PLL base. Helpers `clk_wait_lock()` and `clk_wait_ack()` poll lock/new-divider status. CCF ops are `clk_pll_prepare()`, `clk_pll_unprepare()`, `clk_pll_is_prepared()`, `clk_pll_recalc_rate()`, `clk_pll_determine_rate()`, and `clk_pll_set_rate()`. Constructor `imx_clk_hw_frac_pll()` is exported.

### Control Flow
Prepare clears powerdown and waits for lock. Set-rate computes integer and fractional divider fields using a fixed denominator, writes CFG1, forces output divider to zero, toggles `PLL_NEWDIV_VAL`, waits for ack unless powered down/bypassed, clears the toggle, and returns status.

### State, Persistence, And Dependencies
PLL configuration persists in CFG0/CFG1 registers. Driver state is a heap object. It depends on CCF PLL ops, bitfield helpers, `do_div`, and polling timeouts.

### Integration Points
i.MX8M clock trees use this as a programmable PLL parent for composite roots and peripherals.

### Risks
No explicit validation of `divfi` range in determine/set paths. Ack wait is skipped when powered down or bypassed, so deferred hardware reload behavior must match spec. Lock timeout values are hardware-sensitive.

### Test Signals
Program supported audio/video rates, compare recalc with expected fractional math, test powerdown/prepare, force lock/ack timeout, and run clk rate-change stress under active consumers.
