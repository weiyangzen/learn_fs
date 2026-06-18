# Research: subset-b-008552

Grouped research for Pebble tool sources. Each section preserves the source path in the title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/data_test.go -->
## sources/storage-engines/pebble/tool/data_test.go

Purpose: provides the shared datadriven harness for most `tool` package command tests. `runTests` expands a testdata glob, clones referenced on-disk fixtures into a memory filesystem, constructs a top-level Cobra command around `tool.New`, executes datadriven commands, and normalizes output. This file is the integration glue for `db_*`, `find`, `manifest_*`, and `remotecat` tests.

Important APIs and control flow: `runTests(t, path)` registers custom comparer, alternate comparer, merger, Cockroach key schema, custom corruption enhancer, and an in-memory FS. The special `create` datadriven command opens a Pebble DB with the test comparer/merger and `FormatVirtualSSTables`. Other commands are assembled from datadriven command names, args, and input fields, then path-like args are cloned once into memfs so later commands observe mutations. `timeNow` is replaced with a monotonic deterministic clock for scan summaries; `overrideRenderMetricsForDeterminism` swaps `renderMetrics` to `Metrics.StringForTests`.

State and persistence: test fixture state lives in a per-test memfs, but cloned fixture mappings are retained across commands within a test file to preserve DB/catalog/manifest mutations. Global state mutations (`timeNow`, `renderMetrics`) are deferred back to production values.

Dependencies and integration: depends on `datadriven`, `vfs.Clone`, `cobra`, test comparers, `cockroachkvs`, and `New` command construction. It exercises public command wiring rather than calling command handlers directly.

Risks: path cloning is heuristic and only clones args that resolve against the real FS. Global overrides must be restored or later tests become order-dependent. The harness hides stdout/stderr distinction by routing both into one buffer.

Test signals: all thin test files call this helper; output golden files detect command behavior, formatting, option loading, custom comparer/merger handling, corruption enhancer behavior, and deterministic metric rendering.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/data_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db.go -->
## sources/storage-engines/pebble/tool/db.go

Purpose: implements the `pebble tool db` command family for opening DBs, inspecting state, running consistency checks, mutating simple keys, estimating space, checkpointing, upgrading, excising ranges, printing metrics/properties, and delegating analyze/IO subcommands. `dbT` is both command registry and shared state holder.

Important APIs/types/functions: `dbT` owns Cobra commands, Pebble options, comparer/merger registries, formatting flags, remote/excise hooks, and analyze/benchmark flags. `newDB` constructs commands and flags. `initOptions` and `loadOptions` parse OPTIONS files, resolving custom comparer/merger/key schema hooks. `OpenOption` plus `nonReadOnly` alter options before `pebble.Open`. Command handlers include `runCheck`, `runUpgrade`, `runCheckpoint`, `runGet`, `runLSM`, `runScan`, `runSpace`, `runExcise`, `runProperties`, `runSet`, `inspectManifest`, and `readCurrentVersion`. `props`, `propArgs`, `addProps`, and `makePlural` support property aggregation.

Control flow: most commands initialize options, open the DB read-only by default, perform one operation, print errors to Cobra stderr, and close through `closeDB`. Mutating commands pass `nonReadOnly` and may require `promptForConfirmation`. `runExcise` builds a temporary SST with point and range-key excise tombstones inside the DB directory, ingests it through `IngestAndExcise`, and removes the temp file. `runProperties` avoids opening the DB; it peeks the manifest, replays the current version, opens table backings through an object provider, and aggregates property blocks per level plus total.

State and persistence: OPTIONS parsing mutates `d.opts` comparer, merger, key schema, and schema map. `openDBInternal` clones options, nulls explicit cache in favor of `CacheSize`, and clears unregistered key schema names. Mutating commands persist DB changes, format upgrades, checkpoints, or excise tombstones. `readCurrentVersion` replays MANIFEST into a `manifest.Version` and updates key/value formatters when the manifest declares a comparer.

Dependencies and integration: integrates Pebble DB APIs, `manifest`, `record`, `sstable`, `objstorageprovider`, `logs.NewCmd`, and analyze/benchmark implementations in sibling files. It is the main command tree consumed by `tool.New` and datadriven tests.

Risks: shared flag fields on `dbT` are command-global, so repeated command execution in one process relies on Cobra parsing order and test isolation. `runExcise` disables background behaviors on a local `dbOpts` pointer but opens through `d.openDB`, so future option plumbing changes could undermine assumptions. Virtual SSTs are skipped in `runProperties`. `runGet` prints Pebble errors such as not found on stderr rather than a structured status.

Test signals: `TestDB` datadriven suites cover command output. `data_test.go` stabilizes time and metrics. Analyze and LSM tests cover handlers implemented in sibling files.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_data.go -->
## sources/storage-engines/pebble/tool/db_analyze_data.go

Purpose: implements `db analyze-data`, a sampling tool that reads SSTables and feeds them into `compressionanalyzer.FileAnalyzer` to estimate compression behavior and write progressive CSV output.

Important APIs/types/functions: `runAnalyzeData` drives listing, sampling, progress reporting, throttling, and CSV persistence. `analyzeSSTable` opens a selected object and analyzes it. `analyzeSaveCSVFile` writes analyzer buckets. `dbStorage` abstracts local VFS and remote storage. `vfsStorage` lists local files, filters files modified in the last 15 seconds, and opens object-storage readables. `remoteStorage` lists and opens cloud objects while faking size as 1 MiB. `fileSet`, `fileInSet`, `makeFileSet`, `Refresh`, `Sample`, `Remaining`, and `samplingKey` implement weighted sampling without replacement using the Efraimidis-Spirakis algorithm. `isTTY` and `clearScreen` control interactive progress.

Control flow: the command detects remote paths by `://` and requires `DBRemoteStorageFn`; otherwise it wraps `d.opts.FS`. It builds a random `fileSet`, optionally creates a token-bucket read limiter, and loops until sample percent, timeout, or exhausted files. Every ten seconds, or on stop, it prints bucket summaries, writes CSV, and refreshes the local file list. Sampling ignores deleted or transiently unreadable files and continues after reporting non-not-exist errors.

State and persistence: persistent output is the CSV file required by the command flag. In-memory state tracks sampled files and bytes; local file sets preserve already-sampled entries across refreshes. No DB is opened, which allows analysis against directories or remote object stores.

Dependencies and integration: uses Pebble filename parsing, VFS, remote storage, object-storage readables, `compressionanalyzer`, `tokenbucket`, configured comparers/mergers/key schemas, and the `dbT.analyzeData` flags installed in `db.go`.

Risks: remote object sizes are synthetic, so sampling percentages are file-count based and bytes printed are less meaningful. Very large local SSTables over 512 MiB are skipped to reduce memory pressure. `Refresh` contains a dead `if err != nil` check after `Size`, relying on size zero for errors. The command tolerates live-directory churn but may underreport if files are young or repeatedly removed.

Test signals: `TestFileSetSampling` statistically verifies size-weighted first-sample behavior and uses a wrapper to make memfs files old enough to pass the 15-second filter.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_data.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_data_test.go -->
## sources/storage-engines/pebble/tool/db_analyze_data_test.go

Purpose: provides a focused smoke test for `fileSet` weighted sampling used by `db analyze-data`.

Important APIs/types/functions: `TestFileSetSampling` creates one large `.sst` and ten tiny `.sst` files in a memfs, repeatedly builds a `fileSet`, samples the first file, and asserts the small-file selection rate is less than ten times the theoretical probability. `fsWrapper.Stat` and `fileInfoWrapper.ModTime` make memfs files appear one hour old so `vfsStorage.Size` does not reject them as still-being-written.

Control flow: each iteration constructs `newVFSStorage(fsWrapper{memFS}, "")`, calls `makeFileSet`, samples once, and counts whether the chosen filename differs from the large file. The assertion uses the expected size-weighted probability and a generous bound explained by the Chernoff comment.

State and persistence: all files are in-memory and rebuilt once before the loop. Randomness uses `math/rand/v2` PCG seeded with random seeds, so the test is probabilistic but has an extremely low false-failure bound under the stated distribution.

Dependencies and integration: depends on `vfs.MemFS`, Pebble filename formatting via `base.DiskFileNum`, and `testify/require`. It directly exercises the storage abstraction and sampling logic, not the full Cobra command or compression analyzer.

Risks: because the test uses random seeds, it is not perfectly deterministic. It does not test refresh preservation, CSV writing, remote sampling, timeouts, read limiting, or analyzer errors. It assumes the first `Sample` is the behavior most relevant to weighted ordering.

Test signals: catches regressions that make sampling uniform or otherwise insensitive to file size. The ModTime wrapper also documents the production 15-second young-file guard.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_data_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_metadata.go -->
## sources/storage-engines/pebble/tool/db_analyze_metadata.go

Purpose: implements `db analyze-metadata`, a live SSTable metadata sampler that estimates per-level distributions for file size, blob-referenced size, KV counts, bytes per KV, key-prefix sharing, index/filter size, data blocks, two-level-index usage, and totals.

Important APIs/types/functions: `stat` combines `metricsutil.Welford` with a t-digest builder for mean/stddev and percentile estimates. `levelStats` groups per-level counters and `stat` values. `metadataStats` holds `manifest.NumLevels` entries. `runAnalyzeMetadata` replays the current version, builds level-separated physical SSTable lists, round-robin samples without replacement, and periodically prints. `processSSTableMetadata` opens each table through an object provider and records metadata. `printMetadataStats` renders an ASCII table with compact humanized values, standard-deviation percentages, p90/max lines, and per-level totals.

Control flow: the command uses `readCurrentVersion`, opens an object provider for the DB directory, skips virtual tables, and initializes total-file counts. The sampling loop checks timeout and sample-percent limits, reports every ten seconds or at stop, selects the next non-empty level round-robin, randomly removes one table from that level, processes it, and continues after per-file read errors.

State and persistence: no new files are written. All statistics are in-memory and progressively emitted to stdout. The DB is not opened as a `pebble.DB`; persistence is observed by manifest replay plus table object reads.

Dependencies and integration: integrates `db.go` manifest replay and options, `manifest.TableMetadata`, `objstorageprovider`, `sstable.Reader`, Cockroach `crbytes`/`crhumanize`, Pebble ASCII table rendering, t-digest, Welford statistics, and comparer split-prefix logic.

Risks: virtual tables are skipped, so virtualized workloads may be underrepresented. Per-file failures are logged but do not reduce `totalTables`, affecting sampled percentage. The loop reports only on timeout/sample/exhaustion or 10-second intervals, so very short non-TTY runs with no stopping condition rely on eventual exhaustion. Common-prefix calculation depends on the comparer split function.

Test signals: `db_analyze_metadata_test.go` constructs synthetic stats for empty, unsampled, small, large, zero-valued, and two-level-index cases and verifies formatted output through datadriven goldens.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_metadata_test.go -->
## sources/storage-engines/pebble/tool/db_analyze_metadata_test.go

Purpose: tests `printMetadataStats`, the final renderer for `db analyze-metadata`, with controlled synthetic distributions.

Important APIs/types/functions: `TestPrintMetadataStats` uses `datadriven.RunTest` over `testdata/analyze_metadata`. For the `print-metadata-stats` command, it manually populates a `metadataStats` value with representative per-level states, computes sampled and total file counts, calls `printMetadataStats`, and returns the table output for golden comparison.

Control flow: level fixtures cover L0 with partial sampling and two-level index files, L1 empty, L2 with files but no samples, L3 sampled files without two-level indexes, L4 very small files, L5 large files, and L6 sampled zero-valued data. Each level receives repeated `stat.Add` calls to exercise means, stddev percentages, p90/max percentiles, total extrapolation, and blank/zero branches.

State and persistence: no filesystem or DB state is used beyond the datadriven file. The test is deterministic because all values are synthetic.

Dependencies and integration: depends on `datadriven`, `manifest.NumLevels`, and the `stat`/`metadataStats` types from production code. It isolates formatting from table-reading behavior.

Risks: this test does not validate manifest replay, object provider opening, table property extraction, or sampling loop stop conditions. Because it tests exact rendered output, formatting changes require fixture updates even when semantics are unchanged.

Test signals: protects human-readable formatting, blank handling for empty/unsampled levels, zero mean rendering, percent sampled text, total extrapolations, and percentile rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_analyze_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_io_bench.go -->
## sources/storage-engines/pebble/tool/db_io_bench.go

Purpose: implements `db io-bench`, a random read benchmark over current SSTable backing objects, intended to measure IO-size-to-latency relationships, especially for object storage.

Important APIs/types/functions: `benchIO` records readable index, aligned offset, read size, and measured elapsed time. `runIOBench` parses sizes, opens the DB, opens benchmark tables, generates IOs, runs workers, and prints stats. `genBenchIOs` chooses random 1 MiB blocks across objects and creates one IO per requested size for each chosen block. `openBenchTables` collects unique backing SST numbers from L5/L6 by default or all levels with `--all-levels`, opens object readables, and keeps only objects at least 1 MiB. `parseIOSizes` parses comma-separated KiB sizes, requiring each to divide 1 MiB and be no larger than 1 MiB. `performIOs` uses per-readable `ReadHandle`s and a 1 MiB buffer. `getStats` calculates average, stddev, and p10/p50/p90/p95/p99.

Control flow: IOs for all sizes are shuffled together, then divided among `ioParallelism` goroutines by remaining-average partitioning. Each worker performs sequential reads over its slice and writes elapsed durations into the shared `ios` backing array. Results are regrouped by size after all workers finish.

State and persistence: opens the DB read-only and table objects for reading. It does not persist benchmark artifacts. Randomness is global `rand/v2`, so benchmark sequences are intentionally non-deterministic.

Dependencies and integration: uses `dbT.openDB`, Pebble `SSTables`, DB object provider, `objstorage.Readable`, and command flags installed by `db.go`.

Risks: no explicit validation prevents zero or negative `io-parallelism`; division by zero or panic is possible if misconfigured. `genBenchIOs` assumes at least one 1 MiB block and may panic if object totals are inconsistent, though `openBenchTables` filters too-small objects. Shared writes are safe by disjoint slices, but worker errors only print and do not fail the command. It benchmarks backing objects, so virtual SST sharing is deduplicated.

Test signals: no direct test in this subset; coverage is primarily through compilation and command registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_io_bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_test.go -->
## sources/storage-engines/pebble/tool/db_test.go

Purpose: thin test entry point for DB command datadriven fixtures.

Important APIs/types/functions: `TestDB(t *testing.T)` calls `runTests(t, "testdata/db_*")`, delegating all command construction, memfs fixture cloning, custom comparer/merger setup, deterministic time, and output normalization to `data_test.go`.

Control flow: Go’s test runner invokes `TestDB`, which expands every `testdata/db_*` datadriven file. Each datadriven command becomes a Cobra invocation against a newly built `tool.New` command set with the shared harness configuration.

State and persistence: persistence behavior is entirely fixture-driven. The shared harness clones referenced DB directories into a memory filesystem and keeps clone mappings across commands inside a datadriven file so mutating DB commands can be observed by later commands.

Dependencies and integration: depends directly only on `testing` and `runTests`, but indirectly exercises `db.go`, `db_io_bench.go`, `db_analyze_*`, and other registered tool commands when fixtures invoke them.

Risks: because this file has no assertions of its own, fixture naming is the test scope. New DB fixture files matching `db_*` are automatically included; missing fixtures or overly broad globs can change coverage.

Test signals: serves as the package-level signal that DB command output remains stable for checks, scans, get/set, properties, manifest inspection, checkpoints, upgrades, space estimates, and related fixture scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/find.go -->
## sources/storage-engines/pebble/tool/find.go

Purpose: implements `pebble tool find <dir> <key>`, which finds WAL and SSTable references to a user key and range tombstones covering that key, then annotates SSTable hits with provenance from MANIFEST version edits.

Important APIs/types/functions: `findRef` records internal key, value, file number, and filename. `findT` holds command configuration and discovered manifests, WALs, tables, version edits, table metadata, blob mappings, and decode errors. `newFind` wires flags including comparer, key/value formatters, verbose mode, and `--load-blobs`. `findFiles` walks the directory, accumulates WAL logical logs, and records manifests/tables. `readManifests` decodes version edits, tracks comparer name, edit references by disk file number, and table metadata. `searchLogs` decodes batch records and matches point/range-delete entries. `searchTables` opens SSTables, applies virtual transforms from metadata, scans point and raw range-deletion iterators, and optionally loads blob values. `tableProvenance` classifies matching tables as compacted, flushed, ingested, added, and moved.

Control flow: `run` parses the key, discovers files, reads manifests, initializes blob mappings, resolves comparer/formatters, searches logs and tables, stable-sorts refs by file number/name, groups output by file, prints metadata key ranges and provenance, formats refs, then appends deferred SSTable decode errors.

State and persistence: the tool is read-only. It reconstructs in-memory history from all manifests and reads archived/current WAL and table files. Blob catalog resources are closed at the end.

Dependencies and integration: integrates VFS walking, WAL file accumulation, `record.Reader`, `pebble.Batch`, range tombstone encoding/decoding, SSTable readers/iterators, blob file mappings from sibling code, object-storage readable wrappers, and comparer-specific formatters.

Risks: explicit TODO notes virtual SST support is incomplete; disk scanning will not include purely virtual table identity, though manifest metadata helps transforms for physical hits. Provenance is approximate across manifest rollover and mixed log/ingest ordering. Corrupt WAL/SST handling favors continued output but may hide incomplete scans. Blob loading depends on catalog mappings.

Test signals: `find_test.go` routes `testdata/find` through the datadriven harness. Fixture builders create WAL, flush, ingest, compaction, tombstone, and value-separation cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/find_test.go -->
## sources/storage-engines/pebble/tool/find_test.go

Purpose: thin test entry point for the `find` command’s datadriven fixture.

Important APIs/types/functions: `TestFind` calls `runTests(t, "testdata/find")`.

Control flow: the shared harness builds the full tool command tree, clones referenced fixture DBs into memfs, and executes datadriven commands from `testdata/find`. Those commands exercise `find.go` through Cobra rather than direct helper calls.

State and persistence: fixture DBs are copied into an in-memory filesystem. Since `find` is read-only, persistence mainly concerns preserving the fixture layout of WALs, archived logs, SSTables, manifests, blob files, and catalogs.

Dependencies and integration: indirectly depends on `make_test_find_db.go` and `make_test_find_db_val_sep.go` generated fixtures, custom comparers/mergers from `data_test.go`, and blob/value formatting paths.

Risks: this file itself does not define coverage; all assertions live in the datadriven file. If generated fixture DBs drift without fixture updates, output expectations may fail.

Test signals: validates user-facing grouped output, key/value formatting, provenance strings, range tombstone discovery, WAL/SSTable ordering, and optional value-separation behavior covered by the fixture.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/find_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/logs/compaction.go -->
## sources/storage-engines/pebble/tool/logs/compaction.go

Purpose: implements `logs compactions`, a Cockroach/Pebble log parser that extracts flush, compaction, ingest, blob rewrite, and read-amplification events and summarizes them in fixed time windows.

Important APIs/types/functions: regex globals parse log context, sentinel operation kind, compaction starts/ends, flushes, ingests, read amp lines, and blob rewrites. `compactionType` mirrors Pebble compaction kinds. `compactionStart`, `compactionEnd`, `event`, `compaction`, `ingest`, `readAmp`, and `logContext` model parsed data. `logEventCollector` stores current context, open jobs keyed by node/store/job, completed events, read amps, and parse errors. Parser functions include `parseLog`, `parseLogContext`, `parseCompaction`, `parseFlush`, `parseIngest`, `parseRemainingIngestLogLine`, `parseReadAmp`, `parseBlobRewrite`, `unHumanize`, and `sumInputBytes`. `aggregator.aggregate` groups events; `windowSummary.String` renders ASCII tables for flush/ingest, compaction types and bytes, read amp average, and long-running events.

Control flow: `parseLog` scans lines, saves context when present, uses the sentinel regex to dispatch compaction/flush/ingest parsing, otherwise tries blob rewrite then read amp. Starts are stored until matching end lines arrive; missing starts are reported to stderr. `runCompactionLogs` parses all files, reads `--window` and `--long-running-limit`, aggregates, prints summaries to stdout, then prints accumulated parse errors to stderr.

State and persistence: no persistent state is written. In-memory collector state depends on log order and current context; events without context inherit the last parsed context.

Dependencies and integration: uses Pebble `manifest.NumLevels`, ASCII table helpers, Cobra flags from `logs/tool.go`, and `pebble.AllCompactionKindStrings` in tests to stay synchronized with engine compaction kinds.

Risks: parser correctness depends on evolving log text and regexes. `windowSummary.String` computes read amp average without guarding empty `readAmps`, yielding NaN if no read-amp events are in a window. Long-running sort comment says descending but comparator sorts ascending. Missing start events are printed immediately to `os.Stderr` rather than accumulated. Multi-line or reformatted logs can silently stop matching.

Test signals: regex tests cover current and 23.1 formats, unknown node/store, multilevel compactions, flushable ingests, and byte parsing. Datadriven tests validate aggregation. Sync test fails when Pebble compaction kinds are added without parser support.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/logs/compaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/logs/compaction_test.go -->
## sources/storage-engines/pebble/tool/logs/compaction_test.go

Purpose: tests regex extraction, context parsing, aggregation output, byte parsing, and compaction-kind synchronization for `logs compactions`.

Important APIs/types/functions: constants define representative 23.1 and current log lines for compactions, multilevel compactions, flushes, read amp, unknown node/store, and flushable ingestion. `TestCompactionLogs_Regex` checks specific capture groups for sentinel, compaction, flush, read amp, and ingest regexes. `TestParseLogContext` verifies timestamp/node/store extraction including tenant prefixes and `?` IDs. `TestCompactionLogs` runs datadriven files under `logs/testdata`, writing `log` inputs to temp files, parsing into a collector, and summarizing with configurable window/long-running duration. `TestParseInputBytes` covers old and new humanized byte formats. `TestCompactionKindToolSupport` compares supported parser kinds against `pebble.AllCompactionKindStrings`.

Control flow: regex tests iterate table cases and assert matches are non-nil and exact. Datadriven tests maintain collector state until a `reset` command, allowing multi-file sequences. The sync test excludes flush-logged kinds and maps `blob-file-rewrite` to the parser’s `blob-rewrite` spelling.

State and persistence: temp log files are written for datadriven parsing only. Collector state is intentionally reusable within a datadriven test to simulate multi-log input.

Dependencies and integration: depends on `datadriven`, `pebble.AllCompactionKindStrings`, and parser internals from `compaction.go`. It directly guards compatibility with upstream log format and compaction kind additions.

Risks: tests assert selected regex groups but not every capture. Datadriven coverage is only as broad as files under `logs/testdata`. Sync test detects missing kind names but not semantic aggregation errors for a new kind.

Test signals: high-value drift detector for log format changes, old/new byte-unit formats, node/store context changes, flushable ingest parsing, and enum synchronization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/logs/compaction_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/logs/tool.go -->
## sources/storage-engines/pebble/tool/logs/tool.go

Purpose: exposes the `logs` Cobra command subtree used by `db.go` and top-level tool wiring.

Important APIs/types/functions: `NewCmd() *cobra.Command` creates the root `logs` command and a `compactions` subcommand. The subcommand runs `runCompactionLogs` and registers `--window` with a default of ten minutes and `--long-running-limit` with a default of zero, interpreted by `runCompactionLogs` as disabled.

Control flow: command construction is static: create root, create subcommand, attach duration flags, add subcommand, return root.

State and persistence: no persistent state. Cobra flag state is held in the returned command instance.

Dependencies and integration: depends on Cobra and `time`. `db.go` attaches `logs.NewCmd()` under the DB tool command tree, while parser behavior lives in `compaction.go`.

Risks: all log functionality currently hangs off one subcommand; additional log parsers must be registered here. Defaults affect aggregation output and may alter datadriven expectations if changed.

Test signals: indirectly exercised through `compaction_test.go` parser tests and any command-level fixtures invoking `logs compactions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/logs/tool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/lsm.go -->
## sources/storage-engines/pebble/tool/lsm.go

Purpose: implements `tool lsm <manifest>`, which converts MANIFEST version edits into a self-contained HTML/D3 visualization of LSM evolution.

Important APIs/types/functions: `lsmTableMetadata`, `lsmVersionEdit`, `lsmKey`, and `lsmState` are JSON payload structures consumed by `lsm_data.go` JavaScript. `lsmT` owns command flags, comparer, formatter, state, and key map. `newLSM` registers flags for embedding assets, pretty JSON, start/end edit, and edit count. `validateFlags` enforces compatible edit slicing. `runLSM` reads/coalesces/slices edits, builds keys and edits, then emits HTML with embedded or external CSS/JS. `readManifest` decodes `VersionEdit`s and resolves comparers. `buildKeys` deduplicates sorted boundary internal keys. `buildEdits` tracks current files by level, attaches virtual backings, records add/delete/sublevel deltas, and builds versions via `manifest.NewVersionWithFiles`. `coalesceEdits` folds edits before `start-edit` into synthetic starting state. `reason` classifies edits.

Control flow: after validation and manifest read, optional coalescing provides the starting LSM state for nonzero start edit. Edits are sliced by `end-edit`/`edit-count`, keys are assigned compact IDs, edit deltas are generated, and HTML is written to stdout.

State and persistence: no files are written by the command; output HTML contains serialized state. In-memory `currentFiles`, backing table map, and `state.Files` reconstruct visualization state without applying a full DB open.

Dependencies and integration: uses MANIFEST record decoding, `manifest.L0Organizer`, `NewVersionWithFiles`, comparers/formatters, and generated `lsmDataCSS`/`lsmDataJS`. The `go:generate` directive invokes `make_lsm_data.sh`.

Risks: slicing expression for `endEdit` depends on `startEdit` and can be subtle. `coalesceEdits` mutates the `startingEdit` pointer from the original slice. The visualization is approximate for reasons, relying on deleted tables, min-unflushed log, and sequence-number equality. `log.Fatal` in JSON formatting exits the process on marshal failure.

Test signals: `lsm_test.go` protects L0 sublevel construction when L0 files arrive out of sequence-number order.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/lsm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/lsm_data.go -->
## sources/storage-engines/pebble/tool/lsm_data.go

Purpose: generated asset container for the LSM HTML viewer. It embeds CSS and JavaScript strings used by `lsm.go` when `--embed` is enabled.

Important APIs/types/functions: `lsmDataCSS` defines layout, slider, labels, and SVG classes. `lsmDataJS` builds DOM elements with D3, defines level heights/offsets, humanized sizes, slider behavior, keyboard playback, and the central `version` object. The `version` object manages current level/sublevel file arrays, edit index, add/remove operations, L0 sublevel rebuilding, level info, rendering, mouse-over overlap highlighting, resizing, and slider/index input synchronization.

Control flow: on `window.onload`, JavaScript initializes sublevel counts from `data.Edits`, sets SVG sizing, and applies edit zero. `version.set` steps forward or backward by applying/unapplying add/delete deltas, rebuilds L0 sublevels from recent `Sublevels` maps, sorts L0 by sequence numbers and other levels by key range, updates labels, and renders. `updateSize` rebuilds slider ticks/drag handle and clip paths. Keyboard handlers support left/right stepping and spacebar playback.

State and persistence: browser-only state is held in JavaScript arrays and SVG DOM. No persistent storage is used. Input comes from the global `data` object emitted by `lsm.go`.

Dependencies and integration: depends on D3 v5, either loaded remotely when embedded or from `tool/data/d3.v5.min.js` when not embedded. Generated from `tool/data/lsm.css` and `tool/data/lsm.js` by `make_lsm_data.sh`.

Risks: generated file should not be manually edited. Embedded mode still references remote D3, so fully offline viewing requires `--embed=false` plus local assets. Rendering relies on numeric object keys from JSON and D3 v5 event globals. Some comments and misspellings indicate legacy frontend code; layout is fixed-height SVG oriented.

Test signals: no direct frontend test in this subset. `lsm.go` compilation and `lsm_test.go` indirectly validate that the generated strings exist and are consumed.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/lsm_data.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/lsm_test.go -->
## sources/storage-engines/pebble/tool/lsm_test.go

Purpose: regression test for `lsmT.buildEdits` when overlapping L0 files are added out of largest-sequence-number order.

Important APIs/types/functions: `TestBuildEditsL0OutOfSeqNumOrder` defines `newL0Table`, creating `manifest.TableMetadata` with overlapping user-key bounds, explicit sequence-number ranges, size, and physical backing. It then constructs two version edits adding high-seq and low-seq L0 tables and calls `l.buildEdits`.

Control flow: the test sets up a default comparer, creates two overlapping L0 tables where the first has larger sequence numbers, builds an `lsmT`, assigns its comparer, and asserts `buildEdits` does not panic and produces two state edits.

State and persistence: all objects are in-memory metadata. No MANIFEST or DB files are used.

Dependencies and integration: uses `manifest.TableMetadata`, `base.InternalKey`, `sstable.Comparers`, `pebble.Options`, and `testify/require`. It specifically verifies that production code uses `manifest.NewVersionWithFiles`, which orders L0 for `L0Organizer`, instead of a testing constructor preserving problematic slice order.

Risks: focused on one panic scenario; it does not validate full JSON output, HTML rendering, edit slicing, or virtual backing behavior.

Test signals: protects against regressions that would reintroduce L0 organizer precondition panics for real manifests where L0 additions are not already sorted by sequence number.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/lsm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_incorrect_manifests.go -->
## sources/storage-engines/pebble/tool/make_incorrect_manifests.go

Purpose: build-tagged fixture generator for an intentionally invalid MANIFEST used by manifest check tests.

Important APIs/types/functions: `writeVE` appends and encodes a `manifest.VersionEdit` to a `record.Writer`, fataling on errors. `makeManifest1` creates `tool/testdata/MANIFEST-invalid`, writes two version edits with the LevelDB comparer, min-unflushed log numbers, next file/last sequence metadata, and L6 tables with conflicting sequence ranges. `main` calls `makeManifest1`.

Control flow: guarded by `//go:build make_incorrect_manifests`; it runs only when explicitly invoked with the documented `go run -tags make_incorrect_manifests` command. It overwrites the fixture path using `vfs.Default`.

State and persistence: persists a MANIFEST fixture under `tool/testdata`. The generated edits are crafted to violate manifest/version invariants for negative testing.

Dependencies and integration: uses Pebble internal `manifest`, `record`, `base`, and `vfs`. The output is consumed by datadriven `manifest_check` fixtures through `manifest.go`.

Risks: running from the wrong working directory writes to an unexpected relative path. It uses `log.Fatal`, suitable for a generator but not a library. Any manifest encoding format change requires regenerating fixture expectations.

Test signals: supports tests that ensure `manifest check` reports invalid version application rather than silently accepting corrupt metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_incorrect_manifests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_lsm_data.sh -->
## sources/storage-engines/pebble/tool/make_lsm_data.sh

Purpose: generation script for `lsm_data.go`, embedding the LSM viewer CSS and JavaScript into Go raw string variables.

Important APIs/functions: shell variables `dest`, `do`, `not`, and `edit` build the generated header without spelling the generated-file sentinel directly in one token. The script writes Go package header, starts `lsmDataCSS`, appends `data/lsm.css`, starts `lsmDataJS`, appends `data/lsm.js`, and closes the raw string.

Control flow: sequential `cat >`, `cat >>`, and heredoc operations create the generated file in the current directory. It is referenced by `//go:generate ./make_lsm_data.sh` in `lsm.go`.

State and persistence: overwrites `lsm_data.go`. It reads from `tool/data/lsm.css` and `tool/data/lsm.js` relative to the current working directory expected by `go generate`.

Dependencies and integration: relies on POSIX shell, `cat`, and the asset files. `lsm.go` consumes the generated variables for embedded HTML output.

Risks: raw string embedding will break if CSS or JS contains a backtick. Running the script from the wrong directory will fail or create an incorrectly located file. It does not include D3 itself; the HTML still references D3 separately.

Test signals: no direct test. Compilation of `lsm.go` ensures `lsmDataCSS` and `lsmDataJS` exist after generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_lsm_data.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_find_db.go -->
## sources/storage-engines/pebble/tool/make_test_find_db.go

Purpose: build-tagged generator for the `find-db` fixture used by `find` tests.

Important APIs/types/functions: local `db` wraps `*pebble.DB`, comparer, and merger. `open` configures an alternate comparer, test merger, archive cleaner, logging event listener, VFS, and `FormatFlushableIngest`. Methods wrap Pebble operations: `set`, `merge`, `delete`, `singleDelete`, `deleteRange`, `ingest`, `flush`, `compact`, `snapshot`, and `close`. `ingest` writes a temporary SST using matching comparer/merger and ingests it.

Control flow: `main` removes `tool/testdata/find-db`, opens a new DB, writes point sets and merges, flushes and compacts, holds snapshots to pin data, ingests SSTs, compacts, writes deletes/single deletes/range deletes, flushes, and compacts again.

State and persistence: writes a complete Pebble DB fixture with current and archived WAL/SST/MANIFEST/OPTIONS files. Snapshots intentionally influence compaction output and retained history.

Dependencies and integration: uses Pebble DB APIs, SSTable writer, object-storage file writable, VFS, default comparer clone, and test merger. The generated fixture is consumed by `find.go` through datadriven tests.

Risks: fixture output depends on Pebble format/version behavior, compaction choices, event listener side effects, and relative working directory. The temp ingest file path is fixed and removed only by DB ingest/cleanup behavior.

Test signals: creates coverage for `find` over WAL records, flushed records, ingested tables, compaction provenance, archived files, point mutations, merges, single deletes, and range deletes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_find_db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_find_db_val_sep.go -->
## sources/storage-engines/pebble/tool/make_test_find_db_val_sep.go

Purpose: build-tagged generator for a value-separation DB fixture used by `find` tests, especially blob-reference handling.

Important APIs/types/functions: `minSizeForValSep` sets the value-separation minimum to three bytes. Local `db` wraps `*pebble.DB`; methods parse Cockroach-formatted keys with `cockroachkvs.ParseFormattedKey`, set values, flush, and close. `main` configures `KeySchema`, `KeySchemas`, `FormatValueSeparation`, small block sizes, and a `ValueSeparationPolicy`.

Control flow: the generator removes `tool/testdata/find-val-sep-db`, opens a DB with value separation enabled, writes several keys with values above and below the minimum, flushes, writes more keys and flushes, then writes thirty additional keys and flushes again.

State and persistence: writes a fixture DB containing SSTables, blob files, WALs, OPTIONS, and MANIFEST state under the testdata directory.

Dependencies and integration: uses Cockroach key schema/comparer support, `blobtest` import presence, Pebble value separation, and VFS. The fixture supports `find --load-blobs` and key-schema-aware formatting.

Risks: relative path and Pebble format behavior determine output. The `blobtest.Values` field is unused. If value-separation thresholds or file layout change, fixtures and expected datadriven output must be regenerated.

Test signals: ensures `find` can encounter blob references, map blob files through manifests/catalog data, and optionally load separated values for matching keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_find_db_val_sep.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_remotecat.go -->
## sources/storage-engines/pebble/tool/make_test_remotecat.go

Purpose: build-tagged generator for the remote object catalog fixture used by `remotecat` tests.

Important APIs/functions: `main` creates a temp dir, opens a `remoteobjcat` catalog, sets creator ID, applies one batch adding object 1, then a second batch adding object 2, deleting object 1, and adding object 3 with a custom object name. It closes the catalog, reads `REMOTE-OBJ-CATALOG-000001`, and writes its bytes to `tool/testdata/REMOTE-OBJ-CATALOG`.

Control flow: all operations fatal on error. Batches use `RemoteObjectMetadata` fields including file number, file type, creator ID/file number, cleanup method, locator, and custom object name.

State and persistence: writes a deterministic catalog fixture in the repo testdata directory, after using a temp directory for catalog creation.

Dependencies and integration: uses `remoteobjcat`, `objstorage.SharedRefTracking`, `base.DiskFileNum`, VFS, and OS file helpers. `remotecat.go` reads and dumps the generated record stream.

Risks: fixture content depends on remote object catalog encoding. Relative output path assumes the generator is run from the Pebble repo root. Permissions use `0666`.

Test signals: supports datadriven coverage of creator ID handling, object additions, deletions, custom object names, and final catalog state rendering.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_remotecat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_sstables.go -->
## sources/storage-engines/pebble/tool/make_test_sstables.go

Purpose: build-tagged generator for SSTable fixtures with unusual key ordering and Cockroach key-schema data.

Important APIs/functions: `makeOutOfOrderSST` creates `tool/testdata/000002.sst` with `DisableKeyOrderChecks` and writes keys `a`, `c`, `b` to create an out-of-order SST. `makeCockroachSchemaSST` creates `tool/testdata/000014.sst` using `cockroachkvs.Comparer`, `cockroachkvs.KeySchema`, max table format, small block size, deterministic random KVs, and writes them. `main` runs both generators.

Control flow: each function creates a file through `vfs.Default`, constructs an SSTable writer with appropriate options, writes records, and closes the writer with fatal error handling.

State and persistence: writes two SST fixtures under `tool/testdata`.

Dependencies and integration: uses SSTable writer internals, object-storage file writable, Cockroach key generator, random PCG seed, and VFS. These fixtures are consumed by SSTable/tool datadriven tests outside the main DB command set and may be referenced by corruption/order scenarios.

Risks: disabling key order checks intentionally creates invalid data that should not be used as a normal fixture. Cockroach random KV generation can change if generator semantics change, requiring fixture updates.

Test signals: enables coverage for SSTable validation against out-of-order keys and key-schema-aware table reading/formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/make_test_sstables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/manifest.go -->
## sources/storage-engines/pebble/tool/manifest.go

Purpose: implements manifest-level introspection commands: `manifest dump`, `manifest summarize`, and `manifest check`, plus manifest discovery.

Important APIs/types/functions: `manifestT` owns command pointers, options, comparers, key formatter, verbosity, key filters, and summarize bucket duration. `newManifest` wires Cobra commands and flags. `runDump` decodes version edits, optionally hex dumps encoded records, filters edits by key overlap, prints edit debug strings, accumulates a bulk edit, and prints the final version. `anyOverlap` and `anyOverlapFile` implement key-range filtering. `runSummarizeOne` buckets version edits by creation timestamps and estimates ingest/flush bytes, compaction out/in bytes, compaction files/sec, and optional lifetime histograms. `runCheck` incrementally applies edits to a `manifest.Version`, printing detailed state on failure. `findManifests` walks a directory for manifest files sorted by file number.

Control flow: dump/check read record streams with `record.Reader`, decode `VersionEdit`, resolve comparer names, and maintain accumulated table metadata needed by `BulkVersionEdit.Apply`. Summarize separately tracks metadata by file number, timestamps, likely compactions, intra-L0 compactions, and deleted-file lifetimes.

State and persistence: commands are read-only and reconstruct state in memory. `runCheck` mutates the in-memory version as each edit applies. `runSummarizeOne` uses creation timestamps as an approximate timeline, not wall-clock record times.

Dependencies and integration: uses Pebble internal `manifest`, `record`, `base`, binary formatting, humanization, hdrhistogram, VFS walking, and key formatter comparers. `db.go` has a separate current-version replay but follows similar manifest mechanics.

Risks: summarization is explicitly approximate; comments note overcounting and misclassification for excise/copy/virtualization cases. `runDump` prints `io.EOF` as a line at end. Filters only apply once a comparer is known. `runCheck` reports first apply error rather than all errors.

Test signals: `manifest_test.go` datadriven fixtures cover dump/summarize/check output, including invalid manifests generated by `make_incorrect_manifests.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/manifest_test.go -->
## sources/storage-engines/pebble/tool/manifest_test.go

Purpose: thin test entry point for manifest command datadriven fixtures.

Important APIs/types/functions: `TestManifest` calls `runTests(t, "testdata/manifest_*")`.

Control flow: every datadriven file matching `manifest_*` is executed through the shared tool harness, so tests invoke manifest commands via Cobra with memfs cloning and custom comparer support.

State and persistence: fixture MANIFEST files are cloned into a memory filesystem. The manifest commands are read-only, except for in-memory accumulated version state during checks and summaries.

Dependencies and integration: indirectly covers `manifest.go`, the shared formatter/comparer setup in `data_test.go`, and fixtures generated by `make_incorrect_manifests.go`.

Risks: test breadth is entirely fixture-driven. Adding a new manifest command or flag does not create coverage until a matching datadriven case is added.

Test signals: confirms stable output for manifest dump, summarize, and check behavior, including invalid manifest diagnostics and key formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/remotecat.go -->
## sources/storage-engines/pebble/tool/remotecat.go

Purpose: implements remote object catalog introspection under `remotecat dump`.

Important APIs/types/functions: `remoteCatalogT` holds the root and dump commands, verbose flag, and Pebble options. `newRemoteCatalog` wires the Cobra command and `--verbose` flag. `runDump` iterates filenames and delegates to `runDumpOne`. `runDumpOne` opens a catalog file, reads record-framed `remoteobjcat.VersionEdit`s, optionally prints each edit with offset/edit index, applies edits to a creator ID and object map, then prints final creator ID and sorted object metadata.

Control flow: record iteration stops on EOF, returns decode/read/apply errors, increments edit index after each record, and sorts final disk file numbers before rendering. Verbose output includes creator ID, new objects, deleted objects, locator, custom object name, and creator file metadata.

State and persistence: read-only. In-memory `creatorID` and `objects` represent the catalog state after replaying all edits.

Dependencies and integration: uses Pebble `record`, `objstorage.CreatorID`, `remoteobjcat.RemoteObjectMetadata`, `base.DiskFileNum`, sorting helpers, and options FS. Test fixtures are produced by `make_test_remotecat.go`.

Risks: `runDumpOne` does not close the opened file, which is a resource leak on repeated dumps. It assumes all catalog records decode under the current remote object catalog schema. Output is tightly coupled to metadata field names and ordering.

Test signals: `remotecat_test.go` datadriven fixture validates final object replay and verbose edit printing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/remotecat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/remotecat_test.go -->
## sources/storage-engines/pebble/tool/remotecat_test.go

Purpose: thin test entry point for remote object catalog command fixtures.

Important APIs/types/functions: `TestRemotecat` calls `runTests(t, "testdata/remotecat")`.

Control flow: the shared datadriven harness executes `remotecat` commands through Cobra, cloning `REMOTE-OBJ-CATALOG` fixtures into memfs and comparing normalized output.

State and persistence: the tested command is read-only. Fixture state comes from `make_test_remotecat.go`, which creates a catalog with creator ID, object additions, deletion, locator, and custom object-name cases.

Dependencies and integration: indirectly covers `remotecat.go`, `data_test.go`, and remote object catalog encoding from Pebble object storage.

Risks: like other thin entry points, this file has no direct assertions beyond the fixture. It will not catch resource leaks such as an unclosed file unless they manifest as test failures.

Test signals: validates user-facing catalog dump output and final replayed object ordering for the remote catalog tool.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/remotecat_test.go -->
