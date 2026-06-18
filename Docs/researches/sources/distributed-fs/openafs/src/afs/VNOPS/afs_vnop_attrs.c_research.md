# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_attrs.c

## Purpose

`afs_vnop_attrs.c` implements vnode attribute retrieval and update. It converts OpenAFS vcache metadata to Unix `vattr`, verifies and fetches status when needed, maps Unix attribute updates into AFS store-status requests, handles truncation/writeback, and supports disconnected-mode attribute updates.

## Important APIs, Types, and Functions

- `afs_CopyOutAttrs` copies cached vcache metadata to a platform `vattr`, including mode, uid/gid, fsid, inode number, link count, size, times, dataversion-derived subsecond/gen fields, block size, and block count.
- `afs_getattr` is the vnode getattr operation.
- `afs_VAttrToAS` converts a `vattr` update mask to `struct AFSStoreStatus`.
- `afs_setattr` is the vnode setattr operation.
- `afs_CreateAttr` and `afs_DestroyAttr` allocate/free `struct vattr` from small-space allocation.

## Control Flow

`afs_getattr` handles fakestat mountpoints first, returns cached attributes for hint/UBC cases on some platforms, otherwise enters the disconnected lock, verifies uncached status, flushes pages/text where needed, copies attributes, and performs NFS exporter mode/inode adjustments.

`afs_setattr` creates a request, evaluates fakestat, rejects read-only volumes, checks write permission for size changes, rejects disconnected writes unless write-disconnected mode is active, converts attributes to `AFSStoreStatus`, and handles truncation/growth. Size changes mark the vcache dirty, truncate or extend segments, optionally store segments asynchronously, update modtime, flush text, and then either call `afs_WriteVCache` online or `afs_WriteVCacheDiscon` offline.

## State and Persistence Behavior

Getattr reads from vcache status and may verify/fetch freshness. Setattr mutates vcache state, dcache segments, dirty flags, dataversions, modtime, callback freshness, and remote fileserver status. In disconnected write mode it records local state for later replay. Attribute allocation uses UKERNEL/OSI small-space memory.

## Dependencies and Integration Points

It depends on fakestat, disconnected locking, vcache verification, access checks, segment truncation/extension/store, `afs_WriteVCache`, `afs_WriteVCacheDiscon`, NFS exporter state, cell SUID policy, volume lookup for mountpoint roots, and platform vnode/page-cache helpers.

## Risks and Edge Cases

Dataversion is encoded into subsecond fields differently per platform. SUID/SGID bits are masked for no-SUID cells. Size changes have complex interactions with dirty state, store timing, NFS translator writer counts, and disconnected mode. If online `afs_WriteVCache` fails after local mutation, the vcache is marked stale but callers still need robust error handling.

## Test Signals

Test getattr on regular files, directories, mountpoints, fake-stat mountpoints, root vnodes, no-SUID cells, NFS-exported paths, and stale vcaches. Test setattr for chmod, chown, chgrp, mtime, truncate shrink/grow, read-only volumes, disconnected read-only, disconnected write replay, and store failure stale marking.
