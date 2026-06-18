# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.c

## Purpose
This file implements Nouveau's DRM scheduler integration for software jobs. It wraps `drm_sched_job`, translates Nouveau VM bind and similar operations into scheduler work, handles syncobj dependencies and outputs, and tracks in-flight jobs for orderly scheduler teardown.

## Important APIs, Types, and Functions
Key APIs are `nouveau_job_init`, `nouveau_job_submit`, `nouveau_job_fini`, `nouveau_job_done`, `nouveau_job_free`, `nouveau_sched_create`, and `nouveau_sched_destroy`. Internal helpers cover input dependency lookup, output syncobj/timeline fence preparation and attachment, scheduler backend callbacks, timeout handling, and scheduler/workqueue setup.

## Control Flow
Job initialization copies user-provided wait/signal sync arrays, initializes the DRM scheduler job, and records caller-provided `nouveau_job_ops`. Submit first adds input fences, prepares output sync objects, serializes through `sched->mutex`, runs the operation-specific `submit` callback while failure is still allowed, arms the scheduler job, stores the done fence, optionally calls `armed_submit`, attaches output fences, pushes the job, and optionally waits for synchronous jobs. Scheduler run calls the job's `run` hook; scheduler free calls `nouveau_job_fini`.

## State and Persistence Behavior
State is per job: copied sync arrays, output syncobj references, fence chains, `done_fence`, state enum, client/file pointers, and list membership in `sched->job.list`. Scheduler state includes a DRM scheduler, one entity, an optional owned workqueue, a submit mutex, an in-flight job list, and a waitqueue used by teardown.

## Dependencies and Integration Points
It depends on DRM GPU scheduler, DRM syncobj/timeline sync, dma fences, `drm_gpuvm_exec`, Nouveau client/file state, and operation implementations such as UVMM bind jobs. `nouveau_sched_destroy` waits until `nouveau_job_done` removes every job before finalizing the scheduler.

## Risks
The submit path relies on the operation-specific `submit` hook not failing after jobs are armed. Missing `nouveau_job_done` would hang scheduler destruction. Sync jobs reject explicit in/out sync arrays, so ioctl validation must keep async semantics straight. Output timeline chains must be freed on all error paths.

## Test Signals
Useful signals include async VM bind tests with syncobj waits/signals, timeline syncobj point updates, forced operation submit failures, scheduler timeout injection, synchronous job wait behavior, and driver unload while jobs are still completing.
