<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.h

## Purpose
Declares the Lima L2 cache lifecycle and flush API.

## Important APIs, types, and functions
Forward declares `struct lima_ip` and exports init/fini/resume/suspend plus `lima_l2_cache_flush()`.

## Control flow
No executable flow exists in the header.

## State and persistence
No state is stored here.

## Dependencies and integration points
Used by device IP descriptors and scheduler/cache maintenance paths.

## Risks
Prototype changes affect device init and task cache-management code.

## Test signals
Build coverage and runtime L2 flush tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.h -->
