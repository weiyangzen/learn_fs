# File Research: sources/cow-pools/bcachefs-tools/fs/btree/update.h

Read completeness: full file read, 484 lines.

Purpose: public transaction update API, commit flag definitions, buffered-update helpers, transaction subbuffer helpers, commit wrappers, and mutable-key allocation helpers.

Key declarations and flags:
- Node write/update declarations: `bch2_btree_node_prep_for_write()`, `bch2_btree_bset_insert_key()`, journal pin flush callbacks, `bch2_btree_add_journal_pin()`, and `bch2_btree_insert_key_leaf()`.
- `BCH_TRANS_COMMIT_FLAGS()` defines commit flags for ENOSPC checking, write refs, journal reservation handling, noop skipping, journal reclaim, journal replay, and accounting application.
- Update operations include delete, insert, range delete, bit modification, snapshot whiteout insertion, extent overwrite handling, empty slot lookup, and trigger mutable-new access.
- `bch2_trans_update_ip()`, `bch2_trans_update_buf()`, and `bch2_trans_update()` are the core update staging APIs.
- Transaction subbuffer helpers expose typed allocation for `trans->journal_entries` and `trans->accounting`.
- `bch2_trans_commit()` sets disk reservation and journal sequence output before calling `__bch2_trans_commit()`.
- Retry wrappers `commit_do`, `nested_commit_do`, and deprecated `bch2_trans_commit_do` integrate with lock-restart loops.

Buffered update logic:
- `bch2_btree_write_buffer_insert_checks()` rejects write-buffer updates for btrees not marked `BTREE_IS_write_buffer`.
- `bch2_trans_update_buffered()` validates memory, uses direct clone insert during most journal replay, and otherwise appends a `BCH_JSET_ENTRY_write_buffer_keys` journal entry. Accounting updates remain buffered during replay because they are deltas requiring strict flush order.

Mutable key helpers:
- `__bch2_bkey_make_mut_noupdate()` reassembles an immutable key into transaction memory, optionally type-checking and padding to a minimum size.
- `bch2_bkey_make_mut*()` variants also stage the updated key through an iterator.
- `bch2_bkey_get_mut*()` variants initialize an intent iterator, fetch a key, copy it into transaction memory, and stage it.
- `bch2_bkey_alloc()` allocates and initializes a new typed key at the iterator position and stages it.

Dependencies and integration:
- Includes iterator, journal, superblock IO, and snapshot helpers.
- Implemented by `update.c` and commit code elsewhere.
- Used widely by filesystem metadata operations that modify btrees.

Risks and validation notes:
- `bch2_trans_reset_updates()` drops path refs and zeroes subbuffer sizes; callers must not hold pointers into transaction memory across restarts.
- `bch2_trans_commit_lazy()` returns a transaction restart after a successful commit when updates existed, forcing callers in lazy contexts to restart.
- Buffered update journal entries preserve original ordering; re-journaling write-buffered keys later would break recovery order.
