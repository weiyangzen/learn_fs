# File Research: sources/cow-pools/bcachefs-tools/fs/btree/read.h

Read completeness: full file read, 184 lines.

Purpose: public interface and inline helpers for btree node reads, bset encryption/decryption, validation, root reads, scrub, and metadata-version compatibility transforms.

Key definitions:
- `btree_ptr_sectors_written()` extracts `sectors_written` from `KEY_TYPE_btree_ptr_v2`.
- `bch2_bkey_in_btree_node()` validates a key position against a node's min/max range and reports fsck errors.
- `struct btree_read_bio` embeds a bio plus filesystem/device/node context, selected extent pointer, work item, timing, and async object-list index.
- `btree_nonce()` derives a metadata nonce from bset offset, bset sequence, journal sequence, and `BCH_NONCE_BTREE`.
- `bset_encrypt()` encrypts/decrypts the btree header region for offset zero and the bset data for all offsets.
- `compat_bformat()`, `compat_bpos()`, and `compat_btree_node()` implement on-disk compatibility for inode btree field order and pre-snapshot formats.

Declared API:
- IO coordination: `bch2_btree_node_io_lock()`, `bch2_btree_node_io_unlock()`, `bch2_btree_node_wait_on_read()`, `bch2_btree_node_wait_on_write()`, and the `btree_node_io_lock` guard.
- Validation: `bch2_validate_bset_keys()`, `bch2_validate_bset()`, and `bch2_btree_node_read_done()`.
- Read/scrub operations: `bch2_btree_node_read()`, `bch2_btree_root_read()`, `bch2_btree_node_scrub()`, and `bch2_btree_flush_all_reads()`.

Dependencies and integration:
- Includes bkey methods, bset helpers, locking, checksum, extents, and init error definitions.
- Used by `read.c`, `node_scan.c`, write validation, and recovery code.

Risks and validation notes:
- `bset_encrypt()` is symmetric and called for both encryption and decryption; nonce offset handling must match on-disk block layout.
- Compatibility helpers intentionally mutate positions and formats; applying them twice or in the wrong direction would corrupt interpretation.
