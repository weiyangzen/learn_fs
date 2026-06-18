# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.h

### Purpose
`intel_wm.h` declares the common display watermark API used by atomic modeset, driver initialization, modeset setup/readback, plane visibility checks, debug logging, and debugfs registration.

### Important APIs, Types, And Functions
It exports compute, initial, atomic update, optimize, global compute, hardware readback, sanitize, plane visibility, latency printing, initialization, and debugfs registration functions. It forward-declares the core display, CRTC, atomic, CRTC state, and plane state types.

### Control Flow
The header supports the lifecycle implemented in `intel_wm.c`: initialize backend, compute during atomic check, program initial/intermediate/optimized watermarks during commit, read and sanitize on setup, then expose debugfs hooks.

### State, Persistence, And Dependencies
No state is stored in the header. State flows through `intel_display`, `intel_atomic_state`, `intel_crtc`, and plane/CRTC state objects into backend-specific hardware programming. Dependency footprint is limited to Linux types and forward declarations.

### Integration Points
Used by display driver init, modeset setup, atomic commit, plane checks, debugfs, and platform-specific watermark implementations such as i9xx and SKL.

### Risks
Callers must respect backend availability and ordering; e.g. compute before update, sanitize after readback. `intel_wm_plane_visible()` policy should be used consistently by backends to avoid cursor underruns or unnecessary watermarks.

### Test Signals
Build coverage across platform watermark backends and runtime atomic commit paths, plus debugfs and modeset setup tests, validate the interface.
