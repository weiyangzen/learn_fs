# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.c

## Purpose

`intel_cdclk.c` is the i915 display core clock coordinator. It reads, computes, validates, and programs CDCLK and RAWCLK across many Intel display generations. CDCLK clocks most display pipe logic, so this file enforces minimum clock requirements from pixel rate, planes, DBUF bandwidth, FBC, IPS, audio, DSI, and DSC; chooses a legal platform clock; decides whether the transition can happen live or requires modeset; then sequences hardware programming with PCode, PLL, divider, squash/crawl, AUX, PSR, audio, and DBUF/MDCLK interactions.

## Important APIs, Types, And Functions

The private `struct intel_cdclk_state` embeds `struct intel_global_state` and stores `logical` and `actual` `struct intel_cdclk_config` values, DBUF bandwidth minimum, per-pipe minimum CDCLK and voltage level, pipe selected for synchronized cd2x updates, forced minimum CDCLK, enabled/active pipe masks, and a `disable_pipes` flag. `struct intel_cdclk_funcs` is the platform vtable for `get_cdclk`, `set_cdclk`, `modeset_calc_cdclk`, and optional voltage calculation. `struct intel_cdclk_vals` is the table row for modern CDCLK tables: CDCLK, refclk, squash waveform, and PLL ratio.

External APIs include hardware lifecycle (`intel_cdclk_init_hw()`, `intel_cdclk_uninit_hw()`), hook setup (`intel_init_cdclk_hooks()`), capability/readout (`intel_update_max_cdclk()`, `intel_update_cdclk()`, `intel_read_rawclk()`, `intel_cdclk_read_hw()`), atomic validation (`intel_cdclk_atomic_check()`, `intel_cdclk_state_set_joined_mbus()`, `intel_cdclk_update_dbuf_bw_min_cdclk()`), commit programming (`intel_set_cdclk_pre_plane_update()`, `intel_set_cdclk_post_plane_update()`), state accessors (`intel_atomic_get_cdclk_state()`, `intel_cdclk_logical()`, `intel_cdclk_actual()`, `intel_cdclk_actual_voltage_level()`, `intel_cdclk_min_cdclk()`), PM Demand detection (`intel_cdclk_pmdemand_needs_update()`), and prefill helpers (`intel_cdclk_prefill_adjustment*()`, `intel_cdclk_min_cdclk_for_prefill()`).

Major internal families are legacy fixed/readout functions for i8xx through Haswell/Broadwell, VLV/CHV PUnit/CCK programming, SKL DPLL0 and CDCLK_CTL programming, and BXT+ DE PLL programming. BXT+ includes CDCLK tables for BXT, GLK, ICL, RKL, ADLP, RPLU, DG2, MTL, Xe2LPD/HPD, Xe3LPD, and Xe3P LPD, plus crawl/squash and MDCLK source handling.

## Control Flow

`intel_init_cdclk_hooks()` selects the CDCLK vtable and table based on display version, platform flags, and workarounds. Early hardware init calls `intel_cdclk_init_hw()`, which sanitizes pre-OS CDCLK state and programs a valid initial clock for display version 9 or BXT+ style platforms. `intel_cdclk_read_hw()` reads hardware into both logical and actual global state.

During atomic validation, `intel_cdclk_atomic_check()` updates enabled/active pipe masks, per-CRTC minimum CDCLK, per-CRTC voltage levels, DBUF bandwidth minimums, and forced minimum changes. If anything requires recalculation, `intel_modeset_calc_cdclk()` calls the platform `modeset_calc_cdclk()` function. The generic minimum computation takes the max of forced CDCLK, DBUF bandwidth, per-pipe minima, and GLK audio workaround. Platform calculators then pick the next legal CDCLK and voltage from fixed formulas or CDCLK tables; if no pipes are active they may use a lower `actual` clock while keeping `logical` high enough for enabled CRTCs.

After computing, `intel_modeset_calc_cdclk()` decides the transition method. It serializes the global state if hardware programming or DG2 PCode pipe-count notification is needed. It can use cd2x divider updates synchronized to a single active pipe, PLL crawl, squash, or crawl plus squash without disabling all pipes. If none of those paths fits and the clock changes, it requests a late modeset of all pipes and sets `disable_pipes`.

At commit time, `intel_set_cdclk_pre_plane_update()` handles increases before plane updates, keeps the higher voltage level when needed, and preserves the old joined-MBUS value until DBUF MBUS sequencing updates it. `intel_set_cdclk_post_plane_update()` handles decreases after plane updates. `intel_set_cdclk()` pauses PSR, notifies audio pre/post, locks GMBUS and all DP AUX hardware mutexes, calls the platform `set_cdclk()`, resumes PSR, and verifies readback state. DG2 has explicit pre/post PCode notifications for voltage, CDCLK, and active-pipe power well count.

## State And Persistence

The persistent software state is the global object `display->cdclk.obj`; hardware readout also lives in `display->cdclk.hw`. The logical clock is used for calculations as if enabled CRTCs are active, while the actual clock may be lower when all CRTCs are DPMS-off. Capability state includes `display->cdclk.table`, `max_cdclk_freq`, `max_dotclk_freq`, and SKL preferred VCO. Hardware state includes LCPLL/DPLL0 or DE PLL enable/ratio/lock, CDCLK_CTL divider/decimal/pipe fields, CDCLK squash waveform, MDCLK source and ratio, PUnit/PCode voltage state, GMBUS frequency on VLV/CHV, and RAWCLK programming on PCH families.

## Dependencies And Integration Points

The file integrates with almost every display resource manager: atomic global state, CRTC state, DBUF bandwidth and MDCLK ratio, watermark/prefill math, plane minimum CDCLK, FBC, IPS, audio, PSR, DSI, DSC, display workarounds, PCode, sideband/PUnit, uncore/MMIO register access, PCI config, debugfs, and PCH/platform detection. `intel_cdclk.h` is the public contract, while `intel_display_core.h` stores the selected function table and hardware/cache fields.

## Risks

CDCLK transitions are high risk because mistakes cause underruns, hangs, AUX/GMBUS corruption, or power-management mismatches. Risks include wrong platform table selection, stale pre-OS CDCLK state, invalid PLL VCO or refclk readout, voltage level underestimation, missing serialization for nonblocking commits, incorrect live-transition classification, improper ordering between CDCLK, DBUF/MDCLK joining, and plane updates, and PCode timeout/error handling. Many paths use workarounds keyed by platform/display version; extending tables for new hardware must preserve those conditions. RAWCLK programming affects AUX/backlight timing and can break unrelated display blocks if wrong.

## Test Signals

Test signals include boot logs from CDCLK sanitize/readout, debugfs `i915_cdclk_info`, atomic commits that raise and lower CDCLK, single-pipe live cd2x transitions, crawl/squash transitions, all-pipe modeset-required transitions, DPMS-off actual/logical divergence, DG2 PCode notifications on pipe count and CDCLK changes, GLK multi-pipe audio workaround, DBUF bandwidth-driven minimum changes, and max dotclock validation. Hardware tests should include AUX/GMBUS traffic during CDCLK changes, PSR pause/resume behavior, underrun detection, suspend/resume with BIOS-programmed CDCLK, and RAWCLK-dependent features.
