# sources/distributed-fs/ceph-client/fs/btrfs/verity.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/verity.c` implements Btrfs support for the generic fs-verity operations. It stores fs-verity descriptors and Merkle tree bytes as dedicated Btrfs btree items in the file's filesystem tree while caching Merkle pages in the inode mapping at synthetic offsets past EOF. The file was read as a complete 800-line source file for this report.

## Important APIs, Types, and Functions

The public exported symbols are `btrfs_drop_verity_items()`, `btrfs_get_verity_descriptor()`, and `btrfs_verityops`. Private helpers include `merkle_file_pos()`, `drop_verity_items()`, `write_key_bytes()`, `read_key_bytes()`, `del_orphan()`, `rollback_verity()`, `finish_verity()`, `btrfs_begin_enable_verity()`, `btrfs_end_enable_verity()`, `btrfs_read_merkle_tree_page()`, and `btrfs_write_merkle_tree_block()`.

On disk, descriptor metadata uses `BTRFS_VERITY_DESC_ITEM_KEY`: offset 0 stores `struct btrfs_verity_descriptor_item`, and offsets starting at 1 store the opaque fs-verity descriptor bytes. Merkle tree bytes use `BTRFS_VERITY_MERKLE_ITEM_KEY` with byte offsets starting at 0.

## Control Flow

Enabling verity begins with `btrfs_begin_enable_verity()`, called through fs-verity. It requires the inode lock, rejects encrypted inodes, rejects concurrent enable attempts via `BTRFS_INODE_VERITY_IN_PROGRESS`, drops any stale verity items, starts a transaction, adds an orphan item, and sets the in-progress runtime flag.

While fs-verity builds the Merkle tree, `btrfs_write_merkle_tree_block()` writes each block to `BTRFS_VERITY_MERKLE_ITEM_KEY` items through `write_key_bytes()`, which chunks data into up to 2 KiB btree items and uses a small transaction per item. At the end, `btrfs_end_enable_verity()` either rolls back on a NULL descriptor/error path or calls `finish_verity()`. Finish writes the descriptor header and descriptor blob, marks the inode `BTRFS_INODE_RO_VERITY`, syncs inode flags, updates the inode, deletes the verity orphan, clears the in-progress bit, and sets the filesystem read-only compatible verity bit.

Reading uses `btrfs_get_verity_descriptor()` as a two-pass descriptor API: size query when `buf_size == 0`, then exact descriptor read. Merkle reads use `btrfs_read_merkle_tree_page()`, which computes the synthetic cache index past EOF, looks up or allocates a folio in the file mapping, reads one page of Merkle bytes from btree items via `read_key_bytes()`, zero-fills short reads, marks the folio uptodate, and returns the page to fs-verity.

Rollback clears cached pages past EOF, clears in-progress, drops descriptor and Merkle items, clears the inode verity ro flag, updates the inode, and deletes the orphan. `btrfs_drop_verity_items()` is also used by inode orphan cleanup paths for interrupted enables.

## State and Persistence Behavior

Persistent state lives in filesystem-tree items keyed by inode objectid plus descriptor or Merkle key type. Verity completion also persists the inode ro flag and the filesystem compat-ro verity feature bit. The orphan item is persistent crash-recovery state for an in-progress enable; it lets Btrfs identify and clean partial verity metadata if enable fails or is interrupted.

Runtime state includes `BTRFS_INODE_VERITY_IN_PROGRESS`, page-cache folios at synthetic post-EOF offsets, inode `i_flags` synchronized from Btrfs ro flags, and fs-verity's calls through `struct fsverity_operations`. `merkle_file_pos()` rounds `i_size` up to 64 KiB so cached Merkle pages are beyond the last possible data page even with 64 KiB pages and checks `s_maxbytes` overflow.

## Dependencies and Integration Points

This file depends on the generic fs-verity API, Btrfs transactions, orphan handling, inode flag synchronization, btree item accessors, extent-buffer reads/writes, filemap/folio APIs, and superblock feature bits. `super.c` installs `btrfs_verityops` as `sb->s_vop`; `inode.c` invokes `btrfs_drop_verity_items()` during orphan cleanup; `accessors.h` provides descriptor item accessors; and Btrfs ioctl/inode paths rely on the inode verity flag state after completion.

## Risks and Edge Cases

Enable is a multi-transaction operation that can run out of space partway through a large Merkle tree. The orphan/in-progress protocol is the main protection against persistent partial state, so failures in rollback are escalated with filesystem errors. Encryption is explicitly unsupported because descriptor and Merkle items are stored as metadata rather than file data.

`read_key_bytes()` allows short reads; descriptor reads convert short descriptor blobs to `-EIO`, while Merkle page reads zero-fill missing tail bytes. Descriptor reserved fields and oversized descriptor sizes are treated as corruption (`-EUCLEAN`). Synthetic Merkle cache offsets must not overflow `s_maxbytes`, especially for large files. `write_key_bytes()` can leave earlier chunks written if a later insert fails, so callers must rely on rollback/drop paths.

## Test Signals

Useful tests include generic fs-verity enable/measure/read verification on Btrfs, enable failure injection during Merkle and descriptor writes, crash/orphan cleanup during in-progress enable, large-file Merkle offset overflow checks, descriptor size query/read mismatch, encrypted inode rejection, page-cache reuse of Merkle folios, and inode flag persistence across remount. Btrfs-specific tests should verify that partial verity items are dropped and that the compat-ro feature bit is set only after successful finish.
