# Research Group: subset-b-008511

This grouped report covers the LevelDB storage-engine files assigned to `subset-b-008511`. Each section preserves the original source path and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/recovery_test.cc -->
# sources/storage-engines/leveldb/db/recovery_test.cc

Purpose: exercises DB recovery behavior around MANIFEST reuse, large MANIFEST compaction, missing logs, log reuse, multi-log recovery, and missing descriptor files. The fixture opens a temporary DB with `reuse_logs` by default and exposes helpers for direct file inspection and synthetic log creation.

Important APIs and functions: `RecoveryTest::OpenWithStatus`, `Open`, `Close`, `Put`, `Get`, `CompactMemTable`, `ManifestFileName`, `RemoveLogFiles`, `RemoveManifestFile`, `GetFiles`, `MakeLogFile`, and the test cases `ManifestReused`, `LargeManifestCompacted`, `NoLogFiles`, `LogFileReuse`, `MultipleMemTables`, `MultipleLogFiles`, and `ManifestMissing`.

Control flow: the fixture repeatedly closes and reopens `DBImpl`, compares filesystem state before and after recovery, and injects additional log records through `log::Writer` plus `WriteBatchInternal`. `MultipleMemTables` reduces `write_buffer_size` so recovery must flush multiple memtables into tables rather than reusing the old log. `MultipleLogFiles` appends newer numbered logs, checks they are recovered once, and verifies a stale older log is ignored later.

State and persistence behavior: the tests are centered on persistent files named by `filename.h`: `CURRENT`, MANIFEST/descriptor, log files, and table files. They verify that small appendable manifests and empty logs can be reused, oversized manifests are rewritten compactly, missing logs lose unflushed writes, and a missing MANIFEST is reported as corruption or Chromium-specific I/O error.

Dependencies and integration: depends on `DBImpl` test hooks, `VersionSet` naming conventions, `WriteBatchInternal` log record layout, `Env`, `log::Writer`, and test utilities. It is a regression harness for `VersionSet::Recover`, `ReuseManifest`, and DB open logic.

Risks and edge cases: tests branch on append support because not all `Env` implementations can reopen files appendably. Direct log injection must keep sequence numbers coherent. The `Get` helper accepts a snapshot argument but does not pass it into `ReadOptions`, so snapshot behavior is not covered here.

Test signals: strong signals for recovery/open idempotence, manifest size thresholds, log-number monotonicity, and stale-log exclusion. It does not test corrupted records in detail or all `reuse_logs=false` paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/recovery_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/repair.cc -->
# sources/storage-engines/leveldb/db/repair.cc

Purpose: implements `RepairDB`, a best-effort salvage path that reconstructs a descriptor from surviving LevelDB log and table files. It converts logs into tables, scans tables for metadata, archives unusable files, and writes a fresh MANIFEST with all recovered tables placed at level 0.

Important APIs and types: internal `Repairer`, `TableInfo`, `Run`, `FindFiles`, `ConvertLogFilesToTables`, `ConvertLogToTable`, `ExtractMetaData`, `ScanTable`, `RepairTable`, `WriteDescriptor`, `ArchiveFile`, and public `RepairDB`. It uses `FileMetaData`, `VersionEdit`, `TableCache`, `MemTable`, `BuildTable`, `log::Reader`, and `log::Writer`.

Control flow: `Run` lists DB children, records manifests/logs/tables, converts each log to a memtable and then a new table, scans all table numbers to discover smallest/largest internal keys and max sequence numbers, then writes a temporary descriptor. Successful descriptor writing archives old manifests, renames the temp file to `MANIFEST-000001`, and updates `CURRENT`.

State and persistence behavior: repair intentionally discards old compaction layout and adds every recovered table as a level-0 file. It sets log number to 0, next file to one past the largest allocated or generated number, and last sequence to the maximum sequence seen while scanning tables. Logs and obsolete/corrupt tables are moved under `lost/`, preserving evidence while removing them from active metadata.

Dependencies and integration: tightly coupled to DB file naming, internal key parsing, table iteration, batch insertion into memtables, and table building. `SanitizeOptions` may create owned defaults for logging and cache, tracked by `owns_info_log_` and `owns_cache_`.

Risks and edge cases: the log reader is constructed with checksum verification disabled despite a comment claiming checksumming, so corrupt physical log records may be handled according to the reader's non-checksummed semantics. Repaired DBs may lose data or resurrect overwritten state because all table files are reintroduced at level 0 with broad overlap. `RepairTable` only copies entries it can iterate, so partially corrupt tables may be truncated to readable records.

Test signals: this file is indirectly covered by DB repair tests elsewhere and by public `leveldb_repair_db` bindings. The code logs recovered file counts and bytes, but the success status does not guarantee full data preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/repair.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/skiplist.h -->
# sources/storage-engines/leveldb/db/skiplist.h

Purpose: provides LevelDB's arena-allocated concurrent-reader skip list template used by memtables. It supports externally synchronized single-writer insertion and lock-free reads/iteration while nodes remain alive for the whole list lifetime.

Important APIs and types: `SkipList<Key, Comparator>`, nested `Node`, nested `Iterator`, `Insert`, `Contains`, iterator `Seek`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `FindGreaterOrEqual`, `FindLessThan`, `FindLast`, `RandomHeight`, and `NewNode`.

Control flow: insertion finds predecessor nodes at each level, generates a random height with probability 1/4 for each extra level, updates `max_height_` if needed, initializes the new node's links with relaxed stores, then publishes it through predecessor release stores. Reads traverse from current max height down to level 0 using acquire loads.

State and persistence behavior: no disk state. Memory is owned by an `Arena`; nodes are never individually deleted, which is the key safety property for concurrent readers. `max_height_` may be observed stale or ahead by readers, but head links make either observation safe.

Dependencies and integration: depends on `util/arena.h` for lifetime, `util/random.h` for height generation, and comparator functors. It underpins memtable ordering, so comparator correctness and no duplicate insertion are required.

Risks and edge cases: `Insert` asserts duplicates are absent rather than handling them. `Prev` is O(log n) because there are no backward links. The constructor creates the head node with key `0`, so instantiated key types must accept that construction path in practice. Memory ordering is intentionally minimal and fragile if multi-writer insertion is attempted without external locking.

Test signals: `skiplist_test.cc` validates empty behavior, randomized set equivalence, forward/backward iteration, and concurrent single-writer/multiple-reader visibility invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/skiplist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/skiplist_test.cc -->
# sources/storage-engines/leveldb/db/skiplist_test.cc

Purpose: validates the skip list implementation against a standard set model and stresses its lock-free reader assumptions with a single writer and scheduled concurrent readers.

Important APIs and types: local `Comparator`, `ConcurrentTest`, `ConcurrentTest::State`, `WriteStep`, `ReadStep`, `TestState`, `ConcurrentReader`, `RunConcurrent`, and tests `Empty`, `InsertAndLookup`, `ConcurrentWithoutThreads`, `Concurrent1` through `Concurrent5`.

Control flow: `InsertAndLookup` inserts random keys, compares `Contains` against `std::set`, then checks seeking and iteration. `ConcurrentTest` encodes keys as `<key,generation,hash>`; readers snapshot generation counters, iterate with random `Seek`/`Next`, and assert they never miss keys present at iterator creation. `RunConcurrent` schedules a reader on `Env::Default()` while the main thread performs many writes.

State and persistence behavior: in-memory only. Atomic generation counters use release/acquire to establish a test-visible committed generation for each key. `quit_flag_` coordinates thread termination.

Dependencies and integration: depends on `SkipList`, `Arena`, `Random`, `Hash`, `Env::Schedule`, `port::Mutex`, `port::CondVar`, and gtest. It tests the contract needed by memtable reads rather than DB-level behavior.

Risks and edge cases: tests are probabilistic and can miss rare memory-ordering bugs; they assume a single writer. The concurrent suite can be relatively heavy because it performs repeated scheduled reader runs.

Test signals: high-value signal for iterator monotonicity and publication safety under concurrent reads. It also proves the no-duplicate insert assumption through the model-set insertion pattern.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/skiplist_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/snapshot.h -->
# sources/storage-engines/leveldb/db/snapshot.h

Purpose: implements DB snapshot bookkeeping as a circular doubly linked list of immutable sequence-number handles. Snapshots let reads and iterators observe a stable sequence boundary while newer writes continue.

Important APIs and types: `SnapshotImpl`, `SnapshotList`, `SnapshotImpl::sequence_number`, `SnapshotList::empty`, `oldest`, `newest`, `New`, and `Delete`.

Control flow: `SnapshotList` uses a dummy `head_` node. `New` asserts monotonically nondecreasing sequence numbers, allocates a `SnapshotImpl`, and appends it at the tail. `Delete` unlinks the snapshot from its current neighbors and deletes it.

State and persistence behavior: snapshots are in-memory only and are not persisted across DB reopen. The oldest snapshot is used by DB internals to retain obsolete versions/files and sequence-visible memtable entries.

Dependencies and integration: derives from public `leveldb::Snapshot` and uses `SequenceNumber` from `dbformat.h`. `DBImpl::GetSnapshot` and `ReleaseSnapshot` own the synchronization around this list.

Risks and edge cases: `Delete` takes a const pointer to match public API but deallocates it. Debug builds track `list_` to assert release through the correct list; release through the wrong DB is a user error. Callers must hold the DB mutex when mutating the list.

Test signals: snapshot behavior is indirectly tested by DB iterator/read tests and issue regressions such as snapshot-heavy issue 320.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/table_cache.cc -->
# sources/storage-engines/leveldb/db/table_cache.cc

Purpose: implements `TableCache`, LevelDB's cache of opened SSTable `Table` objects and backing `RandomAccessFile`s. It reduces file open and table metadata parsing costs during reads, iteration, compaction, repair, and offset estimation.

Important APIs and functions: `TableAndFile`, `DeleteEntry`, `UnrefEntry`, `TableCache::FindTable`, `NewIterator`, `Get`, and `Evict`.

Control flow: `FindTable` encodes the file number as a fixed64 cache key, looks up an existing table, otherwise opens `<number>.ldb` or fallback `.sst`, calls `Table::Open`, and inserts the table/file pair into an LRU cache. `NewIterator` opens/looks up the table, returns a table iterator, and registers cleanup to release the cache handle when the iterator is destroyed. `Get` performs a direct `Table::InternalGet` and releases the handle immediately.

State and persistence behavior: cache state is memory-only. Entries own open file handles and parsed table metadata; `DeleteEntry` deletes both. Errors are deliberately not cached so a later repair or transient recovery can succeed.

Dependencies and integration: uses `NewLRUCache`, file naming helpers, `Env::NewRandomAccessFile`, `Table::Open`, `Iterator::RegisterCleanup`, and fixed64 coding. It is used by `Version::Get`, iterators over versions, compactions, repair scanning, and approximate offset calculations.

Risks and edge cases: `file_size` must match the actual table size expected by `Table::Open`. Cache keying by file number assumes LevelDB never reuses a number for a different live table without evicting. The fallback `.sst` path supports older filenames but can mask stale alternate files if metadata is wrong.

Test signals: covered indirectly by DB read/compaction tests, repair, and memenv DB tests. No dedicated table-cache unit test appears in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/table_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/table_cache.h -->
# sources/storage-engines/leveldb/db/table_cache.h

Purpose: declares `TableCache`, a thread-safe facade for locating, opening, caching, iterating, and evicting table files by file number and size.

Important APIs and types: constructor `TableCache(dbname, options, entries)`, destructor, `NewIterator`, `Get`, `Evict`, and private `FindTable`.

Control flow: public methods resolve a file number to a cached `Table`; iterators retain cache handles through registered cleanup while direct gets release immediately after probing.

State and persistence behavior: contains `env_`, `dbname_`, a reference to immutable DB `Options`, and an owned `Cache*`. The cache persists only while the DB process is open.

Dependencies and integration: exposes the table lookup layer used by `VersionSet`, `Version`, repair, and compaction code. It depends on `Cache`, `Table`, `ReadOptions`, `Slice`, and internal key format definitions.

Risks and edge cases: because `options_` is stored by reference, the original `Options` object must outlive the cache through DB lifetime. Cache entry count controls open-file pressure.

Test signals: API contract is exercised through higher-level DB reads and version-set iterators.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/table_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_edit.cc -->
# sources/storage-engines/leveldb/db/version_edit.cc

Purpose: serializes and parses `VersionEdit` records, the persistent mutation format for MANIFEST descriptors. Each record updates metadata such as comparator name, log numbers, next file number, last sequence, compaction pointers, deleted files, and added table files.

Important APIs and functions: enum `Tag`, `VersionEdit::Clear`, `EncodeTo`, `DecodeFrom`, `DebugString`, helper `GetInternalKey`, and helper `GetLevel`.

Control flow: `EncodeTo` emits only fields with `has_*` flags plus repeated compact pointer, deleted file, and new file entries. `DecodeFrom` clears the object, loops over varint tags, reads typed payloads, validates levels and internal keys, and returns `Status::Corruption` on unknown or malformed fields.

State and persistence behavior: tag numbers are on-disk format and must not change. Added file metadata records include level, number, file size, smallest internal key, and largest internal key. Deleted files are stored in an ordered set, giving deterministic re-encoding.

Dependencies and integration: uses `util/coding` varint and length-prefixed encodings, `InternalKey::Encode/DecodeFrom`, `config::kNumLevels`, and `VersionSet::Builder` application logic.

Risks and edge cases: unknown future tags are fatal rather than skipped, so format evolution requires compatibility care. Decode does not validate non-overlap or file-number monotonicity; those are enforced later by `VersionSet`. Partial records leave the edit cleared or partially filled but return corruption.

Test signals: `version_edit_test.cc` round-trips large values, repeated file additions/removals, and compact pointers, giving deterministic encode/decode coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_edit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_edit.h -->
# sources/storage-engines/leveldb/db/version_edit.h

Purpose: defines `FileMetaData` and `VersionEdit`, the in-memory representation of table-file metadata and descriptor-log mutations.

Important APIs and types: `FileMetaData` fields `refs`, `allowed_seeks`, `number`, `file_size`, `smallest`, `largest`; `VersionEdit::SetComparatorName`, `SetLogNumber`, `SetPrevLogNumber`, `SetNextFile`, `SetLastSequence`, `SetCompactPointer`, `AddFile`, `RemoveFile`, `EncodeTo`, `DecodeFrom`, and `DebugString`.

Control flow: users build an edit by setting optional metadata and adding/removing file operations; `VersionSet::LogAndApply` fills missing log/sequence fields, applies it to a builder, persists it, and installs a new `Version`.

State and persistence behavior: `FileMetaData` is reference-counted by live `Version`s and records seek budget for seek-triggered compaction. `VersionEdit` contains flags for optional scalar fields, vectors for compact pointers and new files, and a set for deleted files.

Dependencies and integration: includes `dbformat.h` for internal keys and sequence types. `VersionSet` is a friend and directly reads private fields during apply/recover.

Risks and edge cases: `AddFile` assumes smallest/largest are accurate and the edit has not already been saved. Incorrect metadata can corrupt lookup and compaction behavior. `RemoveFile` is level-specific.

Test signals: encode/decode unit tests cover field persistence but not semantic validation of file ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_edit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_edit_test.cc -->
# sources/storage-engines/leveldb/db/version_edit_test.cc

Purpose: validates that `VersionEdit` encoding and decoding are stable and deterministic.

Important APIs and functions: `TestEncodeDecode` and test `VersionEditTest.EncodeDecode`.

Control flow: the helper encodes an edit, decodes into a fresh object, re-encodes, and asserts byte equality. The test progressively adds files, removals, compact pointers, and scalar metadata with large 50-bit values.

State and persistence behavior: exercises the MANIFEST record byte format, especially varint64 values and repeated entries.

Dependencies and integration: depends on `InternalKey`, `kTypeValue`, `kTypeDeletion`, and gtest. It directly protects compatibility of `version_edit.cc`.

Risks and edge cases: it does not test malformed input, unknown tags, invalid levels, duplicate delete entries, or comparator mismatch handling.

Test signals: strong round-trip signal for normal descriptor edits and large numeric values.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_edit_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_set.cc -->
# sources/storage-engines/leveldb/db/version_set.cc

Purpose: implements LevelDB's version graph, MANIFEST recovery/application, file lookup, read routing, compaction selection, and compaction input expansion. It is the core metadata manager for the LSM tree.

Important APIs and functions: `FindFile`, `SomeFileOverlapsRange`, `Version::AddIterators`, `Get`, `UpdateStats`, `RecordReadSample`, `GetOverlappingInputs`, `PickLevelForMemTableOutput`, `DebugString`, `VersionSet::LogAndApply`, `Recover`, `ReuseManifest`, `WriteSnapshot`, `Finalize`, `PickCompaction`, `CompactRange`, `SetupOtherInputs`, `MakeInputIterator`, `AddBoundaryInputs`, `FindSmallestBoundaryFile`, `Compaction::IsTrivialMove`, `AddInputDeletions`, `IsBaseLevelForKey`, and `ShouldStopBefore`.

Control flow: reads search level 0 overlapping files newest first, then binary-search one file per nonzero level. Version edits are applied by `Builder`, which merges base files with added/deleted files and asserts non-overlap for levels above 0. `LogAndApply` builds a new version, writes a snapshot if opening a new MANIFEST, appends the edit, syncs, updates `CURRENT` if needed, and installs the version. `Recover` reads `CURRENT`, replays MANIFEST records, validates comparator name, reconstructs a version, and either reuses or requests compaction of the manifest.

State and persistence behavior: persistent state is a sequence of encoded `VersionEdit` records in MANIFEST files plus `CURRENT` pointing at the active manifest. In-memory state includes a circular list of live versions, current file/log/sequence counters, per-level compact pointers, file reference counts, and compaction scores. Compaction edits delete inputs and add outputs elsewhere in DB implementation.

Dependencies and integration: depends on file naming, log reader/writer, table cache, table iterators, merging/two-level iterators, internal key comparator, memtable/table builder APIs, `Env`, and `Options`. `DBImpl` calls this for open, reads, writes, compaction scheduling, live-file cleanup, and approximate sizes.

Risks and edge cases: descriptor writes unlock the DB mutex, so callers must obey the no-concurrent-`LogAndApply` precondition. Boundary-file expansion is critical: omitting it can make older records for the same user key win after compaction. Level-0 overlap expansion can grow inputs by restarting range discovery. Reuse of manifests depends on append support and size threshold. File number reuse and stale cache entries must be coordinated with table-cache eviction.

Test signals: `version_set_test.cc` covers `FindFile`, overlap checks, and boundary input expansion. `recovery_test.cc` covers recover/reuse paths. Many DB tests indirectly cover compaction and lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_set.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_set.h -->
# sources/storage-engines/leveldb/db/version_set.h

Purpose: declares the metadata model for LevelDB versions, version sets, and compactions.

Important APIs and types: free functions `FindFile` and `SomeFileOverlapsRange`; class `Version` with `GetStats`, `AddIterators`, `Get`, `UpdateStats`, `RecordReadSample`, `Ref`, `Unref`, `GetOverlappingInputs`, `OverlapInLevel`, `PickLevelForMemTableOutput`, `NumFiles`, and `DebugString`; class `VersionSet` with `LogAndApply`, `Recover`, file-number/sequence accessors, compaction selectors, live-file enumeration, `ApproximateOffsetOf`, and `LevelSummary`; class `Compaction` with input accessors, `IsTrivialMove`, `AddInputDeletions`, `IsBaseLevelForKey`, `ShouldStopBefore`, and `ReleaseInputs`.

Control flow: callers interact with `VersionSet::current()` and `Version` references to protect metadata while iterators and reads run. Compactions are selected by score or seek pressure and represented as two input vectors from adjacent levels.

State and persistence behavior: `VersionSet` owns database name, options, table cache, internal comparator, MANIFEST writer/file, version list, current version pointer, file/log/sequence counters, and per-level compaction pointers. `Version` owns per-level `FileMetaData*` vectors and compaction score hints.

Dependencies and integration: bridges internal format, table cache, manifest logging, environment files, DB mutexes, and compaction code. The header documents thread-compatibility: external synchronization is required for all accesses.

Risks and edge cases: consumers must maintain reference counts correctly or files/versions can be freed under iterators. `LogAndApply` requires the DB mutex on entry and no concurrent callers. Levels above 0 require non-overlapping sorted files.

Test signals: declarations are exercised by version-set, recovery, DB, and compaction tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_set_test.cc -->
# sources/storage-engines/leveldb/db/version_set_test.cc

Purpose: unit-tests version-set helper algorithms for file search, range overlap, and compaction boundary expansion.

Important APIs and types: `FindFileTest`, `FindFileTest::Add`, `Find`, `Overlaps`, test cases for empty/single/multiple/null-boundary/sequence/overlapping files, `AddBoundaryInputsTest`, `CreateFileMetaData`, and boundary-file tests.

Control flow: file metadata is built manually with internal key ranges and checked against expected binary-search and overlap outcomes. Boundary tests construct same-user-key internal key sequences and assert `AddBoundaryInputs` extends compaction input order correctly.

State and persistence behavior: in-memory test metadata only. It models the ordering invariants required for persistent table metadata without writing a DB.

Dependencies and integration: depends on `InternalKeyComparator`, `BytewiseComparator`, `FileMetaData`, and exported test-visible `AddBoundaryInputs`.

Risks and edge cases: tests cover critical boundary cases but do not run full compaction output generation. Manual `FileMetaData` objects may omit fields irrelevant to the helper under test.

Test signals: high-value regression signal for issue-class bugs where compaction splits records for the same user key across levels.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/version_set_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/write_batch.cc -->
# sources/storage-engines/leveldb/db/write_batch.cc

Purpose: implements LevelDB's atomic write-batch encoding, decoding, appending, and insertion into a memtable.

Important APIs and functions: `WriteBatch::Clear`, `ApproximateSize`, `Iterate`, `Put`, `Delete`, `Append`; `WriteBatchInternal::Count`, `SetCount`, `Sequence`, `SetSequence`, `SetContents`, `Contents`, `ByteSize`, `InsertInto`, and `Append`; internal `MemTableInserter`.

Control flow: a batch starts with a 12-byte header: fixed64 sequence and fixed32 count. `Put` and `Delete` increment count and append a tag plus length-prefixed key/value fields. `Iterate` parses records and dispatches to a handler, verifying parsed record count matches the header. `InsertInto` uses a handler that writes each operation to `MemTable` with incrementing sequence numbers.

State and persistence behavior: the `rep_` byte string is written directly into log records and used for DB write recovery. Sequence number is assigned by DB internals before logging/applying. The same encoding is consumed by repair and recovery code.

Dependencies and integration: depends on `dbformat.h` value tags, `MemTable::Add`, `util/coding`, and public `WriteBatch`. `DBImpl::Write` and log recovery rely on this exact format.

Risks and edge cases: malformed batches produce corruption statuses; `SetContents` asserts at least header size and bypasses validation. Appending ignores source sequence numbers and preserves only operation payloads under the destination sequence. Header count must remain consistent.

Test signals: `write_batch_test.cc` covers empty/multiple/corrupt/appended batches and approximate size growth.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/write_batch.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/write_batch_internal.h -->
# sources/storage-engines/leveldb/db/write_batch_internal.h

Purpose: exposes internal-only helpers for manipulating `WriteBatch` representation fields that are intentionally hidden from the public API.

Important APIs and types: `WriteBatchInternal::Count`, `SetCount`, `Sequence`, `SetSequence`, `Contents`, `ByteSize`, `SetContents`, `InsertInto`, and `Append`.

Control flow: DB internals set sequence/count metadata, obtain raw contents for log writing, restore raw contents from log records, and insert batch contents into a `MemTable`.

State and persistence behavior: this header is the gateway to the persistent batch wire format. `Contents` returns a `Slice` over `rep_`, so the batch must outlive the slice.

Dependencies and integration: friends with public `WriteBatch`, uses `SequenceNumber` and `MemTable`. Recovery, repair, tests, and DB write paths include it.

Risks and edge cases: bypasses encapsulation and can create invalid batches if callers set inconsistent contents/counts. It is not a public compatibility promise beyond LevelDB internals.

Test signals: exercised directly by write-batch and recovery tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/write_batch_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/write_batch_test.cc -->
# sources/storage-engines/leveldb/db/write_batch_test.cc

Purpose: validates write-batch encoding and insertion semantics by materializing batches into a memtable and printing internal keys.

Important APIs and functions: helper `PrintContents`, tests `Empty`, `Multiple`, `Corruption`, `Append`, and `ApproximateSize`.

Control flow: `PrintContents` inserts the batch into a memtable through `WriteBatchInternal::InsertInto`, iterates the memtable, parses internal keys, and emits operation plus sequence text. Tests mutate batches and compare expected output strings.

State and persistence behavior: exercises the same byte representation used in WAL records. Sequence ordering is visible through memtable internal keys.

Dependencies and integration: depends on `MemTable`, `InternalKeyComparator`, `ParseInternalKey`, `WriteBatchInternal`, `Iterator`, and logging helpers.

Risks and edge cases: string-output comparison is concise but tied to memtable sort order. It covers truncated payload corruption, not every malformed tag/varint case.

Test signals: good direct coverage for count, sequence assignment, append semantics, and size accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/write_batch_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/helpers/memenv/memenv.cc -->
# sources/storage-engines/leveldb/helpers/memenv/memenv.cc

Purpose: implements `NewMemEnv`, an in-memory `EnvWrapper` that stores file contents in process memory while delegating non-storage functions to a base environment.

Important APIs and types: internal `FileState`, `SequentialFileImpl`, `RandomAccessFileImpl`, `WritableFileImpl`, `NoOpLogger`, `InMemoryEnv`, and exported `NewMemEnv`.

Control flow: `InMemoryEnv` maps filenames to reference-counted `FileState`s. Writable file creation creates or truncates a `FileState`; appendable creation creates or reuses one; sequential/random file objects hold references and call `FileState::Read`; writes append data into fixed 8 KiB blocks. Rename moves map entries and removes any target first.

State and persistence behavior: all file contents disappear when the env is destroyed. `FileState` reference counting lets open file handles survive map operations. Sync/flush/close are no-ops, and locks are no-op heap tokens.

Dependencies and integration: implements enough `Env` for LevelDB tests and full DB operation, using `EnvWrapper`, `Status`, `port::Mutex`, thread annotations, and `MutexLock`.

Risks and edge cases: no directories are represented; `CreateDir` and `RemoveDir` always succeed. `NewAppendableFile` assigns `file = new FileState()` but does not store it back through `*sptr`, so creating a brand-new appendable file may return a handle to a file not present in `file_map_`; typical tests append to existing files. Locking is not process-exclusive. `GetChildren` returns path suffixes for any matching prefix and may include nested paths.

Test signals: `memenv_test.cc` covers basics, read/write, large writes, rename/delete, DB integration, and no-op locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/helpers/memenv/memenv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/helpers/memenv/memenv.h -->
# sources/storage-engines/leveldb/helpers/memenv/memenv.h

Purpose: declares the helper API for creating an in-memory LevelDB environment.

Important APIs and types: forward declaration `Env` and exported `Env* NewMemEnv(Env* base_env)`.

Control flow: callers pass a live base env; the returned env delegates non-file-storage operations while overriding file APIs.

State and persistence behavior: data is memory-resident and tied to the returned env object's lifetime. The base env must remain live while the wrapper is in use.

Dependencies and integration: uses `LEVELDB_EXPORT` for shared-library visibility. Used by tests and clients that need a temporary DB without filesystem persistence.

Risks and edge cases: callers own the returned pointer and must delete it after all DB/file objects using it are closed.

Test signals: covered by `memenv_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/helpers/memenv/memenv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/helpers/memenv/memenv_test.cc -->
# sources/storage-engines/leveldb/helpers/memenv/memenv_test.cc

Purpose: verifies the in-memory env implementation both as a filesystem abstraction and as a backing env for a real LevelDB instance.

Important APIs and functions: fixture `MemEnvTest`, tests `Basics`, `ReadWrite`, `Locks`, `Misc`, `LargeWrite`, `OverwriteOpenFile`, and `DBTest`.

Control flow: tests create/delete/rename files, read sequentially and randomly, exercise no-op sync/flush/locks, write a large multi-block file, overwrite an open file, and open a DB that writes, reads, iterates, and compacts data.

State and persistence behavior: all operations run inside a fresh `NewMemEnv(Env::Default())`. `DBTest` proves LevelDB metadata, logs, tables, and compaction can operate on the memory-backed env.

Dependencies and integration: uses public `Env`, `DB`, `Options`, test utilities, and `DBImpl::TEST_CompactMemTable`.

Risks and edge cases: tests intentionally accept no-op locking, so they do not validate real process exclusion. The overwrite-open-file expectation reflects memenv's shared `FileState` behavior, not necessarily POSIX file snapshot semantics.

Test signals: strong practical coverage for the memenv helper and its DB integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/helpers/memenv/memenv_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/c.h -->
# sources/storage-engines/leveldb/include/leveldb/c.h

Purpose: declares LevelDB's C ABI wrapper, intended for stable shared-library use and bindings such as JNI.

Important APIs and types: opaque handles for DB, options, read/write options, iterators, snapshots, batches, cache, comparator, filter policy, env, logger, and file abstractions; functions for open/close, put/delete/write/get, iterator movement/access, snapshots, properties, approximate sizes, compaction, destroy/repair, write-batch operations, option setters, comparator/filter construction, cache/env creation, memory free, and version reporting.

Control flow: callers allocate option/handle objects, pass raw pointer-plus-length slices instead of C++ `Slice`, receive heap-allocated results/errors, and destroy/free objects with matching C API functions.

State and persistence behavior: maps directly onto the C++ DB and WAL/table/MANIFEST behavior. Error strings and returned values are malloc-owned by the library and must be released with `leveldb_free`.

Dependencies and integration: uses `LEVELDB_EXPORT` and `extern "C"` to expose ABI symbols. The implementation lives elsewhere but wraps public C++ APIs.

Risks and edge cases: custom C comparators do not expose key-shortening hooks, and the API cannot implement custom DB/env/cache/iterator types. All pointer arguments must be non-null. Error-pointer ownership rules are strict, especially on Windows allocators.

Test signals: C API coverage is not in this subset; behavior is indirectly tied to public DB tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/cache.h -->
# sources/storage-engines/leveldb/include/leveldb/cache.h

Purpose: declares the thread-safe cache interface and built-in LRU cache factory used for blocks, opened tables, and other internal caches.

Important APIs and types: `Cache`, opaque `Cache::Handle`, `NewLRUCache`, `Insert`, `Lookup`, `Release`, `Value`, `Erase`, `NewId`, `Prune`, and `TotalCharge`.

Control flow: clients insert charged values with a deleter, receive handles from insert/lookup, access values through handles, and release handles when done. Erase removes the key but active handles keep the entry alive until release.

State and persistence behavior: cache contents are memory-only. Charges approximate capacity consumption; `NewId` lets different clients partition key spaces.

Dependencies and integration: table cache uses it for table handles; block cache uses it for table blocks. Depends on `Slice` keys and exported symbol visibility.

Risks and edge cases: callers must release every handle exactly once. Deleters must understand the key/value lifetime supplied by the implementation. Default `Prune` is a no-op unless overridden.

Test signals: cache behavior is tested elsewhere; in this subset it is exercised indirectly through `TableCache`.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/comparator.h -->
# sources/storage-engines/leveldb/include/leveldb/comparator.h

Purpose: declares the key ordering interface used by DBs and tables, plus the built-in bytewise comparator.

Important APIs and types: abstract `Comparator`, `Compare`, `Name`, `FindShortestSeparator`, `FindShortSuccessor`, and `BytewiseComparator`.

Control flow: DB and table code compare user keys through this interface and persist the comparator name in MANIFEST records. Table builders may call separator/successor hooks to shorten index keys.

State and persistence behavior: comparator ordering is part of the persistent database contract. Opening a DB with a comparator name/order mismatch can make stored tables unreadable or incorrectly ordered.

Dependencies and integration: used by `Options`, `InternalKeyComparator`, bloom-filter compatibility guidance, table building, version metadata, and recovery comparator checks.

Risks and edge cases: comparator implementations must be thread-safe and must change `Name()` whenever ordering semantics change. Incorrect separator/successor logic can violate sorted table invariants.

Test signals: bytewise and custom comparators are covered elsewhere; version recovery validates persisted comparator name.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/comparator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/db.h -->
# sources/storage-engines/leveldb/include/leveldb/db.h

Purpose: declares the main C++ LevelDB API: a persistent, concurrent ordered map from keys to values.

Important APIs and types: `kMajorVersion`, `kMinorVersion`, `Snapshot`, `Range`, abstract `DB`, static `DB::Open`, `Put`, `Delete`, `Write`, `Get`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `GetProperty`, `GetApproximateSizes`, `CompactRange`, `DestroyDB`, and `RepairDB`.

Control flow: users open a DB with `Options`, perform writes and reads with per-operation options, create iterators/snapshots for stable views, ask for properties/size estimates, compact ranges, and delete/repair databases through free functions.

State and persistence behavior: the API abstracts WAL, MANIFEST, SSTable, snapshots, and compaction. `WriteOptions::sync` controls crash durability. Snapshots are immutable handles and must be released.

Dependencies and integration: includes iterator and options APIs. Implemented by `DBImpl` and connected to `VersionSet`, memtables, table cache, env, and write batches.

Risks and edge cases: iterators should be deleted before DB destruction. `DestroyDB` masks some listing failures for backward compatibility. `RepairDB` may lose data. `CompactRange` is advanced and can create latency spikes.

Test signals: nearly all DB tests exercise this API; issue tests in this subset target compaction, iterator snapshots, and snapshot-heavy write workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/dumpfile.h -->
# sources/storage-engines/leveldb/include/leveldb/dumpfile.h

Purpose: declares `DumpFile`, a diagnostic helper that emits text-formatted contents for a LevelDB storage file.

Important APIs and types: `Status DumpFile(Env* env, const std::string& fname, WritableFile* dst)`.

Control flow: implementation reads the named file through `Env`, identifies the storage-file type, and appends newline-terminated textual items to the supplied writable destination.

State and persistence behavior: read-only against the source file; output is written through caller-provided `WritableFile`.

Dependencies and integration: depends on `Env`, `WritableFile`, and `Status`. Useful for debugging logs/tables/manifests without opening the full DB.

Risks and edge cases: returns non-OK if the file is not a recognized LevelDB storage file or cannot be read. Destination append errors are surfaced through status.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/dumpfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/env.h -->
# sources/storage-engines/leveldb/include/leveldb/env.h

Purpose: declares LevelDB's platform/environment abstraction for filesystem, locking, scheduling, logging, time, and file I/O.

Important APIs and types: `Env`, `SequentialFile`, `RandomAccessFile`, `WritableFile`, `Logger`, `FileLock`, `EnvWrapper`, `Log`, `WriteStringToFile`, and `ReadFileToString`. Key methods include file creation/opening, appendable files, existence/listing, remove/rename, locks, background scheduling, test directory, logger creation, `NowMicros`, and sleep.

Control flow: DB internals call `Env` for all OS-facing behavior. File objects expose sequential read/skip, thread-safe random reads, append/flush/sync/close writes, and logging. `EnvWrapper` forwards all methods to a target env for partial overrides.

State and persistence behavior: `WritableFile::Sync` is the durability boundary used by WAL and MANIFEST writes. Lock files prevent multi-process DB opens. `NewAppendableFile` may return `NotSupported`, which recovery code must handle.

Dependencies and integration: every persistent component uses this API. The Windows `DeleteFile` macro workaround preserves class declaration consistency. `memenv` implements a custom wrapper from this header.

Risks and edge cases: `Slice` results returned by file reads may point at caller scratch. Deprecated `DeleteFile/DeleteDir` and modern `RemoveFile/RemoveDir` coexist for compatibility. Scheduling may run tasks concurrently, so DB background code must synchronize.

Test signals: memenv tests validate a custom implementation; recovery tests branch on appendable support.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/export.h -->
# sources/storage-engines/leveldb/include/leveldb/export.h

Purpose: centralizes symbol visibility annotations for public LevelDB APIs.

Important APIs and macros: `LEVELDB_EXPORT`, conditional `LEVELDB_SHARED_LIBRARY`, `LEVELDB_COMPILE_LIBRARY`, `_WIN32`, `__declspec(dllexport/dllimport)`, and GCC/Clang `visibility("default")`.

Control flow: public headers annotate classes/functions with `LEVELDB_EXPORT`; the macro expands based on build mode and platform.

State and persistence behavior: no runtime or persistent state.

Dependencies and integration: included by public API headers and helper headers such as memenv. It controls ABI export/import behavior for static/shared builds.

Risks and edge cases: incorrect build defines can hide symbols or mark imports as exports. Non-Windows shared-library consumers rely on compiler visibility support.

Test signals: validated mostly by build/link tests rather than runtime tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/filter_policy.h -->
# sources/storage-engines/leveldb/include/leveldb/filter_policy.h

Purpose: declares the filter-policy interface used to build per-table filters, usually bloom filters, to avoid unnecessary disk reads.

Important APIs and types: `FilterPolicy`, `Name`, `CreateFilter`, `KeyMayMatch`, and `NewBloomFilterPolicy`.

Control flow: table building calls `CreateFilter` with sorted user keys and appends the encoded filter to table metadata. Table reads call `KeyMayMatch` before reading data blocks for point lookups.

State and persistence behavior: filter bytes are persisted inside table files. `Name()` is a compatibility identifier and must change if encoding changes incompatibly.

Dependencies and integration: referenced from `Options::filter_policy` and internal table/filter block code. Custom comparators that ignore parts of keys require matching filter semantics.

Risks and edge cases: false positives are allowed, false negatives for existing keys are not. Using bytewise bloom filters with a comparator that ignores key suffixes can make existing keys unreachable.

Test signals: bloom/filter tests are elsewhere; this subset only covers integration through options/table APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/filter_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/iterator.h -->
# sources/storage-engines/leveldb/include/leveldb/iterator.h

Purpose: declares the common iterator interface for DBs, tables, internal merged iterators, and error/empty iterators.

Important APIs and types: abstract `Iterator`, `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `Next`, `Prev`, `key`, `value`, `status`, `RegisterCleanup`, `CleanupNode`, `NewEmptyIterator`, and `NewErrorIterator`.

Control flow: callers seek before reading, move forward/backward while valid, inspect key/value slices until the next iterator mutation, then check `status`. Cleanup callbacks run when the iterator is destroyed.

State and persistence behavior: no persistence itself. Iterators often pin resources such as versions, cache handles, table blocks, or snapshots through cleanup callbacks.

Dependencies and integration: table cache registers cache-handle release cleanups; DB and table APIs return `Iterator*`. Uses `Slice` and `Status`.

Risks and edge cases: non-const iterator methods need external synchronization if shared across threads. `key()` and `value()` slices have limited lifetime. Cleanup callbacks must tolerate destruction order.

Test signals: issue 200 covers direction switching behavior at the DB iterator layer; table and DB tests exercise iterator contracts broadly.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/options.h -->
# sources/storage-engines/leveldb/include/leveldb/options.h

Purpose: declares configuration structures for database, read, and write operations.

Important APIs and types: `CompressionType` values `kNoCompression`, `kSnappyCompression`, `kZstdCompression`; `Options` fields for comparator, creation flags, paranoid checks, env, info log, write buffer, open-file limit, block cache/size/restart interval, max file size, compression, zstd level, log reuse, and filter policy; `ReadOptions` fields `verify_checksums`, `fill_cache`, `snapshot`; `WriteOptions::sync`.

Control flow: `Options` is supplied at DB/table-builder open time, while `ReadOptions` and `WriteOptions` alter individual operations. Some table builder options can change dynamically.

State and persistence behavior: comparator name/order, compression type, table block layout choices, filter policy name/encoding, and write sync semantics affect persistent data. `reuse_logs` affects recovery/open behavior. Larger write buffers lengthen recovery work.

Dependencies and integration: references comparator, env, cache, filter policy, logger, and snapshot APIs. Used by DB, table, table builder, repair, and cache code.

Risks and edge cases: compression enum values are persistent and must not change. Opening an existing DB with a different comparator is invalid. `sync=false` can lose recent writes on machine crash. `filter_policy` must remain live while DB is open.

Test signals: recovery tests cover `reuse_logs`; issue178 disables compression to stabilize compaction layout; memenv DB tests set `env`.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/slice.h -->
# sources/storage-engines/leveldb/include/leveldb/slice.h

Purpose: declares `Slice`, LevelDB's lightweight non-owning byte-string view.

Important APIs and types: constructors from pointer/length, `std::string`, and C string; `data`, `size`, `empty`, `begin`, `end`, `operator[]`, `clear`, `remove_prefix`, `ToString`, `compare`, `starts_with`, equality and inequality operators.

Control flow: APIs pass keys, values, encoded metadata, and file-read results as `Slice`s to avoid copies. Parsing code mutates local slices with `remove_prefix`.

State and persistence behavior: no ownership or persistence; it may refer to persistent bytes, scratch buffers, strings, or in-memory encoded records owned elsewhere.

Dependencies and integration: used throughout public and internal APIs. Comparators and filters interpret slices as byte sequences.

Risks and edge cases: caller must ensure backing storage outlives the slice. C-string constructor uses `strlen`, so embedded NUL data requires pointer/length construction. `operator[]` and `remove_prefix` enforce bounds only through asserts.

Test signals: indirectly covered everywhere; no direct slice tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/slice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/status.h -->
# sources/storage-engines/leveldb/include/leveldb/status.h

Purpose: declares `Status`, LevelDB's value type for success and categorized errors.

Important APIs and types: constructors/destructor/copy/move operations, factories `OK`, `NotFound`, `Corruption`, `NotSupported`, `InvalidArgument`, `IOError`, predicates `ok`, `IsNotFound`, `IsCorruption`, `IsIOError`, `IsNotSupportedError`, `IsInvalidArgument`, and `ToString`.

Control flow: functions return `Status` by value. OK is represented by `state_ == nullptr`; errors allocate a compact state buffer containing message length, code, and message.

State and persistence behavior: status is process-local diagnostic state and is not itself persisted, though error categories guide recovery and repair behavior.

Dependencies and integration: all DB/env/table APIs use it. C API converts non-OK statuses into malloc-owned strings.

Risks and edge cases: const methods are thread-safe but mutation/copy assignment requires external synchronization if shared. Error messages are copied, but `Slice` inputs must be valid during construction.

Test signals: indirectly exercised by all tests; no dedicated status tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/table.h -->
# sources/storage-engines/leveldb/include/leveldb/table.h

Purpose: declares the immutable sorted-table reader API for SSTable files.

Important APIs and types: `Table::Open`, destructor, `NewIterator`, `ApproximateOffsetOf`, private friend `TableCache`, `BlockReader`, `InternalGet`, `ReadMeta`, and `ReadFilter`.

Control flow: `Open` reads table footer/metadata and returns a table object tied to a live `RandomAccessFile`. `NewIterator` scans table entries. `InternalGet` seeks and optionally uses filter metadata to avoid block reads. `ApproximateOffsetOf` maps a key to an estimated file byte offset.

State and persistence behavior: table files are immutable persistent storage. `Table` owns parsed metadata but not the file object, which must outlive it.

Dependencies and integration: used by `TableCache`, version reads, compactions, repair, and approximate-size APIs. Depends on iterator and options/read options.

Risks and edge cases: file-size mismatch or corrupted metadata makes `Open` fail. The file lifetime contract is easy to violate outside `TableCache`.

Test signals: table behavior is covered elsewhere; this subset exercises it through table cache, repair, recovery, and DB tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/table_builder.h -->
# sources/storage-engines/leveldb/include/leveldb/table_builder.h

Purpose: declares the writer for LevelDB table files, used by memtable flush, compaction, repair, and standalone table construction.

Important APIs and types: `TableBuilder`, `ChangeOptions`, `Add`, `Flush`, `status`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, private `WriteBlock`, and `WriteRawBlock`.

Control flow: callers create a builder with a writable file, add keys in strictly increasing comparator order, optionally flush blocks, then call `Finish` or `Abandon` before destruction. `Finish` stops using the file but does not close it.

State and persistence behavior: writes persistent table blocks, index/meta blocks, filters, compression, and footer through the supplied file. File size is tracked as output grows.

Dependencies and integration: depends on `Options`, `WritableFile`, `BlockBuilder`, and compression settings. Used by `BuildTable` and repair table copying.

Risks and edge cases: failing to call `Finish` or `Abandon` before destruction violates the contract. Out-of-order keys corrupt table format assumptions. Only some options can change dynamically.

Test signals: indirectly covered by memtable flush, compaction, repair, and memenv DB tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/table_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/write_batch.h -->
# sources/storage-engines/leveldb/include/leveldb/write_batch.h

Purpose: declares the public `WriteBatch` API for grouping ordered updates into one atomic DB write.

Important APIs and types: `WriteBatch`, nested `Handler`, `Put`, `Delete`, `Clear`, `ApproximateSize`, `Append`, and `Iterate`.

Control flow: users add puts/deletes in order, pass the batch to `DB::Write`, or iterate it with a custom handler. Append concatenates operations from another batch without changing the source.

State and persistence behavior: private `rep_` stores the WAL-compatible byte encoding implemented in `write_batch.cc`. Atomicity and sequence assignment are handled by DB internals.

Dependencies and integration: public DB write API consumes it; `WriteBatchInternal` is a friend for log/recovery/memtable insertion.

Risks and edge cases: mutable operations require external synchronization if a batch is shared. `ApproximateSize` is implementation-detail-oriented and not a stable logical byte count.

Test signals: direct tests in `write_batch_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/include/leveldb/write_batch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/issues/issue178_test.cc -->
# sources/storage-engines/leveldb/issues/issue178_test.cc

Purpose: regression test for issue 178, where manual compaction could cause deleted data to reappear.

Important APIs and functions: helpers `Key1`, `Key2`, constant `kNumKeys`, and test `Issue178.Test`.

Control flow: creates a DB with compression disabled, bulk writes a first key range and a second related key range, deletes the second range, manually compacts only the first range, then iterates the DB and expects exactly the first-range key count.

State and persistence behavior: forces large table/level state and tombstones, then validates compaction preserves delete semantics. Disabling compression stabilizes file layout enough to hit the target scenario.

Dependencies and integration: uses public `DB`, `WriteBatch`, `CompactRange`, iterators, and `DestroyDB`. It is tied to compaction boundary and obsolete-entry logic in `VersionSet`/`DBImpl`.

Risks and edge cases: large `kNumKeys` makes it a heavier regression. The test counts keys rather than checking every key's value/deletion state.

Test signals: high-value regression for compaction not resurrecting deleted range data.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/issues/issue178_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/issues/issue200_test.cc -->
# sources/storage-engines/leveldb/issues/issue200_test.cc

Purpose: regression test for iterator direction-switch behavior after a mutation outside the iterator's snapshot.

Important APIs and functions: test `Issue200.Test`.

Control flow: opens a DB, writes keys `1` through `5`, creates an iterator, writes key `25`, then seeks to `5`, moves backward to `3`, and forward to `5`, asserting the new `25` does not disturb the iterator sequence.

State and persistence behavior: relies on iterator creation capturing a stable view independent of later writes.

Dependencies and integration: uses public `DB`, `Iterator`, `ReadOptions`, `WriteOptions`, and test utilities. It targets DB iterator merging and direction-change code outside this subset.

Risks and edge cases: narrow regression, not a broad iterator fuzz test. It assumes bytewise key order where `"25"` sorts between `"2"` and `"3"` lexicographically.

Test signals: precise signal for a historical duplicate/unexpected-yield bug on `Prev` to `Next` transition.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/issues/issue200_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/issues/issue320_test.cc -->
# sources/storage-engines/leveldb/issues/issue320_test.cc

Purpose: stress regression for issue 320 involving many random writes, deletes, updates, large values, and retained snapshots.

Important APIs and functions: helpers `GenerateRandomNumber`, `CreateRandomString`, and test `Issue320.Test`.

Control flow: maintains an in-memory model vector of up to 10,000 key/value pairs, runs 200,000 random operations, checks existing values with `Get` before mutation, writes batches containing put/delete operations, and randomly replaces retained snapshots.

State and persistence behavior: exercises WAL/memtable/table/compaction behavior under snapshot retention, which can delay obsolete-file and obsolete-entry cleanup. Values are 1 KiB strings with deterministic index-derived prefixes.

Dependencies and integration: uses public `DB`, `WriteBatch`, snapshots, read/write options, and destroy/open helpers.

Risks and edge cases: random seed is fixed with `std::srand(0)`, giving reproducible coverage but not exhaustive exploration. Snapshot vector entries must all be released before DB close.

Test signals: strong long-run signal for consistency under snapshots and compaction pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/issues/issue320_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/port/port.h -->
# sources/storage-engines/leveldb/port/port.h

Purpose: selects the active platform port header for synchronization, compression, CRC, and other low-level primitives.

Important APIs and macros: includes `port/port_stdcxx.h` for POSIX/Windows, `port/port_chromium.h` for Chromium, based on `LEVELDB_PLATFORM_POSIX`, `LEVELDB_PLATFORM_WINDOWS`, or `LEVELDB_PLATFORM_CHROMIUM`.

Control flow: all code including `port/port.h` receives platform-specific `leveldb::port` definitions from the selected header.

State and persistence behavior: no runtime state; selected compression/CRC capabilities can affect table encoding/performance through port functions.

Dependencies and integration: included by internal code such as table cache, skiplist tests, memenv, and version-set headers.

Risks and edge cases: builds must define exactly the expected platform macro path; unsupported platforms should use `port_example.h` as a template for a new port.

Test signals: compile/link coverage validates selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/port/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/port/port_config.h.in -->
# sources/storage-engines/leveldb/port/port_config.h.in

Purpose: CMake configuration template for feature-detection macros used by LevelDB's port layer.

Important APIs and macros: `HAVE_FDATASYNC`, `HAVE_FULLFSYNC`, `HAVE_O_CLOEXEC`, `HAVE_CRC32C`, `HAVE_SNAPPY`, and intended `HAVE_ZSTD`.

Control flow: CMake replaces `#cmakedefine01` entries with 0/1 definitions unless the macro is already defined externally.

State and persistence behavior: compile-time only. Feature flags alter sync behavior, compression availability, and accelerated checksum paths.

Dependencies and integration: consumed by platform port implementations and build system generated headers.

Risks and edge cases: the guard uses `#if !defined(HAVE_Zstd)` but defines/checks `HAVE_ZSTD`, a spelling inconsistency that could surprise external defines. Incorrect feature detection can silently disable compression or fsync variants.

Test signals: build configuration and compression/sync tests validate generated output.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/port/port_config.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/port/port_example.h -->
# sources/storage-engines/leveldb/port/port_example.h

Purpose: documents the interface a platform-specific `port_<platform>.h` implementation must provide.

Important APIs and types: `port::Mutex`, `port::CondVar`, Snappy functions, Zstd functions, `GetHeapProfile`, and `AcceleratedCRC32C`.

Control flow: new platform ports implement mutex locking/assertion, condition wait/signal, compression length/compress/uncompress helpers, optional heap profiling, and optional accelerated CRC extension.

State and persistence behavior: port compression choices affect persistent table block encodings; sync and mutex behavior affect durability and correctness indirectly through actual platform implementation.

Dependencies and integration: includes thread annotation macros and defines the contract used by internal LevelDB code through `port/port.h`.

Risks and edge cases: compression functions must return false when unsupported, not produce partial encodings. Mutex and condition variable semantics must match LevelDB concurrency assumptions. CRC acceleration returns zero both for unsupported and a possible CRC value, so callers must follow the documented interpretation.

Test signals: this is a specification header, so tests apply to concrete port implementations rather than this file directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/port/port_example.h -->
