# sources/cloud-native/composefs/libcomposefs/erofs_fs.h

Purpose: canonical EROFS on-disk format definitions used by libcomposefs to create or inspect EROFS-compatible images.

Important APIs/types/functions: feature flags, `erofs_super_block`, inode layouts, chunk info, xattr headers/entries, long xattr prefixes, device slots, dirents, compression config/map structs, chunk indexes, xattr sizing helpers, `erofs_inode_is_data_compressed`, and `erofs_check_ondisk_layout_definitions`.

Control flow: mostly declarative packed/LE structs and macros. Inline helpers compute xattr ibody/entry sizes and validate compile-time struct sizes with `BUILD_BUG_ON`.

State/persistence: defines persistent disk ABI for superblocks, inodes, xattrs, directory entries, chunks, compression maps, and device tables. Any field/layout change affects image compatibility.

Dependencies/integration: included through `erofs_fs_wrapper.h`, depends on wrapper-provided Linux integer/endian macros and compile-time assertions. Used by C composefs image writer/reader code.

Risks/test signals: extremely high compatibility risk; definitions must match Linux EROFS. Compile-time layout checks catch size drift, while integration tests/fsck catch semantic drift.
