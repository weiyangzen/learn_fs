# sources/distributed-fs/ceph-client/fs/exfat/file.c

## Purpose
`file.c` implements VFS file operations and inode attribute operations for regular exFAT files. It handles fallocate-style preallocation, truncate/extend semantics, chmod/chown/time validation, FAT-compatible attribute ioctls, volume label and shutdown ioctls, trim ioctl forwarding, fsync, valid-data-length extension, write/read/mmap/splice wrappers, and the exported `exfat_file_operations` and `exfat_file_inode_operations`.

## Important APIs, types, and functions
Growth and truncate helpers are `exfat_cont_expand()`, `exfat_fallocate()`, `__exfat_truncate()`, and `exfat_truncate()`. Attribute paths are `exfat_getattr()`, `exfat_setattr()`, `exfat_sanitize_mode()`, and `exfat_allow_set_time()`.

Ioctl helpers include `exfat_ioctl_get_attributes()`, `exfat_ioctl_set_attributes()`, `exfat_ioctl_fitrim()`, `exfat_ioctl_shutdown()`, `exfat_ioctl_get_volume_label()`, `exfat_ioctl_set_volume_label()`, `exfat_ioctl()`, and `exfat_compat_ioctl()`. I/O hooks include `exfat_file_fsync()`, `exfat_extend_valid_size()`, `exfat_file_write_iter()`, `exfat_file_read_iter()`, `exfat_page_mkwrite()`, `exfat_file_mmap_prepare()`, and `exfat_splice_read()`.

## Control flow
`exfat_cont_expand()` grows a file by allocating enough clusters for the requested size, appending them to an existing chain, converting to FAT-chain mode if needed, updating `i_size` and `i_blocks`, but deliberately not increasing `valid_size` for unwritten preallocated ranges. `exfat_fallocate()` exposes this only for `FALLOC_FL_ALLOCATE_RANGE` on regular files.

`__exfat_truncate()` marks the volume dirty, computes new versus physical cluster counts, advances to the first cluster to free, shrinks `valid_size`, sets archive attribute, writes the directory entry before cutting the FAT chain, invalidates the cluster cache and hints, then frees removed clusters. This ordering reduces the chance that a crash leaves freed clusters still referenced by the directory entry.

`exfat_setattr()` handles extension before generic checks when `ATTR_SIZE` grows, permits configured owner/group time updates, rejects unsupported uid/gid/mode changes, sanitizes Unix mode into exFAT's limited attribute model, zeroes the tail block on shrink, serializes truncate through `truncate_lock`, and calls `exfat_truncate()`. Write paths zero gaps up to `valid_size` before writing beyond it, then call generic buffered write. Mmap write faults extend `valid_size` before `filemap_page_mkwrite()`.

## State and persistence behavior
Persistent metadata changed here includes directory entry file attributes, stream size, valid size, timestamps, FAT chains, bitmap bits, volume label entries, volume dirty/shutdown flags, and block discard state. Runtime state includes `ei->valid_size`, `ei->start_clu`, `ei->flags`, `ei->attr`, inode size, block count, page cache, and forced shutdown flag. `exfat_file_fsync()` flushes page metadata through `simple_fsync_noflush()`, synchronizes the block device, and issues a device flush.

## Dependencies and integration points
This file depends on FAT and bitmap allocation, inode writeback, directory entry sets, NLS conversion, volume-label helpers, shutdown support in `super.c`, VFS setattr/write/read/mmap/ioctl APIs, blockdev discard/flush, security inode setattr hooks, and legacy FAT ioctl numbers from `msdos_fs.h`.

## Risks and test signals
Risks include valid-size exposure of stale data, crash ordering during truncate/free, file extension without zeroing gaps, direct-I/O alignment differences, chmod/attribute mismatches, ioctl capability/security gaps, forced-shutdown bypass, and concurrent write/truncate races. Tests should include fsx, xfstests generic write/truncate/fallocate/mmap/direct-I/O cases, sparse writes beyond valid size, attr ioctls on files and root directory, volume-label ioctls with lossy names, FITRIM permission and range checks, shutdown ioctl behavior, fsync power-fail testing, and mode mask mount-option combinations.
