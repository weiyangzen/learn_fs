# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-spmi-pmic-div.c

## Purpose
Implements a common-clock provider for Qualcomm SPMI PMIC clock-divider blocks. The driver registers one or more divider clocks under a PMIC register map, computes power-of-two divider factors, gates the hardware with required nanosecond delays based on the XO period, and exposes phandle indexes starting at 1.

## Important APIs, Types, And Functions
- `struct clkdiv` holds the parent PMIC regmap, base offset for one divider block, per-clock spinlock, `clk_hw`, and cached XO period in nanoseconds.
- `div_factor_to_div` maps hardware factor 0 or 1 to divide-by-1 and larger factors to powers of two; `div_to_div_factor` maps requested divisors to a capped 3-bit hardware factor.
- `is_spmi_pmic_clkdiv_enabled`, `__spmi_pmic_clkdiv_set_enable_state`, and `spmi_pmic_clkdiv_set_enable_state` read and update `REG_EN_CTL` and apply documented enable/disable delays.
- `clk_spmi_pmic_div_enable`, `disable`, `determine_rate`, `recalc_rate`, and `set_rate` implement the common-clock operations.
- `spmi_pmic_clkdiv_probe` reads DT properties, obtains the parent regmap and XO clock rate, allocates a counted flexible-array controller, registers `div_clkN` clocks, and adds the provider.

## Control Flow
Probe reads the PMIC child node's `reg` base and `qcom,num-clkdivs`, gets the parent's regmap, obtains the `xo` input clock to calculate `cxo_period_ns`, then creates one `clkdiv` per 0x100-byte block. Each registered clock has a single parent from clock index 0 and the same divider operations. Runtime enable/disable serialize register access with `spin_lock_irqsave`. `set_rate` computes the divider factor from `parent_rate / rate`, disables the divider if it is currently enabled, writes `REG_DIV_CTL1`, and re-enables it with a delay calculated from the new factor.

## State And Persistence
Software state is per-clock base, regmap, lock, and XO period. Persistent hardware state is the divider factor in `REG_DIV_CTL1` and the enable bit in `REG_EN_CTL`; it remains in PMIC registers until changed or reset. There is no saved software copy of the selected divider, so recalc reads hardware.

## Dependencies And Integration Points
The driver depends on the parent SPMI PMIC/MFD regmap, DT properties `reg` and `qcom,num-clkdivs`, an `xo` clock, common-clock registration, and `devm_of_clk_add_hw_provider`. Consumers reference clocks by one-based phandle index. It integrates with PMIC-controlled external clocks or peripheral reference clocks that need simple divided XO outputs.

## Risks And Edge Cases
The provider intentionally subtracts one from the phandle index, so DT consumers using zero will fail. `clk_get_rate(xo)` must be nonzero or period calculation would be invalid. `parent_rate / rate` truncates in `set_rate`, while `determine_rate` rounds up before mapping to a power-of-two divider, so caller expectations should be checked. Enable/disable delays depend on accurate XO period. Register writes during rate changes temporarily gate the clock, which may not be acceptable for always-on consumers.

## Test Signals
Test with invalid and valid one-based clock indexes, missing `reg`, missing `qcom,num-clkdivs`, absent/deferred `xo`, and absent parent regmap. Runtime signals include recalc matching hardware factor, determine-rate choosing power-of-two divisions, rate changes while enabled toggling enable around the divider write, and scoped delays visible in register-level traces.
