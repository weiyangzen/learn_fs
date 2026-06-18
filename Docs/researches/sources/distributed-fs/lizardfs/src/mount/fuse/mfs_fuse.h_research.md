# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.h

## Purpose
This header declares the normal LizardFS low-level FUSE callback surface used by `main.cc`. It exposes the functions installed into `struct fuse_lowlevel_ops` for regular filesystem mounts.

## Important APIs, Types, And Functions
The declarations cover statfs, access, lookup, getattr/setattr, node creation and deletion, directory operations, file create/open/read/write/flush/fsync/release, extended attributes, and optional locking. Signatures are version-gated for `mfs_statfs()` on FUSE 2.6+, `mfs_rename()` on FUSE 3 flags, Apple xattr `position`, POSIX byte-range locks on FUSE 2.6+, and flock on FUSE 2.9+.

## Control Flow
The header has no runtime control flow, but it is the ABI contract between the mount bootstrap and `mfs_fuse.cc`. `init_fuse_lowlevel_ops()` assigns these function pointers, so signature drift breaks mount startup or compilation.

## State And Persistence
No state is stored here. State is passed through `fuse_req_t`, inode ids, `fuse_file_info`, and user buffers into the implementation.

## Dependencies And Integration Points
It depends on `common/platform.h`, libfuse headers, and `protocol/MFSCommunication.h` for protocol-visible constants. It integrates with `main.cc`, `mfs_fuse.cc`, and libfuse's low-level operation structure.

## Risks And Test Signals
Risks are mostly compatibility risks: FUSE version macros must match the libfuse headers used to compile the operation table. Test signals are successful FUSE 2 and FUSE 3 builds, plus compile coverage for Apple and non-Apple xattr signatures and optional file-lock support.
