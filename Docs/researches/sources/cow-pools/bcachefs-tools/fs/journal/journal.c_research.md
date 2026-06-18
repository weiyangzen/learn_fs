# File Research: sources/cow-pools/bcachefs-tools/fs/journal/journal.c

Core journal reservation, entry lifecycle, flushing, blocking, rewind metadata, stuck detection, and debug formatting implementation.

Key responsibilities:
- Contains extensive embedded documentation describing:
  - Journal as write-ahead log for metadata btree updates.
  - Variable-sized `jset` entries and typed subentries.
  - Ring-buffer bucket layout across devices.
  - Dirty/open journal entry tracking through pins.
  - Journal space pressure and reclaim behavior.
  - Flush versus no-flush writes.
  - Recovery, clean shutdown, sequence blacklisting, user-facing options, and replication.
- Tracks open/closed journal entry state and unwritten entry counts.
- Formats journal buffers and in-flight buffers for debug output.
- Detects stuck journal conditions in `journal_error_check_stuck()`:
  - Only for journal-full or pin-full under reclaim watermark.
  - Requires no unwritten entries and no discard ability.
  - Emits debug state and forces emergency read-only.
- Finalizes journal buffer refs in `bch2_journal_buf_put_final()`:
  - Drops pin-list refs.
  - Updates last sequence.
  - Starts writes if needed.
  - Wakes waiters.
- Closes journal entries in `__journal_entry_close()`:
  - Atomically transitions reservation state to closed/error.
  - Writes final `u64s`, computes dirty bytes and sectors.
  - Validates entry did not overrun reserved space.
  - Sets `last_seq` just before opening the next entry to preserve pin ordering semantics.
  - Cancels delayed write work, recomputes space, and drops the opening pin reference.
- Halts journal through `bch2_journal_halt_locked()` / `bch2_journal_halt()`, closing current entry with error value and recording `err_seq`.
- Provides close wrappers:
  - `bch2_journal_entry_close_locked()`
  - `bch2_journal_entry_close()`
- Opens a new journal entry in `journal_entry_open()`:
  - Rejects blocked/error/full states, pin FIFO full, in-flight FIFO full, max-open limit, sequence overflow, blacklisted next sequence, and missing free buffer.
  - Computes current entry capacity from sectors and reserved overhead.
  - Allocates pin and in-flight FIFO slots.
  - Claims preallocated buffer.
  - Initializes `jset` header, sequence, ring fastpath slot, early journal entries, and reservation state.
  - Arms delayed flush work and wakes waiters/reclaim.
- Quiesces journal:
  - `bch2_journal_quiesce()` waits until `seq == seq_ondisk`.
  - `bch2_journal_shutdown_quiesce()` waits for flushed bookkeeping when healthy, or regular seq-on-disk when in error state.
- Implements auto-commit delayed work through `bch2_journal_write_work()`.
- Maintains preallocated free buffer through `journal_buf_prealloc()`.
- Implements slowpath journal reservation in `__journal_res_get()` and `bch2_journal_res_get_slowpath()`:
  - Rechecks fast path.
  - Opens/closes entries as needed.
  - Grows desired buffer size when current buffer fills before disk capacity.
  - Tracks blocked time stats for journal blocked, max in-flight, max open, full, pin full, buffer ENOMEM, and stuck.
  - Directly invokes reclaim when journal is full/pin-full and caller can block.
  - Emits debug after long waits.
- Resizes reserved per-entry space with `bch2_journal_entry_res_resize()`.
- Implements flush APIs:
  - `bch2_journal_flush_seq_async()` waits for or forces a flush for a sequence, handles already-flushed and error states, skips no-flush entries, opens an empty flush entry when needed, sets `must_flush`, and closes entries to trigger writes.
  - `bch2_journal_flush_seq()` synchronously waits and logs after 10 seconds.
  - `bch2_journal_flush_async()` and `bch2_journal_flush()` provide convenience wrappers.
- Implements metadata flush:
  - `__bch2_journal_meta()` writes an empty must-flush metadata entry.
  - `bch2_journal_meta()` wraps it in a filesystem write ref.
- Implements rewind metadata:
  - `bch2_journal_advance_rewind_seq()` advances rewind discard safety limit.
  - `bch2_journal_add_rewind_range()` records an in-memory rewind range and stages a `BCH_JSET_ENTRY_rewind` early journal entry.
- Implements `bch2_journal_noflush_seq()` to mark unwritten entries in a range as no-flush when feature is enabled and no flush has already crossed the range.
- Blocks/unblocks journal:
  - `bch2_journal_block()` marks open entry blocked, quiesces writes, and prevents new reservations.
  - `bch2_journal_unblock()` restores saved entry offset and wakes waiters.
- Supports write-buffer flushing through `bch2_next_write_buffer_flush_journal_buf()`, optionally blocking an open entry until outstanding refs drain.
- Formats complete journal debug state through `__bch2_journal_debug_to_text()` and `bch2_journal_debug_to_text()`.

Important interactions:
- Reservation fast path is shared with inline helpers in `journal.h`.
- Actual journal writes and space accounting are in `journal/write.c` and `journal/reclaim.c`.
- Emergency RO path calls back into `init/fs.c`.
- Rewind entries are consumed by `journal/read.c` and recovery.
- Write-buffer flush integration coordinates journal ordering with btree write buffer state.

Notable invariants:
- Sequence numbers are monotonic and blacklisted sequences must not be reused.
- Reservation ring slot must be published before reservation counter state changes.
- `last_seq` is set at entry close, before the next entry opens, to preserve crash replay guarantees.
- In error state, flush waiters for not-yet-flushed sequences return an error instead of waiting forever.
