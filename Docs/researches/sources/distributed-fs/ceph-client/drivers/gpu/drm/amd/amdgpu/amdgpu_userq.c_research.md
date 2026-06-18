<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.c

## Purpose
`amdgpu_userq.c` implements usermode queue management for AMDGPU. It exposes queue create/free ioctl behavior, validates queue/rptr/wptr VM mappings, pins doorbells, creates MQDs through IP-specific callbacks, maps/preempts/restores/unmaps queues, integrates eviction fences and VM validation, processes userqueue fence IRQs, detects hangs, participates in suspend/resume and GPU reset, and supports scheduling isolation controls.

## Important APIs, Types, And Functions
`amdgpu_userq_get_supported_ip_mask` reports supported userqueue IPs from `adev->userq_funcs`. Reset/hang logic is handled by `amdgpu_userq_is_reset_type_supported`, `amdgpu_userq_detect_and_reset_queues`, `amdgpu_userq_start_hang_detect_work`, `amdgpu_userq_process_fence_irq`, and `amdgpu_userq_reset_work`. VM/VA helpers include `amdgpu_userq_input_va_validate`, `amdgpu_userq_buffer_vas_mapped`, and cleanup helpers. Queue state helpers wrap IP-specific `preempt`, `restore`, `unmap`, and `map` callbacks and transition `AMDGPU_USERQ_STATE_*`.

Object and doorbell helpers are `amdgpu_userq_create_object`, `amdgpu_userq_destroy_object`, and `amdgpu_userq_get_doorbell_index`. The ioctl path is `amdgpu_userq_ioctl`, which delegates to `amdgpu_userq_create` or queue free. Eviction/restore uses `amdgpu_userq_ensure_ev_fence`, `amdgpu_userq_vm_validate`, `amdgpu_userq_restore_worker`, `amdgpu_userq_evict_all`, and `amdgpu_userq_evict`. Manager lifecycle is `amdgpu_userq_mgr_init`, cancel/fini, suspend/resume, isolation stop/start, VA unmap validation, and pre/post reset hooks.

## Control Flow
Queue creation checks priority permissions, resumes runtime PM, validates IP support and input addresses, allocates a queue object, records queue metadata, reserves the VM root BO, validates queue/rptr/wptr virtual mappings, pins the doorbell BO in the doorbell domain, allocates a fence driver, creates an MQD, ensures a live eviction fence, optionally maps the queue, allocates a queue ID, stores the queue in both per-file and global doorbell xarrays, initializes debugfs and hang detection, increments type count, and returns the queue ID.

Queue free erases the queue from the per-file xarray and drops the kref. Destruction cancels resume/hang work, reserves the root BO, removes VA mapping marks, waits the last fence, removes debugfs, unmaps the queue, decrements type count, destroys MQD/fence/doorbell xarray state under reset-domain protection, unpins doorbell and wptr BOs, frees the queue, and drops runtime PM.

Eviction waits all last fences, preempts mapped queues, and on failure triggers queue reset detection. Restore worker runs when the eviction fence has signaled, validates the whole VM, repins userptr pages through HMM, updates page tables, rearms eviction fences, and restores all queues whose VA mappings remain present.

## State And Persistence
Per-process state lives in `struct amdgpu_userq_mgr`: queue xarray, mutex, delayed resume work, device/file pointers, and per-type counts. Per-queue state persists queue type, VM, doorbell object/index, wptr object, MQD data owned by IP callbacks, fence driver, last fence, VA cursor list, delayed hang work, priority, xcp ID, and state enum. Global interrupt lookup is `adev->userq_doorbell_xa`.

## Dependencies And Integration Points
The file depends on DRM auth/master checks, runtime PM, DRM exec locking, AMDGPU VM and HMM, TTM validation, BO reservation/pinning, doorbell BAR indexing, userqueue fence driver, IP-specific `amdgpu_userq_funcs`, reset domains, KFD-adjacent SRAM ECC/reset behavior indirectly through recovery, debugfs, and eviction fence manager integration.

## Risks
This is concurrency-heavy. Queue state is accessed by ioctl, delayed work, IRQ, suspend/resume, eviction, and reset paths. The create path has multiple cleanup labels and must keep runtime PM, MQD, fence driver, VA marks, doorbell pinning, xarray entries, and mutex state paired. The visible source shows success and some cleanup paths calling `mutex_unlock(&uq_mgr->userq_mutex)` in `amdgpu_userq_create`; tests should confirm the lock is actually held on all paths in this tree. `amdgpu_userq_cleanup` calls `list_del(&queue->userq_va_list)` after individual cursor cleanup, so list-head ownership should be audited. VA mapping marks are atomic bo_va flags shared with unmap validation; missed cleanup can leave false positives. IRQ-side xarray lookup and delayed hang work cancellation must avoid use-after-free.

## Test Signals
Create/free queues for GFX, compute, and SDMA; invalid VA/size/priority/doorbell inputs; high priority with and without `CAP_SYS_NICE` or DRM master; VA unmap while queues exist; eviction fence signaling and restore with userptr BOs; suspend/resume for S0ix and normal paths; per-queue reset fallback to full GPU reset; IRQ fence processing with pending fences; isolation stop/start by XCP; runtime PM reference balancing; lockdep/KASAN/KCSAN coverage for xarray, delayed work, and queue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.c -->
