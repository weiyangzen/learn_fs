# sources/cloud-native/composefs/libcomposefs/lcfs-writer-erofs.c

## Purpose
`lcfs-writer-erofs.c` is the format-specific engine that serializes `lcfs_node_s` trees into composefs EROFS images and loads EROFS images back into node trees. It also rewrites trees for overlayfs semantics, including metacopy, redirects, whiteouts, shared xattrs, and synthetic `.`/`..` entries.

## Important APIs, Types, And Functions
Public/internal entry points are `lcfs_ctx_erofs_new`, `lcfs_write_erofs_to`, `lcfs_load_node_from_image_ext`, and `lcfs_load_node_from_image`. Important private groups include xxh32 xattr filtering; shared xattr hash helpers; `compute_erofs_*` layout functions; `write_erofs_*` serialization functions; overlay rewrite helpers; and loader helpers `lcfs_image_get_erofs_inode`, `erofs_readdir_block`, `lcfs_build_node_erofs_xattr`, and `lcfs_build_node_from_image`.

## Control Flow
Write flow clones the root, rewrites nodes for overlayfs, computes deterministic BFS tree order, deduplicates shared xattrs, computes inode sizes/padding/block addresses, writes composefs header and EROFS superblock, writes inode metadata and inline tails, writes shared xattrs, aligns, then writes out-of-band data blocks. Load flow validates composefs and EROFS headers, derives metadata/xattr regions, builds an inode hash to preserve hardlinks, recursively reads directories, reconstructs symlinks/inline content/non-inline stubs, interprets overlay xattrs back into payload/digest/whiteouts, and optionally filters toplevel entries.

## State And Persistence
The writer persists EROFS superblock, compact/extended inodes, xattr headers, inline and block data, chunk-based stubs, and composefs overlay xattrs. Temporary state lives in `lcfs_ctx_erofs_s` and per-node `erofs_*` fields.

## Dependencies And Integration Points
It depends on EROFS kernel-format wrappers, internal node model, hash table, fs-verity constants, Linux fsverity xattr encoding, and utility cleanup helpers. It is selected by `lcfs_write_to` for `LCFS_FORMAT_EROFS`.

## Risks
This is high-risk code: layout math, endian conversion, block alignment, shared xattr offsets, hardlink reconstruction, and overlay xattr escaping are correctness-critical. Non-inline regular files are represented as null chunk pointers and limited by `LCFS_MAX_NONINLINE_CHUNKS`. Loader bounds checks are partial and rely on image size validation plus format assumptions.

## Test Signals
Strong coverage comes from checksum fixtures, `fsck.erofs` validation when available, dump round trips, random FUSE/image tests, should-fail malformed fixtures, filtered dump tests, and `test-lcfs.c` hardlinked-whiteout regression.
