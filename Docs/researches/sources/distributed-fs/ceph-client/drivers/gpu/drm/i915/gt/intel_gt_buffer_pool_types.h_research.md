# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool_types.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool_types.h

### Purpose
`intel_gt_buffer_pool_types.h` defines the data structures backing the GT buffer pool.

### Important APIs, Types, And Functions
It defines `struct intel_gt_buffer_pool` with a spinlock, four cache lists, and delayed cleanup work, plus `struct intel_gt_buffer_pool_node` with `i915_active`, GEM object, list linkage, pool/free/RCU union, age, map type, and pinned state.

### Control Flow
The fields support the implementation's claimed versus cached transitions: `age` marks reusable nodes, `active` links GPU request lifetime to retirement, `link` places cached nodes in buckets, and the union supports active ownership, stale free chains, or RCU freeing.

### State, Persistence, And Dependencies
The types persist inside `struct intel_gt` and per cached object. Dependencies are Linux list/spinlock/workqueue primitives, GEM object types, and i915 active types.

### Integration Points
Included by `intel_gt_types.h` to embed the pool in every GT and by the public buffer-pool API.

### Risks
The union requires strict lifecycle separation: a node cannot simultaneously be in a pool, stale free chain, and RCU callback. `pinned` is represented as `u32` and must match actual GEM page pin state.

### Test Signals
Static checking, KASAN/KCSAN runs around get/retire/free, and teardown assertions that all cache lists are empty provide the main signals.
