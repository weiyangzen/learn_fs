## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.h

### Purpose

`vlv_dsi.h` exposes the small public interface for the VLV/BXT/GLK DSI implementation to the rest of i915 display code while allowing non-i915 builds to compile with inert stubs.

### Important APIs, types, and functions

It forward-declares `enum port`, `struct intel_crtc_state`, `struct intel_display`, and `struct intel_dsi`. When `I915` is enabled it declares `vlv_dsi_wait_for_fifo_empty()`, `vlv_dsi_min_cdclk()`, and `vlv_dsi_init()`. Otherwise it provides no-op or zero-return inline stubs.

### Control flow

There is no runtime control flow beyond stub selection at compile time. Callers can unconditionally include the header and rely on the build configuration to provide either the real DSI implementation or inert functions.

### State and persistence behavior

The header stores no state. The real functions manage DSI panel, encoder, hardware, and clock state in `vlv_dsi.c`.

### Dependencies

It depends only on type forward declarations and the `I915` build macro. The implementation depends on the broader DRM/i915 display subsystem.

### Integration points

`vlv_dsi_init()` is called from display initialization to create DSI outputs when VBT reports a panel. `vlv_dsi_min_cdclk()` feeds cdclk constraints for DSI modes. `vlv_dsi_wait_for_fifo_empty()` is used during DSI disable paths.

### Risks

The stubs hide DSI behavior in non-i915 builds, so callers must not rely on side effects when `I915` is disabled. Signature drift between the header and implementation would break display initialization.

### Test signals

Build tests with and without `I915` defined, plus display initialization tests that confirm DSI panels are discovered only through the real implementation.
