# sources/cloud-native/nydus/rafs/src/mock/mock_inode.rs

## Purpose
`mock_inode.rs` provides an in-memory inode implementation for tests. It implements `RafsInode`, `RafsInodeExt`, and v5 inode helper traits so shared metadata code can be exercised without real v5/v6 direct or cached superblock implementations.

## Important APIs, Types, And Functions
`MockInode` stores inode number, name, digest, parent, mode, project/user/group IDs, RAFS inode flags, size, blocks, nlink, child index/count, block size, rdev, mtime, symlink target, xattrs, chunk vector, child inode vector, blob table, and metadata. `MockInode::mock` creates a regular file with a given inode number, size, and chunks. The `RafsInode` implementation covers validation, FUSE entry/attr construction, symlink access, directory child lookup by binary-search name or index, xattr access, file-type checks, hardlink detection, recursive descendant collection, IO vector allocation through `rafsv5_alloc_bio_vecs`, and basic accessors. `RafsInodeExt` adds name, flags, digest, name size, chunk info, base inode view, and parent. `RafsV5InodeChunkOps` and `RafsV5InodeOps` provide v5 chunk retrieval, default blob lookup, chunk size, and hole status.

## Control Flow
Tests build a `MockInode`, optionally configure it as a directory with sorted children and xattrs, and call the same trait methods used by production `RafsSuper` paths. `collect_descendants_inodes` recursively visits child directories after collecting non-empty non-directory children. `alloc_bio_vecs` delegates to the real v5 IO allocation helper, making this mock useful for exercising chunk range behavior.

## State And Persistence
All metadata is in-memory. `get_entry` uses the embedded `RafsSuperMeta` timeouts. `get_attr` returns a FUSE attr view from stored inode fields. Xattrs are a `HashMap<OsString, Vec<u8>>`; children and chunks are `Arc` vectors. No persistent metadata is read or written.

## Dependencies And Integration Points
The file depends on FUSE ABI types, `nydus_storage` blob and IO types, `MockChunkInfo`, `mock_super::CHUNK_SIZE`, v5 layout IO helpers and traits, shared metadata traits and constants, inode flags, and crate `RafsInodeExt`. It integrates with `MockSuperBlock` for lookup tests.

## Risks
Several behaviors are simplified. `walk_children_inodes` is `todo!`, `get_blob_by_index` returns a default `BlobInfo` rather than a configured table entry, `has_hole` is always false, child lookup assumes children are sorted by name, and many fields are left at defaults by `mock`. It is suitable for focused trait and IO tests, not complete filesystem semantic tests.

## Test Signals
The unit test configures a directory inode with children, xattrs, digest, parent, and chunks. It checks validation, attr and entry construction, symlink errors, child lookup, child and chunk counts, xattr retrieval, file-type predicates, hardlink status, descendant collection, v5 chunk lookup, blob lookup, chunk size, and hole status.
