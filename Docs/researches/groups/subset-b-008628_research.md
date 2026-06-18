# Research: subset-b-008628

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_serialization_test.cc -->
# sources/storage-engines/rocksdb/db/wide/wide_column_serialization_test.cc

Purpose: This is the main unit-test coverage for RocksDB wide-column serialization. It exercises `WideColumn`, `WideColumnSerialization`, V1/V2 entity encodings, blob-column references, V2 fallback behavior in `PinnableWideColumns`, default-column lookup, resolved-entity serialization, and randomized round trips.

Important APIs/types/functions: `WideColumnSerializationTest` exposes friend-access wrappers for private `GetVersion` and `SerializeResolvedEntity`. Local helpers build `BlobIndex` values, convert string pairs to `WideColumns`, serialize and deserialize V2 entities, verify default-column extraction, and generate random blob indexes. Tests cover `Serialize`, `Deserialize`, `SerializeV2`, `DeserializeV2`, `HasBlobColumns`, `GetValueOfDefaultColumn`, `ResolveEntityForMerge`, and `BlobIndex::EncodeTo`.

Control flow: The tests start with construction and V1 serialize/deserialize, then drive corrupt input paths by incrementally appending malformed V1/V2 buffers. V2 tests manually construct binary layouts, verify out-of-order and recursive entity rejection, serialize inline/blob column mixes, deserialize them through V2-specific APIs, and check when generic `Deserialize` must reject unresolved blob references with `NotSupported`. Randomized tests generate sorted unique column names and values, randomly mark columns as blob-backed, then assert V2 metadata, blob-index round trip, optional V1 compatibility, and the Slice-based overload behavior.

State and persistence behavior: The file models wide-column entities as serialized bytes stored in write batches, memtables, or SST/blob layers. It checks binary format version persistence, column order invariants, blob-reference metadata preservation, and resolved entity downgrade to V1 once blob values are fetched. `PinnableWideColumnsFallbacksToV2` verifies persisted V2 bytes can populate the column index while tracking unresolved blob columns.

Dependencies and integration points: It depends on `db/wide/wide_column_serialization.h`, `db/wide/wide_columns_helper.h`, `db/blob/blob_index.h`, `rocksdb/wide_columns.h`, `util/coding.h`, and RocksDB test harness/random utilities. It is tightly coupled to the serialized V2 layout consumed by write batches, merge resolution, blob reads, and `PinnableWideColumns`.

Risks: Tests rely on hand-built buffers matching exact layout order; layout changes require coordinated updates. Randomized tests seed from wall-clock time, so failures need the printed scoped trace seed for reproduction. Inlined TTL blob indexes are avoided in one helper because their slices can dangle after local encoded storage is destroyed.

Test signals: Strong coverage exists for valid/invalid V1 and V2 parsing, duplicate/out-of-order columns, unsupported recursive value types, blob references, default-column fast paths, encode/decode round trips, and null blob fetcher error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_serialization_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_test_util.h -->
# sources/storage-engines/rocksdb/db/wide/wide_column_test_util.h

Purpose: This header provides small inline helpers shared by wide-column and blob integration tests. It centralizes generation of predictable inline/blob-sized values and option presets for blob-file and blob-direct-write scenarios.

Important APIs/types/functions: `GenerateLargeValue(size, fill_char)` returns a repeated-character string intended to exceed blob thresholds. `GenerateSmallValue()` returns `"small"`. `GetOptionsForBlobTest(default_options)` copies caller defaults, enables blob files, sets `min_blob_size = 10`, creates DBs if missing, and disables automatic compactions. `GetBlobDirectWriteCompatibleOptions(default_options)` disables concurrent memtable writes. `GetDirectWriteOptions(default_options)` enables blob files, blob direct write, sets `min_blob_size = 32`, and uses one direct-write partition.

Control flow: All helpers are inline and side-effect-free except for mutating a local `Options` copy. The blob-test path preserves fixture-specific defaults such as custom environments, then layers blob settings. The direct-write path first applies compatibility constraints before enabling direct-write-specific knobs.

State and persistence behavior: These helpers influence where test values persist: small values generally remain inline in LSM data, while values above `min_blob_size` become blob-backed when blob files/direct write are enabled. Disabling auto compaction makes flush/compaction timing deterministic for tests.

Dependencies and integration points: The file depends only on `<string>` and `rocksdb/options.h`, and lives under `wide_column_test_util` in `ROCKSDB_NAMESPACE`. It integrates with DB test fixtures that need blob extraction or direct write without duplicating option setup.

Risks: The "large" and "small" classifications are threshold-dependent; callers changing `min_blob_size` can invalidate assumptions. Direct write requires `allow_concurrent_memtable_write = false`, so tests using these options do not cover the concurrent memtable path.

Test signals: This is a utility header without its own tests, but its consumers validate blob-backed wide-column behavior. Its deterministic defaults are themselves a test signal: small thresholds force blob extraction with compact fixture data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_column_test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns.cc -->
# sources/storage-engines/rocksdb/db/wide/wide_columns.cc

Purpose: This file defines the global default wide-column name, an empty wide-column vector, and the non-inline `PinnableWideColumns::CreateIndexForWideColumns()` implementation that interprets pinned serialized wide-column bytes.

Important APIs/types/functions: It defines `kDefaultWideColumnName` as the empty `Slice`, `kNoWideColumns` as an empty `WideColumns`, and `PinnableWideColumns::CreateIndexForWideColumns()`. The function populates `columns_` and `unresolved_blob_column_indices_` from the currently pinned `value_`.

Control flow: `CreateIndexForWideColumns()` clears any previous index, attempts V1/generic `WideColumnSerialization::Deserialize`, and returns its status unless it is `NotSupported`. A `NotSupported` status can mean V2 bytes contain blob references after partially filling `columns_`; the method clears the partial result, resets the input slice, calls `DeserializeV2`, and records only the indexes of blob-backed columns in `unresolved_blob_column_indices_`.

State and persistence behavior: `PinnableWideColumns` keeps the serialized bytes in `value_` and builds column slices pointing into that storage. The unresolved blob index vector is transient state identifying which column values still require blob fetching; it does not resolve or persist blob contents. Clearing partial V1 results before V2 fallback prevents stale or mixed indexing state.

Dependencies and integration points: The file depends on `rocksdb/wide_columns.h`, `db/blob/blob_index.h`, and `db/wide/wide_column_serialization.h`. It integrates read paths that return `PinnableWideColumns`, V2 serialization with blob references, and callers checking `has_unresolved_blob_columns()`.

Risks: Correctness depends on V1 `Deserialize` returning `NotSupported` for V2 blob references and on `DeserializeV2` requiring an empty output vector. Any new V2 unsupported condition must be distinguished from blob-reference fallback. Slices in `columns_` remain valid only while `value_` backing storage remains valid.

Test signals: `wide_column_serialization_test.cc` directly tests fallback through `PinnableWideColumnsFallbacksToV2` and blob-reference rejection via generic deserialize/default-column APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns_helper.cc -->
# sources/storage-engines/rocksdb/db/wide/wide_columns_helper.cc

Purpose: This file implements stream/debug helpers for wide columns. It turns `WideColumns` or serialized wide-column values into human-readable column dumps used by tests and diagnostics.

Important APIs/types/functions: `WideColumnsHelper::DumpWideColumns(columns, os, hex)` streams columns separated by spaces and optionally switches the stream to hex formatting. `DumpSliceAsWideColumns(value, os, hex)` deserializes a serialized wide-column entity and dumps it only when deserialization succeeds.

Control flow: `DumpWideColumns` returns immediately for empty vectors, saves the original stream flags, applies `std::hex` when requested, writes the first column without a leading separator, then writes remaining columns prefixed with one space, and restores the original flags. `DumpSliceAsWideColumns` copies the input slice, calls `WideColumnSerialization::Deserialize`, and delegates to `DumpWideColumns` on success.

State and persistence behavior: No persistent state is modified. The only mutable state is the stream's formatting flags, which are restored to avoid leaking hex formatting to caller code. `DumpSliceAsWideColumns` consumes only a slice copy, preserving the caller's original slice.

Dependencies and integration points: It depends on `db/wide/wide_columns_helper.h`, `<ios>`, and `db/wide/wide_column_serialization.h`. It is used by write-batch tests to render `PutEntity` records and by helper tests to verify string output.

Risks: This helper uses the generic `Deserialize` path, so serialized V2 entities with unresolved blob references can return `NotSupported` and produce no dump. It assumes `operator<<` for `WideColumn` provides stable `name:value` formatting.

Test signals: `wide_columns_helper_test.cc` verifies plain dumping and serialized-slice dumping for two columns, including separator behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns_helper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns_helper.h -->
# sources/storage-engines/rocksdb/db/wide/wide_columns_helper.h

Purpose: This header declares formatting and lookup helpers for sorted RocksDB wide-column vectors. It is a small utility layer over `WideColumns` used by serialization, write-batch, and merge code.

Important APIs/types/functions: Public static APIs include `DumpWideColumns`, `DumpSliceAsWideColumns`, `HasDefaultColumn`, `HasDefaultColumnOnly`, `GetDefaultColumn`, `SortColumns`, and templated `Find`. `kDefaultWideColumnName` is the expected empty-name first column. `Find` accepts iterator ranges and a `Slice` column name.

Control flow: Default-column helpers check that the vector is non-empty and that the front column has the empty default name; `GetDefaultColumn` asserts that precondition. `SortColumns` orders columns lexicographically by name. `Find` asserts the range is already sorted, uses `std::lower_bound` by column name, and returns `end` when the exact name is absent.

State and persistence behavior: The header mutates only vectors passed to `SortColumns`. It does not own backing storage; all `WideColumn` slices continue to depend on the original string/pinned buffers.

Dependencies and integration points: It includes `<algorithm>`, `<cassert>`, `<ostream>`, `rocksdb/rocksdb_namespace.h`, and `rocksdb/wide_columns.h`. It integrates with `WideColumnSerialization` validation, merge logic that distinguishes plain default-only entities from true wide entities, and test dump rendering.

Risks: `Find` relies on debug-only sorted assertions; release builds can silently produce wrong results on unsorted inputs. `GetDefaultColumn` is assertion-only guarded, so callers must prove default-column presence. Sorting columns with slices whose backing storage is unstable can still leave dangling references.

Test signals: Serialization tests exercise `Find`, default-column paths, and sorted-column invariants. Helper tests cover dump behavior, while merge/write-batch code indirectly covers `HasDefaultColumnOnly`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns_helper_test.cc -->
# sources/storage-engines/rocksdb/db/wide/wide_columns_helper_test.cc

Purpose: This file contains focused unit tests for `WideColumnsHelper` output behavior. It verifies direct vector dumping and serialized-slice dumping.

Important APIs/types/functions: Tests call `WideColumnsHelper::DumpWideColumns`, `WideColumnSerialization::Serialize`, and `WideColumnsHelper::DumpSliceAsWideColumns`. The test harness is standard RocksDB gtest with a local `main`.

Control flow: `DumpWideColumns` constructs two columns, dumps them with `hex = false`, and compares against `"foo:bar hello:world"`. `DumpSliceAsWideColumns` serializes the same two-column vector, wraps output in `Slice`, dumps through deserialization, and asserts the same text.

State and persistence behavior: The tests create ephemeral vectors and serialized strings only. They confirm helper code does not require DB state, memtables, or blob files. The serialized-slice test validates that deserialization does not mutate the original string, only the local slice copy.

Dependencies and integration points: The file depends on `db/wide/wide_columns_helper.h`, `db/wide/wide_column_serialization.h`, `test_util/testharness.h`, and `util/coding.h`. It supports diagnostic behavior used by write-batch tests.

Risks: Coverage is narrow: empty columns, hex output, malformed serialized bytes, and V2 blob-reference entities are not tested here. Those areas are covered more broadly by serialization tests, but not by this helper-specific file.

Test signals: The expected strings lock down separator and `name:value` formatting for non-hex output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/wide/wide_columns_helper_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch.cc -->
# sources/storage-engines/rocksdb/db/write_batch.cc

Purpose: This is the core implementation of RocksDB `WriteBatch`. It owns the compact serialized batch format, public mutation APIs, record iteration, savepoints, optional per-key protection checksums, timestamp updates, write-batch append logic, and insertion of batch records into memtables during normal writes and WAL recovery.

Important APIs/types/functions: Major units include `WriteBatch` constructors/copy/move/clear/release, content queries (`HasPut`, `HasMerge`, etc.), `ReadRecordFromWriteBatch`, `WriteBatchInternal::Iterate`, mutation APIs for `Put`, `TimedPut`, `PutEntity`, `Delete`, `SingleDelete`, `DeleteRange`, `Merge`, `PutBlobIndex`, transaction markers, `SetSavePoint`/`RollbackToSavePoint`/`PopSavePoint`, `UpdateTimestamps`, `VerifyChecksum`, `MemTableInserter`, `WriteBatchInternal::InsertInto`, `Append`, `SetContents`, and `UpdateProtectionInfo`.

Control flow: A batch is a 12-byte header followed by tagged records. Mutators validate key/value sizes, install a `LocalSavePoint`, increment the count, append the tag and length-prefixed fields, set content flags, add protection info when enabled, and commit or roll back if `max_bytes_` is exceeded. `Iterate` decodes records with `ReadRecordFromWriteBatch`, dispatches to `Handler` callbacks, honors `Continue`, handles transaction markers and `TryAgain`, and verifies decoded write count for whole-batch scans.

State and persistence behavior: `rep_` is the persisted serialized batch body used for WAL and replay. The header stores starting sequence and count. `content_flags_` can be eagerly updated or lazily recomputed for externally supplied contents. `save_points_` records byte size, count, and flags for rollback. `prot_info_` stores checksum/protection entries per counted write. Timestamp-enabled column families append placeholder timestamps and later mutate keys in place through `TimestampUpdater`.

Memtable integration: `MemTableInserter` implements `WriteBatch::Handler` to turn records into memtable entries. It resolves column families, skips already-applied WAL updates by log number, schedules flush/trim work, advances sequence numbers per key or per batch, rebuilds prepared transactions during recovery, handles commit/rollback markers, collapses excessive merges when possible, validates range tombstones, and propagates protection info to memtable key/value/sequence checksums.

Dependencies and integration points: This file integrates with column families, `DBImpl`, memtables, flush and trim schedulers, snapshots, merge operators, wide-column serialization, blob indexes, write thread groups, transaction recovery, duplicate detection, and checksum utilities.

Risks: The serialized tag format is compatibility-sensitive. Count/header mismatches are corruption. Savepoint and protection-info counts must stay aligned. `TryAgain` paths assume retry semantics and manually decrement protection indexes. Timestamp in-place mutation depends on correct per-CF timestamp-size discovery. Recovery paths require DB mutex discipline and correct write policy settings. Wide-column V2 entities must be preserved byte-for-byte when handlers rebuild batches.

Test signals: `write_batch_test.cc` covers serialization, append, savepoints, content flags, handler continuation, column families, wide-column entities, large size limits, timestamp APIs, and transaction markers. Broader DB tests cover memtable insertion and recovery behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch_base.cc -->
# sources/storage-engines/rocksdb/db/write_batch_base.cc

Purpose: This file provides default `SliceParts` implementations for `WriteBatchBase` mutation APIs. It lets derived classes implement Slice-based methods while still supporting gathered/scattered key and value inputs.

Important APIs/types/functions: Implemented methods are `Put`, `Delete`, `SingleDelete`, `DeleteRange`, and `Merge` overloads taking `SliceParts`, both with and without `ColumnFamilyHandle*`.

Control flow: Each method materializes `SliceParts` into contiguous `std::string` buffers through `Slice(parts, &buffer)`, then delegates to the corresponding `Slice` overload. Delete methods only materialize keys; range delete materializes begin and end keys; put/merge materialize both key and value.

State and persistence behavior: This layer has no persistent state. It may allocate temporary strings to join parts, and the resulting `Slice` remains valid only for the duration of the delegated call. The derived class owns all actual write-batch persistence.

Dependencies and integration points: It depends on `rocksdb/write_batch_base.h`, `rocksdb/slice.h`, and `rocksdb/status.h`. It is used by `WriteBatch`, `WriteBatchWithIndex`, and any other `WriteBatchBase` subclass that does not provide a more efficient gathered-write implementation.

Risks: The fallback copies input parts, so high-throughput callers may prefer specialized overrides. It relies on delegated Slice overloads to enforce size limits, timestamp restrictions, column-family validation, memory limits, and content-flag/protection updates.

Test signals: `write_batch_test.cc` covers gathered `Put` through `PutGatherSlices`; other gathered overloads are indirectly covered by subclasses and API consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch_base.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch_internal.h -->
# sources/storage-engines/rocksdb/db/write_batch_internal.h

Purpose: This internal header exposes RocksDB-private controls for manipulating `WriteBatch` serialized contents, column-family memtable lookup, memtable insertion, timestamp updates, transaction markers, append, and protection information.

Important APIs/types/functions: `ColumnFamilyMemTables` is the abstract lookup interface used during insertion, with `ColumnFamilyMemTablesDefault` for default-CF-only insertion. `WriteBatch::ProtectionInfo` stores `ProtectionInfoKVOC64` entries. `WriteBatchInternal` declares internal mutation APIs by column-family ID, transaction marker helpers, header accessors (`Count`, `SetCount`, `Sequence`, `SetSequence`), `Contents`, `ByteSize`, `SetContents`, `InsertInto` overloads, `Append`, `Iterate`, timestamp flags, and `UpdateProtectionInfo`. `LocalSavePoint` is an RAII rollback helper. `TimestampUpdater` is a templated `WriteBatch::Handler` for in-place timestamp replacement.

Control flow: Public `WriteBatch` APIs resolve handles to CF IDs and timestamp sizes, then call `WriteBatchInternal` methods. Insertion overloads route a single batch, writer, or write group into memtables. `LocalSavePoint::commit()` checks `max_bytes_` and rolls back serialized bytes, count, protection entries, and flags on memory-limit failure. `TimestampUpdater` iterates records and rewrites trailing timestamp bytes based on a supplied CF-to-size function.

State and persistence behavior: The header defines the 12-byte batch header contract and grants access to private `WriteBatch` fields. Protection info is a parallel per-counted-write structure and must match `Count()`. Timestamp updates mutate serialized keys in place and update protection info when present.

Dependencies and integration points: It includes flush and trim schedulers, write thread, RocksDB DB/options/types/write batch APIs, checksum utilities, `autovector`, and cast helpers. It is consumed by `write_batch.cc`, DB write/recovery paths, tests, transactions, and write-batch-with-index code.

Risks: These APIs bypass public invariants and must keep serialized bytes, count, content flags, timestamp metadata, and protection info synchronized. `TimestampUpdater` returns `NotFound` for unknown CF timestamp sizes and `InvalidArgument` for size mismatches. `LocalSavePoint` asserts commit in debug builds, so internal mutators must call `commit()`.

Test signals: Write-batch tests directly exercise header accessors, append, internal markers, serialized V2 entity preservation, timestamps, savepoints, and insertion into test memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch_test.cc -->
# sources/storage-engines/rocksdb/db/write_batch_test.cc

Purpose: This unit-test file validates the `WriteBatch` serialized format, mutation APIs, handler iteration, memtable insertion semantics, column-family records, savepoints, wide-column entities, large-size boundaries, timestamp handling, and transaction marker callbacks.

Important APIs/types/functions: `PrintContents` inserts a batch into a temporary memtable and renders internal keys. `TestHandler` records callback events for all major tags. `ReplayUntilCountHandler` exercises `Continue()` while buffering prepared batches. `ColumnFamilyHandleImplDummy` supplies test CF IDs/comparators. `TimestampChecker` verifies trailing user-key timestamps.

Control flow: Tests build batches through public and internal APIs, set sequences, iterate through handlers, insert into memtables, and compare deterministic rendered strings. Append tests validate empty, non-empty, and WAL-termination append behavior. Prepared transaction tests use a leading noop rewritten by `MarkEndPrepare`. Continuation tests stop mid-batch and inside committed prepared replay. Column-family tests verify CF-tagged operations and `WriteBatchWithIndex` ordering. Timestamp tests create CFs with and without timestamp comparators, then update in-place.

State and persistence behavior: The tests inspect serialized batch effects through memtable state and handler callbacks. They validate count increments, sequence assignment, savepoint rollback restoring bytes/count/flags, memory limit rollback, `Release()` ownership transfer, WAL-only termination truncation, and preservation of serialized V2 wide-column entities without deserialize/re-serialize loss.

Dependencies and integration points: The file depends on blob indexes, column-family internals, DB test utilities, memtables, wide-column serialization/helper code, `WriteBatchInternal`, comparators, environments, write-batch-with-index, write buffer manager, and test utilities.

Risks: Some stress tests are disabled due to very high memory requirements. `PrintContents` is a test-only approximation of insertion behavior using a temporary default-CF memtable; full DB write/recovery behavior is covered elsewhere. String-order expectations depend on memtable internal ordering and sequence ordering.

Test signals: Coverage is broad for basic operations, corruption, append, log data, unsupported handler defaults, merge-operator requirements, gathered slices, attribute groups, serialized V2 entity rebuilding, CF-specific records, savepoints, memory limits, timestamp sanity/update, and commit-with-timestamp markers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_batch_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_callback.h -->
# sources/storage-engines/rocksdb/db/write_callback.h

Purpose: This header defines the internal `WriteCallback` interface used by DB write paths to run caller-provided validation or side effects on the write thread before a write executes.

Important APIs/types/functions: `WriteCallback` has a virtual destructor, pure virtual `Status Callback(DB* db)`, and pure virtual `bool AllowWriteBatching()`. `DB` is forward-declared to avoid including the full DB interface.

Control flow: DB write code attaches a callback to a `WriteThread::Writer`. Before execution, the write thread invokes `Callback`; a non-OK status aborts that writer's write and is returned to the caller. `AllowWriteBatching()` tells write-thread grouping whether this callback can be batched with other writes.

State and persistence behavior: The interface owns no state. Implementations may hold state such as "was called" flags or validation options. A failing callback prevents WAL/memtable persistence for that write.

Dependencies and integration points: It depends on `rocksdb/status.h` and integrates with `DBImpl::WriteWithCallback`, `WriteThread::Writer`, write grouping, background error reporting for callback failures, and tests in `write_callback_test.cc`.

Risks: Callbacks run on the write path, so expensive or blocking implementations can stall writers. Returning incorrect batching permission can break ordering assumptions or reduce throughput. Callback implementations must tolerate being invoked under write-thread synchronization constraints.

Test signals: `write_callback_test.cc` verifies callback invocation, abort semantics, batching policy behavior across write configurations, and interaction with `UserWriteCallback`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_callback_test.cc -->
# sources/storage-engines/rocksdb/db/write_callback_test.cc

Purpose: This file tests RocksDB write callbacks and user write callbacks across many write-thread configurations. It verifies that internal callbacks can accept or reject writes, influence batching, and coexist with public enqueue/WAL-finish notifications.

Important APIs/types/functions: Test fixtures define `WriteCallbackTestWriteCallback1`, `WriteCallbackTestWriteCallback2`, `MockWriteCallback`, and `MockUserWriteCallback`. `WriteCallbackPTest` parameterizes unordered writes, sequence-per-batch, two write queues, concurrent memtable writes, callback batching permission, WAL enablement, and pipelined writes.

Control flow: The parameterized test builds scenarios of successful/failing write operations, opens `DBImpl` with matching options, uses sync points inside `WriteThread::JoinBatchGroup` to inspect leader/follower states, launches multiple writer threads, and verifies callback status, user callback notifications, persisted keys, and visible sequence numbers. Unsupported option combinations are skipped. A simpler fixture test checks plain `DB::Write`, successful `WriteWithCallback`, failing `WriteWithCallback`, and public `DB::WriteWithCallback` using `UserWriteCallback`.

State and persistence behavior: Successful callback writes persist their batched keys and advance visible sequence numbers; failing callbacks return `Busy`, do not persist keys, and do not fire WAL-finish notifications. `OnWriteEnqueued` fires after the writer is linked/enqueued. `OnWalWriteFinish` fires only when WAL is enabled and the write succeeds.

Dependencies and integration points: The file depends on `db/write_callback.h`, `DBImpl`, `WriteThread` sync points, public `rocksdb/db.h`, `rocksdb/user_write_callback.h`, write batches, threading, random data generation, and per-thread DB paths.

Risks: The parameterized matrix is concurrency-sensitive and uses busy waits plus sync points to force ordering. Adding write-thread states or unsupported option combinations requires test updates. The test invokes callbacks with `nullptr` inside sync-point verification to infer success/failure, so mock callbacks must tolerate null DBs.

Test signals: Strong signals cover write-group leadership, no-batching mode, pipelined/two-queue exclusions, WAL vs no-WAL user callback timing, callback failure abort, key visibility, and sequence accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_callback_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_controller.cc -->
# sources/storage-engines/rocksdb/db/write_controller.cc

Purpose: This file implements write-stall and write-delay control. It provides RAII token creation/destruction and a byte-credit delay algorithm used when compaction pressure requires throttling writes.

Important APIs/types/functions: Implemented methods are `GetStopToken`, `GetDelayToken`, `GetCompactionPressureToken`, `IsStopped`, `GetDelay`, `NowMicrosMonotonic`, and destructors for `StopWriteToken`, `DelayWriteToken`, and `CompactionPressureToken`.

Control flow: Token creation increments the corresponding atomic counter and returns a token whose destructor decrements it. Starting the first delay token resets `next_refill_time_` and `credit_in_bytes_`, then clamps the requested delayed write rate. `GetDelay` returns zero if stopped or not delayed, spends available byte credit if possible, refills credit every 1ms based on elapsed monotonic time and delayed rate, and otherwise computes a sleep duration sufficient to bring the write back under budget with a minimum 1ms delay.

State and persistence behavior: The controller is in-memory DB state. Counters represent active reasons to stop, delay, or speed up compaction. Delay state consists of `credit_in_bytes_`, `next_refill_time_`, and `delayed_write_rate_`. No data is persisted, but the state directly gates write throughput.

Dependencies and integration points: It depends on `db/write_controller.h` and `rocksdb/system_clock.h`. It is used by DB/column-family write stall management, compaction pressure logic, and callers that hold the DB mutex before token operations and delay calculation.

Risks: Comments require DB mutex for all methods including token destruction, but counters are atomic and some loads are relaxed; misuse outside the mutex can still race on non-atomic credit/refill fields. The delay algorithm assumes the caller sleeps for the returned duration. Changing rates while debt exists applies the new rate only to later calculations.

Test signals: No direct test file is in this work item, so coverage is likely through DB write-stall tests elsewhere. Assertions guard token underflow in destructors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_controller.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_controller.h -->
# sources/storage-engines/rocksdb/db/write_controller.h

Purpose: This header declares `WriteController`, RocksDB's write-stall coordinator for stop, delay, and compaction-pressure states, plus RAII token classes that release pressure when destroyed.

Important APIs/types/functions: `WriteController` exposes `GetStopToken`, `GetDelayToken`, `GetCompactionPressureToken`, `IsStopped`, `NeedsDelay`, `NeedSpeedupCompaction`, `GetDelay`, rate setters/getters, and `low_pri_rate_limiter()`. Token types are `WriteControllerToken`, `StopWriteToken`, `DelayWriteToken`, and `CompactionPressureToken`.

Control flow: Actors such as column families request tokens when write stalls are needed. Active stop tokens make `IsStopped()` true. Active delay tokens make `NeedsDelay()` true and cause writers to call `GetDelay(clock, num_bytes)`. Active compaction-pressure tokens request compaction speedup without necessarily stopping writes. Destructing a token decrements the matching counter.

State and persistence behavior: State is in-memory and process-local: atomic counters for stop/delay/pressure, byte credit and refill timestamp for throttling, max/current delayed write rates, and a low-priority rate limiter. Rate setters clamp zero to one byte/sec and cap current delayed rate at the configured maximum.

Dependencies and integration points: It includes atomics, memory, fixed-width integers, `rocksdb/rate_limiter.h`, and forward declares `SystemClock`. DB mutex discipline is part of the contract. It integrates with write stall conditions from compaction/memtable pressure and low-priority rate limiting.

Risks: Non-atomic delay-credit fields require the documented DB mutex. Token lifetime must be scoped carefully; leaked tokens can permanently stop or delay writes, while premature destruction can remove required backpressure. The default delayed write rate and low-priority limiter values affect write latency under pressure.

Test signals: This item includes implementation but no direct unit test. Expected validation comes from write-stall/compaction-pressure integration tests and destructor assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_controller.h -->
