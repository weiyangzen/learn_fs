<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.h

## Purpose
Declares Lima PMU lifecycle APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and exposes init/fini/resume/suspend.

## Control flow
No executable flow exists here.

## State and persistence
No state is stored here; PMU state is held in `struct lima_ip` and hardware registers.

## Dependencies and integration points
Used by the IP descriptor table in `lima_device.c`.

## Risks
Prototype drift breaks PMU lifecycle setup.

## Test signals
Build coverage and runtime suspend/resume power sequencing validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pmu.h -->
