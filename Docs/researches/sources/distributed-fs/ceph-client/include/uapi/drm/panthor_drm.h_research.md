# sources/distributed-fs/ceph-client/include/uapi/drm/panthor_drm.h

## Purpose

`panthor_drm.h` defines the modern Panthor DRM UAPI for Arm Mali CSF GPUs. It documents strict extensibility rules and covers device queries, MMIO offset selection, VM lifecycle and VM_BIND, BO creation/mmap/sync/info/labels, scheduling groups and queues, command submission, group/VM state, tiler heaps, and synchronization operations. The complete 1305-line header was read.

## Important APIs, Types, and Functions

Ioctl IDs cover `DEV_QUERY`, `VM_CREATE/DESTROY/BIND/GET_STATE`, `BO_CREATE/MMAP_OFFSET/SYNC/QUERY_INFO/SET_LABEL`, `GROUP_CREATE/DESTROY/SUBMIT/GET_STATE`, `TILER_HEAP_CREATE/DESTROY`, and `SET_USER_MMIO_OFFSET`. Important shared types are `drm_panthor_obj_array` for stride-versioned arrays and `drm_panthor_sync_op` for binary/timeline syncobj waits/signals. Query structs cover GPU, CSIF, timestamp, and priority info. Runtime structs cover VM bind ops, BOs, queue/group creation and submission, tiler heaps, labels, MMIO offset override, and BO sync/query info.

## Control Flow

Userspace queries capabilities, creates a VM with a user/kernel VA split, creates BOs, binds BO ranges into the VM synchronously or asynchronously with sync operations, creates groups with queue definitions and core masks, creates tiler heaps if needed, submits command streams to queues inside a group, and queries VM/group state after faults. Flush-id optimization maps a read-only user MMIO page at a 32-bit or 64-bit-safe offset, with an override for emulation environments.

## State and Persistence Behavior

VM IDs, BO handles, exclusive-VM BO ownership, group handles, queues, tiler heap handles, labels, async VM bind queues, and group fault state are fd-scoped. Async VM_BIND failure can make a VM `UNUSABLE`; recovery requires a new VM. Timed out or fatally faulted groups reject new jobs. Imported BO info can require explicit sync even when the GPU is normally coherent.

## Dependencies and Integration Points

Depends on `drm.h` and uses `uintptr_t` in the object-array helper. Integrates with Panthor CSF firmware, VM page tables, DRM GEM/dma-buf, PRIME import/export policy, DRM syncobj/timeline syncobj, user command stream generation, cache maintenance, flush-id MMIO mapping, tiler heap firmware objects, and Mesa Panthor.

## Risks and Edge Cases

Compatibility rules are central: 64-bit alignment, natural alignment, zero padding, append-only ioctl IDs, stride-sized indirect arrays, version bumps, and no unions. VM_BIND async failure state, sync-only constraints, group priority privileges, core mask validation, queue stream alignment, imported BO cache requirements, exclusive-VM export restrictions, and 32-bit/64-bit MMIO offset mismatches are major edge cases.

## Test Signals

Cover dev query size-probe/partial-copy, MMIO offset selection/override, VM create/bind/get-state with async failure, BO create/exclusive export rejection/mmap/sync/import info/labels, group queue stride and core mask validation, priority permissions, submit alignment and sync ops, group fault state, tiler heap bounds, object-array forward/backward compatibility, and strict MBZ/unknown flag rejection.
