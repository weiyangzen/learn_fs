# sources/distributed-fs/ceph/src/client/fuse_ll.cc

## Purpose
`fuse_ll.cc` is CephFS's low-level FUSE adapter. It translates FUSE callbacks into `Client::ll_*` operations, manages FUSE session lifecycle, maps Ceph inode/snapshot identities to FUSE inode numbers, forwards request credentials, exposes Ceph and fscrypt ioctls, and wires invalidation/remount/interrupt callbacks back to libcephfs.

## Important APIs, Types, and Functions
The file defines `CephFuse::Handle`, the `fuse_ll_oper` operation table, helpers for errno mapping, device encoding, mountpoint detection, supplementary groups, request TLS, fake inode/snapshot tags, and many `fuse_ll_*` handlers. Key handlers include lookup/getattr/setattr, xattrs, mknod/mkdir/unlink/rmdir/symlink/rename/link, open/read/write/flush/release/fsync, opendir/readdir/releasedir/fsyncdir, statfs, locks/flock, fallocate, access, create, and ioctl. Lifecycle methods are `Handle::init()`, `start()`, `loop()`, `finalize()`, and wrapper methods on `CephFuse`.

## Control Flow
Every FUSE request begins with `fuse_ll_req_prepare()`, storing the request in thread-local state for callbacks such as umask and interrupt switching. Handlers build `UserPerm` from `fuse_req_ctx()`, optionally load supplementary groups, resolve FUSE inode numbers to `Inode*` with `iget()`, call the corresponding `Client::ll_*` method, translate negative Ceph errors to system errno, reply through FUSE, and release inode references when required. `init()` constructs FUSE arguments from Ceph config, parses mount options, registers client callbacks, and `start()` creates/mounts a FUSE session after checking whether the mountpoint already has a Ceph FUSE mount.

## State and Persistence Behavior
Persistent state lives in CephFS. Adapter state includes FUSE session/channel objects, parsed mountpoint/options, request TLS, and `g_fino_maps`, which maps Ceph inode+snapid to fake 64-bit FUSE inode tags when libcephfs is not already faking inode numbers. File and directory handles are stored in `fuse_file_info::fh`.

## Dependencies and Integration Points
It depends on libfuse low-level APIs, `Client`, `Fh`, `Inode`, `Dir`, Ceph config/debug/safe_io, ioctl ABI headers, and `FSCrypt`. It also integrates with parent daemon signaling via `fd_on_success`, kernel cache invalidation notifications, Linux `syncfs()` before snapshot mkdir when configured, and remount commands for dcache trimming.

## Risks
Reference accounting is delicate: created/lookuped inode refs are intentionally left for FUSE forget, while parents are put immediately. `fuse_ll_rename()` can leak one inode reference on early error if only one of `in`/`nin` resolves. Variable-length stack buffers for xattrs can be risky for large sizes. ioctl handling has many ABI-size branches. Fake inode stag exhaustion aborts, though comments expect snapshot counts to stay below the tag range.

## Test Signals
Integration tests should cover mount detection, FUSE2/FUSE3 builds, permission/group propagation, cache invalidation, snapshot fake inode mapping, fscrypt ioctls, Ceph layout ioctls, lock blocking behavior with single-threaded FUSE, and balanced ll ref/forget behavior.
