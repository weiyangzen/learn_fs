# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.h

### Purpose
`intel_gt_buffer_pool.h` exposes the GT buffer pool API used by command parsing and other temporary-buffer users.

### Important APIs, Types, And Functions
It declares `intel_gt_get_buffer_pool()`, `intel_gt_buffer_pool_mark_used()`, init/flush/fini functions, and inline helpers `intel_gt_buffer_pool_mark_active()` and `intel_gt_buffer_pool_put()`.

### Control Flow
Callers obtain a node, pin/mark it used before writing or mapping, attach it to an `i915_request` with `mark_active()`, and release their active hold with `put()`. Retirement happens asynchronously through the active callback in the implementation.

### State, Persistence, And Dependencies
The header owns no state. It depends on `i915_active`, `i915_request`, `intel_gt_buffer_pool_types.h`, and the GEM warning helper used to verify that callers pinned before marking active.

### Integration Points
The API connects request lifetime to pooled GEM object reuse. It is part of GT initialization and teardown through the public init/flush/fini declarations.

### Risks
The inline `mark_active()` only warns if the node was not pinned; it cannot fix misuse. Callers must not drop the node without balancing the active acquisition.

### Test Signals
Compile coverage for users, runtime warnings when `mark_active()` is called without `mark_used()`, request completion returning nodes, and cleanup with no outstanding active nodes are useful signals.
