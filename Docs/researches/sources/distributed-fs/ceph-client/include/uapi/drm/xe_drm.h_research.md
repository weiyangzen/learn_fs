<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/xe_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/xe_drm.h

## Purpose
Defines the Linux UAPI contract for Intel Xe DRM userspace clients: device discovery, GEM allocation and mmap offsets, VM lifecycle, VM binding, execution queues, GPU submission, user fence waits, observation/performance streams, madvise memory attributes, PXP state, EU stall sampling, and DRM RAS enum names. It is an ABI header, so field order, reserved fields, extensibility chains, and ioctl numbers are compatibility-critical.

## Important APIs, Types, And Functions
The exported ioctls are `DRM_IOCTL_XE_DEVICE_QUERY`, `DRM_IOCTL_XE_GEM_CREATE`, `DRM_IOCTL_XE_GEM_MMAP_OFFSET`, `DRM_IOCTL_XE_VM_CREATE`, `DRM_IOCTL_XE_VM_DESTROY`, `DRM_IOCTL_XE_VM_BIND`, `DRM_IOCTL_XE_EXEC_QUEUE_CREATE`, `DRM_IOCTL_XE_EXEC_QUEUE_DESTROY`, `DRM_IOCTL_XE_EXEC_QUEUE_GET_PROPERTY`, `DRM_IOCTL_XE_EXEC`, `DRM_IOCTL_XE_WAIT_USER_FENCE`, `DRM_IOCTL_XE_OBSERVATION`, `DRM_IOCTL_XE_MADVISE`, `DRM_IOCTL_XE_VM_QUERY_MEM_RANGE_ATTRS`, `DRM_IOCTL_XE_EXEC_QUEUE_SET_PROPERTY`, and `DRM_IOCTL_XE_VM_GET_PROPERTY`. Core structs include `drm_xe_device_query`, query reply structs for engines/memory/GT/topology/firmware/OA/PXP/EU stalls, `drm_xe_gem_create`, `drm_xe_vm_create`, `drm_xe_vm_bind_op`, `drm_xe_vm_bind`, `xe_vm_fault`, `drm_xe_exec_queue_create`, `drm_xe_sync`, `drm_xe_exec`, `drm_xe_wait_user_fence`, `drm_xe_observation_param`, `drm_xe_madvise`, and memory range attribute query structs. `drm_xe_user_extension` and `drm_xe_ext_set_property` are the shared extension-chain mechanism.

## Control Flow
Typical userspace flow queries device capabilities, creates GEM buffers and a VM, binds BOs or userptr ranges into the VM, creates an execution queue for selected engine class/instance data, submits batch buffers through `DRM_IOCTL_XE_EXEC`, and waits with sync objects or user fences. Observation streams are opened/configured through `DRM_IOCTL_XE_OBSERVATION` and then controlled with stream-fd ioctls. VM bind supports arrays of bind operations, async sync signaling, prefetch, unmap, userptr mapping, dumpable/PXP checks, CPU address mirroring, decompression, and madvise-autoreset behavior.

## State And Persistence
Kernel state is held in DRM file-private objects: GEM handles, VM ids, exec queue ids, bound VMAs, sync object relationships, observation stream fds, and per-VM fault reporting. The header exposes persistent ABI object handles, not implementation storage. Memory placement and attributes can change through migration, madvise, fault handling, purgeable state, and preferred-location policy. Reserved fields and zero-required extension tails preserve forward compatibility.

## Dependencies And Integration Points
Depends on generic DRM UAPI definitions from `drm.h`. It integrates with Mesa/compute runtimes, libdrm-style userspace, dma-buf/PRIME, syncobj timelines, mmap, GPU scheduler and GuC submission, platform memory regions, PXP protected-content management, perf/OA tooling, and DRM RAS netlink naming. Hardware-specific topology, GT, OA, and firmware details are intentionally queried instead of hard-coded by userspace.

## Risks And Edge Cases
Main risks are ABI drift, nonzero reserved fields, broken 32/64-bit pointer handling, stale two-step query sizing, invalid memory placement masks, VM bind races, userptr lifetime bugs, overcommit/fault-mode differences, long-running VM synchronization restrictions, PXP invalidation, purgeable BO access after DONTNEED, and observation stream overflow/lost reports. Integer sizes, alignment, pointer fields stored in `__u64`, and compact ioctl numbering are sensitive.

## Test Signals
Useful signals include UAPI compile checks, libdrm/Mesa ioctl smoke tests, two-pass query resize tests, GEM create/mmap/bind/exec/wait round trips, VM fault delivery tests, syncobj and user-fence ordering tests, invalid reserved-field rejection tests, memory migration and purgeable-state tests, OA/EU stall read/poll/error-path tests, PXP invalidation handling, and ABI layout comparison across 32-bit and 64-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/xe_drm.h -->
