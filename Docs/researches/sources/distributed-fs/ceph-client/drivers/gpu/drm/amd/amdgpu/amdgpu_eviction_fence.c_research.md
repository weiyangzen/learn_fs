# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eviction_fence.c

## Purpose
`amdgpu_eviction_fence.c` implements per-file eviction fences used to coordinate user-queue eviction and resume with BO reservation objects. When a BO is associated with an unsignaled eviction fence, consumers waiting on that BO trigger user queue suspension before memory eviction or validation proceeds.

## Important APIs, types, and functions
Public manager operations are `amdgpu_evf_mgr_init()`, `amdgpu_evf_mgr_rearm()`, `amdgpu_evf_mgr_attach_fence()`, `amdgpu_evf_mgr_detach_fence()`, `amdgpu_evf_mgr_shutdown()`, `amdgpu_evf_mgr_flush_suspend()`, and `amdgpu_evf_mgr_fini()`. Internal dma-fence operations include driver/timeline naming and `amdgpu_eviction_fence_enable_signaling()`, which schedules the suspension worker. The worker is `amdgpu_eviction_fence_suspend_worker()`.

## Control flow
Manager initialization allocates a dma-fence context, starts with a stub fence, and initializes suspension work. Rearming allocates a new `amdgpu_eviction_fence`, initializes it with a per-manager sequence number and current task name, replaces the manager's current fence, and attaches it to every already locked GEM object in the supplied `drm_exec`. Attaching a BO validates it to allowed domains and adds the current unsignaled fence to its reservation object as a bookkeeping fence. Fence signaling is enabled by scheduling suspend work. The worker locks the file's user queue manager, begins a dma-fence signaling section, gets the current eviction fence, evicts user queues, signals the fence while still holding `userq_mutex`, drops the fence, optionally schedules resume work, and unlocks.

## State and persistence behavior
State lives in `struct amdgpu_eviction_fence_mgr`: fence context, atomic sequence, RCU-protected current fence, work item, and shutdown flag. Individual eviction fences hold a dma-fence, spinlock, task-derived timeline name, and backpointer to the manager. There is no durable persistence; fences are synchronization state for one DRM file lifetime.

## Dependencies and integration points
The file depends on dma-fence, dma-resv, TTM validation, DRM exec locked-object iteration, AMDGPU BO placement, and `amdgpu_userq_evict()` / user queue resume work. It is called from GEM open/close and file release paths.

## Risks and edge cases
Ordering is delicate: signaling must occur while holding `userq_mutex` so queues are not resumed before the next fence is installed. RCU access to `ev_fence` must always take references safely. Shutdown must flush work after making the flag visible. `amdgpu_evf_mgr_attach_fence()` can validate BO placement while handling eviction synchronization, so error propagation matters. Replacement with a stub fence on detach depends on the unique fence context.

## Test signals
Signals include user-queue eviction on fence wait, automatic resume scheduling after eviction, BO reservation bookkeeping fence insertion/removal, GEM open/close interactions, file release with pending work, shutdown flush behavior, and stress tests with concurrent VM BO operations and user queues.
