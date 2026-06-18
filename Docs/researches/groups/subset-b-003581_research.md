# subset-b-003581 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.c

## Purpose

`intel_bw.c` implements i915 display memory bandwidth accounting and SAGV/QGV policy. It reads platform DRAM/QGV/PSF capabilities, derives per-plane-count bandwidth tables, tracks aggregate per-pipe display bandwidth in a global atomic object, and programs or prepares the QGV restrictions needed to keep the selected display configuration within memory bandwidth and latency limits.

## Important APIs, Types, And Functions

The private `struct intel_bw_state` is the persistent global state for display bandwidth. It embeds `struct intel_global_state` and stores `pipe_sagv_reject`, `active_pipes`, `qgv_point_peakbw`, `qgv_points_mask`, per-pipe `data_rate[]`, and per-pipe `num_active_planes[]`. `struct intel_qgv_point`, `struct intel_psf_gv_point`, and `struct intel_qgv_info` hold memory-subsystem timing and point data read from PCode, MCHBAR, or uncore registers. `struct intel_sa_info` holds platform system-agent constants used by the bandwidth formulas.

Initialization APIs are `intel_bw_init()` for global object allocation and initial SAGV disable on display versions 11 through 13, and `intel_bw_init_hw()` for reading DRAM information and populating `display->bw.max[]` using platform-specific formulas. Atomic helpers include `intel_atomic_get_old_bw_state()`, `intel_atomic_get_new_bw_state()`, `intel_atomic_get_bw_state()`, and `to_intel_bw_state()`. The main validation entry point is `intel_bw_atomic_check()`. Commit-time sequencing uses `icl_sagv_pre_plane_update()` and `icl_sagv_post_plane_update()`. State readback/update helpers are `intel_bw_update_hw_state()` and `intel_bw_crtc_disable_noatomic()`. PM demand integration uses `intel_bw_pmdemand_needs_update()`, `intel_bw_qgv_point_peakbw()`, and `intel_bw_can_enable_sagv()`.

The platform data paths are split by generation. `dg1_mchbar_read_qgv_point_info()`, `icl_pcode_read_qgv_point_info()`, and `mtl_read_qgv_point_info()` read QGV timing. `adls_pcode_read_psf_gv_point_info()` reads PSF GV points. `icl_get_bw_info()`, `tgl_get_bw_info()`, `dg2_get_bw_info()`, and `xe2_hpd_get_bw_info()` populate the maximum bandwidth tables using different formulas and constants.

## Control Flow

At driver init, `intel_bw_init()` creates the global bandwidth object. For SAGV-capable display versions 11 through 13 it calls `icl_force_disable_sagv()` so the driver starts from a known restricted QGV state. During hardware init, `intel_bw_init_hw()` inspects `intel_dram_info(display)` and selects the appropriate bandwidth formula for the platform. Icelake/Tigerlake-style paths read QGV timing and calculate derated bandwidth per plane group; DG2 fills a constant dummy QGV point because it has no SAGV/QGV point selection; Xe2 HPD uses a simplified peak-bandwidth algorithm and expects two QGV points.

During atomic check, `intel_bw_atomic_check()` first updates active-pipe state for modesets, then updates the SAGV rejection mask if any CRTC changes whether it can tolerate SAGV. On display versions 11 and newer, it compares per-CRTC data rates and active plane counts with old state, stores changed values into the global object, and recalculates QGV/PSF viability when inputs changed. `intel_bw_check_qgv_points()` converts the aggregate data rate from bytes/s scale to kB/s-ish units via `DIV_ROUND_UP(data_rate, 1000)` and dispatches to `mtl_find_qgv_points()` for display version 14 and newer or `icl_find_qgv_points()` for older QGV platforms.

For display versions 11 through 13, `icl_find_qgv_points()` determines all QGV and PSF points that can satisfy the new data rate. If SAGV cannot be enabled, it narrows QGV to the highest-bandwidth point. The stored `qgv_points_mask` is inverted because PCode accepts the mask of points to disable. If the mask changes, the global state is serialized so concurrent nonblocking commits cannot reorder QGV restrictions. `icl_sagv_pre_plane_update()` widens restrictions before plane changes, while `icl_sagv_post_plane_update()` relaxes restrictions afterward, matching the BSpec rule that masking and unmasking are not combined.

For display version 14 and newer, `mtl_find_qgv_points()` does not send PCode restrictions directly. Instead it stores `qgv_point_peakbw` for PM Demand; when SAGV is disallowed it writes `U16_MAX`, otherwise it chooses the satisfying QGV point with the least excess bandwidth and stores peak bandwidth divided by 100.

## State And Persistence

The persistent software state is the atomic global object at `display->bw.obj`. It survives across commits through atomic duplicate/destroy callbacks and is refreshed from CRTC state by `intel_bw_update_hw_state()` during readout/sanitize paths. Hardware-visible state includes `display->sagv.status`, PCode QGV restrictions for display versions 11 through 13, and PM Demand QGV peak bandwidth for display version 14 and newer. `display->bw.max[]` is a cached capability table derived at init and then used by checks. `intel_bw_crtc_disable_noatomic()` clears one pipe's cached bandwidth counters when a CRTC is disabled outside a full atomic update.

## Dependencies And Integration Points

The file depends on the global atomic object framework, CRTC bandwidth helpers from `skl_watermark.h`, DRAM description from `intel_dram.h`, PCode access through `intel_parent_pcode_*()`, MCHBAR/uncore reads, display version/platform macros, and `display->bw.max[]` storage defined in `intel_display_core.h`. Its outputs feed watermark/SAGV policy, PM Demand programming in `intel_pmdemand.c`, and commit sequencing in the modeset path. It relies on CRTC state helpers such as `intel_crtc_bw_data_rate()`, `intel_crtc_bw_num_active_planes()`, and `intel_crtc_can_enable_sagv()`.

## Risks

The bandwidth formulas are platform- and memory-type-sensitive; incorrect `dram_info` fields, channel-width assumptions, or deinterleave rules can accept underrun-prone modes or reject valid modes. Several paths intentionally use warnings or fallbacks rather than hard failures, such as ignored bandwidth limits when QGV readout fails. QGV masks are stored inverted relative to the set of allowed points, which is easy to mishandle. Commit ordering is delicate: pre-plane restriction, post-plane relaxation, and global serialization are required to avoid transient states that violate PCode/BSpec rules. MTL PM Demand depends on peak bandwidth units of 100 MB/s, so unit mistakes can cause power-management misprogramming.

## Test Signals

Useful test coverage includes boot/readout logs for QGV and PSF points, atomic modesets that change plane counts and high-bandwidth formats, SAGV enable/disable transitions, nonblocking commits that change QGV masks, and PM Demand updates on display version 14 and newer. Runtime signals include `drm_dbg_kms()` lines for QGV/PSF bandwidth decisions, PCode error messages from `icl_pcode_restrict_qgv_points()`, underrun reports under high display load, and validation that `intel_bw_pmdemand_needs_update()` toggles only when `qgv_point_peakbw` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.h

## Purpose

`intel_bw.h` is the public display-bandwidth interface for the i915 display code. It hides the private `struct intel_bw_state` layout and exposes lifecycle, atomic-check, commit sequencing, and PM Demand accessors used by modeset, watermark, and power-management code.

## Important APIs, Types, And Functions

The header forward-declares `struct intel_bw_state` plus the atomic, CRTC, display, and global-state types needed by callers. It declares state conversion and lookup helpers: `to_intel_bw_state()`, `intel_atomic_get_old_bw_state()`, `intel_atomic_get_new_bw_state()`, and `intel_atomic_get_bw_state()`. Lifecycle and readout APIs are `intel_bw_init_hw()`, `intel_bw_init()`, `intel_bw_update_hw_state()`, and `intel_bw_crtc_disable_noatomic()`. Validation and commit APIs are `intel_bw_atomic_check()`, `icl_sagv_pre_plane_update()`, and `icl_sagv_post_plane_update()`. PM Demand helpers are `intel_bw_pmdemand_needs_update()`, `intel_bw_can_enable_sagv()`, and `intel_bw_qgv_point_peakbw()`.

## Control Flow And Integration

Callers initialize the global bandwidth object with `intel_bw_init()`, populate hardware capability tables with `intel_bw_init_hw()`, then call `intel_bw_atomic_check()` as part of display atomic validation. If a commit changes QGV restrictions, the modeset sequence calls `icl_sagv_pre_plane_update()` before plane updates and `icl_sagv_post_plane_update()` afterward. PM Demand code queries whether the bandwidth state changed and reads the selected QGV peak bandwidth through this header without depending on the private state layout.

## State And Persistence

The header deliberately keeps `struct intel_bw_state` opaque. The only persistent object it exposes is the global state handle returned through atomic helper APIs. This keeps callers from mutating fields directly except through functions implemented in `intel_bw.c`.

## Dependencies, Risks, And Test Signals

The header includes `<drm/drm_atomic.h>` and otherwise relies on forward declarations to avoid broad include coupling. Interface risks are mostly ordering and lifetime related: callers must only use old/new accessors when corresponding global state exists in the atomic transaction, and SAGV pre/post functions must be called in the correct commit phases. Compile coverage should catch signature drift; runtime coverage should include modeset commits where `intel_bw_atomic_check()` creates or does not create a new global bandwidth state, plus PM Demand checks on MTL+.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.c

## Purpose

`intel_casf.c` implements Content Adaptive Sharpness Filter support for display hardware starting with Lunar Lake style display version 20+. CASF sharpens the image through the second pipe scaler, so the file computes the CRTC CASF state, programs the sharpness LUT and scaler coefficients, enables or disables the sharpness control register, and supports strength-only updates.

## Important APIs, Types, And Functions

The public entry points are `intel_casf_compute_config()`, `intel_casf_update_strength()`, `intel_casf_sharpness_get_config()`, `intel_casf_needs_scaler()`, `intel_casf_scaler_compute_config()`, `intel_casf_enable()`, and `intel_casf_disable()`. The code uses `crtc_state->uapi.sharpness_strength` as the user input and stores hardware-ready values in `crtc_state->hw.casf_params`: `casf_enable`, `strength`, `win_size`, and scaler filter `coeff[]`.

Internal helpers include `intel_casf_compute_win_size()` for selecting 3x3, 5x5, or 7x7 filter size from adjusted-mode pixel count, `intel_casf_filter_lut_load()` for loading the default 32-entry sharpness LUT, `convert_sharpness_coef_binary()` for converting percent-style coefficients to scaler mantissa/exponent format, and `intel_casf_write_coeff()` for programming 17 phases of 7-tap coefficients into scaler coefficient registers for scaler id 1.

## Control Flow

Atomic check calls `intel_casf_compute_config()`. If the platform lacks CASF, the function leaves state unchanged and succeeds. If user sharpness is zero, it disables CASF in CRTC state. If sharpness is nonzero, it rejects joiner configurations because the hardware does not support CASF with joiner pipes. Otherwise it enables CASF, clamps user strength to 0xef, adds 0x10 to convert to the hardware `(1.0 + strength)` 4.4 fixed-point encoding, chooses a filter size based on resolution, and calculates scaler coefficients.

`intel_casf_scaler_compute_config()` chooses one of three 7-tap coefficient templates according to `win_size`, normalizes the weights to percentages, and converts each tap to the scaler coefficient binary representation. At enable time, `intel_casf_enable()` loads the LUT, writes scaler coefficients, programs `SHARPNESS_CTL` with `FILTER_EN`, strength, and filter size, then calls `skl_scaler_setup_casf()` to configure the second pipe scaler. `intel_casf_disable()` clears scaler 1 control/window registers and sharpness control. `intel_casf_update_strength()` changes only the strength field and rewrites the scaler window size to latch the update.

## State And Persistence

CASF state is stored per CRTC in the atomic CRTC state, not in a separate global object. Hardware persistence consists of per-pipe `SHARPNESS_CTL`, `SHRPLUT_INDEX/DATA`, and scaler 1 coefficient/window/control registers. `intel_casf_sharpness_get_config()` reads `SHARPNESS_CTL` during state readout and reconstructs enable, strength, and window size when the filter is active.

## Dependencies And Integration Points

The file depends on CASF register definitions from `intel_casf_regs.h`, display register accessors from `intel_de.h`, CRTC/display state types, and scaler support in `skl_scaler.h`. It integrates with the DRM CRTC sharpness property created elsewhere, with scaler allocation logic that reserves scaler id 1 for CASF, with pipe config state dumping/checking, and with modeset logic that detects CASF enable/disable and strength changes.

## Risks

CASF consumes the second pipe scaler, so conflicts with pipe scaling or other scaler users are a primary risk. The joiner rejection must remain aligned with hardware capability. The coefficient writer warns and returns if scaler id is not 1; if scaler allocation changes, CASF may silently fail to program coefficients beyond that warning. Strength uses two encodings: user 0..255 and hardware fixed point with +0x10 offset and 0xef clamp. Readout warns if hardware strength is below 16, because such values cannot be represented as valid enabled user strength.

## Test Signals

Test signals include property tests that set sharpness 0, low, high, and over-clamp values; modesets at <=1080p, <=4K, and above 4K to exercise all filter sizes; joiner configurations that must fail with `-EINVAL`; scaler allocation tests proving scaler id 1 is reserved; and readout/state-check tests comparing `casf_enable`, `win_size`, and `strength`. Hardware traces should show writes to `SHRPLUT_*`, scaler coefficient registers, `SHARPNESS_CTL`, and scaler 1 window/control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.h

## Purpose

`intel_casf.h` exposes the Content Adaptive Sharpness Filter interface to display atomic-check, readout, scaler, and commit code while keeping the implementation details in `intel_casf.c`.

## Important APIs, Types, And Functions

The header forward-declares `struct intel_crtc_state` and declares seven functions. `intel_casf_compute_config()` validates and computes CASF state from the user sharpness property. `intel_casf_update_strength()` performs a strength-only hardware update. `intel_casf_sharpness_get_config()` reads CASF state from hardware. `intel_casf_enable()` and `intel_casf_disable()` program or clear the filter. `intel_casf_scaler_compute_config()` computes scaler coefficients. `intel_casf_needs_scaler()` tells scaler allocation that CASF requires a scaler.

## Control Flow And Integration

Callers use the header in three phases: atomic validation computes `hw.casf_params`, scaler allocation checks whether CASF needs scaler resources, and commit/readout code programs or reconstructs the hardware state. The interface is intentionally CRTC-state centric, reflecting that CASF is per pipe and has no global state object.

## State And Persistence

No state is defined in the header. CASF state lives in `intel_crtc_state`, and hardware state is handled by the C implementation through per-pipe sharpness and scaler registers.

## Dependencies, Risks, And Test Signals

The header only includes `<linux/types.h>` for `bool` and basic types, which keeps include coupling low. The main risk is call ordering: coefficient computation must precede enable, and `intel_casf_needs_scaler()` must participate in scaler allocation before programming. Compile tests catch prototype drift; runtime tests should cover property-driven enable/disable, fast strength updates, scaler conflicts, and hardware readout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf_regs.h

## Purpose

`intel_casf_regs.h` defines the per-pipe MMIO addresses and bitfields used to program the Content Adaptive Sharpness Filter control register and sharpness LUT.

## Important APIs, Types, And Functions

The header defines `SHARPNESS_CTL(pipe)` from `_SHARPNESS_CTL_A/B`, with `FILTER_EN`, `FILTER_STRENGTH_MASK`, `FILTER_STRENGTH(x)`, `FILTER_SIZE_MASK`, and the three encoded filter sizes `SHARPNESS_FILTER_SIZE_3X3`, `SHARPNESS_FILTER_SIZE_5X5`, and `SHARPNESS_FILTER_SIZE_7X7`. It also defines `SHRPLUT_DATA(pipe)` and `SHRPLUT_INDEX(pipe)` with `INDEX_AUTO_INCR`, `INDEX_VALUE_MASK`, and `INDEX_VALUE(x)`.

## Control Flow And Integration

`intel_casf.c` uses `SHRPLUT_INDEX` with auto-increment to load the LUT, writes `SHRPLUT_DATA` entries in sequence, and writes `SHARPNESS_CTL` to enable/disable CASF and update strength/filter size. Readout uses the masks in this header to parse hardware state.

## State And Persistence

These definitions map to hardware state only. The control register persists enable, strength, and filter-size fields per pipe; the LUT registers are programmed by index/data access. The header itself contains no software state.

## Dependencies, Risks, And Test Signals

The only include is `intel_display_reg_defs.h`, which supplies `_MMIO_PIPE`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Risks are register-address or bitfield drift against BSpec and the limited A/B base-address pattern if future hardware exposes more pipes differently. Tests should validate MMIO traces when enabling CASF, strength field updates via `FILTER_STRENGTH_MASK`, readout parsing, and LUT auto-increment programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.h

## Purpose

`intel_cdclk.h` is the public CDCLK/RAWCLK interface for i915 display code. It defines the hardware clock configuration structure and exposes lifecycle, atomic, commit, readout, debugfs, PM Demand, and timing helper APIs while leaving the private global-state layout in `intel_cdclk.c`.

## Important APIs, Types, And Functions

`struct intel_cdclk_config` contains `cdclk`, `vco`, `ref`, `bypass`, `voltage_level`, and `joined_mbus`. The `joined_mbus` field is valid for Xe2LPD and newer. The header forward-declares the global `struct intel_cdclk_state` and exposes conversion/access macros `to_intel_cdclk_state()`, `intel_atomic_get_old_cdclk_state()`, and `intel_atomic_get_new_cdclk_state()`.

Public APIs cover hardware lifecycle (`intel_cdclk_init_hw()`, `intel_cdclk_uninit_hw()`, `intel_init_cdclk_hooks()`), readout/capabilities (`intel_update_max_cdclk()`, `intel_update_cdclk()`, `intel_read_rawclk()`, `intel_cdclk_get_cdclk()`, `intel_cdclk_read_hw()`), atomic validation and state mutation (`intel_cdclk_atomic_check()`, `intel_atomic_get_cdclk_state()`, `intel_cdclk_state_set_joined_mbus()`, `intel_cdclk_update_dbuf_bw_min_cdclk()`, `intel_cdclk_force_min_cdclk()`), commit sequencing (`intel_set_cdclk_pre_plane_update()`, `intel_set_cdclk_post_plane_update()`, `intel_cdclk_is_decreasing_later()`), diagnostics (`intel_cdclk_dump_config()`, `intel_cdclk_debugfs_register()`), state accessors, PM Demand detection, and prefill/minimum helpers.

## Control Flow And Integration

Display initialization sets hooks and reads/programs hardware through these declarations. Atomic check code updates per-pipe and DBUF constraints, then calls `intel_cdclk_atomic_check()`. Commit code calls pre/post plane update functions to program increases before plane updates and decreases afterward. Watermark, DBUF, PM Demand, audio, and prefill code query current or computed CDCLK state through the accessors.

## State And Persistence

The header exposes only `struct intel_cdclk_config`; the persistent `struct intel_cdclk_state` remains opaque except for container macros that operate on global-state pointers. This preserves central control over logical vs actual CDCLK, active/enabled pipe masks, and transition flags.

## Dependencies, Risks, And Test Signals

The header includes `<linux/types.h>` and relies on atomic global object helper declarations from surrounding include context for its macros. Risks are mostly API-ordering risks: hooks must be initialized before calls through `display->funcs.cdclk`, global state must exist before atomic accessors are used, and joined MBUS must be sequenced with DBUF updates. Tests should compile all display platforms, run atomic modesets that change CDCLK, verify PM Demand update detection, and validate debugfs/readout consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cdclk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.c

## Purpose

`intel_cmtg.c` handles inherited Common Primary Timing Generator state. The current driver does not actively use CMTG, but firmware or pre-OS code may leave it enabled. This file reads a minimal CMTG configuration and disables CMTG when it can do so without requiring a modeset, so later display sanitization does not leave unsupported timing-generator topology active.

## Important APIs, Types, And Functions

The only public function is `intel_cmtg_sanitize()`. The private `struct intel_cmtg_config` records whether CMTG A and B are enabled and whether transcoder A or B is in CMTG secondary mode. `intel_cmtg_has_cmtg_b()` gates the second CMTG on display version 20 and newer. `intel_cmtg_has_clock_sel()` gates CMTG clock selection register handling on display version 14 and newer. `intel_cmtg_transcoder_is_secondary()` safely reads `TRANS_DDI_FUNC_CTL2` under the transcoder power domain. `intel_cmtg_get_config()` reads CMTG enable and secondary-mode state. `intel_cmtg_disable_requires_modeset()` blocks no-modeset disable on pre-display-version-20 systems if any transcoder is secondary. `intel_cmtg_disable()` clears secondary-mode bits, disables CMTG A/B, and marks their clock selections disabled when supported.

## Control Flow

`intel_cmtg_sanitize()` first exits if `HAS_CMTG(display)` is false. Otherwise it reads current CMTG state, logs it, and checks whether disabling requires a modeset. On older platforms, a secondary transcoder implies modeset-sensitive state, so the function returns and leaves CMTG untouched. On platforms that can be disabled safely, it clears secondary mode for transcoders A/B if present, clears `CMTG_ENABLE` on CMTG A and B, and updates `CMTG_CLK_SEL` to disabled values for the affected CMTGs.

The function must run before any port PLL is disabled in broader sanitization because CMTG registers may depend on the port PLL currently supplying the CMTG clock.

## State And Persistence

There is no persistent software state. The local config is a one-time readout snapshot. Hardware state persists in `TRANS_CMTG_CTL_A/B`, `TRANS_DDI_FUNC_CTL2` secondary-mode bits, and `CMTG_CLK_SEL`. The code intentionally avoids tracking enabled CMTG as an ongoing driver-managed feature.

## Dependencies And Integration Points

The file depends on display version/platform macros, `HAS_CMTG()`, display power-domain helpers, register accessors from `intel_de.h`, transcoder register definitions, and CMTG register definitions from `intel_cmtg_regs.h`. It is part of display sanitization and must be ordered before PLL shutdown.

## Risks

The main risk is disabling timing topology while a transcoder still depends on it. The code mitigates this by refusing the pre-D20 case where secondary mode implies a modeset is required, but the FIXME notes that the driver lacks full CMTG state tracking and synchronized modeset disable. Another risk is register access with power domains disabled; `intel_cmtg_transcoder_is_secondary()` uses `with_intel_display_power_if_enabled()` to avoid forcing domains on just for readout. Future platforms with additional CMTGs or transcoders would need this minimal A/B logic extended.

## Test Signals

Test signals include boot/sanitize logs showing inherited CMTG state, systems where firmware leaves CMTG enabled, display version 13/14/20 platform coverage, and verification that CMTG is disabled only when safe. MMIO traces should show `TRANS_CMTG_CTL_A/B`, `TRANS_DDI_FUNC_CTL2`, and `CMTG_CLK_SEL` updates. Regression tests should watch for blank screens or modeset failures after sanitization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.h

## Purpose

`intel_cmtg.h` exposes the minimal CMTG sanitization API used by display initialization/sanitization code.

## Important APIs, Types, And Functions

The header forward-declares `struct intel_display` and declares `intel_cmtg_sanitize(struct intel_display *display)`. No CMTG state type is exposed because the implementation currently only reads and optionally disables inherited hardware state.

## Control Flow And Integration

Display sanitization callers include this header and call `intel_cmtg_sanitize()` before disabling port PLLs. The implementation handles platform detection, readout, and safe disable internally.

## State And Persistence

The header defines no persistent state. CMTG state remains hardware-only and local to the implementation's readout snapshot.

## Dependencies, Risks, And Test Signals

The low include footprint keeps dependencies minimal. The main API risk is ordering: callers must run the sanitizer while the CMTG clock source is still available. Compile tests catch signature drift; boot tests on CMTG-capable platforms should verify that the sanitizer is invoked and does not disturb active display configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg_regs.h

## Purpose

`intel_cmtg_regs.h` defines the small set of MMIO registers and bitfields needed to identify and disable Common Primary Timing Generator state.

## Important APIs, Types, And Functions

The header defines `CMTG_CLK_SEL` and its A/B masks plus disabled encodings: `CMTG_CLK_SEL_A_MASK`, `CMTG_CLK_SEL_A_DISABLED`, `CMTG_CLK_SEL_B_MASK`, and `CMTG_CLK_SEL_B_DISABLED`. It also defines `TRANS_CMTG_CTL_A`, `TRANS_CMTG_CTL_B`, and the `CMTG_ENABLE` bit.

## Control Flow And Integration

`intel_cmtg.c` uses these definitions when clearing CMTG enable bits and resetting clock selection after disabling inherited CMTG state. Secondary-transcoder mode is defined in the broader display register header, so this file stays focused on CMTG-specific registers.

## State And Persistence

These are hardware register definitions only. The associated hardware state persists in the display engine until explicitly changed or reset. There is no software state in the header.

## Dependencies, Risks, And Test Signals

The header depends on `intel_display_reg_defs.h` for `_MMIO`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Risks are incorrect masks or disabled encodings, especially as CMTG B and clock selection are platform-version dependent in the implementation. Tests should inspect MMIO writes during sanitize and compare the final CMTG clock selection and enable bits with expected disabled values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg_regs.h -->
