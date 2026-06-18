<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20-emc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20-emc.c

Purpose: CCF implementation of the Tegra20/Tegra30-style EMC clock. It provides parent selection, fractional divider programming, low-jitter PLLM_UD selection, MC/EMC same-frequency preparation, and a callback-based rate rounding hook supplied by the external EMC driver.

Important APIs, types, and functions: exported `tegra20_clk_register_emc()`, `tegra20_clk_set_emc_round_callback()`, `tegra20_clk_emc_driver_available()`, and `tegra20_clk_prepare_emc_mc_same_freq()` are the integration points. State is held in local `struct tegra_clk_emc` with `reg`, `mc_same_freq`, `want_low_jitter`, `round_cb`, and `cb_arg`. CCF ops are `emc_recalc_rate()`, `emc_get_parent()`, `emc_set_parent()`, `emc_set_rate()`, `emc_set_rate_and_parent()`, and `emc_determine_rate()`.

Control flow: registration creates a critical `"emc"` clock with parents `"pll_m", "pll_c", "pll_p", "clk_m"`. Recalc and set-rate use Tegra fractional divider math where EMC rate is `parent * 2 / (div + 2)`. Parent/rate writes update source and divider fields, set `USE_PLLM_UD` only for PLLM with divider zero when low jitter is requested, set or clear `MC_EMC_SAME_FREQ`, write the register, and fence for one microsecond. Rate determination first asks `round_cb` to choose a supported EMC rate, then searches parents for an exact representable divider and fills `best_parent_*`.

State and persistence: persistent state is the CAR EMC source register plus software booleans for desired low-jitter and MC same-frequency modes. The callback is installed later by the EMC driver through a global clock lookup. The clock is critical to prevent accidental memory-clock disable.

Dependencies and integration: Tegra20 registers this with `low_jitter=false`; Tegra30 uses `low_jitter=true`. External EMC drivers install the rounding callback and may call same-frequency preparation before clock changes. Depends on `div_frac_get()`, `fence_udelay()`, and public callback typedefs in `include/linux/clk/tegra.h`.

Risks and test signals: risks include `determine_rate()` dereferencing a missing `round_cb` if consumers request rates before the EMC driver registers, no locking around register writes, exact-divider search failure for valid board timings, and stale `mc_same_freq` state. Test callback availability deferral in SoC users, parent/divider combinations, PLLM low-jitter bit behavior, MC same-frequency toggling, and memory stability across rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20-emc.c -->
