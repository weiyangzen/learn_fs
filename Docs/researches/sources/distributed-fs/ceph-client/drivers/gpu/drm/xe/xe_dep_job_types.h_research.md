# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_job_types.h

## Purpose
This header defines a generic dependency job abstraction layered on top of the DRM GPU scheduler. It lets Xe schedule non-engine work only after dependency fences have signaled.

## Important APIs, Types, and Functions
It defines `struct xe_dep_job_ops` with `run_job` and `free_job` callbacks, and `struct xe_dep_job` containing a base `drm_sched_job` plus operation pointers.

## Control Flow
There is no executable flow in the header. The scheduler implementation calls `ops->run_job` when DRM scheduler dependencies are satisfied and `ops->free_job` when the job is released.

## State and Persistence Behavior
Each dependency job persists as a DRM scheduler job until dependencies complete and scheduler cleanup calls the free hook. The operation table defines job-specific lifetime behavior.

## Dependencies and Integration Points
It includes `<drm/gpu_scheduler.h>` and is consumed by `xe_dep_scheduler.c` and users such as exec queue dependency scheduling.

## Risks
Callback contracts must be honored: `run_job` must return a valid fence or error-style fence according to DRM scheduler expectations, and `free_job` must release job-private allocations exactly once. Missing ops would crash at scheduler callback time.

## Test Signals
Compile tests, dependency scheduler users submitting jobs with resolved/unresolved fences, cancellation/fini tests, and memory-leak checks for callback free paths are key signals.
