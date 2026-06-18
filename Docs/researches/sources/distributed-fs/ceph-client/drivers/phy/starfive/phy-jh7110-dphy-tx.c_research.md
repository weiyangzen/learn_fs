# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-tx.c

Purpose: StarFive JH7110 MIPI D-PHY TX provider for DSI transmit, with a large bitrate-to-register timing table and PLL programming.

Important APIs, types, and functions: `reg_configs[]` maps aligned bitrates to PLL feedback and HS timing fields. `stf_dphy_get_config_index()` finds an exact bitrate entry, defaulting to index 0. `stf_dphy_configure()` rounds requested `hs_clk_rate` to 10 MHz, selects a table row, programs ref clock, termination, lane swap, PLL, and HS timing registers. `stf_dphy_hw_reset()` toggles reset and polls PLL lock. Ops include power, init/exit, configure, and validate.

Control flow: probe maps top syscfg, enables runtime PM, obtains `txesc` clock and `sys` reset, creates PHY, and registers simple xlate. Power-on/off only manage runtime PM. Init asserts hardware reset, writes ready/pre-zero defaults, enables txesc clock, and deasserts sys reset. Exit asserts sys reset, disables txesc, and clears hardware reset. Configure can be called with MIPI D-PHY options to program PLL/timing before or around init depending on consumer sequence.

State and persistence: current `phy_configure_opts_mipi_dphy config` field exists but is not used as a cache. Hardware timing state persists in top syscfg registers. Lane map is match-data constant.

Dependencies and integration points: generic MIPI D-PHY framework, DSI bridge/display consumers, PM runtime, clock/reset.

Risks: if bitrate is not exactly in the table after 10 MHz alignment, index 0 is used silently, likely misconfiguring many rates. `stf_dphy_hw_reset()` logs "PLL Locked" on timeout textually ambiguous. If reset deassert fails after txesc enable, the clock is not disabled in that error path.

Test signals: DSI panel modes across bitrate table, validation of unsupported bitrates, PLL lock timeout behavior, init error-path clock balance, and lane swap readback.
