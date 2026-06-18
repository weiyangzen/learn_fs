# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.h

## Purpose

`amdgpu_userq.h` defines the public in-driver contract for AMDGPU user-mode queues. User queues let a DRM file/process own queue state directly while the kernel still manages object allocation, doorbells, VM validation, reset/suspend/resume hooks, eviction fences, hang detection, and synchronization integration. The header is a coordination point between user queue IOCTL handling, hardware-specific MQD programming, eviction fencing, and the `amdgpu_userq_fence` bridge.

## Important APIs, Types, And Data

The main state machine is `enum amdgpu_userq_state`: unmapped, mapped, preempted, hung, and invalid-VA. `struct amdgpu_userq_obj` wraps CPU pointer, GPU address, and backing BO for objects such as MQD, doorbell, firmware, and wptr storage. `struct amdgpu_userq_va_cursor` records GPU VAs that are relevant to validation and unmap detection.

`struct amdgpu_usermode_queue` is the per-queue object. It stores queue type, state, doorbell handle/index, queue flags, MQD properties, VM pointer, four queue-owned objects, `fence_drv` state, the last user queue fence, XCP id, priority, debugfs node, hang-detection delayed work, refcount, and a list of tracked VAs. It also owns `fence_drv_lock` and `fence_drv_xa`, which protect references to external fence drivers discovered by wait IOCTLs until the next signaled fence or queue destruction.

`struct amdgpu_userq_funcs` is the hardware abstraction for creating/updating/destroying MQDs, map/unmap, preempt/restore, and detect/reset. `struct amdgpu_userq_mgr` is a per-DRM-file manager with an xarray of queue ids, a mutex, the device, resume work, file pointer, and per-ring-type queue counts. `struct amdgpu_db_info` carries doorbell resolution inputs.

Exports include queue lookup/refcounting (`amdgpu_userq_get/put`), the userq IOCTL, manager init/fini/cancel, BO object create/destroy, eviction fence maintenance, doorbell lookup, supported IP mask checks, suspend/resume, reset pre/post hooks, scheduler isolation hooks, hang detection work, fence IRQ processing, and VA validation helpers.

## Control Flow And Integration

The header shows the lifecycle shape: a file initializes `amdgpu_userq_mgr`, user IOCTLs create/map queues through hardware-specific `amdgpu_userq_funcs`, GPU work is tracked through `amdgpu_userq_fence_driver`, and teardown cancels resume/hang work, releases queue BOs, and drains fence references. Reset paths call `amdgpu_userq_pre_reset`, `amdgpu_userq_post_reset`, and `amdgpu_userq_reset_work`; isolation paths stop/start schedulers by index. VM integration is explicit through `amdgpu_userq_input_va_validate` and `amdgpu_userq_gem_va_unmap_validate`, which prevent stale queue pointers after GEM VA changes.

Dependencies include `amdgpu_eviction_fence.h`, DRM file/device types, AMDGPU VM and BO types, xarray, workqueues, debugfs, and dma-fence. The queue manager is embedded in `amdgpu_fpriv`, and the helper macros expose that relationship.

## State, Persistence, Risks, And Tests

State is in-memory and per-process: xarray queue maps, queue refcounts, delayed work, object GPU mappings, and fence-driver references. GPU-visible persistence is through BOs and doorbells; reset/suspend code must restore or invalidate it. Important risks are lifetime races between queue destruction, hang/reset work, fence IRQ completion, and wait IOCTL external fence references; stale VM addresses after unmap; queue count leaks; and inconsistent queue state transitions during reset or isolation.

Test signals include user queue create/map/unmap/preempt/restore IOCTL coverage, VM unmap invalidation, reset with active queues, suspend/resume with active and idle queues, hang detection, eviction fence behavior, doorbell allocation, supported IP mask gating, and stress tests for many queues up to `AMDGPU_MAX_USERQ_COUNT`.
