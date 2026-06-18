<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agpgart.h -->
# sources/distributed-fs/ceph-client/include/linux/agpgart.h

## Purpose
`agpgart.h` declares AGPGART frontend/user-facing kernel structures layered on top of the AGP backend and UAPI ioctl definitions.

## Important APIs, types, and functions
It defines `struct agp_info`, `agp_setup`, `agp_segment`, `agp_segment_priv`, `agp_region`, `agp_allocate`, `agp_bind`, `agp_unbind`, `agp_client`, `agp_controller`, `agp_file_private`, and `agp_front_data`. Flag bit numbers track file/client/controller validity and permissions.

## Control flow
The frontend tracks file private state, controllers, clients, memory regions, and bind/unbind requests while delegating actual memory/aperture operations to backend functions from `agp_backend.h`.

## State and persistence behavior
`agp_front_data` is the persistent frontend state: mutex, controller lists, file-private list, and backend acquisition flags. Per-process client/controller objects track allocated segments and memory pools.

## Dependencies and integration points
It depends on mutexes, backend AGP declarations, and UAPI AGPGART structures. It integrates char-device/ioctl frontend code with backend bridge management.

## Risks and test signals
Risks include frontend/backend lifetime mismatch, access flag errors, segment bookkeeping leaks, and ioctl ABI structure drift. Test signals include AGPGART ioctl tests, multi-client/controller use, mmap region validation, and backend acquire/release coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agpgart.h -->
