# subset-b-008712 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_fs.h -->
# sources/storage-engines/rocksdb/utilities/fault_injection_fs.h

## Purpose
This header defines `FaultInjectionTestFS`, a `FileSystemWrapper` used by RocksDB tests and stress tools to simulate filesystem failures, crash-related unsynced data loss, metadata failures, read corruption/truncation, and special file-open contract checks. It also defines wrapper file classes for writable, random-access, random-RW, sequential, and directory objects so faults can be injected at individual filesystem API boundaries.

## Important APIs, types, and functions
`InjectedErrorLog` is a fixed-size thread-safe circular log for recently injected faults. It records timestamp, hashed thread id, and formatted context, and provides `PrintAll()` using async-signal-safe Unix syscalls when possible. `HexHead()` formats a short data prefix for diagnostic messages.

`fault_injection_detail` contains deferred detail builders such as `SizeAndHead`, `OffsetSizeAndHead`, `Count`, and `ReqOffsetAndSize`. These return lambdas evaluated only when a fault is actually injected.

`FaultInjectionIOType` partitions injection into read, write, metadata read, and metadata write. `FSFileState` tracks a file name, last appended offset, last synced offset, and buffered unsynced data, with methods to drop all or random unsynced data.

`TestFSWritableFile` wraps `FSWritableFile` and intercepts `Append`, `PositionedAppend`, `Truncate`, `Flush`, `Sync`, `RangeSync`, `Close`, and `GetFileSize`. It tracks per-file state under a mutex and reports appended, synced, opened, and closed transitions back to `FaultInjectionTestFS`.

`TestFSRandomRWFile`, `TestFSRandomAccessFile`, `TestFSSequentialFile`, and `TestFSDirectory` wrap the corresponding filesystem abstractions and inject write/read/metadata faults. Random-access and sequential wrappers also coordinate with `ReadUnsynced()` so tests can choose whether readers see unsynced data from open writers.

`FaultInjectionTestFS` exposes overrides for most `FileSystem` entry points: file creation/opening, deletion, renaming, linking, metadata queries, directory creation, file-size and free-space queries, async polling, and aborts. Test controls include `SetFilesystemActive`, `SetFilesystemDirectWritable`, `SetInjectUnsyncedDataLoss`, `SetReadUnsyncedData`, `SetAllowLinkOpenFile`, `SetThreadLocalErrorContext`, `Enable/DisableThreadLocalErrorInjection`, file-type and IO-activity exclusions, corruption-before-write toggles, checksum handoff controls, and failure flags for unique id and SST file size APIs.

## Control flow
Normal operations first pass through `FaultInjectionTestFS` validation and `MaybeInjectThreadLocalError()`. If the filesystem is inactive, wrappers return the stored `fs_error_` for operations that should fail during simulated outage/reset. If thread-local injection is enabled and not excluded by IO activity or file type, the relevant `ErrorContext` decides using `Random::OneIn(one_in)` whether to return an injected status or mutate read output.

Writable operations update `FSFileState`: append-style calls advance `pos_at_last_append_` and optionally buffer data for unsynced-loss simulation; sync-style calls advance `pos_at_last_sync_`; close reports final state and prevents repeated raw `Close()` forwarding after the first wrapper close attempt. Directory sync removes entries from `dir_to_new_files_since_last_sync_`.

Read wrappers can consult `ReadUnsynced()` to splice buffered unsynced bytes into scratch or to restrict visible size to synced data when deprecated `read_unsynced_data_` is false. Metadata operations use metadata injection types and can also be forced to report no free space when the inactive filesystem error has `kNoSpace`.

## State and persistence behavior
Persistent simulated state is in memory inside `FaultInjectionTestFS`: `db_file_state_`, `open_managed_files_`, `file_open_contracts_`, `dir_to_new_files_since_last_sync_`, filesystem flags, exclusion sets, thread-local error contexts, corruption and checksum flags, and the injected-error log. It does not persist across process lifetime, but it models what would survive a crash by tracking synced offsets and directory sync state. `DropUnsyncedFileData()`, `DropRandomUnsyncedFileData()`, and `DeleteFilesCreatedAfterLastDirSync()` mutate the underlying target filesystem to reflect simulated recovery.

## Dependencies and integration points
The header depends on RocksDB filesystem abstractions (`rocksdb/file_system.h`), filename parsing (`file/filename.h`), mutex utilities, `Random`, `ThreadLocalPtr`, `Env::IOActivity`, file types, checksum types, `Slice`, `IOStatus`, and platform syscalls for diagnostic printing. It is integrated into db/crash/stress tests by wrapping an existing `FileSystem` and being installed in `Env` or `DBOptions`.

## Risks and edge cases
The injected-error log intentionally accepts benign races while printing signal-safely. Thread-local contexts own callstack memory and must be swapped/deleted carefully. File-open contract tracking and link-open hygiene can reject flows that the underlying filesystem would allow. `read_unsynced_data_` has deprecated semantics and can mask POSIX-like visibility differences. Fault injection can mutate read buffers, truncate slices, or return OK while counting a fault, so callers must not assume all injected faults are non-OK statuses.

## Test signals
`fault_injection_fs_test.cc` directly covers `InjectedErrorLog`, info-log exclusion behavior across read/write/metadata operations, and the writable-file close retry contract. Broader coverage is likely in RocksDB crash, stress, and DB tests that use this wrapper to force filesystem failures and recovery scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_fs_test.cc -->
# sources/storage-engines/rocksdb/utilities/fault_injection_fs_test.cc

## Purpose
This test file validates targeted behavior in `FaultInjectionTestFS` and `InjectedErrorLog`: safe log recording/printing, circular-buffer wraparound, concurrent recording, byte-prefix formatting, file-type exclusions for info logs, and the rule that an injected metadata-close error must not lead to repeated forwarding of the underlying writable file close.

## Important APIs, types, and functions
`NewFaultFsExcludingInfoLogs()` builds a `FaultInjectionTestFS` over the default environment, excludes `FileType::kInfoLogFile`, installs a thread-local error context for a chosen `FaultInjectionIOType`, and enables that injection type.

`CloseCountingWritableFile` wraps a writable file and increments an external counter in `Close()`, providing an observable signal for whether `TestFSWritableFile` forwards close calls.

The `InjectedErrorLogTest` cases exercise `Record()`, `PrintAll()`, circular wrapping past `kMaxEntries`, concurrent `Record()` calls below wraparound, and `HexHead()`. The `FaultInjectionTestFSTest` cases exercise exclusion filters and close semantics.

## Control flow
The info-log exclusion test creates a DB directory, log directory, old info log, current info log name, and manifest files. It then runs four independent fault filesystems, each with a different injection type. Info-log operations are expected to succeed without incrementing injected error counts, while manifest operations are expected to fail and increment exactly once.

The close retry test creates a real writable file through `FaultInjectionTestFS`, wraps it in `TestFSWritableFile` over a `CloseCountingWritableFile`, injects metadata-write errors, appends data, then calls `Close()` twice and destroys the wrapper. It asserts the injected close error prevents inner close forwarding and later wrapper closes remain no-ops.

## State and persistence behavior
Tests write temporary files under `test::PerThreadDBPath()`. Error counts are stored in per-thread `ErrorContext` instances and read/reset through `GetAndResetInjectedThreadLocalErrorCount()`. `InjectedErrorLog` writes to `/dev/null` in tests, so no diagnostic file persists.

## Dependencies and integration points
The test depends on `utilities/fault_injection_fs.h`, `test_util/testharness.h`, RocksDB filename helpers such as `InfoLogFileName`, `OldInfoLogFileName`, `DescriptorFileName`, and file-writing helpers. It installs the RocksDB stack trace handler in `main()`.

## Risks and edge cases
The concurrent log test deliberately avoids circular-buffer slot reuse to stay TSAN-clean; it does not validate concurrent wraparound. The info-log tests cover only recognized info-log file names, so parser changes in `TryParseFileName()` could shift exclusion behavior. Close forwarding is tested through a layered wrapper that mirrors production ownership but does not exercise every close path such as destructor behavior in the raw target.

## Test signals
Strong direct signals exist for the exact regressions named above. Broader `FaultInjectionTestFS` behavior such as unsynced data loss, async reads, directory recovery, and corruption injection is not covered in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_fs_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.cc -->
# sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.cc

## Purpose
This file implements `FaultInjectionSecondaryCache`, a test/stress wrapper around `SecondaryCache` that randomly injects insert and lookup failures according to a configured probability. It is used to verify RocksDB behavior when secondary cache operations fail or silently miss.

## Important APIs, types, and functions
`FaultInjectionSecondaryCache::GetErrorContext()` lazily creates a per-thread `ErrorContext` with deterministic `Random` seed via `ThreadLocalPtr`.

`Insert()` returns `Status::IOError()` when the per-thread random context hits `OneIn(prob_)`; otherwise it forwards to the base cache.

`Lookup()` has two modes. For compressed secondary cache bases, it either returns `nullptr` or directly forwards the base lookup. For other base caches, it wraps the base result handle in `ResultHandle`; when `wait` is true it can reset the handle immediately to simulate a lookup miss/failure.

`ResultHandle` defers injecting lookup failure until `IsReady()`, `Wait()`, or `WaitAll()` resolves the base handle. `UpdateHandleValue()` chooses whether to expose `Value()` and `Size()` or leave them empty.

`Erase()`, capacity APIs, printable options, and force-erase support are delegated to the base cache.

## Control flow
For asynchronous non-compressed lookups, `Lookup()` obtains a base handle and returns a wrapper. When readiness is checked, the wrapper waits or observes readiness, then calls `UpdateHandleValue()`. If the random decision does not inject failure, the wrapper captures the base value and size. In either case it resets the base handle so later calls see the wrapper's terminal state.

`WaitAll()` either filters handles before forwarding to a compressed base cache, or unwraps non-compressed handles, calls base `WaitAll()`, and updates every wrapper that still owns a base handle.

## State and persistence behavior
The wrapper has no persistent state beyond the base cache contents. Fault state is per-thread random generator state initialized from `seed_`. Wrapper result handles hold transient `value_` and `size_` after base handle completion.

## Dependencies and integration points
It depends on `rocksdb/secondary_cache.h`, `util/random.h`, and `util/thread_local.h`. Integration is through the `SecondaryCache` interface, so DB stress can install it wherever a secondary cache is configured.

## Risks and edge cases
`prob_` is passed directly to `Random::OneIn()`, so invalid zero or negative values would be unsafe unless callers validate them. The compressed-cache path does not wrap handles, which means behavior differs from other caches and failure injection occurs before wait rather than at handle completion. In non-compressed `Lookup()`, if the base returns `nullptr`, `ResultHandle::Wait()` would dereference `base_`; callers must avoid waiting on handles with no base or the wrapper must only be used in paths that honor readiness contracts.

## Test signals
No direct test file is listed for this wrapper. Expected coverage is through db_stress or secondary-cache tests configured with this wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.h -->
# sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.h

## Purpose
This header declares `FaultInjectionSecondaryCache`, a `SecondaryCache` decorator that randomly fails inserts and lookups for correctness testing under cache errors.

## Important APIs, types, and functions
The constructor accepts a base `SecondaryCache`, a seed, and a probability denominator. It detects a compressed secondary cache by comparing `base_->Name()` to `"CompressedSecondaryCache"`, setting `base_is_compressed_sec_cache_`.

The public interface implements `Name`, `Insert`, `InsertSaved`, `Lookup`, `SupportForceErase`, `Erase`, `WaitAll`, capacity setters/getters, and printable options. `InsertSaved()` is a no-op returning OK, which is notable because it does not inject errors or forward saved compressed data to the base.

Nested `ResultHandle` implements `SecondaryCacheResultHandle` with `IsReady`, `Wait`, `Value`, `Size`, and static `WaitAll`. It retains the owning cache pointer, optional base handle, final value, and final size.

`ErrorContext` contains only a `Random`. `thread_local_error_` stores per-thread contexts and uses `DeleteThreadLocalErrorContext`.

## Control flow
Callers interact through the normal `SecondaryCache` API. Inserts and lookup readiness draw random decisions from the thread-local context. Delegating methods bypass injection and forward directly to the base cache.

## State and persistence behavior
The header defines wrapper-local configuration (`base_`, `seed_`, `prob_`, compressed-cache flag) and per-thread random state. It does not own persistent cache data; persistence and memory management for entries remain in `base_`.

## Dependencies and integration points
It includes `rocksdb/secondary_cache.h`, `util/random.h`, and `util/thread_local.h`. The class lives in `ROCKSDB_NAMESPACE` and can be plugged into DB options wherever a secondary cache is accepted.

## Risks and edge cases
The compressed-cache name check is string-based and may miss subclasses or renamed implementations. `InsertSaved()` returning OK without forwarding can make saved-object paths appear successful while dropping data. Probability validation is external. Result-handle lifetime assumes the parent cache outlives all handles.

## Test signals
The header has no direct unit test in this subset; behavior should be inferred from tests or stress configurations that exercise secondary cache failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/leveldb_options/leveldb_options.cc -->
# sources/storage-engines/rocksdb/utilities/leveldb_options/leveldb_options.cc

## Purpose
This file implements LevelDB-compatible option defaults and conversion into RocksDB `Options`, providing a compatibility shim for callers that still configure using `LevelDBOptions`.

## Important APIs, types, and functions
`LevelDBOptions::LevelDBOptions()` initializes LevelDB-style defaults: bytewise comparator, false create/error/paranoid flags, default Env, null info log, 4 MiB write buffer, 1000 max open files, null block cache and filter policy, 4 KiB block size, restart interval 16, and Snappy compression.

`ConvertOptions()` maps `LevelDBOptions` to RocksDB `Options`. It copies DB-level flags, env, write buffer, open file limit, and compression. It builds `BlockBasedTableOptions` from block cache, block size, restart interval, and filter policy, then installs a `NewBlockBasedTableFactory`.

## Control flow
Conversion is a single pass: construct default RocksDB `Options`, copy scalar fields, reset smart pointers from raw LevelDB pointer fields, build table options, and return by value.

## State and persistence behavior
No persistent state is stored. A critical ownership transfer occurs: `options.info_log.reset(leveldb_options.info_log)`, `table_options.block_cache.reset(leveldb_options.block_cache)`, and `table_options.filter_policy.reset(leveldb_options.filter_policy)` take ownership of raw pointers supplied in `LevelDBOptions`.

## Dependencies and integration points
The file depends on RocksDB comparator, env, filter policy, options, advanced cache, and table factory APIs. It integrates LevelDB-style configuration with RocksDB open paths.

## Risks and edge cases
Raw pointer ownership transfer can double-delete if the caller also owns these objects or reuses the same `LevelDBOptions` across conversions. Only a subset of LevelDB options is represented. The default compression is Snappy, so environments without Snappy support may behave differently depending on build configuration.

## Test signals
No direct test file is included in this subset. Compatibility is likely covered by LevelDB-options utility tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/leveldb_options/leveldb_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/memory/memory_test.cc -->
# sources/storage-engines/rocksdb/utilities/memory/memory_test.cc

## Purpose
This test file validates `MemoryUtil::GetApproximateMemoryUsageByType()` across multiple DB instances, column families, memtables, table readers, and caches.

## Important APIs, types, and functions
`MemoryTest` is a test fixture creating per-thread DB paths and holding a deterministic `Random`. `UpdateUsagesHistory()` calls the utility and stores per-usage-type samples. `GetCachePointers()` discovers table cache, row cache, and block caches from each DB, using `DBImpl` test hooks and unwrapping `StackableDB` when needed. `GetApproximateMemoryUsageByType()` combines cache discovery with the utility call.

`SharedBlockCacheTotal` opens ten DBs sharing a block cache, writes/flushed data, reads keys to populate cache/table readers, and verifies table reader usage remains stable when no additional flushes happen.

`MemTableAndTableReadersTotal` opens ten DBs with three CFs each, writes large values to grow memtables, verifies monotonic growth, creates iterators to pin flushed memtables, flushes, verifies unflushed memory decreases while table reader and cache usage grow, then deletes iterators and verifies total memtable usage drops.

## Control flow
Tests perform deterministic writes and flushes, sample usage after operations, and compare consecutive history entries for monotonicity or equality. The second test explicitly creates iterators before flush so immutable memtables remain pinned and still count in total memtable usage.

## State and persistence behavior
Temporary DBs under `test::PerThreadDBPath("memory_test")` are destroyed/recreated per DB id. Usage history is in-memory in the fixture. Column family handles and iterators are manually deleted.

## Dependencies and integration points
The test depends on `DBImpl` internals, `rocksdb/utilities/memory_util.h`, block-based table factory, cache APIs, test harness/utilities, `Random`, and `StackableDB`. It validates integration between public DB properties, internal cache pointers, and the memory utility.

## Risks and edge cases
Assertions depend on approximate memory properties and timing of flush/compaction behavior; options disable auto compactions to reduce nondeterminism. Shared cache accounting relies on de-duplicated cache pointer sets. The test is disabled on release Windows builds through `main()`.

## Test signals
This is the direct regression suite for memory usage aggregation, especially monotonic behavior under writes, flushes, cache fills, and pinned memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/memory/memory_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/memory/memory_util.cc -->
# sources/storage-engines/rocksdb/utilities/memory/memory_util.cc

## Purpose
This file implements `MemoryUtil::GetApproximateMemoryUsageByType()`, aggregating approximate RocksDB memory consumption by category across a vector of DB handles and an explicit set of cache pointers.

## Important APIs, types, and functions
The templated `GetApproximateMemoryUsageByType()` accepts `std::vector<DBPtr>`, an `unordered_set<const Cache*>`, and an output map keyed by `MemoryUtil::UsageType`. It explicitly instantiates for `DB*` and `std::unique_ptr<DB>`.

It reads `DB::Properties::kSizeAllMemTables` into `kMemTableTotal`, `DB::Properties::kCurSizeAllMemTables` into `kMemTableUnFlushed`, and `DB::Properties::kEstimateTableReadersMem` into `kTableReadersTotal`. It sums `Cache::GetUsage()` for non-null cache pointers into `kCacheTotal`.

## Control flow
The function clears the output map, loops through DBs for each property category, conditionally adds values only when `GetAggregatedIntProperty()` succeeds, then loops through caches and adds their current usage.

## State and persistence behavior
No state is persisted or cached. The returned map is a snapshot of approximate property values and cache usage at call time.

## Dependencies and integration points
It depends on `rocksdb/utilities/memory_util.h`, `db/db_impl/db_impl.h`, `DB` property names, and the `Cache` interface. Callers must provide a de-duplicated cache set to avoid double-counting shared caches.

## Risks and edge cases
The cache set is passed by value, which copies the set. Missing or unsupported DB properties silently contribute zero. Approximate values can change concurrently with DB activity. The utility does not discover caches itself, so caller omissions or duplicate pointers determine accuracy.

## Test signals
`memory_test.cc` validates monotonic and stable behavior across memtables, table readers, and shared caches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/memory/memory_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/memory_allocators.h -->
# sources/storage-engines/rocksdb/utilities/memory_allocators.h

## Purpose
This header provides simple `MemoryAllocator` implementations and wrappers used by RocksDB components and tests: a default new/delete allocator, a failing base class for conditionally compiled allocators, a wrapper/decorator, and a counted allocator.

## Important APIs, types, and functions
`DefaultMemoryAllocator` implements `Allocate(size_t)` with `new char[size]`, `Deallocate(void*)` with `delete[]`, and reports `Name()` as `"DefaultMemoryAllocator"`.

`BaseMemoryAllocator` implements failure-mode `Allocate()` and `Deallocate()` with `assert(false)`, intended as a base for optional allocators that only provide real behavior when a compile-time feature is enabled.

`MemoryAllocatorWrapper` owns a `shared_ptr<MemoryAllocator>` target, delegates `Allocate`, `Deallocate`, `UsableSize`, and exposes `Inner()`.

`CountedMemoryAllocator` extends the wrapper, defaults to wrapping `DefaultMemoryAllocator`, increments atomic allocation/deallocation counters, returns `GetId()` as its name, and exposes counter getters.

## Control flow
Wrapper methods forward directly to `target_`. Counted methods increment their atomics before delegating. No allocation metadata is stored by the counted wrapper, so it counts calls rather than bytes or live allocations.

## State and persistence behavior
State is in-memory only: `target_` shared ownership plus atomic counters in `CountedMemoryAllocator`.

## Dependencies and integration points
The header depends on `rocksdb/memory_allocator.h` and `<atomic>`. It integrates wherever RocksDB accepts a `MemoryAllocator`, including caches or memory-managed table/block components.

## Risks and edge cases
`BaseMemoryAllocator` will abort in debug builds if used without overrides and return null/do nothing in release after the assert is compiled out. `DefaultMemoryAllocator` provides no alignment beyond `new[]`. Counters can diverge from live allocations when allocations fail or callers deallocate externally allocated memory.

## Test signals
No direct test is listed here. Expected coverage is through allocator users and any tests that inspect counted allocation/deallocation calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/memory_allocators.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators.cc

## Purpose
This file registers RocksDB built-in merge operators with the object registry and implements string-id creation through `MergeOperator::CreateFromString()` and `MergeOperators::CreateFromStringId()`.

## Important APIs, types, and functions
`RegisterBuiltinMergeOperators()` adds factories to an `ObjectLibrary` for `StringAppendOperator`, `StringAppendTESTOperator`, `SortList`, `BytesXOROperator`, `UInt64AddOperator`, `MaxOperator`, `PutOperatorV2`, and deprecated `PutOperator`. Most factories register both class names and nicknames through `PatternEntry().AnotherName()`.

`MergeOperator::CreateFromString()` uses `std::call_once` to register builtins into `ObjectLibrary::Default()` exactly once, then calls `LoadSharedObject<MergeOperator>()`.

`MergeOperators::CreateFromStringId()` wraps `CreateFromString()` and returns `nullptr` on empty, unknown, or failed ids.

## Control flow
The first string-based creation call triggers builtin registration. Later calls skip registration and directly query the object registry/shared object loading path. Factories allocate concrete operators into the provided unique pointer guard and return the raw pointer.

## State and persistence behavior
Global registry state is mutated through the default `ObjectLibrary`. The registration is process-global and persistent for process lifetime.

## Dependencies and integration points
This file depends on all built-in merge operator headers, `rocksdb/utilities/object_registry.h`, `customizable_util`, `rocksdb/options.h`, and `rocksdb/merge_operator.h`. It is the bridge between option strings and concrete merge operator instances.

## Risks and edge cases
Registration into a global singleton can interact with tests that also add factories. Factory count return value is informational only. `CreateFromStringId()` intentionally suppresses error details by returning `nullptr`.

## Test signals
String-id creation is typically covered by options/object registry tests and merge-operator-specific tests. The file has no direct listed test.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators.h

## Purpose
This header declares the `MergeOperators` factory convenience class for constructing RocksDB built-in merge operators.

## Important APIs, types, and functions
Factory methods include `CreatePutOperator`, `CreateDeprecatedPutOperator`, `CreateUInt64AddOperator`, `CreateStringAppendOperator()` overloads, `CreateStringAppendTESTOperator`, `CreateMaxOperator`, `CreateBytesXOROperator`, `CreateSortOperator`, and `CreateFromStringId`.

## Control flow
The header only declares static methods. Implementations in operator-specific `.cc` files return `shared_ptr<MergeOperator>` for concrete operators, while `merge_operators.cc` implements string-id lookup.

## State and persistence behavior
No state is declared in this header. Returned operators are owned by `shared_ptr`s.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and standard string/memory headers. It is the public utility entry point used by applications, tests, and options parsing to obtain built-in merge operators.

## Risks and edge cases
The class mixes stable production operators with test/deprecated operators, so callers must choose intentionally. `CreateFromStringId()` may return null rather than surfacing a detailed `Status`.

## Test signals
Coverage comes from individual merge operator tests and options/object-registry tests that create operators from names.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.cc

## Purpose
This file implements `BytesXOROperator`, an associative merge operator that XORs byte arrays.

## Important APIs, types, and functions
`MergeOperators::CreateBytesXOROperator()` returns a shared `BytesXOROperator`.

`BytesXOROperator::Merge()` ignores key/logger, delegates to `XOR()`, and returns true.

`XOR()` copies the operand when no existing value exists. Otherwise it XORs bytes up to the shorter length and appends the remaining tail from the longer input unchanged.

## Control flow
The merge path clears and reserves `new_value`, processes the common prefix byte-by-byte, then copies the suffix from whichever input is longer.

## State and persistence behavior
The operator is stateless. Persistent DB value state is determined solely by merge operands and compaction/get merge evaluation.

## Dependencies and integration points
It depends on `bytesxor.h`, standard algorithms/strings, and the RocksDB associative merge interface. It is registered by `merge_operators.cc` under class name `"BytesXOR"` and nickname `"bytesxor"`.

## Risks and edge cases
The operator is described as XORing same-sized byte arrays but accepts different sizes by carrying the longer suffix unchanged. XOR on signed `char` operands is stored back into `char`, which is byte-preserving but may be surprising in textual contexts. It always reports success and does not validate input sizes.

## Test signals
No direct test is listed in this subset. Expected coverage is through merge operator unit tests or factory tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.h

## Purpose
This header declares `BytesXOROperator`, a model `AssociativeMergeOperator` for byte-wise XOR semantics.

## Important APIs, types, and functions
The class overrides `Merge()`, exposes `Name()` as `"BytesXOR"`, `NickName()` as `"bytesxor"`, and provides public helper `XOR(const Slice*, const Slice&, std::string*)`.

## Control flow
The header defines no inline control flow beyond names. Implemented behavior is in `bytesxor.cc`.

## State and persistence behavior
The operator stores no member state.

## Dependencies and integration points
It includes RocksDB env, merge operator, slice, coding utilities, and `utilities/merge_operators.h`. It participates in `MergeOperators::CreateBytesXOROperator()` and object-registry registration.

## Risks and edge cases
The exposed `XOR()` helper lets tests or callers use the byte logic outside a merge operation, but it inherits the same no-validation behavior.

## Test signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/max.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/max.cc

## Purpose
This file implements `MaxOperator`, a merge operator that keeps the lexicographically maximum `Slice` according to `Slice::compare()`.

## Important APIs, types, and functions
`FullMergeV2()` initializes the output existing operand from `existing_value` when present, otherwise uses an empty slice if needed, then scans operands and retains the max slice.

`PartialMerge()` compares two operands and assigns the larger to `new_value`.

`PartialMergeMulti()` scans a deque of operands, assigns the max to `new_value`, and returns true.

`MergeOperators::CreateMaxOperator()` returns a shared `MaxOperator`.

## Control flow
Full and partial merge paths are linear scans over operands. `FullMergeV2()` can avoid copying by assigning `merge_out->existing_operand` to an input slice. Partial merges copy the selected slice into `new_value`.

## State and persistence behavior
The operator is stateless. DB value persistence is the max of existing value and accumulated operands at merge evaluation time.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h`, `rocksdb/slice.h`, and `utilities/merge_operators.h`. It is registered under `"MaxOperator"` and `"max"`.

## Risks and edge cases
Ordering is raw byte lexicographic, not numeric. `PartialMergeMulti()` with an empty operand list assigns from a default empty `Slice`, which is safe but may not represent a meaningful merge. `FullMergeV2()` relies on lifetimes of input slices when setting `existing_operand`.

## Test signals
No direct test in this subset; expected coverage is via merge operator and registry tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/max.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/max_operator.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/max_operator.h

## Purpose
This header declares `MaxOperator`, a `MergeOperator` that selects the maximum operand by `Slice::compare()`.

## Important APIs, types, and functions
It exposes `kClassName()` as `"MaxOperator"`, `kNickName()` as `"max"`, overrides `Name()`, `NickName()`, `FullMergeV2()`, `PartialMerge()`, and `PartialMergeMulti()`.

## Control flow
No inline logic beyond names; implementation is in `max.cc`.

## State and persistence behavior
The class has no data members and is stateless.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and forward declares `Logger` and `Slice`. It is consumed by merge operator factories and registry registration.

## Risks and edge cases
The header documents only "maximum operand"; callers must know that maximum is lexicographic `Slice` comparison.

## Test signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/max_operator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/put.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/put.cc

## Purpose
This file implements merge operators that mimic Put semantics by making the latest merge operand become the value.

## Important APIs, types, and functions
`PutOperator::FullMerge()` assigns `operand_sequence.back()` to `new_value`. `PartialMerge()` assigns the right operand. `PartialMergeMulti()` assigns the last operand.

`PutOperatorV2::FullMerge()` is intentionally disabled with `assert(false)` and returns false; `FullMergeV2()` writes the last operand to `merge_out->existing_operand`.

`MergeOperators::CreateDeprecatedPutOperator()` returns `PutOperator`; `CreatePutOperator()` returns `PutOperatorV2`.

## Control flow
Every active merge path chooses the newest/rightmost operand and ignores existing value. This makes merge accumulation equivalent to overwriting with the latest value.

## State and persistence behavior
The operators are stateless. Persistent DB values become the latest merge operand after reads or compactions resolve merge operands.

## Dependencies and integration points
It depends on RocksDB merge/slice APIs and `utilities/merge_operators.h`. `PutOperatorV2` is registered as nickname `"put"` while deprecated v1 uses `"put_v1"`.

## Risks and edge cases
The code asserts non-empty operand sequences but does not handle empty input gracefully in release builds. `PutOperatorV2::FullMerge()` must not be called by code paths expecting only legacy full-merge API. This operator is primarily for testing and examples, not production.

## Test signals
No direct test in this subset; behavior is likely covered by merge operator tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/put.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/put_operator.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/put_operator.h

## Purpose
This header declares the deprecated and V2 Put-like merge operators.

## Important APIs, types, and functions
`PutOperator` exposes class name `"PutOperator"` and nickname `"put_v1"`, overriding legacy `FullMerge`, `PartialMerge`, and `PartialMergeMulti`.

`PutOperatorV2` derives from `PutOperator`, changes nickname to `"put"`, overrides legacy `FullMerge` as unsupported, and implements `FullMergeV2`.

## Control flow
The header declares the split between legacy and V2 merge APIs. Actual newest-operand selection is implemented in `put.cc`.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h`. It is used by factory helpers and object registry registration.

## Risks and edge cases
Inheritance means `PutOperatorV2` still inherits `PartialMerge` behavior from `PutOperator`; callers must not assume all legacy APIs are valid because only `FullMerge` is deliberately disabled.

## Test signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/put_operator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.cc

## Purpose
This file implements `SortList`, a merge operator that takes operands representing comma-separated sorted integer lists and merges them into one sorted comma-separated list.

## Important APIs, types, and functions
`FullMergeV2()` iterates through `merge_in.operand_list`, parses each operand with `MakeVector()`, merges it into an accumulated vector using `Merge()`, and serializes the result to `merge_out->new_value`.

`PartialMerge()` parses left and right operands, merges them, and serializes to `new_value`.

`PartialMergeMulti()` currently ignores inputs and returns true without writing a value.

`MakeVector()` parses integers separated by commas using `std::stoi`. `Merge()` performs the standard two-pointer merge of sorted vectors. `MergeOperators::CreateSortOperator()` returns a shared `SortList`.

## Control flow
Both active merge paths parse string operands into vectors, merge sorted inputs pairwise, then append values with commas between all but the last. `Merge()` preserves duplicates.

## State and persistence behavior
The operator is stateless. DB values persist as serialized sorted integer lists after merge resolution.

## Dependencies and integration points
It depends on `sortlist.h`, RocksDB merge/slice APIs, and the merge operator factory header. It is registered under `"MergeSortOperator"` and `"sortlist"`.

## Risks and edge cases
`FullMergeV2()` and `PartialMerge()` call `left.back()` or serialize assuming non-empty lists; empty operands or no operands can crash or produce undefined behavior. `MakeVector()` directly advances `Slice::data_`, depends on null/comma termination behavior, and can throw from `std::stoi` on invalid integers. `PartialMergeMulti()` returning true without output is suspicious and could lose data if used by merge scheduling.

## Test signals
No direct test in this subset. This operator needs focused tests for empty operands, malformed integers, multi-operand partial merge, duplicates, and negative numbers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.h

## Purpose
This header declares `SortList`, a `MergeOperator` for merging sorted integer-list operands.

## Important APIs, types, and functions
The class overrides `FullMergeV2`, `PartialMerge`, and `PartialMergeMulti`, exposes `Name()` as `"MergeSortOperator"` and `NickName()` as `"sortlist"`, and provides public `MakeVector()` plus private `Merge()`.

## Control flow
No inline control flow beyond names; implementation is in `sortlist.cc`.

## State and persistence behavior
The operator stores no members and is stateless.

## Dependencies and integration points
It depends on RocksDB merge and slice APIs. It is exposed through `MergeOperators::CreateSortOperator()` and registry string creation.

## Risks and edge cases
The public `MakeVector()` mutates its `Slice` parameter's data pointer copy and assumes input format. The header does not document malformed input behavior or `PartialMergeMulti()` limitations.

## Test signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.cc

## Purpose
This file implements the production associative string append merge operator. It concatenates existing value and operand with a configurable delimiter.

## Important APIs, types, and functions
`stringappend_merge_type_info` registers a configurable `"delimiter"` option using `OptionTypeInfo`, allowing option parsing and customization.

Constructors accept either a delimiter character or string, store it in `delim_`, and call `RegisterOptions("Delimiter", &delim_, ...)`.

`StringAppendOperator::Merge()` clears `new_value`; if there is no existing value it copies the operand, otherwise it reserves exact capacity, copies existing value, appends delimiter, then appends operand.

Factory overloads in `MergeOperators` create comma-delimited, char-delimited, or string-delimited operators.

## Control flow
The associative merge path handles the first operand specially by avoiding a leading delimiter. Subsequent merges append delimiter plus operand.

## State and persistence behavior
The operator stores only `delim_`. DB values persist as delimiter-separated concatenations after get/compaction resolves merges.

## Dependencies and integration points
It depends on RocksDB merge/slice APIs, option type registration, and `utilities/merge_operators.h`. It is registered under `"StringAppendOperator"` and `"stringappend"`.

## Risks and edge cases
Delimiter bytes are copied defensively, including empty, multi-character, and null-byte delimiters. The operator is associative only for a fixed delimiter and simple append semantics; values containing the delimiter are not escaped, so parsing is caller-defined.

## Test signals
`stringappend_test.cc` provides broad tests for delimiters, persistence, iterator behavior, random operations, flush, compaction, and TTL/generic operator comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.h

## Purpose
This header declares `StringAppendOperator`, the production associative merge operator for delimiter-separated string append.

## Important APIs, types, and functions
Constructors accept a delimiter character or string. `Merge()` implements `AssociativeMergeOperator`. `Name()` returns `"StringAppendOperator"` and `NickName()` returns `"stringappend"`. The only data member is `std::string delim_`.

## Control flow
No inline merge logic is defined here; implementation is in `stringappend.cc`.

## State and persistence behavior
The delimiter is stored per operator instance and participates in options serialization through registration in the implementation.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and `rocksdb/slice.h`. It is used by `MergeOperators` factories, options parsing, and DB configurations.

## Risks and edge cases
Because delimiter is instance state, opening a DB with a different delimiter changes future merge interpretation. Existing materialized values are plain strings and do not encode delimiter metadata.

## Test signals
Covered by `stringappend_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend2.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend2.cc

## Purpose
This file implements `StringAppendTESTOperator`, a non-associative/test merge operator semantically equivalent to string append. It is useful for testing generic `MergeOperator` paths rather than the simpler `AssociativeMergeOperator` path.

## Important APIs, types, and functions
`stringappend2_merge_type_info` registers the `"delimiter"` option. Constructors store delimiter and register options.

`FullMergeV2()` builds the concatenation from optional existing value plus all operands. If there is no existing value and exactly one operand, it sets `merge_out->existing_operand` to that operand and avoids copying.

`PartialMergeMulti()` returns false, disabling generic partial merge. `_AssocPartialMergeMulti()` implements append-style partial merge for tests/simulation but is private and unused by the public override.

`MergeOperators::CreateStringAppendTESTOperator()` returns a comma-delimited instance.

## Control flow
Full merge computes a reservation size, appends existing value first if present, then loops over operands inserting delimiters only after the first emitted component. Partial merge is deliberately unavailable through the public API.

## State and persistence behavior
The operator stores delimiter state only. DB values persist as delimiter-separated strings after full merge evaluation.

## Dependencies and integration points
It depends on RocksDB merge/slice APIs, option type metadata, and merge operator factories. It is registered as `"StringAppendTESTOperator"` and `"stringappendtest"` and is used by TTL DB tests in this subset.

## Risks and edge cases
The one-operand optimization relies on the lifetime semantics of `existing_operand`. `PartialMergeMulti()` returning false can increase merge work and must be expected by callers. Like the production operator, it does not escape delimiter occurrences in values.

## Test signals
`stringappend_test.cc` runs the same parameterized behavior against normal DB/stringappend and TTL DB/stringappendtest, giving good semantic comparison coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend2.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend2.h

## Purpose
This header declares `StringAppendTESTOperator`, the generic `MergeOperator` implementation of string append used for tests and benchmarking.

## Important APIs, types, and functions
Constructors accept char or string delimiters. The class overrides `FullMergeV2()` and `PartialMergeMulti()`, reports name `"StringAppendTESTOperator"` and nickname `"stringappendtest"`, and has private helper `_AssocPartialMergeMulti()`.

## Control flow
No inline behavior beyond names and signatures; implementation is in `stringappend2.cc`.

## State and persistence behavior
The only member is `std::string delim_`, serialized/configured through option registration in the implementation.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and `rocksdb/slice.h`. It is used by tests and by builtin merge operator registration.

## Risks and edge cases
The type is explicitly non-production. Its public partial merge behavior differs from `StringAppendOperator`, so performance and compaction behavior are intentionally different even when final semantics match.

## Test signals
Covered indirectly and directly by the parameterized `stringappend_test.cc` TTL branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend_test.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend_test.cc

## Purpose
This file is the unit/integration test suite for the string append merge operators. It verifies append semantics through DB APIs, iterators, persistence, flush/compaction, delimiter variants, and both production associative and test generic operator implementations.

## Important APIs, types, and functions
`OpenNormalDb()` opens a regular DB with `StringAppendOperator`. `OpenTtlDb()` opens a `DBWithTTL` with `StringAppendTESTOperator`. Both choose char or string constructor depending on delimiter length.

`StringLists` is a small test harness around `DB::Merge()` and `DB::Get()` treating each key as a string list. `Append()` returns success/failure; `Get()` returns an empty string on not found.

`StringAppendOperatorTest` is parameterized by `bool`; `SetUp()` chooses normal DB or TTL DB. Tests cover iterator snapshots, simple append, simple/empty/multi-character/null delimiters, defensive delimiter copy, one-value no delimiter, multiple keys, random append/get mixes, persistence across reopen, flush, and compaction.

## Control flow
Most tests perform Merge operations through `StringLists`, then Get or iterate to force merge resolution. Persistence tests close and reopen the DB to ensure values survive memtable, L0, and VersionSet paths. The fixture destroys the DB before each test.

## State and persistence behavior
Temporary DB state lives under `test::PerThreadDBPath("stringappend_test")`. Tests intentionally verify persistence across scoped DB destruction/reopen and across flush/compaction. The parameterized TTL branch also verifies behavior when a `DBWithTTL` wraps the base DB.

## Dependencies and integration points
The file depends on `StringAppendOperator`, `StringAppendTESTOperator`, RocksDB DB and TTL APIs, merge operator APIs, test harness, stack trace support, `Random`, and `UnownedPtr`.

## Risks and edge cases
Iterator tests assume key ordering and snapshot behavior. Random tests use deterministic seeds but relatively small word/key distributions. Tests verify delimiter handling but not escaping or parsing of values containing delimiters. TTL behavior uses a large TTL and does not test expiration.

## Test signals
This is strong coverage for string append correctness across public DB workflows. It does not cover registry string creation or options serialization beyond constructing operators directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.cc -->
# sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.cc

## Purpose
This file implements `UInt64AddOperator`, an associative merge operator that treats operands and existing values as fixed-width little-endian uint64 values and stores their sum.

## Important APIs, types, and functions
`UInt64AddOperator::Merge()` decodes existing value if present, decodes the operand, clears `new_value`, writes `orig_value + operand` with `PutFixed64()`, and returns true.

`DecodeInteger()` returns `DecodeFixed64()` when the slice is exactly 8 bytes. Otherwise it logs a corruption message when a logger is available and returns zero.

`MergeOperators::CreateUInt64AddOperator()` returns a shared `UInt64AddOperator`.

## Control flow
The merge path is constant-time: decode existing, decode operand, add, encode. Corrupt-sized inputs are tolerated as zero rather than failing the merge.

## State and persistence behavior
The operator is stateless. Persistent DB values are fixed64-encoded sums. Overflow wraps according to unsigned 64-bit arithmetic.

## Dependencies and integration points
It depends on RocksDB logging, env/merge/slice APIs, `util/coding.h`, and merge factories. It is registered under `"UInt64AddOperator"` and `"uint64add"`.

## Risks and edge cases
Malformed values silently become zero except for optional logging. Overflow is not checked. Endianness/encoding must match `PutFixed64` and `DecodeFixed64`; callers storing decimal strings will get corruption-as-zero semantics.

## Test signals
No direct test in this subset. Expected coverage is through merge operator unit tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.h -->
# sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.h

## Purpose
This header declares `UInt64AddOperator`, a model associative merge operator for uint64 addition.

## Important APIs, types, and functions
The class exposes class name `"UInt64AddOperator"`, nickname `"uint64add"`, overrides `Merge()`, and has private helper `DecodeInteger()`.

## Control flow
No inline behavior beyond names; implementation is in `uint64add.cc`.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and `utilities/merge_operators.h`. It is available through factory helpers and object registry lookup.

## Risks and edge cases
The header does not communicate overflow or corrupt-input-as-zero semantics; callers must consult implementation or docs.

## Test signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/object_registry.cc -->
# sources/storage-engines/rocksdb/utilities/object_registry.cc

## Purpose
This file implements RocksDB's object registry and object library mechanics: matching URI/name patterns to factories, maintaining local and parent registries, managing weakly referenced named objects, registering plugins, and dumping registered factory metadata.

## Important APIs, types, and functions
`MatchesInteger()` and `MatchesDecimal()` validate numeric pattern spans, allowing leading `-` and requiring at least one digit. `ObjectLibrary::PatternEntry::MatchSeparatorAt()` and `MatchesTarget()` implement pattern matching over base names, separators, suffixes, integer/decimal quantifiers, exact matches, zero-or-more matches, optional base names, and alternate names.

`ObjectLibrary` methods include `GetFactoryCount()`, `GetFactoryNames()`, `GetFactoryTypes()`, `Dump()`, and `Default()`. The default library is a static avoid-destruction singleton.

`ObjectRegistry` constructors attach libraries and builtins. `Default()` and `NewInstance()` create singleton/default-parented registries. `SetManagedObject()`, `GetManagedObject()`, and `ListManagedObjects()` manage weak references keyed by type/id and delegate to parents. Factory count/name/type methods aggregate parent plus local libraries. `Dump()` logs plugins and libraries. `RegisterPlugin()` records plugin name and invokes a registrar against a newly added library.

## Control flow
Pattern matching first tries the primary name, then alternate names. For patterned names, it checks prefix, walks separators in order, changes the matching mode according to each separator's quantifier, and validates the remaining tail.

Registry lookup generally checks current state first for managed objects, then parent. Factory metadata counts parent first then local libraries. Plugins append to `plugins_`, create a named library, and invoke the registration callback.

## State and persistence behavior
Registry state is in-memory process state. `ObjectLibrary::Default()` and `ObjectRegistry::Default()` are long-lived singletons. Managed objects are stored as `weak_ptr`, so objects disappear from registry results once external shared ownership is gone. Libraries and plugin lists are owned by registries.

## Dependencies and integration points
It depends on `rocksdb/utilities/object_registry.h`, logging, `Customizable`, `Env`, and string utilities. It underpins options parsing, `LoadSharedObject`, merge operator creation, and configurable RocksDB components.

## Risks and edge cases
Global singleton registration can leak state across tests. Managed object keys use type/id strings, so collisions or inconsistent `GetId()` implementations matter. Pattern matching is hand-rolled and subtle around empty separators, decimal syntax such as `.1`, and optional names. Weak managed objects require callers to hold shared ownership elsewhere.

## Test signals
`object_registry_test.cc` covers factory ownership modes, local/default/parent registry behavior, managed object lifetimes and aliases, plugin registration, factory metadata counts, and many pattern matching cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/object_registry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/object_registry_test.cc -->
# sources/storage-engines/rocksdb/utilities/object_registry_test.cc

## Purpose
This file tests `ObjectLibrary`, `ObjectRegistry`, managed objects, plugin registration, and `PatternEntry` matching semantics.

## Important APIs, types, and functions
Static factories `test_reg_a` and `test_reg_b` register Env factories in the default library. `WrappedEnv` gives owned wrappers around `Env::Default()`.

`RegisterTestUnguarded()` registers one static/unguarded and one owned/guarded Env factory. `MyCustomizable` is a test `Customizable` with type, name, and id behavior.

Registry tests cover `NewStaticObject`, `NewUniqueObject`, `NewSharedObject`, `NewObject`, local libraries, parent registries, factory counts/names/types, weak managed objects, alternate managed names, multiple managed classes, parent managed-object conflict behavior, `GetOrCreateManagedObject`, and `RegisterPlugin`.

Pattern tests cover simple entries, required/optional separator patterns, zero-or-more suffixes, numeric and decimal matches, individual ids of the form `AA@...#...`, alternate names, multiple separators/numbers, suffix plus pattern combinations, and alternate names with patterns.

## Control flow
Tests build registries and libraries, register factories, then request objects under different ownership APIs to verify whether guarded factories are accepted for unique/shared and rejected for static, while unguarded factories have the opposite behavior. Managed object tests reset shared pointers to verify weak registry entries expire.

Pattern tests construct `PatternEntry` objects incrementally and assert exact match truth tables.

## State and persistence behavior
The default object library is mutated by static registration before tests run and persists process-wide. Test-local registries and libraries are heap objects. Managed object entries are weak and disappear when test-held shared pointers reset.

## Dependencies and integration points
The file depends on `rocksdb/utilities/object_registry.h`, `rocksdb/convenience.h`, `Customizable`, Env wrappers, and the RocksDB test harness.

## Risks and edge cases
Because default-library factories are static globals, test order and global registry pollution can affect later tests if names collide. Some tests intentionally count failed factory creations that still increment counters before ownership rejection. Pattern matching coverage is broad but still does not cover every possible empty separator or malformed UTF/non-ASCII input case.

## Test signals
This is strong direct coverage for object registry behavior and pattern matching. It validates important lifetime semantics for weak managed objects and ownership mode safety.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/object_registry_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration.cc -->
# sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration.cc

## Purpose
This file implements `OptionChangeMigration()`, a utility that rewrites/compacts an existing DB so it can be reopened safely after changing compaction style or level-related options, including multi-column-family configurations.

## Important APIs, types, and functions
`GetNoCompactionOptions()` disables automatic compaction and stalls by setting high L0 triggers and zero pending compaction byte limits.

`CompactToLevel()` compacts a CF to a target level using `CompactRangeOptions::change_level`; when target is L0 it forces bottommost compaction to avoid trivial move behavior.

`MigrateToUniversal()`, `MigrateToLevelBase()`, and `MigrateToFIFO()` decide compaction targets for target compaction styles. Universal compacts down only if existing highest level is outside new `num_levels`; level compacts to L1 for non-dynamic or last level for dynamic; FIFO compacts to L0.

`MigrateSingleColumnFamily()` dispatches based on old/new compaction style and treats old FIFO as no-op. `ValidateCFDescriptors()` requires old/new CF descriptor counts, names, and order to match.

`DetermineBaseOptions()`, `ApplySpecialSingleLevelSettings()`, and `PrepareNoCompactionCFDescriptors()` build temporary CF descriptors that can open the DB without unwanted compaction while still being close enough to new settings to rewrite metadata when needed.

`OpenDBWithCFs()`, `CleanupCFHandles()`, and `MigrateAllCFs()` manage DB opening, handle cleanup, and per-CF migration. Public overloads accept either full DB/CF descriptors or single `Options`.

## Control flow
The public multi-CF function validates descriptors, prepares no-compaction descriptors and tracks whether manifest-rewrite reopen is needed, opens the DB with old DB options and temporary CF options, migrates all CFs, destroys non-default CF handles, optionally closes and reopens with temporary descriptors to rewrite manifest state, then closes the DB.

## State and persistence behavior
The utility mutates persistent DB state by running compactions and rewriting manifest/options metadata through DB open/close. It does not add or drop CFs. Temporary in-memory vectors track handles and descriptors; handle cleanup is explicit.

## Dependencies and integration points
It depends on `rocksdb/utilities/option_change_migration.h` and `rocksdb/db.h`. It integrates with RocksDB compaction APIs, DB open/close, column family descriptors, and DB option/CF option conversion.

## Risks and edge cases
Adding, dropping, or reordering CFs is unsupported and rejected. Old FIFO is treated as no-op regardless of target style, which relies on FIFO layout already being acceptable. Cleanup errors can override success. The function opens with `old_db_opts` even for reopen steps using temporary CF descriptors, so DB-level option migration is limited. Very large sentinel values for file size/compaction bytes are magic constants.

## Test signals
`option_change_migration_test.cc` heavily covers compaction-style transitions, dynamic level changes, FIFO size limits, compaction with bottommost files, multi-CF migration, mixed target styles per CF, validation failures, and FIFO source migration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration_test.cc -->
# sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration_test.cc

## Purpose
This test file validates `OptionChangeMigration()` across compaction style and level-count transitions, data preservation, reopen safety, FIFO cases, and multi-column-family migrations.

## Important APIs, types, and functions
`DBOptionChangeMigrationTests` is parameterized by old/new level counts, compaction styles, dynamic-level flags, and FIFO max table file size. Test cases `Migrate1` through `Migrate4` run transitions in both directions and with different data generation patterns, preserving key sets for verification.

`DBOptionChangeMigrationTest.CompactedSrcToUniversal` covers a compacted level source migrating to universal with one level.

`DBOptionChangeMigrationMultiCFTest` covers `BasicMultiCF`, `DifferentStylesPerCF`, `ValidationMismatched`, and `FromFIFOMultiCF`.

## Control flow
Single-CF tests configure old options, write at least megabytes of data, wait for flush/compaction, snapshot all keys via iterator, close, call `OptionChangeMigration()`, reopen with new options, wait/reopen again, and assert exact key ordering/presence.

Multi-CF tests create an extra CF, write data to default and `cf1`, collect key sets, close, build old/new descriptor vectors, migrate, reopen all CFs, and verify data per CF. Validation tests call migration with missing, renamed, or reordered CF descriptors and expect `InvalidArgument`.

## State and persistence behavior
Tests use real DB directories through `DBTestBase` with fsync enabled. They intentionally exercise persistent compaction output and manifest rewriting across close/reopen cycles. CF handles are manually deleted/destroyed.

## Dependencies and integration points
The file depends on `rocksdb/utilities/option_change_migration.h`, `db/db_test_util.h`, stack trace support, `Random`, and DB compaction/flush/test wait hooks.

## Risks and edge cases
The parameter comments sometimes label new values as old in tuple literals, but the tuple positions are clear in code. Tests focus on key preservation, not exact level layout after migration. Multi-CF cleanup skips destroying the default handle, matching DB ownership expectations.

## Test signals
Coverage is strong for successful migration and descriptor validation. It gives high confidence in data preservation across supported compaction-style transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/options/options_util.cc -->
# sources/storage-engines/rocksdb/utilities/options/options_util.cc

## Purpose
This file implements utilities for loading RocksDB options from OPTIONS files, finding the latest OPTIONS file in a DB directory, loading the latest options, and checking current option compatibility against persisted options.

## Important APIs, types, and functions
`LoadOptionsFromFile()` uses `RocksDBOptionsParser::Parse()` with the filesystem from `config_options.env`, copies parsed DB options, builds `ColumnFamilyDescriptor` entries from parsed CF names/options, and optionally injects a supplied shared block cache into any parsed block-based table factory.

`GetLatestOptionsFileName()` lists DB directory children through `Env`, parses filenames with `ParseFileName()`, selects the `kOptionsFile` with the highest timestamp, and returns `NotFound(PathNotFound)` when the directory is missing or contains no options file.

`LoadLatestOptions()` combines latest-file lookup and file parsing.

`CheckOptionsCompatibility()` finds the latest options file, converts supplied CF descriptors into separate name/options vectors, and calls `RocksDBOptionsParser::VerifyRocksDBOptionsFromFile()`.

## Control flow
All operations are synchronous. Latest-file selection is a linear scan. Compatibility verification delegates to the parser, using the filesystem from `config_options.env`.

## State and persistence behavior
The utilities read OPTIONS files but do not mutate DB state. When a cache pointer is supplied, loaded CF descriptors are modified in memory so block-based table factories share that cache.

## Dependencies and integration points
It depends on filename parsing, `options/options_parser.h`, RocksDB convenience/options APIs, and block-based table factory options. It integrates DB open/reopen flows with persisted options files and compatibility checks.

## Risks and edge cases
`LoadOptionsFromFile()` assumes `config_options.env` is non-null. Cache injection only affects table factories whose options are `BlockBasedTableOptions`; other table factories are ignored. Latest-file selection by numeric timestamp ignores malformed or non-options files. Path joining uses `dbpath + "/" + options_file_name`.

## Test signals
`options_util_test.cc` covers save/load, cache injection, compatibility sanity, missing/bad/latest options files, future-version unknown options handling, directory renames, and WAL directory normalization.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/options/options_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/options/options_util_test.cc -->
# sources/storage-engines/rocksdb/utilities/options/options_util_test.cc

## Purpose
This file tests options utility behavior for persisting/loading options, cache injection, compatibility verification, latest OPTIONS file discovery, bad/future options handling, renamed DB directories, and WAL directory settings.

## Important APIs, types, and functions
`OptionsUtilTest` creates a memory Env and per-thread DB name. `SaveAndLoad` randomly initializes DB/CF options, persists them, loads them with escaped input strings, and verifies exact DB/CF/table factory matches. `SaveAndLoadWithCacheCheck` verifies that `LoadOptionsFromFile()` replaces block-based table factory caches with the caller-provided cache.

Dummy classes `DummyTableFactory`, `DummyMergeOperator`, and `DummySliceTransform` support compatibility negative/positive tests.

`SanityCheck` opens a DB with multiple CFs and persisted options, then verifies compatibility behavior for merge operator, prefix extractor, comparator, table factory, and `persist_user_defined_timestamps`.

`LatestOptionsNotFound`, `LoadLatestOptions`, `BadLatestOptions`, `RenameDatabaseDirectory`, `WalDirSettings`, and `WalDirInOptins` exercise latest-file lookup and parsing behavior under many filesystem and option-file scenarios.

## Control flow
Tests create options files either through `PersistRocksDBOptions()` or helper `WriteOptionsFile()`. They call utility APIs, then use `RocksDBOptionsParser` verification or DB reopen/read operations to validate results. Version-skew tests write synthetic OPTIONS files with unknown/invalid options under previous, current, future minor, and future major versions.

## State and persistence behavior
Most tests use an in-memory Env, but DB open tests create and destroy per-thread DB directories. Tests intentionally rely on DB open and `SetDBOptions`/`SetOptions` producing newer OPTIONS files. WAL directory tests inspect loaded `DBOptions::wal_dir` normalization after persisted options are read.

## Dependencies and integration points
The file depends on `options_util.h`, `env/mock_env.h`, filename parsing, options parser, RocksDB DB/table APIs, test harness/utilities, and gflags when enabled.

## Risks and edge cases
Tests mutate random options and must clean up compaction filters manually in `SaveAndLoad`. The test name `WalDirInOptins` contains a typo but verifies real behavior. Future-version behavior depends on parser version policy: unknown/invalid options can be ignored only under specific ignore/future-version combinations.

## Test signals
Coverage is strong for options file parsing/loading and compatibility policy. It directly validates the major integration points used by DB reopen and migration workflows.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/options/options_util_test.cc -->
