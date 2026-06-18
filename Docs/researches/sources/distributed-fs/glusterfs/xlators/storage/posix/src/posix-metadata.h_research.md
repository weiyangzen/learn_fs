# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.h

## Purpose

This header declares the in-memory metadata representation and public APIs for POSIX ctime metadata xattr handling.

## Important APIs, Types, and Functions

`posix_mdata_t` contains flags, ctime, mtime, atime, version, and explicit padding. `posix_mdata_flag_t` contains bitfields for ctime/mtime/atime update selection. Public APIs include locked and unlocked mdata reads, utime and ctime update helpers, direct file and parent ctime setters, copy_file_range timestamp setter, legacy-file xattr seeding, and disk-to-`mdata_iatt` conversion.

## Control Flow

Callers choose locked `posix_get_mdata_xattr` when they do not already hold the inode lock and `__posix_get_mdata_xattr` when they do. Mutating fops call one of the setter helpers after the backend syscall and post-stat. Lookup/setxattr legacy paths call `posix_set_mdata_xattr_legacy_files`.

## State and Persistence Behavior

The header defines in-memory state mirrored to `posix_mdata_disk_t` from `posix-metadata-disk.h`. `posix_mdata_t` is held in inode context and persisted to `GF_XATTR_MDATA_KEY` by implementation functions.

## Dependencies and Integration Points

It includes `posix-metadata-disk.h` and depends on Gluster types `xlator_t`, `inode_t`, `call_frame_t`, `struct iatt`, and `struct mdata_iatt`. The declarations are consumed by POSIX inode/fd, entry, lookup, and metadata code.

## Risks

Bitfield layout is only used in memory but should remain simple. Padding implies ABI/alignment awareness. Callers must respect lock expectations or risk races and deadlocks.

## Test Signals

Compile all call sites, verify locked/unlocked read use, validate timestamp update flags from frame root flags, and run memory-check tests around inode forget cleanup.
