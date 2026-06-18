# sources/cloud-native/composefs/libcomposefs/lcfs-erofs-internal.h

## Purpose
This private header bridges composefs node logic and EROFS on-disk structures. It defines inode helpers, xattr prefix conversions, ACL recognition, and the chunking API used by both writer validation and EROFS serialization.

## Important APIs, Types, And Functions
`erofs_inode` is a union over raw `i_format`, compact inode, and extended inode. Inline helpers decode inode version, datalayout, tailpacking, flat layout, xattr inode size, ACL xattrs, xattr prefix indexes, and full xattr names. `erofs_compute_chunking` is declared for non-inline regular-file stubs.

## Control Flow
Writer and loader code call these helpers while computing layout or parsing image data. Xattr prefix lookup scans `erofs_xattr_prefixes`, maps known EROFS indexes back to full names, and allocates reconstructed names for loader xattr handling.

## State And Persistence
The only static data is `erofs_xattr_prefixes`. It models EROFS xattr namespaces and affects persisted xattr names in images.

## Dependencies And Integration Points
It depends on `lcfs-internal.h`, public EROFS composefs header definitions, and `erofs_fs_wrapper.h`. It is central to `lcfs-writer-erofs.c` and also used by `lcfs-writer.c` validation.

## Risks
`erofs_get_xattr_name` allocates and returns NULL on invalid index or ENOMEM. Prefix ordering matters because broad prefixes such as `trusted.` must not shadow more specific entries incorrectly. Chunking limits feed `LCFS_MAX_NONINLINE_CHUNKS`.

## Test Signals
Covered indirectly by checksum fixtures, random FUSE/image round trips, should-fail oversized fixtures, and `test-lcfs.c` image-load regression.
