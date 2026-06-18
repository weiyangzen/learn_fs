# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.c

Purpose: coordinates shared display link bandwidth fallback during atomic check and exposes a connector debugfs control to force link bits-per-pixel. It lets DP MST, DP tunnel, FDI, and similar shared links ask for lower bpp or DSC-based recomputation without embedding the fallback loop in each encoder.

Important APIs/types/functions: `intel_link_bw_init_limits()` initializes `struct intel_link_bw_limits` from duplicated atomic state and connector force values. `intel_link_bw_reduce_bpp()` and `__intel_link_bw_reduce_bpp()` choose the pipe with the highest current link bpp and lower its maximum. `intel_link_bw_compute_pipe_bpp()` clamps simple encoder pipe bpp to max link bpp. `intel_link_bw_set_bpp_limit_for_pipe()` pins a known-good limit after compute failure. `intel_link_bw_atomic_check()` calls `intel_dp_mst_atomic_check_link()`, `intel_dp_tunnel_atomic_check_link()`, and `intel_fdi_atomic_check_link()`. Debugfs helpers parse fixed-point Q4 bpp strings and implement `intel_link_bw_connector_debugfs_add()`.

Control flow: atomic check initializes limits, computes CRTC states, then shared-link checks may update limits and return `-EAGAIN`. The caller recomputes affected pipes with lower `max_bpp_x16` or newly enabled DSC limits. Bpp reduction first respects per-connector forced bpp, then, if no fallback remains, can reduce below a forced value. The debugfs write path validates the requested bpp against DSC or minimum pipe bpp and maximum pipe bpp under `connection_mutex`.

State and persistence behavior: per-atomic-check bandwidth state is transient in `intel_link_bw_limits`. Forced bpp persists at runtime in `connector->link.force_bpp_x16` until changed or connector teardown. There is no filesystem persistence beyond debugfs control visibility.

Dependencies and integration points: integrates with Intel atomic state, connector state iteration, DP MST bandwidth allocation, DP tunnel allocation, FDI bandwidth checks, DSC capability helpers, fixed-point DRM helpers, and connector debugfs.

Risks: limits must only become stricter; `assert_link_limit_change_valid()` warns if DSC is removed or bpp increases during fallback. YUV420 is noted as a TODO because MST bandwidth currently uses pipe bpp, not actual half-rate link bpp. Forced bpp parsing uses Q4 fixed-point with overflow checks, and debugfs accepts zero as reset. Fallback can loop or fail if affected pipes are not correctly marked for modeset recomputation.

Test signals: MST over-allocation fallback, DP tunnel bandwidth pressure, FDI fallback, forced bpp debugfs read/write including fractional values and reset to zero, DSC and non-DSC min/max validation, `-EAGAIN` recompute loops, and warnings on invalid limit changes.
