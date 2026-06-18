# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_buffer_pool.c

### Purpose
`intel_gt_buffer_pool.c` implements a small reusable pool of internal GEM buffers, mainly for command parser shadow copies. It caches read-only internal objects by size bucket and map type, keeps them active while requests reference them, returns idle buffers to the shrinker, and reaps stale entries.

### Important APIs, Types, And Functions
Public functions are `intel_gt_get_buffer_pool()`, `intel_gt_buffer_pool_mark_used()`, `intel_gt_init_buffer_pool()`, `intel_gt_flush_buffer_pool()`, and `intel_gt_fini_buffer_pool()`. Key internals are `bucket_for_size()`, `node_create()`, `pool_retire()`, `pool_free_older_than()`, `pool_free_work()`, and `node_free()`.

### Control Flow
Requests round the desired size to pages and scan an RCU-protected bucket for a node with sufficient size and matching map type. Claiming a node atomically changes `age` from a nonzero jiffies value to zero, removes it from the list, and acquires its `i915_active` reference. New nodes allocate internal GEM objects and mark them read-only. `mark_used()` pins pages and hides the object from the shrinker; active request tracking returns the node to the pool through `pool_retire()`, which unpins pages, makes the object purgeable, records an age, and schedules delayed reap work.

### State, Persistence, And Dependencies
State lives in `intel_gt.buffer_pool`: four size buckets, a spinlock, delayed work, and per-node active state, GEM object pointer, RCU list node, age, map type, and pinned flag. It depends on GEM internal object allocation, i915 active tracking, shrinker visibility, RCU list deletion, unordered workqueue execution, and request association from callers.

### Integration Points
Command parser and other GT clients request temporary shadow buffers and attach the node to an `i915_request` through the header helper. GT init/fini initializes and asserts the pool is empty, while driver remove flushes stale nodes.

### Risks
The pool relies on `age == 0` meaning active/claimed and nonzero meaning reusable. Race bugs in RCU claiming or list removal could double-use a buffer. Buffers must be marked active after being used, otherwise they can return to the pool too early. Delayed cleanup uses `spin_trylock_irq()`, so stale buffers can persist until a later pass.

### Test Signals
Test buffer reuse by size bucket and map type, concurrent get/put/retire paths, failure in object allocation or active acquire, request completion returning nodes, shrinker visibility toggling, flush on driver remove, and final empty-list assertions.
