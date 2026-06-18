# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/journal.h

## Role

Primary journal API and hot-path inline implementation.

## Major Responsibilities

- Documents journal purpose, on-disk layout, pinning, reclaim, flush/no-flush writes, recovery, blacklisting, options, and self-healing.
- Provides sequence helpers and buffer lookup helpers.
- Implements reservation ring-state counters and fast reservation acquisition.
- Provides journal entry add/init helpers.
- Defines reservation put behavior.
- Declares entry close/write, quiesce, flush, rewind, meta, halt, block/unblock, debug, and write-buffer coordination APIs.

## Key Data Access Patterns

- `journal_seq_to_buf()` requires `j->lock` and indexes `in_flight`.
- `journal_res_buf()` and `journal_res_data()` are lockless for held reservations via the four-slot ring.
- `journal_res_get_fast()` atomically advances `cur_entry_offset`, increments the current ring-slot count, checks watermark and entry capacity, and returns reservation metadata.

## Notable Details

Reservation state encodes current entry offset, ring index, and four buffer refcounts in one 64-bit atomic. This is the core concurrency primitive for journal writes.
