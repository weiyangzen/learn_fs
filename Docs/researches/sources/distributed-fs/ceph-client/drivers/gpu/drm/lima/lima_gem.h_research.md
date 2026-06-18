<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.h

## Purpose
Defines Lima GEM BO state and declares the GEM, heap, submit, and wait APIs.

## Important APIs, types, and functions
`struct lima_bo` embeds `drm_gem_shmem_object`, a mutex, VA mapping list, and heap size. Inline helpers convert GEM objects to Lima BOs, return BO size, and return the DMA reservation object. Prototypes cover heap allocation, object creation, handle creation, info query, submit, wait, and VMA flag setup.

## Control flow
Only simple inline accessors execute.

## State and persistence
The BO structure persists for the GEM object lifetime. The VA list tracks per-VM mappings and heap size tracks committed heap pages.

## Dependencies and integration points
Includes DRM GEM shmem helper and is used by IOCTL, VM, GP recovery, and scheduler submission code.

## Risks
The embedded shmem object layout is assumed by `to_lima_bo()`. Incorrect heap-size semantics can break mmap/pin restrictions and GP heap recovery.

## Test signals
Build coverage plus GEM create/submit/heap tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.h -->
