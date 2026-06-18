# subset-b-008518 Research

Grouped research for the Pebble files assigned to `subset-b-008518`. Each file section preserves the original source path and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite.go -->
# sources/storage-engines/pebble/blob_rewrite.go

## Purpose
Implements Pebble's blob-file rewrite compaction: a compaction variant that rewrites a physical blob file under the same logical `BlobFileID`, omitting values that are no longer referenced by live SSTables. Unlike ordinary compactions, it does not rewrite table files; it rewrites the blob payload and applies a `VersionEdit` that remaps the blob file ID from the old disk file number to the new one.

## Important APIs, Types, and Functions
`pickedBlobFileCompaction` is the picker output and records the target blob file, the referenced version, referencing tables, and whether high-priority garbage heuristics selected it. `ConstructCompaction` refs the version and builds a `blobFileRewriteCompaction`. `blobFileRewriteCompaction` implements the internal `compaction` interface through `AddInProgressLocked`, `Execute`, `Info`, `UsesBurstConcurrency`, cancellation, tracing, labels, and metrics hooks. `DB.runBlobFileRewriteLocked` performs the actual rewrite outside `DB.mu`. `blobFileRewriter`, `blockHeap`, and `blockValues` combine per-SSTable blob-reference liveness encodings and drive `blob.FileRewriter.CopyBlock`.

## Control Flow
The picker constructs a compaction with a referenced manifest version. `Execute` announces begin events, calls `runBlobFileRewriteLocked`, then under manifest update checks that the target blob file ID still maps to the same physical file. If the mapping disappeared, the compaction is cancelled; if it changed, an assertion fires because only one rewrite for a given blob should run. On success it installs a `VersionEdit` deleting the old physical blob and adding the new physical blob for the same `FileID`, updates metrics and read state, and emits an end event. The lower-level rewriter builds a heap of `BlobRefLivenessEncoding` values from all referencing tables, groups encodings by blob block ID, unions live value IDs, and copies only live values into the output file.

## State and Persistence Behavior
Persistent state changes are confined to the new blob object, object-provider sync, and the manifest `VersionEdit`. The file uses a `block.BufferPool` to avoid polluting the block cache while reading liveness blocks. `bytesWritten`, iterator block-read stats, and burst-concurrency counters feed compaction accounting. On failure after creating an output file, the output is recorded as obsolete for deletion pacing. The old blob file is only logically deleted after the version edit is accepted.

## Dependencies and Integration Points
This code integrates with the compaction picker/scheduler, manifest versioning, `objstorage`, blob writer/rewriter code, SSTable readers, columnar blob-reference liveness blocks, event listeners, metrics, `deletepacer`, object I/O tracing, and pprof labels. It depends on `fileCacheHandle.withReader` for reading SSTables and on `manifest.Version.BlobFiles` for stable blob-ID mapping.

## Risks and Edge Cases
The correctness hinge is accurate liveness metadata in all referencing SSTables; missing or malformed liveness encodings can drop live blob values or fail the rewrite. The heap currently stores one item per SSTable block reference, which may be expensive for many references. Cancellation is only checked at manifest application, so the file may still do wasted rewrite work. `Execute` returns nil even after setting event `Err`, which relies on the outer compaction framework's expectations. The output must reduce value size or an assertion catches stale picker statistics. Cleanup uses the input size as an approximate failed-output deletion size.

## Test Signals
Covered by `blob_rewrite_test.go`: datadriven tests validate value-separation metadata and explicit rewrite behavior, and a randomized rewrite test repeatedly rewrites original and rewritten blob files while verifying original blob handles still fetch expected values from new physical files.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite_test.go -->
# sources/storage-engines/pebble/blob_rewrite_test.go

## Purpose
Tests Pebble's blob value separation and blob-file rewrite implementation. It exercises both deterministic datadriven scenarios and randomized rewrite chains that preserve random subsets of live blob values.

## Important APIs, Types, and Functions
`TestBlobRewrite` runs `testdata/blob_rewrite` commands for `init`, `add`, `close-output`, and `rewrite-blob`. It uses `blobtest.Values`, `valsep.ValueSeparation`, `sstable.RawWriter`, a logging in-memory VFS, and `objstorageprovider`. `TestBlobRewriteRandomized` constructs one source blob file and many SSTables, repeatedly runs `newBlobFileRewriter`, and verifies rewritten values through `blob.ValueFetcher`. `constantFileMapping` implements `base.BlobFileMapping` for mapping the logical test blob file to a selected physical output file.

## Control Flow
The datadriven test configures either `PreserveAllHotBlobReferences` or `WriteNewBlobFiles`, writes raw table KVs with inline or blob values, closes output and prints blob references/new blob stats, or constructs a `blobFileRewriter` over named SSTables and target blob metadata. The randomized test writes 1000 values to a blob file, creates 1000 SSTables each referencing one value, then performs 10 rewrite iterations. Each iteration picks a source blob file from the rewrite history, chooses a random non-empty subset of referenced values, rewrites into a new physical file, fetches those values with original block/value handles, and appends the new file to the set of rewrite candidates.

## State and Persistence Behavior
All persistence is in-memory object storage and VFS. The tests deliberately model the production invariant that logical `BlobFileID` remains stable while physical disk file numbers change. Randomized rewrites mutate only test metadata describing which original value indices survive each rewrite. Logging captures file-system/object operations for datadriven expected output.

## Dependencies and Integration Points
The tests touch `valsep`, blob file writers/readers, SSTable raw writers, file cache, block cache, manifest table/blob metadata, object storage, and Pebble test key comparer utilities. They are useful integration tests for the contract between SSTable blob-reference liveness blocks and blob file rewriting.

## Risks and Edge Cases
The randomized test uses time-based seeds, so failures require the logged seed to reproduce. It validates preserved values but not explicitly that omitted values are absent, beyond stats and lower value counts. Datadriven coverage is only as broad as `testdata/blob_rewrite`. The helper `constantFileMapping` always maps a blob ID to the requested disk file, which is appropriate for isolated rewrite validation but bypasses version mapping complexity.

## Test Signals
Strong signals include successful fetch of all preserved values through old handles after rewrite, `stats.ValueCount` bounded by the preserved count, liveness-driven rewrite success in datadriven cases, and expected logging of lazy blob creation and metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cache.go -->
# sources/storage-engines/pebble/cache.go

## Purpose
Exports Pebble's internal block-cache type and constructor as the public `pebble.Cache` API.

## Important APIs, Types, and Functions
`type Cache = cache.Cache` is a type alias, not a wrapper, so all methods and reference-count semantics of `internal/cache.Cache` are exposed directly. `NewCache(size int64) *cache.Cache` calls `cache.New(size)`.

## Control Flow
There is no internal control flow beyond constructing the cache. The comments describe the intended lifecycle: create the cache, pass it into one or more DBs, and usually release the creator's reference with `Unref` after DB creation.

## State and Persistence Behavior
The cache is process memory only. It allocates memory on demand and starts with reference count 1. DBs that use it add their own references. No filesystem state is persisted.

## Dependencies and Integration Points
The file depends only on `github.com/cockroachdb/pebble/internal/cache`. Integration points are `Options.Cache`, tests that create block-cache handles, file-cache reader setup, and all SSTable/block reading paths that use Pebble's shared block cache.

## Risks and Edge Cases
Mismanaging references can leak cache memory or prematurely release it while DBs still rely on it. Because this is an alias, changes to the internal cache API surface through the public Pebble package. A zero or very small size is delegated to internal cache behavior.

## Test Signals
No direct tests live in this file. Indirect coverage appears throughout Pebble tests that call `NewCache`, create cache handles, and unref them, including blob rewrite tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint.go -->
# sources/storage-engines/pebble/checkpoint.go

## Purpose
Implements `DB.Checkpoint`, which creates a filesystem snapshot of a Pebble database directory containing a consistent MANIFEST prefix, OPTIONS file, format marker, relevant SSTables/blob files, remote object catalog state, and WAL records truncated to the snapshot's visible sequence number.

## Important APIs, Types, and Functions
`CheckpointOption`, `WithFlushedWAL`, `WithRestrictToSpans`, and `CheckpointSpan` define the public options. `excludeFromCheckpoint` filters SSTables that do not overlap restricted spans. `mkdirAllAndSyncParents` creates the checkpoint directory and syncs newly created parents and the closest existing ancestor. `DB.Checkpoint` orchestrates snapshot construction. `copyCheckpointOptions` copies OPTIONS while commenting out the WAL Failover stanza. `DB.writeCheckpointManifest` copies record-aligned MANIFEST data and appends deletion edits for excluded files.

## Control Flow
`Checkpoint` rejects an existing destination. If requested, it writes synced empty log data to flush the WAL. It disables file deletion, locks the manifest, captures current version, format version, manifest file number/size, options number, virtual backing files, blob files, WAL list, flushable ingest files, and visible sequence number, refs the current version, then releases locks. It creates/syncs the destination, copies OPTIONS, writes the format marker, links or copies local table/blob files, records remote files for object-provider checkpoint state, appends manifest deletions for excluded tables/blobs, copies WALs through `wal.Copy` up to `visibleSeqNum`, syncs/closes the checkpoint directory, and removes the partial destination on error.

## State and Persistence Behavior
The implementation is crash-conscious: parent dirs are synced after creation, checkpoint files are written through a syncing FS, MANIFEST records are copied via `record.Reader`/`Writer`, marker directory sync happens before manifest marker movement, WALs are copied rather than linked, and the final checkpoint dir is synced. Version refs and disabled file deletion protect live physical files while copying. Restricted checkpoints rewrite manifest state to remove excluded SSTables and blob files.

## Dependencies and Integration Points
The code integrates with manifest/version state, virtual SSTable backing metadata, blob-file metadata, WAL manager/list/copy, object provider lookup and remote checkpoint state, VFS hard-link/copy behavior, atomic filesystem markers, OPTIONS parsing, flushable ingest replay, and Pebble format-version markers.

## Risks and Edge Cases
Restricted checkpoints are approximate: WALs and partially overlapping SSTs can still expose keys outside requested spans, and excluded SSTs can make some visible keys invalid relative to the full DB history. Shared/remote files depend on object-provider checkpoint state and in-memory references; comments warn shared file references may be lost after DB restart unless the checkpoint consumer handles that operationally. WAL copy must exclude writes after the captured visible sequence number. Manifest copying must remain record-aligned when appending deletion edits. Flushable ingest SSTs must be copied even if not yet in the LSM.

## Test Signals
`checkpoint_test.go` covers datadriven checkpoint/open/list/scan behavior, shared storage, options rewriting, concurrent checkpoint and compaction, WAL flushing through crashable memory, many-file restricted manifests crossing record boundaries, and pending flushable ingest regression coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint_test.go -->
# sources/storage-engines/pebble/checkpoint_test.go

## Purpose
Tests checkpoint creation across local/shared storage, restricted spans, compactions, WAL durability, large manifests, and flushable ingest files.

## Important APIs, Types, and Functions
`testCheckpointImpl` is the datadriven harness over `testdata/checkpoint` and `testdata/checkpoint_shared`. It supports commands for opening DBs, applying batches, checkpointing, ingest/excise/build helpers, printing backing files, compacting, flushing, listing, scanning, and closing. `TestCopyCheckpointOptions`, `TestCheckpoint`, `TestCheckpointCompaction`, `TestCheckpointFlushWAL`, `TestCheckpointManyFiles`, and `TestCheckpointFlushableIngest` cover focused behaviors.

## Control Flow
The datadriven harness keeps named DB handles on a logging in-memory VFS plus optional in-memory remote storage. Checkpoint commands parse `restrict=start-end` spans and call `DB.Checkpoint`. The shared-storage variant configures `CreateOnSharedAll` and creator IDs. The compaction stress test concurrently writes keys, compacts, checkpoints 50 directories, and opens each checkpoint to verify all manifest-referenced non-virtual tables exist. The WAL flush test writes unsynced data, checkpoints with `WithFlushedWAL`, crash-clones unsynced data away, and verifies the checkpoint opens with the data. The flushable ingest test forces an overlapping ingest into the memtable queue, checkpoints, and verifies replay can open and read the ingested value.

## State and Persistence Behavior
Tests inspect filesystem operation logs, checkpoint directory listings, manifest-derived table references, WAL file size, virtual backing removal, and replay of flushable ingest records. All persistent state is modeled by in-memory or crashable VFS plus optional in-memory remote storage.

## Dependencies and Integration Points
The harness exercises DB open/close, batch commit, compaction, ingestion, excision, remote storage factory, SSTable writer, VFS logging, crashable memory, and table stats/cleanup waiting. It depends on datadriven files for expected operation traces.

## Risks and Edge Cases
The concurrency test is stress-style and may not deterministically hit every race. `TestCheckpointManyFiles` is skipped under `testing.Short`. Datadriven traces may be sensitive to iterator stack and file open behavior, which is why the harness pins `IteratorStackV1`. Shared-storage behavior is skipped on Windows.

## Test Signals
Signals include successful reopen of checkpoints, scans matching expected data, file operation traces, absence of missing SSTables during checkpoint/compaction races, durable WAL content after simulated crash, exact 10-key restricted checkpoint iteration in many-file tests, and successful WAL replay with pending ingested flushables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/close_test.go -->
# sources/storage-engines/pebble/close_test.go

## Purpose
Regression test ensuring `DB.Close` cancels background contexts and completes promptly even when background table-stats loading or compactions are blocked on remote object reads.

## Important APIs, Types, and Functions
`TestCloseWithBlockedRemoteIO` constructs a DB with remote storage, ingests an external remote file, enables blocking reads, then closes the DB with a timeout. `blockingRemoteStorage` wraps `remote.Storage`; `blockingObjectReader.ReadAt` blocks on `ctx.Done()` after blocking is enabled.

## Control Flow
The test writes an SSTable into the wrapped remote storage, calls `IngestExternalFiles`, then flips the storage into blocking mode. A goroutine calls `d.Close()`. If close cancels the database background context correctly, any blocked remote `ReadAt` returns `ctx.Err()` and close completes. If not, the test fails after 10 seconds.

## State and Persistence Behavior
The file uses in-memory local VFS and in-memory remote storage. The interesting state is cancellation state: `DB.Close` must transition background work from active to cancelled and wait for goroutines without hanging on remote I/O.

## Dependencies and Integration Points
Touches external-file ingestion, remote storage factories, SSTable writing, table stats loading, background compactions, context propagation through object readers, and DB close orchestration.

## Risks and Edge Cases
The timeout is necessarily coarse; it proves no hang in this scenario but not every remote I/O path. `blockingRemoteStorage.block` closes its channel once and is not designed for toggling. It assumes background activity attempts a read after ingestion or that close handles any in-progress read.

## Test Signals
The key signal is `d.Close()` returning nil before the 10-second timeout after remote reads are configured to block until context cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/close_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbench.go -->
# sources/storage-engines/pebble/cmd/pebble/fsbench.go

## Purpose
Defines the `pebble bench fs <dir>` Cobra command for running named filesystem benchmarks from the `bench` package.

## Important APIs, Types, and Functions
`fsBenchConfig` starts with `NumTimes: 1` and `FS: vfs.Default`. `fsBenchCmd` declares usage, help text, argument validation, and `RunE`. `init` binds `--max-ops`, required `--bench-name`, `--num-times`, and adds `listFsBench`. `runFsBench` copies `commonCfg.Verbose` into the filesystem benchmark config and delegates to `bench.RunFsBench`.

## Control Flow
Cobra parses flags, requires one directory argument and a benchmark name, then `runFsBench` invokes the benchmark runner with the shared common config and command-specific config.

## State and Persistence Behavior
The command may create or mutate files under the supplied benchmark directory according to the selected benchmark. This file only stores process-global config populated by flags.

## Dependencies and Integration Points
Depends on `bench.FsBenchConfig`, `bench.RunFsBench`, `vfs.Default`, Cobra, and `commonCfg` from `main.go`. It integrates with `fsbenchlist.go` through the nested `list` subcommand.

## Risks and Edge Cases
Config is global, so repeated in-process command execution could retain mutated fields. `MarkFlagRequired` errors are ignored, though Cobra usually records the requirement. Resource exhaustion is controlled by the benchmark implementation and user flags.

## Test Signals
No direct tests in this file. Useful signals are Cobra parsing, required flag enforcement, and `bench.RunFsBench` receiving expected directory/config values.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbenchlist.go -->
# sources/storage-engines/pebble/cmd/pebble/fsbenchlist.go

## Purpose
Defines `pebble bench fs list`, which lists available filesystem benchmarks or prints descriptions for specific benchmark names.

## Important APIs, Types, and Functions
`listFsBench` is the Cobra command. `runListFsBench` calls `bench.FsBenchmarks(vfs.Default)` and prints either all names or selected benchmark name/description pairs.

## Control Flow
With no arguments, it iterates the benchmark map and prints names. With arguments, it looks each name up, prints metadata, and returns an error for an unknown name.

## State and Persistence Behavior
No persistent state is read or written. Output goes to standard output through `fmt.Println`.

## Dependencies and Integration Points
Depends on `bench.FsBenchmarks`, `vfs.Default`, Cobra, and CockroachDB errors. It is attached as a child command in `fsbench.go`.

## Risks and Edge Cases
Map iteration order is nondeterministic, so output ordering may vary. Unknown names abort the command on the first missing benchmark.

## Test Signals
No direct tests. CLI smoke tests should verify non-empty listing and unknown-name error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbenchlist.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/main.go -->
# sources/storage-engines/pebble/cmd/pebble/main.go

## Purpose
Assembles the `pebble` command-line tool, including benchmark commands and introspection/tool commands with Pebble, Cockroach, and test key schema support.

## Important APIs, Types, and Functions
Global `commonCfg` holds shared benchmark options; `maxOpsPerSec` parses `--rate`. `testKeysSchema` and `defaultSchema` register columnar key schemas. `main` creates `bench` and root Cobra commands, initializes replay/scan/sync/tombstone/YCSB/fs/write benchmark commands, wires `tool.New` commands, and binds shared flags.

## Control Flow
The executable disables Cobra command sorting, builds the command tree, sets the root version string to supported Pebble format versions, assigns a 1 GiB ballast in `commonCfg`, installs common flags on relevant benchmark commands, then executes the root command and exits with code 1 if Cobra returns an error.

## State and Persistence Behavior
The file manages process-global configuration and command structure. Persistence is performed by subcommands or tool commands, not directly here. The default ballast setting reserves disk emergency space for opened DBs through shared benchmark config.

## Dependencies and Integration Points
Integrates `pebble`, `bench`, `cockroachkvs`, `testkeys`, `base.DefaultComparer`, `colblk`, `tool`, and Cobra. It registers comparers, mergers, and key schemas so CLI readers can understand Cockroach and test SSTables.

## Risks and Edge Cases
Global config can carry state across multiple command executions in tests. Several commands share the same `commonCfg` and rate flag, so flag defaults and initialization order matter. The tool assumes installed schemas are sufficient for the CLI's SSTable formats.

## Test Signals
No direct tests. Signals include `pebble --version`, command tree availability, flag parsing across benchmark commands, and successful reads of Cockroach/testkey SSTables through tool commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/queue.go -->
# sources/storage-engines/pebble/cmd/pebble/queue.go

## Purpose
Provides shared flag binding for queue-style benchmark configuration used by the tombstone workload.

## Important APIs, Types, and Functions
`initQueue(cmd *cobra.Command, cfg *bench.QueueConfig)` binds `--queue-size` and `--queue-values` to a command.

## Control Flow
The helper is called during command initialization, notably from `tombstone.go`, and mutates the target command's flag set.

## State and Persistence Behavior
Only command/config state is changed. The queue workload's database mutations are implemented in the `bench` package.

## Dependencies and Integration Points
Depends on Cobra and `bench.QueueConfig`. Integrates with `bench.RunTombstone` through `tombstoneConfig.Queue`.

## Risks and Edge Cases
The helper assumes `cfg.Values` is a non-nil flag value. Reusing it on a command with already-defined flag names would produce Cobra flag conflicts.

## Test Signals
No direct tests. Signals are successful parsing of queue size/value distributions and their effect on tombstone benchmark workload shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/random.go -->
# sources/storage-engines/pebble/cmd/pebble/random.go

## Purpose
Implements the `--rate` flag parser and rate-limiter factory for benchmark commands.

## Important APIs, Types, and Functions
`rateFlag` embeds `randvar.Flag` and adds a fluctuation period plus original spec string. `newRateFlag`, `String`, `Type`, `Set`, and `newRateLimiter` implement Cobra/pflag value behavior and create a `rate.Limiter`.

## Control Flow
An empty spec is converted to a zero random variable and disables limiter creation. Non-empty specs are split on optional `/periodSeconds`; the left side is parsed by `randvar.Flag`, and the optional right side controls a goroutine that periodically changes limiter rate from the random distribution.

## State and Persistence Behavior
State is process memory: parsed random-variable configuration, duration, and spec string. No persistent state is written. A fluctuating limiter starts a ticker goroutine that runs for process lifetime; there is no explicit stop path.

## Dependencies and Integration Points
Depends on Pebble internal `randvar` and `rate` packages, `time`, string parsing, and CockroachDB errors. `main.go` binds it to shared benchmark flags, and individual benchmark runners assign `commonCfg.RateLimiter`.

## Risks and Edge Cases
`time.Duration(fluctuateDurationFloat) * time.Second` truncates fractional seconds before multiplying, so `0.5` becomes zero. The ticker goroutine is not stopped. Invalid split counts, random-variable specs, or period parsing return errors. A spec that evaluates to zero creates a limiter with zero rate.

## Test Signals
No direct tests. Useful checks include empty spec returning nil limiter, valid uniform/zipf specs, invalid parse errors, and fluctuating rate changes over time.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/random.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/replay.go -->
# sources/storage-engines/pebble/cmd/pebble/replay.go

## Purpose
Defines `pebble bench replay <workload>`, a wrapper around captured write-workload replay support in the `bench` package.

## Important APIs, Types, and Functions
`initReplayCmd` creates a default replay config, returns a Cobra command, and binds flags for count, workload name, pacer, max writes, options string, run directory, cache size, log streaming, checkpoint ignoring, and checkpoint directory.

## Control Flow
At command execution, Cobra validates exactly one workload argument and calls `c.RunReplay(cmd.OutOrStdout(), commonCfg.Verbose, args[0])`.

## State and Persistence Behavior
This wrapper only mutates the replay config from flags. Replay itself may create a run directory, use checkpoints, open Pebble DBs, write data, and stream logs depending on config.

## Dependencies and Integration Points
Depends on `bench.DefaultReplayConfig`, replay pacer implementations, Cobra, and shared `commonCfg.Verbose`. It is installed under `bench` from `main.go`.

## Risks and Edge Cases
The closure captures a single config instance, so repeated command execution in-process may retain mutations. `OptionsString` accepts whitespace-delimited OPTIONS overrides, which can be user-error-prone. Checkpoint flags can change replay starting state substantially.

## Test Signals
No direct tests here. Signals include flag parsing, pacer selection, respecting max writes, and replay command output through `cmd.OutOrStdout`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/replay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/scan.go -->
# sources/storage-engines/pebble/cmd/pebble/scan.go

## Purpose
Defines `pebble bench scan <dir>`, a scan benchmark wrapper.

## Important APIs, Types, and Functions
`scanConfig` is `bench.DefaultScanConfig()`. `scanCmd` binds usage and exact-arg validation. `init` adds `--reverse`, `--rows`, and `--values`. `runScan` assigns a rate limiter and calls `bench.RunScan`.

## Control Flow
The command parses flags, constructs `commonCfg.RateLimiter` from `maxOpsPerSec`, and delegates execution to the benchmark package.

## State and Persistence Behavior
Only config globals are changed here. The benchmark may open or populate a DB under the supplied directory depending on `commonCfg`.

## Dependencies and Integration Points
Depends on Cobra and `bench.ScanConfig`. It uses common flags bound in `main.go` such as cache, duration, concurrency, WAL, wipe, shared storage, and rate.

## Risks and Edge Cases
`Run` rather than `RunE` means benchmark errors, if any, must be handled internally by `bench.RunScan`. Global config reuse can affect repeated runs.

## Test Signals
No direct tests. Signals are correct scan direction, row/value distribution parsing, and rate limiter propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/scan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/sync.go -->
# sources/storage-engines/pebble/cmd/pebble/sync.go

## Purpose
Defines `pebble bench sync <dir>`, a benchmark for synchronous writes or WAL-only writes.

## Important APIs, Types, and Functions
`syncConfig` is `bench.DefaultSyncConfig()`. `syncCmd` declares the command. `init` binds `--batch`, `--wal-only`, and `--values`. `runSync` installs a rate limiter and calls `bench.RunSync`.

## Control Flow
Cobra validates one directory argument, parses benchmark-specific and shared flags, then the runner delegates to `bench.RunSync`.

## State and Persistence Behavior
This wrapper stores in-memory config. Persistence and WAL behavior are performed by the benchmark implementation and depend on `--wal-only`, `--disable-wal`, `--wipe`, and related shared flags.

## Dependencies and Integration Points
Depends on Cobra and `bench.SyncConfig`. It uses `random.go` rate limiting and `main.go` shared benchmark config.

## Risks and Edge Cases
Contradictory durability flags are possible at the CLI layer and must be handled by `bench.RunSync`. `Run` cannot return an error to Cobra.

## Test Signals
No direct tests. Signals include batch/value distribution parsing, WAL-only mode behavior, and throughput pacing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/sync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/tombstone.go -->
# sources/storage-engines/pebble/cmd/pebble/tombstone.go

## Purpose
Defines `pebble bench tombstone <dir>`, a mixed YCSB plus queue workload intended to evaluate point-tombstone compaction heuristics.

## Important APIs, Types, and Functions
`tombstoneConfig` starts from `bench.DefaultTombstoneConfig()`. `init` calls `initQueue` and `initYCSB` to share queue and YCSB flags. `tombstoneCmd` contains extensive CLI help explaining workload intent. `runTombstoneCmd` assigns a rate limiter and calls `bench.RunTombstone`.

## Control Flow
The command validates one directory argument, parses YCSB/queue/shared flags, sets rate limiting, then runs the benchmark.

## State and Persistence Behavior
The benchmark mutates the target DB through queue sets/deletes and YCSB operations. This wrapper only stores process-global config.

## Dependencies and Integration Points
Depends on `bench.TombstoneConfig`, queue flag binding, YCSB flag binding, shared common config, and Cobra. Integration with compaction heuristics is indirect through the workload generated by `bench.RunTombstone`.

## Risks and Edge Cases
Because it reuses YCSB and queue config, flag interactions can be complex. The benchmark can grow disk usage if compaction heuristics fail, so `--max-size`, duration, and wipe flags matter. Global state can leak across repeated in-process invocations.

## Test Signals
No direct tests. Useful signals are workload mix correctness, tombstone generation rate, queue live-key count stability, and compaction/disk metrics under the benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/tombstone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/write_bench.go -->
# sources/storage-engines/pebble/cmd/pebble/write_bench.go

## Purpose
Defines `pebble bench write <dir>`, a YCSB-F based benchmark that searches for sustainable write throughput.

## Important APIs, Types, and Functions
`writeBenchConfig` is `bench.DefaultWriteBenchConfig()`. `writeBenchCmd` declares CLI help and execution. `initWriteBench` binds workload, rate search, concurrency, L0 target, cooloff/test-period, wipe, and debug flags. `runWriteBenchmark` delegates to `bench.RunWriteBench`.

## Control Flow
The benchmark wrapper parses flags, then `bench.RunWriteBench` repeatedly tests write rates, classifies pass/fail according to L0 and write-stall heuristics, cools off after failures, and computes an optimal sustained rate. The search logic is documented in the command's long help but implemented in `bench`.

## State and Persistence Behavior
This file changes only config state. The benchmark itself writes to the target database, may wipe it first, and tracks rate-classification state in process.

## Dependencies and Integration Points
Depends on Cobra and `bench.WriteBenchConfig`. It shares `commonCfg.Wipe` with other benchmark commands and uses shared duration flags bound in `main.go`.

## Risks and Edge Cases
The command-level text has one extra quote in "fails\""; harmless but visible. Rate search can stress storage heavily; guardrails depend on duration, max-size, and benchmark heuristics. Global config reuse can affect repeated in-process use.

## Test Signals
No direct tests. Signals are flag parsing, convergence behavior, correct pass/fail classification, and final optimal write-load reporting from `bench.RunWriteBench`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/write_bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/ycsb.go -->
# sources/storage-engines/pebble/cmd/pebble/ycsb.go

## Purpose
Defines `pebble bench ycsb <dir>`, a configurable YCSB workload runner.

## Important APIs, Types, and Functions
`ycsbConfig` is `bench.DefaultYCSBConfig()`. `ycsbCmd` declares usage and detailed help for workload and distribution flags. `initYCSB` binds batch, key distribution, initial/prepopulated key counts, op limit, scan length, workload mix, and value distribution. `runYcsb` installs a rate limiter and delegates to `bench.RunYCSB`.

## Control Flow
After Cobra parses one directory argument and flags, `runYcsb` constructs the shared rate limiter and passes config to the benchmark package.

## State and Persistence Behavior
The wrapper stores config in globals. The YCSB benchmark populates and mutates a Pebble DB according to workload, key distribution, and shared DB options.

## Dependencies and Integration Points
Depends on `bench.YCSBConfig`, `randvar` flag types, Cobra, shared `commonCfg`, and `random.go` rate limiting. The helper is reused by `tombstone.go`.

## Risks and Edge Cases
The `cfg.Batch`, `cfg.Scans`, and `cfg.Values` fields are type-asserted to specific randvar flag types; incompatible config implementations would panic. Workload strings are validated in the bench package, not here. Global config reuse can leak state between runs.

## Test Signals
No direct tests. Useful signals are parsing standard A-F and custom workload mixes, respecting op limits and initial/prepopulated key counts, and applying rate limiter settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/ycsb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/blockproperties.go -->
# sources/storage-engines/pebble/cockroachkvs/blockproperties.go

## Purpose
Defines CockroachDB-specific SSTable block property collectors and filters for MVCC wall-time intervals. These properties enable Pebble readers to skip blocks outside timestamp constraints and support suffix replacement for synthetic suffixes/range-key masking.

## Important APIs, Types, and Functions
`BlockPropertyCollectors` constructs a block interval collector named `MVCCTimeInterval`. `NewMVCCTimeIntervalFilter` creates a half-open wall-time filter `[minWallTime, maxWallTime+1)`. `MVCCWallTimeIntervalRangeKeyMask` wraps `sstable.BlockIntervalFilter` and sets intervals from range-key suffixes. `MVCCBlockIntervalSuffixReplacer` maps synthetic suffix replacement to a single-wall-time interval. `pebbleIntervalMapper` maps point and range keys to intervals through `mapSuffixToInterval`. `MaxMVCCTimestampProperty.Extract` extracts a maximum suffix-like timestamp from encoded block interval properties.

## Control Flow
Point keys map their user key's encoded MVCC suffix to a `{Lower: wall, Upper: wall+1}` interval. Range keys union the intervals of each suffixed range key. Empty or non-MVCC suffixes map to empty intervals. Filters compare block intervals against requested wall-time ranges. Maximum suffix extraction decodes the interval property and encodes `interval.Upper` as a wall-time-only suffix.

## State and Persistence Behavior
Collectors persist encoded block interval properties in SSTables. Filters and masks are in-memory reader-side state. The half-open interval encoding intentionally stores `Upper` one greater than the largest wall time.

## Dependencies and Integration Points
Depends on `sstable` block property APIs and timestamp decoding from `cockroachkvs.go`. Integrates with CockroachDB MVCC scans, range-key masking, synthetic suffix replacement, and maximum suffix property use in table/block metadata.

## Risks and Edge Cases
`NewMVCCTimeIntervalFilter` adds one to `maxWallTime`, so `math.MaxUint64` would overflow. `ApplySuffixReplacement` returns an assertion failure if synthetic suffix decoding fails. `mapSuffixToInterval` must distinguish full engine keys from bare suffixes using the sentinel index; malformed keys return errors. `MaxMVCCTimestampProperty` encodes `Upper`, not `Upper-1`, to remain a valid upper bound under logical timestamp ordering.

## Test Signals
Direct tests are not in this file, but Cockroach key-schema and SSTable tests indirectly exercise suffix decoding and ordering. Dedicated tests should verify interval collection for wall-only/logical/synthetic timestamps, non-MVCC suffix exclusion, range-key unioning, max timestamp extraction, and overflow behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/blockproperties.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs.go

## Purpose
Provides CockroachDB's Pebble key encoding, comparer, formatter/parser, and columnar data-block key schema. It supports Cockroach MVCC keys whose user key is a roach key plus `0x00` sentinel plus optional version bytes and trailing version-length byte.

## Important APIs, Types, and Functions
Public exports include `Comparer`, `EncodeMVCCKey`, `AppendTimestamp`, `EncodeTimestamp`, `NewTimestampSuffix`, `DecodeMVCCTimestampSuffix`, `DecodeEngineKey`, `EncodeKey`, `Split`, `Compare`, `CompareRangeSuffixes`, `ComparePointSuffixes`, `Equal`, `KeySchema`, `FormatKey`, `FormatKeySuffix`, `ParseFormattedKey`, and `ParseFormattedKeySuffix`. Internal components include suffix normalization, `cockroachKeyWriter`, `cockroachKeySeeker`, `suffixTypes`, `validateEngineKey`, and unsafe `memmove`-based materialization.

## Control Flow
Encoding appends a sentinel and optional timestamp/version bytes. Comparison first compares prefix/user key bytes through the sentinel, then compares suffixes in reverse timestamp order; point suffix comparisons normalize away synthetic bits and zero logical components, while range suffix comparison intentionally avoids normalization for historical compatibility. The columnar writer splits keys into roach-key prefix bytes, wall time, logical time, and untyped version columns, tracking which suffix classes are present. The seeker decodes these columns, performs prefix search, then either uses a fast MVCC-only timestamp binary search or a general suffix search. Materialization reconstructs engine keys from decoded columns or applies synthetic suffixes.

## State and Persistence Behavior
The key schema persists columnar block data with a one-byte schema-specific header containing `suffixTypes`. The comparer and formatter are stateless. Unsafe materialization writes directly into iterator buffers and assumes sufficient capacity. Validation enforces terminator length constraints but allows empty keys for separator/index-block cases.

## Dependencies and Integration Points
Integrates with Pebble `base.Comparer`, SSTable columnar block encoding (`colblk`), block iterators, Cockroach MVCC timestamp conventions, Cockroach lock-table key suffixes, and CLI/tool formatting. It uses `crbytes` for common prefixes, invariants for validation, and unsafe metadata casting to fit `cockroachKeySeeker` into `colblk.KeySeekerMetadata`.

## Risks and Edge Cases
Ordering correctness depends on suffix normalization matching Cockroach's engine semantics, including synthetic and zero-logical treatment. Range suffix comparison intentionally differs from point suffix comparison. Unsafe code and `go:linkname` `memmove` require exact buffer sizing and metadata layout. Empty suffix, MVCC suffix, and lock/untyped suffix mixing is rare but handled by a slower path. Parser/formatter panics on invalid human input. `validateEngineKey` permits empty keys but rejects terminator byte `1` and oversized terminators.

## Test Signals
Covered by `cockroachkvs_test.go`, `key_schema_test.go`, `cockroachkvs_64bit_test.go`, and benchmarks. Tests validate comparer properties, separator/successor behavior, writer/seeker datadriven output, lower-bound logic, random block encoding/iteration/seeking, formatting round trips, and metadata size assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_64bit_test.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs_64bit_test.go

## Purpose
Compile-time layout assertion for 64-bit platforms ensuring `cockroachKeySeeker` is not larger than Pebble's fixed `colblk.KeySeekerMetadata` storage.

## Important APIs, Types, and Functions
The file has build tag `arm64 || amd64` and declares `var _ uint = uint(unsafe.Sizeof(cockroachKeySeeker{})) - colblk.KeySeekerMetadataSize`.

## Control Flow
There is no runtime flow. Compilation fails if the subtraction underflows, which would indicate `cockroachKeySeeker` is smaller than the metadata size according to this particular assertion direction.

## State and Persistence Behavior
No runtime or persistent state exists. The file enforces an ABI/layout constraint at build time.

## Dependencies and Integration Points
Depends on `unsafe`, `cockroachKeySeeker`, and `colblk.KeySeekerMetadataSize`. It complements the opposite assertion in `cockroachkvs.go` that checks the seeker fits inside metadata.

## Risks and Edge Cases
This is architecture-specific and only runs on amd64/arm64. It protects unsafe metadata casting but does not validate field alignment beyond `unsafe.Sizeof`.

## Test Signals
The signal is successful package compilation on supported 64-bit architectures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_64bit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_bench_test.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs_bench_test.go

## Purpose
Benchmarks Cockroach key schema performance in SSTable seeking, columnar data-block writing, data-block iteration/seeking, transform handling, and block metadata initialization.

## Important APIs, Types, and Functions
`BenchmarkRandSeekInSST` compares table formats v4-v7 and single/two-level indexes. `benchmarkRandSeekInSST` writes an in-memory SSTable with `Comparer` and `KeySchema`, warms cache, and repeatedly creates iterators and seeks random query keys. `BenchmarkCockroachDataColBlockWriter`, `BenchmarkCockroachDataColBlockIter`, `BenchmarkCockroachDataColBlockIterTransforms`, `benchmarkCockroachDataColBlockIter`, `benchConfigs`, and `BenchmarkInitDataBlockMetadata` exercise columnar block encoding and iteration.

## Control Flow
Benchmarks generate random keys/values with `RandomKVs`, encode blocks or SSTables, optionally warm block cache, reset timers, and repeatedly perform writer finish, iterator `Next`, iterator `SeekGE`, or metadata init. Transform benchmarks cover synthetic sequence numbers, hiding obsolete points, synthetic prefixes, and synthetic suffixes.

## State and Persistence Behavior
All state is in-memory: `objstorage.MemObj`, cache handles sized to fit objects, random generated blocks, and iterator state. Benchmarks report custom `bytes/row` metrics for block iteration cases.

## Dependencies and Integration Points
Depends on SSTable writer/reader, cache, block reader options, internal cache options, `colblk`, blockiter transforms, random key utilities from `test_utils.go`, and helper `generateDataBlock`/`randomQueryKeys` from tests.

## Risks and Edge Cases
Seeds use current time or random values, so benchmark data varies between runs. Iterator creation is inside the `BenchmarkRandSeekInSST` timed loop, so results include construction cost. The benchmark validates some invariants, but it is performance-focused rather than exhaustive correctness coverage.

## Test Signals
Signals are benchmark throughput and `bytes/row` metrics, plus no failures while seeking latest keys when obsolete points are not hidden. These benchmarks can detect regressions in key schema encoding, seeking, and metadata initialization costs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_test.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs_test.go

## Purpose
Primary correctness tests for Cockroach key comparison, formatting/parsing, key writer/seeker logic, random key generation, and columnar data block encoding/iteration.

## Important APIs, Types, and Functions
`testPrefixes` and `testSuffixes` generate comparison cases including MVCC, synthetic, zero-logical, empty, and lock-table suffixes. `TestComparer` calls `base.CheckComparer`. `TestComparerFuncs`, `TestKeySchema_KeyWriter`, and `TestKeySchema_KeySeeker` are datadriven. `TestKeySeekerIsLowerBound`, `TestRandKeys`, `TestCockroachDataColBlock`, `testCockroachDataColBlock`, `generateDataBlock`, `randomQueryKeys`, formatting helpers, parsing helpers, and `TestFormatKey` cover randomized and round-trip behavior.

## Control Flow
Comparer tests generate prefixes/suffixes and verify ordering contracts. Datadriven writer tests parse user keys, compare against previous keys, write schema columns, materialize keys back, and print decoded columns. Seeker tests define blocks, initialize key seeker metadata, call `IsLowerBound`, `SeekGE`, and materialization with optional synthetic suffixes. Randomized block tests generate 100 key configurations, encode blocks, scan with `Next`, seek random keys, and ensure values match.

## State and Persistence Behavior
The tests operate on in-memory encoded blocks and no persistent files. They model persisted columnar block bytes and decode them into iterators/seeker metadata. Random key generation carries base wall time and distribution parameters.

## Dependencies and Integration Points
Depends on Pebble internal base keys, datadriven, `colblk`, block iterators, tablewriter output, Cockroach key helpers, `RandomKVs`, and generated testdata. It exercises the public comparer/key schema as a consumer would through block encoders and iterators.

## Risks and Edge Cases
Several randomized tests use time-based seeds and stop after a fixed number of generated configurations. Parser helpers panic on invalid inputs and are test-only. Datadriven expected output can be sensitive to formatting. The tests focus on point-key columnar behavior, with block property behavior covered only indirectly.

## Test Signals
Strong signals include comparer contract success, separator/successor output, exact writer/seeker datadriven transcripts, lower-bound equivalence to comparer ordering for single-row blocks, random scan and seek equality, value round trips, and format/parse round trips including panic checks for invalid formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/key_schema_test.go -->
# sources/storage-engines/pebble/cockroachkvs/key_schema_test.go

## Purpose
Additional key-schema tests focused on full `colblk.DataBlockEncoder`/`DataBlockIter` behavior, datadriven block descriptions, suffix-type headers, seeking, and random serialized engine keys.

## Important APIs, Types, and Functions
`TestKeySchema` runs datadriven files `suffix_types`, `block_encoding`, and `seek`. `runDataDrivenTest` supports `init`, `describe`, `suffix-types`, `keys`, and `seek`. `TestKeySchema_RandomKeys` generates random serialized engine keys. `randomSerializedEngineKey` creates keys with possible no-version, wall, logical, synthetic, or lock-table version lengths.

## Control Flow
The datadriven harness initializes an encoder and iterator, parses internal KVs, adds them with `KeyWriter.ComparePrev`, verifies `MaterializeLastUserKey`, finishes the block, decodes descriptions, prints suffix types, iterates keys, and performs seeks. The randomized test sorts generated keys with `Compare`, encodes them, decodes an aligned block, scans all keys, verifies materialized keys compare equal and are not longer than originals, seeks exact keys and prefixes, and checks stored values.

## State and Persistence Behavior
State is in-memory serialized columnar block data. The tests validate the bytes that would be persisted in SSTable data blocks, including schema-specific headers and decoded columns.

## Dependencies and Integration Points
Depends on `colblk`, `blockiter`, `binfmt`, `treeprinter`, `pebble.InternalKey`, `Comparer`, `KeySchema`, and parsing helpers from `cockroachkvs_test.go`.

## Risks and Edge Cases
Random engine keys are structurally valid enough for tests but may include arbitrary bytes. Synthetic suffix keys may materialize shorter normalized forms, so the test intentionally allows physical key differences while requiring logical equality. Datadriven expected output can require updates when encoding details change.

## Test Signals
Signals include exact block descriptions, suffix-type classification, ordered iteration, successful exact and prefix seeks, value equality, key validation, and preservation of logical equality across normalized materialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/key_schema_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/rowblk_bench_test.go -->
# sources/storage-engines/pebble/cockroachkvs/rowblk_bench_test.go

## Purpose
Benchmarks legacy row-block writer and iterator behavior with Cockroach keys, providing a comparison point for columnar block benchmarks.

## Important APIs, Types, and Functions
`BenchmarkCockroachDataRowBlockWriter`, `benchmarkCockroachDataRowBlockWriter`, `BenchmarkCockroachDataRowBlockIter`, and `benchmarkCockroachDataRowBlockIter` use shared `benchConfigs`, `RandomKVs`, `rowblk.Writer`, and `rowblk.Iter`.

## Control Flow
Writer benchmarks reset a row-block writer with restart interval 16, add generated internal keys and values until target block size, and finish. Iterator benchmarks prebuild one block, initialize a row-block iterator with `Compare`, `ComparePointSuffixes`, and `Split`, then time `Next` loops and random exact `SeekGE` calls.

## State and Persistence Behavior
All benchmark state is in memory. The serialized row block represents persisted block bytes for performance measurement only.

## Dependencies and Integration Points
Depends on `rowblk`, Pebble internal base keys, block value-prefix handling, blockiter transforms, shared Cockroach key generation and benchmark configs from other test files.

## Risks and Edge Cases
Seeds use current time, so generated distributions vary. The benchmarks validate `SeekGE` does not return nil for sampled existing keys but are not full correctness tests. Comparisons with columnar benchmarks should account for different writer/iterator implementations and included work.

## Test Signals
Signals are benchmark timings and `bytes/row` metrics for row-block write, scan, and seek paths under Cockroach key distributions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/rowblk_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/test_utils.go -->
# sources/storage-engines/pebble/cockroachkvs/test_utils.go

## Purpose
Provides random Cockroach key/value generation utilities shared by tests and benchmarks.

## Important APIs, Types, and Functions
`KeyGenConfig` describes key shape, prefix sharing, average keys per prefix, base wall time, and suffix mix percentages. `KeyGenConfig.String` formats common benchmark names. `RandomKVs` returns sorted keys and random values. `makeMVCCKey`, `cockroachKeyGen`, `makeCockroachKeyGen`, `randRoachKey`, and `randTimestamp` implement generation internals.

## Control Flow
`RandomKVs` constructs a shared prefix, repeatedly generates roach-key prefixes, samples an exponential number of suffixes per prefix, chooses empty/lock/MVCC suffixes according to configured percentages, fills random values, and sorts keys with `Compare`.

## State and Persistence Behavior
No persistent state. Generated keys and values are in-memory fixtures that model Cockroach key distributions for block and SSTable tests.

## Dependencies and Integration Points
Depends on `math/rand/v2`, `slices`, `time`, and Cockroach key encoding/comparison from `cockroachkvs.go`. Used by correctness tests and benchmarks in the same package.

## Risks and Edge Cases
Misconfigured percentages can make empty plus lock suffix probabilities overlap unexpectedly; the code treats `PercentLockSuffix` as the first slice of the combined threshold. `PrefixAlphabetLen` and key lengths must be sensible; invalid zero alphabet length would panic in `IntN`. `AvgKeysPerPrefix` is clamped to at least one generated key per prefix.

## Test Signals
`TestRandKeys`, randomized key-schema tests, columnar block tests, and benchmarks all depend on this helper. Good signals include sorted output, configurable suffix mixes, stable datadriven output under fixed seeds, and broad coverage of prefix/timestamp distributions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/commit.go -->
# sources/storage-engines/pebble/commit.go

## Purpose
Implements Pebble's concurrent commit pipeline for writing batches to the WAL, applying them to memtables, publishing visible sequence numbers in order, and coordinating WAL sync completion.

## Important APIs, Types, and Functions
`commitQueue` is a lock-free fixed-size single-producer/multi-consumer ring of `Batch` pointers with `enqueue` and `dequeueApplied`. `commitEnv` abstracts sequence-number state and `apply`/`write` callbacks for DB integration and tests. `commitPipeline` owns queues, semaphores, and a mutex. Key methods are `newCommitPipeline`, `directWrite`, `Commit`, `AllocateSeqNum`, `prepare`, and `publish`.

## Control Flow
`Commit` reserves queue capacity, prepares the batch under `commitPipeline.mu` by enqueueing it, assigning sequence numbers, and serially writing to the WAL, then applies to the memtable concurrently. `publish` marks the batch applied, drains any applied batches from the ordered queue, ratchets `visibleSeqNum` to each drained batch's end sequence number, and releases each batch's commit wait group. If it reaches an unapplied head, it waits for another goroutine to publish it. Syncing commits add wait-group work for the WAL log writer; `noSyncWait` returns after publication and leaves fsync waiting to `Batch.SyncWait`.

## State and Persistence Behavior
The WAL write is the durable stage, while memtable application and `visibleSeqNum` publication control read visibility. `logSeqNum` is advanced atomically under the pipeline mutex; `visibleSeqNum` is ratcheted atomically in order. Fixed-capacity semaphores reserve space in the commit queue and log sync queue before taking the mutex, avoiding blocking while holding it. `AllocateSeqNum` sequences non-WAL operations such as ingestion, waits for prior writes to become visible before prepare, and publishes synthetic sequence-number allocations.

## Dependencies and Integration Points
Integrates with `Batch`, memtables, `record.LogWriter` sync queue capacity, WAL rotation, ingestion sequencing, base sequence-number visibility, and DB write options. Uses `crtime` for commit stats and runtime scheduling in spin waits.

## Risks and Edge Cases
On prepare/apply errors, comments note queue semaphore slots are not released because the batch remains in the pending queue; this makes error handling performance/capacity-sensitive and prevents batch reuse by clearing `b.db`. The ring queue relies on `record.SyncConcurrency` power-of-two sizing and external semaphores to avoid full queue. `AllocateSeqNum` spin-waits for visibility and must publish even if callbacks internally fail. `noSyncWait` allows committed data to become visible before WAL fsync completes.

## Test Signals
`commit_test.go` validates queue ordering, high-concurrency commits, sync/no-sync-wait behavior, sequence-number allocation, WAL close with full sync queues, LogData/KV sequence publication ordering, and benchmark throughput.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/commit_test.go -->
# sources/storage-engines/pebble/commit_test.go

## Purpose
Tests and benchmarks Pebble's commit queue and commit pipeline concurrency, sync, sequencing, and WAL-close behavior.

## Important APIs, Types, and Functions
`testCommitEnv` supplies `commitEnv` callbacks with atomic sequence numbers, write counts, apply buffers, and optional sync-queue blocking. `TestCommitQueue`, `TestCommitPipeline`, `TestCommitPipelineSync`, `TestCommitPipelineAllocateSeqNum`, `syncDelayFile`, `TestCommitPipelineWALClose`, `TestCommitPipelineLogDataSeqNum`, and `BenchmarkCommitPipeline` cover functionality and performance.

## Control Flow
Queue tests enqueue batches, mark them applied out of order, and verify only the head drains. Pipeline tests launch thousands of goroutines committing one-key batches, then verify write/apply counts and sequence numbers. Sync tests exercise both synchronous wait and `noSyncWait` plus `Batch.SyncWait`. WAL close tests fill commit concurrency with sync-blocked WAL records, unblock sync, close the WAL, and assert no queue-full panic. The LogData test commits a KV and zero-count log data concurrently and asserts `visibleSeqNum` never makes the KV visible before apply returns.

## State and Persistence Behavior
Most tests use fake commit environments in memory. WAL-close and benchmark paths use `record.LogWriter`; `syncDelayFile` controls fsync completion. The benchmark writes to `io.Discard` while applying to an in-memory memtable and exercising real log writer sync queue behavior.

## Dependencies and Integration Points
Depends on batches, base sequence numbers, memtables, arena skiplist errors, record log writer, VFS, race/build tags, and testify/require. It tests the commit pipeline in isolation rather than through full DB writes.

## Risks and Edge Cases
High goroutine counts are reduced under race/slow builds. Fake environments may not cover all DB-level callback failures. Some tests rely on timing/jitter to exercise interleavings, especially LogData sequencing. Benchmarks allocate batches and random keys in timed loops.

## Test Signals
Signals include exact final `logSeqNum` and `visibleSeqNum`, all batches applied/written, successful async sync waits, nonzero sequence allocation behavior, clean WAL close under full sync queue pressure, and no premature KV visibility during concurrent LogData commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/commit_test.go -->
