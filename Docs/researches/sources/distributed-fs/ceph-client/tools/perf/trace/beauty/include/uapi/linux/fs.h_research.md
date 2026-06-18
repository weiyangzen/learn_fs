# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fs.h

## Purpose

`fs.h` is a broad Linux filesystem and block-device UAPI header. In perf trace beauty it supplies constants and structures for decoding generic filesystem ioctls, block ioctls, clone/dedupe/trim requests, inode flags, extended file attributes, per-I/O flags, pagemap scanning, and `/proc/<pid>/maps` query ioctls.

## Important APIs, Types, and Constants

Major groups include file/block defaults (`INR_OPEN_*`, `BLOCK_SIZE`, `SEEK_*`, `RENAME_*`); integrity flags; clone/trim/UUID/sysfs/logical-block metadata structs; dedupe structs and statuses; file/inode statistic structs; `fsxattr`, versioned `file_attr`, and `FS_XFLAG_*`; block ioctls such as `BLKROGET`, `BLKGETSIZE64`, discard, zeroout, diskseq, and trace setup; filesystem ioctls such as `FICLONE`, `FIDEDUPERANGE`, `FITRIM`, `FS_IOC_GETFLAGS`, `FS_IOC_FSGETXATTR`, labels, UUID, sysfs path, and LBMD capability; inode flags `FS_*_FL`; per-I/O `RWF_*` flags and `RWF_SUPPORTED`; and procfs ioctls `PAGEMAP_SCAN` and `PROCMAP_QUERY` with `page_region`, `pm_scan_arg`, and `procmap_query`.

## Control Flow and Integration

The file defines ioctl ABI shapes. Filesystem and block-device commands use `_IO*` encodings. Clone, dedupe, and trim pass fixed or flexible-array structs. `FS_IOC_GETFLAGS` and `SETFLAGS` manipulate inode flags; `FS_IOC_FSGETXATTR` and `FSSETXATTR` use richer project/extent attributes. `preadv2` and `pwritev2` consume `RWF_*`. `PAGEMAP_SCAN` walks an address range and may emit page-region records; `PROCMAP_QUERY` provides structured VMA lookup and optional name/build-id output.

## State and Persistence Behavior

Many described operations mutate state: inode flags, project IDs, labels, filesystem attributes, freeze/thaw, trim/discard, readonly block state, tracing controls, reflink/dedupe extent sharing, and optional pagemap write-protection. `RWF_*` is per-I/O. Query interfaces expose state without persisting new metadata.

## Dependencies and Integration Points

The header includes `linux/limits.h`, `linux/ioctl.h`, `linux/types.h`, optionally `linux/fscrypt.h`, and outside the kernel `linux/mount.h`. It integrates with VFS, block layer, procfs, mm, fscrypt, fs-verity, DAX, reflink/dedupe-capable filesystems, and block metadata protection.

## Risks

Historical ioctl argument types and 32-bit variants must preserve command numbers exactly. Inode flags are both UAPI and ext-family on-disk encoding. Flexible arrays require length-aware decoding. `PAGEMAP_SCAN` can mutate page protection when `PM_SCAN_WP_MATCHING` is set. `procmap_query` contains several user buffers and in/out sizes. `RWF_SUPPORTED` must track newly added flags.

## Test Signals

Trace and decode `FICLONE`, `FIDEDUPERANGE`, `FITRIM`, `FS_IOC_GETFLAGS`, `FS_IOC_FSGETXATTR`, `BLKGETSIZE64`, `PAGEMAP_SCAN`, and `PROCMAP_QUERY`. Unit-check `FS_*_FL`, `FS_XFLAG_*`, `RWF_*`, `PAGE_IS_*`, `PM_SCAN_*`, and `PROCMAP_QUERY_*` masks.
