# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vcache.c

## Purpose

`osi_vcache.c` implements UKERNEL vnode/vcache allocation, initialization, attachment, and hold helpers used by generic OpenAFS vcache code.

## Important APIs, Types, and Functions

- `osi_TryEvictVCache` flushes a vcache only if its vnode refcount is zero, it has no opens, and it is not marked `CUnlinkedDel`.
- `osi_NewVnode` allocates a `struct vcache`.
- `osi_PrePopulateVCache` zeroes a newly allocated vcache.
- `osi_AttachVnode` is a no-op in UKERNEL.
- `osi_PostPopulateVCache` attaches the global VFS and vnode ops to the embedded vnode and defaults the type to `VREG`.
- `osi_vnhold` increments the vnode refcount through `VN_HOLD`.

## Control Flow

Generic vcache creation calls allocate, prepopulate, and postpopulate hooks around OpenAFS cache initialization. Eviction tests the UKERNEL vnode refcount before calling `afs_FlushVCache`.

## State and Persistence Behavior

The file mutates in-memory vcache/vnode metadata only. It depends on `afs_globalVFS` and `afs_ops` to attach a usable vnode.

## Dependencies and Integration Points

It integrates with vcache management, `AFSTOV`, `VREFCOUNT_GT`, `VN_HOLD`, `vSetType`, and the `Afs_vnodeops` table from `osi_vnodeops.c`.

## Risks and Edge Cases

`osi_AttachVnode` ignores the sequence argument. `osi_NewVnode` returns raw allocated memory and requires the caller to run `osi_PrePopulateVCache`. `osi_PostPopulateVCache` defaults every vnode to regular file until later status processing updates type.

## Test Signals

Test vcache allocation paths, refcount increments, postpopulate ops/VFS assignment, and eviction refusal for open, referenced, or unlinked-delete vcaches.
