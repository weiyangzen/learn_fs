# sources/distributed-fs/ceph-client/include/uapi/linux/falloc.h

This UAPI header defines `fallocate(2)` mode flags. It is the public contract for space preallocation, hole punching, range collapse/insert, zeroing, unsharing, fixed-range allocation, and write-zeroes behavior.

Important exports include `FALLOC_FL_KEEP_SIZE`, `PUNCH_HOLE`, `NO_HIDE_STALE`, `COLLAPSE_RANGE`, `ZERO_RANGE`, `INSERT_RANGE`, `UNSHARE_RANGE`, and newer flags such as `FALLOC_FL_ALLOCATE_RANGE` and `FALLOC_FL_WRITE_ZEROES`. The header also documents valid flag combinations and mutually exclusive operations.

Control flow is syscall driven: userspace invokes `fallocate(fd, mode, offset, len)`, VFS validates generic constraints, and the filesystem implements the chosen operation through its fallocate method. State changes live in file size, extent maps, unwritten/allocated extent metadata, copy-on-write sharing state, and block allocation. Persistence is filesystem metadata and possibly zeroed data ranges after journal/transaction completion.

Dependencies are VFS and individual filesystem implementations such as ext4, XFS, Btrfs, F2FS, and network filesystems. Integration points include database preallocation, sparse-file tools, VM image management, reflink/COW unsharing, and block discard/zeroing support.

Risks include stale-data exposure when zero/no-hide semantics are wrong, incompatible flag combinations, alignment restrictions for collapse/insert, quota/enospc accounting bugs, and network filesystem semantic gaps. Test signals include xfstests fallocate groups, sparse-file hole maps via fiemap, fsck after crash tests, reflink unshare tests, and data-zeroing validation.
