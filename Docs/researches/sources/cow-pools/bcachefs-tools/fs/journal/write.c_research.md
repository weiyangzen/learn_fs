# File Research: sources/cow-pools/bcachefs-tools/fs/journal/write.c

This file implements journal write allocation, preparation, checksum/encryption, submission, completion, and write scheduling.

Key responsibilities:
- Allocates journal write destinations across eligible devices and replicas.
- Advances devices to a new journal bucket when current bucket space is insufficient.
- Reallocates journal buffers and resizes the btree write buffer as needed.
- Prepares jsets for write by compacting entries, converting write-buffer keys, adding btree roots, datetime, usage, and clock entries.
- Sets journal magic/version/endian/checksum/encryption flags and computes checksums.
- Submits journal writes through bios, including optional separate preflush bios.
- Handles write completion, replica accounting, degraded writes, errors, emergency read-only transition, and in-flight FIFO advancement.
- Decides whether a journal entry should be flush or noflush and schedules writes from the oldest unallocated sequence.

Important control flow:
- `journal_write_alloc()` first tries the configured metadata/foreground target, then falls back to all devices.
- `__journal_write_alloc()` pins each selected device with a write I/O ref, appends an extent pointer, records the device in `w->cas[]`, updates bucket free space and bucket sequence, and accumulates durability.
- `bch2_journal_write_prep()` flushes write-buffer keys into the write buffer, converts them to btree keys, updates btree roots, marks empty entries, appends common superblock entries, and enforces reserved space.
- `bch2_journal_write_checksum()` validates before checksum when encryption or old metadata versions require it, encrypts payload, computes checksum, then zero-fills sector padding.
- `journal_write_submit()` maps the journal buffer into one or more bios per pointer and submits with sync/idle/meta flags plus FUA/PREFLUSH as needed.
- `journal_write_done()` advances `seq_ondisk`, `flushed_seq_ondisk`, `last_seq_ondisk`, `rewind_seq_ondisk`, releases replica refs in order, wakes waiters, recycles buffers, and recalculates journal space.
- `bch2_journal_do_writes_locked()` starts writes only when no reservations remain for the sequence and flush ordering permits.

Important invariants:
- `write_done` means all post-completion bookkeeping is finished, not merely that the bio completed.
- Flush writes are serialized so `seq_ondisk + 1 == seq` before submission.
- Separate flush is used when more than one read-write member exists.
- Clean superblock state delays journal replica marking until after write completion.
- If `nochanging` mode is enabled, I/O refs are released and completion runs without submitting bios.
- On demoting a flush to noflush, waiters and `must_flush` are carried forward to the next eligible entry.

Dependencies:
- Uses allocator target selection, device write refs, extent pointers, checksums/encryption, btree roots, btree write buffer, journal reclaim/validation, clean superblock helpers, counters, closures, bios, and block flush/FUA semantics.

Research notes:
- The completion path is race-sensitive. Comments document why `write_done` is set only after replica refs and sequence advancement are safe.
- The write scheduler balances latency through noflush writes while preserving enough flush writes for recovery and clean/dirty transitions.
