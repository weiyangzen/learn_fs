<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active_types.h

### Purpose
`i915_active_types.h` defines the storage layout for i915 active fence and active tracker objects without pulling in the full active API.

### Important APIs, Types, And Functions
It defines `struct i915_active_fence`, containing an RCU-protected `struct dma_fence *` and callback, and `struct i915_active`, containing reference count, mutex, rb-tree state, cached node, exclusive fence, flags, active/retire callbacks, work item, and preallocated barrier list. It also defines `I915_ACTIVE_RETIRE_SLEEPS`.

### Control Flow
There is no executable flow in this header. The layout supports the implementation's lifecycle: count transitions activate/retire, rb-tree nodes track per-timeline activity, `excl` tracks exclusive activity, work defers sleeping retirement, and `preallocated_barriers` stages barrier nodes.

### State, Persistence, And Dependencies
State persists wherever i915 embeds `struct i915_active`. The header depends on Linux atomics, dma-fence, llist, mutex, rb-tree, RCU, and workqueue types.

### Integration Points
This header lets low-level i915 structures embed active trackers while avoiding larger include dependencies. `i915_active.h` builds the public API on top of these types.

### Risks
The forward-declared `struct active_node` and cache/rb-tree fields are private to `i915_active.c`; external users should not manipulate them. Layout changes can affect lockdep/debugobject assumptions and any structure embedding these types.

### Test Signals
Build coverage and i915 active selftests catch layout and dependency regressions. Runtime lockdep/debugobject tests catch bad lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active_types.h -->
