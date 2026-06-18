# subset-b-003654 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.c

Purpose: common Qualcomm MSM DSI PHY core. It supplies generic D-PHY/C-PHY timing calculators, selects per-process-node PHY configuration from device tree, maps PHY register windows, registers PLL clock providers, and exposes the enable/disable/save/restore/snapshot entry points used by the DSI host.

Important APIs and functions:
- `msm_dsi_dphy_timing_calc()`, `_v2()`, `_v3()`, `_v4()` and `msm_dsi_cphy_timing_calc_v4()` convert requested bit and escape clock rates into register timing fields in `struct msm_dsi_dphy_timing`.
- `dsi_phy_driver_probe()` allocates `struct msm_dsi_phy`, resolves its hardware index from the `dsi_phy` resource start address, maps `dsi_phy`, `dsi_pll`, optional `dsi_phy_lane`, and optional `dsi_phy_regulator`, gets regulators, attaches runtime PM/pm-clk, initializes the process-specific PLL, and registers the onecell clock provider.
- `msm_dsi_phy_enable()` resumes runtime PM, enables supplies, delegates hardware programming to `cfg->ops.enable`, copies shared timings back to the caller, and restores PLL state after PHY reset when this PHY is not a slave.
- `msm_dsi_phy_disable()`, `msm_dsi_phy_set_usecase()`, `msm_dsi_phy_set_continuous_clock()`, `msm_dsi_phy_pll_save_state()`, `msm_dsi_phy_pll_restore_state()`, and `msm_dsi_phy_snapshot()` are the external control surface for host, clock, and debug code.

Control flow: probe is configuration-driven through `dsi_phy_dt_match`, which maps compatible strings to `struct msm_dsi_phy_cfg` instances compiled from the revision files. Enable flow is layered: common PM and regulator setup happens first, revision-specific register writes happen through `ops.enable`, shared timing values are returned, and cached PLL register state is restored if needed. Disable reverses only the common rails/PM plus the revision-specific power-down hook.

State and persistence: `struct msm_dsi_phy` persists mapped bases, size metadata for snapshots, regulator handles, the last computed timing block, usecase, LDO/CPHY mode flags, VCO clock handle, `pll_on`, onecell clock data, and `state_saved`. PLL save/restore is deliberately stateful because a PHY reset can silently reset PLL registers while the common clock framework still believes rates/dividers are programmed.

Dependencies and integration points: depends on Linux platform driver, OF match data, runtime PM, pm-clk, regulators, clk-provider, dt-bindings `phy-type`, MSM helpers such as `msm_ioremap_size()` and `msm_disp_snapshot_add_block()`, and revision files that export `dsi_phy_*_cfgs`. The DSI host consumes the clock provider through `DSI_BYTE_PLL_CLK` and `DSI_PIXEL_PLL_CLK`.

Risks: timing math is integer-heavy and rate-sensitive; zero rates are rejected but extreme rates can still expose rounding or register-width assumptions. `dsi_phy_get_id()` assumes fixed resource base addresses in each config. Save/restore depends on every revision hook caching the right registers before reset. Runtime PM, regulator, and PLL restore error unwinding must remain ordered to avoid powered partially configured PHY blocks.

Test signals: compile with each `CONFIG_DRM_MSM_DSI_*_PHY` variant, boot DTs for each compatible, verify `of_clk_hw_onecell_get` provides byte/pixel clocks, exercise DSI modes across low/high bit rates, suspend/resume or display handoff paths that trigger PLL save/restore, and inspect `msm_dsi_phy_snapshot()` output when PLL is on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.h

Purpose: internal contract for MSM DSI PHY implementations. It defines the revision operation table, configuration records, timing data container, runtime PHY object, exported config symbols, and timing helper prototypes shared by the common core and per-node PHY files.

Important APIs and types:
- `struct msm_dsi_phy_ops` is the revision hook table: `pll_init`, `enable`, `disable`, `save_pll_state`, `restore_pll_state`, `set_continuous_clock`, and `parse_dt_properties`.
- `struct msm_dsi_phy_cfg` describes a compatible's regulators, operations, PLL min/max rates, resource base addresses used for PHY id detection, quirk flags, and whether separate regulator/lane windows exist.
- `struct msm_dsi_dphy_timing` stores all D-PHY timing registers plus shared host-visible fields and legacy v2 half-byte/prep-delay fields.
- `struct msm_dsi_phy` is the live device state: platform device, MMIO bases/sizes, id, supplies, timing, config, optional tuning data, usecase, mode flags, VCO clock, PLL power state, provided clocks, and save-state marker.

Control flow: revision files fill `msm_dsi_phy_cfg.ops`, the common probe binds one config to one `struct msm_dsi_phy`, and callers invoke only the common exported functions. Timing calculation prototypes centralize the shared math in `dsi_phy.c` while hardware files only commit register values.

State and persistence: the header makes `state_saved`, `pll_on`, `usecase`, `regulator_ldo_mode`, and `cphy_mode` explicit cross-file state. `provided_clocks` has `NUM_PROVIDED_CLKS`, sized around `DSI_PIXEL_PLL_CLK + 1`, so each PLL implementation must populate the expected byte and pixel indices.

Dependencies and integration points: includes dt clock bindings, clk-provider, delay, regulator consumer, and local `dsi.h` for DSI constants and clock request/usecase definitions. Exported `dsi_phy_*_cfgs` are consumed by the common OF table and compiled conditionally via Kconfig in `dsi_phy.c`.

Risks: this header is a tight ABI within the driver. Adding fields or ops requires all revision files to keep coherent semantics. `io_start` based indexing is fragile for new SoCs. Misstating `has_phy_lane` or `has_phy_regulator` causes probe-time mapping failures or missing register programming.

Test signals: build all PHY variants, validate every exported config referenced by `dsi_phy_dt_match`, test D-PHY and C-PHY timing callers, and verify clock-provider consumers see both `DSI_BYTE_PLL_CLK` and `DSI_PIXEL_PLL_CLK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_10nm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_10nm.c

Purpose: 10nm MSM DSI PHY and PLL implementation, including v3.0 PHY programming, PLL rate calculation, common-clock registration, DT tuning properties, bonded-DSI usecase handling, and two config variants for generic 10nm and 8998 old-timing hardware.

Important APIs and functions:
- `struct dsi_pll_10nm`, `struct pll_10nm_cached_state`, and `struct dsi_phy_10nm_tuning_cfg` carry PLL clock state, cached dividers/muxes, and per-lane drive tuning.
- PLL callbacks `dsi_pll_10nm_vco_set_rate()`, `dsi_pll_10nm_vco_prepare()`, `dsi_pll_10nm_vco_unprepare()`, `dsi_pll_10nm_vco_recalc_rate()`, and `dsi_pll_10nm_clk_determine_rate()` implement the VCO `clk_ops`.
- `pll_10nm_register()` builds the clock tree: VCO, out divider, bit divider, byte fixed factor, by-2 bit clock, post-out divider, pclk mux, and DSI pixel divider.
- `dsi_10nm_pll_save_state()` and `dsi_10nm_pll_restore_state()` cache and restore out-div, bit-div, pixel-div, mux, and VCO programming.
- `dsi_10nm_phy_enable()`, `dsi_10nm_phy_disable()`, and `dsi_10nm_phy_parse_dt()` implement PHY lane programming and optional DT drive-strength configuration.

Control flow: probe calls `dsi_pll_10nm_init()`, which registers clocks, stores the PLL in `pll_10nm_list`, performs an initial save-state handoff, and seeds `vco_current_rate`. A rate set computes decimal/fractional dividers, optional SSC values, commits PLL registers, writes frequency-independent PLL registers, and flushes. VCO prepare biases PLL rails, mirrors bias/global-clock to a bonded slave if present, reprograms rate, starts PLL, polls lock, enables global clocks, and enables RBUF. PHY enable calculates v3 D-PHY timings, waits for refgen ready, powers common blocks/lanes, writes timing registers, sets usecase, and commits lane strength/tuning registers.

State and persistence: persistent state lives in `vco_current_rate`, `cached_state`, `slave`, `postdiv_lock`, and `phy->tuning_cfg`. Save/restore is needed after PHY reset and for display handoff. DT tuning is persisted as unsigned masked register values after signed range validation.

Dependencies and integration points: uses common clock APIs, `readl_poll_timeout_atomic`, MMIO register XML headers, `msm_dsi_dphy_timing_calc_v3`, OF properties `qcom,phy-rescode-offset-top`, `qcom,phy-rescode-offset-bot`, and `qcom,phy-drive-ldo-level`. `dsi_10nm_set_usecase()` links master PLLs to `pll_10nm_list[(id + 1) % DSI_MAX]` and selects external PLL source for slaves.

Risks: `dsi_pll_10nm_vco_prepare()` reprograms from `vco_current_rate`; a stale zero/default can program an unintended VCO. The old-timing quirk changes lane `TX_DCTRL` behavior and must match silicon. Lane swap is TODO and fixed. DT offset validation reads into signed arrays through an unsigned OF helper pattern, so property encoding should be tested carefully. Slave lookup assumes both PHYs have probed.

Test signals: verify PLL lock at min/max rates, byte/pixel clock rate propagation through the clock tree, both standalone and bonded DSI, 8998 old timing, DT tuning boundaries `[-32,31]`, allowed LDO levels 375 through 500 mV, suspend/resume save/restore, and warnings when PHY is disabled with PLL still on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_10nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_14nm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_14nm.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_14nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_20nm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_20nm.c

Purpose: 20nm DSI PHY register programming without an in-file PLL clock implementation. It programs legacy D-PHY timing, regulator/LDO selection, lane strength/configuration, and enable/disable sequencing for two PHY instances.

Important APIs and functions:
- `dsi_20nm_dphy_set_timing()` writes common timing fields into 20nm timing control registers, including bit 8 handling for `clk_zero`.
- `dsi_20nm_phy_regulator_ctrl()` selects LDO or non-LDO regulator mode using `phy->regulator_ldo_mode` and the separate regulator register window.
- `dsi_20nm_phy_enable()` calculates legacy timing via `msm_dsi_dphy_timing_calc()`, enables regulator controls, programs strength, global test/bitclk selection, data lanes, clock lane, timing registers, and finally enables PHY control.
- `dsi_20nm_phy_disable()` clears PHY enable and regulator calibration power.
- `dsi_phy_20nm_cfgs` exports supplies, register windows, and ops to the common core.

Control flow: the common core enables PM and regulators, then this file computes timing and performs a fixed register write sequence. The `BITCLK_HS_SEL` setting depends on `phy->id` and `phy->usecase`, so DSI1 standalone differs from other cases. A write memory barrier precedes the final enable register write.

State and persistence: no local heap state or PLL cache exists. Persistent behavior is limited to `phy->timing`, `phy->regulator_ldo_mode`, and `phy->usecase` from the common object. Disable leaves the common core to turn off external supplies and runtime PM.

Dependencies and integration points: depends on `dsi_phy.h`, `dsi.xml.h`, `dsi_phy_20nm.xml.h`, common timing math, common regulator bulk handling, and a separate `dsi_phy_regulator` MMIO mapping because `has_phy_regulator` is true.

Risks: fixed magic register values dominate behavior and have little runtime validation. The code powers all data lanes rather than checking active lane count. Regulator LDO versus DCDC mode must match board DT. There is no PLL save/restore hook in this file, so the surrounding clock source must not require revision-local restoration.

Test signals: smoke test DSI0/DSI1, standalone and paired usecases, LDO and non-LDO regulator modes, timing across supported bit rates, and shutdown ordering with register reads confirming `PHY_CTRL_0` and calibration power clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_20nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm.c

Purpose: mainstream 28nm DSI PHY and PLL implementation for HPM, family B, LP, 8226, and 8937 variants. It registers the 28nm clock tree, programs integer/fractional PLL settings, handles HPM/LP/8226 lock sequences, caches PLL dividers, and enables legacy D-PHY lanes/regulators.

Important APIs and functions:
- `struct dsi_pll_28nm` and `struct pll_28nm_cached_state` store VCO clock state and cached postdiv/mux registers.
- `dsi_pll_28nm_clk_set_rate()`, `_recalc_rate()`, `_is_enabled()`, `_clk_determine_rate()`, and the three prepare variants (`_hpm`, `_lp`, `_8226`) implement PLL clock behavior.
- `pll_28nm_register()` registers VCO, analog postdiv, indirect path /2, pixel divider, byte mux, and byte fixed-factor clock.
- `dsi_28nm_pll_save_state()` and `dsi_28nm_pll_restore_state()` cache `POSTDIV3`, `POSTDIV1`, byte mux, and optionally VCO rate.
- `dsi_28nm_phy_enable()` and `dsi_28nm_phy_disable()` program D-PHY timing, regulator mode, strength, lane registers, global test bit-clock selection, and power-down.

Control flow: rate setting forces postdiv2 to /4, chooses loop-filter resistance from `lpfr_lut`, selects integer versus SDM mode based on reference-clock divisibility, writes SDM/calibration registers, and respects LP-specific delay. VCO prepare is quirk-selected: HPM retries a full power sequence up to three times, LP uses nanosecond-level sequencing and a different lock-detect toggle, and 8226 uses its own calibration and retry loop. PHY enable calculates legacy timing, enables LDO or DCDC regulator mode, writes timing and lane defaults, and sets `BITCLK_HS_SEL` based on DSI id/usecase.

State and persistence: PLL cache stores dividers/mux and `vco_rate`, with restore re-running set-rate and writing cached dividers. `phy->pll_on` is set/cleared by prepare/unprepare. Quirk flags persist per config and drive LP/8226 behavior.

Dependencies and integration points: uses dt clock bindings, common clock framework, `dsi_phy_28nm.xml.h`, common `msm_dsi_dphy_timing_calc()`, regulator `vddio`, and configs referenced by compatible strings in `dsi_phy.c`.

Risks: multiple silicon paths share much code but differ in delay and lock requirements; regressions can be variant-specific. `clk_bytediv_set_rate()` ORs divider bits rather than clearing first, so callers rely on reset or prior state. LPFR lookup can reject out-of-table VCO rates. Fixed lane programming ignores lane masks. Save-state sets VCO rate to zero if PLL is off; restore must not be called with an invalid cached rate in unexpected paths.

Test signals: lock tests for HPM, LP, and 8226 variants; rate recalc comparison against requested byte/pixel clocks; regulator LDO and DCDC modes; save/restore after reset; DSI1 slave/standalone bit-clock selection; and boot tests for all exported configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm_8960.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm_8960.c

Purpose: 28nm 8960/A-family DSI PHY and PLL support. This is a separate legacy PLL topology with custom byte-divider behavior, 27 MHz reference clock, calibration/regulator sequencing, and 8960-specific lane/timing registers.

Important APIs and functions:
- `struct dsi_pll_28nm`, `struct pll_28nm_cached_state`, and `struct clk_bytediv` implement VCO state and a custom byte divider.
- `dsi_pll_28nm_clk_set_rate()`, `_recalc_rate()`, `_is_enabled()`, `_vco_prepare()`, `_vco_unprepare()`, and `_clk_determine_rate()` implement VCO operations.
- `get_vco_mul_factor()` and `clk_bytediv_*()` choose the VCO multiple from requested byte clock and program POSTDIV2.
- `pll_28nm_register()` registers VCO, special byte divider, and pixel divider.
- `dsi_28nm_pll_save_state()/restore_state()`, `dsi_28nm_phy_calibration()`, `dsi_28nm_phy_lane_config()`, and `dsi_28nm_phy_enable()/disable()` implement state and PHY control.

Control flow: byte clock users configure the custom byte divider, which requests a parent VCO multiple of 8, 16, 32, or 64 depending on bit clock. Before VCO enable, `dsi_pll_28nm_vco_prepare()` derives the hidden bit divider from the byte divider, writes POSTDIV1, enables the PLL, and polls the ready bit. PHY enable computes timing, initializes regulator registers, configures LDO/strength/control, runs hardware calibration with busy polling, writes lane/BIST defaults, and commits timing.

State and persistence: cached state includes VCO rate plus three postdiv control registers. `phy->pll_on` tracks VCO power. Calibration status is transient and not persisted. The common PHY stores the computed timing and handles external regulator lifetime.

Dependencies and integration points: uses `qcom,dsi-phy-28nm.h` clock indices, clk-provider divider helpers, `dsi_phy_28nm_8960.xml.h`, common timing math, regulator `vddio`, and two hard-coded resource starts for DSI0/DSI1.

Risks: the hidden bit-divider derivation divides byte divider by 8; unexpected divider values can underflow or misprogram. Calibration only waits until not busy and does not fail if timeout expires. Custom divider `set_rate()` ORs factor bits without clearing. The PLL reference and rate range differ from other 28nm code, so accidental config reuse is unsafe.

Test signals: byte-rate to VCO multiplier tests, PLL lock and recalc at 600 MHz to 1.2 GHz, calibration status observation, BIST/lane programming sanity, save/restore of postdivs, and both 8960 DSI resource starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm_8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_7nm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_7nm.c

Purpose: modern 7nm-family DSI PHY and PLL implementation reused by 7nm, 5nm, 4nm, and 3nm Qualcomm SoCs. It supports D-PHY and C-PHY timing, multiple hardware minor-version quirks, high-rate PLL programming, common-clock registration, continuous clock control, bonded DSI, REFGEN voting, and many SoC-specific config records.

Important APIs and functions:
- `struct dsi_pll_7nm` adds VCO state, postdiv and mux locks, PLL bias reference counting, cached dividers/mux, and bonded slave pointer.
- `dsi_pll_7nm_vco_set_rate()`, `_prepare()`, `_unprepare()`, `_recalc_rate()`, `_lock_status()`, and `_clk_determine_rate()` implement VCO operations.
- `dsi_pll_enable_pll_bias()` and `dsi_pll_disable_pll_bias()` protect common control and PLL mux state with `pll_enable_lock` plus `pll_enable_cnt`.
- `pll_7nm_register()` builds D-PHY or C-PHY-aware byte and pixel clock trees; C-PHY uses /7-style factors and fixes the DSI clock parent to post-out-div.
- `dsi_7nm_phy_enable()`, `dsi_7nm_phy_disable()`, `dsi_7nm_set_usecase()`, `dsi_7nm_set_continuous_clock()`, and PLL save/restore are the core runtime paths.

Control flow: PLL set-rate enables bias, computes decimal/fractional values and quirk-specific clock inverter settings, writes PLL programming and frequency-independent registers, optionally writes SSC registers, disables bias, and flushes. Prepare enables local and slave bias, starts PLL, polls lock, resets PHY digital logic after analog collapse, enables global clocks and RBUF, and marks `pll_on`. PHY enable calculates C-PHY or D-PHY v4 timings, optionally votes REFGEN for newer quirks, waits for refgen ready, selects voltage/strength/rescode settings by quirk, rate, and C-PHY mode, powers common blocks and lanes, sets usecase, writes timing registers, and writes lane settings.

State and persistence: `pll_enable_cnt` prevents unbalanced PLL bias power changes and rate-limits imbalance errors. Save-state caches out-div, bit/pixel dividers, and DSICLK mux while temporarily enabling bias. `vco_current_rate`, `slave`, `cphy_mode`, `usecase`, `pll_on`, and quirk flags strongly influence restore and clock-tree behavior.

Dependencies and integration points: uses `linux/bitfield.h`, clk-provider, `readl_poll_timeout_atomic`, XML register headers, common timing calculators `msm_dsi_dphy_timing_calc_v4()` and `msm_dsi_cphy_timing_calc_v4()`, DSI usecase enums, and compatible-selected configs in `dsi_phy.c`.

Risks: many SoC variants share one code path with quirk-dependent magic values, making regressions subtle. C-PHY support is present but marked with TODOs in parts of the enable path. REFGEN vote sequencing is required only on newer quirks. Slave linkage assumes both PHYs are initialized. Bias reference counting catches underflow but cannot repair missed enables/disables. 32-bit builds cap max PLL rate at `ULONG_MAX`, which differs from 64-bit 5 GHz configs.

Test signals: D-PHY and C-PHY mode tests, rate sweeps through inverter threshold bands, REFGEN vote on V4.3/V5.2/V7.2, continuous clock bit toggling, bonded master/slave external PLL selection, suspend/resume save/restore, 32-bit build coverage, and smoke tests for each exported 7nm/5nm/4nm/3nm config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_7nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.c

Purpose: top-level MSM HDMI transmitter platform driver. It owns HDMI device allocation, resource acquisition, component binding to MSM KMS, runtime PM of core power resources, IRQ fan-out, bridge/connector creation, PHY lookup, and module register/unregister plumbing.

Important APIs and functions:
- `msm_hdmi_set_mode()` writes `REG_HDMI_CTRL` under `reg_lock`, handling HDMI versus DVI mode and enable state.
- `msm_hdmi_irq()` dispatches a shared interrupt to HPD, DDC/I2C, and optional HDCP handlers.
- `msm_hdmi_init()` creates the workqueue, DDC adapter, and optional HDCP controller.
- `msm_hdmi_modeset_init()` creates the DRM bridge, optional next bridge, bridge connector, connector/encoder link, and IRQ request.
- `msm_hdmi_dev_probe()` maps MMIO/QFPROM, gets IRQ, regulators, clocks, optional external pixel clock, optional HPD GPIO, and associated PHY.
- runtime PM hooks enable/disable regulators, pinctrl state, and power clocks.

Control flow: platform probe collects all resources that may defer, finds the PHY through the `phys` phandle, enables runtime PM, and registers as a component. Component bind calls `msm_hdmi_init()` and stores `priv->kms->hdmi`. Later KMS calls `msm_hdmi_modeset_init()` to build DRM objects. Unbind/destroy tears down workqueue, HDCP, and DDC; remove unregisters the component and drops the PHY device reference.

State and persistence: `struct hdmi` persists audio state, booleans `power_on` and `hpd_enabled`, pixel clock, MMIO physical address for HDCP, regulator/clock handles, PHY pointer/device reference, DDC adapter, connector/bridge/encoder pointers, IRQ, workqueue, HDCP control, and `reg_lock`. `state_mutex` protects power/hpd booleans while `reg_lock` protects shared registers.

Dependencies and integration points: integrates with DRM bridge connector helpers, `drm_of_find_panel_or_bridge`, OF platform PHY lookup, Linux component framework, runtime PM, pinctrl, GPIO descriptors, regulators, clocks, MSM KMS private data, HDMI PHY driver registration, DDC and HDCP submodules, and compatible-specific power config tables.

Risks: `msm_hdmi_set_mode()` dereferences `hdmi->connector`, so call ordering must ensure connector exists. Runtime resume error path disables regulator and pinctrl but does not explicitly undo a partially enabled clock if `clk_bulk_prepare_enable()` fails internally after enabling some clocks, relying on bulk helper semantics. Optional QFPROM can be NULL, so HDCP users must tolerate it. IRQ handler assumes bridge and i2c are initialized by modeset setup.

Test signals: probe deferral when PHY, regulators, clocks, GPIO, or DDC are unavailable; component bind/unbind cycles; HDMI and DVI sink mode toggles; IRQ dispatch for HPD/DDC/HDCP; runtime PM suspend/resume; bridge connector creation with and without next bridge; and DT compatibility coverage for 8660/8960 and 8974-family configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.h

Purpose: shared internal header for MSM HDMI transmitter, bridge, audio, DDC, HDCP, PHY, and PLL code. It defines device state containers, platform config contracts, register access helpers, PHY abstractions, and cross-file function prototypes.

Important APIs and types:
- `struct hdmi_audio` stores enabled/rate/channel state used by audio register programming.
- `struct hdmi` is the central device object with DRM, platform, power, MMIO, PHY, DDC, connector/bridge, encoder, workqueue, HDCP, mutex, and spinlock state.
- `struct hdmi_platform_config` lists regulator and clock names for HDMI core power.
- `struct hdmi_bridge` wraps `drm_bridge` and hotplug work.
- `enum hdmi_phy_type`, `struct hdmi_phy_cfg`, and `struct hdmi_phy` describe HDMI PHY variants and resources.
- Inline helpers `hdmi_write/read`, `hdmi_qfprom_read`, `hdmi_phy_write/read` centralize MMIO access.

Control flow: HDMI submodules include this header and collaborate through `struct hdmi`. The top-level driver fills resources, bridge code drives power/timing/infoframes, audio code reads/writes audio fields, DDC/HDCP modules attach through prototypes, and PHY files implement the declared PHY/PLL functions.

State and persistence: persistent state is all in `struct hdmi` and `struct hdmi_phy`. `state_mutex` protects `power_on` and `hpd_enabled`; `reg_lock` protects several shared HDMI registers across interrupt/work/atomic contexts. The header also defines compile-time HDCP and common-clock stubs so callers can use uniform functions when features are disabled.

Dependencies and integration points: includes Linux I2C, clock, platform, regulator, GPIO, HDMI definitions, DRM bridge, MSM driver definitions, and generated `hdmi.xml.h` register definitions. Exposes hooks to ALSA HDMI codec bridge callbacks and DRM bridge HPD/detect flows.

Risks: inline QFPROM read has no NULL guard, so callers must ensure resource availability. The `hdmi_phy` field `cfg` is non-const despite extern const configs, which can invite accidental mutation. Locking rules are documented but not enforced by types. Feature stubs return `-ENODEV` or no-op and must be handled by callers.

Test signals: compile with and without `CONFIG_COMMON_CLK` and `CONFIG_DRM_MSM_HDMI_HDCP`, sparse/lockdep attention around `reg_lock` and `state_mutex`, and cross-module build coverage for HDMI audio, bridge, DDC, HDCP, PHY, and PLL files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_audio.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_audio.c

Purpose: HDMI audio programming for MSM HDMI bridge integration. It validates audio parameters, updates DRM HDMI audio infoframes, computes ACR N/CTS values, and enables or disables HDMI audio packets/registers based on video power state.

Important APIs and functions:
- `msm_hdmi_audio_update()` is the low-level register update path for ACR, VBI, audio packet control, audio config, interrupt enable, and general control packets.
- `msm_hdmi_bridge_audio_prepare()` is the DRM bridge HDMI audio callback; it validates sample rates, updates the connector audio infoframe, stores rate/channels/enabled state, and calls the update path.
- `msm_hdmi_bridge_audio_shutdown()` clears the DRM audio infoframe, resets audio state to disabled stereo defaults, and updates hardware.

Control flow: audio prepare accepts only 32, 44.1, 48, 88.2, 96, 176.4, and 192 kHz. If the connector is not HDMI, `msm_hdmi_audio_update()` rejects with `-EINVAL`. Enabled audio is forced off if video is not powered or `pixclock` is zero. For high sample rates, N is divided and an ACR multiplier is used. The selected ACR bank follows the 32/44.1/48 kHz families, then packets, GC, FIFO watermark, engine enable, and interrupts are programmed.

State and persistence: software state is `hdmi->audio.enabled`, `rate`, and `channels`; hardware state persists in HDMI packet/audio registers until changed. The code reads current packet/config registers before modifying bit fields, preserving unrelated state.

Dependencies and integration points: uses DRM HDMI helpers for ACR calculation and atomic connector infoframe updates, ALSA `hdmi-codec` params, `hdmi.xml.h` register fields, and bridge callbacks wired in `hdmi_bridge.c`.

Risks: audio register writes are not protected by `reg_lock`, so interactions with other register users depend on register separation and atomic callback serialization. Non-HDMI/DVI sinks reject audio update. Audio enable depends on current video state and must be refreshed on video power transitions; bridge pre-enable/post-disable does call update. Unsupported rates return `-EINVAL` before touching state.

Test signals: prepare/shutdown for all supported sample rates, rejection of unsupported rates and DVI sinks, 2-channel versus multichannel layout bit, video-off audio suppression, ACR N/CTS verification for each rate family, and audio update during HDMI bridge power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_bridge.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_bridge.c

Purpose: DRM bridge implementation for the MSM HDMI transmitter. It controls bridge power sequencing, mode timing registers, HDMI infoframes, EDID/DDC access, HPD notification work, TMDS clock validation, PHY powerup/down, HDCP hooks, and HDMI audio bridge callbacks.

Important APIs and functions:
- `msm_hdmi_power_on()` and `power_off()` manage runtime PM and optional external pixel clock.
- `msm_hdmi_bridge_atomic_pre_enable()` programs timings, powers resources, updates audio/infoframes, powers the PHY, enables HDMI core, and starts HDCP.
- `msm_hdmi_bridge_atomic_post_disable()` stops HDCP, disables HDMI core while preserving HPD mode if needed, powers down PHY, updates audio, disables resources, and drops runtime PM.
- `msm_hdmi_set_timings()` writes total, active hsync/vsync, interlace F2, and frame polarity registers.
- clear/write infoframe helpers implement AVI, audio, SPD, and vendor HDMI packets.
- `msm_hdmi_bridge_edid_read()`, `msm_hdmi_bridge_tmds_char_rate_valid()`, `msm_hdmi_hotplug_work()`, and `msm_hdmi_bridge_init()` integrate EDID, mode validation, HPD work, and DRM bridge registration.

Control flow: atomic pre-enable obtains the new connector and CRTC state, stores TMDS char rate in `hdmi->pixclock`, programs timings, powers resources under `state_mutex` if not already on, updates audio if sink is HDMI, asks DRM helpers to update infoframes, powers the PHY with current pixclock, enables the HDMI core, and turns on HDCP. Post-disable reverses this, but `msm_hdmi_set_mode()` is called with `hpd_enabled` to keep the core active enough for HPD if requested. EDID read temporarily sets `HDMI_CTRL_ENABLE` around DDC access and restores the previous control value.

State and persistence: `hdmi->pixclock` persists the current TMDS rate and feeds audio ACR plus PHY/external clock setup. `power_on` and `hpd_enabled` are protected by `state_mutex`. Infoframe register state persists until DRM helper callbacks clear or rewrite it. HPD work queues bridge notifications asynchronously on the HDMI workqueue.

Dependencies and integration points: uses DRM bridge atomic helpers, bridge connector, EDID/DDC helpers, HDMI infoframe state helpers, MSM KMS `round_pixclk`, optional `extp_clk`, HDMI PHY power helpers, HDCP helpers, and audio callbacks in `hdmi_audio.c`.

Risks: power-on ignores the return value of `pm_runtime_resume_and_get()`, so later register/clock operations may proceed after runtime PM failure. Infoframe packing is hardware-specific and length-sensitive. EDID temporarily modifies `REG_HDMI_CTRL` without `reg_lock`, while other paths also touch that register. `power_off()` waits a fixed 20 ms rather than synchronizing to an actual final vblank. TMDS validation demands exact rounded rate equality, which can reject modes if clock providers round slightly.

Test signals: atomic enable/disable on HDMI and DVI sinks, interlaced and polarity flag modes, all infoframe helper paths and invalid lengths, EDID read with HPD on/off, TMDS validation through KMS `round_pixclk` and `extp_clk`, HDCP on/off sequencing, runtime PM failure injection, and hotplug work notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_bridge.c -->
