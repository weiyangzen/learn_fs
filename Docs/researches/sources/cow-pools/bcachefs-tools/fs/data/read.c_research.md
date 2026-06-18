# File Research: sources/cow-pools/bcachefs-tools/fs/data/read.c

## Purpose
Implements the bcachefs data read pipeline: extent lookup, device selection, IO submission, checksum/decryption/decompression, split/bounce handling, retry, self-heal, cache promotion, stale pointer handling, poisoning, and initialization of read biosets/mempools.

## Main Interfaces and Behavior
- The file-level documentation states the intended behavior: reads are transparent and self-healing; checksum/IO failures retry other replicas and can rewrite bad copies; read target selection adapts by device latency.
- Latency/congestion helpers compute per-device congestion and probabilistically mark targets congested, used to avoid promotion to overloaded targets. `bch2_dev_congested_to_text()` renders metrics when latency accounting is enabled.
- Promotion/self-heal:
  - `should_promote()` rejects already-promoted, unwritten, or congested-target reads.
  - `__promote_alloc()` creates a `promote_op` backed by `data_update`, either for cached promotion or self-heal after failures.
  - `promote_alloc()` decides whether to promote full extents, forces bounce/full read as needed, and marks the original read as self-healing for failure recovery.
  - Completion flows through `promote_start()`, `promote_start_work()`, `promote_done()`, and `promote_free()`.
- Error and retry:
  - `bch2_read_err_msg_trans()` formats inode/offset-aware errors.
  - `bch2_rbio_error()` either queues retry work for retryable errors or completes with failure.
  - `bch2_rbio_retry()` redoes lookup/read with `BCH_READ_in_retry`, clears hard device requirement, forces clone, disables promotion, tracks failures, and emits success/self-heal/error diagnostics.
  - `rbio_mark_io_failure()` records device/EC/checksum failures and propagates IO-error masks to parent data updates.
- Checksum/poison/narrowing:
  - `maybe_poison_extent()` marks extents with checksum errors as `BCH_EXTENT_FLAG_poisoned` when mounted read-write and updates a parent data update copy if needed.
  - `bch2_rbio_narrow_crcs()` can rechecksum an uncompressed checksummed extent and update its CRC entry after a full read, reducing future read amplification.
- End IO:
  - `bch2_read_endio()` accounts block IO completion, restores iterators, checks stale pointers, and punts to high-priority or unbound workqueues when checksum/compression/encryption/promotion/narrowing require process context.
  - `__bch2_read_endio_work()` validates checksum, decrypts, decompresses when necessary, copies bounced data, verifies data-update decompression when requested, and completes or returns retryable errors.
- Read submission:
  - `__bch2_read_extent()` handles inline data, poison checks, pointer selection via `bch2_bkey_pick_read_device()`, missing encryption keys, stale dirty pointers, read-full/bounce decisions, EC reconstruction reads, direct block IO submission, and retry-mode synchronous completion.
  - `read_extent_rbio_alloc()` allocates or reuses rbios, handles promotion rbios, clone/bounce decisions, adjusts CRC/pointer offsets for partial unencoded reads, sets bio sector/endio, traces, and increments clocks.
  - `read_extent_inline()` fills zeros before/after inline payload as needed.
  - `read_extent_hole()` zero-fills holes/reservations and reports overwritten keys to data-update retries.
- Top-level `bch2_read()` walks extent slots for a subvolume inode, resolves reflink indirect extents through `bch2_read_indirect_extent()`, splits a bio across extents, maintains previous-read failure state in retry mode, and calls `__bch2_read_extent()` for each fragment.
- Debug/text/init:
  - `bch2_read_bio_to_text()` and atomic helpers render rbio timing, state flags, selected pointer, and bio.
  - `bch2_fs_io_read_init()` allocates per-CPU promotion semaphores, bounce page mempool, and read/split biosets.
  - `bch2_fs_io_read_exit()` releases those resources.

## Dependencies and Coupling
Coupled to checksum/encryption, compression, EC reconstruction, btree extent lookup, subvolume snapshots, data update, write promotion, device IO refs, allocator targets, and error accounting.

## Risks and Invariants
- If reading into user-mapped buffers and checksum fails without bounce, the read is retried with forced bounce because userspace might have modified the buffer.
- For compressed/checksummed extents, partial logical reads may require full encoded extent reads.
- Retry mode is the only mode where `__bch2_read_extent()` returns many errors directly; non-retry mode generally completes through bio endio.
