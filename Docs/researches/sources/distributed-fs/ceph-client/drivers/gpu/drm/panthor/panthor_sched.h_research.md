# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.h

## Purpose
Declares the Panthor scheduler interface used by ioctl, VM/MMU, reset, firmware IRQ, reservation, and fdinfo paths.

## Important APIs, Types, and Functions
Forward declarations cover DRM scheduler, exec, file, memory stats, Panthor device/file/group/job, and UAPI create/submit/state structs. Public functions include group create/destroy/state/pool helpers, job create/ref/put/VM/update helpers, scheduler init/unplug/reset/suspend/resume hooks, MMU fault and VM-destruction notifications, firmware event reporting, and fdinfo memory/profiling gatherers.

## Control Flow
File-open code creates a group pool, ioctl paths create groups and jobs, submit paths prepare reservations and feed jobs to DRM scheduler, firmware IRQ code reports events to the scheduler, reset code brackets the scheduler with pre/post hooks, and VM destruction flushes scheduler eviction work before mappings vanish.

## State and Persistence
The header owns no state but exposes the lifecycle contracts for refcounted jobs and group pools. Group and job objects persist behind opaque handles/references until destroyed and all scheduler/fence references are released.

## Dependencies and Integration Points
Includes no concrete implementation headers beyond declarations, keeping scheduler internals private. It connects UAPI structs, DRM scheduler jobs, VM objects, Panthor file state, firmware events, and fdinfo accounting.

## Risks and Edge Cases
Callers must pair job references, destroy groups before VM teardown where possible, and call reset/suspend hooks in the expected order. `panthor_sched_report_fw_events()` accepts a raw event mask, so producer correctness matters.

## Test Signals
Compile and link coverage across Panthor modules, ioctl submit tests, reservation update tests, firmware event simulation, reset/suspend sequencing, and fdinfo collection validate this API surface.
