# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.c

Purpose: tracks the display data-buffer bandwidth pressure that contributes to minimum CDCLK selection on DISPLAY_VER >= 9. It models per-pipe, per-DBuf-slice maximum plane data rates and active plane counts, stores that model in an i915 global atomic object, and feeds old/new minimum CDCLK values into CDCLK recalculation.

Important APIs and types: private `struct intel_dbuf_bw` stores `max_bw[slice]` and `active_planes[slice]`; private `struct intel_dbuf_bw_state` embeds `struct intel_global_state` and per-pipe DBuf bandwidth arrays. Public helpers retrieve old/new/current global state, initialize the global object, update state from current hardware, clear one pipe during noatomic disable, compute minimum CDCLK, and participate in atomic CDCLK calculation.

Control flow: `skl_crtc_calc_dbuf_bw()` clears one pipe model, skips inactive CRTCs and cursor planes, then adds primary/sprite plane rates for their allocated DDB slices, including Y-plane DDB on DISPLAY_VER < 11. `intel_dbuf_bw_min_cdclk()` walks each DBuf slice, finds the maximum per-plane bandwidth and total active plane count across pipes, multiplies them to model equal-share arbiter limits, takes the maximum slice pressure, and divides by 64 rounded up. `intel_dbuf_bw_calc_min_cdclk()` compares old/new CRTC-derived bandwidth, obtains and updates global state only when needed, locks the global object when the aggregate state changes, and calls `intel_cdclk_update_dbuf_bw_min_cdclk()`.

State and persistence: persistent state lives in `display->dbuf_bw.obj.state` and is duplicated/destroyed through `intel_global_state_funcs`. Atomic transactions clone and mutate this global state; non-atomic setup/disable paths update it directly to keep software state in sync with hardware. No hardware registers are written by this file.

Dependencies and integration: depends on `skl_watermark.h` for DDB slice masks and watermark/DDB state, display core/types for pipes/planes/platform iteration, and CDCLK code for applying the derived minimum. Display driver init calls `intel_dbuf_bw_init()`, modeset setup refreshes state, CRTC disable can clear state noatomically, and `intel_cdclk.c` calls the calc/min helpers.

Risks: cursor planes are assumed too small to affect bandwidth; if future cursor behavior changes, this model may understate DBuf pressure. The equal-share arbiter approximation intentionally uses max plane rate times active plane count and may be conservative or inaccurate for unusual DDB splits. State must be locked when aggregate bandwidth changes to avoid racing other global-state users.

Test signals: atomic modeset tests that alter plane data rates, DDB allocations, pipe activity, and CDCLK requirements on SKL+ hardware; plane enable/disable and Y-plane cases on pre-Gen11; modeset setup/readout keeping `display->dbuf_bw.obj.state` synchronized; and CDCLK recalculation when only DBuf bandwidth changes.
