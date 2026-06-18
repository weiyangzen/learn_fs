# sources/distributed-fs/ceph-client/include/uapi/linux/fiemap.h

This UAPI header defines the `FS_IOC_FIEMAP` data structures and flags used to report logical-to-physical file extent mappings. It is a filesystem-independent ABI for sparse-file inspection, backup tools, defragmenters, and diagnostics.

Important exports are `struct fiemap_extent`, `struct fiemap`, `FIEMAP_MAX_OFFSET`, request flags `FIEMAP_FLAG_SYNC`, `FIEMAP_FLAG_XATTR`, `FIEMAP_FLAG_CACHE`, and extent flags such as `FIEMAP_EXTENT_LAST`, `UNKNOWN`, `DELALLOC`, `ENCODED`, `DATA_ENCRYPTED`, `NOT_ALIGNED`, `DATA_INLINE`, `DATA_TAIL`, `UNWRITTEN`, `MERGED`, and `SHARED`.

Control flow is ioctl based: userspace fills `struct fiemap` with a start, length, flags, and extent array capacity; VFS/filesystem maps extents, writes `fm_mapped_extents`, possibly updates `fm_flags`, and fills extent records until capacity or end. State is a snapshot of filesystem extent metadata and delayed allocation/writeback state. Persistence is the underlying file layout, not the ioctl response itself.

Dependencies include `linux/types.h`, generic `FS_IOC_FIEMAP` in `fs.h`, and filesystem extent mapping implementations. Integration points include `filefrag`, backup/deduplication tools, ext4/XFS/Btrfs/F2FS, reflink detection through `SHARED`, and xattr tree mapping.

Risks include races with concurrent writes/truncates, misreporting delayed/unwritten/shared/encoded extents, alignment assumptions, and exposing physical block layout where permissions are insufficient. Test signals include xfstests fiemap coverage, sparse/reflink/unwritten extent tests, concurrent modification tests, encrypted/compressed file behavior, and userspace `filefrag` comparisons.
