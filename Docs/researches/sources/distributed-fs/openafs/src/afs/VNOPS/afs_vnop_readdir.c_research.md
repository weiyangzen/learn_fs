# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_readdir.c

## Purpose
Implements directory iteration over AFS/Vice directory blobs and translates AFS directory entries into each platform's `dirent` representation.

## Important APIs, Types, and Functions
`BlobScan` skips page headers and free blobs using the directory page allocation bitmap. `afs_readdir_type` infers BSD/Darwin `d_type` from vnode parity or cached vcache status. `afs_readdir_move` serializes one `DirEntry` into the caller's uio with correct inode number, record length, name length, type, offset, and padding. `afs_readdir` and `afs_readdir2` drive the directory read.

## Control Flow and State
`afs_readdir` creates a request, evaluates fakestat, verifies the directory vcache, fetches the full directory dcache at chunk zero, waits for current data, and then iterates from the opaque uio offset. The loop uses `BlobScan` and `afs_dir_GetVerifiedBlob` to look ahead one entry, so it can size the previous entry to fill the user buffer exactly when the next entry will not fit. On EOF it returns any held previous entry, releases dcache/vcache locks, and sets `eofp` where the platform API expects it.

Readdir is read-only for server data, but it depends on fresh dcache state and `CStatd`. It consumes and updates uio offset/residual as an opaque blob cursor. It may consult volume `mtpoint` and vcache `mvid.parent` to report stable inode numbers for `.` and `..` across volume roots and mountpoints. The broader system tracks in-progress readdir with `CReadDir`, `readdir_pid`, and `dcreaddir`, which lookup and bulk stat use to avoid deadlocks.

## Dependencies and Integration Points
Integrates with the AFS directory package, dcache freshness and lock rules, fakestat helpers, volume lookup, `afs_calc_inum`, platform `dirent` layouts, `AFS_UIOMOVE`, and vnode type information cached by lookup/bulk stat. Linux has a separate implementation, so changes that affect shared semantics must be mirrored there.

## Risks and Test Signals
The code carries many platform-specific layout assumptions. Small user buffers can return `EINVAL` when no entry fits. Correct `.` and `..` inode reporting across root volumes and mountpoints is subtle and depends on cached parent and volume state. Directory offsets are AFS blob indices, not byte offsets.

Test root volumes, mountpoint targets, dynroot-style directories, buffers that hold zero/one/many entries, EOF offset handling, long names, platform `d_type` reporting, stale dcache retry, concurrent directory fetch, `.` and `..` inode stability, and platform-specific record sizing where supported.
