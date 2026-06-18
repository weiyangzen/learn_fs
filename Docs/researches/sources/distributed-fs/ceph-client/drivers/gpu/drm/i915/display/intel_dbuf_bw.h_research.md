# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dbuf_bw.h

Purpose: public interface for DBuf-bandwidth global state and minimum-CDCLK calculation.

Important APIs: `to_intel_dbuf_bw_state()` casts an `intel_global_state`; `intel_atomic_get_old_dbuf_bw_state()`, `intel_atomic_get_new_dbuf_bw_state()`, and `intel_atomic_get_dbuf_bw_state()` access the global object in an atomic transaction; `intel_dbuf_bw_init()` creates the global object; `intel_dbuf_bw_calc_min_cdclk()` updates atomic state and reports whether CDCLK recalculation is needed; `intel_dbuf_bw_min_cdclk()` computes the current minimum from a state object; `intel_dbuf_bw_update_hw_state()` and `intel_dbuf_bw_crtc_disable_noatomic()` keep non-atomic paths synchronized.

Control flow and state: declarative only. The opaque `struct intel_dbuf_bw_state` prevents callers from depending on internal arrays while allowing CDCLK and setup code to pass state objects around.

Dependencies and integration: includes `<drm/drm_atomic.h>` for atomic-related types and forward-declares i915 display structures. It is consumed by display driver init, CDCLK code, and modeset setup/disable paths.

Risks: callers must handle `ERR_PTR` from `intel_atomic_get_dbuf_bw_state()` and must not assume DBuf bandwidth is meaningful on DISPLAY_VER < 9, where implementation helpers return early or zero. Since state is global, misuse outside atomic locking rules can create inconsistent CDCLK decisions.

Test signals: compile coverage and integration tests for CDCLK recalculation with plane/DDB changes, plus noatomic disable/readout synchronization.
