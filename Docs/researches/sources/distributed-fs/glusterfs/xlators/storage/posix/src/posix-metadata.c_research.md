# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.c

## Purpose

This file implements GlusterFS POSIX ctime/mtime/atime metadata persistence using the `GF_XATTR_MDATA_KEY` xattr. It maintains an in-memory `posix_mdata_t` per inode, stores a portable disk format, supports legacy file healing when ctime is enabled after files already exist, and updates timestamps according to flags carried by the call frame.

## Important APIs, Types, and Functions

Serialization helpers are `posix_mdata_to_disk`, `posix_mdata_from_disk`, and `posix_mdata_iatt_from_disk`. Disk access is handled by `posix_fetch_mdata_xattr` and `posix_store_mdata_xattr`. Cache/read APIs are `__posix_get_mdata_xattr` and `posix_get_mdata_xattr`. Legacy creation/update is handled by `posix_set_mdata_xattr_legacy_files`. The central writer is `posix_set_mdata_xattr`, called by public update helpers `posix_update_utime_in_mdata`, `posix_update_ctime_in_mdata`, `posix_set_ctime`, `posix_set_parent_ctime`, and `posix_set_ctime_cfr`.

`posix_mdata_flag_t` determines which of ctime/mtime/atime should be updated. `posix_get_mdata_flag` decodes direct inode flags such as `MDATA_CTIME`, `MDATA_MTIME`, and `MDATA_ATIME`; `posix_get_parent_mdata_flag` decodes parent timestamp flags.

## Control Flow

Reads first look in inode context slot 1. If absent, they allocate `posix_mdata_t`, fetch `GF_XATTR_MDATA_KEY` from an fd, real path, or GFID handle path, convert from disk endian format, and cache it in the inode context when an inode is available. If the xattr is absent but a caller supplied `stbuf`, the read path treats this as legacy/no-mdata and returns success without overriding backend timestamps.

Writes take the inode lock, obtain or allocate cached metadata, optionally fetch current disk metadata, initialize new metadata for newly-created ctime-enabled files, update only the requested timestamp fields, and store the disk xattr. Non-utime updates retain the highest observed time for each requested field to reduce distributed race regressions. Explicit utime updates may set atime/mtime to caller-provided earlier or later values, while ctime is still only advanced. The updated metadata is copied into `stbuf` when provided.

Legacy healing uses `posix_set_mdata_xattr_legacy_files`: it either reuses existing cached/fetched metadata or initializes from a `struct mdata_iatt` received through xdata, compares incoming times with existing ones, keeps the larger value for each field, then stores the xattr.

`posix_set_ctime_cfr` handles `copy_file_range` as a two-inode operation: destination should get ctime/mtime updates, source should get atime updates when requested.

## State and Persistence Behavior

Persistent state is the packed `posix_mdata_disk_t` value stored in the backend xattr. In-memory state is a `posix_mdata_t *` stored in the inode context and freed by `posix_forget`. The code supports path-based, fd-based, and handle-path-based access. It logs occasional warnings for missing xattr support and explicit errors for failed mdata fetch/store.

## Dependencies and Integration Points

The file depends on `posix.h`, `posix-metadata.h`, `posix-handle.h`, POSIX syscall wrappers, endian helpers, inode context APIs, inode locks, frame root timestamp flags, and message IDs. It is called from setattr, fsetattr, open/opendir, read/write/truncate/ftruncate/fallocate/zerofill/copy_file_range, xattr remove, readdirp stat fill, checksum, and parent-entry operations.

## Risks

The metadata path is race-sensitive. It uses inode locks, but different clients/bricks can race through xattr updates, so monotonic comparison is used except for explicit utime. Error handling intentionally tolerates absent xattrs for legacy files, which can hide backend problems if op_errno classification is wrong. The code stores metadata on every update, which can be expensive and can amplify xattr failures. `posix_set_ctime_cfr` should be reviewed closely because source and destination arguments are easy to mix. Conversion uses unsigned 64-bit fields and assumes timestamps fit that representation. Inode-context allocation ownership must remain paired with `posix_forget`.

## Test Signals

Test xattr round-trip, missing xattr support, absent legacy mdata, lookup-triggered legacy healing, concurrent timestamp updates choosing the highest non-utime times, explicit utime to older and newer values, frame flag combinations for file and parent updates, fd-based and path-based updates, copy_file_range source/destination timestamp behavior, brick restart losing inode context and refetching from disk, and memory cleanup on forget.
