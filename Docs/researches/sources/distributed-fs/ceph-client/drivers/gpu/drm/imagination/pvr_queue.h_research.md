# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.h

## Purpose
Defines the public queue data structures and API for PowerVR job scheduling. It exposes the per-queue state used by contexts, jobs, firmware event processing, and reset handling while keeping most scheduler/fence mechanics implemented in `pvr_queue.c`.

## Important APIs, types, and functions
- `struct pvr_queue_fence_ctx` holds a dma-fence context ID, sequence counter, and spinlock.
- `struct pvr_queue_cccb_fence_ctx` extends the base fence context with the single job waiting for CCCB space and a mutex.
- `struct pvr_queue_fence` wraps a `dma_fence`, the creating queue, and deferred release work.
- `struct pvr_queue` holds the DRM scheduler/entity, job type, owning context, active/idle node, in-flight counter, CCCB and job fence contexts, timeline UFO firmware object/mapping, last scheduled fence, CCCB, register-state object, firmware context offset, and callstack address.
- Declares queue job lifecycle, queue lifecycle, firmware event processing, reset hooks, and device-level init/fini functions.

## Control flow
The header has no executable control flow beyond declarations. The exposed lifecycle is device queue init, per-context queue creation, per-job init/arm/push/cleanup, firmware event processing through `pvr_queue_process()`, reset stop/start through device pre/post reset, queue kill/destroy, and device queue finalization.

## State and persistence
The structures declared here are persistent runtime state. `pvr_queue` objects live with a PowerVR context but can outlive handle destruction while jobs/fences hold references. Fence contexts persist for sequence allocation over the queue lifetime. The timeline UFO is firmware-visible state used to signal and wait for native queue fences.

## Dependencies and integration points
Includes DRM GPU scheduler, Linux workqueue declarations, `pvr_cccb.h`, and `pvr_device.h`; forward-declares `pvr_context`. The declarations are used by context management, job submission, power reset, firmware event processing, and other code that needs to test UFO-backed fences.

## Risks
The header exposes mutable queue internals, so changes to structure layout or locking expectations can affect several subsystems. The `pvr_queue_cccb_fence_ctx` comment documents an important invariant: only one CCCB-space waiter should exist because scheduler entity submission is serialized. Callers must respect queue lifetime and use kill/destroy in the intended order.

## Test signals
Build coverage catches structural and signature drift. Runtime coverage comes from context creation/destruction, job submit/cleanup, reset, firmware event processing, fence release work, and CCCB-space wait/unwait paths.
