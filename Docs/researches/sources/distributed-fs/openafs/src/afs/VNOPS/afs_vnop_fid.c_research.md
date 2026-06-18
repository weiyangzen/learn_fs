# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_fid.c

## Purpose

`afs_vnop_fid.c` implements platform-specific vnode-to-filehandle conversion for NFS export paths. It is excluded from UKERNEL and compiled only for platforms defining `AFS_VNOP_FID_ENV`.

## Important APIs, Types, and Functions

The primary function is `afs_fid`, with signatures varying across AIX, SunOS, and other platforms. It builds either a compact `SmallFid` containing volume, vnode, cell index, and unique bits, or a magic translator fid containing the vnode address and `AFS_XLATOR_MAGIC`. Counters `afs_fid_vnodeoverflow` and `afs_fid_uniqueoverflow` track values too large for the compact fields.

## Control Flow

If shutting down, `afs_fid` returns `EIO`. If NFS root-only mode is off, or the vnode is `/afs`, or AIX translator credentials request it, the function builds a `SmallFid`. Otherwise it builds a magic fid so unsupported submounts fail or are ignored unless translated. Depending on platform, it writes into a supplied `struct fid` or allocates one with `AFS_KALLOC`.

## State and Persistence Behavior

No filesystem state is changed except overflow counters and possible vnode refcount hold in magic-fid paths. The returned fid is a transient handle used by NFS/export layers.

## Dependencies and Integration Points

It depends on cell lookup for `cellIndex`, global root vnode `afs_globalVp`, `afs_NFSRootOnly`, platform `struct fid`, `SmallFid`, and NFS translator credential checks. It integrates with export/mountd/NFS lookup paths outside UKERNEL.

## Risks and Edge Cases

The compact fid stores only limited cell, vnode, and unique bits, so overflow is counted but still truncates information. Magic fids include vnode addresses and require careful refcount handling. Platform signature differences make prototype drift risky. Because this file is not compiled for UKERNEL, grouped research should not treat it as part of libuafs runtime.

## Test Signals

Platform NFS export tests should verify root-only and submount behavior, SmallFid round trips, overflow counter increments, magic fid rejection/translation, shutdown `EIO`, and AIX iauth behavior.
