# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_14nm.c

Purpose: 14nm DSI PHY and PLL support. It implements fractional VCO programming with spread-spectrum support, custom N1/N2 post-divider clocks that mirror master settings to a bonded slave, v2 D-PHY lane timing programming, and multiple SoC configs with different supplies and resource starts.

Important APIs and functions:
- `struct dsi_pll_config` holds fixed and computed PLL/SSC values; `struct dsi_pll_14nm` owns VCO clock state, post-divider lock, cached state, and optional slave pointer.
- `dsi_pll_14nm_vco_set_rate()`, `_recalc_rate()`, `_prepare()`, `_unprepare()`, and `dsi_pll_14nm_clk_determine_rate()` implement VCO clock operations.
- `pll_14nm_ssc_calc()`, `pll_14nm_dec_frac_calc()`, `pll_14nm_calc_vco_count()`, `pll_db_commit_common()`, `pll_db_commit_ssc()`, and `pll_db_commit_14nm()` compute and commit PLL programming.
- `dsi_pll_14nm_postdiv_*()` implements custom divider ops so bonded DSI slaves receive matching N1/N2 divider values.
- `dsi_14nm_pll_save_state()`, `dsi_14nm_pll_restore_state()`, `dsi_14nm_set_usecase()`, `pll_14nm_register()`, and `dsi_14nm_phy_enable()/disable()` are the main integration functions.

Control flow: PLL init registers VCO, N1 postdiv, byte fixed factor, N1/2 clock, and N2 pixel divider, then stores the PLL in the global list. Rate setting initializes default SSC parameters, computes decimal/fractional values and VCO/KVCO counts, commits slave registers first when master, then commits local registers. Prepare starts PLL via common control and polls both lock and ready bits. PHY enable computes v2 timings, programs LDO/common state, writes all four data lanes plus clock lane through `dsi_14nm_dphy_set_timing()`, resets the digital block, selects bit clock behavior for slave/standalone, sets usecase, and releases power-down.

State and persistence: caches `n1postdiv`, `n2postdiv`, and `vco_rate` from `REG_DSI_14nm_PHY_CMN_CLK_CFG0` and clock framework rate. `pll_14nm_list` and `slave` persist cross-PHY relationships. `postdiv_lock` protects the shared `CMN_CLK_CFG0` register.

Dependencies and integration points: uses clk-provider dividers/fixed factors, OF-matched configs, `msm_dsi_dphy_timing_calc_v2`, DSI register XML headers, regulators named `vcca` or `vdda`, and DSI usecases `STANDALONE`, `MASTER`, and `SLAVE`.

Risks: SSC is enabled by default with hard-coded spread/frequency and no DT override, so EMI/tolerance changes require code changes. Bonded mode assumes the slave PLL exists in `pll_14nm_list`; missing probe ordering could break master programming. Post-divider writes are mirrored only from master. PLL lock polling requires both lock and ready bits and can fail on timing-sensitive hardware. Some configs omit regulators, relying on zero-count bulk handling.

Test signals: rate sweep 1.3 to 2.6 GHz, SSC register inspection, divider rate propagation, bonded DSI master/slave operation, save/restore after PHY reset, all compatible configs including 2290/6150 single-PHY variants, and lane timing validation at low and high bit clocks.
