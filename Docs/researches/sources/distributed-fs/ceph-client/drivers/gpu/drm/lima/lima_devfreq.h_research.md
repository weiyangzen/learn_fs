<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.h

## Purpose
Declares Lima devfreq state and APIs for initialization, teardown, utilization accounting, and PM transitions.

## Important APIs, types, and functions
`struct lima_devfreq` contains devfreq/cooling handles, simple_ondemand governor data, busy/idle times, last update time, busy count, and spinlock. Prototypes cover init/fini, busy/idle recording, resume, and suspend.

## Control flow
No executable flow exists in the header.

## State and persistence
The structure persists inside `struct lima_device` and is active only when an OPP table was found and devfreq registration succeeded.

## Dependencies and integration points
Includes devfreq, spinlock, and ktime headers. Used by device lifecycle and scheduler runtime accounting.

## Risks
All mutable fields require lock discipline because GP and PP completion paths can update accounting concurrently.

## Test signals
Build coverage plus devfreq load/suspend/resume tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.h -->
