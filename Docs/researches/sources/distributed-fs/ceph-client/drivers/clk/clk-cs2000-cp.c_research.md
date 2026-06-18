# sources/distributed-fs/ceph-client/drivers/clk/clk-cs2000-cp.c


### Purpose
`clk-cs2000-cp.c` drives the Cirrus Logic CS2000-CP fractional-N clock synthesizer and clock multiplier. It exposes one programmable output clock sourced from either dynamic `clk_in` or static `ref_clk` mode.

### Important APIs, Types, And Functions
`struct cs2000_priv` stores CCF hardware, I2C client, `clk_in`, `ref_clk`, regmap, mode flags, ratio format, clock-skip setting, and suspend/resume rate state. Important helpers include `cs2000_rate_to_ratio()`, `cs2000_ratio_to_rate()`, `cs2000_ratio_set()`, `cs2000_ratio_select()`, `cs2000_select_ratio_mode()`, `cs2000_enable_dev_config()`, and `cs2000_wait_pll_lock()`. `cs2000_ops` implements parent reporting, recalc/determine/set rate, prepare, and unprepare.

### Control Flow, State, And Persistence
Probe allocates state, initializes regmap, obtains both parent clocks, registers the clock, checks chip revision, and unwinds provider/clock registration on revision failure. Registration parses `clock-output-names`, `cirrus,dynamic-mode`, `cirrus,aux-output-source`, and `cirrus,clock-skip`, bounds the reference clock divider, initializes static mode to 1:1, and adds an OF provider. Set-rate freezes global config, chooses 12.20 or 20.12 ratio mode, writes four ratio bytes for channel 0, selects ratio channel/mode, unfreezes, and saves rate state for late resume. Prepare enables device config and outputs, then polls PLL lock.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C/regmap, two parent clocks, OF properties, CCF `CLK_SET_RATE_GATE`, and late system sleep resume. Risks include `dev_get_drvdata()` in resume relying on drvdata being set through I2C client data conventions, channel 0-only implementation, ratio format boundary mistakes, static/dynamic parent semantics, and timeout sensitivity while polling lock. Test signals include dynamic and static mode parent choice, ref-clock range validation, ratio round-trip math, PLL lock timeout, output disable on unprepare, revision rejection, resume reprogramming of saved ratio, and `-EPROBE_DEFER` for missing parents.
