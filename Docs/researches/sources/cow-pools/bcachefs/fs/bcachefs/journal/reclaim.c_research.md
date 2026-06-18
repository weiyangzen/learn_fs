# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.c

## Role

Implements journal space accounting, discard scheduling, pin management, reclaim flushing, reclaim thread lifecycle, targeted pin flushes, and reclaim diagnostics.

## Major Responsibilities

- Computes available journal space at discarded, clean-on-disk, clean, and total levels.
- Maintains journal watermarks for low space, low pin FIFO capacity, and write-buffer pressure.
- Advances dirty/discard indices and queues discard work.
- Updates `last_seq` as pin refcounts reach zero.
- Transfers journal replica references as entries become clean on disk.
- Drops replay pins as journal replay progresses.
- Sets, copies, drops, and flushes journal pins.
- Selects pins to flush by sequence and pin type.
- Runs direct/background reclaim and starts/stops the reclaim kthread.
- Flushes all pins, outstanding pins, or pins involving a specific device.
- Prints pin/reclaim debug state and timing stats.

## Space Accounting

`bch2_journal_space_available()` walks online journal devices, advances `dirty_idx` and `dirty_idx_ondisk` based on `last_seq` and `last_seq_ondisk`, computes per-replica available space, sets `JOURNAL_may_skip_flush`, updates the watermark, and sets `cur_entry_sectors` or `journal_full`.

## Pin/Reclaim Flow

Journal pins are organized per sequence into unflushed/flushed lists by type. `journal_flush_pins()` picks the oldest eligible pin, records `flush_in_progress`, calls its flush callback, moves it to the flushed list if still valid, and records timing by type.

`__bch2_journal_reclaim()` chooses `seq_to_flush` based on half-full journal buckets and pin FIFO pressure, forces at least one flush after reclaim delay or under pressure, includes key-cache dirty limits, and loops for background reclaim while useful work continues.

## Notable Details

- Reclaim will not flush unreplayed pins to avoid deadlocking journal replay.
- Discard work only issues block discards when changes are allowed and discard is enabled; it always advances discard indices after bucket cleanup.
- Shutdown pin flushing is type-ordered and intentionally avoids closing extra journal entries until pins are actually flushed.
