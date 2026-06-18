<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.h

### Purpose
`i915_display_pc8.h` declares the i915 implementation of the shared Intel display PC8 interface.

### Important APIs, Types, And Functions
It declares `extern const struct intel_display_pc8_interface i915_display_pc8_interface`.

### Control Flow
There is no executable logic. Display initialization code binds to the callback table implemented in `i915_display_pc8.c`.

### State, Persistence, And Dependencies
The header has no state and relies on consumers having the interface type available.

### Integration Points
It connects i915 uncore forcewake handling to the display power-management layer.

### Risks
As with other minimal interface headers, include ordering must provide the interface type where needed.

### Test Signals
Build integration and display power-management tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_display_pc8.h -->
