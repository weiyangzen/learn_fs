# subset-b-008540 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/open_test.go -->
# sources/storage-engines/pebble/open_test.go

## Purpose

`open_test.go` is a broad regression and behavior suite for Pebble database opening, closing, file naming, locking, OPTIONS compatibility, read-only mode, WAL replay, WAL corruption detection, WAL failover, crash recovery, consistency checking, and disabled-WAL persistence. The file does not implement production open logic, but it is one of the most important signals for the expected durability and recovery contract around `Open`, `Close`, `GetVersion`, `Peek`, `mkdirAllAndSyncParents`, WAL directory migration, and file-system failure handling.

## Important APIs, Types, and Helpers

- `TestOpenSharedFileCache` verifies that `Options.FileCache` is honored and shared across DB instances when paired with a shared block cache.
- `TestErrorIfExists`, `TestErrorIfNotExists`, and `TestErrorIfNotPristine` cover user-visible open guard options and their error identities: `ErrDBAlreadyExists`, `ErrDBDoesNotExist`, and `ErrDBNotPristine`.
- `TestOpenFormatVersion1NotSupported` asserts that old format-version-1 stores are rejected clearly instead of being treated as empty directories.
- `TestOpen_WALFailover` is datadriven and exercises opening with primary WAL dirs, secondary failover dirs, recovery dirs, identifier files, missing-dir allowances, file listing, stat, and log inspection.
- `TestOpenRecovery` is datadriven and verifies recovery after defining DB state, committing batches, closing, and reopening with changed options.
- `TestOpenAlreadyLocked` covers automatic and caller-provided locks on the data dir, primary WAL dir, secondary WAL dir, and WAL recovery dirs across memfs, disk absolute paths, and disk relative paths.
- `TestNewDBFilenames`, `testOpenCloseOpenClose`, and `TestOpenCloseOpenClose` verify expected newly created file names, repeated open/close persistence, external or store-relative WAL paths, and single live OPTIONS file retention.
- `TestOpenOptionsCheck` and `TestOpenCrashWritingOptions` check persisted OPTIONS compatibility and tolerance of a torn OPTIONS write.
- `optionsTornWriteFS` and `optionsTornWriteFile` simulate a partial write that fails around the serialized `comparer=` field.
- `TestOpenReadOnly` verifies read-only behavior, including non-mutating failed opens, write API failures, iterator/snapshot/indexed-batch reads, and unchanged directory contents.
- WAL replay tests include `TestOpenWALReplay`, `TestWALReplaySequenceNumBug`, `TestOpenWALReplay2`, `TestTwoWALReplayCorrupt`, `TestCrashOpenCrashAfterWALCreation`, `TestOpenWALReplayReadOnlySeqNums`, and `TestOpenWALReplayMemtableGrowth`.
- Crash/corruption randomized tests include `TestWALFailoverRandomized`, `runRandomizedCrashTest`, `TestWALHardCrashRandomized`, `TestWALCorruption`, `TestWALCorruptionBitFlip`, and `TestCrashDuringOpenRandomized`.
- `ensureFilesClosed`, `closeTrackingFS`, and `closeTrackingFile` instrument VFS file handles to catch leaked files in open tests.
- `TestCheckConsistency` builds synthetic `manifest.Version` state and on-disk table files for datadriven consistency checks.
- `TestOpenRatchetsNextFileNum` exercises shared-object storage and next-file-number ratcheting during reopen and open-triggered compactions.
- `TestMkdirAllAndSyncParents`, `TestPeek`, `TestGetVersion`, `TestOpenNeverFlushed`, `TestOpen_ErrorIfUnknownFormatVersion`, and `TestDisableWAL` cover targeted open-adjacent behavior.

## Control Flow and State

Most tests follow the same lifecycle: construct `Options` with a memory, crashable memory, logging, error-injecting, or real filesystem; call `Open`; write keys, flush, compact, ingest, or manipulate DB internals; close; mutate files or crash-clone the filesystem; reopen; then assert either successful state recovery or a specific error. Several tests deliberately inspect or modify internal guarded state under `d.mu`, including `d.mu.compact.flushing`, `d.mu.mem.queue`, `d.mu.versions`, `d.mu.compact.compactingCount`, and file deletion toggles.

The WAL replay tests use value sizes and memtable sizes to force specific replay shapes: one or more WALs, large batches in flushable batches, flushed sstables plus trailing logs, read-only replay without flush-on-open, and manifest sequence numbers ahead of unflushed WAL sequence numbers. The randomized crash runner maintains an expected key-state array with `kvUnset`, `kvMaybeSet`, and `kvSet` so crash clones can validate all recovered keys against conservative durability expectations.

Locking tests pre-acquire different lock combinations and verify that `Open` handles owned locks correctly, rejects concurrent opens on the same data/WAL/secondary directory, and releases references after close. WAL failover tests use datadriven commands to create and reopen stores under evolving primary, secondary, and recovery configurations.

## Persistence and Durability Behavior

This file is heavily focused on persistence. It verifies that:

- Open creates format markers, manifests, OPTIONS files, locks, and WALs with expected names.
- Reopen preserves keys across normal close, read-only replay, WAL-only state, flushed state, ingested-only state, disabled-WAL state after flush, and remote/shared object configurations.
- Corrupted WAL records and bit flips are detected as `ErrCorruption`.
- Strict WAL tail behavior prevents replay past a corrupt earlier WAL when later WALs exist.
- Crash windows during open and immediately after WAL creation remain recoverable.
- Read-only opens do not create or mutate files beyond expected lock handling and keep directory contents unchanged.
- Torn OPTIONS writes do not poison the store because later opens can ignore or recover from incomplete newer OPTIONS files.
- WAL directory changes require appropriate current or recovery directory configuration unless unsafe missing-WAL-dir allowance is explicitly set.

## Dependencies and Integration Points

The tests integrate with `vfs` memory, crashable, logging, default disk, and error-injecting filesystems; `wal` failover and stable identifiers; `atomicfs` marker files; `manifest` versions and table metadata; `objstorageprovider` and `remote` shared storage; `sstable` writers; `datadriven` test fixtures; `metamorphic.Weighted` randomized operation scheduling; `stream` for log slicing; `testkeys`, `testutils`, `leaktest`, `require`, and `pretty` for assertions and diagnostics.

Production integration points under test include `Open`, `DB.Close`, `DB.Set`, `DB.Flush`, `DB.AsyncFlush`, `DB.Compact`, `DB.Ingest`, `DB.Get`, `DB.NewIter`, `Batch`, `Snapshot`, `Peek`, `GetVersion`, `checkConsistency`, `mkdirAllAndSyncParents`, file cache sharing, WAL replay, manifest replay, directory locking, cleaner behavior, shared-object file-number allocation, and read-only API enforcement.

## Risks and Edge Cases

- Many tests depend on carefully shaped LSM/WAL state. Changes to memtable growth, large-batch thresholds, flush scheduling, table-file naming, format marker names, or cleaner timing can invalidate assumptions.
- Randomized crash tests are high-value but can be seed-sensitive. Failures need seed preservation and may indicate real durability regressions.
- Some tests reach into internal mutex-protected state, so refactors of DB internals may require test rewrites even when public behavior is unchanged.
- Read-only behavior is subtle: replay must expose data without creating durable side effects or scheduling flushes.
- WAL failover and WAL recovery-dir compatibility guard against data loss; relaxing errors or path resolution can make missing WALs silently unrecoverable.
- The file-closure checker wraps selected tests and can surface leaks introduced by new open paths or early-return error handling.

## Test Signals

The whole file is test code. It provides direct signals for open-time correctness, crash safety, idempotent reopening, file naming, WAL corruption detection, read-only semantics, lock behavior, option compatibility, object-storage integration, and disabled-WAL behavior. Datadriven fixture coverage makes expected filesystem and LSM output explicit, while randomized crash tests broaden coverage over timing and durability interleavings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/open_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/options.go -->
# sources/storage-engines/pebble/options.go

## Purpose

`options.go` defines Pebble's public and internal configuration surface. It contains option structs for iterators, writes, levels, DB-wide behavior, WAL failover, value separation, span policies, compression, table filters, object storage, and user-key categorization. It also implements defaulting, OPTIONS serialization/parsing, compatibility checks against previously persisted options, validation, and conversion into lower-level sstable/blob/object-storage settings.

## Important APIs, Types, and Functions

- Public aliases expose internal/base and sstable types such as `SpanPolicy`, `ValueStoragePolicyAdjustment`, `TieringPolicy`, `UserKeyBounds`, `TableFilterPolicy`, `KeySchema`, `BlockPropertyCollector`, `BlockPropertyFilter`, `MaximumSuffixProperty`, `ShortAttributeExtractor`, and `UserKeyPrefixBound`.
- `IterKeyType` and `IteratorStack` enumerate iterator key modes and the legacy/V2 iterator implementation selection.
- `IterOptions` controls iterator bounds, point/range block filters, key types, range-key masking, durable-only reads, L6 filter use, stats category, tracking exemption, debugging, and internal iterator fields.
- `RangeKeyMasking` and `BlockPropertyFilterMask` support automatic point-key masking by range keys, optionally accelerated by suffix-aware block-property filters.
- `WriteOptions`, `Sync`, `NoSync`, and `GetSync` define per-write sync behavior.
- `LevelOptions` configures per-level block sizes, restart intervals, compression, filters, and index block size. `EnsureL0Defaults` and `EnsureL1PlusDefaults` fill defaults.
- `Options` is the main DB configuration struct. It spans cache, cleaner, comparer, debug checks, WAL behavior, open guard flags, event listeners, compaction knobs, read sampling, tombstone compaction, format major version, VFS, key schemas, locks, LSM sizing, logging/tracing, memtables, merger, concurrency, read-only mode, shared cache, block properties, remote storage, value separation, span policies, iterator tracking, table filters, flush delays, WAL recovery/failover, deletion pacing, allocator hints, unsafe options, and private test/internal knobs.
- `ValueSeparationPolicy`, `ValueStorageLatencyTolerant`, `ValueStorageLowReadLatency`, `SpanPolicyFunc`, and `MakeStaticSpanPolicyFunc` configure blob/value-placement policy by key span.
- `WALFailoverOptions.Validate` checks secondary WAL configuration.
- `DBCompressionSettings`, predefined compression profiles, `UniformDBCompressionSettings`, and `Options.ApplyCompressionSettings` configure compression across levels.
- `DBTableFilterPolicy`, progressive Bloom and binary-fuse filter profiles, `UniformDBTableFilterPolicy`, and `Options.ApplyTableFilterPolicy` configure filters per level.
- `Options.EnsureDefaults`, `DefaultOptions`, `WithFSDefaults`, `AddEventListener`, and `Clone` initialize and manipulate option values.
- `Options.String`, `parseOptions`, `ParseHooks`, and `Options.Parse` serialize and parse the OPTIONS file format, including RocksDB-compatible section/key mapping.
- `ErrMissingWALRecoveryDir`, `ErrSecondaryIdentifierMismatch`, `CheckCompatibility`, `checkWALDir`, `MakeStoreRelativePath`, `resolveStorePath`, and `validateWALRecoveryDirIdentifier` enforce compatibility and WAL recovery safety.
- `Validate`, `MakeReaderOptions`, `MakeWriterOptions`, `DB.makeWriterOptions`, `DB.makeBlobWriterOptions`, and `MakeObjStorageProviderSettings` translate validated options into runtime subsystems.
- `UserKeyCategories`, `UserKeyCategory`, `MakeUserKeyCategories`, `CategorizeKey`, and `CategorizeKeyRange` classify key ranges for informational labels.

## Control Flow and State

`EnsureDefaults` is the central defaulting path and is expected before validation and use. It fills cache size, comparer, cleaner, deletion pacing, ingest behavior, iterator stack, compaction concurrency, value separation policy, table filter decoders, key schema defaults, L0/level sizing, per-level defaults, logger/listener, manifest and file limits, memtable sizing, merger, format major version, filesystem wrappers, flush split bytes, WAL failover defaults, read sampling, tombstone thresholds, file-cache shards, multilevel compaction heuristic, span policy, virtual table rewrite threshold, and time functions.

`Options.String` serializes a stable OPTIONS representation with `[Version]`, `[Options]`, optional `[Value Separation]`, optional `[WAL Failover]`, and one `[Level "N"]` section per level. Private options are serialized only when true. Dynamic option functions are called at serialization time, so the persisted text captures current values rather than closures.

`parseOptions` scans the INI-like text line by line, maps RocksDB `CFOptions "default"` keys for comparer and merger compatibility, and delegates section/key handling through callbacks. `Options.Parse` uses this scanner to populate fields, parse durations/numbers/bools, invoke hooks for custom cleaner/comparer/filter/key-schema/merger implementations, tolerate unknown options with logging or `OnUnknown`, and reconstruct closure-backed fields for parsed values.

`CheckCompatibility` scans previous OPTIONS text for comparer, merger, WAL dir, and WAL failover secondary dir. It uses `checkWALDir` to ensure any previously relevant WAL directory is still current or listed in `WALRecoveryDirs`, unless unsafe missing-dir allowance is enabled. Identifier validation is only applied when a recovery dir matches the current secondary WAL directory, avoiding false failures for old secondaries.

`MakeStaticSpanPolicyFunc` builds a sorted, compacted boundary list from non-overlapping input spans, fills gaps with default policies, and returns a function that binary-searches by the requested start key to produce the span policy valid for that interval.

## Persistence Behavior

The serialized OPTIONS string is persisted to disk and later parsed for compatibility checks during open. Comparer and merger names are treated as compatibility-critical because changing them can make existing keys unreadable or incorrectly ordered. WAL directory history is also persistence-critical: if a previous primary or secondary WAL directory may contain unflushed logs, opening without listing it in current WAL locations or recovery dirs returns `ErrMissingWALRecoveryDir`.

`MakeStoreRelativePath` and `resolveStorePath` support portable WAL path encoding using `{store_path}`. `validateWALRecoveryDirIdentifier` reads `wal.StableIdentifierFilename` when available to protect against using the wrong current secondary disk.

Format major version defaulting is sensitive to shared objects: `FormatDefault` maps to `FormatMinSupported`, but `CreateOnShared` raises the default to the minimum format for shared objects. Validation also rejects incompatible `CreateOnShared` and format-version combinations.

## Dependencies and Integration Points

This file ties the public `pebble` package to many internal subsystems: `base` comparers, filters, key bounds, locks, and span policies; `cache`; `deletepacer`; `humanize`; `invariants`; `keyspan`; `manifest`; `objstorageprovider`; `remote`; `rangekey`; `sstable`, `blob`, `block`, `colblk`, `tablefilters`, `binaryfuse`, and `bloom`; `vfs`; `wal`; and `redact`. Runtime users include `Open`, iterator constructors, table readers/writers, blob writers, compaction/flush paths, WAL failover/recovery code, object storage providers, event listeners, file caches, and diagnostics.

## Risks and Edge Cases

- `Options` contains many closure-backed fields. Capturing loop indices correctly in `ApplyCompressionSettings` and `ApplyTableFilterPolicy` is essential; both functions copy the index before creating closures.
- `EnsureDefaults` mutates the receiver and can install wrappers around `FS`, including disk-health checking with a closer stored privately. Callers sharing `Options` must account for mutation.
- `Parse` intentionally tolerates many unknown fields for forward compatibility, but malformed known fields should fail. Overly strict parsing could break older/newer OPTIONS files; overly lax parsing could miss unsafe incompatibility.
- WAL directory compatibility is data-loss sensitive. Path resolution, `{store_path}` handling, secondary identifiers, and unsafe bypasses must remain conservative.
- `Validate` assumes defaults have already been applied. Calling it on raw options may produce misleading results or panic if closure fields are nil.
- User key categories require sorted upper bounds and a nil upper bound for the final category; invalid input panics.
- `MakeWriterOptions` panics if a selected key schema is missing. This is correct for internal invariants but means defaulting/validation must run first.

## Test Signals

`options_test.go` covers target file sizing, default string stability, parse/string round trips, RocksDB compatibility parsing, WAL recovery-dir compatibility, WAL identifier validation, invalid levels, validation failures, key categories, compression/table-filter policy closures, and static span policy behavior. `open_test.go` indirectly validates OPTIONS persistence, compatibility checks, WAL dir migration safety, and torn OPTIONS write handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/options_test.go -->
# sources/storage-engines/pebble/options_test.go

## Purpose

`options_test.go` verifies the behavior defined by `options.go`: randomized test defaulting, target file-size computation, exact default OPTIONS serialization, compatibility checks, WAL recovery directory validation, parse/string round trips, validation errors, key category classification, compression/table-filter policy application, and static span policy lookup. It is the focused test companion for Pebble's configuration surface.

## Important APIs, Types, and Functions

- `(*Options).randomizeForTesting` installs a test logger, randomizes `FormatMajorVersion` when unset, optionally randomizes value separation policy for formats that support it, optionally enables iterator tracking, and then calls `EnsureDefaults`.
- `testingRandomized` is a helper wrapper used across tests in this package.
- `TestTargetFileSize` checks `Options.TargetFileSize` for L0, base-level-relative target sizes, and shifted base levels.
- `TestDefaultOptionsString` pins `runtime.GOMAXPROCS`, forces `IteratorStackV1`, and asserts the full string emitted by `DefaultOptions().String()`.
- `TestOptionsCheckCompatibility` checks comparer and merger compatibility, RocksDB-style options parsing, `nullptr` merger handling, WAL dir and failover secondary migration checks, and `ErrMissingWALRecoveryDir` values.
- `TestWALRecoveryDirValidation` verifies that stale/old secondary recovery directories do not have their stable identifiers validated unless they are the current secondary.
- `writeTestIdentifierToFile` writes a stable identifier fixture into a VFS file and syncs it.
- `testCleaner` is a custom cleaner used to test parse hooks.
- `TestOptionsParse` constructs customized options, serializes them, parses them into a new `Options` with `ParseHooks`, and compares the resulting string.
- `TestOptionsParseLevelNoQuotes`, `TestOptionsParseInvalidLevel`, and `TestOptionsParseComparerOverwrite` target level section parsing and unknown-comparer behavior.
- `TestOptionsValidate` covers validation errors for compaction concurrency, L0 thresholds, memtable size, memtable stop-write threshold, and missing WAL failover secondary FS.
- `TestKeyCategories` verifies point-key and range-key category labels.
- `TestApplyDBCompressionSettings` and `TestApplyDBTableFilterPolicy` ensure dynamic profile closures are reflected across levels.
- `TestStaticSpanPolicyFunc` is datadriven and checks span policy selection over parsed key bounds.

## Control Flow and State

The tests mostly construct `Options`, call `EnsureDefaults`, serialize with `String`, parse with `Parse`, or validate with `Validate`. The parse round-trip test deliberately sets many fields before defaulting, including WAL failover, level options, deletion pacing, compaction knobs, tombstone thresholds, file-cache shards, secondary cache size, and value separation policy. It then ensures that the serialized and reparsed forms match exactly while confirming non-serialized runtime state like `Cache` remains nil.

Compatibility tests pass previous OPTIONS strings directly to `CheckCompatibility`, checking both Pebble's `[Options]` section and RocksDB's `[CFOptions "default"]` mapping. WAL migration cases inspect typed errors with `errors.As` and compare the reported directory. The WAL recovery identifier test creates directories and identifier files in `vfs.NewMem`, then calls the unexported `checkWALDir` path to ensure only the current secondary directory validates IDs.

The key category tests build a `UserKeyCategories` partition with sorted upper bounds, then test both single-key classification and range classification that may span multiple categories. Static span policy tests parse datadriven command args into `SpanPolicy` ranges and query `MakeStaticSpanPolicyFunc` for each input bound.

## Persistence and Compatibility Behavior

The file treats the OPTIONS string as a persisted compatibility contract. `TestDefaultOptionsString` detects accidental serialization changes to defaults. `TestOptionsParse` verifies that a persisted string can reconstruct all parseable fields. `TestOptionsCheckCompatibility` encodes the most important persisted-safety checks: comparer and merger identity, previous WAL directories, failover secondary directories, RocksDB import compatibility, and the explicit recovery-dir requirement for locations that may still contain WALs.

`TestWALRecoveryDirValidation` is a nuanced persistence signal: old secondary directories may carry IDs from past configurations and should still be usable for recovery without matching the current secondary ID. The check only validates identifiers for the current secondary, preventing false-open failures during WAL failover migrations.

## Dependencies and Integration Points

The tests use `leaktest`, `require`, `datadriven`, `errors`, `vfs`, `wal`, `base`, `strparse`, `testkeys`, `testutils`, `block`, `bloom`, and `crstrings`. They directly exercise `Options`, `ParseHooks`, `Cleaner`, `WALFailoverOptions`, `ValueSeparationPolicy`, `DBCompressionSettings`, `DBTableFilterPolicy`, `UserKeyCategories`, and `SpanPolicyFunc`, and indirectly guard `Open` because these persisted options are read during database startup.

## Risks and Edge Cases

- `TestDefaultOptionsString` is intentionally brittle. Any intentional default or serialization change requires updating the full expected string and considering on-disk compatibility.
- Randomization in `randomizeForTesting` broadens coverage but can make failures seed-dependent through format versions, value separation, and iterator tracking.
- Parse hooks must preserve existing fields when hooks cannot resolve custom names; `TestOptionsParseComparerOverwrite` guards against niling a comparer on unknown input.
- WAL dir compatibility tests are safety-critical because accepting an omitted recovery dir can lose unflushed writes.
- Closure-backed compression and filter policies must capture per-level indices correctly and must respond to later profile changes.
- Category and span-policy helpers panic on invalid construction, so tests focus on valid mappings rather than recovery from invalid caller input.

## Test Signals

This file is itself the direct test signal for `options.go`. It provides exact default-output regression coverage, parser compatibility coverage, validation coverage, and targeted behavioral checks for policy helpers. It complements `open_test.go`, which verifies that these options behave correctly when persisted and used by real DB opens.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/overlap.go -->
# sources/storage-engines/pebble/overlap.go

## Purpose

`overlap.go` adapts Pebble's DB/version/table iterator machinery to the internal `overlap` package. It defines `overlapChecker`, a thin implementation of `overlap.IteratorFactory`, and uses it to determine whether a requested user-key bound overlaps point keys, range deletions, or range keys in an LSM version.

## Important APIs, Types, and Functions

- `overlapChecker` holds the comparer, table iterator factory, iterator options, target `manifest.Version`, object-storage provider, and a `skipRemoteProbe` flag.
- `(*overlapChecker).DetermineLSMOverlap(ctx, bounds)` constructs an `overlap.Checker` with the user-key comparator and itself as iterator factory, optionally installs a remote-table skip predicate, and calls `LSMOverlap`.
- `var _ overlap.IteratorFactory = (*overlapChecker)(nil)` is a compile-time interface assertion.
- `Points(ctx, m)` opens point-key iterators for a table using `newIters(..., iterPointKeys)` and returns `iters.point`.
- `RangeDels(ctx, m)` opens range-deletion iterators using `iterRangeDeletions` and returns `iters.rangeDeletion`.
- `RangeKeys(ctx, m)` opens range-key iterators using `iterRangeKeys` and returns `iters.rangeKey`.

## Control Flow and State

The type is stateful only by holding references needed to open table iterators and inspect the current version. `DetermineLSMOverlap` delegates the actual overlap algorithm to `internal/overlap`. If `skipRemoteProbe` is set, it assigns `checker.SkipProbe` to return true for tables whose backing file is not local according to `objstorage.IsLocalTable`. Local tables are still probed normally.

The iterator methods all use the same pattern: call the `tableNewIters` function with context, table metadata, the checker's `IterOptions`, default `internalIterOpts`, and a specific key-kind selector. Errors propagate immediately. Successful calls return only the iterator type requested by the `overlap.IteratorFactory` interface.

## Persistence and State Behavior

This file does not persist state. It reads existing LSM metadata from `manifest.Version` and opens table iterators through the configured object provider. Its behavior depends on current table locality when `skipRemoteProbe` is active, meaning overlap results may conservatively avoid probing remote-backed tables while still using metadata-level overlap logic provided by the checker.

## Dependencies and Integration Points

Dependencies include `context`, `internal/base` for comparers, bounds, and internal iterators; `internal/keyspan` for range deletion/key iterators; `internal/manifest` for table metadata and versions; `internal/overlap` for the main overlap algorithm; and `objstorage` for local-vs-remote table detection. The code integrates with Pebble table opening through `tableNewIters`, `internalIterOpts`, and iterator-kind constants.

Likely callers are DB code paths that need to determine whether a key span overlaps existing LSM contents before choosing an operation strategy, for example ingestion/excise/delete-only compaction checks or remote-object-aware probing.

## Risks and Edge Cases

- Iterator resource ownership is delegated to the `overlap` checker. Any future change must preserve correct closing semantics in the caller/algorithm.
- `skipRemoteProbe` can change overlap precision for remote-backed tables. It must only be used by callers that can tolerate skipped probing and rely on conservative metadata behavior.
- Passing the wrong `iterPointKeys`, `iterRangeDeletions`, or `iterRangeKeys` selector would silently produce incomplete overlap checks.
- `IterOptions` bounds and filters may affect opened iterators; callers must provide options compatible with the bounds they ask the overlap checker to evaluate.

## Test Signals

There are no tests in this file. Coverage is expected through higher-level tests for operations that call overlap detection. Useful targeted tests would mock table metadata with local and remote backings, assert `SkipProbe` behavior, and verify that point, range deletion, and range key overlaps each request the correct iterator kind.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/overlap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/range_del_test.go -->
# sources/storage-engines/pebble/range_del_test.go

## Purpose

`range_del_test.go` tests and benchmarks Pebble range deletion behavior. It covers datadriven range tombstone semantics, delayed flushing for range deletions and range keys, stress around concurrent delayed flush triggers, correctness of range tombstone truncation during compactions across levels, and iterator performance when many keys are covered by tombstones.

## Important APIs, Types, and Functions

- `TestRangeDel` runs `testdata/range_del` with commands for defining DB contents, waiting for table stats, compacting, getting keys, and iterating at optional sequence numbers.
- `TestFlushDelay` verifies that all supported ways to write range deletions or range keys trigger the configured flush delay: direct DB calls, batch commits, deferred batch operations, `SetRepr`, and `Apply`.
- `TestFlushDelayStress` runs concurrent random `DeleteRange`, `RangeKeySet`, and `Set` operations with small memtables and flush delays under `synctest`.
- `TestRangeDelCompactionTruncation`, `TestRangeDelCompactionTruncation2`, and `TestRangeDelCompactionTruncation3` construct small target-file-size LSMs to verify range tombstones are truncated to compaction/table boundaries and do not incorrectly delete newer keys in lower levels.
- `BenchmarkRangeDelIterate` and `benchmarkRangeDelIterate` measure iterator behavior when an ingested sstable is mostly or fully covered by a range tombstone, with and without a snapshot plus compaction scenario.

## Control Flow and State

`TestRangeDel` manages a single DB across datadriven commands. `define` closes any prior DB, opens a new one with automatic compactions disabled, forces base level 1 for deterministic output, and returns memtable/version state. `compact` runs a command helper, again forces base level 1, and returns the current version string. `get` and `iter` query visible state, with `iter` able to use a custom sequence number by constructing a `Snapshot` with `base.SeqNum`.

`TestFlushDelay` opens a memfs DB with both `FlushDelayDeleteRange` and `FlushDelayRangeKey` set. Before each write case, it captures the current mutable memtable's `flushed` channel under `d.mu`; after the write commits, it waits on that channel, proving the delayed flush fired. The cases deliberately cover alternate write paths so range operations cannot bypass the flush-delay accounting.

`TestFlushDelayStress` repeats randomized concurrent writes across multiple DB instances. It uses `runtime.GOMAXPROCS(0)` writers, randomized keys, tiny memtables, and short sleeps before waiting for all writers. This is mainly a race/deadlock/regression signal around scheduling delayed flushes while memtables rotate.

The compaction truncation tests force specific LSM shapes by using small `TargetFileSizes`, snapshots that preserve old versions, manual compactions over narrow bounds, and direct version string assertions. They verify both positive visibility (`Get("b")` succeeds when a higher-level tombstone should not cover it) and negative visibility (`ErrNotFound` remains correct after further compactions).

The benchmark builds an external sstable with `sstable.NewRawWriter`, ingests it, writes a range tombstone covering most or all keys, optionally holds a snapshot and compacts, and repeatedly creates an iterator and seeks to the tombstone start.

## Persistence and State Behavior

The tests exercise persistent state through flushed sstables, ingested external sstables, WAL-backed writes, snapshots, range tombstones, and compaction outputs. Range tombstones are persisted in sstable range-deletion blocks and may have wider bounds on disk than an individual output table. The truncation tests specifically guard the invariant that in-memory/table metadata boundaries used during compaction prevent a tombstone in one table or level from deleting newer keys outside its effective file/compaction bounds.

Flush-delay tests verify memtable lifecycle state: once a range deletion or range key is added, Pebble should schedule a flush so disk space can be reclaimed and lazy combined iteration is not blocked indefinitely. The stress test probes this behavior under concurrent writes and memtable rotation.

## Dependencies and Integration Points

The file depends on `datadriven`, `synctest`, `leaktest`, `require`, `vfs`, `manifest`, `testkeys`, `testutils`, `objstorageprovider`, `sstable`, and Pebble helpers such as `runDBDefineCmd`, `runCompactCmd`, `runGetCmd`, `runIterCmd`, `runWaitForTableStatsCmd`, `closeAllSnapshots`, and `randStr`.

Production APIs under test include `DB.DeleteRange`, `Batch.DeleteRange`, `Batch.DeleteRangeDeferred`, `Batch.SetRepr`, `Batch.Apply`, `DB.RangeKeySet`, `DB.RangeKeyUnset`, `DB.RangeKeyDelete`, range-key batch operations, `DB.Flush`, `DB.Compact`, `DB.Get`, `DB.NewIter`, `DB.Ingest`, snapshots, and internal version/compaction state.

## Risks and Edge Cases

- The compaction truncation tests are tightly coupled to file sizing, estimated sizes, format versions, and resulting file numbers. Comments acknowledge that some scenarios need future datadriven rewrites for newer table formats.
- Range tombstone correctness is subtle because on-disk tombstone spans may exceed table boundaries. Bugs can cause deletion of newer keys in lower levels or incorrect LSM bounds expansion.
- Flush-delay behavior must avoid both missed flushes and excessive flush churn. Concurrent stress helps catch races but may still be timing-sensitive.
- Tests manipulate internal DB state such as `dynamicBaseLevel`, `forceBaseLevel1`, and version strings, so compaction picker or LSM formatting changes may require updates.
- Benchmarks ingest generated sstables and use snapshots to reproduce known expensive iteration patterns; changes to iterator tombstone skipping may shift results significantly.

## Test Signals

This file is direct test coverage for range deletion behavior. It provides datadriven semantic coverage, targeted regression tests for tombstone truncation during compaction, delayed-flush path coverage for range deletions and range keys, concurrency stress under synthetic time, and benchmark signals for iterator performance over tombstone-heavy data.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/range_del_test.go -->
