# Research: subset-b-008553

Grouped research for `subset-b-008553`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/sstable.go -->
# Research: sources/storage-engines/pebble/tool/sstable.go

## Purpose
`tool/sstable.go` implements the Pebble CLI's `sstable` command family. It provides read-only introspection for table files: checksum verification, block/record layout, properties, record scans, and disk-usage estimates over key ranges.

## Important APIs, Types, And Functions
The central type is `sstableT`, which owns Cobra commands plus shared flags and state: Pebble options, registered comparers and mergers, key/value formatters, scan bounds, prefix filter, row count, verbosity, and optional blob-loading directory. `newSSTable` wires the subcommands `check`, `layout`, `properties`, `scan`, and `space` and registers shared flags.

`newReader` converts a `vfs.File` into an `objstorage.Readable`, applies Pebble reader options, installs comparer/merger registries, and configures cache options with the parsed file number when available. `foreachSstable` walks file or directory arguments and uses `processFiles` to open `.sst` and `.ldb` files.

`runCheck` validates block checksums, checks sorted internal-key order, and tests prefix iteration via `SeekPrefixGE`. `runLayout` prints the table layout, optionally formatting records. `runProperties` emits either raw `sstable.Properties.String()` output or a tabular summary. `runScan` scans point records, raw range deletions, and raw range keys. `runSpace` calls `EstimateDiskUsage`.

## Control Flow
All commands route through `foreachSstable`, so directory traversal, reader creation, property loading, reader closing, and extension filtering are shared. `runScan` has the richest flow: it may first load blob mappings from a manifest directory, creates an iterator with an optional end bound and blob context, seeks to the start key, materializes raw range tombstones into sorted spans, and then merges point records and tombstones into output order. After point/tombstone output, it separately scans raw range keys.

## State And Persistence
The file is read-only with respect to database data. Persistent state is opened through `vfs.FS` and `objstorage`; transient state includes iterator handles, cache handles, loaded blob mappings, copied last-key buffers, and in-memory tombstone spans. When blob loading is requested, external blob files are opened through `blobFileMappings` and closed after the scan.

## Dependencies And Integration Points
This code integrates CLI flag parsing (`spf13/cobra`), Pebble reader configuration, sstable internals, range deletion/keyspan helpers, blob-loading debug context, object storage, cache handles, and `vfs` traversal. It relies on comparer-specific formatters and prefix split functions for correctness of pretty output and prefix-iteration validation.

## Risks And Edge Cases
Prefix filtering uses `bytes.HasPrefix` plus comparer comparisons, and a comment notes this is only known to be kosher for common comparers. Range tombstone filtering has subtle overlap logic around inclusive/exclusive scan bounds. `runScan` uses `os.Exit(1)` in some range-span error paths, which is abrupt for embedded uses. Missing file numbers disable blob loading for non-numeric paths. Iterator close errors are printed rather than returned.

## Test Signals
Coverage comes indirectly through `TestSSTable` datadriven tests and fixture databases. Important signals include checksum failure text, out-of-order key warnings, prefix iteration failures, layout formatting, non-verbose properties summaries, range deletion/range key scan output, count limiting, key/value formatter behavior, and blob handle loading from manifest/blob directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/sstable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/sstable_test.go -->
# Research: sources/storage-engines/pebble/tool/sstable_test.go

## Purpose
`tool/sstable_test.go` is the entry point for datadriven tests covering the `sstable` CLI commands. It keeps test logic centralized in shared harness code and selects only fixtures whose names match `testdata/sstable_*`.

## Important APIs, Types, And Functions
The file defines `TestSSTable(t *testing.T)`, which delegates to `runTests(t, "testdata/sstable_*")`. There are no local helper types or assertions; the behavior depends on the broader `tool` package datadriven test harness.

## Control Flow
The Go test runner invokes `TestSSTable`; `runTests` discovers matching testdata files, executes the configured command sequences, and compares command output to expected datadriven output. This file is intentionally thin so all CLI tools share one execution and golden-output path.

## State And Persistence
No persistent state is mutated directly here. The datadriven harness may open fixture SSTables and databases under `tool/testdata`, but this file only declares the suite boundary.

## Dependencies And Integration Points
It depends on the package-local `runTests` helper and the `testing` package. Its integration point is the naming convention for datadriven fixture files, so adding a new `testdata/sstable_*` file automatically expands this suite.

## Risks And Edge Cases
Because this file delegates all work, failures may be difficult to localize from this file alone. The suite's completeness depends entirely on fixture coverage and on `runTests` setting up commands with the same flags and registered comparers used by production tooling.

## Test Signals
The signal is broad CLI regression coverage: command parsing, stdout/stderr rendering, fixture compatibility, formatter output, and golden diffs. A missing or incorrectly named fixture would silently fall outside this test.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/sstable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/testdata/make-fixtures.go -->
# Research: sources/storage-engines/pebble/tool/testdata/make-fixtures.go

## Purpose
`tool/testdata/make-fixtures.go` is a fixture generator for Pebble tool tests. It builds specialized databases used to exercise CLI behavior around external files, remote object storage metadata, synthetic prefix/suffix formats, and CockroachDB key schema formatting.

## Important APIs, Types, And Functions
`makeBrokenExternalDB` creates a database named `broken-external-db` using `FormatSyntheticPrefixSuffix`, disabled automatic compactions, and an in-memory remote storage factory. It writes a remote `foo.sst`, creates local compacted ranges, and ingests the external file with intentionally suspicious metadata such as a declared size of `123` and a broad `[a25,c19]` key range.

`makeCRSchemaDB` creates `cr-schema-db` with the CockroachDB comparer and key schema, generates deterministic random Cockroach KVs using `rand.NewPCG(1,1)`, flushes, and compacts the resulting table.

`main` runs both fixture builders.

## Control Flow
Each builder constructs Pebble options, opens an absolute-path database, writes deterministic contents, flushes and compacts to produce stable LSM structure, prints `db.DebugString`, and closes the DB. The external DB path creates a remote SST first, then introduces local data on either side of the external span before ingesting it.

## State And Persistence
The program creates or overwrites fixture DB directories relative to its working directory. It persists Pebble manifests, SSTables, local metadata, and remote in-memory object contents during execution; only the generated DB directories survive the process. `ErrorIfExists` prevents accidental overwrite of existing fixture directories.

## Dependencies And Integration Points
It depends on Pebble DB APIs, `sstable.NewWriter`, `objstorageprovider.NewRemoteWritable`, remote storage locators, and CockroachDB key-generation utilities. The generated fixtures feed `tool` datadriven tests for DB, LSM, manifest, sstable, and remote/external introspection.

## Risks And Edge Cases
Fixture determinism depends on format versions, compaction behavior, random generator stability, and key schema semantics. The external file fixture deliberately creates an unusual ingest state; if Pebble starts rejecting it or changes DebugString output, golden tests must be regenerated carefully. Because paths are absolute after `filepath.Abs`, running from the wrong directory can create fixtures in the wrong tree.

## Test Signals
Useful signals include stable `DebugString` output, expected remote object references, external file metadata visibility, and Cockroach key-schema pretty formatting. The generated data also checks that tools can inspect DBs using newer format gates and custom comparers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/testdata/make-fixtures.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/testdata/mixed/main.go -->
# Research: sources/storage-engines/pebble/tool/testdata/mixed/main.go

## Purpose
`tool/testdata/mixed/main.go` generates a fixture database containing both point keys and range keys, with one flushed SSTable and one unflushed memtable represented in the WAL. The fixture is designed for CLI tests that inspect mixed point/range-key content across SSTables and WALs.

## Important APIs, Types, And Functions
`main` removes prior generated files under `./tool/testdata/mixed` while preserving `main.go`, opens Pebble with `testkeys.Comparer`, `FormatNewest`, logging event listener, and disabled automatic compactions, then writes two batches. Local closures wrap `Batch.Set`, `RangeKeySet`, `RangeKeyUnset`, and `RangeKeyDelete`.

## Control Flow
The first batch writes 26 alpha point keys at sequence-style suffix `@1`, a range key set over `[a,z)`, a range key unset over `[a,z)`, and a range key delete over `[a,b)`. It commits and flushes, producing an SSTable. The second batch writes a later point key and additional range key operations but does not flush, leaving data in the memtable/WAL when the process exits.

## State And Persistence
The generator mutates the fixture directory by deleting old generated files and writing a Pebble DB. Persistent artifacts include the table file, WAL, manifest marker, lock/options files, and related metadata. It intentionally leaves unflushed state so WAL introspection has content.

## Dependencies And Integration Points
It integrates Pebble batch APIs, range-key APIs, `internal/testkeys` deterministic key formatting, and `vfs.Default`. The output is consumed by `tool` datadriven tests that need predictable range key and point key layout.

## Risks And Edge Cases
The cleanup walk removes any file except `main.go` and directories under `outDir`, so the path must be correct. Not closing the DB explicitly means process exit handles cleanup; if future Pebble behavior requires close for durability of some artifacts, the fixture contract may need adjustment. Range bounds use `[a,z)`, so the last generated alpha key and range end semantics are intentionally exclusive.

## Test Signals
Signals include one SSTable with flushed point and range keys, one WAL with unflushed point and range-key mutations, testkey formatting stability, and command output for range key set/unset/delete records.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/testdata/mixed/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/tool.go -->
# Research: sources/storage-engines/pebble/tool/tool.go

## Purpose
`tool/tool.go` defines the public container for Pebble introspection commands and the options used to customize those commands. It is the package's assembly point for DB, find, LSM, manifest, remote catalog, SSTable, WAL, and blob tooling.

## Important APIs, Types, And Functions
`T` holds the root command list, subtool structs, mutable `pebble.Options`, comparer and merger registries, default comparer name, open-error enhancer, open options, DB excise span provider, and remote storage resolver.

Public configuration functions include `Comparers`, `DefaultComparer`, `Mergers`, `FilterDecoders`, `KeySchema`, `KeySchemas`, `OpenOptions`, `FS`, `OpenErrEnhancer`, `WithDBExciseSpanFn`, and `WithDBRemoteStorageFn`. `New` applies defaults and user options, constructs each subtool, and exposes their root commands through `T.Commands`. `ConfigureSharedStorage` mutates remote storage settings after construction.

The file also defines `Comparer` and `Merger` aliases and `debugReaderProvider`, which implements `blob.ReaderProvider` for cache-less debug reads of blob files.

## Control Flow
`New` starts from read-only Pebble options using `vfs.Default`, registers the default comparer, default table filter decoders, and default merger, then applies caller options. It creates all subtools with shared option and registry pointers, so later commands see consistent comparer, merger, filesystem, open options, and remote storage behavior.

## State And Persistence
The code itself does not persist data, but it configures how tools open databases and object storage. `debugReaderProvider.GetValueReader` opens a blob object through `objstorage.Provider`, constructs a `blob.FileReader`, and returns a close hook that closes the reader.

## Dependencies And Integration Points
This is the integration surface for embedding Pebble tooling in higher-level binaries. It couples Cobra command construction, Pebble options, table filter decoders, key schemas, object storage, remote storage, blob reading, and command-specific option injection.

## Risks And Edge Cases
Because most subtools receive pointers to `t.opts`, post-construction mutation can affect command behavior, which is useful but requires care. Custom comparers must be registered before commands attempt pretty formatting or reading custom-comparer tables. `debugReaderProvider.GetValueReader` returns no cleanup for failed `blob.NewFileReader` besides the readable's own lifecycle, so callers rely on underlying constructors to close on error.

## Test Signals
Expected signals are command availability, default read-only behavior, custom comparer/merger registration, Cockroach key schema support, filter decoder registration, remote storage resolution, and blob value debug reads through the provider hook.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/tool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/util.go -->
# Research: sources/storage-engines/pebble/tool/util.go

## Purpose
`tool/util.go` contains shared parsing, formatting, traversal, and file-processing helpers for Pebble CLI tools. It normalizes user-provided key syntax and output formatting across SSTable, WAL, DB, and related commands.

## Important APIs, Types, And Functions
`key` implements Cobra flag parsing for raw strings, `hex:` bytes, `raw:` bytes, and `crdb:` formatted Cockroach keys. `keyFormatter` and `valueFormatter` implement formatter flags with built-ins `null`, `quoted`, `pretty`, `size`, `pretty:<comparer>`, and one-percent `fmt` patterns. Comparer-aware `setForComparer` methods install `FormatKey` and `FormatValue` hooks when available.

Formatting helpers include `formatKey`, `formatSeqNumRange`, `formatKeyRange`, `formatKeyValue`, and `formatSpan`. `walk` recursively traverses an FS in sorted order. `processFiles` walks CLI arguments, filters extensions, opens files, creates a 128 MiB cache and handle, constructs readers, invokes a callback, and closes resources.

## Control Flow
Formatter `Set` methods parse the user spec and set a formatter function. Value formatting wraps the selected formatter to render values prefixed with `blob-value:` in a special debug-friendly form. `processFiles` routes each candidate file through open, cache creation, reader construction, processing, and deferred cleanup. Directory traversal is depth-first and deterministic because entries are sorted.

## State And Persistence
The helpers do not write persistent state. Transient state includes formatter selection, optional comparer override names, buffers used by callers, cache handles, opened files, and constructed readers. `timeNow` is a package variable for test substitution.

## Dependencies And Integration Points
The file integrates Cobra flag interfaces, Cockroach key parsing, Pebble cache management, internal key formatting, keyspan formatting, sstable comparer registries, and `vfs.FS`. Most tool subcommands depend on these helpers for consistent output.

## Risks And Edge Cases
Formatter validation only accepts specs with exactly one `%` for custom `fmt` output; invalid specs fail flag parsing. Pretty formatting mutates formatter functions depending on table comparer unless the user explicitly chose a formatter. `processFiles` creates a new cache per file, which is simple but can be heavy over many files. Recursive traversal reports errors to stderr and keeps going, so partial failures are possible.

## Test Signals
Signals include parsing of `hex:`, `raw:`, and `crdb:` keys; formatter selection and comparer overrides; suppression via `null`; size output; blob-value display; sorted recursive traversal; extension filtering; reader close behavior; and stable key/value formatting in golden CLI tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/wal.go -->
# Research: sources/storage-engines/pebble/tool/wal.go

## Purpose
`tool/wal.go` implements WAL introspection commands. It can dump individual WAL files or merge segmented WAL files into logical logs before decoding Pebble batch records.

## Important APIs, Types, And Functions
`walT` owns the Cobra root plus `dump` and `dump-merged` commands, shared Pebble options, key/value formatters, comparer registry, default comparer, and verbosity flag. `newWAL` initializes default quoted key formatting and size value formatting.

`runDump` reads physical WAL files with `record.NewReader`, parses batches with `pebble.Batch.SetRepr`, and calls `dumpBatch`. `runDumpMerged` accumulates segment files through `wal.FileAccumulator`, then calls `runDumpMergedOne` per logical log. `dumpBatch` decodes `batchrepr.Reader` entries and renders each supported internal key kind.

## Control Flow
For physical dumps, each argument's basename is parsed with `wal.ParseLogFilename` to recover the disk file number used by record checksums. The command loops record-by-record, copies record bytes into a buffer, handles EOF/zeroed/invalid chunks specially, decodes a batch, prints offset, sequence number, count, and length, then prints each batch operation. Merged dumps first group segments into logical logs and use logical offsets from the WAL package.

## State And Persistence
The commands are read-only. Transient state includes a reusable `pebble.Batch`, bytes buffer, accumulated error lists, opened WAL files, and logical log readers. No decoded state is persisted.

## Dependencies And Integration Points
The implementation depends on Pebble batch representation, internal key kinds, range-key decoding, record readers, WAL segment accumulation, Cobra, registered comparers, and shared tool formatters. It is an important debugging bridge between on-disk WAL bytes and human-readable Pebble operations.

## Risks And Edge Cases
Zeroed and invalid chunks are treated like EOF because preallocation and recycling commonly leave such bytes. Sync or corruption errors are printed and accumulated but the command keeps scanning other files. `dumpBatch` handles many key kinds including ingest-with-blobs and range keys; unknown kinds are reported as errors with sequence context. Blob ID varint parsing in ingest-with-blobs stops if malformed, so output may be partial.

## Test Signals
Datadriven `wal_*` tests should cover physical and merged dumps, recycled/preallocated EOF behavior, batch header validation, all major key kinds, range-key decode errors, delete-sized values, ingest SST and ingest-with-blobs formatting, and custom key/value formatters.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/wal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/wal_test.go -->
# Research: sources/storage-engines/pebble/tool/wal_test.go

## Purpose
`tool/wal_test.go` selects the datadriven test suite for WAL tooling. It verifies WAL command output through shared test infrastructure rather than local assertions.

## Important APIs, Types, And Functions
The sole test, `TestWAL`, calls `runTests(t, "testdata/wal_*")`. The pattern identifies all WAL-specific datadriven fixtures under `tool/testdata`.

## Control Flow
The Go test runner invokes `TestWAL`; `runTests` discovers matching fixture files, executes the specified CLI command sequences, captures stdout/stderr, and compares them to expected output.

## State And Persistence
The file itself has no persistent state. Fixture files may read generated WALs and databases, but this test entry point only provides the glob that scopes the suite.

## Dependencies And Integration Points
It depends on the package-local datadriven harness and on WAL fixture naming conventions. It integrates with `wal.go` by exercising command parsing and output without duplicating command setup.

## Risks And Edge Cases
The test can only catch behavior represented in `testdata/wal_*`. If new WAL record kinds or output modes are added without fixtures, this entry point still passes. Because all assertions are golden-output based, intentional output changes require careful fixture updates.

## Test Signals
Signals include golden output for dump and dump-merged commands, formatting stability, recycled WAL handling, and decoded batch operation rendering.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/wal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/treesteps_test.go -->
# Research: sources/storage-engines/pebble/treesteps_test.go

## Purpose
`treesteps_test.go` is an invariants-build datadriven test that records iterator tree-step visualizations for Pebble iterator implementations. It verifies iterator behavior while also generating visualization URLs for debugging traversal decisions.

## Important APIs, Types, And Functions
`TestTreeSteps` walks `testdata/treesteps`, detects V1 versus V2 fixtures by filename suffix, and supports commands `define`, `level-iter`, `merging-iter`, `level-iter-v2`, `merging-iter-v2`, and `iterator`. `treeStepsStartRecording` configures optional max tree depth and normalizes recording names from datadriven positions.

## Control Flow
Each datadriven file defines a DB with `testkeys.Comparer`, in-memory FS, newest format, disabled automatic compactions, and either iterator stack V1 or V2. Individual commands then construct the requested internal iterator, start a treesteps recording, run iterator commands through `itertest` or user-iterator helpers, finish the recording, and append the visualization URL to textual output.

## State And Persistence
All DB state is in-memory and per test file. Iterator state is transient. The treesteps recording is emitted as a URL rather than persisted here. The build tag `invariants` gates the entire file, and the test skips if `treesteps.Enabled` is false.

## Dependencies And Integration Points
The test integrates DB definition helpers, `internal/treesteps`, V1 `levelIter`/`mergingIter`, V2 `iterv2` iterators, manifest level metadata, `itertest`, and public iterator commands. It is a cross-check between data structure topology and iterator-visible behavior.

## Risks And Edge Cases
Because it is build-tagged, normal test runs may not execute it. Visualization URLs can change if recording naming, tree depth, or iterator topology changes. The test must close DBs and iterators carefully to avoid leaked references. V1 and V2 command names must remain aligned with fixture suffixes.

## Test Signals
Signals include iterator outputs plus treesteps URLs for level iterators, merging iterators, and public iterators across both iterator stacks. It is especially useful for seek optimization, level layout, and merging decisions that are hard to understand from key output alone.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/treesteps_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/valsep/sst_blob_writer.go -->
# Research: sources/storage-engines/pebble/valsep/sst_blob_writer.go

## Purpose
`valsep/sst_blob_writer.go` provides `SSTBlobWriter`, a wrapper that writes an SSTable plus zero or more blob value files for later ingestion. It applies value-separation policy while exposing a writer interface close to `sstable.Writer`.

## Important APIs, Types, And Functions
`SSTBlobWriter` holds the public `SSTWriter`, chosen `ValueSeparation` strategy, accumulated error, blob file-number counter, close state, strict-obsolete flag, scratch KV, and metadata for blob files written. `SSTBlobWriterOptions` configures SST and blob writer options, whether blob files are disabled, minimum separation sizes, span policy, and `NewBlobFileFn`.

`NewSSTBlobWriter` builds the SST writer, applies fast-compression span policy, chooses `NeverSeparateValues` or `NewWriteNewBlobFiles`, and supplies a blob-object factory that assigns unique synthetic disk file numbers. `Set` adds an ordinary SET key with sequence zero. `BlobWriterMetas` returns blob stats after close. `Close` closes both SST and value-separation outputs. `HandleTestKVs` maps parsed datadriven KVs/spans into writer calls.

## Control Flow
Construction computes the active minimum separation size, honoring span-policy overrides and disable flags. `Set` first checks accumulated errors and strict-obsolete mode, prepares an internal SET KV, asks the raw SST writer whether the value is likely MVCC garbage, and delegates to the selected `ValueSeparation.Add`. `Close` closes the SST first, finishes value separation, collects new blob file stats, marks the writer closed, and returns combined errors.

## State And Persistence
The writer persists an SST object and any created blob objects through `objstorage.Writable`. It tracks blob metadata in memory until close. The `ValueSeparator` writes inline blob handles into the SST and writes separated values into blob files.

## Dependencies And Integration Points
It integrates `sstable.Writer`, `sstable.RawWriter`, `blob.FileWriter`, span policies, value-storage policy adjustments, short attributes, object storage, and ingest metadata. It is the external writer-side bridge between Pebble tables and blob value files.

## Risks And Edge Cases
`BlobWriterMetas` is invalid before close. Strict obsolete mode forbids `Set` and requires raw writer paths. A missing `NewBlobFileFn` would fail when the first value is separated. The synthetic file number starts at zero and is only used to produce reference indexes, so consumers must not treat it as final manifest identity without translation. Accumulated invalid-value callback errors are combined with writer errors.

## Test Signals
Datadriven tests exercise build options, span-policy overrides, disabled separation, MVCC garbage thresholds, output table size, blob file count, and blob stats. `HandleTestKVs` also verifies non-SET operations pass through to the underlying SST writer.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/valsep/sst_blob_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/valsep/sst_blob_writer_test.go -->
# Research: sources/storage-engines/pebble/valsep/sst_blob_writer_test.go

## Purpose
`valsep/sst_blob_writer_test.go` provides datadriven tests for `SSTBlobWriter`. It checks how external SST construction produces table metadata and blob file metadata under different value-separation options.

## Important APIs, Types, And Functions
`TestSSTBlobWriter` calls `runDataDriven` over `testdata/sst_blob_writer`. `parseSpanPolicy` parses a compact span-policy string into `base.SpanPolicy`, supporting `no-value-separation`, `value-separation-min-size`, and `disable-value-separation-by-suffix`. `parseBuildSSTBlobWriterOptions` extracts datadriven command args. `runDataDriven` implements the `build` command.

## Control Flow
For each `build` command, the test creates a logging in-memory FS, opens an object store, configures writer options with `testkeys.Comparer` and table format Pebble v7, supplies a blob-file factory that increments a counter, creates an SST object, parses input KVs/spans, feeds each to `HandleTestKVs`, closes the writer, reads table metadata and blob metadata, and prints a stable summary.

## State And Persistence
All files live in an in-memory VFS/object store. The test persists an SST object and any blob objects only for the duration of the datadriven command. Logging FS output is captured but not directly printed in the current returned output except through errors.

## Dependencies And Integration Points
The test integrates `datadriven`, `objstorageprovider`, `vfs.WithLogging`, `sstable.ParseTestKVsAndSpans`, `testkeys.Comparer`, and `require` assertions. It directly validates the external writer API rather than a DB compaction path.

## Risks And Edge Cases
The span-policy parser is intentionally narrow and fails on unknown options. It assumes one span policy for the whole SST. The test enforces `blobFileCount == len(blobMetas)`, so missing metadata collection after writing blobs is caught. Deferred close avoids leaks if a command exits early.

## Test Signals
Signals include table size changes, zero versus nonzero blob file creation, blob stats string formatting, option parsing failures, minimum-size overrides, suffix-based disablement, and correct handling of parsed point/range operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/valsep/sst_blob_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/valsep/value_separation.go -->
# Research: sources/storage-engines/pebble/valsep/value_separation.go

## Purpose
`valsep/value_separation.go` defines the core `ValueSeparation` interface and metadata structures used when compactions or external writers store some values in separate blob files instead of inline SSTable storage.

## Important APIs, Types, And Functions
`ValueSeparationOutputConfig` describes per-output policy: minimum value size, suffix-based separation disablement, and MVCC-garbage-specific minimum size. `ValueSeparation` defines lifecycle methods `SetNextOutputConfig`, `OutputConfig`, `EstimatedFileSize`, `EstimatedReferenceSize`, `Add`, and `FinishOutput`.

`NewBlobFileInfo` describes a newly created blob file, including writer stats, object metadata, and manifest physical metadata. `ValueSeparationMetadata` returns table blob references, reference size, reference depth, and new blob file info. `NeverSeparateValues` implements the interface by always writing values into the SSTable.

## Control Flow
The interface separates per-output configuration from per-KV addition and final metadata collection. `NeverSeparateValues.Add` resolves the KV value and calls `tw.Add`; `FinishOutput` returns empty metadata. This provides a no-op strategy for callers that want uniform plumbing without blob files.

## State And Persistence
`NeverSeparateValues` has no state. Other implementations use the metadata contracts here to persist blob references into table metadata and blob file metadata into manifests. `EstimatedFileSize` and `EstimatedReferenceSize` are transient planning estimates.

## Dependencies And Integration Points
The interface ties together internal keys, manifest blob references, object storage metadata, SSTable raw writers, and blob file stats. It is consumed by compaction output writing and by `SSTBlobWriter`.

## Risks And Edge Cases
Implementations must keep table inline handles, `BlobReferences`, reference depth, and new physical blob metadata consistent. `MinimumMVCCGarbageSize` uses zero to mean all likely garbage values are eligible, but `SetNextOutputConfig` in the stateful implementation also treats zero as "use global default", which callers must understand. `NeverSeparateValues.Add` still resolves lazy values, so value fetch errors propagate.

## Test Signals
Tests should validate no-op behavior, metadata shape, per-output config override semantics, estimated sizes, and correct pass-through of `forceObsolete` and `KVMeta` to raw SSTable writers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/valsep/value_separation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/valsep/value_separation_test.go -->
# Research: sources/storage-engines/pebble/valsep/value_separation_test.go

## Purpose
`valsep/value_separation_test.go` datadriven-tests value-separation policies independent of full DB compaction. It checks no-op storage, preservation of existing blob references, rewriting into new blob files, estimates, metadata, and invalid short-attribute handling.

## Important APIs, Types, And Functions
`TestValueSeparationPolicy` manages a `ValueSeparation`, raw SSTable writer, blob test values, in-memory object store, and logging buffer. Datadriven commands include `init`, `add`, `estimated-sizes`, and `close-output`. `errShortAttrExtractor` implements `base.ShortAttributeExtractor` and always returns an error for fallback testing.

## Control Flow
`init` selects `NeverSeparateValues`, `NewPreserveAllHotBlobReferences`, or `NewWriteNewBlobFiles`, parsing input physical blob metadata when preserving references. `add` lazily creates a raw writer and feeds parsed internal KVs, either in-place values or blob handles from `blobtest.Values`. `estimated-sizes` prints current file/reference estimates. `close-output` closes the raw writer, calls `FinishOutput`, and prints created blob metadata and blob reference entries.

## State And Persistence
The test uses an in-memory VFS/object store and increments file numbers for tables and blobs. It persists temporary table and blob objects only inside the test. The value-separation object carries pending reference state until `close-output`, then resets for later outputs.

## Dependencies And Integration Points
It integrates `datadriven`, manifest debug parsing, blob test value parsing, object storage, raw SST writers, logging raw writer wrappers, `testkeys.Comparer`, and short attribute extraction. It is the main policy-level validation surface for `ValueSeparator`.

## Risks And Edge Cases
Preserve mode requires input physical blob metadata for every referenced blob ID. Short-attribute extractor errors are intentionally non-fatal and should fall back to inline SSTable values. The test's output format must remain stable while still exposing enough metadata to catch reference-depth and size regressions.

## Test Signals
Signals include lazy blob file creation, blob reference ordering, preserved versus rewritten references, estimated size accounting, new blob physical metadata, MVCC garbage behavior through policy inputs, and invalid-value callback output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/valsep/value_separation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/valsep/value_separator.go -->
# Research: sources/storage-engines/pebble/valsep/value_separator.go

## Purpose
`valsep/value_separator.go` implements the stateful `ValueSeparator`, which either preserves existing hot blob references or rewrites eligible values into newly created blob files while writing an output SSTable.

## Important APIs, Types, And Functions
The internal mode enum distinguishes `preserveAllHotBlobReferences` from `rewriteAllHotBlobReferences`. `ValueSeparator` tracks input physical blob files, output reference depth, comparer, blob object factory, short attribute extractor, blob writer options, current/global output config, invalid-value callback, scratch buffer, pending references, and per-tier blob writer state.

Constructors are `NewPreserveAllHotBlobReferences` and `NewWriteNewBlobFiles`. Key methods are `SetNextOutputConfig`, `OutputConfig`, `EstimatedFileSize`, `EstimatedReferenceSize`, `Add`, `separateValue`, `preserveBlobReference`, `getWriter`, `closeWriters`, `maybeCheckInvariants`, and `FinishOutput`.

## Control Flow
`Add` preserves lazy blob handles only in preserve mode. Otherwise it resolves the value and either writes it inline or separates it if the key kind is SET/SETWITHDEL and the value meets size or likely-MVCC-garbage criteria. `separateValue` optionally extracts a short attribute, lazily opens a hot-tier blob writer, appends the value, maps the blob handle's file number to the output table's reference ID, and writes an inline blob handle to the SSTable. `FinishOutput` builds manifest blob references for preserved files, closes new blob writers, computes reference size and depth, resets state, and returns metadata.

## State And Persistence
Pending references determine the reference ID encoded into SSTable inline handles. New blob file writers persist separated values and produce physical blob metadata. Preserved references rely on `inputBlobPhysicalFiles` to populate manifest references. State resets after every output SSTable.

## Dependencies And Integration Points
The implementation integrates internal key/value representations, lazy blob fetchers, `manifest.CurrentBlobFileSet`-style metadata, `blob.FileWriter`, `sstable.RawWriter.AddWithBlobHandle`, object storage, storage tiers, invariants, and short attributes. It is used by compactions and external SST blob writing.

## Risks And Edge Cases
Reference ordering is correctness-critical: the inline `ReferenceID` must match the table's `BlobReferences` index. Missing input physical metadata in preserve mode is an assertion failure. `SetNextOutputConfig` treats zero values as "inherit global", so callers cannot override to zero except where semantics define zero globally. Short-attribute extraction errors intentionally fall back to inline values to avoid flush busy loops. Currently all blob references are hot-tier only.

## Test Signals
Policy tests should check preserve and rewrite modes, lazy writer creation, inline fallback for small or unsupported key kinds, MVCC garbage separation, short-attribute error fallback, estimated file/reference sizes, reference depth truncation, state reset after `FinishOutput`, and invariants around preserved value totals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/valsep/value_separator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/version_set.go -->
# Research: sources/storage-engines/pebble/version_set.go

## Purpose
`version_set.go` manages Pebble's sequence of immutable LSM versions and durable MANIFEST updates. It applies version edits, rotates manifests, tracks live/zombie/obsolete table and blob objects, maintains level metrics and compaction picker state, and locates the current manifest through an atomic marker.

## Important APIs, Types, And Functions
`versionSet` stores sequence-number atomics, object provider, DB mutex, options, filesystem, comparer, `manifest.VersionList`, latest-version mutable state, compaction picker, metrics, obsolete queues, zombie table/blob sets, WAL/manifest file numbers, manifest writer/file, rotation helper, and write serialization state.

`latestVersionState` tracks the L0 organizer, current blob file set, and latest virtual table backings. Initialization paths are `init`, `initNewDB`, and `initRecoveredDB`. Manifest write serialization uses `logLock`, `logUnlock`, and `logUnlockAndInvalidatePickedCompactionCache`. `UpdateVersionLocked` is the core apply path. Supporting functions include `getZombieTablesAndUpdateVirtualBackings`, `getZombieBlobFiles`, `createManifest`, `append`, `addLiveFileNums`, `addObsoleteLocked`, `setBasicLevelMetrics`, and `findCurrentManifest`.

## Control Flow
New DB initialization creates an empty version, compaction picker, initial MANIFEST snapshot, flushes and syncs it, syncs the directory, then moves the manifest marker. Recovered DB initialization installs recovered version state without rewriting the manifest.

`UpdateVersionLocked` serializes writers, calls a user update function, fills version-edit sequence and file-number fields, decides whether to rotate the manifest, updates virtual backings and blob file edit fields, drops `DB.mu` during manifest I/O, optionally creates a new manifest snapshot, encodes and syncs the edit, moves the marker after rotation, then reacquires `DB.mu` to update L0 metadata, zombies, obsolete queues, current version, manifest file number, metrics, and compaction picker.

## State And Persistence
Persistent state is the MANIFEST record stream plus `atomicfs` marker files pointing at the active manifest. Table/blob object liveness is represented in versions, blob file sets, virtual backings, zombie sets, and obsolete deletion queues. Sequence-number atomics govern WAL assignment and recovery. Directory sync before marker movement is part of the crash-safety contract.

## Dependencies And Integration Points
The file integrates manifest edit encoding/apply, record writers, object storage placement, delete pacing, virtual SSTables, blob rewrite heuristics, L0 organization, compaction picking, format-version gates, `vfs`, and `atomicfs.Marker`. It is on the critical path for flush, compaction, ingestion, recovery, and cleanup.

## Risks And Edge Cases
Manifest I/O errors after writing begins are fatal because partial durability is hard to reason about. `LastSeqNum` must remain at least every assigned sequence, including ingests. Manifest rotation must snapshot the pre-edit version and then append the edit. Virtual backing refcounts and `RemovedBackingTables` must stay consistent or table deletion can be unsafe. Marker movement relies on strict sync ordering. Metrics are recomputed in invariant builds to catch drift.

## Test Signals
Tests should exercise fresh and recovered initialization, manifest rotation, checkpoint reopen, sequence-number recovery, virtual backing create/delete/protect/unprotect, blob file deletion, zombie-to-obsolete transitions with live version refs, L0 organizer updates, metric recomputation, malformed marker names, and crash during large manifest writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/version_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/version_set_test.go -->
# Research: sources/storage-engines/pebble/version_set_test.go

## Purpose
`version_set_test.go` validates `versionSet` behavior through datadriven manifest edits, checkpoint/reopen scenarios, sequence-number accounting, large keys, and crash recovery during manifest writes.

## Important APIs, Types, And Functions
`writeAndIngest` builds a one-key external SSTable and ingests it. `TestVersionSet` drives `versionSet.UpdateVersionLocked` directly with parsed debug edits and commands for protecting backings, holding version refs, reopening, and printing metrics. `TestVersionSetCheckpoint` verifies manifest rotation preserves state. `TestVersionSetSeqNums` checks `LastSeqNum` in the active manifest. `TestLargeKeys` exercises DB operations and sstable layout/properties with huge shared-prefix keys. `TestCrashDuringManifestWrite_LargeKeys` simulates crashes during manifest writes with crashable memory FS clones.

## Control Flow
The main datadriven test initializes an in-memory version set with value separation enabled, parses each edit, normalizes/deduplicates table backings, creates physical files for non-virtual backings, resolves deleted table/blob metadata, applies the edit under the DB mutex, and prints current version, virtual backing state, zombie objects, and obsolete files. Reopen commands recover from the manifest and rebuild lookup maps.

## State And Persistence
Tests use in-memory or crashable VFS instances and object stores. They persist MANIFEST records, marker files, table objects, and ingested SSTables within test filesystems. Some tests intentionally hold version references to keep deleted objects zombie rather than obsolete.

## Dependencies And Integration Points
The file integrates manifest debug parsing, object storage provider, atomic manifest markers, record readers, errorfs injection, testkey comparers, external ingestion, DB open/close/recovery, and CLI-style helper commands for layout/properties.

## Risks And Edge Cases
The datadriven harness must manually keep metadata maps consistent with parsed edits. Randomized forced manifest rotation broadens coverage but requires deterministic output cleanup such as zeroing `NextFileNum`. Crash tests use randomness and can reveal multi-block record decoding problems. Large-key tests protect against separator-shortening assumptions in index and manifest logic.

## Test Signals
Signals include exact current-version debug strings, virtual backing state, zombie/obsolete object lists, metrics output, successful reopen after repeated rotations, manifest `LastSeqNum == logSeqNum-1`, stable large-key layout/properties output, and successful open after crash-cloned partial manifest writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/version_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/atomicfs/marker.go -->
# Research: sources/storage-engines/pebble/vfs/atomicfs/marker.go

## Purpose
`vfs/atomicfs/marker.go` implements an atomic, durable marker abstraction over a filesystem directory. Pebble uses it to point at the current MANIFEST without relying on in-place file overwrite.

## Important APIs, Types, And Functions
Public APIs are `ReadMarker`, `LocateMarker`, `LocateMarkerInListing`, `(*Marker).Move`, `NextIter`, `RemoveObsolete`, `SyncDir`, and `Close`. Marker files are named `marker.<name>.<iter>.<value>` by `markerFilename`, and parsed by `parseMarkerFilename`. `scanForMarker` selects the highest-iteration marker for a marker name and records older files as obsolete.

`Marker` holds the FS, directory, open directory file descriptor, marker name, current filename, current iteration, and obsolete file list.

## Control Flow
Locating lists or accepts a listing, scans marker filenames, opens the directory, and returns a handle plus current value. `Move` increments the iteration, creates a new marker file, syncs it, closes it, removes the old marker if present, and syncs the directory. `RemoveObsolete` deletes older marker files discovered during locate or failed old-file removal.

## State And Persistence
State is persisted entirely in marker filenames plus directory entries. Durability depends on syncing the new marker file before directory sync. A marker handle also keeps in-memory iteration and obsolete-file state. `SyncDir` exposes directory fsync for callers that need to make related files durable before marker movement.

## Dependencies And Integration Points
It depends on `vfs.FS`, `vfs.File`, Cockroach errors, and not-exist classification. `version_set.go` relies on this code for MANIFEST switching and uses `SyncDir` before `Move` to ensure the manifest exists durably before the marker points at it.

## Risks And Edge Cases
Marker names and values are encoded into filenames, so malformed `marker.` files cause scan errors. The abstraction is not safe for concurrent use across processes. If create returns an error after actually creating a file, a later locate treats it as obsolete. Directory sync errors panic because fsync errors are considered unrecoverable. Iteration can advance even when `filename` remains on the old value after a failed move.

## Test Signals
Tests should cover filename round trips, parse failures, selecting highest iteration, multiple marker names, empty markers, moves, obsolete cleanup, strict crashable-memory sync behavior, and injected filesystem errors with retry.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/atomicfs/marker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/atomicfs/marker_test.go -->
# Research: sources/storage-engines/pebble/vfs/atomicfs/marker_test.go

## Purpose
`vfs/atomicfs/marker_test.go` verifies marker filename parsing, marker movement, obsolete cleanup, crash durability, and fault tolerance under injected filesystem errors.

## Important APIs, Types, And Functions
`TestMarker_FilenameRoundtrip` checks formatting/parsing. `TestMarker_Parsefilename` validates accepted and rejected marker names. `TestMarker` is a datadriven suite with commands `list`, `locate`, `mkdir-all`, `move`, `next-iter`, `read`, `remove-obsolete`, and `touch`. `TestMarker_StrictSync` uses crashable memory FS to verify synced marker survival. `TestMarker_FaultTolerance` injects errors at successive operation counts and retries injected failures once.

## Control Flow
The datadriven test keeps a map of open markers per directory/name, closing prior handles on relocalization. Fault-tolerance testing runs a fixed sequence of locate/move/remove-obsolete operations repeatedly while shifting the injected-error point until no operation is hit; injected errors are retried exactly once.

## State And Persistence
Tests use `vfs.NewMem` and `vfs.NewCrashableMem`. Persistent test state is marker files in memory, open directory handles, and obsolete marker lists. Strict sync tests crash-clone with unsynced data dropped to confirm `Move` and directory syncs are sufficient.

## Dependencies And Integration Points
It integrates datadriven files, `crstrings` line parsing, `errorfs`, crashable VFS behavior, and `require` assertions. It validates the durability primitive used by Pebble MANIFEST markers.

## Risks And Edge Cases
The tests intentionally do not inject sync errors because production treats them as fatal panics. Because marker handles are not concurrent-safe, tests manage one active handle per marker path. Fault-tolerance relies on retrying operations after injected errors and checking the final visible value.

## Test Signals
Signals include correct handling of values containing dots, max uint64 iteration parsing, malformed marker rejection, highest-iteration selection, `NextIter`, obsolete file deletion, crash persistence of moved values, and robustness to create/remove/list/open failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/atomicfs/marker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/clone.go -->
# Research: sources/storage-engines/pebble/vfs/clone.go

## Purpose
`vfs/clone.go` implements recursive filesystem cloning between `vfs.FS` implementations. It supports optional skipping, syncing, and hardlink-or-copy optimization.

## Important APIs, Types, And Functions
`CloneOption` configures `cloneOpts`. Public options are `CloneSkip`, `CloneSync`, and `CloneTryLink`. `Clone(srcFS, dstFS, srcPath, dstPath, opts...)` returns `(true,nil)` on success, `(false,nil)` if the source does not exist, and `(false,err)` on real errors.

## Control Flow
`Clone` opens the source path and stats it. If it is a directory, it creates the destination directory, lists and sorts entries, recursively clones each non-skipped child, optionally syncs the destination directory, and returns. If it is a file and `CloneTryLink` is set with the same FS object, it tries `LinkOrCopy`. Otherwise it reads the full source file into memory, creates the destination file, writes all bytes, optionally syncs the file, closes it, and returns.

## State And Persistence
The function persists copied directory structure and file contents in the destination FS. `CloneSync` adds file and directory syncs for durability. It does not preserve metadata beyond directory/file existence and bytes.

## Dependencies And Integration Points
It depends on the `vfs.FS` and `vfs.File` interfaces, `io.ReadAll`, sorted directory listings, and `LinkOrCopy`. It is useful for checkpointing, test setup, and copying DB-like directory trees between VFS implementations.

## Risks And Edge Cases
Reading whole files into memory can be expensive for large files. If a source disappears during cloning, initial open returns `(false,nil)` for not-exist, while later recursive errors abort. `CloneTryLink` only attempts hardlinking when `srcFS == dstFS`; wrappers may prevent that identity check from matching. Syncing errors abort the clone.

## Test Signals
Tests should cover missing sources, nested directory copies, deterministic traversal, skip predicates, file contents, same-FS hardlink fallback, cross-FS copy fallback, file sync and directory sync paths, and mid-copy error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/clone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/default_linux.go -->
# Research: sources/storage-engines/pebble/vfs/default_linux.go

## Purpose
`vfs/default_linux.go` provides Linux-specific wrappers around `os.File` for Pebble's default VFS. It implements Linux prefetch, preallocation, fdatasync, partial sync hints, directory opening, and device ID extraction.

## Important APIs, Types, And Functions
`wrapOSFileImpl` returns a `linuxFile` and detects whether `sync_file_range` is supported for the file descriptor. `defaultFS.OpenDir` opens a directory with `O_CLOEXEC` and returns `linuxDir`. `linuxFile` implements `Prefetch` via `readahead`, `Preallocate` via `fallocate`, `SyncData` via `fdatasync`, and `SyncTo` via either `fdatasync` or `sync_file_range`. `isSyncRangeSupported` allowlists ext filesystems and calls `syncRangeSmokeTest`. `deviceIDFromFileInfo` extracts major/minor device numbers from `syscall.Stat_t`.

## Control Flow
On file wrap, the code records the fd and checks filesystem support. `SyncTo` falls back to full `fdatasync` when sync range is unsupported, otherwise issues asynchronous writeback for `[0, offset]` with wait-before semantics. Directory methods mostly delegate to `os.File` and make unsupported file operations no-ops.

## State And Persistence
The wrapper persists data through kernel sync syscalls. `useSyncRange` is per-file transient state based on filesystem type and syscall availability. Directory `SyncData` delegates to full sync.

## Dependencies And Integration Points
It depends on Linux build tags, `golang.org/x/sys/unix`, syscall constants, Pebble `File` interface expectations, and default FS wrapping in other VFS files. Pebble write paths use these methods for durability and writeback throttling.

## Risks And Edge Cases
`sync_file_range` does not provide persistence guarantees, so `SyncTo` reports `fullSync=false`. The allowlist avoids filesystems where it may be a noop, but only ext filesystems are enabled. WSL ENOSYS disables it. Offset/length conversion in readahead uses uintptr and assumes valid nonnegative inputs from callers.

## Test Signals
Tests should cover interface conformance, fdatasync fallback, sync range smoke-test behavior, filesystem allowlist decisions, directory open/sync behavior, and device ID extraction on Linux.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/default_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/default_unix.go -->
# Research: sources/storage-engines/pebble/vfs/default_unix.go

## Purpose
`vfs/default_unix.go` implements default VFS file wrappers for non-Linux Unix platforms: Darwin, DragonFly, FreeBSD, NetBSD, OpenBSD, and Solaris.

## Important APIs, Types, And Functions
`wrapOSFileImpl` returns a `unixFile` with the underlying `os.File` and fd. `defaultFS.OpenDir` opens a directory with `O_CLOEXEC`. `unixFile` implements `Stat`, no-op `Prefetch` and `Preallocate`, `SyncData` as full `Sync`, and `SyncTo` as full `Sync` returning `fullSync=true`. `deviceIDFromFileInfo` extracts major/minor device numbers through `unix.Major` and `unix.Minor`.

## Control Flow
All file operations mostly delegate to the embedded `os.File`. Since these platforms do not use Linux `sync_file_range` here, any `SyncTo` request becomes a full sync.

## State And Persistence
No extra persistent state is introduced. Durability relies on the platform's `fsync` behavior through `os.File.Sync`. Directory files are wrapped in the same `unixFile` type.

## Dependencies And Integration Points
It depends on build tags, `golang.org/x/sys/unix`, `syscall.Stat_t`, and the Pebble `vfs.File` interface. It provides the platform-specific layer below default FS consumers.

## Risks And Edge Cases
Prefetch and preallocation are silent no-ops, so performance and space-reservation behavior differs from Linux. `SyncTo` is conservative but potentially more expensive because it performs a full sync. `OpenDir` passes `O_CLOEXEC` with read mode zero; platform differences in opening directories matter.

## Test Signals
Useful signals include interface conformance, successful directory opening/syncing, device ID extraction, no-op prefetch/preallocate behavior, and full-sync behavior for `SyncData` and `SyncTo`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/default_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/default_windows.go -->
# Research: sources/storage-engines/pebble/vfs/default_windows.go

## Purpose
`vfs/default_windows.go` provides Windows-specific wrappers for Pebble's default VFS files and directories.

## Important APIs, Types, And Functions
`wrapOSFileImpl` returns `windowsFile`. `defaultFS.OpenDir` opens a path with `O_CLOEXEC` and returns `windowsDir`. `windowsDir` implements `Stat`, no-op prefetch/preallocate, no-op `Sync`, no-op `SyncData`, and no-op `SyncTo`. `windowsFile` implements no-op prefetch/preallocate, `Stat`, `SyncData` as `Sync`, and `SyncTo` as full `Sync`. `deviceIDFromFileInfo` returns an empty `DeviceID` because it is unsupported.

## Control Flow
File operations delegate to `os.File`, except unsupported advisory operations are no-ops. Directory syncs are intentionally ignored to match RocksDB Windows behavior. File `SyncTo` performs a full sync and reports `fullSync=true`.

## State And Persistence
The wrapper introduces no additional state. File durability depends on Windows file sync semantics. Directory durability is not explicitly enforced through `Sync`.

## Dependencies And Integration Points
It depends on Windows build tags, `os`, `syscall`, Cockroach errors, and the Pebble `vfs.File` interface. It provides compatibility for code paths that assume directory objects implement sync-related methods.

## Risks And Edge Cases
Ignoring directory sync means crash-safety semantics differ from Unix. `deviceIDFromFileInfo` cannot distinguish devices, so disk-health or placement logic depending on IDs must tolerate an empty ID. Prefetch and preallocation are not implemented.

## Test Signals
Signals include Windows interface conformance, file sync behavior through `SyncData`/`SyncTo`, directory sync no-op behavior, unsupported device ID handling, and no-op prefetch/preallocate calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/default_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_full.go -->
# Research: sources/storage-engines/pebble/vfs/disk_full.go

## Purpose
`vfs/disk_full.go` implements `OnDiskFull`, an FS wrapper that detects `ENOSPC`, invokes a callback once per write generation, blocks concurrent write operations while the callback runs, and retries eligible operations once.

## Important APIs, Types, And Functions
`OnDiskFull(fs, fn)` returns an `enospcFS`. `enospcFS` wraps write-oriented FS methods and file methods, tracks a generation counter, and uses a mutex/condition variable around callback execution. `waitUntilReady` waits if an ENOSPC callback is active. `handleENOSPC` elects the first failing operation in a generation to run the callback. `enospcFile` wraps `Write`, `WriteAt`, `Sync`, `SyncData`, and `SyncTo`. `isENOSPC` unwraps Cockroach errors to detect `syscall.ENOSPC`.

## Control Flow
Before a write-capable operation, the wrapper loads an even generation or waits for an odd generation to finish. If the operation returns ENOSPC, the first goroutine for that generation increments to odd, runs the callback outside the mutex, increments to the next even generation, and broadcasts. Other goroutines from the same generation wait only for that callback. Most operations retry once; sync operations trigger the callback but do not retry.

## State And Persistence
The wrapper does not persist its own state. It affects persistence by giving callers a chance to free disk space, for example by deleting a ballast file, before retrying writes. Underlying files and directories persist through the wrapped FS.

## Dependencies And Integration Points
It depends on the `vfs.FS` and `vfs.File` interfaces, Cockroach error unwrapping, syscall errno, and condition variables. Pebble can wrap its FS to coordinate disk-full remediation across WAL, manifest, flush, and compaction writes.

## Risks And Edge Cases
Retried writes use remaining bytes after partial writes, so underlying write semantics must be respected. Sync cannot safely be retried because a later successful fsync does not prove earlier writes survived. If the callback fails to free space, the retry returns ENOSPC and later generations may invoke callbacks again. Read-only operations are not blocked.

## Test Signals
Tests cover all wrapped FS write operations, file `Write` partial retry, non-retry `Sync`, one callback for concurrent same-generation ENOSPCs, error unwrapping, invocation counts, and benchmark overhead when no ENOSPC occurs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_full.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_full_test.go -->
# Research: sources/storage-engines/pebble/vfs/disk_full_test.go

## Purpose
`vfs/disk_full_test.go` validates the `OnDiskFull` wrapper's ENOSPC callback, retry, and concurrency semantics.

## Important APIs, Types, And Functions
`filesystemWriteOps` enumerates FS operations expected to handle ENOSPC: `Create`, `Lock`, `ReuseForWrite`, `Link`, `MkdirAll`, `Remove`, `RemoveAll`, and `Rename`. `TestOnDiskFull_FS` checks callback and retry per operation. `TestOnDiskFull_File` checks file `Write` and `Sync`. `TestOnDiskFull_Concurrent` checks one callback for a concurrent generation. `enospcMockFS` and `enospcMockFile` inject wrapped ENOSPC errors and count invocations. `BenchmarkOnDiskFull` measures no-error write overhead.

## Control Flow
Tests configure the mock FS to return ENOSPC a controlled number of times. FS method tests expect the wrapper to invoke the callback and retry successfully. File write tests simulate a partial write before ENOSPC and expect the retry to write the remainder. Sync tests expect the callback but a returned error. The concurrent test synchronizes failing goroutines so they all belong to one generation.

## State And Persistence
State is entirely in-memory: ENOSPC counters, invocation counters, callback counters, and condition-variable synchronization. No real filesystem data is required.

## Dependencies And Integration Points
The tests use `require`, Cockroach error wrapping, syscall ENOSPC, Go sync primitives, and the `vfs` interfaces. They directly exercise the wrapper contract that Pebble write paths rely on during full-disk events.

## Risks And Edge Cases
The mock must wrap `syscall.ENOSPC` to verify deep unwrapping. Concurrent test reliability depends on all goroutines consuming ENOSPC before retry proceeds. The suite does not test `SyncData`, `SyncTo`, `WriteAt`, or callback panics, so those remain residual risk.

## Test Signals
Signals include exactly one callback for one failing generation, exactly two underlying invocations for retried FS operations, correct partial-write byte accounting, no sync retry, and low wrapper overhead in the benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_full_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_health.go -->
# Research: sources/storage-engines/pebble/vfs/disk_health.go

## Purpose
`vfs/disk_health.go` implements disk write statistics and slow-disk detection for Pebble's VFS. It wraps files and write-oriented filesystem metadata operations, reports operations that exceed a threshold, and aggregates bytes written by disk write category.

## Important APIs, Types, And Functions
`OpType` enumerates monitored operations and has string/redaction formatting. `DiskWriteCategory`, `WriteCategoryUnspecified`, `DiskWriteStatsAggregate`, and `DiskWriteStatsCollector` provide write-byte aggregation. `diskHealthCheckingFile` wraps a `File`, tracks one in-flight file operation in a packed atomic, runs a ticker, times `Write`, `WriteAt`, `Preallocate`, `Sync`, `SyncData`, and `SyncTo`, and increments category bytes.

`DiskSlowInfo` formats slow-operation reports. `diskHealthCheckingFS` wraps an FS, tracks concurrent metadata operations in reusable slots, starts/stops a ticker goroutine, and wraps `Create`, `ReuseForWrite`, `OpenReadWrite`, and directories. `WithDiskHealthChecks` returns either the inner FS or a wrapper plus closer.

## Control Flow
For file operations, `timeDiskOp` packs start delta, write size, and op type into `lastWritePacked`, runs the operation, then clears it. A ticker periodically checks whether the current operation duration exceeds the threshold and calls `onSlowDisk`. For filesystem operations, `timeFilesystemOp` claims a slot, records name/op/start time, runs the operation, then clears the slot; a separate ticker scans all in-flight slots and reports slow metadata operations.

## State And Persistence
The wrapper's state is transient: ticker goroutines, stop channels, packed atomics, slot slices, create times, and byte counters. It does not persist data itself; it delegates to the underlying FS. `DiskWriteStatsCollector` accumulates in-memory per-category totals.

## Dependencies And Integration Points
It depends on `crtime` monotonic clocks, redact formatting, sync/atomic primitives, `vfs.FS` and `vfs.File`, and Pebble options that install disk-health checks. It integrates with event listeners through the `onSlowDisk` callback and with metrics through the stats collector.

## Risks And Edge Cases
`diskHealthCheckingFile` assumes no concurrent write-like operations on the same file handle and panics if detected. The packed timestamp supports about 34 years of uptime; larger deltas panic. Write sizes are rounded down to KiB and capped under about 1 GiB. `OpenReadWrite` wraps only stats collection with threshold zero, so slow detection is disabled there. Ticker close/reuse must avoid leaking goroutines.

## Test Signals
Tests cover byte aggregation, slow file writes and syncs, op-type packing limits, packing/unpacking edge cases, delta overflow panic, slow metadata operations, repeated close/reuse of FS wrapper, and `DiskSlowInfo` text containing full path, op, size, and duration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_health_test.go -->
# Research: sources/storage-engines/pebble/vfs/disk_health_test.go

## Purpose
`vfs/disk_health_test.go` validates disk-health checking, byte aggregation, operation packing, filesystem-operation stall detection, close/reuse behavior, and slow-operation formatting.

## Important APIs, Types, And Functions
`mockFile` sleeps during write/sync/preallocate operations. `mockFS` supplies configurable FS methods. Tests include `TestDiskHealthChecking_WriteStatsCollector`, `TestDiskHealthChecking_File`, `TestDiskHealthChecking_NotTooManyOps`, `TestDiskHealthChecking_File_PackingAndUnpacking`, `TestDiskHealthChecking_File_Underflow`, `TestDiskHealthChecking_Filesystem`, `TestDiskHealthChecking_Filesystem_Close`, and `TestDiskSlowInfo`.

## Control Flow
File slow-operation tests shrink `defaultTickInterval`, create wrapped files, perform blocking operations, and wait for `DiskSlowInfo` on a channel. Packing tests call `pack`/`unpack` directly with boundary inputs. Filesystem tests use a mock FS whose metadata operations block on a channel until the slow detector observes them, then unblock. Close/reuse tests repeatedly close the wrapper and verify later operations start a new ticker.

## State And Persistence
All state is in memory: sleep durations, channels, atomic counters, temporary wrappers, and mock file handles. There is no real disk persistence.

## Dependencies And Integration Points
The tests depend on runtime GOOS skips, `require`, `crtime`, mock VFS implementations, and the public `WithDiskHealthChecks` contract. They exercise both file-level and FS-level instrumentation paths.

## Risks And Edge Cases
Timing tests can be unreliable on Windows and are skipped there. Slow detection is ticker-based, so tests use timeouts and small intervals. The mock FS implements only required methods and panics for unexpected calls, which is useful for surfacing accidental behavior changes. The suite does not cover every op type at file level, but it covers packing capacity for the enum.

## Test Signals
Signals include sorted per-category stats, slow write/sync reports with expected op and size, no overflow of op bits, negative delta clamping, large size truncation, 35-year delta panic, metadata-operation stall reports, reusable closer behavior, and full-path formatting in `DiskSlowInfo`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_linux.go -->
# Research: sources/storage-engines/pebble/vfs/disk_usage_linux.go

## Purpose
`vfs/disk_usage_linux.go` implements Linux disk-usage reporting for `defaultFS.GetDiskUsage`.

## Important APIs, Types, And Functions
The file defines `func (defaultFS) GetDiskUsage(path string) (DiskUsage, error)`. It calls `unix.Statfs`, then computes `AvailBytes`, `TotalBytes`, and `UsedBytes`.

## Control Flow
The function creates a `unix.Statfs_t`, invokes `unix.Statfs(path, &stat)`, returns an error on failure, and otherwise calculates byte counts. It uses `stat.Frsize` rather than `stat.Bsize` because Linux `Bavail` and `Bfree` are in fragment-size units and this matches `df`/coreutils behavior.

## State And Persistence
The function is read-only and has no persistent state. It returns a snapshot of filesystem usage at the time of the syscall.

## Dependencies And Integration Points
It depends on the Linux build tag and `golang.org/x/sys/unix`. It implements the `vfs.FS` disk usage hook used by wrappers and callers that report or enforce disk-space budgets.

## Risks And Edge Cases
Integer multiplication assumes the stat fields fit in `uint64`. `UsedBytes` uses `TotalBytes - freeBytes`, not `TotalBytes - availBytes`, so it includes blocks reserved for privileged users as used from an ordinary availability perspective. The `Frsize` choice is Linux-specific and intentionally differs from some other Unix files.

## Test Signals
Tests should compare against expected `df`-style values on Linux, verify error propagation for missing paths, and check that wrappers delegate `GetDiskUsage` to the inner FS.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_netbsd.go -->
# Research: sources/storage-engines/pebble/vfs/disk_usage_netbsd.go

## Purpose
`vfs/disk_usage_netbsd.go` implements NetBSD disk-usage reporting for `defaultFS.GetDiskUsage`.

## Important APIs, Types, And Functions
The file defines NetBSD's `GetDiskUsage` method using `unix.Statvfs_t` and `unix.Statvfs`.

## Control Flow
The method calls `unix.Statvfs(path, &stat)`, returns an empty `DiskUsage` plus error on failure, and otherwise multiplies `Bsize` by `Bfree`, `Bavail`, and `Blocks` to compute free, available, and total bytes. Used bytes are total minus free.

## State And Persistence
The method is read-only and returns a point-in-time filesystem usage snapshot.

## Dependencies And Integration Points
It is selected by the `netbsd` build tag and depends on `golang.org/x/sys/unix`. It implements the platform-specific branch of the VFS disk usage API.

## Risks And Edge Cases
The code assumes NetBSD `Bsize` is the correct unit for all block counts returned by `Statvfs`. Reserved blocks are counted as used because `UsedBytes` subtracts `Bfree`, while `AvailBytes` reports `Bavail`.

## Test Signals
Signals include successful `Statvfs` conversion, missing-path error propagation, and consistency with platform tools for total, used, and available bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_openbsd.go -->
# Research: sources/storage-engines/pebble/vfs/disk_usage_openbsd.go

## Purpose
`vfs/disk_usage_openbsd.go` implements OpenBSD disk-usage reporting for the default VFS.

## Important APIs, Types, And Functions
The file defines `func (defaultFS) GetDiskUsage(path string) (DiskUsage, error)` using `unix.Statfs_t` and OpenBSD field names `F_bsize`, `F_bfree`, `F_bavail`, and `F_blocks`.

## Control Flow
The method calls `unix.Statfs`, returns any syscall error, then computes free, available, total, and used byte counts from block counts and block size. Used bytes are total minus free bytes.

## State And Persistence
The method has no persistent state and does not mutate the filesystem. It reports a snapshot of the filesystem containing `path`.

## Dependencies And Integration Points
It is selected by the `openbsd` build tag and depends on `golang.org/x/sys/unix`. It satisfies `vfs.FS.GetDiskUsage` for callers and wrappers.

## Risks And Edge Cases
Platform field names differ from other Unix implementations, making this file sensitive to `x/sys/unix` struct definitions. Like other implementations, available bytes and used bytes use different free concepts, so reserved blocks are reflected in the difference.

## Test Signals
Tests should verify syscall error propagation and compare reported byte counts with OpenBSD filesystem tools or controlled test mounts when available.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_unix.go -->
# Research: sources/storage-engines/pebble/vfs/disk_usage_unix.go

## Purpose
`vfs/disk_usage_unix.go` implements default VFS disk-usage reporting for Darwin, DragonFly, and FreeBSD.

## Important APIs, Types, And Functions
The file defines `GetDiskUsage` using `unix.Statfs_t`, `unix.Statfs`, and fields `Bsize`, `Bfree`, `Bavail`, and `Blocks`.

## Control Flow
The method performs `Statfs`, propagates errors, computes free bytes from all free blocks, available bytes from user-available blocks, total bytes from all blocks, and used bytes as total minus free.

## State And Persistence
The method is read-only. It captures filesystem usage at the moment of the stat call.

## Dependencies And Integration Points
It is selected by build tags for Darwin, DragonFly, and FreeBSD and depends on `golang.org/x/sys/unix`. It backs `vfs.FS.GetDiskUsage` for disk-space reporting and wrappers on those platforms.

## Risks And Edge Cases
The implementation assumes `Bsize` is the correct multiplier for block counts across these platforms. It does not account for path-level quotas or container limits beyond what `Statfs` exposes. Reserved space is not available but is not included in `UsedBytes` beyond the total-minus-free calculation.

## Test Signals
Signals include correct conversion on supported Unix platforms, error propagation for bad paths, and wrapper delegation through disk-health and disk-full FS layers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_windows.go -->
# Research: sources/storage-engines/pebble/vfs/disk_usage_windows.go

## Purpose
`vfs/disk_usage_windows.go` implements Windows disk-usage reporting for `defaultFS.GetDiskUsage`.

## Important APIs, Types, And Functions
The method converts the input path with `windows.UTF16PtrFromString`, calls `windows.GetDiskFreeSpaceEx`, fills `DiskUsage.AvailBytes` and `TotalBytes`, receives total free bytes separately, and computes `UsedBytes`.

## Control Flow
If UTF-16 path conversion fails, the method returns the conversion error. Otherwise it invokes the Windows API and computes `UsedBytes = TotalBytes - freeBytes` regardless of whether the syscall returned an error; callers should inspect the returned error.

## State And Persistence
The method is read-only and reports a point-in-time view of the volume containing `path`.

## Dependencies And Integration Points
It is selected by the `windows` build tag and depends on `golang.org/x/sys/windows`. It implements VFS disk-usage reporting for Windows callers and for higher-level wrappers that delegate to the default FS.

## Risks And Edge Cases
Path conversion can fail for invalid strings. `GetDiskFreeSpaceEx` distinguishes caller-available bytes from total free bytes, so `AvailBytes` may be lower than total free under quotas. Computing `UsedBytes` after an error may leave zero values; callers must respect the error.

## Test Signals
Tests should cover invalid path conversion, syscall error propagation, normal volume accounting, quota-sensitive available bytes when feasible, and wrapper delegation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/disk_usage_windows.go -->
