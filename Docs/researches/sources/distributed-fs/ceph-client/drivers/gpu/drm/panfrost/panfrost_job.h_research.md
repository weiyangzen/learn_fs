# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.h

## Purpose
This header defines Panfrost job and job-manager context structures plus the job manager API used by ioctl, device, reset, and scheduler code.

## Important APIs, Types, and Functions
`struct panfrost_job` embeds `drm_sched_job` and stores device, MMU, JM context, fences, job chain address, requirements, flush id, BO/mapping arrays, render fence, and profiling fields. `NUM_JOB_SLOTS` is 3. `struct panfrost_jm_ctx` owns scheduler entities per slot. The header declares job push/put, slot selection, JM lifecycle, IRQ helpers, idle test, and context handle helpers.

## Control Flow
The header has no executable flow. It defines the data contract consumed by submit ioctls, scheduler callbacks, IRQ handlers, resets, dumps, and fd cleanup.

## State and Persistence Behavior
Jobs persist from ioctl creation until scheduler/free and IRQ completion drop all refs. JM contexts persist per DRM file until destroyed or file close, but jobs can hold refs after the userspace handle is removed.

## Dependencies and Integration Points
It includes Panfrost UAPI and DRM GPU scheduler headers. It is included by driver ioctl code, job implementation, dump code, and device state definitions.

## Risks
Field ownership is subtle: `engine_usage` may be nulled when a file context is destroyed, while jobs continue. BO and mapping arrays must be cleaned after scheduler completion. Any new job requirement bits must stay synchronized with ioctl validation and slot selection.

## Test Signals
Build coverage, submit/timeout/reset tests, context create/destroy, fd close races, and devcoredump generation validate the interface.
