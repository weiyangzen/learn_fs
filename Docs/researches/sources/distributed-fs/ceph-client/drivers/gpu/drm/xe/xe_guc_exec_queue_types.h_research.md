# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_exec_queue_types.h

## Purpose
Defines GuC-specific state attached to each `xe_exec_queue`.

## Important APIs, Types, And Functions
The main type is `struct xe_guc_exec_queue`, containing a parent queue pointer, RCU head, GPU scheduler, scheduler entity, static scheduler messages, async destroy work, resume timestamp, atomic state, work queue item head/tail, GuC ID, suspend wait queue and flags, and VF migration recovery flags.

## Control Flow
This header has no functions, but the fields indicate control-flow roles: scheduler messages travel through the GPU scheduler when allocations are disallowed, `destroy_async` defers final cleanup, wait queues coordinate suspends, and recovery flags drive cleanup/suspend/resume after VF migration.

## State And Persistence
The struct persists for the lifetime of the parent execution queue. `id` is allocated from the GuC ID manager, `state` is atomic for concurrent submission state transitions, and `needs_*` flags preserve recovery work across migration handling.

## Dependencies And Integration Points
Depends on scheduler types, Linux RCU, spinlock/workqueue/waitqueue infrastructure, and `struct xe_exec_queue`. Used by GuC submission, scheduling, suspend/resume, and SR-IOV migration recovery code.

## Risks And Test Signals
Risks center on lifetime and concurrency: exported fences require RCU-safe freeing, static messages must not exceed `MAX_STATIC_MSG_TYPE`, and suspend/resume flags must be cleared exactly once. Tests should exercise queue destruction, migration recovery, and suspend wait wakeups.
