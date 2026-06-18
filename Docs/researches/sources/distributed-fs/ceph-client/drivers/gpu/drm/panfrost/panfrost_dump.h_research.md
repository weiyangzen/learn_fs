# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.h

## Purpose
This header declares the Panfrost core dump entry point.

## Important APIs, Types, and Functions
It forward-declares `struct panfrost_job` and declares `void panfrost_core_dump(struct panfrost_job *job)`.

## Control Flow
There is no executable flow. The job timeout path includes this header and invokes the dump function with the timed-out job.

## State and Persistence Behavior
The header stores no state. The implementation reads job/device/BO state and emits devcoredump data.

## Dependencies and Integration Points
It is an integration point between the job manager and dump implementation while avoiding a full job header dependency for callers that only need the prototype.

## Risks
Signature drift between the declaration and implementation would break build. Callers must pass a live job whose BO and mapping arrays are still valid.

## Test Signals
Build coverage and timeout-driven dump generation validate the interface.
