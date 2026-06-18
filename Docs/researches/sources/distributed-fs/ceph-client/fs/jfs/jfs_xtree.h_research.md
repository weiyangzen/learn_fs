<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.h

## Purpose
`jfs_xtree.h` defines the on-disk/in-memory layout and public interface for the JFS extent allocation descriptor tree used by regular files, long symlinks, special metadata files, and some directory truncation paths.

## Important APIs, types, and functions
The central type is `xad_t`, a 16-byte descriptor containing flags, a 40-bit logical offset, and a `pxd_t` location with length and physical address. Macros `XADoffset`, `XADaddress`, `XADlength`, `offsetXAD`, `addressXAD`, and `lengthXAD` encode/decode endian-sensitive fields. `struct xadlist` batches descriptors. Tree page layout is `struct xtheader`, `xtroot_t`, and `xtpage_t`, with slot constants `XTROOTINITSLOT_DIR`, `XTROOTINITSLOT`, `XTROOTMAXSLOT`, `XTPAGEMAXSLOT`, and `XTENTRYSTART`. Public functions declared here are `xtLookup`, `xtInitRoot`, `xtInsert`, `xtExtend`, `xtUpdate`, `xtTruncate`, `xtTruncate_pmap`, and `xtAppend`.

## Control flow
The header has no execution flow by itself. It establishes the contract consumed by `jfs_xtree.c` and by higher-level inode, directory, symlink, resize, and truncate code. Callers construct or inspect `xad_t` records through macros instead of directly composing split endian fields.

## State and persistence behavior
The structs mirror persistent JFS metadata. `xtroot_t` lives inline in the JFS inode; non-root `xtpage_t` instances live in metapages. `xad_t` flags distinguish newly allocated, extended, compressed, not-recorded, and copy-on-write extents. The maximum length `MAXXLEN` bounds a single extent at 24 bits, forcing callers to split longer mappings.

## Dependencies and integration points
It includes `jfs_btree.h` for common B+-tree definitions and uses `pxd_t` helpers for physical extent encoding. The declarations are the shared API between xtree management and the rest of JFS allocation, resize, symlink, truncate, and write paths.

## Risks and test signals
Risks are ABI/layout drift, endian conversion mistakes, direct field access bypassing macros, and single-extent length overflow. Test signals are on-disk metadata compatibility, fsck validation of xtree roots/pages, block mapping beyond 32-bit logical offsets, and builds across endian architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.h -->
