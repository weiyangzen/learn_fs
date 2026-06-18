# subset-b-003592 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.c

## Purpose

`intel_dpio_phy.c` programs the DPIO display PHY blocks used by Intel Valleyview, Cherryview, Broxton, and Geminilake display outputs. These PHYs back DP/HDMI/DDI ports and are partly controlled through platform display MMIO registers and partly through VLV/CHV IOSF sideband DPIO register accesses. The file owns port-to-PHY/channel mapping, PHY power/reset sequencing, signal swing/de-emphasis programming, lane reset/latency programming, and state verification for the DPIO-specific display hardware.

The implementation is split into two families. The BXT/GLK path uses MMIO-style `intel_de_*()` accessors and tables describing DPIO PHY topology. The VLV/CHV path uses `vlv_dpio_get()`, `vlv_dpio_read()`, `vlv_dpio_write()`, and `vlv_dpio_put()` to access sideband DPIO registers, with separate helpers for common lanes, PCS blocks, and TX lanes.

## Important APIs, Types, And Functions

`struct bxt_dpio_phy_info` is the local topology table type. It records whether a PHY is dual-channel, which other PHY supplies RCOMP/GRC calibration, reset delay, display power-on mask, and the port mapped to each channel. `bxt_dpio_phy_info[]` maps BXT PHY0 to ports B/C and PHY1 to port A. `glk_dpio_phy_info[]` maps GLK PHY0/1/2 to ports B/A/C and adds reset delays and different power-on masks.

`bxt_port_to_phy_channel()` is the main BXT/GLK mapping function. It scans the selected topology table and returns `enum dpio_phy` plus `enum dpio_channel`, warning and falling back to PHY0/CH0 on unexpected ports.

`bxt_dpio_phy_init()`, `_bxt_dpio_phy_init()`, `bxt_dpio_phy_uninit()`, `bxt_dpio_phy_is_enabled()`, and `bxt_dpio_phy_verify_state()` manage BXT/GLK PHY lifecycle. Initialization powers the PHY through `BXT_P_CR_GT_DISP_PWRON`, waits for `PHY_POWER_GOOD` and reserved-bit accessibility, writes RCOMP offsets, power-gating bits, optional copied GRC calibration, optional delay, and releases common reset through `COMMON_RESET_DIS`. Verification rereads the same fields and uses `display->state.bxt_phy_grc` for copied calibration checks.

`bxt_dpio_phy_set_signal_levels()` uses the encoder buffer translation table from `encoder->get_buf_trans()` and per-lane `intel_ddi_level()` values to program BXT margin, unique transition scale, scaling compensation, and de-emphasis. It toggles PCS swing calculation bits before and after writing TX lane fields.

`bxt_dpio_phy_calc_lane_lat_optim_mask()`, `bxt_dpio_phy_set_lane_optim_mask()`, and `bxt_dpio_phy_get_lane_lat_optim_mask()` compute and program the per-lane latency optimization bit used by BXT and related CHV terminology.

`vlv_dig_port_to_channel()`, `vlv_dig_port_to_phy()`, `vlv_pipe_to_phy()`, and `vlv_pipe_to_channel()` are VLV/CHV mapping helpers. They encode the hardware distinction that ports map to PCS/TX channels while pipes map to common-lane PLL resources.

`chv_set_phy_signal_level()`, `chv_data_lane_soft_reset()`, `chv_phy_pre_pll_enable()`, `chv_phy_pre_encoder_enable()`, `chv_phy_release_cl2_override()`, and `chv_phy_post_pll_disable()` implement Cherryview lane programming and sequencing. They cover swing/de-emphasis setup, data lane reset assertion/deassertion, clock distribution, used-clock-channel selection, latency programming, lane stagger programming, CL2 override cleanup, and post-disable clock distribution cleanup.

`vlv_set_phy_signal_level()`, `vlv_phy_pre_pll_enable()`, `vlv_phy_pre_encoder_enable()`, `vlv_phy_reset_lanes()`, and `vlv_wait_port_ready()` implement the older Valleyview path, including group-register signal writes, reset defaults, skew workarounds, used-clock-channel programming, and polling port-ready status.

## Control Flow And State

The BXT/GLK enable path starts with platform topology lookup. If a PHY depends on another PHY's RCOMP calibration, `bxt_dpio_phy_init()` temporarily powers the RCOMP source if needed, initializes the requested PHY, then powers the source back down if it was not originally enabled. `_bxt_dpio_phy_init()` first checks whether the PHY is already enabled and valid. If enabled but verification fails, it reprograms it. This gives the boot/readout path a chance to preserve correct firmware state while repairing invalid register state.

Signal-level programming is invoked after the encoder/CRTC state has a lane count and train-set levels. The function clears PCS swing calculation, writes per-lane TX fields for every active lane, checks for the invalid `UNIQUE_TRANGE_EN_METHOD` plus disabled scaling combination, writes de-emphasis, and restarts swing calculation.

The CHV pre-PLL path asserts soft reset, powers down unused lanes, may force CL2 alive when channel/pipe crossing needs access to the second common lane, sets left/right clock distribution, sets PCS used-clock-channel override based on pipe B or non-B, and writes common-lane used-clock-channel state. The pre-encoder path then lets hardware manage TX FIFO reset source, writes latency optimization and lane stagger values based on port clock and lane count, and deasserts soft reset. Post-disable undoes clock distribution and leaves at least one lane not explicitly powered down so later channel power gating can work.

The VLV sequence is similar but simpler: pre-PLL writes lane reset defaults and skew workaround constants; pre-encoder selects the clock channel and lane clock registers; reset-lanes writes reset values when disabling; `vlv_wait_port_ready()` polls the appropriate DPLL or PHY status register for the selected port.

Persistent state is minimal and hardware-facing. The file writes register state and stores copied BXT GRC calibration in `display->state.bxt_phy_grc`. CHV additionally stores `dig_port->release_cl2_override` so a temporary CL2 powergate override can be released later.

## Dependencies And Integration Points

This file integrates with the i915 display encoder and modeset pipeline through `struct intel_encoder`, `struct intel_crtc_state`, and `struct intel_digital_port`. It relies on DDI buffer translation (`intel_ddi_buf_trans.h`), DP lane count helpers (`intel_dp_unused_lane_mask()`), display power-domain locking, BXT and VLV DPIO register definitions, and sideband access wrappers from `vlv_sideband.h`.

It is closely coupled to `intel_dpll.c` and `intel_dpll_mgr.c`: DPIO PHY setup must match PLL routing, channel selection, and port clock programming. The BXT PLL manager also calls `bxt_port_to_phy_channel()` to program port PLL registers. CHV/VLV PLL code uses the VLV pipe-to-PHY/channel helpers to read and write PLL registers.

## Risks And Edge Cases

The register sequences are timing-sensitive. BXT power-on waits for reserved bits to become readable and for power-good, while GRC calibration waits only 10 ms. Short or reordered waits can lead to inaccessible registers or unstable PHY state.

The BXT RCOMP dependency is easy to break: PHYs without their own resistor copy calibration from another PHY, and verification depends on `display->state.bxt_phy_grc` being read or written consistently. A bad fallback PHY/channel mapping can program the wrong port's PLL or lanes.

CHV channel/pipe crossing is fragile because the common lane normally follows the pipe but PCS/TX follows the port. The CL2 override path is a known special case and must be released exactly once. Lane count branches mean two-lane and four-lane modes program different PCS blocks.

The code contains hardware-workaround constants and comments noting unclear documentation, especially around unique transition scale selection and VLV/CHV skew/clock fields. These should be treated as behavioral requirements rather than cleaned up casually.

## Test Signals

Useful validation comes from modeset tests on BXT/GLK/VLV/CHV hardware or emulation that exercise HDMI and DP on all DPIO ports, one/two/four-lane DP, pipe/port crossing on VLV/CHV, suspend/resume state readout, and repeated enable/disable cycles. Kernel log signals include DDI PHY state mismatch messages, GRC timeout, PHY power-on timeout, port-ready timeout, PLL lock failures from adjacent PLL code, and warnings for unexpected ports or lane counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.h

## Purpose

`intel_dpio_phy.h` declares the DPIO PHY interface used by i915 display code. It exposes the PHY/channel enums and the platform-specific helpers implemented in `intel_dpio_phy.c` for BXT/GLK, VLV, and CHV display PHY programming. The header also provides no-op/static-inline fallbacks when the file is included without `I915`, allowing non-i915 build contexts to compile without pulling in DPIO implementation details.

## Important APIs And Types

`enum dpio_channel` defines `DPIO_CH0` and `DPIO_CH1`, matching the two possible channels inside dual-channel DPIO PHYs. `enum dpio_phy` defines `DPIO_PHY0`, `DPIO_PHY1`, and `DPIO_PHY2`, covering VLV/CHV/BXT/GLK mappings.

The BXT/GLK API includes `bxt_port_to_phy_channel()`, `bxt_dpio_phy_set_signal_levels()`, `bxt_dpio_phy_init()`, `bxt_dpio_phy_uninit()`, `bxt_dpio_phy_is_enabled()`, `bxt_dpio_phy_verify_state()`, `bxt_dpio_phy_calc_lane_lat_optim_mask()`, `bxt_dpio_phy_set_lane_optim_mask()`, and `bxt_dpio_phy_get_lane_lat_optim_mask()`.

The VLV/CHV mapping API includes `vlv_dig_port_to_channel()`, `vlv_dig_port_to_phy()`, `vlv_pipe_to_phy()`, and `vlv_pipe_to_channel()`.

The CHV API includes `chv_set_phy_signal_level()`, `chv_data_lane_soft_reset()`, `chv_phy_pre_pll_enable()`, `chv_phy_pre_encoder_enable()`, `chv_phy_release_cl2_override()`, and `chv_phy_post_pll_disable()`.

The VLV API includes `vlv_set_phy_signal_level()`, `vlv_phy_pre_pll_enable()`, `vlv_phy_pre_encoder_enable()`, `vlv_phy_reset_lanes()`, and `vlv_wait_port_ready()`.

## Control Flow And State

The header itself does not own runtime state. Its declarations are called by display modeset, encoder enable/disable, and PLL setup code. In `#ifdef I915` builds the declarations bind to the full implementation. In the fallback branch, all mutating operations become empty functions, status queries return safe defaults (`false` for enabled, `true` for verify), and mapping functions return PHY0/CH0.

The fallback behavior is intentionally compile-oriented, not hardware-functional. It prevents unresolved symbols in non-i915 contexts but does not represent usable DPIO operation.

## Dependencies And Integration Points

The header forward-declares `enum pipe`, `enum port`, `struct intel_crtc_state`, `struct intel_digital_port`, `struct intel_display`, and `struct intel_encoder` to avoid heavy includes. It includes only `<linux/types.h>` for fixed-width integer and boolean type availability.

The declarations are consumed by display PLL code, DDI/DP encoder enable paths, VLV/CHV power-gating code, and BXT PLL manager code. Because the enums are used across multiple files, changes to the enum ordering would affect register macro indexing and platform mapping logic.

## Risks And Edge Cases

The biggest header-level risk is semantic mismatch between fallback stubs and real implementation. A non-i915 build can compile but will silently skip all PHY programming. Another risk is adding new ports/PHYs without extending both the enum and implementation tables. Function signatures carry platform assumptions such as lane count, port clock, and `intel_crtc_state` contents; callers must compute these before invoking the PHY helpers.

## Test Signals

Build coverage should include both `I915` and non-`I915` include contexts. Runtime validation is indirect: successful modesets on VLV/CHV/BXT/GLK, absence of missing-case warnings in mapping helpers, and matching PHY state verification all confirm that callers and declarations stay aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.h

## Purpose

`intel_dpll.h` declares the display PLL interface implemented primarily by `intel_dpll.c` and used by modeset, encoder, CRTC, and shared-DPLL manager code. It exposes clock computation, hardware-state readback, divider math, VLV/CHV/BXT helpers, per-platform enable/disable calls, assertions, and simple clock comparison.

## Important APIs

Top-level atomic hooks are `intel_dpll_init_clock_hook()`, `intel_dpll_crtc_compute_clock()`, and `intel_dpll_crtc_get_dpll()`. These initialize platform hook selection, compute CRTC PLL state, and reserve shared DPLLs where needed.

Divider and hardware-state helpers are `i9xx_calc_dpll_params()`, `i9xx_dpll_compute_fp()`, `i9xx_dpll_get_hw_state()`, `vlv_compute_dpll()`, `chv_compute_dpll()`, `bxt_find_best_dpll()`, and `chv_calc_dpll_params()`.

PLL force and lifecycle APIs are `vlv_force_pll_on()`, `vlv_force_pll_off()`, `chv_enable_pll()`, `chv_disable_pll()`, `vlv_enable_pll()`, `vlv_disable_pll()`, `i9xx_enable_pll()`, and `i9xx_disable_pll()`.

Clock readback APIs are `i9xx_crtc_clock_get()`, `vlv_crtc_clock_get()`, and `chv_crtc_clock_get()`.

State checking helpers are `assert_pll_enabled()`, `assert_pll_disabled()`, and `intel_dpll_clock_matches()`.

## Control Flow And State

The header does not store state, but its function set defines the order used by the display pipeline: initialize hooks at display setup, compute CRTC PLL state during atomic check, optionally reserve a shared DPLL, enable the relevant PLL during modeset, read back hardware state during get-config/sanitize, and disable or force-off during teardown.

Functions operate on `struct intel_crtc_state`, `struct intel_atomic_state`, `struct intel_display`, `struct intel_crtc`, `struct dpll`, and `struct intel_dpll_hw_state`. Those structures carry all persistent state; this header only connects users to the implementation.

## Dependencies And Integration Points

The header includes `<linux/types.h>` and forward-declares the display types needed by prototypes. It is included by shared DPLL management, display modeset code, and DPIO PHY code. Because it exposes legacy and modern paths together, it is a compatibility boundary between old pipe PLL programming and newer port/shared PLL management.

## Risks And Edge Cases

The declarations mix platform-specific functions with top-level generic hooks. Callers must know which functions are legal for a platform; for example VLV/CHV force PLL helpers are not generic DPLL APIs. Adding or changing hardware-state structs requires matching all prototypes that consume `struct intel_dpll_hw_state`.

## Test Signals

Build coverage is the primary header-level signal. Runtime validation comes from the implementation callers: successful atomic check/commit flows, correct PLL lock/readback, and no unresolved or mismatched function declarations when platform code is compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.c

## Purpose

`intel_dpll_mgr.c` implements the shared display PLL abstraction for i915 display platforms. It initializes platform PLL inventories, computes hardware states, reserves compatible PLLs in atomic state, tracks pipe users, enables and disables PLLs under lock, reads and sanitizes hardware state, dumps and compares PLL state, and verifies software tracking against hardware after commits.

The manager covers multiple hardware generations: IBX/CPT PCH PLLs, HSW/BDW WRPLL/SPLL/LCPLL, SKL/KBL DPLLs, BXT/GLK port PLLs, ICL/TGL/DG1/ADL combo and Type-C PLLs, MTL C10/C20/CX0 PLLs, and Xe3 LPD LT PHY PLLs. It hides those differences behind `struct intel_dpll_mgr` and `struct intel_dpll_funcs`.

## Important APIs, Types, And Functions

`struct intel_dpll_funcs` is the per-PLL operation table: `enable`, `disable`, `get_hw_state`, and `get_freq`. `struct intel_dpll_mgr` is the per-platform manager table: PLL inventory plus callbacks for compute, reserve, release, active-DPLL update, refclk update, dump, and compare.

Atomic state helpers include `intel_atomic_duplicate_dpll_state()`, `intel_atomic_get_dpll_state()`, `intel_reference_dpll()`, `intel_unreference_dpll()`, `intel_put_dpll()`, `icl_put_dplls()`, and `intel_dpll_swap_state()`. They stage `struct intel_dpll_state` changes in the atomic state and swap them into `pll->state` during commit.

Core public APIs include `intel_dpll_init()`, `intel_dpll_compute()`, `intel_dpll_reserve()`, `intel_dpll_release()`, `intel_dpll_update_active()`, `intel_dpll_enable()`, `intel_dpll_disable()`, `intel_dpll_get_freq()`, `intel_dpll_get_hw_state()`, `intel_dpll_update_ref_clks()`, `intel_dpll_readout_hw_state()`, `intel_dpll_sanitize_state()`, `intel_dpll_dump_hw_state()`, `intel_dpll_compare_hw_state()`, `intel_dpll_state_verify()`, and `intel_dpll_verify_disabled()`.

PLL selection is centered on `intel_find_dpll()`. It receives a desired hardware state and an allowed DPLL bitmask, prefers an already-referenced PLL with matching state for sharing, otherwise remembers the first unused PLL, and returns `NULL` when no compatible or free PLL exists.

Generation-specific blocks define inventories and operations:

- PCH: `ibx_pch_dpll_*()`, `pch_plls`, `pch_pll_mgr`.
- HSW: WRPLL/SPLL/LCPLL calculation and get/reserve paths, including `hsw_ddi_calculate_wrpll()`.
- SKL: `skl_ddi_calculate_wrpll()`, CFGCR programming, DP link-rate state, and SKL DPLL inventory.
- BXT: `bxt_ddi_pll_enable()`, `bxt_ddi_pll_get_hw_state()`, DP fixed divider table, HDMI divider calculation through `bxt_find_best_dpll()`, and port-to-PLL 1:1 reservation.
- ICL/TGL/ADL: combo PLL and MG/DKL Type-C PLL calculators, TBT PLL state, combo/TC reservation, active-DPLL switching, enable/disable/readback functions, and platform inventories.
- MTL/Xe3: wrappers around `intel_cx0pll_*()` and `intel_lt_phy_*()` helpers, with TBT PLLs marked always-on and alternate-port handling retained.

## Control Flow And State

Initialization starts in `intel_dpll_init()`, which initializes `display->dpll.lock`, chooses a manager based on platform, fills `display->dpll.dplls[]` from the selected `dpll_info` table, stores indexes, and records `display->dpll.mgr` plus `num_dpll`. DG2 explicitly has no shared DPLL manager because port PLLs are part of the PHY.

During atomic check, `intel_dpll_compute()` dispatches to the manager's compute callback. The callback fills `crtc_state->dpll_hw_state` or `crtc_state->icl_port_dplls[]` with the desired state and updates `port_clock` from the get-frequency function when needed. `intel_dpll_reserve()` then dispatches to the manager's get callback, which calls `intel_find_dpll()` with a generation-specific allowed mask. Successful reservation stages a pipe reference in atomic DPLL state and stores the selected `struct intel_dpll *` in `crtc_state->intel_dpll`.

ICL and newer Type-C flows may reserve two PLLs: a default TBT PLL and an MG/TC/CX0/LT PHY PLL. `icl_update_active_dpll()` selects which one is active based on current Type-C mode, and `icl_set_active_port_dpll()` copies the selected port-DPLL state into `crtc_state->intel_dpll` and `crtc_state->dpll_hw_state`.

During commit, `intel_dpll_enable()` marks the CRTC's joined pipe mask active under `display->dpll.lock`. If the PLL has no prior active users, it gets an optional power-domain wakeref and calls the PLL's enable callback. `intel_dpll_disable()` removes the active pipe mask and disables/releases the power domain only when no active users remain.

Readout and sanitize run outside atomic compute. `intel_dpll_readout_hw_state()` reads every PLL's hardware state, records `pll->on`, gets wakerefs for powered PLLs with power domains, reconstructs `pipe_mask` from active CRTC states, and initializes `active_mask`. `intel_dpll_sanitize_state()` disables PLLs that are on but unused, while preserving active or always-on behavior.

Verification uses `verify_single_dpll_state()` to compare software `on`, `active_mask`, `pipe_mask`, and stored hardware state against fresh readback. It has special handling for always-on PLLs and LT PHY comparisons. `intel_dpll_state_verify()` checks new and old PLLs around a CRTC transition, including alternate-port DPLL cases for TC ports.

Persistent state includes `display->dpll.dplls[]`, each `pll->state.hw_state`, `pll->state.pipe_mask`, `pll->active_mask`, `pll->on`, `pll->wakeref`, staged `state->dpll_state[]`, `state->dpll_set`, platform ref clocks in `display->dpll.ref_clks`, and ICL+ per-CRTC port-DPLL selections.

## Dependencies And Integration Points

The manager depends on display register access (`intel_de_*()`), display power domains, atomic CRTC state, encoder type helpers, HTI DPLL masks, PCH refclk setup, DPIO PHY mapping for BXT, DKL PHY access, Type-C mode helpers, CX0 PHY helpers, LT PHY helpers, and platform stepping/workaround helpers.

It integrates upward with `intel_dpll.c`, which calls `intel_dpll_compute()` and `intel_dpll_reserve()` from platform clock hooks. It integrates sideways with encoder/PHY code that calculates port clocks and Type-C mode, and downward with low-level register definitions for every platform generation.

## Risks And Edge Cases

Shared PLL correctness depends on exact hardware-state comparison. A missing field in a compare function can share incompatible PLL states; an extra unstable readback field can prevent sharing or trigger false mismatch warnings. The ICL compare function explicitly notes a FIXME to split combo versus MG state more thoroughly.

Atomic reference tracking is sensitive to ordering. `intel_atomic_get_dpll_state()` requires the connection mutex, staged state must be swapped exactly once, and release paths differ between single-PLL and ICL multi-port-DPLL reservations. Failing to unreference the TBT PLL on MG reservation failure would leak a staged reference, so the error path explicitly unwinds it.

Power and lock sequencing is hardware-sensitive. Many enable paths have short waits for power state and lock bits. Some PLLs require power-domain wakerefs, some are always-on, and some have no-op enable/disable because the clock is fixed or owned elsewhere.

Platform selection and masks are dense. HTI can reserve DPLLs, DG1 splits masks by port group, EHL/JSL/RKL expose DPLL4 quirks, ADL-P has a CMTG clock-gating workaround tied to DPLL0, and MTL/Xe3 map ports to PLL IDs via encoder lookup. Wrong masks can allocate a PLL that cannot physically drive the port.

## Test Signals

High-value test signals include atomic modeset coverage with multiple CRTCs sharing and not sharing PLLs, Type-C DP-alt and legacy-mode transitions, MST using primary-port DPLL decisions, suspend/resume readout and sanitize, hotplug across combo and TC ports, forced HTI-reserved DPLL masks, and fastset checks where old active DPLL selection matters. Kernel logs to watch include DPLL allocation failures, PLL lock/power timeout messages, software/hardware state mismatch dumps, active-mask and pipe-mask verification warnings, and unexpected missing-case warnings for port, refclk, divider, or platform selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.c -->
