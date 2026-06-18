<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.h

### Purpose
`i915_dpt.h` declares i915 display page-table helpers and the display DPT interface object.

### Important APIs, Types, And Functions
It forward-declares `struct intel_dpt`, `struct i915_address_space`, and `struct i915_vma`, and declares `i915_dpt_to_vm()`, `i915_dpt_pin_to_ggtt()`, `i915_dpt_unpin_from_ggtt()`, `i915_dpt_offset()`, and `i915_display_dpt_interface`.

### Control Flow
Display code creates a DPT through the interface, converts it to an address space for binding, pins it to GGTT for hardware visibility, reads the offset, and later unpins/destroys it.

### State, Persistence, And Dependencies
The header owns no state. State is hidden in the private `struct intel_dpt` implementation.

### Integration Points
It is the bridge between shared Intel display code and i915-specific DPT address-space/GEM handling.

### Risks
The `struct intel_dpt` internals are intentionally opaque; callers must use the declared helpers and interface callbacks to preserve pin and VM lifetime rules.

### Test Signals
Build integration with display DPT users and runtime DPT pin/unpin tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dpt.h -->
