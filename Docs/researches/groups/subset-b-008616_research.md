<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.cc -->
# sources/storage-engines/rocksdb/db/log_reader.cc

## Purpose
Implements RocksDB's physical and logical log reader for WAL and other log-format streams. It reconstructs logical records from fixed-size block fragments, verifies optional CRCs, handles recyclable-log headers, recognizes metadata record types, supports WAL compression, tracks user-defined timestamp sizes, and reports corruption according to recovery mode. It also implements `FragmentBufferedReader`, a retry-friendly reader used when a caller may see partial records at the current end of a growing file.

## Important APIs, Types, And Functions
`Reader::ReadRecord()` is the central logical-record API. It loops over `ReadPhysicalRecord()`, assembles `kFirstType`/`kMiddleType`/`kLastType` fragments into `scratch`, returns `kFullType` payloads directly, and updates `last_record_offset_` and `first_record_read_` only after a complete user record is found. `ReadPhysicalRecord()` parses legacy and recyclable headers, verifies CRCs, filters old recyclable records by `log_number_`, skips mmap zero records, and applies streaming decompression after a `kSetCompressionType` record.

`ReadMore()` fills a block-sized buffer from `SequentialFileReader`; `UnmarkEOF()` and `UnmarkEOFInternal()` realign the file position when tailing a file that has grown since EOF. `MaybeVerifyPredecessorWALInfo()` validates recorded predecessor WAL metadata against observed WAL metadata when `track_and_verify_wals_` is enabled. `UpdateRecordedTimestampSize()` accumulates nonzero timestamp sizes for column families and rejects repeated entries. `FragmentBufferedReader::ReadRecord()`, `TryReadFragment()`, and `TryReadMore()` preserve partial fragments across failed reads so callers can retry after more data arrives.

## Control Flow
The normal reader clears caller scratch, resets stream checksum state, resets the decompressor if active, then repeatedly obtains physical records. Full records return immediately. First/middle/last fragments update the scratch buffer and a streaming XXH3 checksum when requested. Side records are consumed internally: compression records initialize decompression, predecessor records may report WAL holes or mismatches, and timestamp-size records update the per-column-family map. EOF, old recycled records, bad headers, bad lengths, checksum mismatches, and unknown types are translated into either ignored tail conditions, reporter callbacks, or scan continuation depending on `WALRecoveryMode`.

Physical reads operate one block at a time. The parser requires enough bytes for a minimal or recyclable header, validates payload length against the current buffer, checks the embedded log number for recyclable records, optionally validates CRC from header byte 6 through payload, then returns a payload slice or an uncompressed buffer slice. The fragment-buffered reader uses similar parsing but can return "not ready" without declaring corruption when a header/body is incomplete at EOF.

## State And Persistence Behavior
The file does not persist data itself; it interprets bytes from `SequentialFileReader`. It maintains read cursor state (`buffer_`, `end_of_buffer_offset_`, `eof_offset_`), replay-visible state (`last_record_offset_`, `recorded_cf_to_ts_sz_`, compression mode), and recovery safety state (`recycled_`, predecessor WAL verification inputs, read-error and EOF flags). Corruption reports include approximate dropped bytes and sometimes a specific predecessor log number. Old records in recycled logs act like EOF for normal recovery modes, preventing stale bytes from being replayed.

## Dependencies And Integration Points
Depends on `db/log_format.h` record types, `file/sequence_file_reader.h`, `util/coding.h`, `util/crc32c.h`, `util/compression.h`, `util/udt_util.h`, XXH3 hashing, `WALRecoveryMode`, and optional `Logger`. It is paired with `log_writer.cc`; the tests in `log_test.cc` exercise both sides. Higher layers use `LastRecordEnd()`, recorded timestamp sizes, old-log detection, and corruption callbacks during WAL recovery and tailing.

## Risks And Edge Cases
The recovery-mode matrix is subtle: the same truncated tail is ignored for tolerant recovery but reported for absolute consistency and point-in-time recovery. Recyclable logs intentionally turn checksum and stale-log-number issues into EOF-like conditions in some modes. Compression records must be first and unique, while timestamp-size records must never update an existing column family in a file. `UnmarkEOFInternal()` must preserve unread buffered bytes while aligning to the next block. The fragment-buffered reader currently does not support record checksums for logical records, and it has different tail-corruption behavior by design.

## Test Signals
`log_test.cc` covers empty files, normal read/write, fragmentation, trailers, aligned EOF, random reads, read errors, bad record types, safe-ignore types, bad lengths, checksum mismatch, missing fragments, EOF clearing, recycled logs, timestamp-size side records, compression, streaming compression, and retriable partial-header/body reads through `FragmentBufferedReader`. Sync points include `LogReader::ReadMore:AfterReadFile` and `FragmentBufferedLogReader::TryReadMore:FirstEOF`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.h -->
# sources/storage-engines/rocksdb/db/log_reader.h

## Purpose
Declares the general-purpose log stream reader interfaces used to read RocksDB log-format files. The header exposes `log::Reader` for standard blocking scans and `log::FragmentBufferedReader` for tailing/retry scenarios where a physical record may be partially available.

## Important APIs, Types, And Functions
`Reader::Reporter` is the callback interface for corruption and old-log notifications. `Reader` owns a `SequentialFileReader`, an optional reporter, checksum and WAL-verification settings, block buffer storage, compression state, timestamp-size state, and offset accounting. Public APIs include `ReadRecord()`, `GetRecordedTimestampSize()`, `LastRecordOffset()`, `LastRecordEnd()`, `IsEOF()`, `hasReadError()`, `UnmarkEOF()`, `file()`, `GetReporter()`, `GetLogNumber()`, `GetReadOffset()`, and `IsCompressedAndEmptyFile()`.

Protected helpers define the physical-record layer: `ReadPhysicalRecord()`, `ReadMore()`, `UnmarkEOFInternal()`, `ReportCorruption()`, `ReportDrop()`, `ReportOldLogRecord()`, `InitCompression()`, `UpdateRecordedTimestampSize()`, and `MaybeVerifyPredecessorWALInfo()`. The private-like enum extends record types with internal sentinel values such as `kEof`, `kBadRecord`, `kBadHeader`, `kOldRecord`, `kBadRecordLen`, and `kBadRecordChecksum`. `FragmentBufferedReader` overrides `ReadRecord()` and `UnmarkEOF()` and adds retained `fragments_` state plus `TryReadFragment()`/`TryReadMore()`.

## Control Flow
The header establishes the split between logical records and physical records. Callers repeatedly call `ReadRecord()` and receive complete logical payloads while the implementation hides block fragmentation, side records, decompression, and recovery-mode decisions. EOF can be cleared with `UnmarkEOF()` when the caller knows a file has grown. The fragment-buffered subclass keeps partially assembled logical fragments across calls so a later call can finish a record after a writer appends the missing bytes.

## State And Persistence Behavior
`Reader` is non-copyable and requires the underlying file and reporter to remain valid for its lifetime. Its state is in-memory only, but it directly controls persistent recovery semantics by deciding which bytes from a WAL are replayed, dropped, reported, or treated as stale. `recorded_cf_to_ts_sz_` accumulates side-record metadata applying to subsequent WAL records. Compression state is initialized lazily from a leading compression-type record.

## Dependencies And Integration Points
Includes `db/log_format.h`, `file/sequence_file_reader.h`, RocksDB options/status/slice types, compression utilities, hash containers, UDT utilities, and XXH3. It is consumed by WAL recovery, log tests, and any component reading RocksDB's log format. It must remain format-compatible with `log_writer.h`/`log_writer.cc`.

## Risks And Edge Cases
The contract around scratch lifetimes is important: returned slices are valid only until reader mutation or scratch mutation. Reporter lifetime is external. Subclassing is limited but real; changes to protected state or sentinel values can break `FragmentBufferedReader`. WAL verification fields are reader-level state, while recovery mode is per-call, so callers must pass consistent recovery mode when replaying a file.

## Test Signals
The public API is exercised heavily in `log_test.cc`, especially through both `Reader` and `FragmentBufferedReader` parameterizations. Tests validate `IsEOF()`, `UnmarkEOF()`, timestamp-size maps, recyclable-log behavior, and checksum calculation expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_test.cc -->
# sources/storage-engines/rocksdb/db/log_test.cc

## Purpose
Provides the main unit-test suite for RocksDB log reader/writer format behavior. It validates standard and recyclable WAL framing, error handling, EOF retry semantics, user-defined timestamp-size side records, compression metadata, streaming compression round trips, and reader/writer interoperability.

## Important APIs, Types, And Functions
`LogTest` is parameterized by recyclable-log flag, retry-after-EOF flag, and compression type. Its in-memory `StringSource` simulates sequential reads, forced EOF, and forced read errors, while `test::StringSink` captures writer output. Helpers include `Write()`, `Read()`, `IncrementByte()`, `SetByte()`, `ShrinkSize()`, `FixChecksum()`, `ForceError()`, `ForceEOF()`, `UnmarkEOF()`, `MatchError()`, and `CheckRecordAndTimestampSize()`.

`RetriableLogTest` writes real filesystem fragments and uses sync points to coordinate a writer and `FragmentBufferedReader` around partial headers and full headers. `CompressionLogTest` derives from `LogTest` and explicitly writes a compression-type side record before normal records. `StreamingCompressionTest` directly exercises `StreamingCompress`/`StreamingUncompress`.

## Control Flow
The basic tests write records through `log::Writer`, reset the source slice, then read with either `Reader` or `FragmentBufferedReader`. Corruption tests mutate serialized bytes after writing, often fixing CRCs when they want the reader to reach a specific record-type path. Tail tests shrink buffers or force EOF/errors to check tolerant versus absolute recovery behavior. Recycle tests overwrite old in-memory content with a recyclable writer and ensure old records with the wrong log number do not replay. Compression tests initialize writer compression, then validate that the reader sees original uncompressed records.

## State And Persistence Behavior
Most tests use memory-backed file abstractions, but `RetriableLogTest` uses a temporary filesystem path to validate concurrent tailing behavior with `WritableFileWriter::Sync()`. The suite inspects persisted byte counts, block alignment, injected byte corruption, timestamp-size map accumulation, dropped byte accounting, and reported corruption strings. It intentionally simulates stale bytes from recycled logs and partial writes at the end of a file.

## Dependencies And Integration Points
Depends on `db/log_reader.h`, `db/log_writer.h`, `file/sequence_file_reader.h`, `file/writable_file_writer.h`, `test_util/testharness.h`, `test_util/testutil.h`, CRC/coding utilities, random data generation, sync points, filesystem abstractions, and memory allocator utilities. It is the direct regression surface for `log_reader.cc` and `log_writer.cc`.

## Risks And Edge Cases
The tests encode expectations for nuanced behavior: safe-ignorable unknown record types should not report drops; truncated tails may or may not report depending on recovery mode; recyclable logs suppress certain corruption paths by treating stale/corrupt data as EOF; fragment-buffered reads should not flag partial records as corrupt while retry is allowed; and timestamp metadata must be accumulated but not include zero-size entries.

## Test Signals
Named tests include `ReadWrite`, `ReadWriteWithTimestampSize`, `ManyBlocks`, `Fragmentation`, trailer boundary tests, `RandomRead`, all major reader error paths, `ClearEof*`, `Recycle*`, `TimestampSizeRecordPadding`, `TailLog_PartialHeader`, `TailLog_FullHeader`, `NonBlockingReadFullRecord`, compression read/write/fragmentation/checksum tests, and `StreamingCompressionTest.Basic`. Instantiations cover regular and recyclable logs, retry and non-retry readers, no compression, and ZSTD when supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.cc -->
# sources/storage-engines/rocksdb/db/log_writer.cc

## Purpose
Implements RocksDB's append-only log writer for the block-based log format consumed by `log_reader.cc`. It fragments logical records across fixed-size blocks, emits legacy or recyclable physical headers, writes side records for compression, predecessor WAL verification, and user-defined timestamp sizes, optionally compresses WAL payloads, and tracks the largest sequence number written.

## Important APIs, Types, And Functions
`Writer::AddRecord()` is the primary record-writing path. It fragments the input slice, handles block trailer padding, drives optional `StreamingCompress`, chooses full/first/middle/last record types, emits physical records, flushes unless `manual_flush_` is set, and updates `last_seqno_recorded_`. `EmitPhysicalRecord()` formats headers, encodes recyclable log numbers when needed, computes masked CRCs over type/header extension/payload, and appends header and payload to `WritableFileWriter`.

`AddCompressionTypeRecord()` writes the leading compression-type side record and initializes streaming compression buffers. `MaybeAddPredecessorWALInfo()` writes a side record for WAL continuity verification when tracking is enabled. `MaybeAddUserDefinedTimestampSizeRecord()` records new nonzero column-family timestamp sizes and writes a side record before subsequent data. `MaybeSwitchToNewBlock()` pads to the next block when a side record will not fit contiguously. `WriteBuffer()`, `Close()`, `PublishIfClosed()`, `BufferIsEmpty()`, and `MaybeHandleSeenFileWriterError()` manage writer/file state.

## Control Flow
Construction precomputes per-record-type CRC seeds and selects legacy versus recyclable header size. `AddRecord()` first checks for prior file-writer errors, prepares IO options, then loops until all uncompressed or compressed bytes are emitted. If the current block cannot fit a header, it pads the trailer with zeros and resets `block_offset_`. For compressed WALs, compression can produce one or more output chunks; each chunk is further split into physical records as necessary. After successful emission, the writer flushes unless configured for manual flush and records the max provided sequence number.

## State And Persistence Behavior
The writer persists log-format bytes to `WritableFileWriter`. Persistent state includes physical record headers, payloads, CRCs, recyclable log-number fields, compression-type side records, predecessor WAL info records, timestamp-size side records, and zero trailer padding. In-memory state includes current block offset, recorded timestamp-size map, compression stream and buffer, manual-flush mode, log number, recyclable mode, and last sequence number recorded. The destructor attempts a best-effort buffer flush if the destination is still open.

## Dependencies And Integration Points
Depends on `WritableFileWriter`, `db/log_format.h`, `db/dbformat.h`, RocksDB IO/status/slice/write options, compression utilities, UDT utilities, `crc32c`, `coding`, and thread-status helpers. It is used by WAL and manifest/log creation paths and must stay byte-format compatible with `Reader::ReadPhysicalRecord()`.

## Risks And Edge Cases
Block-boundary accounting is critical: the writer must never leave fewer than header-size bytes without padding, and side records must not straddle blocks. Compression initialization must happen after the compression-type record is durably emitted; on failure compression is disabled. Timestamp-size records update in-memory state before writing, so failed side-record writes need careful caller handling. `PublishIfClosed()` assumes `dest_` is non-null; callers using `file()` directly must follow the expected close/publish sequence. Recyclable headers only store low 32 bits of the log number, relying on practical collision improbability plus CRC.

## Test Signals
`log_test.cc` validates round trips, many-block writes, empty records, fragmentation, trailer padding, recyclable overwrite behavior, timestamp-size padding, compression side records and compressed payloads, checksum mismatch handling, and sequence of EOF retry cases. Sync point `LogWriter::EmitPhysicalRecord:BeforeEncodeChecksum` supports corruption-injection testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.h -->
# sources/storage-engines/rocksdb/db/log_writer.h

## Purpose
Declares the append-only `log::Writer` interface and documents the RocksDB log file layout. The header is the format contract for legacy and recyclable physical records, block trailer padding, record fragmentation, and public writer operations.

## Important APIs, Types, And Functions
`Writer` is non-copyable and owns a `std::unique_ptr<WritableFileWriter>`. Its constructor accepts log number, recyclable-log mode, manual-flush mode, compression type, WAL verification mode, and an optional initial block offset for appending to an existing log. Public methods include `AddRecord()`, `AddCompressionTypeRecord()`, `MaybeAddPredecessorWALInfo()`, `MaybeAddUserDefinedTimestampSizeRecord()`, `file()`, `get_log_number()`, `WriteBuffer()`, `Close()`, `PublishIfClosed()`, `BufferIsEmpty()`, `TEST_block_offset()`, and `GetLastSeqnoRecorded()`.

Private members define persistent format state: `block_offset_`, `log_number_`, `recycle_log_files_`, `header_size_`, precomputed `type_crc_`, optional streaming compressor, compressed output buffer, recorded timestamp sizes, WAL-tracking flag, and `last_seqno_recorded_`. Private helpers are `EmitPhysicalRecord()`, `MaybeHandleSeenFileWriterError()`, and `MaybeSwitchToNewBlock()`.

## Control Flow
The header's format comment describes fixed `kBlockSize` blocks containing variable-size physical records plus zero padding when a record cannot fit. Legacy headers contain CRC, payload size, and type. Recyclable headers add a 32-bit log number to distinguish current data from bytes left by a previous use of the same file. Logical records larger than the remaining block capacity are split into first/middle/last fragments.

## State And Persistence Behavior
`Writer` manages append state for one log stream. It can be used in manual flush mode where callers control buffer flushing, or default mode where records/side records are flushed after writing. `GetLastSeqnoRecorded()` provides metadata for WAL predecessor verification. Timestamp-size side-record state is monotonic per column family within a writer.

## Dependencies And Integration Points
Includes `db/dbformat.h`, `db/log_format.h`, RocksDB compression/env/IO/status/slice types, hash containers, and `WritableFileWriter`. It is the producer-side counterpart to `log_reader.h` and is directly tested by `log_test.cc`.

## Risks And Edge Cases
Callers must emit compression metadata before compressed data, use `initial_block_offset` correctly when appending to an existing file, and avoid using a writer after `Close()` or successful `PublishIfClosed()`. Manual flushing changes durability timing. Format changes in this header have broad compatibility impact because old WALs and manifests may need to remain readable.

## Test Signals
The header API is covered through `LogTest`, `CompressionLogTest`, and `RetriableLogTest`. `TEST_block_offset()` is used to validate timestamp-size side-record padding behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.cc -->
# sources/storage-engines/rocksdb/db/logs_with_prep_tracker.cc

## Purpose
Implements tracking of WAL files that contain outstanding two-phase-commit prepare sections. The tracker lets obsolete-file discovery keep the earliest WAL that might still contain an uncommitted or unaborted prepared transaction.

## Important APIs, Types, And Functions
`MarkLogAsContainingPrepSection(log)` records one prepare section in a log, maintaining `logs_with_prep_` as a sorted vector of `{log, cnt}` entries. `MarkLogAsHavingPrepSectionFlushed(log)` records completion of one prepared section in `prepared_section_completed_`, a log-number-to-count map. `FindMinLogContainingOutstandingPrep()` reconciles both structures and returns the smallest log still containing an outstanding prepare, or zero if none remain.

## Control Flow
Prepare paths call `MarkLogAsContainingPrepSection()`, which locks `logs_with_prep_mutex_`, searches from the vector end because new prepares are usually in the latest log, increments an existing count or inserts a new sorted entry. Commit/abort/flush completion calls `MarkLogAsHavingPrepSectionFlushed()`, which only locks the completion map and increments the completed count. The min lookup locks the sorted vector, then for each smallest log locks the completion map briefly. If completions are missing or fewer than prepares, it returns that log. If counts match, it erases both structures and advances.

## State And Persistence Behavior
The state is in-memory and count-based. It does not persist transaction status itself; it protects WAL retention by reporting the earliest WAL that cannot yet be deleted. Returning zero means no known prepared sections require WAL retention. Completed counts are lazily reconciled to reduce contention on prepare insertion paths.

## Dependencies And Integration Points
Depends on `logs_with_prep_tracker.h` and `port/likely.h`. It integrates with transaction prepare/commit/abort flows and obsolete WAL cleanup logic. `MemTable::RefLogContainingPrepSection()` is a related per-memtable signal for the minimum referenced prepare log.

## Risks And Edge Cases
Both mark APIs assert nonzero log numbers. The vector erase-from-front in `FindMinLogContainingOutstandingPrep()` is intentionally not optimized because it is not on the fast path. Correctness depends on matching each prepare mark with exactly one completion mark; mismatched counts can retain WALs indefinitely or permit deletion too early. Lock ordering is vector mutex then completion mutex in the min lookup; other methods lock only one mutex, reducing deadlock risk.

## Test Signals
The header exposes `TEST_PreparedSectionCompletedSize()` and `TEST_LogsWithPrepSize()` for unit tests. Behavior is typically verified through transaction/WAL-retention tests that check obsolete log deletion around prepared transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.h -->
# sources/storage-engines/rocksdb/db/logs_with_prep_tracker.h

## Purpose
Declares `LogsWithPrepTracker`, a small concurrency-aware helper for tracking WAL files with outstanding prepared transaction sections.

## Important APIs, Types, And Functions
Public methods are `MarkLogAsHavingPrepSectionFlushed()`, `MarkLogAsContainingPrepSection()`, `FindMinLogContainingOutstandingPrep()`, and two test-size accessors. The private `LogCnt` struct stores a log number and prepare-section count. The class uses `logs_with_prep_` plus `logs_with_prep_mutex_` for sorted prepare counts and `prepared_section_completed_` plus `prepared_section_completed_mutex_` for completed counts.

## Control Flow
The header establishes a two-lane update design: prepare writers update the sorted vector, while commit/abort completion writers update a separate map. The min lookup reconciles the two. This avoids making every completion contend with prepare insertion in the common path.

## State And Persistence Behavior
All state is in-memory. Its output influences persistence indirectly by determining the oldest WAL that must be retained for transaction recovery. The zero return value from `FindMinLogContainingOutstandingPrep()` means no log is currently protected by this tracker.

## Dependencies And Integration Points
Uses standard mutex, unordered map, vector, assertions, and RocksDB namespace configuration. It is part of DB transaction/WAL lifecycle code and should be considered when changing WAL cleanup or prepared-transaction recovery.

## Risks And Edge Cases
The sorted-vector invariant and count matching are essential. The two mutexes protect different structures, so any future code touching both must preserve the lock order used by the implementation. The test accessors are not locked and should be used only in controlled test contexts.

## Test Signals
Direct tests can inspect container sizes after mark/reconcile operations. Higher-level tests should verify WAL retention under multiple prepares in the same log, prepares spanning logs, and out-of-order completions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/lookup_key.h -->
# sources/storage-engines/rocksdb/db/lookup_key.h

## Purpose
Declares `LookupKey`, the compact lookup-key helper used by `DBImpl::Get()` and memtable/table lookup paths. It packages a user key, optional user-defined timestamp, and snapshot sequence number into the length-prefixed memtable key and internal-key forms expected by RocksDB's internal comparators.

## Important APIs, Types, And Functions
The constructor `LookupKey(const Slice& _user_key, SequenceNumber sequence, const Slice* ts = nullptr)` is declared here and implemented in `dbformat.cc`. Public accessors are `memtable_key()`, `internal_key()`, and `user_key()`. `memtable_key()` returns the full length-prefixed buffer; `internal_key()` skips the varint length and returns `userkey|tag`; `user_key()` strips the final 8-byte internal tag and returns the user-key portion, including user-defined timestamp bytes when enabled.

The object stores three internal pointers (`start_`, `kstart_`, `end_`) and a 200-byte inline buffer. The destructor frees heap storage only when the key did not fit in `space_`. Copying and assignment are disabled.

## Control Flow
Callers construct a `LookupKey` for a user key and sequence/snapshot. The constructor encodes `klength` as varint32, appends user key plus timestamp when applicable, and appends a packed sequence/type tag. Memtable code passes `memtable_key().data()` to memtable reps for efficient seek and uses `internal_key()` for comparator ordering.

## State And Persistence Behavior
`LookupKey` is stack-oriented transient state. It persists nothing, but its exact byte layout is a cross-module contract with memtable entries, internal iterators, and comparators. The inline buffer avoids allocation for short keys; long keys allocate dynamically and are released by the destructor.

## Dependencies And Integration Points
Depends on `rocksdb/slice.h` and `rocksdb/types.h`. It is consumed by `memtable.cc` `Get`, `MultiGet`, `Update`, `UpdateCallback`, and merge-count paths, and by DB get/read flows that need a consistent internal-key representation.

## Risks And Edge Cases
Returned slices point into the `LookupKey` object and become invalid when it is destroyed. The `user_key()` accessor includes timestamp bytes by design, so callers that need timestamp-stripped keys must use timestamp-aware helpers. Layout changes must remain compatible with memtable entry encoding and `InternalKeyComparator`.

## Test Signals
Coverage is indirect through memtable get/update/multiget tests, comparator/internal-key tests, and DB read paths with and without user-defined timestamps. Bugs typically surface as missed memtable hits, incorrect snapshot visibility, or comparator-order violations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/lookup_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.cc -->
# sources/storage-engines/rocksdb/db/malloc_stats.cc

## Purpose
Implements optional allocator statistics dumping for builds linked with jemalloc. It appends jemalloc's `malloc_stats_print()` output into a caller-provided string when jemalloc is available; otherwise it is a no-op.

## Important APIs, Types, And Functions
`DumpMallocStats(std::string* stats)` is the only exported function. Under `ROCKSDB_JEMALLOC`, helper struct `MallocStatus` tracks the current and end pointer of a fixed-size buffer. `GetJemallocStatus()` is the callback passed to `malloc_stats_print()`; it copies each emitted status chunk into the remaining buffer and advances the cursor.

## Control Flow
When compiled with jemalloc support, `DumpMallocStats()` first checks `HasJemalloc()`. If false, it returns without modification. If true, it allocates a 1,000,001-byte buffer, initializes callback cursor bounds, invokes `malloc_stats_print(GetJemallocStatus, &mstat, "")`, then appends the collected C string to `stats`. Without jemalloc support, the function body is empty.

## State And Persistence Behavior
The function only reads allocator process state and appends diagnostic text to memory. It does not persist data or mutate RocksDB state. Output is bounded by the fixed buffer size; callback chunks that do not fit are ignored.

## Dependencies And Integration Points
Depends on `db/malloc_stats.h`, `<cstring>`, `<memory>`, and `port/jemalloc_helper.h`. It is used by diagnostics/statistics code paths that want allocator-level visibility in logs or status reports.

## Risks And Edge Cases
The callback uses `snprintf()` and advances by `status_len`; if jemalloc emits more than the fixed buffer, excess output is silently dropped. The buffer is default-initialized through `new char[]` and appended as a C string after callback writes, relying on allocation/value behavior and callback termination semantics to leave a valid string. Build-time and runtime jemalloc availability can differ, so callers must tolerate empty output.

## Test Signals
Coverage is usually build-configuration dependent. Tests can assert no-op behavior without jemalloc and non-crashing bounded output when `ROCKSDB_JEMALLOC` and `HasJemalloc()` are true.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.h -->
# sources/storage-engines/rocksdb/db/malloc_stats.h

## Purpose
Declares the allocator diagnostic hook `DumpMallocStats()`.

## Important APIs, Types, And Functions
The header exposes `void DumpMallocStats(std::string*)` in the RocksDB namespace. The function appends allocator statistics to the provided string when supported by the build/runtime environment.

## Control Flow
Callers pass a mutable string buffer. The implementation decides at compile time and runtime whether jemalloc stats can be collected.

## State And Persistence Behavior
The API is diagnostic only. It does not own state and does not persist results except by appending to the caller's string.

## Dependencies And Integration Points
Includes `<string>` and RocksDB namespace configuration. It is used by DB diagnostics and logging paths that collect memory allocator state.

## Risks And Edge Cases
Callers must accept that output can be empty. The function takes a raw pointer and assumes it is valid. It should not be used as a correctness signal because availability depends on build flags and allocator linkage.

## Test Signals
Tests are mostly configuration-level: no-op builds should link and run, jemalloc builds should return without crashing and produce bounded diagnostic text when jemalloc is active.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.cc -->
# sources/storage-engines/rocksdb/db/manifest_ops.cc

## Purpose
Implements `GetCurrentManifestPath()`, a small helper that reads a RocksDB `CURRENT` file, validates it, parses the referenced manifest file number, and returns the absolute manifest path under the DB directory.

## Important APIs, Types, And Functions
`GetCurrentManifestPath(const std::string& dbname, FileSystem* fs, bool is_retry, std::string* manifest_path, uint64_t* manifest_file_number)` is the only function. It uses `ReadFileToString()`, `CurrentFileName(dbname)`, and `ParseFileName()` from filename utilities. When `is_retry` is true, it sets `IOOptions::verify_and_reconstruct_read` before reading.

## Control Flow
The function asserts non-null filesystem and output pointers, constructs IO options, reads the `CURRENT` file contents, and returns any read error. It then requires the contents to be non-empty and newline-terminated, strips the newline, parses the filename into a number and type, requires `kDescriptorFile`, and builds `manifest_path` as `dbname + "/" + fname` unless `dbname` already ends with `/`.

## State And Persistence Behavior
It only reads persistent DB metadata. It does not modify `CURRENT` or the manifest. The returned manifest path and file number become inputs to version-set recovery or retry paths. With `is_retry`, the filesystem may perform stronger integrity verification/reconstruction reads.

## Dependencies And Integration Points
Depends on `db/manifest_ops.h` and `file/filename.h`. Integrates with DB open/recovery code that needs to locate the active MANIFEST from `CURRENT`, especially after a perceived corruption where retry reads should be more defensive.

## Risks And Edge Cases
Malformed `CURRENT` files produce corruption statuses if missing the trailing newline, empty, unparsable, or not naming a descriptor file. `dbname.back()` assumes `dbname` is non-empty. The helper does not normalize paths beyond inserting a slash, so callers control DB path canonicalization.

## Test Signals
Relevant tests should cover valid `CURRENT`, missing newline, empty content, non-MANIFEST filename, parse failures, read errors, retry mode setting `verify_and_reconstruct_read`, and DB names with and without trailing slash.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.h -->
# sources/storage-engines/rocksdb/db/manifest_ops.h

## Purpose
Declares the helper for resolving the active MANIFEST path from a DB's `CURRENT` file.

## Important APIs, Types, And Functions
`GetCurrentManifestPath()` takes a DB name, `FileSystem*`, retry flag, output manifest path, and output manifest file number. The comment documents that `is_retry=true` enables stronger `verify_and_reconstruct_read` behavior for perceived corruption cases.

## Control Flow
The header defines a single synchronous read/parse helper contract. Callers use it when they need the descriptor file path before opening or re-reading a manifest.

## State And Persistence Behavior
The API reads persistent metadata through the filesystem and returns parsed results by output pointer. It does not mutate DB files.

## Dependencies And Integration Points
Includes `<cassert>` and `rocksdb/env.h` for `Status` and `FileSystem`. It belongs to manifest/version-set recovery utilities and is implemented in `manifest_ops.cc`.

## Risks And Edge Cases
The raw pointer outputs must be valid. Because this helper reports corruption for malformed `CURRENT`, callers should distinguish read IO errors from metadata corruption. Retry behavior depends on filesystem support for the reconstruct-read option.

## Test Signals
Coverage should validate successful path construction and all corruption cases in `manifest_ops.cc`, plus retry-mode behavior in filesystem mocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manual_compaction_test.cc -->
# sources/storage-engines/rocksdb/db/manual_compaction_test.cc

## Purpose
Tests manual compaction behavior, including an old regression where deleted data could reappear, compaction filter coverage across manual ranges, and skipping levels/ranges with no overlapping files.

## Important APIs, Types, And Functions
`ManualCompactionTest` creates a per-thread DB path and destroys stale state in its constructor. `DestroyAllCompactionFilter` drops entries whose value is `"destroy"`. `LogCompactionFilter` records which level each key was compacted at and exposes `Reset()`, `NumKeys()`, and `KeyLevel()`. Helpers `Key1()` and `Key2()` generate related key ranges, and `kNumKeys` controls reduced-size regression data.

## Control Flow
`CompactTouchesAllKeys` runs once for level compaction and once for universal compaction, writes four keys, compacts through `key4`, and verifies only `key3` survives after the compaction filter removes `"destroy"` values. `Test` writes one key range, writes a second suffixed range, deletes the second range, manually compacts only the first range, then iterates the DB and expects exactly the first range to remain. `SkipLevel` creates three flushed L0 files with keys `1`, `2`, and `[4,8]`, then issues several compact ranges and checks whether the compaction filter saw the expected keys/levels as files move from L0 to L1.

## State And Persistence Behavior
The tests create and destroy real RocksDB instances under a test path. They force no compression and small write buffers/flushes to shape the LSM. Manual compactions rewrite SST state and trigger compaction filters. The final assertions inspect persistent key visibility through iterators and filter-observed level state.

## Dependencies And Integration Points
Uses the public RocksDB `DB` API, `Options`, `CompactRangeOptions`, `FlushOptions`, `WriteBatch`, iterators, compaction filters, and the test harness. It validates DB compaction scheduling/selection behavior rather than the lower-level compaction implementation directly.

## Risks And Edge Cases
The tests rely on deterministic LSM shape from flushes, compression disabled, fixed level options, and manual compaction range boundaries. If compaction picker heuristics or level placement changes, `SkipLevel` expectations may need adjustment. `options.compaction_filter` is a raw pointer manually deleted after DB close, so test lifetime ordering matters.

## Test Signals
The file itself is a test signal. Failures indicate manual compaction skipped needed keys, compacted unnecessary levels, resurrected deleted keys, mishandled compaction filters, or changed level/range overlap semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manual_compaction_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable.cc -->
# sources/storage-engines/rocksdb/db/memtable.cc

## Purpose
Implements RocksDB's mutable and immutable memtable behavior: memory allocation and flush triggers, point/range entry insertion, iteration, range tombstone fragmentation, gets and multigets, merge processing, in-place updates, blob/wide-column handling, per-entry checksum protection, timestamp-aware iteration, and WAL prepare-section tracking.

## Important APIs, Types, And Functions
`ImmutableMemTableOptions` snapshots immutable/mutable column-family options relevant to memtable behavior. `ReadOnlyMemTable::ProtectSealedBlobFiles()` and `ReleaseProtectedSealedBlobFiles()` protect blob files referenced by immutable memtables. `MemTable::MemTable()` constructs arena-backed point and range-deletion memtable reps, bloom filters, cached range-tombstone state, and timestamp metadata. Memory/flush APIs include `ApproximateMemoryUsage()`, `ShouldFlushNow()`, `UpdateFlushState()`, and `UpdateOldestKeyTime()`.

Insertion and validation center on `Add()`, `VerifyEntryChecksum()`, `VerifyEncodedEntry()`, and `UpdateEntryChecksum()`. Read paths include `NewIterator()`, `NewTimestampStrippingIterator()`, `NewRangeTombstoneIterator()`, `NewRangeTombstoneIteratorInternal()`, `ConstructFragmentedRangeTombstones()`, `Get()`, `GetFromTable()`, and `MultiGet()`. Mutation helpers include `Update()`, `UpdateCallback()`, `CountSuccessiveMergeEntries()`, `AddLogicallyRedundantRangeTombstone()`, and `BumpIngestSeqnoBarrier()`. Tail helpers track prepared WAL refs and newest user-defined timestamp.

Internal helper classes/functions include `MemTableIterator`, `TimestampStrippingIterator`, `Saver`, `SaveValue()`, wide-column/blob merge helpers, `EncodeKey()`, and `MemTableRep::Get()`/`MultiGet()`.

## Control Flow
Construction builds the point table from the configured memtable factory and the range-deletion table from a concurrent skip list. `Add()` encodes entries as `varint32 internal_key_len | user_key | packed seq/type | varint32 value_len | value | optional checksum`, inserts into the point or range table, updates counters, bloom filters, sequence bounds, newest timestamp, flush state, and range-tombstone caches. Concurrent insertion defers counter aggregation through `MemTablePostProcessInfo`.

Read paths first account for range tombstones, then use bloom filters when safe, then seek the memtable rep and invoke `SaveValue()` for entries with the target user key. `SaveValue()` enforces callback visibility, verifies checksums, applies covering range tombstones, handles value/blob/wide-column/delete/merge types, and either returns a final value/status or continues gathering merge operands. `MultiGet()` can batch memtable lookups after range tombstone handling and bloom filtering, then marks completed keys and enforces `value_size_soft_limit`.

Iterator paths wrap memtable rep iterators, optionally use prefix bloom/dynamic prefix iterators, validate entries on seek/next when configured, expose write time via `SeqnoToTimeMapping`, and optionally strip timestamps from internal keys/range tombstone values. Range tombstone reads build cached fragmented lists for mutable memtables and precomputed lists for immutable memtables.

## State And Persistence Behavior
Memtables are in-memory, arena-allocated write buffers, but they are the live source for reads before flush and determine what later persists to SSTs. State includes entry/data/delete/range-delete counters, arena memory, approximate memory usage, bloom filters, first/earliest sequence numbers, creation sequence, oldest key time, cached fragmented tombstone lists, immutable flag, ingest sequence barrier, protected blob file references, prepared-WAL minimum reference, and newest UDT pointer. Flush state changes when memory/range-delete thresholds are reached or explicitly marked.

## Dependencies And Integration Points
This file integrates with internal key format, comparators, merge operators, wide-column serialization, blob fetching and blob-file partition protection, range tombstone fragmentation, `MemTableRep` factories, write buffer management, arena allocation, perf counters/statistics, read callbacks, prefix extractors, pinned iterators, sequence-to-time mapping, protection checksums, and transaction/WAL retention. It is a central bridge between DB write batches, read paths, flush, compaction, blob GC safety, and timestamp-aware features.

## Risks And Edge Cases
Correctness depends on byte-format consistency between `Add()`, `SaveValue()`, iterators, and checksum validation. Range tombstone cache invalidation must be thread-safe with readers. Bloom filters are disabled or narrowed in multiget when range tombstones are present to avoid false negative deletion behavior. In-place updates must preserve existing sequence numbers and update checksum state correctly. Wide-column default values may be blob-backed and require a blob fetcher; missing fetchers become corruption/not-supported outcomes. The ingest sequence barrier prevents logically redundant tombstones from invalidating assumptions around externally ingested files. Timestamp stripping must preserve comparator semantics while hiding UDT bytes from downstream consumers.

## Test Signals
Coverage comes from RocksDB DB, memtable, merge, range tombstone, timestamp, blob, write-buffer, corruption/protection, and transaction tests. Sync points include `MemTable::Add:Encoded`, `MemTable::Add:BeforeReturn:Encoded`, `Memtable::SaveValue:Found:entry`, `MemTableIterator::Next:0`, and `MemTable::AddLogicallyRedundantRangeTombstone:AddRange`. Failures typically show as missed reads, incorrect merge results, flush timing regressions, range tombstone visibility bugs, checksum corruption reports, or WAL-retention mistakes for prepared transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable.cc -->
