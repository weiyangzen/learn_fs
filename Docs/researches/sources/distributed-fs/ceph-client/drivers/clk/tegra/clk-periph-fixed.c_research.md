# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-fixed.c

Registers fixed-factor Tegra peripheral clocks that still have peripheral enable/reset bits in the CAR register banks.

`tegra_clk_periph_fixed_ops` implements is_enabled, enable, disable, and recalc_rate. Enable writes the bank's enable-set register; disable writes enable-clear; is_enabled requires the enable bit set and reset bit deasserted. Recalc applies `parent_rate * mul / div`. `tegra_clk_register_periph_fixed()` resolves the register bank from the peripheral number, allocates the clock, fills init data, and registers it.

Enable/reset state persists in CAR bank registers. The fixed multiplier/divider are immutable software parameters. It depends on `get_reg_bank()` and Tegra periph register metadata from `clk.h`, CCF registration, and MMIO write-one-to-set/clear registers.

Wrong peripheral number maps to the wrong enable/reset bank. The driver does not deassert reset on enable; it only reports reset as part of enabled state. Test signals include gate bit writes, reset-state readback, and fixed-factor rate visible in `clk_summary`.
