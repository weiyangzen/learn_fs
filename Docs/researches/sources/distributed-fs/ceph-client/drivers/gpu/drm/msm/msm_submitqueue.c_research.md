# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_submitqueue.c

## Purpose
Manages MSM per-context submit queues and scheduler entities. It creates/destroys queues, maps userspace priority to rings and DRM scheduler priorities, supports VM_BIND-specific queues, tracks fence IDR state and fault counts, closes queues on file release, and manages per-context sysprof state.

## Important APIs, Types, and Functions
- `msm_context_set_sysprof()` applies per-context profiling mode and balances GPU PM/sysprof refs.
- `__msm_context_destroy()` destroys scheduler entities, releases VM, labels, and context memory.
- `msm_submitqueue_create()` creates legacy or VM_BIND queues and inserts them into `ctx->submitqueues`.
- `msm_submitqueue_init()` creates the default queue id 0.
- `msm_submitqueue_get()`, `msm_submitqueue_put()`, and `msm_submitqueue_destroy()` manage queue refs.
- `msm_submitqueue_close()` removes all queues and closes the context VM.
- `msm_submitqueue_query()` returns queue fault counters.
- `msm_submitqueue_remove()` removes non-default queues.
- `get_sched_entity()` lazily creates per-context/per-ring/per-priority DRM scheduler entities.

## Control Flow
Queue creation validates GPU/context availability. VM_BIND queues require a VM_BIND context, priority zero, and use the VM's scheduler with an embedded scheduler entity. Non-VM_BIND queues validate priority through `msm_gpu_convert_priority()`, reject incompatible preemption flags, and reuse a per-context entity for FIFO behavior at a given ring/priority. The queue is refcounted, assigned an increasing context-local id under `queuelock`, initializes fence IDR and locks, and is appended to the context list. Close removes all queues, flushes VM_BIND entities, drops refs, and then closes the VM.

## State and Persistence
State is in `struct msm_context` and `struct msm_gpu_submitqueue`: submitqueue list, queue ids, scheduler entity table, fence IDR, queue locks, fault counters, sysprof mode, context labels, VM ref, and krefs. All state is per DRM file/context and in-memory.

## Dependencies and Integration Points
Depends on DRM scheduler entities, MSM GPU priority conversion, runtime PM for sysprof, VM close from `msm_gem_vma.c`, and submit/VM_BIND ioctl queue lookup. Fault counts are incremented by GPU recovery and queried via UAPI.

## Risks
Risks include scheduler entity sharing assumptions, queue removal racing submits, VM_BIND queue lifetime, sysprof ref/PM imbalance, and correct default queue semantics. The context close path relies on no more user ioctls, so it uses less locking while tearing down queues.

## Test Signals
Create/remove queues at many priorities, query faults, verify id 0 cannot be removed, create VM_BIND queues only in VM_BIND contexts, close files with queued jobs, check scheduler entity reuse/FIFO behavior, and test sysprof transitions 0/1/2 with PM refs.
