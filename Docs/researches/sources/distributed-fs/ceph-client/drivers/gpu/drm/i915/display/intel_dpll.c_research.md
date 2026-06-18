# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.c

## Purpose

`intel_dpll.c` contains display PLL clock computation, readback, hook selection, and enable/disable sequencing for legacy and transitional Intel display platforms. It covers pre-shared-DPLL per-pipe PLLs, PCH-era clock computation hooks, VLV/CHV DPIO PLL programming, BXT divider search support, and the top-level `intel_dpll_crtc_compute_clock()` / `intel_dpll_crtc_get_dpll()` dispatch used by atomic modesets.

The file bridges old pipe-owned PLL programming and the newer shared-DPLL manager in `intel_dpll_mgr.c`. Older platforms compute and program pipe-local registers directly. ILK/HSW and newer paths often compute clock state here but reserve shared PLLs through the manager.

## Important APIs, Types, And Functions

`struct intel_dpll_global_funcs` selects per-platform hooks for `crtc_compute_clock` and `crtc_get_dpll`. `intel_dpll_init_clock_hook()` fills `display->funcs.dpll` based on platform generation, DDI availability, PCH split, and special platforms such as DG2, MTL, and Xe3 LPD.

`struct intel_limit` captures divider and clock validity ranges. The file defines many limit tables for i8xx, i9xx, G4x, Pineview, Ironlake/Sandybridge, VLV, CHV, and BXT.

Divider math helpers include `pnv_calc_dpll_params()`, `i9xx_calc_dpll_params()`, `vlv_calc_dpll_params()`, `chv_calc_dpll_params()`, and `bxt_find_best_dpll()`. They populate `struct dpll` fields including feedback multiplier, post divider, VCO, and dot clock.

Readback helpers include `i9xx_dpll_get_hw_state()`, `i9xx_crtc_clock_get()`, `vlv_crtc_clock_get()`, and `chv_crtc_clock_get()`. They decode hardware registers into `struct dpll` and update `crtc_state->port_clock`.

Search helpers include `i9xx_find_best_dpll()`, `pnv_find_best_dpll()`, `g4x_find_best_dpll()`, `vlv_find_best_dpll()`, and `chv_find_best_dpll()`. They apply `intel_pll_is_valid()` and platform-specific preferences such as P divider preference, smaller N, larger M values, and CHV preference for larger P.

Register-state builders include `i9xx_dpll_compute_fp()`, `i9xx_compute_dpll()`, `i8xx_compute_dpll()`, `ilk_compute_dpll()`, `vlv_compute_dpll()`, and `chv_compute_dpll()`.

PLL programming APIs include `i9xx_enable_pll()`, `i9xx_disable_pll()`, `vlv_enable_pll()`, `vlv_disable_pll()`, `chv_enable_pll()`, `chv_disable_pll()`, `vlv_force_pll_on()`, and `vlv_force_pll_off()`. Assertions and utilities include `assert_pll_enabled()`, `assert_pll_disabled()`, and `intel_dpll_clock_matches()`.

## Control Flow And State

Atomic compute starts at `intel_dpll_crtc_compute_clock()`. It clears `crtc_state->dpll_hw_state`, skips disabled CRTCs, and dispatches to the selected global hook. For legacy platforms the hook computes the best divider, fills `crtc_state->dpll` and `crtc_state->dpll_hw_state`, then updates `port_clock` and adjusted CRTC clock. For shared-DPLL platforms the hook usually delegates PLL computation to `intel_dpll_compute()` in the manager.

After compute, `intel_dpll_crtc_get_dpll()` reserves a shared PLL if the platform hook has a `crtc_get_dpll` callback, skipping disabled CRTCs and states that already have `intel_dpll`.

Enable sequences are platform-specific. `i9xx_enable_pll()` writes FP0/FP1, toggles VGA mode around divider changes, waits for stabilization, writes DPLL_MD or rewrites DPLL for old multiplier behavior, and writes the DPLL three times for warmup. `vlv_enable_pll()` first enables refclk without VCO/ext buffer, then prepares DPIO PLL registers and waits for lock if VCO is required. `chv_enable_pll()` writes refclk/SSC without VCO, prepares fractional DPIO PLL state, enables DCLKP, waits, enables PLL, handles DPLL_MD propagation workaround for non-pipe-A, and records `display->state.chv_dpll_md[pipe]`.

Readout reconstructs clock state from register fields. CHV and VLV skip DSI-disabled DPLL paths. CHV reconstructs fixed-point M2 including fractional bits and decodes common-lane p1/p2 fields. VLV reads PLL divider register through sideband DPIO.

Persistent software state includes `crtc_state->dpll`, `crtc_state->dpll_hw_state`, `crtc_state->port_clock`, `crtc_state->hw.adjusted_mode.crtc_clock`, and CHV's `display->state.chv_dpll_md[]` cache for pipes whose DPLL_MD cannot be read directly.

## Dependencies And Integration Points

This file depends on register definitions and display state types, VLV/CHV DPIO helpers from `intel_dpio_phy.h`, sideband access from `vlv_sideband.h`, panel/LVDS helpers for SSC and dual-link decisions, PPS assertions, and newer PHY helpers for DG2/MTL/Xe3 hook selection.

It integrates with `intel_dpll_mgr.c` through `intel_dpll_compute()` and `intel_dpll_reserve()` for shared PLL platforms. It integrates with encoder code through `intel_crtc_has_type()`, `intel_crtc_has_dp_encoder()`, `intel_crtc_dotclock()`, and platform-specific enable/disable calls during modeset.

## Risks And Edge Cases

Clock search is highly platform-specific. Divider limits, refclk values, LVDS SSC frequencies, dual-link LVDS assumptions, and DSI exceptions all affect validity. Small changes can cause modeset failures or off-by-one clock mismatches.

VLV/CHV programming relies on DPIO sideband access ordering and lock polling. CHV has special handling for DPLLCMD absence, VGA mode expectations on DPLLB, fractional M2, and cached DPLL_MD. BXT reuses CHV-style fixed-point divider search through `bxt_find_best_dpll()`.

The hook-selection order matters. Newer platforms may use shared manager paths or external PHY code; selecting the wrong hook would either skip required reservation or run legacy register programming.

## Test Signals

Test signals include successful atomic modesets across legacy VGA/LVDS/SDVO/HDMI/DP outputs, clock readback matching requested port clocks within `intel_dpll_clock_matches()`, absence of `Couldn't calculate DPLL settings` and PLL lock errors, suspend/resume readout consistency, and platform-specific coverage for LVDS SSC, DSI no-DPLL paths, VLV/CHV sideband paths, and shared-DPLL reservation paths.
