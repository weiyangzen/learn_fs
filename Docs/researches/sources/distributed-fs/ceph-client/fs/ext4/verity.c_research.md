# sources/distributed-fs/ceph-client/fs/ext4/verity.c

## Purpose
`verity.c` implements ext4's `fsverity_operations`. It stores Merkle tree blocks and the fs-verity descriptor beyond normal `i_size`, starting at the next 64 KiB boundary, so metadata remains invisible to userspace while still using ext4's normal page-cache, encryption, block mapping, quota, and journaling paths.

## Important APIs, Types, And Functions
The exported table is `ext4_verityops`, with callbacks `ext4_begin_enable_verity()`, `ext4_end_enable_verity()`, `ext4_get_verity_descriptor()`, `ext4_read_merkle_tree_page()`, `ext4_readahead_merkle_tree()`, and `ext4_write_merkle_tree_block()`. Helper `ext4_verity_metadata_pos()` computes the hidden metadata base. `pagecache_read()` and `pagecache_write()` perform internal IO past `i_size` without using normal file read/write syscalls.

Descriptor layout is handled by `ext4_write_verity_descriptor()` and `ext4_get_verity_descriptor_location()`. The descriptor starts at a filesystem block boundary after the Merkle tree. Its size is stored as a little-endian 32-bit value in the last four bytes of the last allocated filesystem block, allowing lookup by finding the last extent.

## Control Flow
Enabling verity begins in `ext4_begin_enable_verity()`: DAX is rejected, concurrent enable is rejected, the inode gets a JBD2 inode and quota initialization despite the readonly file descriptor, inline data is converted out, non-extent files are rejected, post-EOF blocks are truncated to avoid confusing descriptor lookup, and the inode is added to the orphan list while `EXT4_STATE_VERITY_IN_PROGRESS` is set.

fs/verity writes Merkle tree blocks through `ext4_write_merkle_tree_block()`, which offsets writes by the hidden metadata base and writes through ext4 address-space operations. `ext4_end_enable_verity()` then writes the descriptor, waits for all data and metadata pages, starts a transaction, marks fast commit ineligible, removes the orphan entry, reserves and dirties the inode, sets `EXT4_INODE_VERITY`, and clears the in-progress state. On any failure or when fs/verity passes `desc == NULL`, cleanup truncates cached and on-disk metadata beyond `i_size`, removes orphan state, and clears in-progress state.

Reading verity metadata offsets generic Merkle page reads and readahead by the metadata base. Descriptor lookup finds the last extent, reads the trailing descriptor-size field, validates size and position bounds, and reads the descriptor into the caller buffer or returns its size.

## State And Persistence Behavior
Verity metadata is persisted as hidden file blocks past EOF. Because verity files are readonly after enabling, those blocks can be stable and invisible to userspace. The orphan-list transaction makes interrupted enable operations recoverable: if enabling fails or the system crashes before the verity flag is persisted, metadata beyond `i_size` can be truncated away. The final inode flag is persisted only after writeback of data and metadata pages, preserving crash consistency.

## Dependencies And Integration Points
This file integrates ext4 extents, inline-data conversion, truncation, orphan handling, JBD2 transactions, quota initialization, address-space `write_begin`/`write_end`, page-cache folios, fsverity generic Merkle helpers, fscrypt requirements for encrypted files, and fast-commit exclusion via `ext4_fc_mark_ineligible()`. It requires extent-based files because descriptor discovery relies on the final extent.

## Risks And Edge Cases
DAX is incompatible and rejected. Non-extent files are unsupported. Descriptor discovery depends on the last allocated block, so `ext4_begin_enable_verity()` must remove unrelated post-EOF blocks before metadata is written. `pagecache_write()` must handle short `write_end()` as `-EIO`; reads beyond `i_size` must not use normal VFS reads. Bounds checks in descriptor lookup protect against corrupt size fields, missing extents, and descriptors before the metadata base. Fast commits are explicitly made ineligible for the final enable transaction.

## Test Signals
Tests should cover enabling verity on normal, encrypted, inline-data, DAX, non-extent, sparse, and quota-controlled files; crash or fault injection at each begin/write/end phase; orphan cleanup after interrupted enable; descriptor size/location validation with corrupt extents or trailing size fields; Merkle tree read/readahead offsets; cleanup of post-EOF metadata on failure; and verification that userspace file size and reads never expose hidden metadata blocks.
