# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vnodeops.c

## Purpose

`osi_vnodeops.c` wires generic OpenAFS vnode operations into the UKERNEL `usr_vnodeops` table and provides read/write and inactive adapters.

## Important APIs, Types, and Functions

- `afs_vrdwr` dispatches `UIO_WRITE` to `afs_write` and all other directions to `afs_read`.
- `afs_inactive` ignores shutdown, asserts the vcache refcount is zero, and calls `afs_InactiveVCache`.
- `Afs_vnodeops` maps open, close, rdwr, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, and lockctl to OpenAFS implementations, with unsupported bmap/strategy/bread/brelse/ioctl entries set to bad ops/noops.
- `afs_ops` points at `Afs_vnodeops`.

## Control Flow

UKERNEL vnode callers dereference `v_op` set by `osi_PostPopulateVCache`. Read/write calls enter `afs_vrdwr`, which adapts `usr_uio` and credentials to `afs_read`/`afs_write`. Vnode release in `VN_RELE` eventually calls `afs_inactive`.

## State and Persistence Behavior

The operation table is static process state. `afs_inactive` can trigger vcache cleanup and state transitions in generic cache-manager code. Read/write persistence is handled by the underlying OpenAFS data paths.

## Dependencies and Integration Points

It integrates `sysincludes.h`'s `struct usr_vnodeops` with VNOPS implementations from `src/afs/VNOPS` and with vcache lifecycle code.

## Risks and Edge Cases

Unsupported vnode operations intentionally route to `afs_badop`; callers must not expect block-device or buffer-cache behavior in UKERNEL. `afs_vrdwr` treats anything other than `UIO_WRITE` as read, so direction values must be normalized.

## Test Signals

Test vnode operation table completeness, libuafs read/write paths, final-reference release calling inactive, and bad-op behavior for unsupported operations.
