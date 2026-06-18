# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/types.h

## Role

Defines the journal runtime and device data structures used by journal init, read, write, reclaim, and recovery.

## Major Structures

- `struct journal_buf`: one in-flight journal entry buffer with staged `jset`, target devices, write state, flush flags, sizing, and closure waiters.
- `struct journal_ringbuf`: four-slot reservation fastpath cache for current buffer/data pointers.
- `struct journal_entry_pin_list`: per-sequence pin lists and refcount.
- `struct journal_entry_pin`: pin object with flush callback and sequence.
- `struct journal_res`: held reservation metadata.
- `union journal_res_state`: 64-bit atomic reservation state packing current offset, ring index, and four refcounts.
- `struct journal`: filesystem-wide journal state, including reservations, flags, buffers, in-flight FIFO, sequence tracking, rewind ranges, pin FIFO, space accounting, write point, reclaim state, stats, and locks.
- `struct journal_device`: per-device journal bucket array, bucket sequence table, ring indices, bioset, discard work, and read state.
- `struct journal_start_info`: recovery-computed sequence window used to start the journal.

## Important Constants

- `JOURNAL_SEQ_MAX` limits usable sequence numbers to 56 bits because the btree write buffer uses high bits.
- `JOURNAL_STATE_BUF_NR` is four reservation ring slots.
- Journal entries range from 64 KiB to 4 MiB.
- Special `cur_entry_offset` sentinel values represent blocked, closed, and error states.

## Notable Details

`journal_start_info` documents the three recovery zones: replay `[last_seq, replay_end]`, blacklist `[replay_end + 1, cur_seq)`, and new writes from `cur_seq`.
