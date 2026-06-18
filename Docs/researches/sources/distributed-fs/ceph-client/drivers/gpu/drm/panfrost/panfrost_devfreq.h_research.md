# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.h

## Purpose
This header declares Panfrost devfreq state and lifecycle/accounting entry points.

## Important APIs, Types, and Functions
`struct panfrost_devfreq` contains devfreq and cooling handles, governor data, OPP table state, current/fast frequency, busy/idle timing buckets, last update timestamp, busy count, and a spinlock. It declares init/fini, suspend/resume, and busy/idle record functions.

## Control Flow
The header has no executable flow. It defines the interface used by device initialization, PM callbacks, job submission/completion, reset paths, and fdinfo reporting.

## State and Persistence Behavior
The struct is embedded in `struct panfrost_device`, so it persists for the device lifetime. Its timing fields are mutable runtime counters protected by `lock`.

## Dependencies and Integration Points
It includes devfreq, spinlock, and ktime headers and forward-declares Panfrost and cooling types. `panfrost_device.h` embeds it, while `panfrost_job.c` and `panfrost_device.c` use the function declarations.

## Risks
Callers must check whether devfreq was actually registered before assuming frequency scaling. The lock discipline around timing fields must be preserved because jobs can update utilization concurrently.

## Test Signals
Build coverage catches signature drift. Runtime tests should validate that job paths and PM paths can call the declared hooks when devfreq is present or skipped.
