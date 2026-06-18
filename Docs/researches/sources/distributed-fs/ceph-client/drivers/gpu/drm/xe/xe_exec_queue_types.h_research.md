<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue_types.h

## Purpose
`xe_exec_queue_types.h` defines the execution queue data model, priority enums, multi-queue group state, queue flags, scheduling properties, long-running state, TLB invalidation tracking, PXP metadata, and backend operation contract.

## Important APIs, types, and functions
It defines `enum xe_exec_queue_priority`, `enum xe_multi_queue_priority`, `struct xe_exec_queue_group`, `struct xe_exec_queue`, flag bits such as `EXEC_QUEUE_FLAG_KERNEL`, `VM`, `MIGRATE`, and `LOW_LATENCY`, TLB invalidation slot constants, `XE_MAX_JOB_COUNT_PER_EXEC_QUEUE`, and `struct xe_exec_queue_ops`. Backend ops cover init/kill/fini/destroy, scheduling property updates, multi-queue priority, suspend/wait/resume, reset status, and active state.

## Control flow and integration points
There is no executable control flow, but the structure layout defines the runtime contract for GuC and execlist backends, exec ioctl, VM bind, LR compute mode, PXP termination, fdinfo accounting, and SR-IOV migration fixups.

## State and persistence behavior
`struct xe_exec_queue` is persistent for the queue lifetime. It stores VM/file refs, engine class/logical mask/name/width, backend union state, multi-queue membership, scheduler properties, LR preemption fence state, dependency schedulers and TLB fences, VM/hw-engine-group links, user fence syncobj, replay state, DRM sched entity, job count, LRC lookup lock, and an LRC flex array.

## Dependencies, risks, and test signals
Dependencies include DRM scheduler, kref, hardware engine, LRC, fence, and Xe GPU scheduler types. Risks include backend union misuse, missing initialization of links/locks, flex-array width bugs, property state not propagated to backend, and queue flags with incompatible semantics. Test signals include backend init/fini, multi-queue group stress, LR preemption, TLB invalidation ordering, PXP queue handling, job-count throttling, and KASAN/lockdep during queue destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue_types.h -->
