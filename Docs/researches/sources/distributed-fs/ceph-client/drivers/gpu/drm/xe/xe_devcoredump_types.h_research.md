# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump_types.h

## Purpose
This header defines the in-memory data structures used by Xe devcoredump capture and readout.

## Important APIs, Types, and Functions
`struct xe_devcoredump_snapshot` stores capture time, boot time, process identity, reason string, affected GT, deferred work item, GuC CT/log snapshots, GuC execution queue snapshot, HW engine snapshots, job snapshot, matched GuC capture node, VM snapshot, and formatted-read buffer metadata. `struct xe_devcoredump` wraps the snapshot with a mutex and a `captured` flag.

## Control Flow
The types are populated synchronously by `devcoredump_snapshot`, extended by deferred work, read by the devcoredump read callback, and freed/reset by the release callback. The `work_struct` embedded in the snapshot bridges immediate hang capture to later allocation-heavy capture.

## State and Persistence Behavior
Snapshot fields persist from first captured hang until userspace/kernel releases the devcoredump. The formatted read buffer may hold either the full dump or a chunk window. `captured` prevents overwriting the first failure with subsequent hangs.

## Dependencies and Integration Points
It depends on ktime, mutex, workqueue, hardware-engine types, and forward-declared GuC/VM/job snapshot types supplied by other Xe subsystems. `xe_device_types.h` embeds `struct xe_devcoredump` in `struct xe_device`.

## Risks
Because the structure aggregates many subsystem-owned snapshot pointers, free/reset code must match every capture field. The single matched-node model assumes one hardware-engine capture per devcoredump event. Process identity and reason strings must remain valid after the originating file/job is gone.

## Test Signals
Snapshot allocation/free leak tests, repeated hang suppression, deferred capture completion, VM/job/engine snapshot print coverage, and coredump release/reset tests validate the type contract.
