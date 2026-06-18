# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.h

## Purpose
This header defines the user-mode GPUVM data structures and public functions for Nouveau's DRM GPUVM based VM_BIND implementation.

## Important APIs, Types, and Functions
It defines `struct nouveau_uvmm`, `struct nouveau_uvma_region`, `struct nouveau_uvma`, `struct nouveau_uvmm_bind_job`, and `struct nouveau_uvmm_bind_job_args`. It declares VM init/bind ioctl handlers, UVMM teardown, BO map/unmap-all callbacks, conversion macros, and simple mutex lock/unlock helpers.

## Control Flow
The header has no executable control flow beyond inline locking helpers. It establishes ownership: `nouveau_uvmm` wraps `drm_gpuvm`, `nouveau_uvma` wraps `drm_gpuva`, and bind jobs embed `nouveau_job` for scheduler execution.

## State and Persistence Behavior
The structures persist the raw NVIF VMM, GPUVM object, sparse-region maple tree, UVMM mutex, sparse-region completion/dirty state, UVMA region/kind/page-shift metadata, and bind job operation list/completion/kref.

## Dependencies and Integration Points
It depends on DRM GPUVM and Nouveau driver, BO, memory, and scheduler declarations. It is included by BO move code, ioctl code, and UVMM implementation.

## Risks
The container macros require embedded object layout to remain stable. Lock helpers expose a single mutex that callers must use consistently with DRM GPUVA and GEM reservation locks.

## Test Signals
Build coverage, VM_BIND ioctl tests, BO move remap tests, and teardown with sparse regions verify the header contract.
