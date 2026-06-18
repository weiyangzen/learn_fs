# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-sam9x60-pll.c

Purpose: modern PLL provider for SAM9X60/SAM9X7/SAMA7-style fractional PLL cores and divider outputs using `PLL_UPDT`, `PLL_CTRL0`, `PLL_CTRL1`, `PLL_ACR`, and lock status registers.

Important APIs and data: `sam9x60_clk_register_frac_pll()` and `sam9x60_clk_register_div_pll()` register fractional and divider clocks. Shared `sam9x60_pll_core` stores id, layout, characteristics, regmap, and lock; `sam9x60_frac` stores mul/frac; `sam9x60_div` stores div/safe_div. Ops support gated or live-changing set_rate modes plus save/restore.

Control flow: fractional prepare selects PLL ID, loads ACR, writes mul/frac, enables optional UPLL bandgap/regulator sequencing, issues update, enables lock/PLL, and waits for lock. Fractional set-rate computes integer and 22-bit fractional multiplier. Divider prepare selects ID and enables programmed divider; changeable mode writes div while running. A notifier can switch one divider to a safe value before parent rate changes.

State and persistence: cached mul/frac/div initialize from hardware if already locked/enabled, otherwise from minimum valid rate. Save/restore records enable status and replays setup for active clocks.

Dependencies and integration: used by SAM9X60 and SAM9X7 SoC files and newer SAMA7 files. It depends on spinlocked regmap access, PLL characteristics including core/output ranges and ACR defaults, and common-clock notifier support.

Risks: one global notifier divider is supported; unbounded lock waits can hang on invalid PLL settings; `sam9x60_div_pll_compute_div()` iterates against `div_mask` rather than decoded max count, making layout masks important. Test signals include PLL lock bits, ACR UPLL sequencing, safe-divider behavior during CPU PLL changes, and exact rate propagation through generated/USB/master clocks.
