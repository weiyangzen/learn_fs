# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.c

Purpose: initializes and controls PCH reference clocks for IBX/CPT and LPT platforms, including LPT iCLKIP programming, CLKOUT_DP enable/disable, SSC source decisions, and Haswell FDI mPHY programming workaround.

Important functions/types: `struct iclkip_params` captures divisor/phase settings. Public APIs are `lpt_program_iclkip()`, `lpt_disable_iclkip()`, `lpt_get_iclkip()`, `lpt_iclkip()`, `lpt_disable_clkout_dp()`, and `intel_init_pch_refclk()`. Important helpers include `lpt_compute_iclkip()`, `lpt_enable_clkout_dp()`, `lpt_bend_clkout_dp()`, `spll_uses_pch_ssc()`, `wrpll_uses_pch_ssc()`, `lpt_init_pch_refclk()`, and `ilk_init_pch_refclk()`.

Control flow: LPT iCLKIP programming disables the clock, computes divisors from adjusted mode clock, writes SBI ICLK divider/phase/auxdiv/control registers under SBI lock, waits 24 us, then ungates pixel clock. LPT refclk init checks whether SPLL/WRPLLs already use PCH SSC; if so it preserves it, otherwise enables CLKOUT_DP with FDI if analog output exists or disables it. ILK/CPT init inspects encoders for LVDS/eDP/panel, checks active DPLLs using SSC, computes final `PCH_DREF_CONTROL`, and transitions nonspread/SSC/CPU outputs with required delays.

State and persistence: writes SBI ICLK/MPHY registers, `PIXCLK_GATE`, `PCH_DREF_CONTROL`, and tracks `display->dpll.pch_ssc_use` bitmask. It may leave PCH SSC enabled to avoid disrupting active PLL users.

Dependencies/integration: uses encoder list, panel SSC policy, platform/PCH macros, DPLL lists, SBI lock/read/write, display MMIO, and PCH display LPT paths.

Risks/test signals: reference clock transitions are timing-sensitive and platform-specific. Test LPT-H vs LPT-LP, analog FDI present/absent, CPU eDP/LVDS panel SSC choices, CK505 systems, active PLLs already using PCH SSC, runtime suspend/resume, and exact iCLKIP frequency readback. Watch WARNs for FDI without spread, invalid clock divisors, and LP PCH FDI assumptions.
