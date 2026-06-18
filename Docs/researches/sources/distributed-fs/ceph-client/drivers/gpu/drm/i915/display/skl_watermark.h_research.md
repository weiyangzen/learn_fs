# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_watermark.h

Purpose: declares the exported SKL+ watermark, SAGV, DBUF, MBUS, and verification interface used by i915 display atomic check/commit code and plane programming code.

Important APIs/types/functions: SAGV APIs include `intel_sagv_pre_plane_update()`, `intel_sagv_post_plane_update()`, `intel_crtc_can_enable_sagv()`, and `intel_has_sagv()`. DDB/watermark APIs include `skl_ddb_dbuf_slice_mask()`, `skl_ddb_allocation_overlaps()`, `skl_plane_wm_level()`, `skl_plane_trans_wm()`, `skl_plane_relative_data_rate()`, `skl_wm0_prefill_lines_worst()`, `skl_wm0_prefill_lines()`, `skl_watermark_max_latency()`, `skl_wm_init()`, noatomic disable helpers, and state verification. DBUF/MBUS APIs include `intel_atomic_get_dbuf_state()`, `intel_dbuf_init()`, slice/pipe counters, `intel_dbuf_state_set_mdclk_cdclk_ratio()`, pre/post plane update hooks, MDCLK/CDCLK ratio update, MBUS pre/post DDB update, PM demand checks, and `intel_program_dpkgc_latency()`.

Control flow: the header is used in atomic check to compute and fetch DBUF global state, in commit sequencing to order SAGV/DBUF/MBUS updates around plane programming, in plane code to select programmed watermark levels and DDB values, and in debug/verification paths to inspect or expose status.

State and persistence behavior: declares opaque `struct intel_dbuf_state` and watermark structures without exposing internals. Callers mutate persistent atomic global DBUF state only through the provided functions. SAGV and IPC state are stored in `intel_display`, while watermark and DDB results are stored in CRTC state.

Dependencies and integration points: forward declarations keep includes light while integrating CRTC state, plane state, atomic state, plane IDs, DDB entries, and pipe watermark structures. The implementation depends on many display internals, but external users only need this contract.

Risks: commit ordering is implicit in the API names: pre-plane and post-plane hooks must be called at the correct time or hardware can be programmed with incompatible DBUF slices, MBUS mode, or SAGV state. `skl_plane_wm_level()` can return SAGV-selected levels depending on pipe state, so callers must not bypass it when programming hardware.

Test signals: compile coverage from atomic/commit/plane code, DBUF global state acquisition failure paths, hook ordering tests, watermark verification, debugfs status files, and platforms with and without SAGV/IPC/MBUS joining.
