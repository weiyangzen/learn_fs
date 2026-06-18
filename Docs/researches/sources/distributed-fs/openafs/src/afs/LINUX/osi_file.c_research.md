# sources/distributed-fs/openafs/src/afs/LINUX/osi_file.c

## Purpose
This file implements Linux cache-file operations for OpenAFS disk cache access. It opens cache files from stored file handles, records cache filesystem metadata, performs kernel-space read/write/truncate/stat operations through Linux VFS wrappers, and implements AFS `uio` movement helpers.

## Important APIs, types, and functions
- `afs_linux_raw_open(afs_dcache_id_t *ainode)` decodes a stored cache file handle to a dentry and opens it read/write with cache credentials.
- `osi_UFSOpen` allocates and initializes `struct osi_file` for a cache dcache entry.
- `osi_get_fh` encodes and validates uniform filesystem file handles for cache files.
- `afs_osi_Stat`, `osi_UFSClose`, and `osi_UFSTruncate` implement stat, close, and shrink operations.
- `afs_osi_Read` and `afs_osi_Write` build one-element `uio`s and call `osi_rdwr`.
- `osi_InitCacheInfo` resolves the cache path, stores cache device/superblock/mount/filehandle info, and initializes export ops.
- `osi_rdwr` loops through `uio` iovecs, temporarily lifts `RLIMIT_FSIZE`, optionally switches address limits on older kernels, and calls `afs_file_read`/`afs_file_write`.
- `setup_uio` and `uiomove` are utility routines for AFS-style UIO structures.

## Control flow and behavior
Cache initialization looks up the cache directory path, stores the mount, dentry, superblock, device, fragment mask, and initial file handle, then configures superblock export operations for file-handle decode support. Opening a cache file decodes its stored file handle through `afs_get_dentry_from_fh`, sets `S_NOATIME`, overrides credentials when available, opens via `afs_dentry_open`/`dentry_open`, falls back from stashed cache credentials to current credentials on newer cred kernels, and returns a `struct file`.

Read/write wrappers validate `struct osi_file`, update the stored offset when requested, build a `uio`, drop `AFS_GLOCK`, call `osi_rdwr`, reacquire `AFS_GLOCK`, convert success to byte counts, and normalize errors. `osi_rdwr` overrides cache credentials, sets file-size rlimit to infinity, optionally sets kernel address limits for old APIs, iterates iovecs, calls the compatibility file read/write wrapper at `uio_offset`, advances iovec/residual/offset on progress, and treats a zero-length VFS transfer as `EIO`. Truncation avoids expensive no-op truncates, locks the inode, prepares attributes with current time, calls compatibility setattr helpers, and truncates page cache.

## State and persistence
This file stores global cache file-handle format state (`cache_fh_type`, `cache_fh_len`) and uses global cache mount/superblock/device values. `struct osi_file` tracks `filp`, `size`, `offset`, and optional completion callback `proc`. It persists cache contents through the underlying Linux filesystem and keeps access times suppressed via `S_NOATIME`.

## Dependencies and integration points
It depends on Linux VFS, exportfs, namei, credentials, inode locks, file read/write APIs, and compatibility helpers from `osi_compat.h`. It integrates with OpenAFS disk cache state (`cacheDiskType`, `cacheDev`, `cacheInode`, `afs_cacheMnt`, `afs_cacheSBp`, `cache_creds`), allocator/stat APIs, and higher-level cache manager read/write paths.

## Risks
Cache file handle decoding failures are warned as potentially leading to AFS access errors or kernel panic. Uniform file-handle assumptions are enforced with panic if cache files produce inconsistent handle type/length. Credential override/fallback behavior can mask LSM issues or fail under changed security policy. `osi_rdwr` mutates the current task rlimit and older address limit state and must restore them on every path. A zero-byte VFS read/write is treated as `EIO`, which may turn EOF-like conditions into errors for cache operations. Truncate avoids `notify_change` intentionally, so compatibility with newer inode/dentry expectations depends on wrappers.

## Test signals
Test cache initialization on filesystems with and without export operations, cache open/read/write/truncate/stat/close, file-handle consistency across multiple cache files, SELinux/AppArmor cache credential scenarios, ENOSPC write warnings, shutdown behavior with null `osi_file`, and old/new kernel file I/O API builds. Fault injection around `afs_get_dentry_from_fh`, `dentry_open`, `setattr_prepare`, and partial VFS transfers is valuable.
