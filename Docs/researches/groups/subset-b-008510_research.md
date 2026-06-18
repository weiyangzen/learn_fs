# Research Group subset-b-008510

This grouped report covers LevelDB DB-layer implementation, format, log, memtable, utility, C API, corruption, fault-injection, and regression test files under `sources/storage-engines/leveldb/db`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/c_test.c -->
# sources/storage-engines/leveldb/db/c_test.c

## Purpose
This C executable is the smoke and integration test for the public `leveldb/c.h` API. It validates object lifecycle, option setters, read/write/delete calls, batches, iterators, approximate sizes, properties, snapshots, repair, custom comparators, cache/env ownership, and filter policies from pure C.

## Important APIs, Types, And Functions
The file uses `leveldb_t`, comparator/cache/env/options/readoptions/writeoptions/snapshot/iterator/writebatch/filterpolicy handles, and the C functions for open/close, destroy/repair, get/put/delete/write, compaction, iteration, property lookup, approximate sizing, and memory release. Test helpers include `StartPhase`, `CheckNoError`, `CheckCondition`, `CheckEqual`, `CheckGet`, `CheckIter`, write-batch callbacks `CheckPut`/`CheckDel`, comparator callbacks, and fake filter callbacks.

## Control Flow
`main` builds all C API objects, destroys any old test DB, verifies open failure when `create_if_missing` is off, opens with options, performs puts, range compactions, batch append/iterate checks, ordered iterator navigation, bulk writes for approximate size checks, property reads, snapshot isolation, repair/reopen, and two filter-policy runs. It then destroys all API objects and prints `PASS`.

## State And Persistence Behavior
The test creates a real database in the default test directory, writes sync and non-sync records, forces compaction, closes/reopens around repair, and verifies that repair preserves surviving keys. Snapshots preserve the older `foo` value after deletion until released. The filter phase destroys and recreates the DB for custom and bloom-filter runs.

## Dependencies And Integration Points
It depends on the C wrapper over `DBImpl`, write batches, iterators, options, Env test directory, comparator/filter callback bridges, repair, and compaction APIs. It is the key compatibility signal for non-C++ users.

## Risks And Edge Cases
The test exercises ownership and `leveldb_free` paths, but it is single-threaded and does not check all option combinations. The custom filter negative-path check appears guarded by `if (phase == 0)`, comparing a string pointer to zero, so the intended fake-filter-false assertions are effectively disabled.

## Test Signals
Failures identify C ABI regressions, callback marshalling bugs, iterator ordering issues, snapshot breakage, repair problems, property/size API regressions, or object lifecycle leaks/crashes.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/c_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/corruption_test.cc -->
# sources/storage-engines/leveldb/db/corruption_test.cc

## Purpose
This gtest suite validates LevelDB behavior when logs, table files, descriptors, and compaction inputs are corrupted or missing. It checks both tolerant recovery and paranoid error propagation.

## Important APIs, Types, And Functions
`CorruptionTest` owns a `test::ErrorEnv`, tiny block cache, `Options`, and `DB*`. Helpers `Build`, `Check`, `Corrupt`, `RepairDB`, `TryReopen`, `Property`, `Key`, and `Value` create deterministic data, corrupt newest files of a requested `FileType`, and count surviving records. Tests cover recovery, write errors, table corruption, repair, index/footer corruption, descriptor loss/corruption, sequence recovery, compaction input errors, paranoid mode, and unrelated-key writes.

## Control Flow
Most tests populate the DB, force memtable/table compactions via `DBImpl` test hooks, mutate on-disk bytes using the underlying env, reopen or repair, then iterate to count valid keys. Log corruption drops complete corrupted records. Table corruption causes partial data loss or read errors depending on paranoid checks. Descriptor corruption prevents open until repair.

## State And Persistence Behavior
The suite intentionally damages persistent log, table, and manifest/descriptor files. Repair reconstructs metadata from tables and logs and must recover the last sequence number so later writes are not hidden by older entries. `Corrupt` picks the highest-numbered file of a type and flips bytes at absolute or end-relative offsets.

## Dependencies And Integration Points
It integrates `DBImpl`, file naming, WAL format, `VersionSet`, table cache, repair, write batches, `test::ErrorEnv`, block cache, and table checksums. It exercises recovery decisions that normal DB tests do not cover.

## Risks And Edge Cases
The expected key-count ranges tolerate partial loss, so they catch broad safety properties more than exact recovery contents. Corruption offsets assume current file layout. Non-paranoid recovery ignores some errors by design, while paranoid mode should convert corruption into persistent write/open failure.

## Test Signals
Strong signals are bounded surviving record counts, reopen failure on missing/corrupt descriptors under paranoid checks, repair restoring latest values, writes failing after paranoid compaction corruption, and unrelated keys remaining usable after a corrupt table.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/corruption_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_impl.cc -->
# sources/storage-engines/leveldb/db/db_impl.cc

## Purpose
This is LevelDB's central `DB` implementation. It coordinates option sanitization, DB creation/open/recovery, write-ahead logging, memtable and immutable memtable state, snapshots, reads, write batching, L0 flushing, background/manual compaction, file garbage collection, properties, approximate sizes, destruction, and the public `DB::Open`/`DestroyDB` entry points.

## Important APIs, Types, And Functions
Internal structs `DBImpl::Writer`, `CompactionState`, `CompactionState::Output`, and `ManualCompaction` model write queue entries and in-flight compactions. Major functions include `SanitizeOptions`, `NewDB`, `Recover`, `RecoverLogFile`, `WriteLevel0Table`, `CompactMemTable`, `CompactRange`, `MaybeScheduleCompaction`, `BackgroundCompaction`, `DoCompactionWork`, `NewInternalIterator`, `Get`, `NewIterator`, `Write`, `BuildBatchGroup`, `MakeRoomForWrite`, `GetProperty`, `GetApproximateSizes`, `DB::Open`, and `DestroyDB`.

## Control Flow
Open creates a `DBImpl`, locks the DB, creates or recovers the manifest, replays eligible logs into memtables, optionally reuses the last log, creates a new log/memtable if needed, writes recovered manifest edits, removes obsolete files, and schedules compaction. Writes enter a FIFO writer queue, optionally group compatible batches, reserve sequence numbers, append to the WAL, optionally sync, insert into `mem_`, publish `LastSequence`, and wake queued writers. `MakeRoomForWrite` delays near L0 soft limits, waits on immutable memtables and L0 hard limits, or rotates to a new log and immutable memtable before scheduling background compaction.

## State And Persistence Behavior
Persistent state is the DB directory: `CURRENT`, `LOCK`, `LOG`, `MANIFEST-*`, `.ldb/.sst` tables, and temp files. `pending_outputs_` protects files being built from deletion. Manifest changes are installed via `VersionSet::LogAndApply`; log replay writes memtables to L0 when recovery memory exceeds `write_buffer_size`. Sync write failures and log close failures record `bg_error_`, after which future writes fail and obsolete file deletion is suppressed. Snapshots pin sequence visibility; iterators pin `mem_`, `imm_`, and the current `Version`.

## Dependencies And Integration Points
The file is tied to `MemTable`, `VersionSet`, `VersionEdit`, `Compaction`, `TableCache`, table `BuildTable`, `log::Reader`/`Writer`, `WriteBatchInternal`, `DBIter`, `filename` helpers, Env file APIs, comparators, filter policies, block/table builders, merging iterators, snapshots, and logging. Public methods implement the `leveldb::DB` contract and expose test hooks used heavily by `db_test.cc` and corruption tests.

## Risks And Edge Cases
This file is concurrency and crash-recovery critical. Risks include write group sequence assignment, WAL sync uncertainty, log reuse recovery, stale-file deletion after failed manifest writes, compaction output installation order, snapshot-aware version dropping, deletion-marker elision only at base level, L0 write stalls, manual compaction range progress, shutdown races, and iterator lifetime pinning. `MaybeIgnoreError` deliberately masks some errors unless `paranoid_checks` is set.

## Test Signals
`db_test.cc`, `corruption_test.cc`, and `fault_injection_test.cc` directly validate most surfaces: open options, locking, recovery, large logs, log reuse, sync/log-close/manifest errors, missing SST files, compaction output cleanup, snapshots, iterators, bloom filters, multithreaded writes, randomized model comparison, and crash-like unsynced file loss.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_impl.h -->
# sources/storage-engines/leveldb/db/db_impl.h

## Purpose
This header declares `DBImpl`, the concrete implementation of the public `leveldb::DB` interface, and exposes internal test hooks plus option sanitization.

## Important APIs, Types, And Functions
`DBImpl` overrides `Put`, `Delete`, `Write`, `Get`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `GetProperty`, `GetApproximateSizes`, and `CompactRange`. Test-only APIs are `TEST_CompactRange`, `TEST_CompactMemTable`, `TEST_NewInternalIterator`, `TEST_MaxNextLevelOverlappingBytes`, and `RecordReadSample`. Private declarations cover recovery, log replay, memtable flush, write-room management, write grouping, compaction scheduling, compaction output creation/finish/install, and `SanitizeOptions`.

## Control Flow
The header shows the intended lock discipline: most persistent DB state is under `mutex_`, while `table_cache_` has its own synchronization and `shutting_down_`/`has_imm_` are atomics for background coordination. Background work runs through static `BGWork` into instance methods. Manual compaction state is represented by `ManualCompaction`.

## State And Persistence Behavior
Members capture all live DB state: env/options/db name, file lock, current WAL file and writer, `mem_`, immutable memtable, writer queue, snapshots, pending output table numbers, background/manual compaction state, `VersionSet`, background error, and per-level compaction stats. Persistent structures are not encoded here, but the declarations define which objects can mutate logs, manifests, and table files.

## Dependencies And Integration Points
The header depends on internal key format, log writer, snapshots, public DB/Env APIs, port mutex/condvar/thread annotations, and forward declarations for memtable/table-cache/version classes. Tests include this header to downcast `DB*` and call private-ish test hooks.

## Risks And Edge Cases
The main risks are ownership and lifetime: raw pointers for log files, memtables, versions, cache, logger, and DB lock must be released on all paths. Thread annotations document but do not enforce runtime safety. Test hooks bypass public API constraints and can perturb background scheduling.

## Test Signals
Compilation validates interface consistency. Behavioral coverage comes from `db_test.cc`, corruption tests, and fault-injection tests using `DBImpl` hooks to force memtable and range compactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_iter.cc -->
# sources/storage-engines/leveldb/db/db_iter.cc

## Purpose
This file implements `DBIter`, the user-facing iterator adapter that turns internal `(user key, sequence, value type)` entries from memtables and tables into visible user key/value entries at a snapshot sequence.

## Important APIs, Types, And Functions
The anonymous `DBIter` class derives from `Iterator` and implements `Valid`, `key`, `value`, `status`, `Next`, `Prev`, `Seek`, `SeekToFirst`, and `SeekToLast`. Private helpers `FindNextUserEntry`, `FindPrevUserEntry`, `ParseKey`, `SaveKey`, `ClearSavedValue`, and `RandomCompactionPeriod` manage visibility, direction switching, saved reverse values, and read sampling. `NewDBIterator` is the exported factory.

## Control Flow
Forward iteration skips entries newer than the snapshot, hides older values behind deletion markers, and returns the first visible value for a user key. Reverse iteration walks internal entries backwards, retaining the latest visible non-deleted value for each previous user key. Direction changes reposition the child iterator to avoid re-yielding the current user key. Seek constructs an internal seek key with `kValueTypeForSeek`.

## State And Persistence Behavior
The iterator has no durable state, but it affects compaction scheduling through `DBImpl::RecordReadSample` after roughly randomized `config::kReadBytesPeriod` bytes. It preserves snapshot state via the fixed `sequence_`. Large saved reverse values may release capacity to avoid retaining excessive memory.

## Dependencies And Integration Points
It depends on `DBImpl`, internal key parsing, `Iterator`, `Random`, comparators, logging utilities, and config constants. `DBImpl::NewIterator` wraps a merging internal iterator with this adapter.

## Risks And Edge Cases
Iterator correctness hinges on internal-key ordering by user key then decreasing sequence. Direction switching around invalid child positions, deletion markers, corrupted internal keys, and saved large values are sensitive paths. Read sampling must not corrupt iteration state.

## Test Signals
`db_test.cc` iterator tests cover empty/single/multi-key scans, seek boundaries, forward/reverse direction changes, deletes, compaction, snapshot pinning, large values, and randomized model comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_iter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_iter.h -->
# sources/storage-engines/leveldb/db/db_iter.h

## Purpose
This header declares the factory for creating a user-visible DB iterator over an internal iterator at a fixed sequence number.

## Important APIs, Types, And Functions
`NewDBIterator(DBImpl* db, const Comparator* user_key_comparator, Iterator* internal_iter, SequenceNumber sequence, uint32_t seed)` returns a heap-allocated `Iterator`. The caller transfers ownership of `internal_iter` to the returned iterator.

## Control Flow
There is no implementation in the header. The signature exposes the needed inputs: DB backpointer for read sampling, user comparator for key grouping, internal iterator for raw entries, snapshot sequence for visibility, and random seed for sampling period.

## State And Persistence Behavior
The header defines no state and no persistence behavior. Runtime state lives in `DBIter` in `db_iter.cc`, while persistent visibility is controlled by the supplied sequence number.

## Dependencies And Integration Points
It includes `dbformat.h` and `leveldb/db.h`, forward-declares `DBImpl`, and is consumed by `db_impl.cc`.

## Risks And Edge Cases
Callers must pass an internal iterator ordered by `InternalKeyComparator` and keep DB/comparator lifetimes valid for the iterator. Misusing the sequence number changes snapshot visibility.

## Test Signals
Coverage is indirect through public iterator tests in `db_test.cc` and randomized iterator comparison against `ModelDB`.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_test.cc -->
# sources/storage-engines/leveldb/db/db_test.cc

## Purpose
This is the broad integration and regression suite for LevelDB's DB layer. It validates CRUD, recovery, snapshots, iteration, compaction, approximate sizes, comparator behavior, open/destroy semantics, error handling, bloom filters, concurrency, and randomized equivalence to a model DB across option configurations.

## Important APIs, Types, And Functions
Helpers include `SpecialEnv` for injected file/sync/manifest/log errors and random-read counting, `DBTest` for DB lifecycle and compaction helpers, `AllEntriesFor`, `FilesPerLevel`, `DeleteAnSSTFile`, and `RenameLDBToSST`. Test cases span basic operations, immutable/version reads, memory usage, snapshot families, L0 ordering, iterator behavior, recovery, minor/major compactions, repeated overwrite control, sparse merge overlap, deletion-marker handling, L0 bug regressions, custom comparators, manual compaction, open/destroy/lock options, no-space/non-writable/sync/manifest/log-close failures, missing/legacy SST handling, bloom filters, multithreading, and randomized model comparison.

## Control Flow
Most tests run under multiple option configurations: default, log reuse, bloom filter, and no compression. The fixture repeatedly destroys/reopens databases, writes deterministic or random data, forces memtable and range compactions via `DBImpl` hooks, checks visible values and internal entries, and reopens to validate persistence. The randomized test mirrors operations into a `ModelDB`, compares full and snapshot iterators every 100 steps, and reopens the real DB during the run.

## State And Persistence Behavior
The suite exercises WAL replay, manifest persistence, memtable flush to tables, L0 and deeper compactions, obsolete file deletion, snapshots pinning old sequence visibility, lock files, and recovery across process-like reopen. `SpecialEnv` simulates data sync errors, no-space writes dropped on floor, non-writable filesystems, manifest sync/write failure, log close failure, and delayed data sync.

## Dependencies And Integration Points
It integrates nearly every DB-layer component: `DBImpl`, `VersionSet`, file naming, write batches, table files, bloom filters, cache, Env, mutex/thread APIs, internal key parsing, and public DB APIs. It is the principal regression suite for changes in `db_impl.cc`, `db_iter.cc`, `dbformat`, compaction logic, and file cleanup.

## Risks And Edge Cases
The file encodes many historical bug cases, so changes to compaction thresholds, file naming, or option defaults can require careful updates. Timing-sensitive tests use sleeps for background compaction and multithreading. Randomized testing compares iterators but has a TODO for direct `Get()` model checks.

## Test Signals
High-value signals include exact iterator sequences, `AllEntriesFor` internal-version expectations, file count bounds, successful reopen after recovery cases, future write failure after sync/log errors, manifest failure not losing data, bloom filter random-read limits, thread value-pattern checks, and randomized model iterator equivalence.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/db_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/dbformat.cc -->
# sources/storage-engines/leveldb/db/dbformat.cc

## Purpose
This file implements LevelDB's internal key encoding, internal comparator, internal filter-policy adapter, debug formatting, and `LookupKey` construction.

## Important APIs, Types, And Functions
`PackSequenceAndType`, `AppendInternalKey`, `ParsedInternalKey::DebugString`, `InternalKey::DebugString`, `InternalKeyComparator::Name/Compare/FindShortestSeparator/FindShortSuccessor`, `InternalFilterPolicy::Name/CreateFilter/KeyMayMatch`, and `LookupKey::LookupKey` are the main functions.

## Control Flow
Internal keys append the user key followed by a fixed64 tag `(sequence << 8) | type`. The comparator first delegates to the user comparator on extracted user keys, then sorts larger sequence/type tags earlier. Separator/successor shortening applies only to the user portion and appends the maximal sequence seek tag. The filter adapter strips internal suffixes before delegating to the user filter policy.

## State And Persistence Behavior
The internal key encoding is persisted in memtables, WAL write batches after insertion, SSTable keys, manifests via file key bounds, and lookup keys. Changing it would break on-disk compatibility. `LookupKey` uses inline stack storage for short keys and heap storage for large keys.

## Dependencies And Integration Points
It depends on comparators, filter policies, table builder APIs, fixed/varint coding, logging escaping, and `Slice`. It is used by memtable, version/table lookup, compaction, iterators, file metadata, and tests.

## Risks And Edge Cases
The low eight bits of the tag encode value type, so enum values are compatibility-sensitive. `InternalFilterPolicy::CreateFilter` mutates the caller-provided `Slice` array via `const_cast`, relying on table-builder behavior. Separator logic must preserve strict ordering.

## Test Signals
`dbformat_test.cc` checks encode/decode, empty decode failure, separators, successors, and debug strings. DB and iterator tests indirectly validate ordering and visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/dbformat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/dbformat.h -->
# sources/storage-engines/leveldb/db/dbformat.h

## Purpose
This header defines LevelDB's internal key format and constants used across the DB implementation.

## Important APIs, Types, And Functions
It declares `config` constants for level count, L0 compaction/slowdown/stop thresholds, max memtable compaction level, and read sampling period. It defines `ValueType`, `SequenceNumber`, `kMaxSequenceNumber`, `ParsedInternalKey`, `InternalKeyComparator`, `InternalFilterPolicy`, `InternalKey`, `LookupKey`, `AppendInternalKey`, `ParseInternalKey`, `ExtractUserKey`, and `InternalKeyEncodingLength`.

## Control Flow
Inline parsing requires at least eight suffix bytes, decodes the fixed64 tag, splits sequence and value type, and rejects unknown value types. `InternalKey` wraps encoded strings to discourage accidental bytewise comparisons. `LookupKey` exposes three slices: memtable key with length prefix, internal key, and user key.

## State And Persistence Behavior
These definitions are on-disk contract. Internal keys are stored in tables and memtables and determine ordering, snapshot visibility, and deletion semantics. Config constants control compaction scheduling and write stall behavior, affecting persistent file layout but not file format.

## Dependencies And Integration Points
The header is included by DB implementation, memtable, version set, table cache, builders, iterators, filenames, dumps, and tests. It connects public comparators/filter policies to LevelDB internal data.

## Risks And Edge Cases
Changing enum values, sequence packing, comparator semantics, or max sequence would be format-breaking. `ExtractUserKey` asserts length >= 8, so callers must validate corrupted keys before extraction.

## Test Signals
`dbformat_test.cc` directly covers core encoding and comparator shortening. DB, corruption, and iterator tests exercise the same definitions under real storage operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/dbformat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/dbformat_test.cc -->
# sources/storage-engines/leveldb/db/dbformat_test.cc

## Purpose
This file tests internal key encoding, parsing, comparator shortening, successor generation, and debug formatting.

## Important APIs, Types, And Functions
Helpers `IKey`, `Shorten`, `ShortSuccessor`, and `TestKey` wrap `AppendInternalKey`, `InternalKeyComparator`, and `ParseInternalKey`. Tests include `InternalKey_EncodeDecode`, `InternalKey_DecodeFromEmpty`, `InternalKeyShortSeparator`, `InternalKeyShortestSuccessor`, `ParsedInternalKeyDebugString`, and `InternalKeyDebugString`.

## Control Flow
Tests encode multiple user keys and sequence-number boundaries, parse them back, and assert type/sequence/user-key equality. Separator tests compare exact encoded results for same keys, misordered ranges, ordered ranges, prefix cases, and successor cases.

## State And Persistence Behavior
The tests do not create DB files, but they validate the persistent key format used in WAL-derived memtable entries and SSTable keys.

## Dependencies And Integration Points
It depends on `dbformat.h`, `gtest`, bytewise comparator, and logging utilities. It protects assumptions used by memtable, table building, lookup, and compaction.

## Risks And Edge Cases
Coverage focuses on bytewise comparator behavior. Custom comparator separator behavior is not tested here, though `db_test.cc` covers a numeric comparator at the DB level.

## Test Signals
Failures indicate format incompatibility, comparator ordering regressions, separator/successor mistakes, or corrupted-key debug output changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/dbformat_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/dumpfile.cc -->
# sources/storage-engines/leveldb/db/dumpfile.cc

## Purpose
This file implements `DumpFile`, a debugging utility that prints LevelDB log, descriptor, and table file contents in human-readable form.

## Important APIs, Types, And Functions
Key helpers are `GuessType`, `CorruptionReporter`, `PrintLogContents`, `WriteBatchItemPrinter`, `WriteBatchPrinter`, `DumpLog`, `VersionEditPrinter`, `DumpDescriptor`, `DumpTable`, and exported `DumpFile`.

## Control Flow
`DumpFile` infers file type from the basename using `ParseFileName`. Logs and descriptors are read with `log::Reader`; each WAL record is interpreted as a `WriteBatch`, and each descriptor record as a `VersionEdit`. Table dumping opens a table with default options, iterates from first to last without seeking by comparator-sensitive ranges, parses internal keys, and prints sequence/type/value lines or bad-key diagnostics.

## State And Persistence Behavior
The file reads persistent DB artifacts but does not mutate them. It disables cache filling while dumping tables. Corruption encountered by the log reader is reported to the destination `WritableFile`.

## Dependencies And Integration Points
It integrates filename parsing, log reader, version edit decoding, write batch internals, table opening/iteration, internal key parsing, Env file APIs, and logging escape helpers. `leveldbutil.cc` exposes it via a command-line tool.

## Risks And Edge Cases
Dumping tables with default comparator is intentionally limited to sequential operations; seek/prev would be unsafe if DB comparator differs. Malformed WAL records shorter than the write-batch header are reported but not decoded.

## Test Signals
No direct test is listed in this subset. Indirect confidence comes from log, version edit, table, and filename tests; manual use of `leveldbutil dump` is the operational signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/dumpfile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/fault_injection_test.cc -->
# sources/storage-engines/leveldb/db/fault_injection_test.cc

## Purpose
This suite simulates crash-like loss of unsynced file data or unsynced newly-created files, validating LevelDB recovery across sync boundaries with and without log reuse.

## Important APIs, Types, And Functions
`FileState` tracks file position, last sync, and last flush. `TestWritableFile` wraps `WritableFile` to report appends, flushes, syncs, close, and parent directory sync. `FaultInjectionTestEnv` wraps Env operations, tracks file states and files created since the last directory sync, and can truncate unsynced data or remove unsynced files. `FaultInjectionTest` supplies `Build`, `Verify`, `OpenDB`, `CloseDB`, `DeleteAllData`, `ResetDBState`, and partial/no-write fault scenarios.

## Control Flow
Each test opens a DB under the wrapper env, repeatedly writes and compacts a pre-sync population, writes a post-sync population, simulates filesystem inactivity, closes the DB, drops unsynced state by truncating data or deleting unsynced new files, reopens, and verifies which key ranges should survive. It runs both `reuse_logs=false` and `reuse_logs=true`.

## State And Persistence Behavior
The wrapper models durable state as data that has reached `Sync()` and directory entries whose parent directory has been synced. `DropUnsyncedData` truncates files to their last synced position. `RemoveFilesCreatedAfterLastDirSync` deletes new files whose directory entries were not synced. The test assumes actual directory sync is not needed for the test environment and records it logically.

## Dependencies And Integration Points
It integrates `DBImpl`, Env wrappers, writable file lifecycle, file naming, log format, version set, table files, cache, write batches, mutex annotations, and random test data. It validates DBImpl's ordering of table/log/manifest/directory syncs.

## Risks And Edge Cases
This is a model of crash behavior, not a perfect filesystem simulator. It uses truncation via default Env and tracks only files opened through the wrapper. Expected errors for post-sync ranges are broad: a missing value is treated as acceptable when loss is expected.

## Test Signals
Passing indicates pre-sync data remains readable after simulated faults, post-sync unsynced data can be lost without corrupting the DB, and log reuse does not violate recovery guarantees.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/fault_injection_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/filename.cc -->
# sources/storage-engines/leveldb/db/filename.cc

## Purpose
This file constructs and parses LevelDB-owned file names and atomically updates `CURRENT` to point at the active manifest.

## Important APIs, Types, And Functions
`MakeFileName`, `LogFileName`, `TableFileName`, `SSTTableFileName`, `DescriptorFileName`, `CurrentFileName`, `LockFileName`, `TempFileName`, `InfoLogFileName`, `OldInfoLogFileName`, `ParseFileName`, and `SetCurrentFile` are implemented here.

## Control Flow
Numbered files use six-digit formatting plus suffixes `.log`, `.ldb`, `.sst`, or `.dbtmp`; descriptors use `MANIFEST-%06llu`; fixed names include `CURRENT`, `LOCK`, `LOG`, and `LOG.old`. `ParseFileName` recognizes these forms, consumes decimal numbers without locale-sensitive parsing, rejects trailing junk/overflow, and classifies `.sst` and `.ldb` as table files. `SetCurrentFile` writes the manifest basename plus newline to a temp file, renames it over `CURRENT`, and removes the temp on failure.

## State And Persistence Behavior
File naming defines the DB directory layout. `CURRENT` update is persistence-critical because it selects the active descriptor on reopen. Legacy `.sst` table names are accepted for compatibility, while new table names use `.ldb`.

## Dependencies And Integration Points
It depends on Env, status, `Slice`, `ConsumeDecimalNumber`, and `WriteStringToFileSync`. DB creation, recovery, destruction, compaction, table cache, repair, and utilities all rely on these helpers.

## Risks And Edge Cases
Parsing accepts `0.log` and `0.ldb` even constructors assert positive numbers, because existing or malformed names may be inspected. A failed rename leaves old `CURRENT` in place and removes the temp file. Locale-independent parsing avoids platform surprises.

## Test Signals
`filename_test.cc` validates successful and rejected parses, max uint64 boundary handling, and round trips for every constructor.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/filename.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/filename.h -->
# sources/storage-engines/leveldb/db/filename.h

## Purpose
This header declares LevelDB file type names, filename construction helpers, filename parsing, and `CURRENT` update API.

## Important APIs, Types, And Functions
`FileType` enumerates `kLogFile`, `kDBLockFile`, `kTableFile`, `kDescriptorFile`, `kCurrentFile`, `kTempFile`, and `kInfoLogFile`. The header declares constructors for log/table/legacy SST/descriptor/current/lock/temp/info-log names, `ParseFileName`, and `SetCurrentFile`.

## Control Flow
The header does not implement behavior, but its comments document DB-owned filename forms and that constructors prefix paths with `dbname`.

## State And Persistence Behavior
These declarations represent the stable DB directory contract. `SetCurrentFile` is used when creating or switching manifests and must make `CURRENT` durable enough for recovery.

## Dependencies And Integration Points
It depends on `Slice`, `Status`, port definitions, and forward-declares `Env`. It is included by DB implementation, dump utilities, tests, corruption/fault-injection suites, and repair/version code.

## Risks And Edge Cases
All components must agree on `FileType` classification. Accepting legacy `.sst` files while creating `.ldb` files is important for compatibility. Misparsing can lead to missed live files or unsafe deletion.

## Test Signals
`filename_test.cc` is the direct coverage; `db_test.cc` missing/legacy SST and destroy tests indirectly validate integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/filename.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/filename_test.cc -->
# sources/storage-engines/leveldb/db/filename_test.cc

## Purpose
This test suite validates LevelDB filename parsing and construction helpers.

## Important APIs, Types, And Functions
`FileNameTest.Parse` checks `ParseFileName` for fixed names, numbered logs/tables/descriptors, legacy `.sst`, `.ldb`, `.dbtmp`, info logs, and invalid forms. `FileNameTest.Construction` checks every constructor by stripping the DB prefix and parsing the basename.

## Control Flow
The parse test iterates successful cases with expected number/type pairs and a list of rejected strings, including overflow beyond `uint64_t`. The construction test builds names for multiple DB names and numbers, asserts the prefix, then validates parse results.

## State And Persistence Behavior
No files are created. The tests protect the naming contract used by persistent DB directories and recovery.

## Dependencies And Integration Points
It depends on `filename.h`, `dbformat.h`, port helpers, logging, and gtest. It supports DBImpl recovery, destroy, repair, and utility behavior.

## Risks And Edge Cases
Tests intentionally allow number zero in parsed table/log names but constructors assert positive numbers. They do not call `SetCurrentFile`, so temp-write/rename failure behavior is covered elsewhere only indirectly.

## Test Signals
Failures show filename compatibility regressions, parser laxness/strictness changes, or numeric overflow handling problems.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/filename_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/leveldbutil.cc -->
# sources/storage-engines/leveldb/db/leveldbutil.cc

## Purpose
This file implements the small `leveldbutil` command-line utility, currently exposing the `dump` command.

## Important APIs, Types, And Functions
`StdoutPrinter` implements `WritableFile` by writing appended data to `stdout`. `HandleDumpCommand` calls `DumpFile` for each supplied file. `Usage` prints accepted syntax. `main` parses `argv`, dispatches `dump`, and returns success/failure status.

## Control Flow
If no command or an unknown command is supplied, usage is printed and exit code is 1. For `dump`, every file argument is dumped to stdout; individual dump failures are printed to stderr while the command continues over remaining files and returns failure if any dump failed.

## State And Persistence Behavior
The utility does not mutate DB state. It reads files through `Env::Default()` and writes human-readable output to stdout/stderr.

## Dependencies And Integration Points
It depends on public dumpfile, Env, Status, and the `WritableFile` abstraction. It is the command-line integration point for `dumpfile.cc`.

## Risks And Edge Cases
There is no option parsing beyond command name, no explicit help command, and all output is unbuffered through `fwrite` from `Append`. Dump behavior depends on `DumpFile` type recognition.

## Test Signals
No direct test is listed here. Build/link success and manual `leveldbutil dump` behavior are the main signals; `dumpfile.cc` dependencies have indirect coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/leveldbutil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_format.h -->
# sources/storage-engines/leveldb/db/log_format.h

## Purpose
This header defines the physical write-ahead log record format shared by log reader and writer.

## Important APIs, Types, And Functions
`log::RecordType` defines `kZeroType`, `kFullType`, `kFirstType`, `kMiddleType`, and `kLastType`, with `kMaxRecordType = kLastType`. Constants `kBlockSize = 32768` and `kHeaderSize = 7` define block and header sizes.

## Control Flow
There is no executable code. The comments define that each header stores checksum (4 bytes), length (2 bytes), and type (1 byte), and that fragmented logical records use first/middle/last records.

## State And Persistence Behavior
This is a persistent WAL and descriptor-log format contract. Writers pad block trailers and readers use these constants to reassemble logical records and detect corruption.

## Dependencies And Integration Points
It is included by `log_reader`, `log_writer`, DB recovery, corruption tests, fault-injection tests, and log tests.

## Risks And Edge Cases
Changing constants or enum values would break existing logs and manifests. `kZeroType` is reserved for preallocated file regions and must be handled specially by readers.

## Test Signals
`log_test.cc` heavily exercises block boundaries, trailers, fragmentation, corruption, and initial offsets using these constants.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_reader.cc -->
# sources/storage-engines/leveldb/db/log_reader.cc

## Purpose
This file implements the LevelDB log reader that reconstructs logical records from physical WAL/manifest fragments, verifies checksums, handles corruption, and supports reading from an initial physical offset.

## Important APIs, Types, And Functions
`Reader::Reporter::~Reporter`, constructor/destructor, `SkipToInitialBlock`, `ReadRecord`, `LastRecordOffset`, `ReportCorruption`, `ReportDrop`, and `ReadPhysicalRecord` are implemented. Special internal record results are `kEof` and `kBadRecord`.

## Control Flow
`ReadRecord` skips to the first eligible block, then loops over physical records. Full records return immediately; first/middle/last fragments are appended into `scratch`; unexpected fragment types report corruption; EOF discards incomplete trailing logical records without corruption. Initial-offset resync silently skips middle/last fragments until a new full/first record. `ReadPhysicalRecord` refills 32 KiB blocks, parses headers, validates lengths, ignores zero-length preallocation records, checks CRC if enabled, and skips records beginning before the initial offset.

## State And Persistence Behavior
The reader is read-only but recovery-critical. It reports dropped bytes only when the dropped region is at or after the initial offset. It treats truncated final headers/records as EOF to tolerate writer crashes.

## Dependencies And Integration Points
It depends on `SequentialFile`, `Slice`, `Status`, log format constants, fixed coding, and crc32c. DB recovery and dump utilities use it for WAL and manifest records.

## Risks And Edge Cases
Checksum mismatch drops the rest of the buffer because length may be corrupt. Initial offset handling must avoid returning partial logical records. The "earlier writer empty first record" compatibility path suppresses false corruption for old logs.

## Test Signals
`log_test.cc` covers normal reads, fragmentation, trailers, append reopen, read errors, bad type/length/checksum, missing fragments, joining-prevention after corrupted blocks, and initial-offset positioning.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_reader.h -->
# sources/storage-engines/leveldb/db/log_reader.h

## Purpose
This header declares the WAL/manifest log `Reader` and its corruption reporting interface.

## Important APIs, Types, And Functions
`Reader::Reporter` exposes virtual `Corruption(size_t bytes, const Status& status)`. `Reader` exposes constructor, destructor, `ReadRecord(Slice* record, std::string* scratch)`, and `LastRecordOffset`. Private declarations cover initial block skipping, physical record reading, and corruption/drop reporting.

## Control Flow
The public contract states that returned record data is valid only until the next mutating reader operation or scratch mutation. The constructor accepts `checksum` and `initial_offset`, enabling recovery/dump modes and offset-based readers.

## State And Persistence Behavior
Members track file pointer, reporter, checksum flag, backing block buffer, EOF, last record offset, end-of-buffer offset, initial offset, and resync mode. These fields drive safe recovery from partial or corrupted persistent logs.

## Dependencies And Integration Points
It depends on log format constants, public `Slice`/`Status`, and forward-declared `SequentialFile`. It is used by `db_impl.cc`, `dumpfile.cc`, and log tests.

## Risks And Edge Cases
The file passed to `Reader` and reporter must outlive the reader. Incorrect scratch lifetime handling by callers can invalidate returned records. Initial-offset semantics are physical-offset based, not logical sequence based.

## Test Signals
Coverage is direct through `log_test.cc`, especially corruption reporting and offset tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_test.cc -->
# sources/storage-engines/leveldb/db/log_test.cc

## Purpose
This gtest suite validates the log writer/reader pair across normal records, fragmentation, block-boundary trailers, append mode, random data, corruption paths, and initial-offset reading.

## Important APIs, Types, And Functions
Helpers generate big/random strings and numbers. `LogTest` owns in-memory `StringDest`, `StringSource`, `ReportCollector`, `Writer`, and `Reader`. It provides `Write`, `Read`, byte mutation/truncation helpers, checksum repair, `ReopenForAppend`, forced read errors, error matching, and initial-offset helpers.

## Control Flow
Tests write records into memory, switch to reading lazily, then assert exact returned logical records or EOF. Corruption tests mutate header bytes, lengths, checksums, record types, or remove fragments and then verify returned records plus dropped-byte/error reports. Initial-offset tests construct a known multi-block log and assert which logical record is returned from many physical offsets.

## State And Persistence Behavior
No disk files are used; the in-memory dest/source models persistent log bytes. The suite validates durable format behavior: block padding, fragmentation, checksum coverage, append with existing file length, and tolerance for truncated final records.

## Dependencies And Integration Points
It depends on `log_reader`, `log_writer`, Env file interfaces, coding, crc32c, random utilities, and gtest. It protects DB recovery and manifest replay behavior.

## Risks And Edge Cases
Expected dropped byte counts are tied to exact block/header math. Some corruption paths intentionally recover later records, while truncated trailing records are ignored to model writer crashes.

## Test Signals
Failures indicate WAL format incompatibility, bad fragment assembly, false corruption reporting, missed corruption, broken append offsets, or incorrect physical-offset resync.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_writer.cc -->
# sources/storage-engines/leveldb/db/log_writer.cc

## Purpose
This file implements the physical log writer for WAL and descriptor records.

## Important APIs, Types, And Functions
`InitTypeCrc`, `Writer` constructors, destructor, `AddRecord`, and `EmitPhysicalRecord` are implemented. `type_crc_` caches CRC seeds for record-type bytes.

## Control Flow
`AddRecord` fragments a logical slice across 32 KiB blocks. If fewer than seven bytes remain in a block, it pads the trailer with zeros and starts a new block. It emits at least one physical record even for empty slices, choosing full/first/middle/last type from begin/end state. `EmitPhysicalRecord` writes a seven-byte header with masked crc32c over type+payload, little-endian length, type, then appends payload and flushes.

## State And Persistence Behavior
The writer appends to a `WritableFile` and tracks `block_offset_`. The second constructor resumes append mode from an existing file length. It flushes after every physical record but leaves durable syncing to callers such as `DBImpl::Write`.

## Dependencies And Integration Points
It depends on `WritableFile`, log format constants, fixed coding, and crc32c. It is used for DB WAL records, manifest/descriptor records, DB creation, and tests.

## Risks And Edge Cases
Record length must fit in 16 bits, guaranteed by block fragmentation. Padding relies on `kHeaderSize == 7`. Flush without sync means callers must handle durability explicitly. Append-mode offset must match actual file length.

## Test Signals
`log_test.cc` validates empty records, many records, fragmentation, marginal trailers, append reopen, random reads, and reader corruption behavior against writer output.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_writer.h -->
# sources/storage-engines/leveldb/db/log_writer.h

## Purpose
This header declares LevelDB's log `Writer`, used to append logical records to WAL and manifest files.

## Important APIs, Types, And Functions
`Writer(WritableFile* dest)`, `Writer(WritableFile* dest, uint64_t dest_length)`, destructor, and `AddRecord(const Slice& slice)` are public. Private state includes destination file, current block offset, and precomputed type CRCs. `EmitPhysicalRecord` is the private physical-fragment writer.

## Control Flow
The constructor contract distinguishes empty-file writing from appending to an existing file. `AddRecord` is the only public mutation method and handles physical fragmentation internally.

## State And Persistence Behavior
The writer does not own the destination file and requires it to remain live. It tracks block offset but does not expose sync/close; callers control durability on the underlying file.

## Dependencies And Integration Points
It includes log format, `Slice`, `Status`, and forward-declares `WritableFile`. It is consumed by `DBImpl`, DB creation, manifest writing through version code, and log tests.

## Risks And Edge Cases
Misstating `dest_length` corrupts block-boundary decisions for appended logs. Callers must not destroy or close `dest_` while the writer is active.

## Test Signals
`log_test.cc` directly covers the writer through round trips and append-mode tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/log_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/memtable.cc -->
# sources/storage-engines/leveldb/db/memtable.cc

## Purpose
This file implements the in-memory write buffer for LevelDB using an arena-backed skiplist keyed by length-prefixed internal keys.

## Important APIs, Types, And Functions
`GetLengthPrefixedSlice`, `MemTable` constructor/destructor, `ApproximateMemoryUsage`, `KeyComparator::operator()`, `EncodeKey`, anonymous `MemTableIterator`, `NewIterator`, `Add`, and `Get` are implemented.

## Control Flow
`Add` encodes an entry as varint internal-key length, user key, fixed64 sequence/type tag, varint value length, and value bytes, then inserts it into the skiplist. `Get` seeks to the lookup memtable key, verifies same user key, decodes the tag, and returns either value or a not-found status for deletion. The iterator exposes decoded internal key and value slices from skiplist nodes and supports forward/backward navigation.

## State And Persistence Behavior
Memtable state is volatile until represented in the WAL and later flushed to table files. Memory is allocated from `Arena` and freed only when reference count reaches zero. Entry encoding mirrors internal key ordering and is consumed by table building during flush.

## Dependencies And Integration Points
It depends on `dbformat`, `SkipList`, public comparator/iterator/status APIs, Env declarations, and coding helpers. `DBImpl` writes batches into memtables, reads current/immutable memtables, and flushes them through `BuildTable`.

## Risks And Edge Cases
`GetLengthPrefixedSlice` assumes entries are not corrupted and reads up to five bytes for varint length. Reference counting is manual. The comparator must compare internal keys, not raw entry pointers. `Get` relies on lookup seek skipping entries above the snapshot sequence.

## Test Signals
Coverage is indirect through DB read/write, snapshot, iterator, recovery, compaction, and randomized tests; no standalone memtable test is in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/memtable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/db/memtable.h -->
# sources/storage-engines/leveldb/db/memtable.h

## Purpose
This header declares `MemTable`, LevelDB's reference-counted mutable in-memory table for recent writes.

## Important APIs, Types, And Functions
Public methods are constructor, `Ref`, `Unref`, `ApproximateMemoryUsage`, `NewIterator`, `Add`, and `Get`. Private types include `KeyComparator` and the skiplist `Table`. The destructor is private to force deletion through `Unref`.

## Control Flow
Callers must increment references before sharing a memtable with readers/iterators/background work and call `Unref` when done. `Add` accepts explicit sequence/type/key/value; `Get` accepts a `LookupKey` built for a snapshot sequence.

## State And Persistence Behavior
Members are comparator, integer refcount, arena allocator, and skiplist. The memtable is volatile but is paired with a WAL during normal DB operation and becomes immutable before being flushed to an SSTable.

## Dependencies And Integration Points
It depends on internal key format, skiplist, public DB types, and arena. `DBImpl`, recovery, write-batch insertion, table building, and iterators use it directly.

## Risks And Edge Cases
Manual non-atomic refcounting assumes external synchronization or single-threaded ownership discipline. Iterators do not keep the memtable alive by themselves; callers must ensure lifetime. Large values increase arena memory until the whole memtable is freed.

## Test Signals
DB-level tests validate memtable behavior through reads before/after flush, immutable-layer reads, recovery, snapshots, approximate memory usage, and compactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/db/memtable.h -->
