# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write.h

Read completeness: full file read, 45 lines.

Purpose: public declarations and data structure for btree node write IO.

Key definitions:
- `struct btree_write_bio` wraps a work item, copied btree pointer key, bounce data pointer and size, sector offset, timing, optional async object-list index, and embedded `struct bch_write_bio`.
- `enum btree_write_flags` extends write type bits with `BTREE_WRITE_only_if_need` and `BTREE_WRITE_already_started`.
- `btree_node_write_if_need()` is a convenience wrapper around `bch2_btree_node_write_trans()`.

Declared API:
- `bch2_btree_post_write_cleanup()`
- `__bch2_btree_node_write()`
- `bch2_trans_submit_write_bios()`
- `bch2_btree_node_write_trans()`
- `bch2_btree_init_next()`
- `bch2_btree_write_stats_to_text()`
- `bch2_btree_flush_all_writes()`
- `bch2_btree_cancel_all_writes()`

Dependencies and integration:
- Includes data write types for `struct bch_write_bio`.
- Implemented by `write.c` and used by traversal, update, cache reclaim, journal reclaim, and read wait paths.

Risks and validation notes:
- `BTREE_WRITE_only_if_need` and write-type bits share the same integer namespace; additions must preserve the `BTREE_WRITE_TYPE_BITS` offset convention from `types.h`.
