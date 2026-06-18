# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.h

## Purpose
This header declares the generic Xe dependency scheduler API.

## Important APIs, Types, and Functions
It forward-declares scheduler, DRM entity, workqueue, and Xe device types, then exposes `xe_dep_scheduler_create`, `xe_dep_scheduler_fini`, and `xe_dep_scheduler_entity`.

## Control Flow
There is no executable flow. Callers create a scheduler, obtain its DRM scheduler entity for job submission, and later finalize it.

## State and Persistence Behavior
The header stores no state; it describes ownership of a heap-allocated scheduler object managed by create/fini.

## Dependencies and Integration Points
It is included by code that needs a dependency-only scheduler, especially exec queue infrastructure. It hides the internal DRM scheduler wrapper layout.

## Risks
Callers must not use the returned entity after `xe_dep_scheduler_fini`. Header/API drift would break scheduler users at build time.

## Test Signals
Build coverage plus create/submit/fini tests with dependency jobs validate the contract.
