# subset-b-008620 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/seqno_to_time_mapping.cc -->
# sources/storage-engines/rocksdb/db/seqno_to_time_mapping.cc

## Purpose

`seqno_to_time_mapping.cc` implements the sampled sequence-number to wall-clock time map declared in `seqno_to_time_mapping.h`, plus small packing helpers used by timed value paths. The mapping gives RocksDB a compact, approximate bridge from write sequence numbers to Unix seconds for time-aware tiering and retention decisions. It is intentionally lossy: entries are sampled, merged, pruned by time span, and compacted by capacity.

## Important APIs, Types, and Functions

Key implementation functions are `FindGreaterTime`, `FindGreaterEqSeqno`, `FindGreaterSeqno`, `GetProximalTimeBeforeSeqno`, `GetProximalSeqnoBeforeTime`, and `GetCurrentTieringCutoffSeqnos`. Mutating paths include `Append`, `PrePopulate`, `AddUnenforced`, `DecodeFrom`, `CopyFromSeqnoRange`, `SetMaxTimeSpan`, `SetCapacity`, and `Enforce`. `SeqnoTimePair::Merge`, `Encode`, `Decode`, `ComputeDelta`, and `ApplyDelta` define pair-level compaction and persistence encoding. `PackValueAndWriteTime`, `PackValueAndSeqno`, and the parse helpers append or strip fixed-width trailers from value slices.

## Control Flow

Reads assume `enforced_` is true and use binary search over `pairs_`. `Append` tries to merge with the newest entry, handles clock/time anomalies through `SeqnoTimePair::Merge`, sorts only after unenforced additions, then enforces time-span and non-strict capacity limits. `Enforce` sorts/merges if necessary, prunes by `max_time_span_`, and strictly reduces to configured capacity. Capacity enforcement greedily removes interior entries whose removal creates the smallest time gap, preserving the endpoints. Decode appends decoded delta entries and rolls back on corruption; if it merges with an already constrained map it leaves the object unenforced until a later enforcement pass.

## State and Persistence Behavior

Persistent representation is varint count followed by delta-encoded varint sequence/time pairs; an empty map encodes as an empty string. The map keeps one older-than-cutoff entry so queries near the retention boundary still have a lower bound. Sequence number zero and time zero are reserved unknown-before-all sentinels and are skipped or asserted around. Packed timed values persist a fixed 64-bit trailer after the user value, so callers must pass slices of at least eight bytes to parse.

## Dependencies and Integration Points

The file depends on `db/dbformat.h`, `db/version_edit.h`, and string/coding utilities. `ColumnFamilyData`, `SuperVersion`, table properties, and tiering options consume these mappings to estimate sequence cutoffs for `preserve_internal_time_seconds` and `preclude_last_level_data_seconds`. SST metadata can carry copied sequence ranges through `EncodeTo`/`DecodeFrom`.

## Risks and Test Signals

Risks center on sortedness/enforcement preconditions, off-by-one cutoff semantics, unsigned underflow in time-span pruning, corruption rollback, and fixed-trailer parsing asserts. Tests should cover duplicate seqnos, duplicate times, backward time movement, capacity zero/one, strict versus non-strict compaction, decode corruption with rollback, range copy boundary inclusion, tiering cutoff `+1`, and packed value round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/seqno_to_time_mapping.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/seqno_to_time_mapping.h -->
# sources/storage-engines/rocksdb/db/seqno_to_time_mapping.h

## Purpose

`seqno_to_time_mapping.h` declares `SeqnoToTimeMapping`, the constants controlling mapping sizes, a helper for combining time-retention options across column families, and the fixed-trailer value packing APIs used by timed writes. The header documents the central approximation: a recorded pair means the timestamp is at or after that sequence number and before the next sampled sequence number.

## Important APIs, Types, and Functions

`SeqnoToTimeMapping::SeqnoTimePair` stores a `SequenceNumber` and Unix time, supports varint encoding/decoding, delta math, sorting, equality, and merge logic. Public mapping APIs configure `SetMaxTimeSpan` and `SetCapacity`, populate or append entries, switch through unenforced additions via `AddUnenforced`, decode/copy ranges, query proximal time or sequence bounds, encode to binary properties, and format a human-readable string. `MinAndMaxPreserveSeconds` combines `preserve_internal_time_seconds` and `preclude_last_level_data_seconds` settings and computes the sampling cadence. The packing functions add or parse a write-time or sequence-number trailer on a value.

## Control Flow

The class has two logical modes. Enforced mode promises sorted entries, nominal capacity, and time-span retention for external const queries. Unenforced mode allows historical or decoded data to be appended cheaply, deferring sort/merge/prune work until `Enforce` or `Append` reestablishes invariants. Query APIs require enforced mode and return sentinel values when no lower bound is known.

## State and Persistence Behavior

The state is a `std::deque<SeqnoTimePair>` plus `max_time_span_`, `capacity_`, and `enforced_`. Constants cap mappings at 100 pairs per SST and nominally 100 per CF, with a combined upper bound of 1000 when multiple CF settings interact. The header exposes debug-only inspection for tests but otherwise keeps the deque private.

## Dependencies and Integration Points

The header depends on RocksDB `Status`, `Slice`, `SequenceNumber`, and `dbformat` definitions. It is integrated by version/table metadata, column-family superversions, and time-aware compaction/tiering logic. `MinAndMaxPreserveSeconds` is designed for scanning CF options before choosing a global sample cadence.

## Risks and Test Signals

Risks include callers querying while unenforced, mixing sentinel zero with real data, capacity/time-span settings changing while entries are present, and trailer parse calls on too-short values. Test signals should assert API preconditions in debug builds, verify cadence rounding and disabled behavior, cover range-copy semantics, and ensure all packing helpers preserve value bytes and parse the expected trailer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/seqno_to_time_mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/snapshot_checker.h -->
# sources/storage-engines/rocksdb/db/snapshot_checker.h

## Purpose

`snapshot_checker.h` defines the callback interface used by flush and compaction to decide whether an internal key version is visible to a snapshot, especially when transaction engines can make sequence-number visibility differ from simple sequence ordering. It provides default and write-prepared implementations plus helper predicates for GC decisions.

## Important APIs, Types, and Functions

`SnapshotCheckerResult` distinguishes `kInSnapshot`, `kNotInSnapshot`, and `kSnapshotReleased`. `SnapshotChecker::CheckInSnapshot(sequence, snapshot_sequence)` is the core virtual callback. `DisableGCSnapshotChecker` returns `kNotInSnapshot` and has a singleton `Instance`. Despite the inline comment saying this prevents values from being GCed, the intended integration depends on helper predicates that conservatively interpret checker results. `WritePreparedSnapshotChecker` delegates to a `WritePreparedTxnDB`. `DataIsDefinitelyInSnapshot` and `DataIsDefinitelyNotInSnapshot` are declared helpers for users that need conservative answers.

## Control Flow

Compaction-style callers pass a key sequence number and snapshot sequence into a checker. The checker returns a three-state answer so callers can avoid treating released snapshots as authoritative. Write-prepared transaction DBs use this hook to consult transaction commit/prepared state instead of relying only on sequence comparisons.

## State and Persistence Behavior

The base interface has no state. `DisableGCSnapshotChecker` is a process singleton. `WritePreparedSnapshotChecker` stores a raw const pointer to the owning transaction DB, so lifetime is external. The file does not persist anything, but it directly affects whether obsolete internal versions are removed during flush/compaction.

## Dependencies and Integration Points

The header depends on `rocksdb/types.h` for `SequenceNumber`. It is integrated by compaction iterators, flush garbage collection, and write-prepared transaction visibility code. The public shape intentionally avoids taking DB mutexes or ownership in the checker interface.

## Risks and Test Signals

Risks include reversed interpretation of `kInSnapshot`/`kNotInSnapshot`, use-after-free if the transaction DB outlives the checker incorrectly, and unsafe GC when the result is `kSnapshotReleased`. Tests should cover ordinary snapshots, released snapshots, write-prepared committed/uncommitted states, and compaction behavior with GC disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/snapshot_checker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/snapshot_impl.cc -->
# sources/storage-engines/rocksdb/db/snapshot_impl.cc

## Purpose

`snapshot_impl.cc` implements `ManagedSnapshot`, the RAII wrapper around RocksDB snapshot acquisition and release. It keeps snapshot lifetime tied to a C++ object so early returns and exceptions do not leak retained snapshots.

## Important APIs, Types, and Functions

`ManagedSnapshot::ManagedSnapshot(DB* db)` calls `db->GetSnapshot()`. The second constructor wraps an existing `const Snapshot*` with the same release semantics. `~ManagedSnapshot` calls `db_->ReleaseSnapshot(snapshot_)` when the pointer is non-null. `snapshot()` returns the wrapped raw pointer.

## Control Flow

Construction stores the DB pointer and snapshot pointer. Destruction is the only mutating step and releases through the owning DB. No ownership transfer API is provided, so callers using the explicit-snapshot constructor must only pass snapshots that should be released by this wrapper.

## State and Persistence Behavior

The wrapper stores `DB* db_` and `const Snapshot* snapshot_`. It does not persist state; it affects in-memory snapshot retention, which in turn affects compaction history retention, WAL/file cleanup, and write-conflict boundaries elsewhere.

## Dependencies and Integration Points

The file depends on public `rocksdb/db.h` and `rocksdb/snapshot.h`. It integrates with any caller that needs scoped snapshots for reads or iterators without manually pairing `GetSnapshot` and `ReleaseSnapshot`.

## Risks and Test Signals

Risks are mostly ownership-related: wrapping a snapshot that will be released elsewhere causes double release, while destroying after the DB object is gone is unsafe. Tests should check scoped release on normal destruction, null-safe behavior if construction ever permits null, and no leaked snapshot count across read paths using `ManagedSnapshot`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/snapshot_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/snapshot_impl.h -->
# sources/storage-engines/rocksdb/db/snapshot_impl.h

## Purpose

`snapshot_impl.h` defines RocksDB's internal snapshot records and snapshot containers. `SnapshotImpl` extends the public `Snapshot` interface with sequence number, Unix time, timestamp, write-conflict-boundary state, and doubly-linked-list membership. `SnapshotList` manages ordinary snapshots, while `TimestampedSnapshotList` manages timestamp-keyed shared snapshots.

## Important APIs, Types, and Functions

`SnapshotImpl` exposes `GetSequenceNumber`, `GetUnixTime`, and `GetTimestamp`. `SnapshotList::New` inserts a caller-owned `SnapshotImpl` at the newest end of a circular list. `Delete` unlinks without freeing. `GetAll` returns sorted, deduplicated snapshot sequence numbers up to `max_seq` and can return the oldest write-conflict-boundary snapshot. `GetNewest`, `GetOldestSnapshotTime`, `GetOldestSnapshotSequence`, and `count` expose list metadata. `TimestampedSnapshotList` provides `GetSnapshot`, range lookup through `GetSnapshots`, `AddSnapshot`, and `ReleaseSnapshotsOlderThan`.

## Control Flow

Ordinary snapshots are appended to the circular list in creation order and removed by pointer. `GetAll` walks oldest to newest, stops once sequence exceeds `max_seq`, deduplicates repeated sequence numbers, and records the first write-conflict boundary. Timestamped snapshots use `std::map<uint64_t, shared_ptr<const SnapshotImpl>>`; lookup with max timestamp returns the latest snapshot, while release moves old shared pointers into a caller-provided container before erasing map entries.

## State and Persistence Behavior

Snapshot state is in-memory only, but it pins sequence ranges that affect compaction, history trimming, and transaction conflict checking. `SnapshotList` uses a dummy head node initialized with debug placeholder fields. `TimestampedSnapshotList` requires DB mutex protection and keeps shared ownership so erased timestamp entries can be released outside helper code while preserving lifetime.

## Dependencies and Integration Points

The header depends on `dbformat`, public `DB`/`Snapshot`, `autovector`, and STL containers. `DBImpl`, transaction code, compaction, and timestamped snapshot APIs use these lists to collect active snapshots and retention boundaries.

## Risks and Test Signals

Risks include list corruption from unprotected concurrent access, forgetting that `Delete` does not free, duplicate timestamp insertions being ignored by `try_emplace`, and releasing timestamped snapshots without DB mutex coordination. Tests should cover insertion/removal order, duplicate sequence deduplication, max-sequence filtering, write-conflict boundary discovery, timestamp range queries, latest-timestamp lookup, and release-before-threshold behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/snapshot_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_cache.cc -->
# sources/storage-engines/rocksdb/db/table_cache.cc

## Purpose

`table_cache.cc` implements the column-family table reader cache. It opens SST files, constructs `TableReader`s through the configured table factory, caches or pins readers, serves point and batched reads, manages row-cache replay logs, exposes table properties and approximate size/offset helpers, and marks obsolete table readers.

## Important APIs, Types, and Functions

Core functions are `GetTableReader`, `FindTable`, `NewIterator`, `Get`, `MultiGetFilter`, generated sync/async `MultiGet`, `GetRangeTombstoneIterator`, `GetTableProperties`, `ApproximateKeyAnchors`, `GetMemoryUsageByTableReader`, `ApproximateOffsetOf`, `ApproximateSize`, `Evict`, `Lookup`, and `ReleaseObsolete`. Private helpers build row-cache prefixes and replay row-cache hits. `kLoadConcurency` stripes loader mutexes to limit duplicate opens.

## Control Flow

`FindTable` first honors explicitly requested ephemeral readers, then pinned file readers, then cache lookup, then serialized file open under a stripe mutex. It rechecks pinned/cache state under the mutex before opening and can pin handles into file metadata when the cache capacity indicates effectively infinite open files. `NewIterator` uses `FindTable`, applies optional table filters, registers cache-handle cleanup on iterators, wires range tombstones into an aggregator or truncated iterator, and transfers ephemeral reader ownership to iterator cleanup only after all setup succeeds. `Get` and `MultiGet` check row cache when safe, open or find the table reader, update range tombstone sequence numbers, invoke table-reader lookup, and insert replay logs back into row cache on hits.

## State and Persistence Behavior

The cache key is the file number bytes and is shared with blob cache infrastructure. Persistent data is not written here, but file open metadata can be passed to the filesystem for fast SST open and refreshed into manifest-facing metadata. Row cache entries include row-cache id, file number, and a visibility sequence discriminator so snapshot reads do not reuse unsafe entries. Obsolete release marks readers obsolete and erases cache entries after file deletion decisions elsewhere.

## Dependencies and Integration Points

Dependencies include file readers, `TableReader`, table factories, `VersionEdit` metadata, range tombstone iterators, block cache tracing, IO tracing, statistics, sync points, and coroutine macros. `VersionBuilder`, `VersionStorageInfo`, read paths, compaction iterators, and DB property APIs use this class as the shared SST access layer.

## Risks and Test Signals

Risks include leaked cache handles, double-free around ephemeral readers, no-IO reads accidentally doing I/O, stale fast-open metadata, unsafe row-cache keys for snapshot/callback reads, missed range tombstone updates, and races between pinning and cache lookup. Tests should cover cache hit/miss/open errors, `kBlockCacheTier` incomplete behavior, row cache replay, MultiGet with filters and tombstones, iterator cleanup, ephemeral-reader bypass, fast-SST metadata size limits, obsolete release, and concurrent opens of the same file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_cache.h -->
# sources/storage-engines/rocksdb/db/table_cache.h

## Purpose

`table_cache.h` declares `TableCache`, a thread-safe wrapper over cached SST `TableReader` objects and row cache access. It hides file opening, table-reader construction, cache-handle lifetime, range tombstone access, and table property helpers behind a column-family scoped API.

## Important APIs, Types, and Functions

`TableCacheOpenOptions` controls ephemeral table readers, shared metadata cache avoidance, and filter skipping. `TableCache` exposes `NewIterator`, `Get`, `GetRangeTombstoneIterator`, `MultiGetFilter`, sync/async `MultiGet`, static `Evict`/`ReleaseObsolete`/`Lookup`, `FindTable`, `GetTableProperties`, `ApproximateKeyAnchors`, memory usage, approximate offset/size, `get_cache`, `file_options`, `SetTablesAreImmortal`, `UpdateShouldPinTableHandles`, and `SetFastSstOpen`. Type aliases wrap typed cache handles for table readers and row cache strings.

## Control Flow

Most public operations resolve a `TableReader` through `FindTable`, then delegate to table-reader methods. `NewIterator` returns an `InternalIterator` whose cleanup releases any cache handle. `Get` and `MultiGet` optionally consult row cache before table I/O. Static cache helpers are used by obsolete-file cleanup paths that may not have a full `TableCache` instance.

## State and Persistence Behavior

The class stores immutable options, copied file options, typed cache interface, row-cache id, immortality/pinning flags, relaxed-atomic fast-SST-open flag, block/IO tracers, striped loader mutexes, and session id. It does not own durable SST metadata but it uses `FileMetaData` and `FileDescriptor` fields, including pinned readers and file-open metadata.

## Dependencies and Integration Points

The header depends on cache, DB format, range deletion, CF options, public env/options/table APIs, table readers, block cache tracing, and coroutine utilities. It is owned by `ColumnFamilyData`, used by read paths, compaction setup, `VersionBuilder::LoadTableHandlers`, and DB metadata/property queries.

## Risks and Test Signals

Risks include caller misuse of `open_ephemeral_table_reader` with `table_reader_ptr` or no-IO reads, stale `should_pin_table_handles_` after cache capacity changes, filter skipping changing correctness, and static cache erasure conflicting with concurrent users. Tests should cover every documented ownership contract, cache-capacity transitions, pinning behavior, range deletion iterator ownership, and both sync and coroutine MultiGet declarations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_cache_sync_and_async.h -->
# sources/storage-engines/rocksdb/db/table_cache_sync_and_async.h

## Purpose

`table_cache_sync_and_async.h` contains the macro-expanded implementation of `TableCache::MultiGet` for both ordinary and coroutine builds. It is included twice by `table_cache.cc` with different macro definitions so RocksDB can compile sync and async variants from one body.

## Important APIs, Types, and Functions

The file defines `DEFINE_SYNC_AND_ASYNC(Status, TableCache::MultiGet)` with parameters for read options, comparator, file metadata, `MultiGetContext::Range`, mutable CF options, file read histogram, filter/range-deletion skips, level, and an optional existing table handle. It uses coroutine macros `CO_AWAIT` and `CO_RETURN` when enabled.

## Control Flow

The function starts with a pinned reader or optional handle. It builds a `MultiGetRange`, checks row cache when enabled and sequence numbers are not needed, skips keys satisfied from row cache, then opens/finds the table if remaining keys need table access. It updates range tombstone sequence numbers unless disabled, delegates to `TableReader::MultiGet`, and maps `kBlockCacheTier` incomplete table-cache misses into `MarkKeyMayExist` results. After table lookup it records replay logs into row cache for keys that produced cacheable data and releases any table handle it owns.

## State and Persistence Behavior

State is transient except row-cache insertions. Replay logs are temporarily attached to each `GetContext` and are detached before insertion. Row-cache charges include string capacity plus object overhead. The function does not write SST/WAL data, but its row-cache and range-tombstone updates affect read results and performance.

## Dependencies and Integration Points

It depends on `util/coro_utils.h`, the declarations in `table_cache.h`, `GetContext`, `MultiGetContext`, row cache helpers, table readers, and range tombstone iterators. It is part of point-lookup batching used by DB read paths.

## Risks and Test Signals

Risks include row-cache entry index mismatches after skipped keys, leaked handles across coroutine suspension, replay logs left attached on errors, and inconsistent no-IO behavior versus single-key `Get`. Tests should cover all-row-cache hits, mixed hits/misses, row-cache disabled by sequence reads, range tombstone updates, filter skipping, existing handle ownership, pinned-reader use, and both sync and coroutine compilation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_cache_sync_and_async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_properties_collector.cc -->
# sources/storage-engines/rocksdb/db/table_properties_collector.cc

## Purpose

`table_properties_collector.cc` implements adapter logic between internal-key table building and user-facing table property collectors, plus helpers for reading collected delete and merge counters from user-collected properties.

## Important APIs, Types, and Functions

`UserKeyTablePropertiesCollector::InternalAdd` parses an internal key and calls the wrapped `TablePropertiesCollector::AddUserKey` with user key, entry type, sequence, value, and current file size. `BlockAdd`, `Finish`, and `GetReadableProperties` delegate to the wrapped collector. The anonymous `GetUint64Property` decodes a varint64 property and reports presence. `GetDeletedKeys` and `GetMergeOperands` read `TablePropertiesNames::kDeletedKeys` and `kMergeOperands`.

## Control Flow

During table building, internal keys are fed into `InternalAdd`; parse failures return a non-OK status and stop/poison collection. Successful parses convert internal value types to public `EntryType` before delegation. Finish-time properties are whatever the wrapped collector emits. Read helpers are defensive: absent properties return zero and `property_present=false` where applicable; malformed varints also decode to zero.

## State and Persistence Behavior

The adapter owns a `std::unique_ptr<TablePropertiesCollector>`. It writes no files directly, but its output becomes persisted user-collected table properties in SST metadata blocks. The helper functions interpret those persisted properties after tables are read.

## Dependencies and Integration Points

The file depends on `dbformat`, varint coding, string utilities, and the public table properties APIs. `ColumnFamilyData` wraps user collector factories into internal collector factories; table builders call these collectors; compaction and property APIs later inspect the emitted properties.

## Risks and Test Signals

Risks include internal-key parse errors, incorrect mapping from RocksDB value types to public entry types, silent zero on malformed varints, and user collectors assuming they receive internal rather than user keys. Tests should cover puts, deletes, single deletes, merges, malformed internal keys, malformed property values, and readable-property passthrough.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_properties_collector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_properties_collector.h -->
# sources/storage-engines/rocksdb/db/table_properties_collector.h

## Purpose

`table_properties_collector.h` declares the internal collector abstraction used by RocksDB table builders, adapters for public user-key collectors, a factory wrapper, and a timestamp min/max collector for user-defined timestamp keys.

## Important APIs, Types, and Functions

`InternalTblPropColl` defines `InternalAdd`, `BlockAdd`, `Finish`, `GetReadableProperties`, `NeedCompact`, and `Name`. `InternalTblPropCollFactory` creates collectors for a column family, level, total levels, and last-level sequence threshold. `UserKeyTablePropertiesCollector` wraps a public `TablePropertiesCollector`. `UserKeyTablePropertiesCollectorFactory` converts public factories to internal factories and fills `TablePropertiesCollectorFactory::Context`. `TimestampTablePropertiesCollector` extracts timestamps from internal keys and emits `rocksdb.timestamp_min` and `rocksdb.timestamp_max`.

## Control Flow

Table building constructs internal collectors through factories, feeds every internal key/value and block-size event into them, then calls `Finish` to populate user-collected property maps. The timestamp collector extracts the user key, validates it is long enough for the comparator timestamp size, compares timestamps through the comparator, and records min/max strings.

## State and Persistence Behavior

Collectors are per-table objects. User-collected properties become SST metadata. Timestamp collector state is two strings initialized to `kDisableUserTimestamp`; empty tables persist empty min/max. Collector factories retain shared pointers to user factories so option-owned factories remain alive.

## Dependencies and Integration Points

The header depends on `dbformat`, public comparator and table properties APIs. It is used by table builders, option sanitization, timestamp-aware compaction/read logic, and tests validating table property persistence across block-based and plain table formats.

## Risks and Test Signals

Risks include non-thread-safe factories despite the contract, timestamp comparator mismatch, short user keys causing corruption, old `Add`-only collectors needing compatibility, and `NeedCompact` propagation. Tests should cover factory context values, block callbacks, legacy collector mode, timestamp min/max with custom comparators, empty tables, and short-key corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_properties_collector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_properties_collector_test.cc -->
# sources/storage-engines/rocksdb/db/table_properties_collector_test.cc

## Purpose

`table_properties_collector_test.cc` verifies user and internal table property collectors across block-based and plain table formats, including backward-compatible collector APIs and internal key statistic collectors.

## Important APIs, Types, and Functions

The test defines `TablePropertiesTest`, `MakeBuilder`, `RegularKeysStartWithA`, `RegularKeysStartWithABackwardCompatible`, `RegularKeysStartWithAInternal`, `RegularKeysStartWithAFactory`, `FlushBlockEveryThreePolicy`, `TestCustomizedTablePropertiesCollector`, and `TestInternalKeyPropertiesCollector`. It uses `GetDeletedKeys`, `GetMergeOperands`, `ReadTableProperties`, and table builders over in-memory `StringSink`/`StringSource` files.

## Control Flow

Customized collector tests build ordered internal keys with puts, deletes, and single deletes, finish a table, read table properties back from the in-memory file, then assert custom properties and type counters. The tests run both user-key adapter and direct internal collector modes, and both modern and legacy collector callbacks. Internal-key property tests build a second key set with deletes, single delete, and merge operands, then verify built-in deleted/merge counts and sanitized user collectors where applicable.

## State and Persistence Behavior

Tables are built entirely in memory but exercise real table metadata serialization and parsing for block-based and plain table magic numbers. The custom collector records count of keys starting with `A`, entry type counts, and file-size-change observations. Sanitization wraps public collectors into internal collectors to persist compatible properties.

## Dependencies and Integration Points

The test depends on DB options, immutable/mutable CF options, table factories, block flush policy, table builders, metadata readers, internal key comparator, and RocksDB test harness. It is the direct regression suite for `table_properties_collector.{h,cc}` and related option sanitization.

## Risks and Test Signals

The file signals expected behavior for collector context fields, backwards-compatible `Add`, delete and merge property decoding, table-format parity, and file-size monotonicity. Gaps remain around timestamp collector behavior, malformed internal keys, malformed varint properties, and collector `NeedCompact` propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/table_properties_collector_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/transaction_log_impl.cc -->
# sources/storage-engines/rocksdb/db/transaction_log_impl.cc

## Purpose

`transaction_log_impl.cc` implements `TransactionLogIteratorImpl`, the public WAL iterator used to stream write batches from archived and live log files starting at a requested sequence number while enforcing sequence continuity.

## Important APIs, Types, and Functions

Implemented methods include the constructor, `OpenLogFile`, `GetBatch`, `status`, `Valid`, `RestrictedRead`, `SeekToStartSequence`, `Next`, `NextImpl`, `IsBatchExpected`, `UpdateCurrentWriteBatch`, and `OpenLogReader`. It uses `WriteBatchInternal` to parse batch contents, sequence, and count.

## Control Flow

Construction initializes reporter state and immediately seeks to the requested sequence. `OpenLogFile` tries the expected live or archive path, falling back from live to archive if needed. `SeekToStartSequence` scans records until the current batch covers the requested sequence, optionally requiring exact alignment in strict mode. `NextImpl` reads records from the current log, advances files on EOF, and returns `TryAgain` at the live tail when DB last sequence has advanced beyond what was read. If a batch sequence is not the expected next sequence after iteration has started, `UpdateCurrentWriteBatch` logs the discontinuity, rewinds to a previous file if needed, updates the target sequence, and reseeks.

## State and Persistence Behavior

The iterator owns current `WriteBatch`, `log::Reader`, scratch buffer, file index, current batch start sequence, and current last sequence. It does not write WAL data. `RestrictedRead` refuses to read past `VersionSet::LastSequence`, so the iterator does not expose incomplete future tail records.

## Dependencies and Integration Points

Dependencies include `log_reader`, `VersionSet`, filename helpers, filesystem sequential readers, immutable DB options, IO tracing, write batch internals, and logging. DB APIs that expose transaction logs construct this iterator with WAL metadata collected from live/archive logs.

## Risks and Test Signals

Risks include sequence gaps across rolled logs, WAL files moving to archive while opening, ignoring `SetContents` parse errors, off-by-one batch coverage for requested sequence inside a batch, and `TryAgain` behavior at live tail. Tests should cover archived fallback, missing first sequence strict/non-strict modes, very small/corrupt records, multi-file iteration, sequence discontinuity reseek, checksum verification, and no read beyond last sequence.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/transaction_log_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/transaction_log_impl.h -->
# sources/storage-engines/rocksdb/db/transaction_log_impl.h

## Purpose

`transaction_log_impl.h` declares the concrete WAL metadata and iterator classes behind RocksDB's transaction log API. It represents WAL files and streams `BatchResult`s from a sequence-number starting point.

## Important APIs, Types, and Functions

`WalFileImpl` implements `WalFile` with log number, type, start sequence, and byte size; `PathName` returns live or archived names with an empty base path, while callers prepend directories elsewhere. `TransactionLogIteratorImpl` implements `Valid`, `Next`, `status`, and `GetBatch`, and declares helpers for opening files/readers, restricted reading, seeking, batch continuity checking, and updating current batch state. `LogReporter` logs corruption and informational messages through RocksDB logging.

## Control Flow

The iterator is initialized with an ordered vector of WAL descriptors, DB options, env options, read options, a start sequence, and the `VersionSet` used for current last sequence. Public `Next` delegates to `NextImpl` unless status is already non-OK. `GetBatch` moves the currently owned batch to the caller, so callers must not call it when invalid.

## State and Persistence Behavior

State includes references to DB directory/options/env options, owned WAL vector, current file index, current batch and reader, scratch storage, current status, and sequence bounds. The iterator is read-only; it affects no durable WAL state. `seq_per_batch_` is present but asserted false in the constructor in this code path.

## Dependencies and Integration Points

The header depends on log reader, version set, filename helpers, DB options, env/options, public transaction log API, port utilities, and IO tracing. It is constructed by DB transaction-log retrieval APIs after WAL file discovery.

## Risks and Test Signals

Risks include dangling references to `dir`, `options`, or `VersionSet`, path-name ambiguity if `WalFileImpl::PathName` is used without directory context, moved-out batches after `GetBatch`, and unsupported `seq_per_batch_` assumptions. Tests should validate object lifetime expectations, public iterator state transitions, batch move semantics, and reporter behavior on corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/transaction_log_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/trim_history_scheduler.cc -->
# sources/storage-engines/rocksdb/db/trim_history_scheduler.cc

## Purpose

`trim_history_scheduler.cc` implements a small concurrent scheduler for column families whose flushed immutable memtable history may need trimming. It queues referenced `ColumnFamilyData` pointers and returns non-dropped CFs to callers that will invoke `MemTableList::TrimHistory`.

## Important APIs, Types, and Functions

`ScheduleWork` refs a `ColumnFamilyData`, pushes it into `cfds_`, and clears the empty flag. `TakeNextColumnFamily` pops queued CFs, updates the empty flag, skips dropped CFs while unrefing them, and returns a live CF with the scheduler's reference still held. `Empty` reads the relaxed atomic flag. `Clear` drains and unrefs all returned CFs.

## Control Flow

All queue mutations are under `checking_mutex_`. Although the header calls it FIFO, the implementation uses `cfds_.back()` and `pop_back()`, so behavior is LIFO relative to `push_back`. Dropped CFs are cleaned up internally and the loop continues until a live CF or empty queue is found.

## State and Persistence Behavior

State is an `autovector<ColumnFamilyData*>`, a mutex, and a relaxed atomic `is_empty_` used as a cheap fast-path signal. No durable data is written. Reference counts protect queued CFs across asynchronous trimming delay.

## Dependencies and Integration Points

The file depends on `column_family.h` for `Ref`, `IsDropped`, and `UnrefAndTryDelete`. DB background work that trims flushed immutable memtable history uses this scheduler alongside flush/compaction lifecycle code.

## Risks and Test Signals

Risks include FIFO/documentation mismatch, duplicate scheduling of the same CF, callers forgetting to unref returned CFs after trimming, and relaxed `Empty` being only advisory. Tests should cover dropped CF draining, reference count balance, `Clear`, concurrent schedule/take/empty calls, and ordering expectations if callers rely on FIFO.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/trim_history_scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/trim_history_scheduler.h -->
# sources/storage-engines/rocksdb/db/trim_history_scheduler.h

## Purpose

`trim_history_scheduler.h` declares `TrimHistoryScheduler`, a thread-safe work queue for column families that may need flushed immutable memtable history trimming.

## Important APIs, Types, and Functions

The public API is `ScheduleWork(ColumnFamilyData*)`, `TakeNextColumnFamily()`, `Empty()`, and `Clear()`. The scheduler holds an atomic empty flag, an `autovector` of `ColumnFamilyData*`, and a mutex named `checking_mutex_`.

## Control Flow

Producers call `ScheduleWork` when a CF needs history trimming. Consumers call `TakeNextColumnFamily` and are responsible for invoking the trim operation and releasing the scheduler-held reference. `Empty` is a lightweight check suitable for avoiding unnecessary scheduler work, while `Clear` drains the queue during shutdown.

## State and Persistence Behavior

The scheduler state is memory-only. Its important persistence-adjacent effect is delaying or enabling removal of flushed memtable history, which can affect how much history remains available for reads, snapshots, or timestamp retention before later flush/compaction work.

## Dependencies and Integration Points

The header forward-declares `ColumnFamilyData` and depends on `autovector`, mutex, and atomic support. It integrates with DB background scheduling and memtable-list trimming.

## Risks and Test Signals

Risks include the stated FIFO contract diverging from vector back-pop implementation, unsafely interpreting relaxed `Empty` as a hard guarantee, and unclear ownership if callers do not know returned CFs are still referenced. Tests should check thread-safe draining, shutdown clear, duplicate entries, and dropped-CF cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/trim_history_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_builder.cc -->
# sources/storage-engines/rocksdb/db/version_builder.cc

## Purpose

`version_builder.cc` implements `VersionBuilder`, the accumulator that applies a sequence of `VersionEdit`s to a base `VersionStorageInfo` and materializes a new storage view without constructing full intermediate versions. It handles SST additions/deletions, blob-file metadata deltas, compact cursors, consistency checks, table-reader preloading, point-in-time recovery tracking, savepoints, and base-version lifetime management.

## Important APIs, Types, and Functions

Most behavior lives in `VersionBuilder::Rep`. Comparators sort L0 by newest sequence or epoch and non-L0 by smallest key. `LevelState` tracks deleted and newly added files per level. `BlobFileMetaDataDelta` and `MutableBlobFileMetaData` accumulate garbage and SST link changes. Important methods include `Apply`, `ApplyFileAddition`, `ApplyFileDeletion`, `ApplyBlobFileAddition`, `ApplyBlobFileGarbage`, `SaveTo`, `SaveSSTFilesTo`, `SaveBlobFilesTo`, `CheckConsistencyDetails`, `ValidVersionAvailable`, `OnlyMissingL0Suffix`, `LoadTableHandlers`, and savepoint wrappers. `BaseReferencedVersionBuilder` refs/unrefs the base version around builder use.

## Control Flow

`Apply` first checks base consistency, processes blob additions and garbage, then table deletions, table additions, and compact cursors. Table-file level tracking prevents adding an already-live file or deleting from the wrong level. Deleting an added file unrefs its temporary metadata and may record intermediate files for cleanup in point-in-time mode. Saving merges base files with unordered additions, filters deletions and missing L0 files, sorts by the level's required comparator, merges blob metadata from base and mutable state, writes compact cursors, and reruns consistency checks. `LoadTableHandlers` opportunistically opens newly added files subject to cache capacity and initial-load limits.

## State and Persistence Behavior

The builder owns temporary `FileMetaData` refs for added files and releases pinned table readers/cache reservations when refs drop to zero. It does not write MANIFEST records itself; it consumes edits already decoded from MANIFEST/WAL-like metadata and populates `VersionStorageInfo`. Blob metadata deleters mark obsolete blob files in `VersionSet` and evict blob cache entries. Point-in-time mode tracks found, missing L0/non-L0 SSTs, missing blob files, atomic-group edits, and intermediate files so recovery can accept a complete version or, when configured, an older valid view missing only an L0 suffix and associated blobs.

## Dependencies and Integration Points

Dependencies include blob metadata/cache, cache reservation manager, table cache, internal stats, version edit/handler/set/storage, version utilities, sync points, and string utilities. The class is used by manifest application, DB open/recovery, secondary/tailing version handling, and table-reader warmup. It cooperates with `ColumnFamilyData` for options, table cache, blob cache, and file metadata cache reservations.

## Risks and Test Signals

Risks are high: refcount imbalance can leak or prematurely free file metadata/readers; level/order checks must preserve L0 epoch and non-L0 non-overlap invariants; blob-to-SST links must remain bidirectionally consistent; memory reservation failure must unwind added metadata; incomplete-version recovery must not expose non-suffix missing data; and invalid levels during `num_levels` shrink must cancel out. Tests should cover add/delete reorderings, duplicate file numbers, wrong-level deletes, L0 ordering with and without epoch numbers, non-L0 overlap corruption, blob garbage overflow, link consistency, missing-file PIT recovery, savepoint copy/ref behavior, cache-reservation limits, table handler load limits, and obsolete blob cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_builder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_builder.h -->
# sources/storage-engines/rocksdb/db/version_builder.h

## Purpose

`version_builder.h` declares the version-building abstraction used to apply manifest edits to a base RocksDB version efficiently. It exposes normal builder operations, point-in-time recovery helpers, savepoint support, table-handler loading, and an RAII wrapper that keeps the base `Version` referenced while the builder is alive.

## Important APIs, Types, and Functions

`VersionBuilder` is constructed from file options, immutable CF options, table cache, base storage, version set, optional file metadata cache reservation manager, optional `ColumnFamilyData`, optional `VersionEditHandler`, and flags for found/missing file tracking and incomplete-version acceptance. Public methods include `CheckConsistencyForNumLevels`, `Apply`, `SaveTo`, `LoadTableHandlers`, `CreateOrReplaceSavePoint`, `ValidVersionAvailable`, `HasMissingFiles`, `GetAndClearIntermediateFiles`, `ClearFoundFiles`, `SaveSavePointTo`, `LoadSavePointTableHandlers`, and `ClearSavePoint`. `BaseReferencedVersionBuilder` has constructors for current or explicit base versions and exposes `version_builder()`.

## Control Flow

Callers typically create a builder with a referenced base version, call `Apply` for one or more edits, optionally validate availability in point-in-time mode, load table handlers for new files, and `SaveTo` a destination `VersionStorageInfo`. Savepoints move the current `Rep` into `savepoint_` and continue from a copied representation, enabling callers to preserve an earlier valid state while applying more edits.

## State and Persistence Behavior

The header hides implementation state behind `class Rep`. Persistent effects are indirect: saved storage later becomes the in-memory representation of MANIFEST state; table-handler loading may open SSTs and pin readers; PIT helpers track missing/intermediate file names for recovery cleanup. The wrapper's destructor unrefs the base version and therefore can trigger cleanup of old version resources.

## Dependencies and Integration Points

Dependencies include `version_edit`, file system options, metadata, slice transforms, `TableCache`, `VersionStorageInfo`, `VersionSet`, `VersionEditHandler`, `ColumnFamilyData`, and cache reservation management. Manifest readers, DB open, recovery, and secondary instance tailing use this interface.

## Risks and Test Signals

Risks include using the builder after the base version/storage has been destroyed, calling PIT-only APIs when tracking is disabled, saving a savepoint that is invalid or missing, and forgetting the DB mutex requirement around `BaseReferencedVersionBuilder`. Tests should cover constructor variants, repeated savepoint replacement, invalid savepoint status, current-version ref/unref balance, incomplete-version flags, and table-handler loading through savepoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_builder.h -->
