# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.c

## Purpose

`amdgpu_userq_fence.c` bridges user-mode queue progress into the Linux `dma_fence`, DRM syncobj, and BO reservation model. User queues expose progress through GPU-written seq64 memory. This file allocates that seq64 memory, creates dma-fences whose sequence numbers are queue write pointers, publishes those fences to BO reservations and syncobjs, and returns wait metadata so another user queue can wait on AMDGPU user queue fences by polling GPU VAs.

## Important APIs And Functions

`amdgpu_userq_fence_driver_alloc()` allocates `struct amdgpu_userq_fence_driver`, seq64 memory via `amdgpu_seq64_alloc`, a dma-fence context, timeline name, refcount, and the fence list lock. `amdgpu_userq_fence_driver_destroy()` cancels and signals remaining fences with `-ECANCELED`, frees seq64 memory, and releases the driver. `amdgpu_userq_fence_driver_get/put()` wrap kref lifetime.

`amdgpu_userq_fence_driver_process()` reads the seq64 value, cuts all pending fences whose `seqno <= rptr` into a temporary list, signals them, drops their retained external fence driver arrays, and releases the fence references. `amdgpu_userq_fence_driver_force_completion()` marks the latest queue fence canceled, writes its seqno into seq64 memory, and processes the list.

`amdgpu_userq_fence_alloc()` allocates a fence and drains `userq->fence_drv_xa` into `fence_drv_array`, taking references to external fence drivers. This prevents wait-created dependencies from accumulating indefinitely in the queue and makes the new fence responsible for releasing them when it signals. `amdgpu_userq_fence_init()` initializes `dma_fence`, updates `last_fence`, puts it on the driver's pending list if not already signaled, and starts hang detection.

`amdgpu_userq_signal_ioctl()` looks up syncobjs, BO read/write handles, and the target queue; reads the queue wptr from the queue's VM mapping; creates a userq dma-fence; locks BO reservations with `drm_exec`; adds read/write fences to BO reservation objects; and replaces the requested syncobjs. `amdgpu_userq_wait_ioctl()` either counts relevant fences or returns an array of GPU VA/value pairs for AMDGPU userq fences, falling back to blocking waits on non-userq fences.

## Control Flow And State

Signal flow is: validate feature and handle counts, duplicate user arrays, look up objects, get queue, read wptr, create fence, release queue-manager mutex, lock BO reservations, publish fence, and unwind references. Wait flow is two-phase: with `num_fences == 0`, it counts syncobj and BO reservation fences so userspace can size a buffer; with a nonzero count, it gathers fences, deduplicates them, finds userq fences, stores their fence-driver references in the wait queue xarray, and copies `va/value` pairs to userspace.

Persistent state is in-memory plus GPU-visible seq64 memory. Each fence driver owns seq64 CPU/GPU/VA addresses and a pending fence list. Each queue owns a primary fence driver, a temporary xarray of external fence drivers, and `last_fence`. BO reservations and syncobjs receive fence references that outlive the IOCTL.

## Dependencies And Integration

The file integrates with `amdgpu_userq.h`, `amdgpu_seq64`, AMDGPU VM/BO lookup, `drm_exec`, GEM object lookup, DRM syncobj APIs, dma-resv, dma-fence unwrap/dedup helpers, xarray, RCU fence release, and user-copy helpers. It relies on the queue manager's `userq_mutex` being held by `amdgpu_userq_get()` paths and explicitly unlocks it after fence initialization.

## Risks And Test Signals

Important risks include fence-driver lifetime bugs, xarray draining errors, incorrect use of `xas_find_marked` when no free mark is available, lock ordering between queue mutexes, BO reservations, and fence list locks, user pointer/count overflow, blocking waits on non-AMDGPU fences, stale wptr mappings, and lost completion if seq64 memory is freed too early. The code also caps handle arrays at `1 << 16` but needs tests for zero, max, and malicious counts.

Test signals should cover signal IOCTL with read/write BOs and syncobjs, wait IOCTL count and return modes, timeline syncobj unwrapping, non-userq fence fallback waits, queue destruction with pending waits, forced completion on reset, concurrent signal/wait/destruction, invalid user pointers, missing queue ids, wptr BO mapping failures, fence IRQ processing, and stress with many external fence drivers.
