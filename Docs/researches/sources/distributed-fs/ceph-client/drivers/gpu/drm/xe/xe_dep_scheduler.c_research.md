# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.c

## Purpose
This file implements a small Xe wrapper around the DRM GPU scheduler for generic dependency jobs. It runs callback-based jobs once their fences are ready, without tying the work to a hardware engine scheduler.

## Important APIs, Types, and Functions
The private `struct xe_dep_scheduler` contains a `drm_gpu_scheduler`, one `drm_sched_entity`, and an RCU head for deferred free. Public functions are `xe_dep_scheduler_create`, `xe_dep_scheduler_fini`, and `xe_dep_scheduler_entity`. Static scheduler ops map DRM callbacks to `xe_dep_job_ops`.

## Control Flow
Creation allocates the wrapper, initializes a DRM scheduler with one run queue, the provided workqueue, a credit limit from `job_limit`, no finite timeout, and the device pointer. It then initializes a single scheduler entity. Runtime job dispatch calls `xe_dep_scheduler_run_job`, which downcasts to `xe_dep_job` and invokes its `run_job`; cleanup invokes `free_job`. Fini tears down entity and scheduler, then frees the wrapper through RCU because scheduler fences can export timeline names.

## State and Persistence Behavior
The scheduler object persists until `xe_dep_scheduler_fini`. Jobs persist in DRM scheduler queues and are freed by their callbacks. RCU-delayed freeing protects external fence/timeline readers after scheduler teardown.

## Dependencies and Integration Points
It depends on DRM GPU scheduler, Xe device types, and `xe_dep_job_types.h`. It is used by exec queue code for deferred dependency-driven work such as resource freeing or invalidation sequencing.

## Risks
The wrapper assumes one entity and one scheduler run queue are enough for its users. Incorrect `job_limit` can throttle or over-admit dependency jobs. Fini must not race live submissions. Job callback bugs propagate through the DRM scheduler context.

## Test Signals
Dependency-job submission tests, scheduler teardown with exported fences, job-limit pressure, workqueue-backed execution, and callback free coverage are relevant signals.
