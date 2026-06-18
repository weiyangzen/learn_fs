# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.h

## Purpose
This header defines the Nouveau software job and scheduler interface used by UVMM and other submit paths that need DRM scheduler ordering, syncobj handling, and common lifecycle management.

## Important APIs, Types, and Functions
It defines `enum nouveau_job_state`, `struct nouveau_job_args`, `struct nouveau_job`, the embedded `struct nouveau_job_ops`, and `struct nouveau_sched`. It declares job lifecycle functions and scheduler create/destroy helpers. `to_nouveau_job` converts a `drm_sched_job` back to its Nouveau container.

## Control Flow
The header has no executable control flow, but its hook contract is important: `submit` may fail before arming, `armed_submit` is guaranteed after a successful `submit`, `run` executes from the DRM scheduler backend, `free` releases operation-specific state, and `timeout` is optional.

## State and Persistence Behavior
The structures persist copied sync arrays, output syncobj/fence-chain staging, a done fence, job state, client references, scheduler entity state, and a protected in-flight job list.

## Dependencies and Integration Points
It includes DRM GPUVM and GPU scheduler headers and is consumed by `nouveau_sched.c` and UVMM bind job code. It also depends on Nouveau client and DRM file concepts through `nouveau_drv.h`.

## Risks
The hook ordering contract must remain synchronized with the implementation. Callers must set `resv_usage`, `credits`, sync flags, and `ops` consistently or fence publication and reservation locking can be wrong.

## Test Signals
Build coverage catches signature drift. Runtime signals come from VM bind submission, scheduler teardown, timeout handling, and syncobj integration tests.
