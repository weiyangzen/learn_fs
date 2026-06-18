# subset-b-008642 research

Grouped research for RocksDB public headers under `sources/storage-engines/rocksdb/include/rocksdb`. Each section is bounded for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/env.h -->
# sources/storage-engines/rocksdb/include/rocksdb/env.h

## Purpose

`env.h` defines RocksDB's historical public abstraction over the operating system environment. It covers file creation/opening, file IO primitives, directory and lock operations, dynamic library loading, logging, background thread pools, clocks, test directories, and helper wrappers. The top-level contract says `Env` implementations are safe for concurrent access, while individual returned file objects document their own synchronization rules. It is the compatibility bridge for older Env-based integrations and for newer FileSystem/SystemClock composition through `NewCompositeEnv`.

## Important APIs, types, and functions

The central type is `Env : public Customizable`, with factory/load entry points `Env::Default()`, `CreateFromString()`, and `CreateFromUri()`. `EnvOptions` carries file-open and IO tuning flags such as mmap, direct IO, fallocate, `bytes_per_sync`, `strict_bytes_per_sync`, write buffering, and rate limiting.

File abstractions are `SequentialFile`, `RandomAccessFile`, `WritableFile`, `RandomRWFile`, `MemoryMappedFileBuffer`, and `Directory`. They expose operations such as `Read`, `Skip`, `MultiRead`, `Append`, `PositionedAppend`, `Flush`, `Sync`, `Fsync`, `Truncate`, `InvalidateCache`, `Allocate`, and unique-id retrieval. `ReadRequest` represents batched random read inputs and per-request statuses. Logging is modeled by `Logger`, `InfoLogLevel`, free functions `Log`, `Info`, `Warn`, `Error`, `Fatal`, and `NewEnvLogger`. `FileLock` and `DynamicLibrary` model database locks and runtime symbol lookup.

`EnvWrapper` and the file wrappers forward calls to a target implementation, allowing partial behavioral overrides. `NewMemEnv`, `NewTimedEnv`, and `NewCompositeEnv` are extension factories.

## Control flow and behavior

DB code enters through `Env` methods to create files and directories, inspect filesystem state, lock DB paths, schedule background work, and query time. Most file open methods return owning `std::unique_ptr` objects and set `nullptr` on failure. `RandomAccessFile::MultiRead` defaults to a loop over `Read`, while `WritableFile::PrepareWrite` tracks preallocation blocks and calls `Allocate` when an append crosses a new block. `SyncFile` provides a path-level durability helper using writable reopen plus `Sync` or `Fsync` by default.

Thread control flows through `Schedule`, `UnSchedule`, `StartThread`, `StartThreadTyped`, and pool sizing calls. `StartThreadTyped` wraps typed arguments in `FunctorWrapper`, invokes the stored function inside a raw `StartThread` trampoline, then deletes the wrapper.

## State and persistence

`Env` owns optional `file_system_`, `system_clock_`, and `thread_status_updater_` pointers. `WritableFile` tracks preallocation state, IO priority, write lifetime hint, and strict range-sync behavior. Persistence semantics are explicitly layered: `Flush` makes data independent of process memory, `Sync` persists file data, `Fsync` persists metadata when overridden, and `Directory::Fsync` persists directory changes. `Close` is expected to surface final write errors, but objects still need destructor cleanup for unclosed resources.

## Dependencies and integration points

This header depends on `Customizable`, `Status`, `ThreadStatus`, `types`, `FunctorWrapper`, `FileSystem`, `SystemClock`, `DBOptions`, `ImmutableDBOptions`, `RateLimiter`, and `IOOptions`. It integrates directly with DB open options, compaction and WAL IO optimization, table file writing, logging, Env-based tests, plugin loading, and thread-status reporting. `EnvWrapper` is the key integration hook for instrumentation, encryption, rate limiting, in-memory filesystems, or partial overrides.

## Risks and test signals

The strongest risk is contract drift between base classes and wrappers; comments repeatedly require wrapper updates when methods are added. Implementations must not throw exceptions across RocksDB APIs. Direct IO users must respect alignment for offsets, lengths, and buffers. Incorrect `Flush`/`Sync`/`Fsync` semantics can lose data or metadata after crashes. `GetUniqueId` must avoid prefix ambiguity. Test signals include Env wrapper forwarding tests, direct-IO alignment and positioned append tests, crash/durability tests for `SyncFile`, background scheduling and unscheduling tests, logger level tests, and tests that default unsupported APIs return `NotSupported` without breaking callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/env_encryption.h -->
# sources/storage-engines/rocksdb/include/rocksdb/env_encryption.h

## Purpose

`env_encryption.h` declares the public encryption wrapper interfaces for storing RocksDB files encrypted at rest. It provides factories for an encrypted `Env` or encrypted `FileSystem`, cipher abstractions, an encryption provider contract, encrypted file wrappers, and an encrypted filesystem base class.

## Important APIs, types, and functions

Top-level factories are `NewEncryptedEnv(base_env, provider)` and `NewEncryptedFS(base_fs, provider)`. `BlockAccessCipherStream` defines random-access block encryption with `BlockSize`, `Encrypt`, `Decrypt`, protected `AllocateScratch`, `EncryptBlock`, and `DecryptBlock`. `BlockCipher : public Customizable` defines fixed-block `Encrypt`/`Decrypt`, `CreateFromString`, and a test-only `NewROT13Cipher`. `EncryptionProvider : public Customizable` creates per-file streams and prefixes through `GetPrefixLength`, `CreateNewPrefix`, `AddCipher`, `CreateCipherStream`, and optional `GetMarker`.

Encrypted wrappers include `EncryptedSequentialFile`, `EncryptedRandomAccessFile`, `EncryptedWritableFile`, and `EncryptedRandomRWFile`, all holding an underlying FS file plus a `BlockAccessCipherStream` and prefix length. `EncryptedFileSystem` extends `FileSystemWrapper` and exposes `AddCipher`.

## Control flow and behavior

On file creation, the provider creates a prefix and a cipher stream. Reads and writes are translated from logical user offsets to underlying file offsets after the encryption prefix. The sequential wrapper tracks `offset_` starting at `prefixLength_`; `Skip` and `Read` advance around encrypted payload offsets. Random-access reads, positioned writes, cache invalidation, range sync, preallocation, truncate, and file size all need prefix adjustment. The base `BlockAccessCipherStream` supports multi-block and partial-block encryption by dispatching to block-level methods with scratch storage.

## State and persistence

The persistent state added by encryption is the file prefix, which stores encryption options and usually aligns to page size for performance. Providers also hold cipher descriptors and read/write key state through `AddCipher`. File sizes visible to RocksDB exclude the prefix, while underlying persisted bytes include it. Durability is delegated to the wrapped filesystem's `Flush`, `Sync`, `Fsync`, and `Close`.

## Dependencies and integration points

The header depends on `Customizable`, `Env`, `FileSystem`, `Status`, and `Slice`. It integrates with RocksDB file creation and opening through `EnvOptions` and `FileOptions`, with the customization registry through `CreateFromString`, and with storage backends through `FileSystemWrapper`. It is designed to layer encryption without requiring table or DB code to understand encrypted bytes.

## Risks and test signals

Offset translation is the highest-risk behavior: prefix length must be consistently added for reads, writes, preallocation, truncation, and cache invalidation. The provider must preserve key compatibility for existing files, and `GetMarker` must not create false positives. The ROT13 cipher is explicitly test-only. Tests should cover partial block encryption, positioned reads/writes across block boundaries, prefix persistence and reopening, file size adjustment, unsupported `GetFileSize` fallback on encrypted random access files, key rotation/addition, and crash-safe flush/sync delegation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/env_encryption.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/experimental.h -->
# sources/storage-engines/rocksdb/include/rocksdb/experimental.h

## Purpose

`experimental.h` gathers APIs that are intentionally not stable. The file covers compaction helpers, manifest metadata update utilities, current-manifest checksum extraction, and a large experimental SST query filtering framework based on key segmentation and versioned filter configurations.

## Important APIs, types, and functions

The simple DB helpers are `SuggestCompactRange`, deprecated `PromoteL0`, `GetFileChecksumsFromCurrentManifest`, and `UpdateManifestForFilesState`. `UpdateManifestForFilesStateOptions` currently controls temperature refresh.

The filtering system centers on `KeySegmentsExtractor`, which maps keys or bounds into `Result { segment_ends, category }`. It defines `KeyCategory`, error pseudo-categories with filter/file/DB scope, `KeyCategorySet`, and `KeyKind` for full keys and iterator bounds. `MakeSharedCappedKeySegmentsExtractor` builds a safer fixed-width segment extractor.

Filter inputs are represented by `FilterInput`, a `std::variant` over `SelectWholeKey`, `SelectKeySegment`, `SelectKeySegmentRange`, and future selectors. `SstQueryFilterConfig` is the non-extensible base for concrete filter schemes. `MakeSharedBytewiseMinMaxSQFC` and `MakeSharedReverseBytewiseMinMaxSQFC` create min/max filters over selected inputs and categories. `SstQueryFilterConfigs` groups filters with an extractor. `SstQueryFilterConfigsManager` stores versioned named configurations and creates `Factory` objects that both collect table properties and produce table filters for range queries.

## Control flow and behavior

Manifest helper calls operate on closed or mostly quiescent DB directories, reading current metadata and writing updated manifest state when file temperature or future metadata is inconsistent. The filtering framework flows from extractor design to SST construction and read filtering. During table building, a factory writes configured filter properties. During reads, `GetTableFilterForRangeQuery` builds a predicate from lower and upper bounds and table properties, returning false for SSTs that definitely cannot match.

The lengthy inline comments are part of the behavioral contract: safe filtering depends on segment maximal prefix, common segment prefix, segment ordering, and category contiguousness properties. Version numbers in `SstQueryFilterConfigsManager` are immutable and gapless, with version 0 reserved for no filters.

## State and persistence

Compaction suggestions and L0 promotion affect LSM layout. Manifest update APIs persist metadata such as file temperatures and checksums. Query filter configs persist indirectly in SST table properties and must stay readable across code versions. Extractor `GetId()` is persistent compatibility state; changing behavior without changing the ID risks incorrect filtering of old files.

## Dependencies and integration points

The header depends on `data_structure`, `db`, `status`, table property collection, `FileSystem`, and checksum list interfaces. It integrates with compaction, manifest editing, `TablePropertiesCollectorFactory`, table filters, column family descriptors, and DB read options. The filtering system is meant to replace or extend older prefix-filter concepts while being version-managed in application code.

## Risks and test signals

The main risk is false-negative filtering: a bad extractor, category assignment, comparator mismatch, or mutated version can cause RocksDB to skip SSTs containing matching keys. The comments document many examples where delimiter handling or short-key categorization breaks correctness. Tests should include property-based extractor ordering checks, range-query filter correctness against full scans, version downgrade/upgrade matrix tests, SSTs written under old configs, unsupported config-name behavior, manifest update on live-changing directories, and checksum extraction from current manifests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/experimental.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/external_table.h -->
# sources/storage-engines/rocksdb/include/rocksdb/external_table.h

## Purpose

`external_table.h` declares an experimental plugin interface for using non-block-based table file implementations with RocksDB. External tables can be written through `SstFileWriter` and read through `SstFileReader`, with future ingestion into restricted RocksDB instances. The design supports total-order seek, prefix seek, or both.

## Important APIs, types, and functions

`ExternalTableIterator : public IteratorBase` adds `Prepare` for multi-scan planning, `NextAndGetResult`, `PrepareValue`, `value`, and `UpperBoundCheckResult`. `ExternalTableReader` creates iterators, serves `Get` and `MultiGet`, optionally returns a raw properties block, returns `TableProperties`, and optionally verifies checksums. `ExternalTableBuilder` writes sorted key/value pairs through `Add`, reports `status`, finalizes with `Finish`, cleans partial output with `Abandon`, returns `FileSize`, writes optional properties blocks, exposes table properties, and may expose whole-file checksum data.

`ExternalTableOptions` passes prefix extractor, comparator, filesystem, and file options to readers. `ExternalTableBuilderOptions` passes read/write options, prefix extractor, comparator, column family name, creation reason, and filesystem to builders. `ExternalTableFactory : public Customizable` creates readers and builders, and `NewExternalTableFactory` wraps it as a RocksDB `TableFactory`.

## Control flow and behavior

For writing, RocksDB calls `NewTableBuilder`, then `Add` in comparator order, checks `status`, and calls either `Finish` or `Abandon`. RocksDB owns final sync and close of the supplied `FSWritableFile`. For reading, RocksDB opens a reader, creates an iterator, optionally calls `Prepare` with scan options, seeks, iterates, and materializes lazy values through `PrepareValue` when needed. Point and batched lookups flow through `Get` and `MultiGet`.

## State and persistence

External table builders persist the table file and table properties. Minimum required properties are comparator name, entry count, raw key size, and raw value size. Optional raw properties blocks must be written as-is with returned offset and size. Optional checksums integrate with file checksum metadata using constants from `file_checksum.h`.

## Dependencies and integration points

The header depends on advanced iterator APIs, customizable, checksums, filesystem, iterator base, options, status, and table factory types. It integrates with `SstFileWriter`, `SstFileReader`, `ReadOptions`, `WriteOptions`, `SliceTransform`, `Comparator`, `FileSystem`, `FSWritableFile`, and `TableFactory` selection through column family options.

## Risks and test signals

The interface is explicitly experimental and subject to change. Correct key ordering is critical: total-order mode must obey the comparator globally, while prefix mode must maintain order within each prefix and honor `prefix_same_as_start`. Failure to return required properties can break metadata consumers. Lazy value preparation must be consistent with iterator validity. Tests should cover total-order and prefix seeks, forward/reverse iteration, `Prepare` reuse and interruption, `Get`/`MultiGet` status mapping, properties block round trips, checksum verification, `Abandon` cleanup, and not closing or syncing the file inside the builder.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/external_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/file_checksum.h -->
# sources/storage-engines/rocksdb/include/rocksdb/file_checksum.h

## Purpose

`file_checksum.h` defines RocksDB's public interfaces for whole-file checksum generation and manifest/ingestion checksum list handling. It lets table writers compute a checksum while writing and lets metadata APIs carry checksum values and function names for SST files.

## Important APIs, types, and functions

Constants define metadata states: `kUnknownFileChecksum` is the empty checksum, `kUnknownFileChecksumFuncName` means no factory was configured when written, `kNoFileChecksumFuncName` means no checksum metadata is available, and `kStandardDbFileChecksumFuncName` names the built-in CRC32C generator. `FileChecksumGenContext` passes `file_name` and requested checksum function name to factories.

`FileChecksumGenerator` has the lifecycle `Update` zero or more times, `Finalize` once, then `GetChecksum` and `Name`. `FileChecksumGenFactory : public Customizable` supports registry creation via `CreateFromString` and creates generators per file through `CreateFileChecksumGenerator`. `FileChecksumList` stores per-file checksum records with `reset`, `size`, `GetAllFileChecksums`, `SearchOneFileChecksum`, `InsertOneFileChecksum`, and `RemoveOneFileChecksum`. `NewFileChecksumList` and `GetFileChecksumGenCrc32cFactory` expose built-ins.

## Control flow and behavior

During table file writing, RocksDB or an external table builder creates a generator from the configured factory and updates it as bytes are written. After finalization, the checksum and function name can be stored in table properties or manifest metadata. Consumers use `FileChecksumList` to collect all checksums from a manifest or prepare checksum metadata for ingestion.

## State and persistence

The generator owns transient checksum accumulation state until finalized. Persistent checksum state is the checksum byte string and function name associated with a file number. Checksums may contain arbitrary non-printable bytes and should not be assumed to be human-readable. The built-in CRC32C factory uses big-endian encoding and is documented as compatible with many CRC32C implementations but unlike RocksDB's masked little-endian CRC32C usage elsewhere.

## Dependencies and integration points

The header depends on `Customizable` and `Status`. It integrates with file options metadata, external table builders, manifest checksum extraction in `experimental.h`, SST ingestion, and DB file checksum verification. Factories participate in the RocksDB configurable object registry.

## Risks and test signals

Lifecycle misuse is a risk: `GetChecksum` is only valid after `Finalize`, and factories should return `nullptr` for unrecognized requested names. Empty checksum strings are reserved for unknown state, so real generators should not return empty. Tests should cover generator lifecycle, CRC32C compatibility and byte order, unknown/unavailable metadata propagation, list insert/search/remove/reset behavior, duplicate file numbers, arbitrary binary checksum strings, and `CreateFromString` registry loading.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/file_checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/file_system.h -->
# sources/storage-engines/rocksdb/include/rocksdb/file_system.h

## Purpose

`file_system.h` defines RocksDB's newer, IOStatus-based storage abstraction. Compared with `Env`, it separates filesystem IO from clocks and thread pools, passes per-request `IOOptions` and `IODebugContext`, supports async reads and filesystem-owned buffers, and exposes richer file-open and metadata contracts for local or remote storage systems.

## Important APIs, types, and functions

`IOOptions` carries timeout, deprecated priority, rate-limiter priority, IO type, opaque property bag, directory fsync controls, recursion controls, verify-and-reconstruct-read, and IO activity. `DirFsyncOptions` explains why a directory fsync is needed. `FileOpenContract` declares constraints such as no reopen-for-write and no readers while open for write. `FileOptions : EnvOptions` adds embedded `IOOptions`, temperature, open contract, checksum handoff type, write hint, file checksum metadata, and optional file-open metadata.

`IODebugContext` records file path, counters, message, request id, trace data, cost info, and a shared mutex for implementation-side synchronization. `FileSystem : public Customizable` is the top-level factory for `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, `FSRandomRWFile`, memory-mapped buffers, directories, locks, loggers, and metadata operations. It also exposes `Poll`, `AbortIO`, `DiscardCacheForDirectory`, and `SupportedOps`.

File classes mirror `Env` classes but return `IOStatus` and accept `IOOptions` plus debug contexts. `FSReadRequest` supports synchronous `MultiRead`, asynchronous `ReadAsync`, and optional filesystem-owned buffers via `FSAllocationPtr`. Wrapper and owner-wrapper classes forward calls while optionally owning the wrapped object.

## Control flow and behavior

DB code opens files through `FileSystem` with `FileOptions`, then performs each IO with request-specific options and debug context. Default `GetChildrenFileAttributes` lists names, stats each child, and silently skips children deleted after listing. Default `FSRandomAccessFile::MultiRead` loops over `Read`; default `ReadAsync` performs synchronous read and invokes the callback before returning. `SupportedOps` defaults to async IO and prefetch support, and implementations must override it to advertise filesystem buffers or verify-and-reconstruct reads. `SyncFile` is the path-level durability hook for callers that need to sync a named file without violating file-open contracts.

## State and persistence

`FileSystem` itself has no mandated persistent state, but implementations may track DB path registration, caches, async handles, rate limiters, and metadata. `FSWritableFile` tracks preallocation blocks, IO priority, write hint, and strict `bytes_per_sync` behavior. Persistence semantics match `Env`: `Flush` makes data readable and independent of process memory, `Sync` persists data, `Fsync` persists metadata if implemented, directory fsync persists namespace changes, and `Close` surfaces final errors.

## Dependencies and integration points

The header depends on `env.h`, `io_status.h`, `options.h`, `table.h`, `thread_status.h`, `Customizable`, and C++ standard concurrency/utility types. It integrates with `DBOptions::env` through `NewCompositeEnv`, table building and reading, checksum handoff, remote filesystem optimizations, IO tracing, rate limiting, temperature-aware storage, direct IO, async reads, and custom object loading with `FileSystem::CreateFromString`.

## Risks and test signals

Implementations must respect no-exception contracts, thread-safety of the `FileSystem`, and individual file synchronization rules. Async IO is risky because callbacks, `io_handle`, deleters, `Poll`, and `AbortIO` must have clear ownership and completion semantics. Filesystem-owned read buffers require callers to use `result.data()` rather than assuming `fs_scratch` points to char data. `FileOptions` checksum metadata must distinguish unknown, unavailable, and empty-forbidden internal states. Tests should cover wrapper forwarding, IOOptions propagation, debug context copy/request id behavior, default `MultiRead` and async fallback, buffer ownership deleters, path-level sync with file-open contracts, directory listing races, preallocation, range sync strict mode, temperature reporting, and supported-ops gating.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/file_system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/filter_policy.h -->
# sources/storage-engines/rocksdb/include/rocksdb/filter_policy.h

## Purpose

`filter_policy.h` defines the public interface for SST filter generation and reading, primarily for Bloom and Ribbon filters in block-based tables. Filters let RocksDB avoid disk reads for keys that definitely are not present.

## Important APIs, types, and functions

`FilterBuildingContext` carries table options plus creation context such as compaction style, number of levels, logger, column family name, creation level, bottommost status, and file creation reason. `FilterPolicy : public Customizable` defines `CompatibilityName`, `CreateFromString`, `GetBuilderWithContext`, and `GetFilterBitsReader`. `FilterBitsBuilder` and `FilterBitsReader` are forward-declared internal details. Factory functions `NewBloomFilterPolicy` and `NewRibbonFilterPolicy` create built-in policies.

## Control flow and behavior

When building an SST, table code asks the policy for a builder using the contextual data. A policy can return `nullptr` to suppress filters or delegate to built-ins depending on level, compaction style, or reason. When reading an SST, table code asks for a reader over filter block contents. Built-in Bloom and Ribbon policies share a compatibility family, so readers can understand filters generated by related built-ins even when their customizable names differ.

## State and persistence

The policy object is configuration state. Persistent state is the filter block written into SST files plus the compatibility name needed to decide readability. Bloom filters use configured bits per key, with low values rounded to no-filter or minimum useful settings. Ribbon filters trade build CPU and temporary memory for lower persisted filter size and can be mixed with Bloom by level using `bloom_before_level`.

## Dependencies and integration points

The header depends on advanced options, customizable, status, types, block-based table options, table file creation reasons, and logger types. It integrates with `BlockBasedTableOptions::filter_policy`, configurable string loading, `SetOptions`, table builders/readers, custom comparators, and compaction-level-aware filter choices.

## Risks and test signals

The comparator warning is critical: using a filter that hashes full keys with a comparator that ignores some bytes can produce incorrect misses. Compatibility names must be forwarded by wrappers. Ribbon filters can use substantial temporary memory for very large filters. Tests should cover Bloom and Ribbon creation from strings, no-filter thresholds, compatibility-name behavior, custom policy delegation by `FilterBuildingContext`, reading old built-in filters, mutable `bloom_before_level`, and comparator/filter consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/filter_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/flush_block_policy.h -->
# sources/storage-engines/rocksdb/include/rocksdb/flush_block_policy.h

## Purpose

`flush_block_policy.h` defines the configurable policy that tells block-based table builders when to finish the current data block and start another. It is the extension point behind block boundary decisions.

## Important APIs, types, and functions

`FlushBlockPolicy` exposes one method, `Update(const Slice& key, const Slice& value)`, which tracks the key/value stream and returns whether the current block should be flushed. `FlushBlockPolicyFactory : public Customizable` creates policies with `CreateFromString` and virtual `NewFlushBlockPolicy(table_options, data_block_builder)`. `FlushBlockBySizePolicyFactory` is the built-in size-based factory with class name `FlushBlockBySizePolicyFactory` and static construction helper accepting target size, deviation, and `BlockBuilder`.

## Control flow and behavior

During table building, each added key/value is passed to the active policy. The policy inspects accumulated block-builder state and the incoming record, then returns true when the block should be emitted. The factory is configured in table options and creates a fresh policy per data block builder context. Built-in string loading supports default EveryKey or BySize policies.

## State and persistence

Policy objects own transient state about the current block and key/value sequence. They do not directly persist metadata, but their decisions determine data block boundaries in SST files, which affects index layout, compression, cache behavior, read amplification, and filter granularity.

## Dependencies and integration points

The header depends on `Customizable` and `table.h`, and forward-declares `Slice`, `BlockBuilder`, `ConfigOptions`, and `Options`. It integrates with `BlockBasedTableOptions`, block-based table builders, configurable option parsing, and any code that relies on predictable block sizes.

## Risks and test signals

Custom policies must not throw exceptions and must avoid decisions that produce pathological tiny or huge blocks unless intentionally configured. They must treat `key` and `value` as transient inputs and rely on builder metadata carefully. Tests should cover factory string creation, default by-size behavior, deviation handling, EveryKey behavior if configured, block size distribution, and table read correctness after custom flush boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/flush_block_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/functor_wrapper.h -->
# sources/storage-engines/rocksdb/include/rocksdb/functor_wrapper.h

## Purpose

`functor_wrapper.h` is a small C++11 compatibility helper used to store a typed callable and its arguments behind a raw `void*` thread entry point. In this source set it supports `Env::StartThreadTyped`.

## Important APIs, types, and functions

The `detail` namespace implements a compile-time index sequence: `IndexSequence`, recursive `IndexSequenceHelper`, `make_index_sequence`, and overloaded `call` helpers that expand tuple elements into a callable. `FunctorWrapper<Args...>` stores `std::function<void(Args...)>` and `std::tuple<Args...>`, and exposes `invoke()` to call the function with the stored tuple values.

## Control flow and behavior

`Env::StartThreadTyped` constructs a `FunctorWrapper` with a callable and forwarded arguments, passes it to `StartThread` as a raw pointer, and uses a trampoline to call `invoke()` and delete the wrapper after the thread function returns. `detail::call` computes tuple size at compile time, builds an index sequence, and expands `std::get<I>(t)...` into the stored function.

## State and persistence

The wrapper owns only transient in-memory state for a scheduled thread invocation: the `std::function` and copied or moved argument tuple. It has no persistence behavior. Ownership is manual because it is passed through a C-style `void*` API; deletion is expected in the trampoline.

## Dependencies and integration points

The header depends on `<functional>`, `<memory>`, `<utility>`, tuple support through included standard headers, and RocksDB namespace definitions. Its practical integration point is `env.h`, where it adapts typed C++ callables to the raw function pointer API exposed by `Env::StartThread`.

## Risks and test signals

Argument lifetime and move/copy semantics are the main risks. The constructor stores `Args...` in a tuple, so references and move-only arguments need careful template behavior. If the trampoline is bypassed or thread creation fails after allocation, the wrapper could leak. Tests should cover typed thread launch with multiple arguments, moved values, reference-like wrappers if supported, deletion after invocation, and exception policy alignment because exceptions must not escape into RocksDB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/functor_wrapper.h -->
