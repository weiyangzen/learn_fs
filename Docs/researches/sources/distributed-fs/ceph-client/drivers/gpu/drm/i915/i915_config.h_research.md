<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.h

### Purpose
`i915_config.h` declares fence timeout helpers for i915.

### Important APIs, Types, And Functions
It declares `i915_fence_context_timeout(u64 context)` and defines inline `i915_fence_timeout()` as a call with `U64_MAX`.

### Control Flow
Callers either request a timeout for a specific fence context or use the generic nonzero-context wrapper.

### State, Persistence, And Dependencies
The header has no state and depends on Linux integer limits/types.

### Integration Points
Fence wait call sites include this header to use i915's configured timeout policy.

### Risks
The generic wrapper intentionally forces a nonzero context, so it will enable configured timeout behavior. Callers needing context-zero semantics must call the underlying function directly.

### Test Signals
Compile coverage and direct helper tests for timeout conversion are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_config.h -->
