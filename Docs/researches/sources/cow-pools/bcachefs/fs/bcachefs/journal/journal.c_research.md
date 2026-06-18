# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.c

## Role

Core journal reservation, entry open/close, write triggering, flush, rewind-range, blocking, and diagnostics implementation.

## Major Responsibilities

- Opens and closes journal entries around atomic reservation state.
- Starts writes when a closed buffer has no outstanding reservation references.
- Tracks unwritten buffers in `in_flight`.
- Detects stuck journal conditions and forces emergency read-only.
- Provides slowpath reservation acquisition with reclaim and wait diagnostics.
- Resizes reserved per-entry space.
- Flushes specific sequences or current journal metadata.
- Adds rewind ranges to runtime state and early journal entries.
- Marks journal ranges as no-flush when supported.
- Blocks/unblocks journal reservations for write-buffer flush coordination.
- Exposes detailed debug text for journal state and devices.

## Key Mechanics

The hot reservation path uses `journal_res_get_fast()` in `journal.h`; when it fails, `bch2_journal_res_get_slowpath()` may preallocate buffers, close the current entry, open a new one, run reclaim, or wait on `async_wait`.

`journal_entry_open()` increments the global sequence, creates a pin FIFO entry, pushes an `in_flight` buffer, claims the preallocated data buffer, publishes the four-slot ring pointer, copies early entries, and atomically marks the entry open.

`__journal_entry_close()` atomically closes the entry, finalizes `u64s`, records bytes, checks reserved sector bounds, writes `last_seq`, refreshes space accounting, and drops the opening pin reference so the write can begin when references drain.

## Flush/Rewind Details

`bch2_journal_flush_seq_async()` marks a buffer as `must_flush`, opens an empty entry if needed, waits on the target buffer, and closes the current entry when appropriate. `bch2_journal_add_rewind_range()` records runtime rewind bounds and appends a persistent rewind entry to `early_journal_entries`.

## Notable Details

- The journal can be halted by closing the current entry with `JOURNAL_ENTRY_ERROR_VAL`.
- `bch2_journal_noflush_seq()` refuses no-flush if a relevant flush is already requested or persisted.
- `bch2_next_write_buffer_flush_journal_buf()` can block the journal, wait for reservation refs to drain, and hand a buffer to the btree write buffer.
