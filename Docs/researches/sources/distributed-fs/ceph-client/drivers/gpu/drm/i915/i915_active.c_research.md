<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.c

### Purpose
`i915_active.c` implements i915's composite GPU activity tracker. It records the latest fence per timeline plus an optional exclusive fence, provides active/retire callbacks around resource lifetime, waits or wires dependencies onto active GPU work, and supports idle barriers that defer retirement through engine kernel-context requests.

### Important APIs, Types, And Functions
The main APIs are `__i915_active_init()`, `i915_active_add_request()`, `i915_active_set_exclusive()`, `i915_active_acquire()`, `i915_active_acquire_if_busy()`, `i915_active_release()`, `__i915_active_wait()`, `i915_request_await_active()`, `i915_sw_fence_await_active()`, `i915_active_fini()`, `i915_active_acquire_preallocate_barrier()`, `i915_active_acquire_barrier()`, `i915_request_add_active_barriers()`, `__i915_active_fence_set()`, `i915_active_fence_set()`, `i915_active_create()`, `i915_active_get()`, `i915_active_put()`, `i915_active_module_init()`, and `i915_active_module_exit()`. Internal state uses `struct active_node`, `struct i915_active`, `struct i915_active_fence`, rb-trees, RCU fence pointers, dma-fence callbacks, low-level lists, and a slab cache.

### Control Flow
Initialization sets locks, the rb-tree, cached node, exclusive tracker, preallocated barrier list, work item, and debug object state. Callers acquire an active ref before adding requests. `i915_active_add_request()` finds or allocates the per-timeline node, replaces pending barriers when needed, installs the request fence callback, and ensures timeline ordering by awaiting the previous fence. Fence callbacks clear the RCU pointer and call `active_retire()`, which decrements the active count and either retires immediately or queues work if retirement may sleep. Final retirement prunes the tree to one reusable cached node, calls the owner's retire callback, wakes waiters, and frees discarded nodes.

Wait and dependency APIs snapshot existing active fences, enable signaling, optionally flush idle barriers, and attach waits to either an i915 request or software fence. Barrier acquisition preallocates per-physical-engine proto-nodes while active, inserts them into the active rb-tree, queues them on engine `barrier_tasks`, and later `i915_request_add_active_barriers()` links them onto a kernel-context barrier request fence so retirement happens after that request.

### State, Persistence, And Dependencies
State persists in `atomic_t count`, `mutex`, `tree_lock`, timeline rb-tree, cached node, `excl` fence, flags, callbacks, work item, preallocated barriers, and the module-global active-node slab cache. RCU protects fence pointer reads, dma-fence locks protect callback list migration, `tree_lock` protects rb-tree mutation, and the active mutex serializes first activation. Dependencies include dma-fence, i915 requests/timelines, engine PM and barrier tasks, debugobjects, workqueues, lockdep, RCU, and the i915 selftest include.

### Integration Points
GEM objects, VMAs, contexts, and other i915 resources embed `struct i915_active` to defer freeing or mutation until GPU access has ceased. Request submission calls `i915_active_add_request()` or `i915_active_fence_set()`. Other requests and software fences call the await helpers to synchronize with current resource activity.

### Risks
The code is highly concurrency-sensitive: fence memory can be RCU-reused, callback lists migrate between old and new fences, active count transitions trigger lifetime callbacks, and barriers are manipulated from low-level lists without the normal timeline lock in some paths. Missing acquire/release pairing can leak activity or retire too early. Barrier proto-nodes use `ERR_PTR(-EAGAIN)` in the fence pointer, so callers must not treat all non-NULL fence values as real fences.

### Test Signals
Signals include i915 selftests for active tracking, concurrent add/wait/release stress, exclusive and per-timeline dependency ordering, RCU fence reuse scenarios, barrier preallocation on virtual and physical engines, `I915_ACTIVE_RETIRE_SLEEPS` workqueue retirement, interruptible wait behavior, module init/exit slab checks, and debugobject assertions under `CONFIG_DRM_I915_DEBUG_GEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.c -->
