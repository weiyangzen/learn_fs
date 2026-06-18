<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.h

## Purpose
Declares the Lima DLBU lifecycle, enable/disable, and register-programming API.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_device`. Exports `lima_dlbu_enable()`, `lima_dlbu_disable()`, `lima_dlbu_set_reg()`, and init/fini/resume/suspend functions.

## Control flow
No executable flow exists in the header.

## State and persistence
No state is stored here; callers pass `struct lima_device` or `struct lima_ip`.

## Dependencies and integration points
Used by `lima_device.c` for IP lifecycle and `lima_pp.c` for Mali450 task setup.

## Risks
Prototype drift would break PP task dispatch or device init.

## Test signals
Build coverage plus Mali450 DLBU render tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.h -->
