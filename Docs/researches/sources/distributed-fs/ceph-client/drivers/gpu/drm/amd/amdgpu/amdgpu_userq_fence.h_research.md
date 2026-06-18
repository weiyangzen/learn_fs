# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq_fence.h

## Purpose

`amdgpu_userq_fence.h` declares the data structures and entry points for the user queue fence subsystem. It is the header consumed by queue lifecycle code, IOCTL dispatch, reset paths, and fence IRQ handling to allocate, process, force-complete, and publish user queue synchronization.

## Important Types And APIs

`struct amdgpu_userq_fence` embeds `struct dma_fence` as `base`, a spinlock required by dma-fence operations, a list link for the driver's pending-fence list, and an array of retained `amdgpu_userq_fence_driver` pointers. That array carries external userq fence-driver dependencies returned by wait IOCTLs so they can be released when the next queue fence is signaled.

`struct amdgpu_userq_fence_driver` owns the seq64 progress memory (`va`, `gpu_addr`, `cpu_addr`), a dma-fence context, `fence_list_lock`, the list of pending fences, the AMDGPU device pointer, a kref, and a task-derived timeline name. It is the per-queue object that turns a GPU-written sequence value into dma-fence completion.

The exported functions are lifetime helpers (`amdgpu_userq_fence_driver_alloc/free/get/put/destroy`), progress helpers (`amdgpu_userq_fence_driver_process`, `amdgpu_userq_fence_driver_force_completion`), and IOCTL entry points (`amdgpu_userq_signal_ioctl`, `amdgpu_userq_wait_ioctl`).

## Control Flow And Integration

The header reflects a split between per-queue fence-driver state and per-fence objects. Queue creation allocates a fence driver. User signal creates fences and publishes them to reservations/syncobjs. Fence IRQ or forced reset paths process or complete the driver. Queue teardown frees the driver and drops any wait-derived driver references.

Dependencies include Linux `types.h`, dma-fence structures through included AMDGPU headers, `amdgpu_userq.h`, xarray ownership from `struct amdgpu_usermode_queue`, and DRM IOCTL dispatch types. The header is intentionally small but sits on a high-risk boundary between userspace synchronization ABI and kernel fence lifetime rules.

## State, Risks, And Tests

State is not persistent across driver lifetime; it is GPU-visible through seq64 memory and kernel-visible through lists/refcounts. Risks are mostly lifetime and lock-rule related: dangling fence-driver pointers, missed kref drops, fence list corruption, and forced completion racing normal signaling. Test signals should include allocation/free failure paths, queue destruction with pending fences, repeated wait/signal cycles that create external driver arrays, reset cancellation, and dma-fence callback/wait correctness.
