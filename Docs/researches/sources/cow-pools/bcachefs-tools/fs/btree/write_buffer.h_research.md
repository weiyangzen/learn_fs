# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.h

Read completeness: full file read, 208 lines.

Purpose: public API and inline helpers for btree write-buffer indexing, insertion into journal write-buffer entries, accounting accumulation, maybe-flush state, and lifecycle/stat operations.

Key definitions and helpers:
- `bch_wb_btree_idx()` maps a `BTREE_ID_*` that uses the write buffer to dense `BCH_WB_BTREE_*` indexes.
- `bch_wb_btree_to_btree_id()` maps dense write-buffer indexes back to btree ids.
- `bch2_btree_write_buffer_must_wait()` reports pressure when total buffered keys exceed three quarters of allocated intake size.
- `struct wb_maybe_flush` tracks the last key that caused a maybe-flush, flush count, processed count, and whether an error was seen.
- `struct journal_keys_to_wb_btree` and `struct journal_keys_to_wb` track per-btree intake locks/room for converting one journal sequence into write buffers.
- `wb_key_cmp()` compares buffered keys by bpos for accounting eytzinger lookup.
- `bch2_accounting_key_to_wb()` fast-finds an existing accounting accumulator and adds a delta, falling back to `bch2_accounting_key_to_wb_slowpath()`.
- Low-level key layout helpers compute variable buffered-key size and iterate packed buffered-key arrays.
- `bch2_journal_key_to_wb_reserved()`, `__bch2_journal_key_to_wb()`, and `bch2_journal_key_to_wb()` append journal keys into the correct per-btree write buffer with validation and accounting special handling.

Declared API:
- Flush: `bch2_btree_write_buffer_flush_sync()`, `bch2_btree_write_buffer_flush_going_ro()`, `bch2_btree_write_buffer_tryflush()`, and `bch2_btree_write_buffer_maybe_flush()`.
- Journal conversion: `bch2_journal_keys_to_write_buffer_start()` and `bch2_journal_keys_to_write_buffer_end()`.
- Sizing/stats/lifecycle: `bch2_btree_write_buffer_resize()`, `bch2_btree_write_buffer_to_text()`, `bch2_btree_write_buffer_stop()`, `bch2_btree_write_buffer_start()`, `bch2_fs_btree_write_buffer_exit()`, `bch2_fs_btree_write_buffer_init_early()`, and `bch2_fs_btree_write_buffer_init()`.

Dependencies and integration:
- Includes bkey buffers and accounting helpers; relies on `write_buffer_types.h` through `types.h`.
- Used by journal replay/intake, transaction buffered updates, fsck maybe-flush checks, and write-buffer lifecycle code.

Risks and validation notes:
- `bch_wb_btree_idx()` intentionally `BUG()`s on non-write-buffer btrees; callers should use `bch2_btree_write_buffer_insert_checks()` before converting arbitrary btree ids.
- Buffered key arrays are stored as raw `u64` darrays with variable-size records; iterator helpers must be used consistently to avoid misalignment.
