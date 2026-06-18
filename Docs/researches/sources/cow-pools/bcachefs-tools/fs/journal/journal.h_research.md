# File Research: sources/cow-pools/bcachefs-tools/fs/journal/journal.h

Core journal API and inline hot-path helpers for reservations, entries, flushing, blocking, and debug.

Key contents:
- Large design comment explaining:
  - Journal purpose as btree update log.
  - Persistence behavior for synchronous/asynchronous metadata updates.
  - `jset` entry structure and sequence numbers.
  - Ring-buffer bucket layout.
  - Dirty/open journal entry tracking through `last_seq`, per-device bucket seqs, and pin refs.
  - Journal-full handling through dirty btree flushing.
- Provides basic state helpers:
  - `journal_wake()`
  - `journal_med_on_space()`
  - `journal_low_on_space()`
  - `journal_cur_seq()`
  - `journal_last_unallocated_seq()`
  - `journal_cur_buf()`
- Provides sequence/buffer lookup:
  - `journal_seq_to_buf()` under journal lock.
  - `journal_res_buf()` and `journal_res_data()` fast path for held reservations.
- Provides reservation state bitfield helpers:
  - `journal_state_count()`
  - `journal_state_seq_count()`
  - `journal_state_inc()`
  - `journal_state_buf_put()`
- Provides journal entry size/overhead helpers:
  - `jset_u64s()`
  - `journal_entry_overhead()`
- Provides entry construction helpers:
  - `bch2_journal_add_entry_noreservation()`
  - `journal_res_entry()`
  - `journal_entry_init()`
  - `journal_entry_set()`
  - `__bch2_journal_add_entry()`
  - `bch2_journal_add_entry()`
  - `journal_entry_empty()`
- Provides error helper:
  - `bch2_journal_error()`
- Provides buffer/ref release helpers:
  - `__bch2_journal_buf_put()`
  - `bch2_journal_buf_put()`
  - `bch2_journal_res_put()`
- Defines reservation flags:
  - `JOURNAL_RES_GET_NONBLOCK`
  - `JOURNAL_RES_GET_CHECK`
- Implements fast reservation acquisition in `journal_res_get_fast()`:
  - Atomically reserves space in the current open journal entry.
  - Checks entry capacity, watermark, and ring-slot refcount overflow.
  - Supports check-only mode.
  - Fills reservation seq/offset/overwrite state on success.
- Implements public inline `bch2_journal_res_get()` wrapper:
  - Asserts journal running.
  - Uses fast path, then slow path.
  - Acquires lockdep shared map for real reservations.
- Declares non-inline journal APIs for close, put-final, slowpath, quiesce, shutdown quiesce, write work, reservation resizing, flushes, rewind, noflush, metadata flush, halt, block/unblock, write-buffer flush selection, and debug formatting.
- Defines RAII class `journal_block` for scoped blocking/unblocking.

Role:
- This is the hot-path interface used by btree transactions and metadata update code to reserve journal space and append entries.
- Keeps lockless/atomic reservation logic inline for performance while delegating slow/error paths to `journal.c`.

Notable invariants:
- Held reservations pin their ring slot, allowing lockless `journal_res_buf()` lookup.
- `bch2_journal_res_put()` pads unused reserved space with empty btree-key entries before dropping the buffer ref.
- `bch2_journal_res_get()` assumes `JOURNAL_running` and no foreign stop thread unless the journal is already in error state.
