<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.h

## Purpose
Declares the Lima broadcast unit interface used by device initialization and the PP scheduler path.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and exposes lifecycle calls plus `lima_bcast_enable()`, `lima_bcast_mask_irq()`, and `lima_bcast_reset()`.

## Control flow
No runtime flow exists here. Callers use the declarations to initialize, suspend/resume, enable, mask, and reset broadcast programming.

## State and persistence
No state is declared beyond using `struct lima_ip` and `struct lima_device` from including contexts.

## Dependencies and integration points
Used by `lima_device.c` for IP lifecycle and `lima_pp.c` for multi-PP task dispatch and recovery.

## Risks
The header references `struct lima_device` without its own forward declaration, relying on include order in current users.

## Test signals
Build coverage catches signature drift; runtime coverage comes from Mali450 broadcast rendering paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.h -->
