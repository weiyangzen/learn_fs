<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.h

## Purpose
Declares the Lima GP IP lifecycle and scheduler pipe setup APIs.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and `struct lima_device`. Exports GP init/fini/resume/suspend plus `lima_gp_pipe_init()` and `lima_gp_pipe_fini()`.

## Control flow
No executable flow exists here.

## State and persistence
No state is stored; implementations operate on IP and device objects.

## Dependencies and integration points
Used by `lima_device.c` to initialize the GP IP and GP scheduler pipe.

## Risks
Signature drift breaks device initialization and scheduler callback installation.

## Test signals
Build coverage and GP task execution validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.h -->
