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
