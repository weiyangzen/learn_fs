<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/erofs/Kconfig

## Purpose
`Kconfig` defines build-time features for EROFS, a modern read-only filesystem for immutable images, containers, application sandboxes, datasets, and remote/on-demand blobs.

## Important APIs, types, and functions
Important symbols include `EROFS_FS`, `EROFS_FS_DEBUG`, `EROFS_FS_XATTR`, `EROFS_FS_POSIX_ACL`, `EROFS_FS_SECURITY`, `EROFS_FS_BACKED_BY_FILE`, `EROFS_FS_ZIP`, algorithm options for LZMA/DEFLATE/ZSTD, `EROFS_FS_ZIP_ACCEL`, deprecated `EROFS_FS_ONDEMAND`, per-CPU kthread options, and experimental `EROFS_FS_PAGE_CACHE_SHARE`.

## Control flow
There is no runtime control flow. Symbol selections pull in dependencies such as CRC32, FS_IOMAP, decompression libraries, crypto acceleration, fscache/cachefiles, and netfs support.

## State and persistence
The file has no runtime state. It shapes supported on-disk feature compatibility at build time, especially compressed, xattr, file-backed, fscache, and page-cache-sharing behavior.

## Dependencies and integration points
It integrates EROFS with block devices, iomap, optional xattr/ACL/security stacks, compression libraries, crypto acomp, fscache, cachefiles, and netfs.

## Risks and test signals
Risks include unsupported filesystem images when compression algorithms are disabled, deprecated fscache behavior, feature combinations such as page-cache-share excluding ondemand, and debug-only consistency checks. Test signals include build matrices across compression and I/O modes plus mount attempts for images with each advertised on-disk feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Kconfig -->
