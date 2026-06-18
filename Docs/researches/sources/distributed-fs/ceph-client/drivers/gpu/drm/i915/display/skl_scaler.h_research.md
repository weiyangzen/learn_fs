# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.h

### Purpose
`skl_scaler.h` declares the public interface for SKL-style pipe scaler staging, atomic setup, programming, disable/readback, CASF setup, mode validation, ECC workaround hooks, and prefill/max-scale estimates.

### Important APIs, Types, And Functions
The header exports scaler update functions for CRTC and plane users, `intel_atomic_setup_scalers()`, programming functions for pfit and plane scalers, detach/disable/readback functions, CASF setup, mode validation, ADL ECC mask/unmask, max-scale queries, and normal/worst-case scaler prefill helpers.

### Control Flow
Callers stage scaler requirements during plane/CRTC atomic checks, call `intel_atomic_setup_scalers()` during CRTC check to allocate IDs and validate scale factors, then program or detach scalers during commit. Readback fills scaler state during modeset setup. Prefill helpers are queried by prefill/VRR logic after scaler use is known or in worst-case mode.

### State, Persistence, And Dependencies
The header owns no state and relies on forward declarations for display, CRTC, plane, atomic, DSB, and mode types. State is held in `intel_crtc_state` and `intel_plane_state`, then persisted by the implementation to scaler MMIO.

### Integration Points
Used by universal plane code, CRTC atomic checks, panel fitter code, CASF, display readback, workarounds, and prefill/VRR calculations.

### Risks
Consumers must preserve the staging/setup/programming ordering; programming with an unallocated `scaler_id` is invalid. Prefill helpers are estimates and should not be treated as exact hardware timing unless implementation improves the FIXME paths.

### Test Signals
Build coverage plus runtime scaling tests for plane and pipe users, CASF, scaler detach/readback, and prefill-driven guardband/CDCLK behavior validate the interface.
