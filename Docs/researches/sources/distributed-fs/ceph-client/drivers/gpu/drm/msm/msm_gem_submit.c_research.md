# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_submit.c

## Purpose
Implements the legacy MSM GEM command submission ioctl. It converts userspace submit descriptions into DRM scheduler jobs, validates and pins GEM buffers, handles explicit and implicit synchronization, optionally patches relocations, creates userspace-visible fences, and pushes work to the selected GPU submit queue.

## Important APIs, Types, and Functions
- `msm_ioctl_gem_submit()` is the ioctl entry point and main control-flow owner.
- `submit_create()` allocates `struct msm_gem_submit`, allocates a hardware fence, initializes `drm_sched_job`, binds the queue, ring, context VM, pid, and submit identity.
- `submit_lookup_objects()` bulk-copies BO descriptors, validates flags, and looks up GEM handles under `file->table_lock`.
- `submit_lookup_cmds()` validates command descriptors and copies relocation arrays; VM_BIND contexts must provide direct IOVAs and no relocs or submit index/offset.
- `submit_lock_objects()` locks the VM reservation object and BOs with `drm_exec`; VM_BIND mode uses `drm_gpuvm_prepare_vm()` and `drm_gpuvm_prepare_objects()`.
- `submit_fence_sync()` adds implicit dependencies unless suppressed globally or per-BO.
- `submit_pin_objects()` maps and pins BOs in the context VM, stores `vm_bo` refs and IOVAs, and moves objects to the pinned LRU state.
- `submit_attach_object_fences()` attaches the scheduler fence to object reservations or, for VM_BIND, to the GPUVM reservation object and `vm->last_fence`.
- `submit_reloc()` maps command buffers CPU-side and patches relocation targets.
- `msm_submit_retire()` releases BO and GPUVM references after scheduler/GPU retirement.

## Control Flow
The ioctl validates pipe and flags, rejects unusable VMs, obtains the submitqueue, allocates an optional output fence fd, creates a submit, and serializes per-queue submission with `queue->lock`. It imports input sync-file fences, parses syncobj dependencies, parses post-dependencies, copies BO and command arrays, locks all relevant reservation objects, attaches implicit dependencies, pins objects, validates command stream bounds, and applies relocations for non-VM_BIND contexts. It arms the scheduler job, allocates or validates a userspace fence id in `queue->fence_idr`, creates a sync-file if requested, attaches reservation fences, validates the VM when using VM_BIND, dumps RD debug data, and pushes the job to the DRM scheduler. Error paths unwind fd allocation, syncobjs, locks, pins, submit references, and queue references.

## State and Persistence
Submit state is transient but reference-counted across ioctl, scheduler, ring in-flight list, and retirement. Persistent per-context state includes `queue->last_fence`, `queue->fence_idr`, scheduler entities, `ctx` accounting updated later on retirement, and `vm->last_fence` in VM_BIND mode. BO pin and LRU state persists until retire or error cleanup. No disk persistence exists.

## Dependencies and Integration Points
Integrates with `msm_gpu.h` structures, `msm_ringbuffer` scheduler backend, MSM GEM VMA/pin helpers, `msm_syncobj.c`, Linux `sync_file`, DRM scheduler, DRM GPUVM, dma-resv implicit sync, IDR fence lookup, RD debug capture, and GPU tracepoints. It feeds jobs to `msm_ringbuffer.c`, which eventually calls `msm_gpu_submit()`.

## Risks
Primary risk areas are userspace input validation, relocation bounds and ordering, correct lock/pin/unpin ordering under reclaim, fence-id IDR races, error-path reference balancing, and VM_BIND differences. The code intentionally avoids `copy_from_user()` while holding ww locks and separates page acquisition from LRU locking to reduce deadlock risk. VM unusable state is checked before accepting new jobs.

## Test Signals
Exercise submit with valid and invalid BO flags, handles, command sizes, relocations, sync-file in/out, syncobj timeline dependencies, explicit fence sequence numbers, disabled implicit sync, VM_BIND contexts, and closed contexts. Expected observability includes `trace_msm_gpu_submit`, fence-id waitability, RD dumps, no GEM ref leaks, no lockdep complaints, and correct scheduler retirement.
