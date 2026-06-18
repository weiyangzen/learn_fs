<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.cc

## Purpose
Implements `BlobFilePartitionManager`, the write-path manager for blob direct write files. It partitions appended blob records across configurable writer slots, tracks blob files across mutable and immutable memtable generations, seals files at flush time, records initial garbage from failed transformed writes, and provides a direct-write read fallback before files become manifest-visible.

## Important APIs, Types, and Functions
The file defines the default `RoundRobinBlobFilePartitionStrategy`, thread-local direct-write compression state, and all manager methods declared in the header. `OpenNewBlobFile` allocates a file number, registers manager ownership, creates a `WritableFileWriter`, writes a `BlobLogHeader`, and initializes partition metadata. `WriteBlob` compresses if needed, chooses a partition, rolls files on column family, compression, or size changes, appends a `BlobLogRecord`, updates offsets and counters, and optionally prepopulates the blob cache. `RotateCurrentGeneration`, `PrepareFlushAdditions`, and `CommitPreparedGenerations` implement the memtable-generation lifecycle. `ResolveBlobDirectWriteIndex` bridges normal `Version::GetBlob` reads and footer-skipping reads of files still owned by direct write.

## Control Flow
Writes compress outside the manager mutex, then enter the selected partition under `mutex_`. If the active file is incompatible or would exceed `blob_file_size_`, it is finalized into `current_generation_sealed_files_`; otherwise the existing writer is reused. On memtable switch, current sealed files and any still-open partition writers move into a FIFO `GenerationBatch`. Flush preparation seals deferred files exactly once, appends their `BlobFileAddition` records and optional `BlobFileGarbage`, and leaves the generation queued until manifest commit calls `CommitPreparedGenerations`.

## State and Persistence Behavior
Persistent state is the physical blob log file plus the manifest edits returned during flush. Open and deferred files remain in `file_to_partition_` so obsolete-file collection knows they are manager-owned. Sealed direct-write files can also be reference-counted in `protected_blob_file_refs_` while live memtables or old SuperVersions may still point at them. Sealing writes a footer, syncs/closes through `BlobLogWriter::AppendFooter`, invokes completion callbacks, and transfers checksum metadata into `BlobFileAddition`. Cache eviction happens when manager-owned mappings are removed or protection drops to zero to avoid keeping footer-less readers after a file is finalized.

## Dependencies and Integration Points
This implementation depends on blob log format/writer/reader/cache components, `Version` blob reads, RocksDB file creation utilities, checksum handoff, event listeners, IO tracing, statistics, compression managers, and DB version metadata. The manager is called from write batching, memtable switch/flush commit paths, blob file cache reads, obsolete-file protection, and direct-write rollback handling.

## Risks and Edge Cases
The generation FIFO must stay exactly aligned with memtable flush ordering; missing or extra generations produce corruption. Failed seal operations remove file mappings and reset partition state, so callers must treat them as hard failures. Compression settings are cached per thread and rebuilt when mutable options change. Direct-write cache prepopulation failures are logged but do not fail the write. `MarkBlobWriteAsGarbage` must be able to find records in active, current sealed, deferred, or pending sealed state; otherwise rollback accounting returns corruption. `ResolveBlobDirectWriteIndex` intentionally propagates manifest-visible failures rather than masking them with fallback reads.

## Test Signals
No tests are in this file, but related coverage is expected through direct-write DB tests and blob reader tests. Observable behaviors include partition selection modulo bounds, file rollover, retry-safe flush preparation, protection reference underflow logging, stale footer-less reader eviction, and corruption retry through uncached reader refresh.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.h

## Purpose
Declares the per-column-family manager for write-path blob direct write. The interface documents how active partition writers, immutable memtable generations, sealed file additions, initial garbage, and direct-write read fallback are coordinated.

## Important APIs, Types, and Functions
The public API includes `WriteBlob`, `SelectWideColumnPartition`, `RotateCurrentGeneration`, `PrepareFlushAdditions`, `CommitPreparedGenerations`, `SyncAllOpenFiles`, file-number protection/query helpers, rollback garbage marking, and static `ResolveBlobDirectWriteIndex`. Internal structs model lifecycle state: `Partition` for active writers, `DeferredFile` for writers moved out at memtable rotation, `SealedFile` for manifest-ready metadata plus initial garbage, and `GenerationBatch` for FIFO immutable memtable batches.

## Control Flow
The header defines a two-phase lifecycle: active partition writes are either sealed during the mutable generation or deferred at memtable switch; flush preparation seals deferred writers and exposes additions; commit removes prepared generations only after MANIFEST edits land. File-number tracking uses a separate RW mutex so obsolete-file and read paths can query ownership without taking the main append-generation mutex.

## State and Persistence Behavior
State includes writer ownership, file size, blob counts, total record bytes, compression and column-family identity, sync requirements, initial garbage counters, current-generation sealed files, queued immutable generations, manager-owned file mappings, and protected sealed-file reference counts. Persistent state is not directly edited by this header, but the exported `BlobFileAddition` and `BlobFileGarbage` vectors are the contract used by flush/version code to publish blob files.

## Dependencies and Integration Points
The declaration ties together blob additions, garbage records, log writer, blob file cache, callbacks, listeners, checksum factories, IO tracer, RocksDB options, wide-column partition strategy, `Version`, and read-prefetch/pinnable-slice APIs. It sits between write batch transformation, memtable/flush scheduling, MANIFEST publication, blob cache lifecycle, and read paths that encounter direct-write blob indexes.

## Risks and Edge Cases
The documented v1 design still serializes blob appends through one manager mutex, so partition fanout does not yet imply fully parallel blob file writes. Callers must respect generation ordering and pair `PrepareFlushAdditions` with `CommitPreparedGenerations`. Protection APIs are reference-count based and can leak obsolete readers if not balanced. Fallback reads must only be used when the file is not manifest-visible.

## Test Signals
Header-level test signals come from consumers: flush generation tests should verify FIFO behavior, rollback tests should verify initial-garbage accounting, read tests should verify footerless direct-write fallback, and cache tests should verify eviction when mappings/protection are removed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_reader.cc

## Purpose
Implements random-access blob file reads for individual and batched blob references. It validates blob file headers/footers, enforces column-family and TTL expectations, optionally verifies record CRCs, handles compressed values, supports direct I/O and prefetch buffers, and exposes a footer-skipping mode for in-flight direct-write files.

## Important APIs, Types, and Functions
`Create` opens the file, reads the header, optionally validates the footer, initializes decompression state, and constructs a `BlobFileReader`. `OpenFile` creates the `RandomAccessFileReader`, obtains file size using open-handle-first fallback logic, and relaxes direct reads when footer validation is skipped. `GetBlob` validates offset and compression, reads either the value or full record depending on checksum verification, verifies record metadata when requested, decompresses if needed, and returns `BlobContents`. `MultiGetBlob` batches sorted read requests into `FSReadRequest` arrays and processes per-request statuses. Helpers include `ReadHeader`, `ReadFooter`, `ReadFromFile`, `VerifyBlob`, and `UncompressBlobIfNeeded`.

## Control Flow
Reader creation follows open, size check, header decode, optional footer decode, decompressor setup. Single reads compute an adjustment from the value offset back to the record header when checksums are enabled, attempt a prefetch-buffer cache read first, fall back to file read, optionally verify key/value sizes and CRC, then produce uncompressed contents. Multi-read validates each request first, only emits reads for valid requests, performs one `MultiRead`, maps results back to original requests, verifies/decompresses successful records, and accumulates bytes for successful reads.

## State and Persistence Behavior
`BlobFileReader` is read-only and owns a `RandomAccessFileReader`, cached compression metadata, optional decompressor, stats/clock pointers, file size, and `has_footer_`. The footer flag changes offset validation so direct-write files without a footer can be read up to current file size. Read calls update blob bytes-read counters, perf counters, and decompression timing but do not mutate persistent state.

## Dependencies and Integration Points
The implementation depends on blob log format, `BlobContents`, file prefetch buffer, `RandomAccessFileReader`, file naming, file-size helper utilities, compression managers, table multiget constants, sync points for tests, statistics, and RocksDB read options. It is used by `BlobFileCache`, `BlobSource`, version-backed blob reads, and direct-write fallback reads.

## Risks and Edge Cases
Offset validation must account for footer presence, record-header adjustment, user-key length, and overflow-safe end checks. `skip_footer_validation` disables direct reads because direct I/O cannot safely handle the changing tail of an open direct-write file. MultiGet bookkeeping is delicate because validation failures mean the adjustments vector is shorter than the original request array. Corruption during cached-reader reads may be caused by stale footer-less readers, so higher layers refresh readers on corruption. Unsupported compression types produce decompressor failures during creation or decode.

## Test Signals
`blob_file_reader_test.cc` covers normal reads, checksum and no-checksum modes, multiget, stale path-level file sizes, unsupported open-handle size fallback, propagated size errors, malformed/truncated files, TTL rejection, column-family mismatch, CRC and decode corruption injection, Snappy compression and decompression errors, injected I/O errors, and the multiget validation-index regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_reader.h

## Purpose
Declares `BlobFileReader`, the random-access reader for RocksDB blob log files. It exposes single-blob and batched blob retrieval while hiding file open, format validation, direct I/O, decompression, and footerless direct-write handling.

## Important APIs, Types, and Functions
The overloaded static `Create` factory has a normal path and a `skip_footer_validation` path for in-flight direct-write blob files. `GetBlob` reads one blob by user key, value offset, stored size, and compression type. `MultiGetBlob` accepts sorted `BlobReadRequest` entries and fills per-request status/content pairs. `GetCompressionType` and `GetFileSize` expose file metadata for callers. Private helpers perform open, header/footer reads, raw reads, blob verification, and decompression.

## Control Flow
Callers construct readers through `Create`, then issue reads against BlobIndex-derived offsets. The read path can validate only byte ranges or the full record depending on `ReadOptions::verify_checksums`. Batched callers must sort offsets ascending before calling `MultiGetBlob`, enabling efficient filesystem multi-read.

## State and Persistence Behavior
Reader state is immutable after construction: owned file reader, file size, compression type, decompressor, clock/statistics pointers, and whether the footer was present when opened. It does not persist changes; it only reports counters and returns allocated `BlobContents`.

## Dependencies and Integration Points
The header exposes dependencies on `BlobReadRequest`, `RandomAccessFileReader`, advanced compression, file prefetching, memory allocators, RocksDB read/file/immutable options, and statistics. It is consumed by blob cache/source code, version blob reads, direct-write fallback, compaction blob reads, and tests.

## Risks and Edge Cases
The footer-skipping factory is intentionally special-purpose; using it on ordinary manifest-visible files would reduce corruption detection. `MultiGetBlob` requires sorted offsets and a batch size bounded by `MultiGetContext::MAX_BATCH_SIZE`. Callers must pass the same compression type and logical user key used when the blob record was written, especially when checksums are verified.

## Test Signals
The associated test file validates factory behavior, direct/read paths, corruption handling, compression, I/O propagation, and multiget edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_reader_test.cc

## Purpose
Tests `BlobFileReader` behavior across normal reads, multiget reads, format validation, compression, corruption, I/O failures, and file-size discovery. It provides regression coverage for low-level blob file reader contracts used by `BlobSource`, blob cache, and direct-write fallback.

## Important APIs, Types, and Functions
The test helper `WriteBlobFile` writes complete blob files with configurable column family, TTL flags, expiration ranges, compression, keys, values, offsets, and sizes. Filesystem wrappers simulate stale path sizes, open-handle `GetFileSize` failures, unsupported open-handle sizes, and fallback path-size failures. Test fixtures use `MockEnv`, `CompositeEnvWrapper`, `FaultInjectionTestEnv`, and sync points to inject read, decode, CRC, and decompression failures.

## Control Flow
Most tests create an isolated mock DB path, write a blob file through `BlobLogWriter`, create a `BlobFileReader`, then issue `GetBlob` and/or `MultiGetBlob` calls with chosen `ReadOptions`. Parameterized tests activate sync points at open, header read, footer read, blob read, or decode locations to verify errors surface at the right stage. Compression tests conditionally run when Snappy is available.

## State and Persistence Behavior
The test files are persisted in mock/fault-injection environments only. State under test includes encoded blob offsets/sizes, reader file-size selection, per-request status arrays, bytes-read counters returned by reads, and whether result buffers remain null on failure.

## Dependencies and Integration Points
The tests integrate blob log writer/format, reader, filename utilities, file options, writable-file writers, compression utilities, sync points, test harness, mock env, composite env, and fault-injection env. They indirectly validate agreements between writer offsets and reader offset validation.

## Risks and Edge Cases
The suite deliberately exercises offsets too close to file start/end, wrong compression, shorter or incorrect keys, incorrect value sizes, malformed files without footers, TTL or expiration ranges where non-TTL blob files are expected, wrong column family IDs, CRC mismatch, decompression corruption, I/O failures, and multiget requests where some entries fail validation before filesystem reads.

## Test Signals
Key named tests include `CreateReaderAndGetBlob`, file-size fallback/propagation tests, `Malformed`, `TTL`, `ExpirationRangeInHeader`, `ExpirationRangeInFooter`, `IncorrectColumnFamily`, `BlobCRCError`, `Compression`, `UncompressionError`, parameterized I/O and decoding error tests, and `MultiGetBlobWithFailedValidation`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.cc

## Purpose
Implements compaction-time measurement of additional blob-file garbage. It parses blob references from compaction input and output key/value pairs, aggregates per-file inflow/outflow, and lets callers derive how many blob records/bytes became unreachable.

## Important APIs, Types, and Functions
`ProcessInFlow` and `ProcessOutFlow` delegate to `ProcessFlow`. `ParseBlobIndexReference` parses ordinary `kTypeBlobIndex` values. `ProcessEntityBlobReferences` scans `kTypeWideColumnEntity` values for embedded blob indexes through `WideColumnSerialization::ForEachBlobFileNumber`. `GetBlobReferenceDetails` rejects TTL/inlined indexes and computes physical blob record bytes as value size plus record-header/key adjustment. `AddFlow` updates inflow for input references and outflow only for blob files already seen in inflow.

## Control Flow
For every compaction input/output entry, the meter parses the internal key. Plain values return without state changes. Blob index entries decode a `BlobIndex`; wide-column entities iterate each encoded blob reference. Valid references are added to a per-file `BlobInOutFlow`. Output-only references for new blob files are ignored because they do not represent newly generated garbage in preexisting files.

## State and Persistence Behavior
All state is in-memory in `flows_`, a map from blob file number to counters. No persistent metadata is written. The byte accounting intentionally measures full blob-log record contribution, not just stored value length, by including `BlobLogRecord::CalculateAdjustmentForRecordHeader`.

## Dependencies and Integration Points
The implementation depends on `BlobIndex`, blob log format, RocksDB internal key parsing, value types, and wide-column serialization. It feeds compaction/version-edit logic that updates blob garbage metadata after compaction rewrites or drops references.

## Risks and Edge Cases
Malformed internal keys or blob indexes return errors and should fail the compaction accounting path. TTL and inlined blob indexes are treated as corruption in this non-TTL blob-file meter. Outflow without prior inflow is ignored by design, so caller ordering must process all relevant input references as inflow before output-only new files are considered. Wide-column entities can contain multiple blob references per user key and must all be counted.

## Test Signals
`blob_garbage_meter_test.cc` verifies ordinary blob index inflow/outflow deltas, plain values ignored, corrupt keys/indexes rejected, inlined TTL indexes rejected, and wide-column entity references counted independently.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.h -->
# sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.h

## Purpose
Declares `BlobGarbageMeter`, a small compaction helper that tracks per-blob-file inflow and outflow of blob references to compute newly generated garbage.

## Important APIs, Types, and Functions
`BlobStats` counts records and bytes. `BlobInOutFlow` stores inflow/outflow stats, validates that outflow does not exceed inflow, and exposes `HasGarbage`, `GetGarbageCount`, and `GetGarbageBytes`. The public methods `ProcessInFlow`, `ProcessOutFlow`, and `flows` are the caller-facing API. Private helpers parse blob index references, process wide-column entities, and add flow entries.

## Control Flow
Callers feed compaction input references to `ProcessInFlow` and output references to `ProcessOutFlow`. After processing, each `BlobInOutFlow` where inflow exceeds outflow represents blob-file garbage introduced by the compaction.

## State and Persistence Behavior
The class owns only an in-memory `std::unordered_map<uint64_t, BlobInOutFlow>`. It performs no persistence and makes no manifest edits itself; callers translate resulting counters into blob garbage metadata.

## Dependencies and Integration Points
The header depends on blob constants, RocksDB status, parsed internal keys, slices, and `BlobIndex`. It is intended for compaction code that sees internal keys and encoded values.

## Risks and Edge Cases
Debug assertions enforce monotonic consistency but release builds still rely on caller ordering and valid compaction streams. The API distinguishes additional garbage from all garbage; newly written output-only blob files are intentionally not tracked unless they also appear in inflow.

## Test Signals
The companion test file checks counter math, valid/invalid input parsing, ignored plain values, TTL rejection, and wide-column entity support.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_garbage_meter_test.cc

## Purpose
Tests `BlobGarbageMeter` accounting for ordinary blob indexes, non-blob values, malformed input, TTL/inlined indexes, and wide-column entities with multiple blob references.

## Important APIs, Types, and Functions
`MakeBlobIndex` encodes and decodes a test blob reference. `MeasureGarbage` constructs descriptors with expected physical byte sizes, feeds inflow/outflow combinations, and checks per-file counters. Other tests exercise `ProcessInFlow`, `ProcessOutFlow`, and the public `flows` map under specific value types.

## Control Flow
The main test builds internal keys of type `kTypeBlobIndex`, encodes `BlobIndex` values, conditionally processes them as inflow and outflow, then validates two tracked files: one with no additional garbage and one with missing outflow. Wide-column testing serializes V2 columns with blob references, then verifies that a removed column blob becomes garbage while the retained default blob does not.

## State and Persistence Behavior
The suite uses in-memory strings and `BlobGarbageMeter` state only. It validates byte accounting based on blob value size plus record-header/key adjustment rather than external file state.

## Dependencies and Integration Points
The tests depend on `BlobIndex`, blob log format, RocksDB internal keys, wide-column serialization, and the test harness. They model compaction input/output streams without invoking the full compaction subsystem.

## Risks and Edge Cases
The corrupt-key and corrupt-index tests ensure parse failures are not silently ignored. `InlinedTTLBlobIndex` documents the meter's non-TTL assumption. `WideColumnEntity` verifies that multiple blob indexes in one value are independently counted, a path easy to miss if only `kTypeBlobIndex` is tested.

## Test Signals
Coverage signals are direct assertions on `BlobStats`, `BlobInOutFlow::IsValid`, `HasGarbage`, `GetGarbageCount`, and `GetGarbageBytes`, plus `ASSERT_NOK` for invalid inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_index.h -->
# sources/storage-engines/rocksdb/db/blob/blob_index.h

## Purpose
Defines the encoded pointer format stored in the LSM value for blob-backed entries. `BlobIndex` can represent inlined TTL values, external blob references, or external TTL blob references, and provides encode/decode/debug helpers.

## Important APIs, Types, and Functions
`BlobIndex::Type` has `kInlinedTTL`, `kBlob`, `kBlobTTL`, and `kUnknown`. Accessors expose TTL, inlined value, file number, offset, size, and compression after type checks. `DecodeFrom` parses the one-byte type, optional expiration varint, external reference fields, and one-byte compression. `EncodeTo`, `EncodeInlinedTTL`, `EncodeBlob`, and `EncodeBlobTTL` serialize each format. `DebugString` prints either inlined value or external reference metadata.

## Control Flow
Encoding starts with the type byte, then writes varint metadata and either raw inlined value bytes or file/offset/size/compression fields. Decoding mirrors this layout and rejects unknown types or malformed varints/field tails. For external references, exactly one byte must remain for compression after the three varints.

## State and Persistence Behavior
`BlobIndex` is a lightweight decoded view over an encoded LSM value. Inlined values are stored as a `Slice` into the decoded input, so the source buffer must outlive the object when `value()` is used. The persistent bytes are the encoded value stored under `kTypeBlobIndex` or inside wide-column entity metadata.

## Dependencies and Integration Points
The class depends on RocksDB compression enums, `Slice`, varint coding helpers, compression string utilities, and status reporting. It is consumed by blob readers, compaction garbage accounting, DB get/iterator code, wide-column serialization, and direct-write index resolution.

## Risks and Edge Cases
Accessors rely on assertions for type correctness, so production callers must branch on `IsInlined` and `HasTTL` before use. `DecodeFrom` asserts non-empty input before reading the type byte; callers should not pass empty slices. Compression is stored as a raw byte and is not validated here against supported compression managers. Slice-backed inlined values can dangle if decoded from a temporary string.

## Test Signals
The files in this subset exercise `EncodeBlob`, `EncodeInlinedTTL`, `DecodeFrom`, and external-reference accessors in blob reader and garbage meter tests. Broader DB tests should cover TTL blob index behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_log_format.cc

## Purpose
Implements encoding, decoding, and CRC verification for the blob log header, footer, and record header formats shared by readers and writers.

## Important APIs, Types, and Functions
`BlobLogHeader::EncodeTo` and `DecodeFrom` serialize/parse magic number, version, column-family ID, flags, compression, and expiration range. `BlobLogFooter::EncodeTo` and `DecodeFrom` serialize/parse magic number, blob count, expiration range, and masked CRC. `BlobLogRecord::EncodeHeaderTo`, `DecodeHeaderFrom`, and `CheckBlobCRC` handle per-record key size, value size, expiration, header CRC, blob CRC, key, and value verification.

## Control Flow
Header decode validates exact size, fixed fields, magic number, version, flags/compression bytes, and expiration fields. Footer decode computes a CRC over all footer bytes except the CRC field, then validates magic and stored CRC. Record header decode computes the header CRC over key/value sizes and expiration before reading stored CRCs. Blob CRC verification separately hashes key and value slices.

## State and Persistence Behavior
These methods define persistent on-disk blob log bytes. Encoding clears and reserves destination strings, writes fixed-width little-endian fields, and stores masked CRCs. Decoding mutates struct fields but does not own key/value payload storage beyond slices assigned by callers.

## Dependencies and Integration Points
The implementation uses RocksDB fixed-width coding helpers and CRC32C utilities. It is the compatibility contract for `BlobLogWriter`, `BlobLogSequentialReader`, `BlobFileReader`, blob compaction logic, direct-write files, and tests.

## Risks and Edge Cases
Any layout change is format-breaking unless versioned. Header flags currently only interpret bit 0 for TTL; other bits are ignored. Compression type is decoded as a raw byte without support validation. Record header CRC and blob CRC protect different byte ranges, so callers must pass valid key/value slices before `CheckBlobCRC`.

## Test Signals
Reader tests tamper with header, footer, and blob record slices to assert corruption paths. Writer/reader round trips in tests also validate encoded sizes and offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.h -->
# sources/storage-engines/rocksdb/db/blob/blob_log_format.h

## Purpose
Declares the stable blob log file format: file header, file footer, record header, magic/version constants, expiration range representation, and offset validation helper.

## Important APIs, Types, and Functions
`BlobLogHeader` is a 30-byte header with version, column family, compression, TTL flag, and coarse expiration range. `BlobLogFooter` is a 32-byte footer with blob count, exact expiration range, and CRC. `BlobLogRecord` has a 32-byte fixed header plus key and value payloads. `BlobLogRecord::CalculateAdjustmentForRecordHeader` converts a BlobIndex value offset back to the record-header start. `IsValidBlobOffset` checks whether a value offset and size fit inside a blob file, optionally reserving footer bytes.

## Control Flow
Readers and writers use the declared sizes to read/write exact fixed sections. Blob indexes point to the value payload, so checksum-verifying readers subtract the key-size-plus-header adjustment before reading full records. Offset validation checks minimum prefix, key-size relationship, footer reservation, and value end bounds.

## State and Persistence Behavior
This header is the authoritative on-disk contract. Header/footer presence distinguishes fully sealed files from in-flight direct-write files, and `has_footer` in `IsValidBlobOffset` controls which tail bytes are considered available.

## Dependencies and Integration Points
It depends on RocksDB options, slices, status, and compression/type definitions. It is included by writer, sequential reader, file reader, garbage meter, partition manager, and tests.

## Risks and Edge Cases
`IsValidBlobOffset` is central to preventing underflow/overflow on corrupt indexes; changes must preserve unsigned arithmetic safety. Footerless validation is only safe for files known to be open direct-write files. The fixed-width layout favors simple random access but leaves no variable extension fields beyond versioning.

## Test Signals
Reader and writer tests indirectly validate header/footer/record sizes, CRC behavior, offset adjustment, TTL rejection, malformed file detection, and footerless direct-write interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.cc

## Purpose
Implements sequential reading of blob log files through a `RandomAccessFileReader` while maintaining a cursor. It can read file headers, records at different materialization levels, and footers.

## Important APIs, Types, and Functions
The constructor stores the file reader, clock, statistics, and initializes `next_byte_`. `ReadSlice` reads bytes at the current cursor, advances the cursor, records bytes read, and rejects short reads. `ReadHeader` requires the cursor at zero and decodes a `BlobLogHeader`. `ReadRecord` reads a record header, optionally key or key+value payload, returns the value offset, and checks blob CRC when full payload is read. `ReadFooter` reads and decodes the footer.

## Control Flow
`ReadRecord` always reads the 32-byte record header first. For `kReadHeader`, it skips key and value by advancing the cursor. For `kReadHeaderKey`, it materializes the key and skips the value. For `kReadHeaderKeyBlob`, it materializes key and value and validates blob CRC. The optional `blob_offset` is computed after the header as current cursor plus key size.

## State and Persistence Behavior
The reader does not mutate files; its only state is `next_byte_`, temporary buffer slices, and owned buffers attached to `BlobLogRecord`. It records read latency/bytes in statistics and uses raw `IOOptions`.

## Dependencies and Integration Points
It depends on `RandomAccessFileReader`, blob log format, statistics counters, and `StopWatch`. It is a generic blob log scanner for maintenance or recovery-style code, although the implementation notes it appears lightly used.

## Risks and Edge Cases
`ReadSlice` advances `next_byte_` before checking the read status or short read, so callers cannot retry from the same position without resetting. Large key/value sizes come from the record header and are trusted for allocation/skipping after header CRC validation. The TODO notes missing rate limiting. The macro-based header buffer size should remain synchronized with format sizes.

## Test Signals
No dedicated test is in this subset. Indirect format tests cover decode failures; sequential-reader-specific tests should verify cursor advancement, read levels, blob offsets, short-read corruption, and CRC validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.h -->
# sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.h

## Purpose
Declares `BlobLogSequentialReader`, a cursor-based stream reader over blob log files backed by `RandomAccessFileReader`.

## Important APIs, Types, and Functions
`ReadLevel` selects whether `ReadRecord` returns only the header, header plus key, or header plus key plus blob value. Public methods include `ReadHeader`, `ReadRecord`, `ReadFooter`, `ResetNextByte`, and `GetNextByte`. Private `ReadSlice` performs cursor-based file reads into caller-provided buffers.

## Control Flow
Callers read from byte zero through header, zero or more records, and footer. `ResetNextByte` allows repositioning to the beginning; otherwise reads are strictly sequential according to `next_byte_`.

## State and Persistence Behavior
State consists of the owned file reader, clock/statistics pointers, a temporary slice, fixed header buffer, and current byte offset. It is read-only with respect to persistent data.

## Dependencies and Integration Points
The header depends on blob log format and RocksDB slice types, and forward-declares file, env, statistics, status, and clock types. It complements `BlobLogWriter` and can be used by blob file scanning/recovery tools.

## Risks and Edge Cases
The `MAX_HEADER_SIZE` macro is local but non-idiomatic and must track all fixed header/footer sizes. The API assumes records are consumed in order and does not expose arbitrary seek except reset. Payload allocations occur in the implementation based on decoded sizes.

## Test Signals
Coverage should assert all read levels, cursor values, footer decode, short-read handling, and blob offset calculation. No dedicated test file appears in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_log_writer.cc

## Purpose
Implements append-only writing of blob log files: header, records, footer, sync/close, checksum handoff, and statistics.

## Important APIs, Types, and Functions
`Sync` prepares IO options, syncs the underlying `WritableFileWriter` with optional fsync, and records sync stats. `WriteHeader` encodes and appends `BlobLogHeader`, optionally flushes, updates offsets, and records bytes. `AddRecord` overloads construct a record header with or without expiration and delegate to `EmitPhysicalRecord`. `EmitPhysicalRecord` appends header, key, value, flushes if configured, returns key/value offsets, and updates `block_offset_`. `AppendFooter` encodes the footer, appends, syncs, closes, and extracts file checksum method/value.

## Control Flow
Writers must start with `WriteHeader`, then append zero or more records, then call `AppendFooter`. Assertions enforce the element order in debug builds. `do_flush_` flushes after header/record appends for readers that need immediate visibility, while durability is provided by `Sync` during explicit syncs or footer append. `AppendFooter` short-circuits if the writer has seen an error.

## State and Persistence Behavior
Persistent bytes are appended in blob log format order. `block_offset_` tracks the current file offset and is used to compute returned key and blob value offsets. Footer append syncs and closes the file, and optional checksum outputs come from `WritableFileWriter`. Statistics record bytes written and synced-file events.

## Dependencies and Integration Points
The writer depends on blob log format, `WritableFileWriter`, RocksDB write/system-clock/statistics APIs, sync points, coding utilities, and stop-watch timing. It is used by blob file creation in tests, flush/blob-file builder paths, and `BlobFilePartitionManager` direct-write files.

## Risks and Edge Cases
Offset outputs are set after appends regardless of later flush/stat status, so callers must only use them when status is OK. In release builds, misuse of method order is not protected by assertions. `AppendFooter` resets `dest_` after close attempts, making the writer single-use after finalization. Seen-error handling returns an IOError without trying to close, which callers must propagate.

## Test Signals
Blob reader tests use this writer to generate valid and malformed files. Direct-write tests should verify flush-each-record visibility, sync behavior, footer checksum handoff, and returned offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.h -->
# sources/storage-engines/rocksdb/db/blob/blob_log_writer.h

## Purpose
Declares `BlobLogWriter`, the append-only writer abstraction for RocksDB blob log files.

## Important APIs, Types, and Functions
The constructor takes ownership of a `WritableFileWriter`, clock/statistics pointers, blob file number, fsync setting, flush policy, and optional starting offset. Public methods include `ConstructBlobHeader`, `AddRecord` overloads, `EmitPhysicalRecord`, `AppendFooter`, `WriteHeader`, `file`, `get_log_number`, and `Sync`. `last_elem_type_` tracks header/record/footer order for assertions.

## Control Flow
Callers create a writer for an empty file, write the header, add records, then append the footer. Record appends return both key offset and value offset; BlobIndex stores the value offset. Footer append closes the underlying file.

## State and Persistence Behavior
State includes the owned writable file, logical file number, current block/file offset, fsync and flush policies, and last element type. The writer is the persistence boundary for blob log bytes and file-level checksum metadata.

## Dependencies and Integration Points
The header depends on blob log format, slices, statistics, statuses, write options, and `WritableFileWriter`. It is used by blob DB write builders, direct-write partition manager, tests, and any code that creates blob files.

## Risks and Edge Cases
The API exposes `EmitPhysicalRecord`, so callers can bypass expiration-specific helpers if misused. Method-order correctness is assertion-based. The writer owns and may reset `dest_` on footer append, so external users must not retain stale raw file pointers after finalization.

## Test Signals
Round-trip tests through `BlobFileReader` validate writer output. Additional coverage should verify footer append after zero records, seen-error behavior, fsync/flush paths, and checksum output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_read_request.h -->
# sources/storage-engines/rocksdb/db/blob/blob_read_request.h

## Purpose
Defines the request structures shared by `BlobSource::MultiGetBlob` and `BlobFileReader::MultiGetBlob`.

## Important APIs, Types, and Functions
`BlobReadRequest` contains a user-key pointer, blob value offset, stored length, compression type, output `PinnableSlice`, and output `Status`. Its constructor binds these fields to caller-owned objects. `BlobFileReadRequests` groups a blob file number, file size, and an `autovector` of requests for that file.

## Control Flow
Higher-level code groups blob indexes by file, creates `BlobReadRequest` objects, sorts requests by offset before reader calls, and expects each request status/result to be filled independently. Cache hits can complete some requests while misses are passed to `BlobFileReader`.

## State and Persistence Behavior
This header defines transient stack/request state only. It does not own user keys, results, or statuses; those pointers must outlive the multiget call.

## Dependencies and Integration Points
It depends on compression enums, `Slice`, `Status`, `PinnableSlice`, and `autovector`. It is included by blob source and reader components and ties multiget request plumbing to caller-owned status/result storage.

## Risks and Edge Cases
Default construction leaves pointers null, so implementations assert fields before use. Copying is shallow; copied requests still point at the same user key, result, and status. `len` is a `size_t` while offsets and file sizes are `uint64_t`, so callers must avoid truncation when converting from blob metadata.

## Test Signals
Reader and source multiget tests validate status/result mutation, sorted-offset expectations, cache-hit/miss handling, and partial failure semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_read_request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_source.cc

## Purpose
Implements `BlobSource`, the high-level access layer for blob values. It combines blob value cache lookup, blob file reader cache lookup, on-disk reads, optional cache population, cache handle pinning, multiget batching, and stale-reader refresh on corruption.

## Important APIs, Types, and Functions
The constructor configures the shared typed blob cache and optionally wraps it in `ChargedCache` when block-based cache charging is enabled. `GetBlobFromCache`, `PutBlobIntoCache`, `GetEntryFromCache`, and `InsertEntryIntoCache` isolate cache access. `PinCachedBlob` transfers cache handle ownership to a `PinnableSlice`; `PinOwnedBlob` pins heap-owned contents with a cleanup callback. `GetBlob` reads one blob through cache then file. `MultiGetBlob` dispatches per-file groups, while `MultiGetBlobFromOneFile` handles cache hits, file multireads, refresh retries, cache insertion, and result pinning.

## Control Flow
Single reads compute a cache key from db id/session/file/offset, try the blob cache, obey `kBlockCacheTier` by returning incomplete on misses, then use a cached `BlobFileReader`. If file read returns corruption, the cached reader is evicted, an uncached fresh reader is opened, and the read is retried; successful retries refresh the reader cache. Multiget first sorts each file group, services cache hits, marks cache-only misses as incomplete when no I/O is allowed, reads remaining misses from one file, retries only corrupted requests with a fresh reader, optionally installs that reader, then fills or owns result buffers.

## State and Persistence Behavior
`BlobSource` itself is mostly read-only after construction, but it mutates blob cache contents and blob file reader cache state. Cache keys intentionally use DB id, session id, file number, and offset. Bytes-read outputs report on-disk compressed record bytes for consistency even when values come from cache. Persistent blob files are not modified.

## Dependencies and Integration Points
The implementation depends on typed/shared cache interfaces, charged cache, blob contents/cache/file reader/log format, cache reservation support, block-based table options, get/multiget context limits, statistics counters, and RocksDB mutable/immutable options. It is the bridge used by point lookups, multigets, iterators, and version blob reads.

## Risks and Edge Cases
Cache handle pinning transfers ownership, so cleanup lifetimes must be correct. `kBlockCacheTier` only succeeds on cache hits; misses must not open blob files. Corruption retry must preserve original corruption details while appending refresh failures when retry cannot prove the cached reader was stale. Multiget uses a `uint64_t` bit mask, so it relies on the batch size not exceeding mask width and `MultiGetContext::MAX_BATCH_SIZE`. Cache insertion failures are propagated after successful disk reads, meaning a read can fail because cache population failed.

## Test Signals
No companion test appears in this subset, but expected tests include cache hit/miss accounting, no-I/O read tier behavior, fill-cache on/off pinning, stale cached-reader refresh for single and multiget reads, partial multiget corruption retry, charged cache usage, and cache-key session isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.h -->
# sources/storage-engines/rocksdb/db/blob/blob_source.h

## Purpose
Declares `BlobSource`, the unified blob value retrieval interface above blob value cache, blob file reader cache, and storage.

## Important APIs, Types, and Functions
Public methods include `GetBlob`, `MultiGetBlob`, `MultiGetBlobFromOneFile`, `GetBlobFileReader`, `GetBlobCache`, `TEST_BlobInCache`, and typed-cache `Create`. Private helpers manage cache lookup/insert, pinning cached or owned contents into `PinnableSlice`, typed cache access, and cache key construction.

## Control Flow
Callers pass BlobIndex-derived file number, offset, file size, stored value size, and compression type. `BlobSource` first uses blob cache when available, then falls back to file readers if the read tier allows disk I/O. Multiget callers supply requests grouped by blob file; the source sorts within each file and delegates to the single-file path.

## State and Persistence Behavior
The class stores references to DB id/session id strings, statistics, blob file cache, a mutable typed shared blob cache interface, and the lowest cache tier used. It does not own the id strings or file cache. Cache keys are offsetable and session-scoped to avoid reuse across DB sessions.

## Dependencies and Integration Points
The header depends on cache key and typed cache infrastructure, `BlobContents`, `BlobFileCache`, `BlobReadRequest`, RocksDB cache APIs, `CachableEntry`, and `autovector`. It is used by version/read paths and tests that need blob cache visibility.

## Risks and Edge Cases
Lifetime of referenced `db_id`, `db_session_id`, and `blob_file_cache` must exceed the source. `TEST_BlobInCache` is test-only but still performs real cache lookup and can affect stats through `GetBlobFromCache`. The `file_size` parameter is currently not used in cache keys, so offset uniqueness relies on file number/session/offset.

## Test Signals
Expected coverage should validate single and multiget reads through cache and file, cache charge reporting, no-disk read tier, reader refresh on corruption, and result pinning lifetimes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.h -->
