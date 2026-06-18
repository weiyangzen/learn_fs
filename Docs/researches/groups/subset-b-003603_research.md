# subset-b-003603 i915 display plane, watermark, and VLV clock research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.c

Purpose: implements the Skylake-and-newer i915 universal plane backend. It defines supported plane formats and modifiers, maps DRM fourcc and atomic plane state into hardware register values, validates plane framebuffer geometry, computes surface offsets for tiled/CCS/NV12 layouts, programs plane color/CSC/scaler/PSR selective-fetch state, handles plane enable/disable/async flip sequencing, and creates DRM universal plane objects for SKL, GLK, ICL, TGL, ADL, Xe3 and related display generations.

Important APIs/types/functions: exported helpers include `skl_universal_plane_create()`, `skl_get_initial_plane_config()`, `skl_fixup_initial_plane_config()`, `skl_format_to_fourcc()`, `skl_calc_main_surface_offset()`, `icl_link_nv12_planes()`, `icl_is_nv12_y_plane()`, `icl_hdr_plane_mask()`, `icl_is_hdr_plane()`, and `skl_plane_aux_dist()`. Core plane hooks are installed through `struct intel_plane`: `check_plane`, `update_noarm`, `update_arm`, `disable_arm`, `get_hw_state`, `capture_error`, `async_flip`, flip-done IRQ enable/disable, stride/alignment/width/cdclk callbacks, and `disable_tiling`. Format/modifier policy lives in the `skl_plane_formats`, `skl_planar_formats`, `glk_planar_formats`, `icl_sdr_y_plane_formats`, `icl_sdr_uv_plane_formats`, and `icl_hdr_plane_formats` tables plus `*_plane_format_mod_supported()` callbacks.

Control flow: atomic check starts in `skl_plane_check()`. It validates framebuffer constraints with `skl_plane_check_fb()`, selects scaler limits, calls `intel_plane_check_clipping()`, makes damage viewport-relative, computes GTT/view state via `skl_check_plane_surface()`, validates destination/source coordinates and NV12 rotation, derives protected-content handling, and stores precomputed `ctl`, `color_ctl`, and `cus_ctl` values in the plane state. Surface validation computes CCS auxiliary offsets first, then NV12 chroma offsets, then the main surface. It repeatedly backs up aligned offsets when required so AUX distance is non-negative, X-tile scanout does not cross stride limits, and CCS AUX coordinates match main-plane coordinates.

Update programming is split into no-arm and arm phases. `skl_plane_update_noarm()` writes stride, position, size, and watermarks for pre-ICL style planes; `skl_plane_update_arm()` writes color key, offsets, AUX distance, optional scaler state, then arms with `PLANE_CTL` followed by `PLANE_SURF`. ICL+ paths add color pipeline programming, clear-color values, CUS control, input CSC matrices for HDR YUV, PSR2 selective-fetch registers, per-plane CSC black-fill for protected content failure, pixel normalizer programming, and color pipeline arm commits. Disable paths write watermarks, clear selective fetch/normalizer/CUS as needed, clear `PLANE_CTL`, then write `PLANE_SURF` to arm the disable.

State and persistence behavior: persistent software state is mostly carried by `intel_plane` capabilities and callbacks and by per-commit `intel_plane_state` fields such as `ctl`, `color_ctl`, `cus_ctl`, `surf`, `decrypt`, `force_black`, damage rectangles, color-plane offsets, and scanout strides. Hardware state is programmed via MMIO/DSB writes to plane registers and recovered during initial readout through `skl_get_initial_plane_config()`. The initial plane readout builds an `intel_framebuffer` from live `PLANE_CTL`, `PLANE_SURF`, `PLANE_SIZE`, `PLANE_STRIDE`, and tiling/compression bits, but intentionally rejects joiner and 90/270 rotation configurations. `skl_fixup_initial_plane_config()` updates `PLANE_SURF` when framebuffer takeover moved the surface in GGTT.

Dependencies and integration points: this file sits between DRM atomic plane helpers and i915 display hardware. It depends on DRM format/color/blend/damage helpers, i915 framebuffer layout helpers, GEM object protection checks, FBC, PSR, scaler, color pipeline, DSB/MMIO access, display workarounds, frontbuffer tracking, IRQ handling, watermarks from `skl_watermark.h`, and register definitions from `skl_universal_plane_regs.h`. `skl_universal_plane_create()` integrates the plane with DRM properties for rotation, color encoding/range, alpha, blend mode, immutable zpos, damage clips, scaling filters, and display-version-specific modifiers.

Risks: the code is highly sensitive to display generation, platform workarounds, and modifier-specific alignment. Incorrect surface offset or AUX distance handling can cause corruption, faults, or hangs, especially for CCS, DPT, protected content, and tiled/rotated surfaces. Watermark or DDB changes are intentionally tied into plane update decisions; allowing async flips while DDB/watermarks change is rejected. Initial plane takeover supports only a subset of live BIOS configurations. Several comments flag unresolved hardware details: linear async flip restrictions, X-tile panning, chroma-plane size limits, prefill/scaler assumptions, and protected-session invalidation after commit.

Test signals: useful coverage includes atomic plane format/modifier validation across SKL/GLK/ICL/TGL/DG2/MTL/Xe3, CCS and MC/RC clear-color modifiers, NV12/P010/P012/P016 planar linking, AUX distance and offset backtracking tests, 90/270 rotation rejection/acceptance by format, horizontal flip constraints, async flip on supported PLANE_1 modifiers, PSR2 selective-fetch damage clips, protected BO decrypt/force-black paths, initial framebuffer readout, and hardware-state verification after enable/disable/modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.h

Purpose: declares the public interface for the Skylake universal plane implementation. It exposes plane construction, initial plane readout/fixup, format conversion, surface offset calculation, NV12 plane linkage, HDR/Y-plane classification, and AUX distance calculation to the rest of the i915 display subsystem.

Important APIs/types/functions: `skl_universal_plane_create()` allocates and initializes a platform-specific `intel_plane`. `skl_get_initial_plane_config()` and `skl_fixup_initial_plane_config()` support firmware framebuffer takeover. `skl_format_to_fourcc()` maps hardware format bits plus RGB order/alpha state to DRM fourcc codes. `skl_calc_main_surface_offset()` computes main-surface GGTT/DPT offsets and adjusted x/y coordinates. `icl_link_nv12_planes()` links ICL+ Y and UV plane states. `icl_is_nv12_y_plane()`, `icl_hdr_plane_mask()`, and `icl_is_hdr_plane()` expose generation-specific plane-role classification. `skl_plane_aux_dist()` computes the programmed distance from a main surface to its AUX plane.

Control flow: callers include display plane initialization, initial framebuffer readout, atomic plane checking, and watermark/plane programming code. The header avoids exposing implementation-local register packing and keeps external dependencies to forward declarations plus `linux/types.h`.

State and persistence behavior: the header itself has no state. Its functions operate on persistent `intel_plane`, `intel_crtc`, `intel_display`, `intel_initial_plane_config`, `intel_plane_state`, `skl_ddb_entry`, and `skl_wm_level` objects owned elsewhere.

Dependencies and integration points: it is included by display initialization and other i915 display files that need to create or inspect SKL-style planes. It bridges CRTC state, initial plane config, watermark DDB data, and plane state without requiring those users to include the full implementation details.

Risks: the API assumes callers pass generation-appropriate plane IDs and states. `skl_calc_main_surface_offset()` mutates coordinate outputs, so misuse can desynchronize source rectangles and surface view state. NV12 linkage helpers are only meaningful on ICL+ plane layouts.

Test signals: compile coverage from all include sites, plane creation on each display generation, initial plane takeover tests, NV12 Y/UV pairing checks, and unit-style validation for format-to-fourcc mappings are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane_regs.h

Purpose: defines MMIO register address macros and bit fields for SKL+ universal plane programming. It covers plane control, stride, position, size, color keying, surface base/live address, offsets, AUX distance/offset, chroma upsampling, plane color control, input/plane CSC, per-plane gamma LUTs, watermarks, DDB buffer configuration, selected-fetch registers, plane pixel normalizer, and selected platform-specific fields.

Important APIs/types/functions: address constructors include `_SKL_PLANE()`, `_SKL_PLANE_DW()`, `_MMIO_SKL_PLANE()`, `_MMIO_SKL_PLANE_DW()`, `_SEL_FETCH()`, and `_MMIO_SEL_FETCH()`. Main register macros include `PLANE_CTL`, `PLANE_STRIDE`, `PLANE_POS`, `PLANE_SIZE`, `PLANE_KEYVAL`, `PLANE_KEYMSK`, `PLANE_SURF`, `PLANE_SURFLIVE`, `PLANE_KEYMAX`, `PLANE_OFFSET`, `PLANE_CC_VAL`, `PLANE_AUX_DIST`, `PLANE_AUX_OFFSET`, `PLANE_CUS_CTL`, `PLANE_COLOR_CTL`, `PLANE_INPUT_CSC_*`, `PLANE_CSC_*`, `PLANE_WM`, `PLANE_WM_TRANS`, `PLANE_WM_SAGV`, `PLANE_WM_SAGV_TRANS`, `PLANE_NV12_BUF_CFG`, `PLANE_BUF_CFG`, `PLANE_MIN_BUF_CFG`, `SEL_FETCH_PLANE_*`, and `PLANE_PIXEL_NORMALIZE`.

Control flow: implementation files use these macros to compose register writes and reads with `intel_de_read()`, `intel_de_write()`, `intel_de_write_dsb()`, and read-modify-write helpers. `PLANE_CTL` fields encode enable, arbitration slots, format, color key mode, RGB order, YUV420 Y-plane tagging, CSC/range, compression, tiling, async flip, horizontal flip, alpha, and rotation. DDB/watermark fields are consumed by both plane programming and watermark verification.

State and persistence behavior: the header defines symbolic access to hardware state but owns no runtime data. Its bit definitions become persistent hardware state only when written by display commit code. Some bit positions intentionally alias across generations, such as pre-GLK alpha versus TGL+ media compression or Yf versus tile4 tiling, so callers must gate by display version.

Dependencies and integration points: depends on `intel_display_reg_defs.h` for `_MMIO`, `_PIPE`, `_PLANE`, `_PICK`, and `REG_*` helpers. It is shared by `skl_universal_plane.c`, `skl_watermark.c`, cursor/watermark code, and color pipeline code that must address per-plane registers.

Risks: generation aliasing is the major risk. A field that is valid on one display version can mean something else on another; implementation code must preserve version checks. Plane and selective-fetch address helpers encode non-linear plane numbering and pipe ranges, so adding new planes or display versions requires careful validation against BSpec. Register masks for DDB sizes span SKL through Xe3 and must be interpreted with platform-specific block counts.

Test signals: build-time compile coverage, register read/write trace comparison with BSpec, hardware state dumps before and after commits, watermark verification, selected-fetch enable/disable tests, and modifier-specific plane programming tests all exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.c

Purpose: implements SKL+ display watermark, DDB/DBUF, SAGV, MBUS, IPC, and related latency handling for i915 atomic display commits. It computes per-plane watermark levels from plane geometry and memory latency, partitions DBUF/DDB blocks among active pipes and planes, controls SAGV enablement around plane updates, updates DBUF slices and MBUS join state, reads/sanitizes hardware watermark state, and verifies hardware programming against atomic state.

Important APIs/types/functions: `struct intel_dbuf_state` is an i915 global atomic state object holding per-pipe DDB ranges, weights, DBUF slice masks, enabled slices, active pipe mask, MDCLK/CDCLK ratio, and MBUS join state. `struct skl_wm_params` carries derived plane geometry for watermark math. Exported entry points include `intel_enabled_dbuf_slices_mask()`, `intel_has_sagv()`, `intel_sagv_pre_plane_update()`, `intel_sagv_post_plane_update()`, `intel_crtc_can_enable_sagv()`, `skl_ddb_dbuf_slice_mask()`, `skl_ddb_allocation_overlaps()`, `skl_plane_wm_level()`, `skl_plane_trans_wm()`, `skl_plane_relative_data_rate()`, `skl_wm0_prefill_lines_worst()`, `skl_wm0_prefill_lines()`, `intel_program_dpkgc_latency()`, `intel_atomic_get_dbuf_state()`, `intel_dbuf_init()`, DBUF/MBUS pre/post update hooks, PM demand helpers, noatomic disable helpers, `intel_wm_state_verify()`, `skl_wm_init()`, debugfs registration, and `skl_watermark_max_latency()`.

Control flow: initialization calls `skl_wm_init()`, which probes SAGV, reads memory latency from PCode or MTL latency registers, adjusts/sanitizes latency values, and installs `skl_wm_funcs`. Atomic check enters `skl_compute_wm()`: it builds raw pipe watermarks for changed CRTCs, computes DDB/DBUF global state, sets whether software SAGV watermarks should be selected, adds affected planes when watermarks/DDB changed, and emits KMS debug change logs. Per-plane watermark construction derives `skl_wm_params`, computes normal levels, transition watermarks, and TGL+ SAGV watermarks. It handles planar formats by computing UV requirements and ICL+ linked Y/UV plane behavior.

DDB and DBUF control flow: `skl_compute_ddb()` calculates active pipes, MBUS join eligibility, DBUF slice masks from platform tables, enabled slice masks, per-pipe weights, and per-pipe DDB ranges. `skl_crtc_allocate_plane_ddb()` then reserves cursor blocks, finds the highest watermark level whose minimum block requirements fit, allocates minimum plus proportional extra DDB to planes by relative data rate, disables impossible levels, and handles Xe3 minimum/interim DDB programming. Platform slice topology is encoded in `icl_allowed_dbufs`, `tgl_allowed_dbufs`, `dg2_allowed_dbufs`, and `adlp_allowed_dbufs`, with special MBUS joining preference for selected ADL-P style configurations.

SAGV and latency flow: SAGV is enabled or disabled around plane updates through `intel_sagv_pre_plane_update()` and `intel_sagv_post_plane_update()`. Pre-ICL uses PCode SAGV control directly; ICL+ delegates to bandwidth-state helpers. `intel_crtc_can_enable_sagv()` rejects inherited state, disabled modparams, interlace, missing common levels, or missing TGL+ SAGV watermark capability. Latency setup reads PCode levels or MTL latency registers, applies DG2 multiplication, monotonic sanitation, memory read latency, and 16 Gb DIMM workarounds. Display 20+ package C-state latency programming uses max watermark latency, flip queue added wake time, and line-time rounding.

State and persistence behavior: DBUF state is a global atomic object duplicated/destroyed by `intel_dbuf_funcs`; committed state persists in `display->dbuf.obj.state` and mirrors hardware slice/DDB programming. Watermark state persists in `intel_crtc_state->wm.skl.raw` and `.optimal`, plus per-plane DDB arrays and Xe3 min/interim arrays. SAGV status and block time persist in `display->sagv`; IPC enable state persists in `display->wm.ipc_enabled`; memory latencies persist in `display->wm.skl_latency`; DBUF enabled slices persist in `display->dbuf.enabled_slices`. Hardware is read back during `skl_wm_get_hw_state()` and checked by `intel_wm_state_verify()`.

Dependencies and integration points: integrates atomic global state, bandwidth state, CDCLK/MDCLK, PCode mailbox, display runtime PM, DRAM information, DBUF power control, MBUS registers, cursor registers, universal plane watermark/DDB registers, scaler/prefill, VRR guardband logic, PSR latency reporting, flip queue timing, debugfs, and DRM KMS debug logging. Plane programming consumes `skl_plane_wm_level()`/`skl_plane_trans_wm()` and DDB arrays when writing `PLANE_WM*` and `PLANE_BUF_CFG`.

Risks: this file guards hardware hang and underrun scenarios, so off-by-one block calculations, stale DBUF slice state, or missed affected-plane additions are high risk. DBUF transitions must serialize global state when enabled slices or MBUS joining change. DDB/watermark updates are forbidden during async flips. BIOS DBUF misconfiguration can cause impossible transitions, so sanitize disables planes when overlap or wrong-slice conditions are detected. SAGV control is fragile on systems where BIOS disables control or PCode reports no support. Latency workarounds intentionally bias conservative values; incorrect platform detection can hurt power or stability.

Test signals: key signals include atomic modeset and plane-update tests across single/multi-pipe configurations, DBUF slice map validation for ICL/TGL/DG2/ADLP, DDB overlap checks, cursor offscreen/disable watermark updates, async flip rejection when DDB/WM changes, SAGV enable/disable transitions, IPC debugfs toggling, latency read/sanitize logs, hardware-state mismatch reports from `intel_wm_state_verify()`, VRR prefill guardband tests, package C latency programming, suspend/resume readout, and BIOS misconfigured DBUF sanitization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.h

Purpose: declares the exported SKL+ watermark, SAGV, DBUF, MBUS, and verification interface used by i915 display atomic check/commit code and plane programming code.

Important APIs/types/functions: SAGV APIs include `intel_sagv_pre_plane_update()`, `intel_sagv_post_plane_update()`, `intel_crtc_can_enable_sagv()`, and `intel_has_sagv()`. DDB/watermark APIs include `skl_ddb_dbuf_slice_mask()`, `skl_ddb_allocation_overlaps()`, `skl_plane_wm_level()`, `skl_plane_trans_wm()`, `skl_plane_relative_data_rate()`, `skl_wm0_prefill_lines_worst()`, `skl_wm0_prefill_lines()`, `skl_watermark_max_latency()`, `skl_wm_init()`, noatomic disable helpers, and state verification. DBUF/MBUS APIs include `intel_atomic_get_dbuf_state()`, `intel_dbuf_init()`, slice/pipe counters, `intel_dbuf_state_set_mdclk_cdclk_ratio()`, pre/post plane update hooks, MDCLK/CDCLK ratio update, MBUS pre/post DDB update, PM demand checks, and `intel_program_dpkgc_latency()`. Debug and IPC APIs include `skl_watermark_ipc_init()`, `skl_watermark_ipc_update()`, `skl_watermark_ipc_enabled()`, and `skl_watermark_debugfs_register()`.

Control flow: the header is used in atomic check to compute and fetch DBUF global state, in commit sequencing to order SAGV/DBUF/MBUS updates around plane programming, in plane code to select programmed watermark levels and DDB values, and in debug/verification paths to inspect or expose status.

State and persistence behavior: declares opaque `struct intel_dbuf_state` and watermark structures without exposing internals. Callers mutate persistent atomic global DBUF state only through the provided functions. SAGV and IPC state are stored in `intel_display`, while watermark and DDB results are stored in CRTC state.

Dependencies and integration points: forward declarations keep includes light while integrating CRTC state, plane state, atomic state, plane IDs, DDB entries, and pipe watermark structures. The implementation depends on many display internals, but external users only need this contract.

Risks: commit ordering is implicit in the API names: pre-plane and post-plane hooks must be called at the correct time or hardware can be programmed with incompatible DBUF slices, MBUS mode, or SAGV state. `skl_plane_wm_level()` can return SAGV-selected levels depending on pipe state, so callers must not bypass it when programming hardware.

Test signals: compile coverage from atomic/commit/plane code, DBUF global state acquisition failure paths, hook ordering tests, watermark verification, debugfs status files, and platforms with and without SAGV/IPC/MBUS joining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark_regs.h

Purpose: defines MMIO registers and bit fields for SKL+ DBUF, MBUS, watermark latency, and package C-state latency control. It is the register companion for `skl_watermark.c`.

Important APIs/types/functions: main register macros include `PIPE_MBUS_DBOX_CTL()`, `MBUS_UBOX_CTL`, `MBUS_BBOX_CTL_S1`, `MBUS_BBOX_CTL_S2`, `MBUS_CTL`, `DBUF_CTL_S()`, `MTL_LATENCY_LP0_LP1`, `MTL_LATENCY_LP2_LP3`, `MTL_LATENCY_LP4_LP5`, `MTL_LATENCY_SAGV`, and `LNL_PKG_C_LATENCY`. Bit fields cover MBUS DBOX transaction throttling, A/B/I/BW credits, MBUS join and hash mode, join pipe selection, translation throttle minimum, DBUF power request/state, tracker-state service fields, MTL latency pairs, SAGV QCLK latency, and Lunar Lake package C latency plus added wake time.

Control flow: watermark code uses these macros to read latency values, inspect or update DBUF power state, program MBUS joining and pipe selection, update tracker service ratios when CDCLK/MDCLK changes, configure DBOX credits for active pipes, and program package C-state latency for display power behavior.

State and persistence behavior: the header has no software state. Values written through these macros persist in hardware registers across display power/runtime sequences until reset, firmware, or driver code changes them. Some fields have generation-specific widths, such as Xe3P versus older DBUF minimum tracker service masks and MBUS translation throttle fields.

Dependencies and integration points: depends on `intel_display_reg_defs.h`. It is consumed by watermark/DBUF code and indirectly by CDCLK, power, and atomic commit paths that coordinate with DBUF and MBUS state.

Risks: incorrectly selecting older versus Xe3P field masks can corrupt unrelated bits. MBUS join state must match DBUF slice allocation and CDCLK state or underruns/hangs are possible. Latency register fields are packed pairs, so parsing even/odd levels incorrectly would invalidate all watermark calculations.

Test signals: register dumps across MBUS join/unjoin, DBUF slice enable/disable, latency readout logs, package C latency writes on display 20+, KMS underrun checks, and hardware-state verification after modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.c

Purpose: provides Valleyview/Cherryview-style clock read helpers for HPLL VCO, hrawclk, czclk, cdclk, and GPLL reference clocks. The helpers read CCK sideband registers, convert hardware divider values to kHz, and cache selected stable frequencies in `intel_display`.

Important APIs/types/functions: exported functions are `vlv_clock_get_hpll_vco()`, `vlv_clock_get_hrawclk()`, `vlv_clock_get_czclk()`, `vlv_clock_get_cdclk()`, and `vlv_clock_get_gpll()`. The local helper `vlv_clock_get_cck()` performs common sideband read, divider extraction, in-progress warning, and frequency calculation. It uses `display->vlv_clock.hpll_freq` and `display->vlv_clock.czclk_freq` as caches.

Control flow: `vlv_clock_get_hpll_vco()` lazily reads `CCK_FUSE_REG`, indexes the VCO table `{800, 1600, 2000, 2400}` MHz, stores kHz in the display cache, and logs it. `vlv_clock_get_cck()` acquires CCK access, reads the requested register, releases access, warns if frequency status does not match the divider, and returns `DIV_ROUND_CLOSEST(ref_freq << 1, divider + 1)`. hrawclk, cdclk, and GPLL calls pass the appropriate CCK register and reference frequency; czclk is lazily cached after first read.

State and persistence behavior: HPLL and CZ clock values persist in `display->vlv_clock` once read. The file explicitly notes that this lazy caching is fragile because the first call must happen when the registers are readable; a future explicit initialization point would be safer. hrawclk, cdclk, and GPLL are read live each call.

Dependencies and integration points: depends on DRM logging, `intel_display_core.h`, `intel_display_types.h`, `vlv_sideband.h`, and the CCK sideband access helpers `vlv_cck_get()`, `vlv_cck_read()`, and `vlv_cck_put()`. These helpers feed display clock setup/readout paths for older VLV/CHV platforms.

Risks: wrong timing of the first lazy cached read can permanently cache zero or stale frequencies. Divider status mismatches mean a frequency change is in progress and the returned value may be transient. The HPLL table assumes fuse encoding stays in range. Callers on non-VLV platforms should rely on header stubs or avoid these functions.

Test signals: VLV/CHV boot logs for HPLL/CZ values, sideband read failure instrumentation, status-mismatch warning paths during clock changes, repeated calls proving cache stability, and comparing computed clock rates with BIOS/kernel display clock readouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.h

Purpose: declares VLV clock read helpers when building the i915 driver and provides zero-returning inline stubs when the header is included outside `I915` builds.

Important APIs/types/functions: the public functions are `vlv_clock_get_hpll_vco()`, `vlv_clock_get_hrawclk()`, `vlv_clock_get_czclk()`, `vlv_clock_get_cdclk()`, and `vlv_clock_get_gpll()`, all taking `struct drm_device *` and returning integer kHz values in the real implementation. The non-`I915` stubs return `0`.

Control flow: build-time `#ifdef I915` selects between external declarations and static inline fallback implementations. This lets shared code include the header without pulling in VLV sideband implementation dependencies when i915 is not present.

State and persistence behavior: the header owns no state. In i915 builds, the implementation caches selected values in `intel_display`; in stub builds, calls have no side effects.

Dependencies and integration points: forward-declares `struct drm_device` and is included by VLV/CHV display clock code or shared display code that needs clock helpers conditionally.

Risks: the zero stubs are safe for compilation but not meaningful clock values; callers must not treat stub builds as real hardware readout. The API does not encode units in the type, so callers must preserve the kHz convention from the implementation.

Test signals: compile coverage with and without `I915`, VLV/CHV runtime clock readout, and call sites verifying that zero-return stubs are only used in non-hardware or unsupported configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_clock.h -->
