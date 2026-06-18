# subset-b-008674 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block.cc -->
# sources/storage-engines/rocksdb/table/block_based/block.cc

## Purpose

`block.cc` implements the parsed block reader and iterator algorithms declared in `block.h`. It decodes uncompressed block-based table blocks produced by `block_builder.cc`, supports data, metadata, and index block iteration, and handles modern block-format features such as data-block hash indexes, separated key/value storage, value-delta-encoded index entries, interpolation search for uniform index blocks, global-sequence-number rewriting, user-defined timestamp padding, read-amplification accounting, and per-key/value checksum verification.

## Important APIs, types, and functions

- `DataBlockIter::SeekImpl`, `SeekForGetImpl`, `SeekForPrevImpl`, `NextImpl`, `PrevImpl`, `SeekToFirstImpl`, and `SeekToLastImpl` implement ordered navigation over internal-key data blocks. `SeekForGetImpl` uses `DataBlockHashIndex` when present, falling back to binary restart search on collisions or unsupported value types.
- `MetaBlockIter` implements the same movement primitives for metadata blocks, using strict entry decoding and bytewise user-key ordering.
- `IndexBlockIter::SeekImpl`, `PrefixSeek`, `BinaryBlockIndexSeek`, `FindRestartPointForSeek`, `DecodeCurrentValue`, and movement methods implement index-block lookup. It supports prefix-index lookup, binary search, interpolation search, delta-encoded block handles, optional first internal key, and global seqno rewriting for first keys.
- `BlockIter<TValue>::ParseNextKey` is the core entry decoder. It advances from `entry_`, decodes shared/non-shared key bytes and value length, rebuilds delta-encoded keys, updates restart index state, and supports separated KV by resolving value slices from the values section.
- `BlockIter<TValue>::BinarySeekRestartPointIndex`, `InterpolationSeekRestartPointIndex`, `GetRestartKey`, and `FindKeyAfterBinarySeek` provide restart-array search plus final linear scan within a restart interval.
- `Block::Block` parses `DataBlockFooter`, initializes restart metadata, strips hash-index suffixes, recognizes separated KV sections, and creates read-amp bitmaps when configured.
- `Block::InitializeDataBlockProtectionInfo`, `InitializeIndexBlockProtectionInfo`, and `InitializeMetaIndexBlockProtectionInfo` precompute per-entry checksums using iterators over the parsed block.
- `Block::NewDataIterator`, `NewIndexIterator`, and `NewMetaIterator` allocate or initialize iterators, validate block size/restart state, and pass checksum, separated-KV, timestamp, prefix-index, and search-mode state into the iterator.

## Control flow

Iterator movement always follows the same high-level contract: subclass `*Impl()` functions position `raw_key_`, `value_`, `entry_`, `current_`, and restart bookkeeping, while the final methods in `BlockIter` call `UpdateKey()` exactly once afterward. `UpdateKey()` then exposes either the raw internal key, raw user key, or a synthesized internal key with `global_seqno_`, and verifies per-KV checksum when enabled.

Forward iteration uses `ParseNextKey`. The function advances `current_` to the end of the previous entry, decodes the entry header, reconstructs the key from shared and non-shared bytes, and sets `value_`. In regular blocks values are inline immediately after key bytes; in separated-KV blocks the first entry in each restart interval encodes a value offset and later entries derive their value slice from the previous value. Corruption is reported if decoding fails, shared-key state is inconsistent, strict bounds checks fail, or separated-KV slices would pass the restart array.

Reverse iteration scans backward to the preceding restart point and then parses forward until the entry before the original position. `DataBlockIter::PrevImpl` adds a cache of parsed previous entries so repeated reverse movement within the same restart interval can avoid reparsing and reassembling delta-encoded keys. Index and meta iterators use the simpler restart-scan approach.

Seek first locates a restart interval and then scans within it. Data and metadata seeks always use binary restart search. Index seeks can use prefix lookup when a `BlockPrefixIndex` is supplied and total-order seek is not requested. Otherwise, index seeks choose binary or interpolation search through `FindRestartPointForSeek`. `kAuto` search resolution happens in `Block::NewIndexIterator`, based on the block uniformity bit and bytewise comparator compatibility.

Point lookup has an additional data-block fast path. `DataBlockIter::SeekForGetImpl` asks `DataBlockHashIndex` for the restart interval for the target user key. Collisions fall back to full seek. Missing entries are treated carefully because the lookup may need to continue in the next data block depending on block-boundary ordering. The optimized path only trusts a limited set of value types; other types fall back to normal seek.

`Block::Block` is the entry point for parsed block construction. It decodes the footer, records `num_restarts_` and `is_uniform_`, validates the data-block index type, initializes `data_block_hash_index_` for binary-and-hash blocks, trims the input view back to the restart array, computes `restart_offset_`, validates separated-KV offsets, and marks malformed blocks by setting the content size to zero. Later iterator construction detects that marker and returns a corruption status, with `GetCorruptionStatus()` re-decoding the footer to preserve a more specific error when possible.

## State and persistence behavior

The code reads persistent block bytes but does not write file data. Persistent layout assumptions include entry delta encoding, restart arrays, data-block footers, optional hash-index payloads, optional separated-KV value sections, and encoded `IndexValue` records. `Block` stores a moved `BlockContents` object and then derives non-owning pointers such as `values_section_` into `contents_.data`.

Iterator state is transient and points into block memory unless key reconstruction, timestamp padding, or global seqno rewriting requires internal buffers. `block_contents_pinned` controls whether returned key/value slices may be treated as pinned by higher layers. The read-amplification bitmap persists for the lifetime of the `Block` and records useful-byte statistics lazily when values are read.

Per-KV protection state is stored in heap memory owned by `Block` as `kv_checksum_`, with `checksum_size_` and `protection_bytes_per_key_` describing the array. The checksum is generated by scanning all entries after block construction and is verified during iterator `UpdateKey()` for the current visible key.

## Dependencies and integration points

This file depends on `DataBlockFooter`, `DataBlockHashIndex`, `BlockPrefixIndex`, `IndexValue`, `BlockHandle` decoding, `InternalKeyComparator`, timestamp helpers, RocksDB statistics/perf context, and block-format coding utilities. It is used by block-based table readers, cache warmers, dictionary-buffer replay in `block_based_table_builder.cc`, meta-block readers, index readers, and tests injecting corruption through sync points.

Important integration contracts include:

- `BlockBuilder` must produce entries whose footer, restart array, hash index, and separated-KV offsets match the parser expectations here.
- `IndexBuilder` and table properties must agree with `have_first_key`, `value_is_full`, `key_includes_seq`, and restart interval settings used when creating index iterators and per-KV checksums.
- Callers using global seqno must only read blocks whose encoded seqnos are zero and whose value types are permitted by the assertions.
- Prefix index seek may return invalid with `NotFound` when the prefix is definitely absent, which upper layers use differently from end-of-block invalidation.

## Risks and edge cases

- Corruption handling relies on carefully preserving the error marker state. Some paths intentionally set `contents_.data.size_ = 0`, after which iterator constructors must avoid dereferencing block internals.
- Per-KV checksum verification is tied to `cur_entry_idx_`. Comments note cases where seeking to the end after scanning might not verify the last parsed key because `UpdateKey()` sees the iterator invalid.
- Interpolation search assumes bytewise comparator semantics and can fall back to binary search after poor guesses. Incorrect use with another comparator would violate ordering assumptions; `NewIndexIterator` guards `kAuto`, but explicit interpolation relies on assertions.
- Separated-KV support changes the meaning of the keys-end offset. Code that accidentally uses `restarts_` instead of `GetKeysEndOffset()` could overrun into values or restart metadata.
- `DataBlockIter::PrevImpl` caches slices and copied key bytes. The distinction between pinned block key data and transient cached buffers is subtle and affects `IsKeyPinned()`.
- Data-block hash lookup is conservative. False positives, collisions, non-point-like value types, and next-block boundary cases all need fallback behavior to preserve correctness.
- Timestamp stripping/padding and global seqno rewriting affect key material used for comparison, exposure, and checksums. The file contains TODOs around timestamp implications for KV protection.

## Test signals

The file has sync points for constructor entry, iterator corruption injection, read-amp randomization, checksum length exposure, and value-pointer observation. Assertions cover restart invariants, separated-KV boundaries, global seqno assumptions, index decoding, and parallel key ordering assumptions. Relevant tests should exercise malformed footers, zero-restart/empty blocks, hash-index collision and no-entry cases, prefix-index absent prefixes, interpolation-vs-binary seek equivalence, reverse iteration with delta-encoded keys, separated-KV blocks, per-KV checksum failures, global seqno files, and timestamp persistence disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block.h -->
# sources/storage-engines/rocksdb/table/block_based/block.h

## Purpose

`block.h` declares the in-memory representation and iterator interfaces for parsed RocksDB block-based table blocks. It covers data blocks, metadata blocks, index blocks, read-amplification tracking, and per-key/value checksum protection. The header establishes the contracts that `block.cc`, block-based table readers, cache code, and table-building replay paths rely on when navigating uncompressed key/value blocks.

## Important APIs, types, and functions

- `BlockReadAmpBitmap` maps byte ranges in a block to a coarser bitmap and records `READ_AMP_TOTAL_READ_BYTES` and `READ_AMP_ESTIMATE_USEFUL_BYTES`. It uses atomic bitmap words so concurrent iterators can mark reads safely.
- `Block` owns or references `BlockContents`, parses block footer/restart metadata, creates `DataBlockIter`, `IndexBlockIter`, and `MetaBlockIter`, exposes content and memory accounting, and initializes per-KV checksum protection.
- `BlockIter<TValue>` is the shared iterator base for block entries. It final-overrides movement APIs so subclasses implement only `Seek*Impl`, `NextImpl`, and `PrevImpl`; the base then runs `UpdateKey()` consistently after every movement.
- `DataBlockIter` iterates internal-key data blocks with `Slice` values. It supports read-amp marking, hash-index point lookup through `SeekForGet`, separated-KV storage, and reverse-iteration caching.
- `MetaBlockIter` iterates metadata blocks with bytewise user keys, no sequence numbers, and no read-amp accounting. It is used for properties and metaindex-like blocks.
- `IndexBlockIter` iterates index entries with `IndexValue` values. It supports user-key or internal-key index keys, full or delta-encoded values, optional first internal key, prefix indexing, binary or interpolation restart search, and global seqno rewriting for decoded first keys.
- `Block::GenerateKVChecksum` is the local helper for encoding a protected key/value checksum into the checksum side array.

## Control flow and contracts

`Block` is constructed from `BlockContents` and later manufactures iterators. Iterator creation takes comparator, global seqno, pinning, timestamp persistence, index-value shape, prefix-index, and search-mode options. The returned iterators are either initialized over the block or invalidated with OK/corruption status for empty or malformed blocks.

`BlockIter` enforces a two-phase movement model. Subclasses do raw positioning and parsing in protected `Impl` functions. The public `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, and `Prev` methods then call `UpdateKey()`, which prepares the key visible through `key()`. This is important because a block might store user keys, internal keys, stripped timestamps, or zero seqnos that need to be presented differently to callers.

The base iterator stores offsets rather than owning entries. `current_` points at the current entry offset, `entry_` spans the current encoded entry, `value_` points at the current value, `raw_key_` stores the parsed block key, and `key_buf_` is used only when exposed key bytes must be synthesized. Restart metadata is used for seek and reverse iteration. `GetKeysEndOffset()` abstracts whether entries end at the restart array or at a separated values section.

Checksum protection is configured by passing `protection_bytes_per_key`, `kv_checksum`, and `block_restart_interval` to `InitializeBase`. Subclasses must keep `cur_entry_idx_` accurate because the base uses it to locate the checksum for the current parsed entry in `UpdateKey()`.

## State and persistence behavior

`Block` state mirrors persistent block layout: `restart_offset_`, `num_restarts_`, `is_uniform_`, `data_block_hash_index_`, and `values_section_` are derived from encoded bytes. `block_restart_interval_` can come from table properties or be computed by scanning. `kv_checksum_` is an in-memory protection side array, not part of the block payload.

`BlockReadAmpBitmap` is transient instrumentation state associated with the block. It stores a randomized byte-to-bit alignment so the read amplification estimate avoids consistent boundary bias, and it can update its statistics pointer if the DB replaces the statistics object while the block remains cached.

Iterator pinning state is explicit. `block_contents_pinned_` says block memory outlives cleanup transfer, while `key_pinned_` says the current exposed key points directly into stable memory. Values are pinned whenever block contents are pinned.

## Dependencies and integration points

The header integrates with `InternalIteratorBase`, `PinnedIteratorsManager`, `Cache::Handle`, `Comparator`, `InternalKeyComparator`, `IndexValue`, `BlockContents`, `BlockPrefixIndex`, `DataBlockHashIndex`, table options, statistics, checksum protection, and timestamp-aware key helpers. It is a central dependency for block-based table reading and for builder-side buffered-block replay when compression dictionaries are trained.

The index iterator contract is coupled to `IndexBuilder` serialization choices: `have_first_key`, `key_includes_seq`, `value_is_full`, and restart interval must match between writing, reading, and checksum construction. Data-block iterator hash lookup is coupled to the `DataBlockHashIndex` built by the block builder. Meta-block iteration assumes bytewise keys and restart interval one for metaindex blocks.

## Risks and edge cases

- `BlockIter` relies on subclasses updating `cur_entry_idx_`, `entry_`, `raw_key_`, `value_`, and `restart_index_` consistently. A movement bug can surface as wrong checksum lookup, bad pinning state, or invalid seek results.
- The base destructor and `Invalidate` assert that pinned iterators are not destroyed while pinning is enabled. Mismanaged cleanup transfer can cause debug failures or dangling slices.
- `BlockReadAmpBitmap::Mark` only records useful bytes when the first bit in a range was previously clear, so very coarse `bytes_per_bit` or unusual access patterns can undercount repeated range utility.
- `IndexBlockIter` has multiple optional encodings active at once: delta-encoded values, first keys, global seqno rewriting, timestamp padding, and separated-KV. Reader and writer options must remain synchronized.
- The raw comparator passed into iterators must be the unwrapped user comparator. Passing a wrapped comparator would break internal/user-key comparison assumptions.
- Metadata blocks intentionally avoid strict assertions on malformed content in some contexts, while data and index blocks are more strict. Tests need to account for those different tolerance levels.

## Test signals

Test hooks and debug-only methods include corruption callbacks in movement functions, `TEST_CurrentEntrySize`, `TEST_GetKVChecksum`, `SetPinnedItersMgr`, and read-amp randomization sync points. Useful tests should cover pinning transfer, cache-handle reference behavior, checksum initialization and verification, timestamp persistence toggles, global seqno rewriting, data hash index lookup, prefix-index seeks, interpolation search selection, separated-KV boundaries, and reverse iteration cache behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.cc -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.cc

## Purpose

`block_based_table_builder.cc` implements `BlockBasedTableBuilder`, the writer for RocksDB block-based SST files. It accepts sorted internal keys, builds data blocks, range-deletion blocks, filters, index blocks, properties, optional compression dictionary blocks, the metaindex, and the footer. It also handles compression selection and verification, optional dictionary sampling, block-cache prepopulation, parallel data-block compression/writing, per-file table properties, alignment padding, and checksum trailers.

## Important APIs, types, and functions

- `CreateFilterBlockBuilder` chooses a full or partitioned filter builder based on table options, filter policy, partition settings, timestamp persistence, and index-builder coupling.
- `BlockBasedTableBuilder::Rep` owns nearly all mutable builder state: options, file writer, offset, block builders, filter/index builders, compression objects, table properties, status, cache keys, parallel compression state, dictionary buffers, and tail-size accounting.
- `BlockBasedTableBuilder::BlockBasedTablePropertiesCollector` writes block-based-table-specific properties such as index type, whole-key filtering, prefix filtering, and decoupled partitioned filters.
- `ParallelCompressionRep` is a lock-free-ish ring-buffer state machine for data-block compression and writing. It tracks emit/compress/write cursors, idle threads, abort/end flags, in-flight size estimates, worker threads, semaphores, and debug watchdog state.
- `Add` validates input value size and key ordering, classifies value types, updates table properties, flushes data blocks when the flush policy says so, feeds filters and index builders, and records range tombstones separately.
- `Flush` finalizes the current data block, optionally samples compression ratios, notifies table property collectors, buffers blocks for dictionary training or emits them for compression and writing, and finalizes filter-block state per data block.
- `MaybeEnterUnbuffered` transitions from dictionary-sampling buffered mode to normal writing by choosing samples, creating a data-block compressor, configuring dictionary-aware verification, replaying buffered blocks into filter/index builders, and emitting all buffered data blocks.
- `EmitBlock` and `EmitBlockForParallel` hand finalized data blocks to the single-threaded or parallel compression/write path and coordinate index-entry preparation/finalization.
- `CompressAndVerifyBlock`, `WriteBlock`, `WriteMaybeCompressedBlock`, and `WriteMaybeCompressedBlockImpl` compress blocks when allowed, verify compression if configured, append block payloads and trailers, update offsets/properties, optionally pad for alignment, and optionally warm the block cache.
- `WriteFilterBlock`, `WriteIndexBlock`, `WriteCompressionDictBlock`, `WriteRangeDelBlock`, `WritePropertiesBlock`, and `WriteFooter` write the tail of the SST.
- `Finish` drives final flush, buffered-to-unbuffered transition, parallel worker shutdown, tail block writing, metaindex/footer writing, final state closure, and status return.

## Control flow

Construction sanitizes table options, creates `Rep`, sets up the base cache key, starts parallel compression if eligible, and allocates a reusable compressed output buffer for the single-threaded path. `Rep` construction is the main configuration phase: it creates compressors/decompressors, decides whether dictionary sampling requires `kBuffered` state, configures compression sampling, reserves cache budget for dictionary buffers, creates the proper index builder, optionally wraps it with a user-defined index builder, creates the filter builder, installs table property collectors, initializes properties, and validates incompatible options such as block alignment with compression.

`Add` is the hot ingestion path. For regular value types, it checks ordering in debug builds, asks `flush_block_policy` whether the existing data block should be flushed before adding the new key, adds the previous-key-aware filter entry in unbuffered mode, appends the key/value to `data_block`, updates `last_ikey`, notifies the index builder only when unbuffered, and notifies table property collectors. Range deletions go to `range_del_block`, with timestamp stripping applied to the tombstone end key when user timestamps are not persisted.

`Flush` finalizes a data block by calling `data_block.Finish()`. It performs optional compression sampling in the emit thread because table property collectors are not thread-safe and need serialized block accounting. In buffered mode, it swaps the block bytes into `data_block_buffers`, updates buffered byte counts, and calls `MaybeEnterUnbuffered`. In unbuffered mode, it increments `num_data_blocks`, finalizes filter state for the block, and either emits the block into the parallel ring buffer or writes it directly.

Parallel compression splits work into emit, compress, and write roles. The emit thread owns creation of uncompressed block bytes and prepared index entries. Worker threads can compress blocks and one worker at a time writes the next block in file order. `ParallelCompressionRep::StateTransition` uses packed atomic bit fields to assign work, track ready-to-write slots, put threads idle, wake idle threads, and stop or abort. `BGWorker` loops over assigned states and calls compression/write helpers. On error it stores the IO status and sets abort.

`MaybeEnterUnbuffered` handles dictionary training. It waits until finish, buffer limit, or cache reservation pressure forces the transition. It selects samples across buffered blocks using a prime-step traversal, creates the data-block compressor with those samples, configures dictionary-aware decompression verification, re-reads buffered blocks through `Block`/`DataBlockIter`, replays keys into filters and index builders, determines next-block first keys for index separators, emits each buffered block, then clears buffer memory and releases cache reservation.

`Finish` flushes the final data block with no next key, forces dictionary-buffer replay if still buffered, stops parallel compression after all emitted blocks are written, records the tail start offset, writes filter, index, compression dictionary, range deletion, properties, metaindex, and footer blocks, marks the builder closed, records actual tail size, and returns the first stored status.

## State and persistence behavior

The persistent file is written as a sequence of blocks followed by the footer. Each block append consists of block payload, one-byte compression type, and four-byte checksum. The checksum includes the block contents, compression type byte, and a context modifier derived from the per-file base context checksum and block offset for newer format versions. Data blocks may be padded for super-block or block alignment, and index delta encoding can be skipped for the first block after alignment padding.

Data block bytes are persisted before the tail. Tail order is filter, index, compression dictionary, range deletion, properties, metaindex, and footer. Depending on format version, the index handle is either placed in the footer or recorded in the metaindex. Table properties persist compression details, index/filter details, timestamps, sequence-number bounds, compression sampling estimates, compression rejection/bypass counts, data sizes, tail offsets, and user-collected properties.

Builder state transitions are explicit: `kBuffered` accumulates uncompressed data blocks for dictionary sampling, `kUnbuffered` writes blocks as they are finalized, and `kClosed` is required before destruction. Status is stored as `IOStatus` protected by a mutex for the rare error case and an atomic OK flag for hot paths. Parallel compression adds in-flight block state in `pc_rep` and makes `EstimatedFileSize()` include upper-bound in-flight size.

## Dependencies and integration points

The builder integrates with `BlockBuilder`, `IndexBuilder` and partitioned index builders, `FilterBlockBuilder` implementations, user-defined index wrappers, `PropertyBlockBuilder`, `MetaIndexBuilder`, `FooterBuilder`, `WritableFileWriter`, `CompressionManager`/`Compressor`/`Decompressor`, cache warming helpers, table property collectors, internal key/timestamp helpers, `FlushBlockPolicy`, and RocksDB statistics/logging.

Reader integration depends on persisted properties matching encoding choices: data block restart interval, index block restart interval, separated key/value setting, index value delta encoding, index key user-key status, compression manager name/type set, filter block names, compression dictionary meta block, and checksum context. The buffered dictionary replay path directly uses `Block` and `DataBlockIter`, so reader-side parsing must remain compatible with just-written data blocks.

## Risks and edge cases

- Parallel compression is complex. Correctness depends on ordered writes despite out-of-order compression, correct `NeedsWriter` bits, wakeup accounting, abort propagation, and prepared index entries matching the final block handle.
- Dictionary buffering delays index/filter updates until replay. Any mismatch between `BlockBuilder` output and `Block` replay can corrupt indexes or filters for buffered files.
- `Add` passes approximate file offsets to collectors in parallel mode, which comments acknowledge are not exact.
- User-defined index, partitioned filter coupling, and parallel compression have incompatibilities enforced in the constructor. New option combinations need similar validation.
- Compression verification requires a matching decompressor, especially after dictionary training. Failure to clone a dictionary-aware verifier becomes a builder error.
- Alignment padding mutates file offsets and can force index delta encoding to be skipped. Tests need to verify index handles and separators across padding boundaries.
- Status handling is optimized for the OK case and shared across worker threads. Any new thread path must use `SetIOStatus`/`SetStatus` and abort parallel work on failure.
- Tail size estimation is intentionally conservative and asserted as an overestimate only for a subset of compaction configurations.

## Test signals

The file exposes many sync points for constructor cache-key setup, `Add` skipping, `WriteBlock` compressed-data tampering, compression result-type tampering, checksum tampering, super-block alignment, filter/property block metadata, raw compression dictionary observation, and finish-time parallel IO status injection. High-value tests include sorted-add enforcement, oversized value rejection, range tombstone timestamp stripping, dictionary sampling and replay, cache reservation pressure, all supported index/filter combinations, user-defined index option failures, compression verification failure, block/trailer checksum validation, block alignment and super-block alignment, parallel compression abort and normal shutdown, tail-size estimates, empty-table finish, and cache prepopulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.h -->
# sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.h

## Purpose

`block_based_table_builder.h` declares the `BlockBasedTableBuilder` class, RocksDB's `TableBuilder` implementation for block-based SST files. The header defines the public lifecycle and metric surface used by flush, compaction, and external SST writers, and it declares the private helpers that implement block emission, compression, cache insertion, metadata writing, and parallel compression in the `.cc` file.

## Important APIs, types, and functions

- `BlockBasedTableBuilder(const BlockBasedTableOptions&, const TableBuilderOptions&, WritableFileWriter*)` creates a builder writing to a caller-owned file writer.
- `Add(const Slice& key, const Slice& value)` adds sorted internal keys or range deletion records to the table.
- `Finish()` finalizes all data and metadata blocks and stops using the file. `Abandon()` closes the builder without completing the SST.
- `status()` and `io_status()` expose build and I/O failures. Internally the implementation stores errors in `Rep`.
- `NumEntries`, `IsEmpty`, `PreCompressionSize`, `FileSize`, `EstimatedFileSize`, `EstimatedTailSize`, `GetTailSize`, `NeedCompact`, `GetTableProperties`, `GetFileChecksum`, `GetFileChecksumFuncName`, `SetSeqnoTimeTableProperties`, and `GetWorkerCPUMicros` expose builder progress, properties, and diagnostics.
- Private write helpers include `Flush`, `MaybeEnterUnbuffered`, `EmitBlock`, `EmitBlockForParallel`, `WriteBlock`, `WriteMaybeCompressedBlock`, `WriteMaybeCompressedBlockImpl`, and metadata writers for filter, index, properties, compression dictionary, range deletion, and footer blocks.
- Cache and compression helpers include `SetupCacheKeyPrefix`, `InsertBlockInCache`, `InsertBlockInCacheHelper`, `InsertBlockInCompressedCache`, `CompressAndVerifyBlock`, `MaybeStartParallelCompression`, `StopParallelCompression`, and `BGWorker`.
- Forward declarations for `Rep`, `WorkingAreaPair`, and `ParallelCompressionRep` keep implementation-heavy state out of the header.

## Control flow and contracts

The public contract is a standard builder lifecycle: construct, call `Add` zero or more times with sorted keys, then call either `Finish` or `Abandon` before destruction. `Add` must not be called after closure. The destructor asserts the builder is closed, so callers must explicitly finish or abandon.

Flush control is private but important to the class contract. `Flush(const Slice* first_key_in_next_block)` can force a block boundary and is used internally when the flush policy or finish path requires it. The optional next-block first key lets the index builder choose shortened separators for the current data block.

The header separates single-threaded and parallel block emission. `EmitBlock` compresses/writes the block in the caller thread and immediately adds the index entry. `EmitBlockForParallel` hands uncompressed block bytes to the parallel compression framework while preparing enough index state for later finalization by writer workers.

`WriteBlock` is for compressible data/index blocks, while `WriteMaybeCompressedBlock` writes an already chosen compressed or uncompressed payload and block trailer. `WriteMaybeCompressedBlockImpl` returns `IOStatus` and is usable from worker threads.

## State and persistence behavior

Most state is hidden in `Rep`, but the header reveals the persistent responsibilities: data blocks, filter blocks, index blocks, properties block, compression dictionary block, range-deletion block, metaindex block, and footer. `kBlockBasedTableMagicNumber` is exported for the file footer. `kCompressionSizeLimit` prevents attempting compression on blocks larger than the underlying compression libraries can handle.

The builder reports both actual file offset and estimates. `FileSize()` is the current written size, while `EstimatedFileSize()` may include in-flight data when parallel compression is enabled. `EstimatedTailSize()` and `GetTailSize()` distinguish predicted and final post-data-block tail bytes. `PreCompressionSize()` accumulates uncompressed payload plus trailers/padding for compaction statistics.

## Dependencies and integration points

The class implements `TableBuilder` and is constructed by the block-based table factory. It integrates with `WritableFileWriter`, table and column-family options, compression utilities, `BlockBuilder`, `BlockHandle`, `MetaIndexBuilder`, table properties collectors, block cache, flush block policy, listener/file-creation metadata, and sequence-number-to-time properties.

The public APIs are consumed by flush/compaction jobs, ingestion/external-SST writers, and tests. The private APIs are coupled to the `.cc` implementation's `Rep` layout and to reader expectations for block handles, block trailers, metaindex names, footer format, and table properties.

## Risks and edge cases

- The lifecycle precondition is strict: destroying without `Finish` or `Abandon` is a debug assertion failure.
- `Add` ordering is a caller responsibility except for debug checks. A release build that receives unsorted internal keys could write a malformed table.
- Private helpers assume `rep_->state` is appropriate. For example, compression/write helpers assert unbuffered state, and parallel helpers assert a live `ParallelCompressionRep`.
- `skip_delta_encoding` is a subtle cross-layer signal from block alignment to index entry encoding. Callers must pass it for data blocks and preserve it into index building.
- `GetWorkerCPUMicros` only has meaning when parallel compression workers are used.
- The header declares cache insertion helpers for both parsed and compressed cache paths; implementation choices must remain aligned with cache item helpers and table options.

## Test signals

The header exposes `TEST_InjectIOError` in debug builds, which allows tests to force builder failure. Lifecycle tests should cover finish, abandon, status propagation, empty files, range-deletion-only files, file-size estimates, tail-size estimates, worker CPU accounting, and injected I/O errors. Integration tests should verify that all private metadata writers produce blocks discoverable by block-based table readers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.h -->
