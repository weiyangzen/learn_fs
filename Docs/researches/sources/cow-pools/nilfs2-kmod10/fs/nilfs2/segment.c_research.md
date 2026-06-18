# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.c

## Summary
Implements the NILFS2 segment constructor and log writer. It coordinates filesystem transactions, dirty buffer collection, logical segment construction, super-root creation, data-sync segment writes, cleaner-driven segment migration, writeback completion, and segctord lifecycle.

## Main Responsibilities
- Provides transaction begin/commit/abort locking around NILFS metadata updates.
- Runs the `segctord` kernel thread and request/timer machinery.
- Collects dirty file, metadata, DAT, checkpoint, sufile, and GC inode blocks into segment buffers.
- Builds segment summaries, finfo/binfo records, super-root blocks, and segment usage updates.
- Allocates, extends, truncates, cancels, or frees segment buffers through sufile state.
- Assigns final block numbers through bmap/DAT machinery before writeout.
- Handles fsync-style data-only logical segments and full checkpoint-forming logical segments.
- Implements cleaner entry point `nilfs_clean_segments()`.

## Key APIs
- `nilfs_transaction_begin()`, `nilfs_transaction_commit()`, `nilfs_transaction_abort()`.
- `nilfs_relax_pressure_in_lock()`.
- `nilfs_construct_segment()`.
- `nilfs_construct_dsync_segment()`.
- `nilfs_flush_segment()`.
- `nilfs_clean_segments()`.
- `nilfs_attach_log_writer()`, `nilfs_detach_log_writer()`.

## Important Behavior
The segment constructor is staged through `NILFS_ST_INIT`, GC, file, ifile, cpfile, sufile, DAT, super-root, dsync, and done stages. Stage changes go through wrapper helpers so tracepoints are emitted.

Normal checkpoint construction uses `SC_LSEG_SR`; data-only operations use `SC_LSEG_DSYNC`, `SC_FLUSH_FILE`, or `SC_FLUSH_DAT`. Full checkpoint construction creates a checkpoint, writes metadata files, optionally frees cleaned segments, writes DAT, appends a super root, updates sufile usage, and advances `ns_cno`.

If the current set of segment buffers fills after checkpoint metadata collection begins, collection can retry after extending the segment chain. If segment construction fails, it redirties affected inodes, cancels pending sufile frees, frees incomplete logs, and marks failed segments or discontinuity as needed.

`nilfs_segctor_update_payload_blocknr()` assigns physical block numbers after collection and writes the proper binfo format for normal files, DAT, or dsync mode. The write path marks folios/buffers for writeback, adds checksums, submits logs, then completes or aborts folio/buffer state.

The background thread waits on commit, explicit sync, flush, and timer conditions. It can choose between full checkpoint construction and lightweight file/DAT flush depending on unclosed logical segment state and pending flush bits.

## State and Synchronization
Uses `ns_segctor_sem` as the primary exclusion boundary between transactions and the writer. Normal file operations take it read-side; segment construction takes it write-side. Per-task transaction context lives in `current->journal_info`.

`sc_state_lock` protects segctord request state, timer state, flush bits, and request sequence counters. `ns_inode_lock` protects dirty inode queues. Completion to synchronous callers is handled by sequence-numbered wait requests on `sc_wait_request`.

## Risks
This file is one of the most concurrency-sensitive parts of NILFS2. Correctness depends on pairing transaction begin/commit/abort, not calling synchronous construction from inside a transaction, preserving collection stage state across retries, and canceling sufile changes on every failure path.

Segment allocation and write failure handling are delicate: partial writes can discontinue the log chain, mark segments erroneous, or require fallback superblock behavior. Folio writeback handling has special cases for split b-tree node buffers and blocksize smaller than page size.
