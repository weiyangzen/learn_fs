# File Research: sources/block-storage/kvdo/vdo/recovery-journal-block.c

Read completely: 396 lines.

This file manages one in-memory recovery journal block and its on-disk packed representation. It allocates the block buffer and metadata VIO, initializes block headers/sectors, queues data VIOs waiting for journal entries, packs queued entries into sectors, and submits the journal block write.

`vdo_initialize_recovery_block()` clears the block buffer, fills a packed header with metadata type, nonce, recovery count, sequence number, check byte, and usage counters, sets the on-disk circular block number, and initializes sector 1 as the active sector. Sector 0 is the header; subsequent sectors hold packed entries with per-sector check/recovery bytes.

`vdo_enqueue_recovery_block_entry()` queues a data VIO for the next commit, increments entry counts, and updates journal started counters. `add_queued_recovery_entries()` drains entry waiters, builds `struct recovery_journal_entry` values from each data VIO operation and tree-lock slot, packs them into the active sector, tracks FUA requirements for data increments, moves VIOs to commit waiters, and advances sectors when full. `vdo_commit_recovery_block()` validates commit readiness, translates the journal partition block to PBN, updates header heads and entry count, sets write flags including preflush/sync and optional FUA, and submits the metadata VIO.

Dependencies: data VIOs, tree locks, packed recovery journal format, metadata VIO submission, partition translation, wait queues, recovery journal state, and read-only notifier checks.

Security/reliability notes: commit is refused when the journal is read-only, already committing, or has no queued entries. The write path always uses a flush because journal ordering protects data references and previous mappings. If queuing to commit waiters fails, the affected data VIO is continued with the error.
