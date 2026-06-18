# sources/distributed-fs/ceph-client/fs/f2fs/verity.c

## Purpose
`verity.c` implements F2FS support for fs-verity. It stores the Merkle tree and fsverity descriptor beyond normal file size at the next 64 KiB boundary after `i_size`, and stores only a small F2FS verity xattr that points to the descriptor location. This avoids xattr size limits and ensures verity metadata is encrypted with file data when fscrypt is used.

## Important APIs, Types, And Functions
The exported integration object is `const struct fsverity_operations f2fs_verityops`, consumed by `super.c` through `sb->s_vop`. It provides `begin_enable_verity`, `end_enable_verity`, `get_verity_descriptor`, `read_merkle_tree_page`, `readahead_merkle_tree`, and `write_merkle_tree_block`.

`f2fs_verity_metadata_pos()` computes the metadata base as `round_up(inode->i_size, 65536)`. `pagecache_read()` and `pagecache_write()` read and write beyond `i_size` through the file mapping rather than VFS read/write helpers. The on-disk xattr payload is `struct fsverity_descriptor_location`, containing version, descriptor size, and descriptor file position.

## Control Flow
Enabling verity starts in `f2fs_begin_enable_verity()`. It rejects concurrent verity enablement, rejects atomic files, initializes quota accounting because the file is opened read-only, converts inline data to regular blocks, and sets `FI_VERITY_IN_PROGRESS`.

During fs-verity construction, `f2fs_write_merkle_tree_block()` writes Merkle blocks at offsets relative to the hidden metadata base. `f2fs_end_enable_verity()` then appends the descriptor after the Merkle tree, writes and waits for all mapping pages, creates the verity xattr with descriptor location, sets the VFS verity flag, persists inode flags, marks the inode dirty, and clears `FI_VERITY_IN_PROGRESS`. If any step fails, it truncates pages and blocks beyond `i_size` while holding `i_gc_rwsem[WRITE]`, clears in-progress state, and marks the filesystem for fsck if cleanup truncation fails.

At file-open or verification time, `f2fs_get_verity_descriptor()` reads the location xattr, validates version, size, overflow, maximum file blocks, and minimum metadata position, then reads the descriptor from page cache. Merkle page reads and readahead translate fs-verity-relative indexes by adding the metadata base page offset before calling generic helpers.

## State And Persistence Behavior
Persistent state is split between hidden file data blocks and xattr metadata. The Merkle tree and descriptor are stored in the inode mapping beyond visible EOF. The xattr `F2FS_XATTR_INDEX_VERITY/F2FS_XATTR_NAME_VERITY` stores only the descriptor location. The inode verity flag is set only after metadata pages are written and waited on, which gives crash consistency ordering: metadata first, xattr next, inode flag last.

## Dependencies And Integration Points
This file depends on fs-verity core APIs, F2FS xattr functions, quota initialization, inline-data conversion, inode dirtying, truncation, GC locking, and max file block calculations from `super.c`. It integrates with fscrypt implicitly by storing metadata in encrypted file contents rather than plaintext xattrs.

## Risks
The critical risks are crash ordering, cleanup after failed enablement, and bounds validation for hidden metadata offsets. If `FI_VERITY_IN_PROGRESS` is cleared too early, pages beyond `i_size` may not be written correctly. If cleanup races GC, stale hidden metadata could be reintroduced, which is why the cleanup path takes the write side of the GC inode semaphore. Corrupt xattrs must be treated as filesystem corruption because they can point outside valid metadata space.

## Test Signals
Test signals include fs-verity enable and verify tests on regular, encrypted, compressed-disabled, and inline-data files; rejection on atomic files; interruption/failure injection during descriptor or xattr writes; corrupted verity xattr handling; cleanup verification after failed enablement; and reads on architectures or configurations with different page sizes.
