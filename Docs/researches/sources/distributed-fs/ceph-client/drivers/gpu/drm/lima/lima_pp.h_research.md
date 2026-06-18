<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.h

## Purpose
Declares Lima PP IP lifecycle, broadcast pseudo-IP lifecycle, and PP scheduler pipe APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_device`. Exports `lima_pp_*()`, `lima_pp_bcast_*()`, `lima_pp_pipe_init()`, and `lima_pp_pipe_fini()`.

## Control flow
No executable flow exists in the header.

## State and persistence
No state is stored here.

## Dependencies and integration points
Used by `lima_device.c` IP descriptors and pipe initialization.

## Risks
Prototype drift affects PP device lifecycle and scheduler setup.

## Test signals
Build coverage and PP render submissions validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.h -->
