# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.h

This header defines the B-tree read API and compatibility helpers.

Key elements:
- `btree_ptr_sectors_written()` extracts written-sector count from `btree_ptr_v2`.
- `bch2_bkey_in_btree_node()` validates key position against a node’s min/max range.
- `struct btree_read_bio` carries asynchronous read state, selected replica, work item, and bio.
- IO lock/wait declarations protect node read/write in-flight state.
- `btree_nonce()` and `bset_encrypt()` define metadata encryption/decryption nonce handling for first and subsequent bsets.
- Compatibility helpers transform old on-disk formats for inode btree changes, snapshot fields, endian conversion, and min/max key semantics.

The header connects read.c to B-tree cache, checksum, extents, fsck validation, and write/scrub consumers.
