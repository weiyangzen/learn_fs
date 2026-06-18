# Research Group: subset-b-008517

This grouped report covers Pebble batch representation, batch implementation/tests, and the `bench` workload helpers. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/batch.go -->
# sources/storage-engines/pebble/batch.go

## Purpose
`batch.go` implements Pebble's mutable write batch abstraction, including public point/range mutation APIs, optional indexing for read-your-own-writes, binary batch representation ownership, commit lifecycle state, and the `flushableBatch` adapter used when a large batch is represented as a memtable-like flushable. It is persistence-critical because the batch byte representation is the WAL payload format and must remain backward compatible for CockroachDB raft log replay.

## Important APIs, Types, And Functions
Key exported surfaces are `Batch`, `DeferredBatchOp`, `BatchCommitStats`, `BatchOption`, `WithInitialSizeBytes`, and `WithMaxRetainedSizeBytes`. `Batch` implements Pebble `Reader` and `Writer`. Mutators include `Set`, `Merge`, `Delete`, `DeleteSized`, `SingleDelete`, `DeleteRange`, `RangeKeySet`, `RangeKeyUnset`, `RangeKeyDelete`, `LogData`, plus deferred variants that return slices into `Batch.data`. Representation APIs are `Repr`, `SetRepr`, `Reader`, `SeqNum`, `Count`, `Len`, and `Empty`. Read surfaces are `Get`, `NewIter`, `NewIterWithContext`, and `NewBatchOnlyIter`, all requiring an indexed batch. Internal orchestration includes `newBatch`, `newIndexedBatch`, `Apply`, `refreshMemTableSize`, `newFlushableBatch`, `batchIter`, `flushableBatchIter`, range span fragmentation helpers, and private test hook `batchSort`.

## Control Flow
Mutation starts by lazily initializing `data` with the 12-byte batch header, appending a kind byte and varstring-encoded key/value fields, incrementing counters, and optionally adding the record offset to a `batchskl.Skiplist`. Range deletes and range keys use separate lazily allocated indexes and invalidate cached fragmented spans. `Apply` appends another batch's records after the header, updates counts and format-version requirements, then scans just the appended region when memtable sizing or indexing is needed. `SetRepr` validates the header and, when attached to a DB, rescans records to rebuild memtable size and kind counters. `Commit` delegates to `DB.Apply`; async sync paths use `commit`/`fsyncWait` and `SyncWait`.

## State And Persistence Behavior
`Batch.data` is both in-memory storage and the stable WAL representation: little-endian sequence number, little-endian count, then kind-tagged records. `Count` excludes `LogData` from memtable-modifying operations; ingest/excise batches count WAL records but restore memtable size. `minimumFormatMajorVersion` is ratcheted by newer record kinds such as sized deletes, flushable ingest, blob-file ingest, and excise. Lifecycle reuse is guarded by an atomic refcount plus `batchClosedBit` so WAL failover can retain `data` safely after commit returns. `Reset` may drop `data` when references remain, and `Close` may defer pooling until `Unref`. `grow` panics on the 4 GiB representation limit.

## Dependencies And Integration Points
The file depends on `batchrepr` for wire-format reading/writing, `batchskl` for indexed-batch skiplist storage, `base` for internal keys and sequence numbers, `keyspan`, `rangedel`, and `rangekey` for range operation fragmentation, `rawalloc` for backing buffers, DB commit pipeline state, `private.BatchSort` for tests, and Pebble comparers/split functions for prefix and range-key invariants. `flushableBatch` integrates with the memtable flush queue through the `flushable` interface.

## Risks And Edge Cases
The highest risks are corrupt batch representations, stale `minimumFormatMajorVersion` propagation, indexed-batch mutation while iterators are open, range span cache invalidation, prefix iteration with non-trivial split functions, lifecycle data races under WAL failover, and divergent behavior between `batchIter` and `flushableBatchIter` (the code explicitly requires they stay in sync). Deferred operations are footgun-prone because callers must populate returned slices and call `Finish` exactly once. Large or corrupted batches can panic or return marked corruption errors; ingest/excise records are intentionally illegal in `Batch.Apply`.

## Test Signals
`batch_test.go` exercises normal and deferred mutations, ingest records with blob IDs, format-version propagation through `Apply`, reset/reuse/lifecycle behavior, indexed and batch-only iteration, strict-prefix behavior, range key/delete fragmentation, flushable batches, commit stats, memtable size handling, overflow conditions, and batch options. Datadriven tests cover iteration and range behavior against golden files.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/batch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/batch_test.go -->
# sources/storage-engines/pebble/batch_test.go

## Purpose
`batch_test.go` is the primary behavioral regression suite for Pebble batches. It validates the binary record stream, deferred APIs, indexed-batch semantics, flushable-batch behavior, range-key/range-delete span handling, lifecycle reuse, commit statistics, and selected performance benchmarks.

## Important APIs, Types, And Functions
The file defines many `Test*` functions, with notable coverage in `TestBatch`, `TestBatchIngestSSTWithBlobs`, `TestBatchApplyPropagatesMinimumFormatMajorVersion`, `TestBatchReset`, `TestBatchReuse`, `TestIndexedBatchReset`, `TestIndexedBatchMutation`, `TestBatchIterStrictPrefix`, `TestBatchRangeOps`, `TestFlushableBatchIterStrictPrefix`, `TestFlushableBatch`, `TestBatchCommitStats`, `TestBatchLogDataMemtableSize`, `TestBatchSpanCaching`, and `TestBatchOption`. Benchmarks compare normal and indexed `Set` paths and deferred variants.

## Control Flow
Tests create in-memory DBs, raw `Batch` instances, or indexed batches, apply operations through public, deferred, and `AddInternalKey` APIs, then inspect `Reader` output, iterators, counts, memtable sizes, and internal fields. Datadriven tests parse commands such as `define`, `apply`, `iter`, `scan`, `clone`, `mutate`, and `dump`, letting golden files exercise many iterator states. Some tests deliberately manipulate internal wait groups, format versions, batch sequence numbers, lifecycle refs, and `data` capacity to hit non-public states.

## State And Persistence Behavior
The tests verify that record counts and serialized headers are consistent; that `LogData` affects WAL representation but not memtable size/count; that ingest batches remain WAL-only and may encode blob IDs; that `Reset` clears commit and range-cache state while preserving reusable configuration; and that `ApplyNoSyncWait` makes keys visible before fsync completion while `SyncWait` observes durability errors. Flushable tests confirm sequence-number assignment, sorted point offsets, and range span output for large-batch commit behavior.

## Dependencies And Integration Points
The suite uses `datadriven`, `leaktest`, `testutils`, `testkeys`, `itertest`, `batchrepr`, `batchskl`, `keyspan`, and in-memory `vfs`. It integrates with broader Pebble helpers such as `runBatchDefineCmd`, `runIterCmd`, iterator cloning, DB flush/commit paths, and Cockroach-style key comparers.

## Risks And Edge Cases
The tests target risks around empty keys/values, zero-length batches, count overflow, oversized batches, stale indexed iterators after mutation, prefix mode crossing prefix boundaries, snapshot filtering within batch sequence numbers, range span cache staleness after writes, lifecycle-close double use, and false failures from timing-sensitive commit-stat assertions. Randomized span caching logs a seed because failures may be order-dependent.

## Test Signals
This file itself is the signal source. It combines table tests, datadriven golden tests, direct internal-state assertions, benchmarks, and randomized stress. Important missing areas are mostly external: real filesystem WAL failover races and production-scale >4 GiB behavior are represented by guards or unit-level simulation rather than full end-to-end tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/batch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/reader.go -->
# sources/storage-engines/pebble/batchrepr/reader.go

## Purpose
`batchrepr/reader.go` provides low-level decoding for Pebble's stable binary batch representation. It is used by `pebble.Batch`, WAL replay, tests, and any code that must scan a serialized batch without owning higher-level batch state.

## Important APIs, Types, And Functions
Exports include `ErrInvalidBatch`, `HeaderLen`, `IsEmpty`, `ReadHeader`, `Header`, `Header.String`, `ReadSeqNum`, `Read`, `Reader`, `Reader.Next`, `DecodeStr`, and `DecodeBlobFileIDs`. `HeaderLen` is fixed at 12 bytes: 8 bytes sequence number and 4 bytes count. `Reader` is a byte-slice cursor over records after the header.

## Control Flow
`ReadHeader` validates the slice length and decodes little-endian header fields. `Read` skips the header or returns nil for empty/short inputs. `Reader.Next` reads a kind byte, rejects kinds above `InternalKeyKindMax`, decodes the user key as a varstring, and conditionally decodes a value varstring for record kinds that carry values. `DecodeStr` has a fast path for short inputs where only one-byte varints can be valid and an unsafe unrolled slow path for up to 5-byte uint32 varints. `DecodeBlobFileIDs` reads a count varint, bounds allocation by remaining bytes, and decodes each blob ID varint.

## State And Persistence Behavior
The reader is stateless except for advancing the `Reader` slice cursor. Returned key/value slices alias the input representation, so callers must preserve the backing bytes. Errors are marked corruption errors via `base.MarkCorruptionError`, preserving DB corruption semantics for bad WAL or externally supplied batch bytes.

## Dependencies And Integration Points
It depends on `encoding/binary`, `unsafe`, `internal/base`, and `github.com/pkg/errors`. `pebble.Batch.refreshMemTableSize`, `Apply`, `newFlushableBatch`, tests, and writer pretty-printing all rely on this decoder to interpret records consistently with the WAL format.

## Risks And Edge Cases
Primary risks are malformed varints, truncated records, invalid kind tags, huge blob counts causing allocation panics, and unsafe reads in the slow path. The code mitigates the unsafe path by using it only when `len(data) > 128`, which guarantees enough bytes for five-byte loads. `ReadSeqNum` deliberately does not validate length and will panic on too-short input; callers must use it only on validated or performance-sensitive paths.

## Test Signals
`reader_test.go` covers datadriven scans, empty detection, `DecodeStr` truncation and fast/slow paths, blob ID malformed inputs, huge count defense, round trips, and truncated `Reader.Next` records.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/reader_test.go -->
# sources/storage-engines/pebble/batchrepr/reader_test.go

## Purpose
This test file validates the batch representation reader and its defensive behavior on malformed binary input. It is important because reader failures surface as corruption during WAL replay or `Batch.SetRepr`.

## Important APIs, Types, And Functions
`TestReader` drives `IsEmpty`, `ReadHeader`, `Read`, and `Reader.Next` through datadriven hex input. `readRepr` converts whitespace/comment-tolerant hex fixtures into bytes. `TestDecodeStr`, `TestDecodeBlobFileIDs`, and `TestReaderNextTruncated` directly target decoder edge cases.

## Control Flow
Datadriven commands either report emptiness or scan a representation, printing header and each decoded record until EOF or error. `readRepr` strips comments and whitespace line-by-line, then hex-decodes. Direct tests enumerate malformed slices and assert `ok=false` without panics. Slow-path `DecodeStr` tests pad input above 128 bytes to force the unsafe unrolled decoder.

## State And Persistence Behavior
The file does not persist data, but it simulates persisted batch/WAL bytes. It confirms that corrupt or truncated record payloads fail cleanly with errors rather than advancing undefined state or panicking.

## Dependencies And Integration Points
Dependencies include `datadriven`, `crstrings`, `require`, `encoding/hex`, `encoding/binary`, and `internal/base`. Fixtures under `batchrepr/testdata/reader` provide regression vectors for representation formatting and error text.

## Risks And Edge Cases
Covered risks include empty input, short headers, truncated one-byte and multi-byte varints, declared lengths exceeding payload, missing values after a valid key, blob count values exceeding remaining data, and huge blob counts that previously could panic during allocation.

## Test Signals
Signals are strong for decoder robustness and output formatting. They do not prove semantic validity of every internal key kind beyond `Reader.Next`'s structural parsing; higher-level batch tests cover kind-specific behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/writer.go -->
# sources/storage-engines/pebble/batchrepr/writer.go

## Purpose
`writer.go` contains the minimal low-level mutation helpers for the batch representation header. It is intentionally small because higher-level record construction lives in `pebble.Batch`.

## Important APIs, Types, And Functions
`SetSeqNum(repr []byte, seqNum base.SeqNum)` writes the first 8 header bytes as a little-endian sequence number. `SetCount(repr []byte, count uint32)` writes bytes 8 through 11 as a little-endian count.

## Control Flow
Both functions perform direct little-endian stores into the supplied slice. There is no validation branch; slices shorter than `HeaderLen` panic by design, matching performance-sensitive internal callers that already own initialized representations.

## State And Persistence Behavior
These helpers mutate the WAL batch header in-place. `Batch.Repr` uses `SetCount` to synchronize the stored count before exposing bytes, and commit paths use sequence-number mutation to publish the assigned sequence number.

## Dependencies And Integration Points
The file depends on `encoding/binary` and `internal/base`. It shares the private `countOffset` and `HeaderLen` constants from `reader.go`.

## Risks And Edge Cases
Main risks are passing a too-short representation or accidentally mutating a representation still observed by another component. The functions do not copy or guard against races; callers must enforce ownership and length.

## Test Signals
`writer_test.go` verifies mutations through datadriven inputs and reuses the reader to inspect header values and pretty-print records.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/writer_test.go -->
# sources/storage-engines/pebble/batchrepr/writer_test.go

## Purpose
This file tests and visualizes in-place batch header writes. It also provides `prettyBinaryRepr`, a helper for readable datadriven output of raw batch bytes.

## Important APIs, Types, And Functions
`TestWriter` supports datadriven commands `init`, `read-header`, `set-count`, and `set-seqnum`. `prettyBinaryRepr` prints the header and each decodable record, falling back to an invalid-remainder line when `Reader.Next` reports corruption.

## Control Flow
The datadriven test maintains one `repr` slice across commands. It initializes from hex input with `readRepr`, mutates header fields with `SetCount` or `SetSeqNum`, then prints the resulting bytes. Pretty-printing delegates record parsing to `Read`/`Reader.Next`.

## State And Persistence Behavior
State is the mutable representation byte slice. The tests confirm header updates happen in place and do not disturb trailing record bytes. This mirrors production mutation of WAL batch headers.

## Dependencies And Integration Points
It depends on `datadriven`, `base.ParseSeqNum`, `binfmt`, and reader helpers from the same package. The helper is test-only but useful for diagnosing binary representation regressions.

## Risks And Edge Cases
The test covers short representations by printing hex instead of decoding. It also preserves invalid record bytes when pretty-printing, reducing the chance that diagnostic output hides corruption.

## Test Signals
Golden datadriven outputs verify endian layout, count offset, sequence-number formatting, and integration with reader decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/batchrepr/writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/bench.go -->
# sources/storage-engines/pebble/bench/bench.go

## Purpose
`bench.go` defines shared benchmark configuration and execution loops for Pebble command-line benchmarks. It abstracts DB-backed and non-DB benchmarks, handles duration/size/signal termination, periodic reporting, optional compaction waiting, and profiler rotation.

## Important APIs, Types, And Functions
`CommonConfig` holds knobs shared by workloads: cache size, concurrency, WAL disabling, duration, max size, verbose logging, wipe behavior, shared-storage options, ballast, auto-compaction disabling, rate limiter, and logger. `Test` and `TestWithoutDB` package workload callbacks. `RunTest`, `RunTestWithoutDB`, `startCPUProfile`, and `startRecording` are the core functions. `wait` applies optional rate limiting.

## Control Flow
`RunTest` optionally wipes the directory, opens a DB through `NewPebbleDB`, runs `Init`, starts worker goroutines through `Run`, and enters a select loop over a one-second ticker, worker completion, and interrupt/timeout signals. It prints metrics periodically, stops on `MaxSize`, and may wait for background compactions after workers finish. `RunTestWithoutDB` mirrors this for filesystem benchmarks. CPU profiling rotates every 10 seconds and finalizers write heap and mutex profiles.

## State And Persistence Behavior
This file creates, opens, and may delete benchmark directories. Profiling emits `cpu.*.prof`, `heap.prof`, and `mutex.prof` in the current directory. It does not directly mutate Pebble data beyond delegating to workload callbacks and `NewPebbleDB`.

## Dependencies And Integration Points
It depends on `pebble`, `internal/rate`, `runtime/pprof`, OS signals, and the `DB` abstraction from `db.go`. All workload files call into `RunTest` or `RunTestWithoutDB`.

## Risks And Edge Cases
Risks include unbounded long-running goroutines if a workload never exits, process-level `log.Fatal` in profile setup, profile file churn, and `MaxSize` polling lag. `signal.Notify` is not stopped, which is acceptable for benchmark processes but would be undesirable in reusable libraries.

## Test Signals
There are no direct tests in this file. Coverage is indirect through benchmark commands and workload-specific tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/db.go -->
# sources/storage-engines/pebble/bench/db.go

## Purpose
`db.go` provides a narrow database abstraction for benchmarks and a Pebble-backed implementation. It centralizes benchmark-specific Pebble options so workloads can focus on access patterns.

## Important APIs, Types, And Functions
Interfaces `DB`, `Iterator`, and `Batch` capture only benchmark needs. `pebbleDB` wraps `*pebble.DB` and optional ballast. `NewPebbleDB` opens a configured Pebble instance. Methods implement `Flush`, `NewIter`, `NewBatch`, `Scan`, `Metrics`, and `Close`.

## Control Flow
`NewPebbleDB` builds `pebble.Options` with Cockroach key schema/comparer, cache, WAL, L0, memtable, compaction, blob/value separation, block-size, and shared-storage settings, then opens the DB. Verbose mode installs a logging event listener with noisy events disabled. `Scan` seeks forward or reverse and copies keys/values into a `bytealloc.A` to simulate consumption while avoiding compiler elision.

## State And Persistence Behavior
It creates or opens an on-disk Pebble DB at the requested directory and may configure remote/shared object creation. The ballast is retained in memory, not persisted. `Scan` is read-only; workloads mutate through `Batch` and `Flush`.

## Dependencies And Integration Points
The file depends on Pebble core packages, Cockroach key encoding, sstable key schemas, `remote` object storage, `vfs`, and `bytealloc`. Every DB-backed benchmark reaches Pebble through this adapter.

## Risks And Edge Cases
`NewPebbleDB` uses `log.Fatal` on open/configuration failures, which is appropriate for CLI benchmarks but not library use. `NewIter` ignores iterator creation errors. Shared-storage creator ID is hard-coded to 1 for benchmark convenience. Value separation defaults may affect comparability with older benchmark runs.

## Test Signals
No direct tests. Behavior is exercised by all benchmark workloads and `ycsb_bench_test.go` fixture generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/fsbench.go -->
# sources/storage-engines/pebble/bench/fsbench.go

## Purpose
`fsbench.go` implements filesystem microbenchmarks for create, delete, write+sync, and disk-usage operations through Pebble's `vfs.FS` interface. It is independent of Pebble DB state and measures filesystem behavior relevant to storage-engine performance.

## Important APIs, Types, And Functions
`FsBenchConfig`, `DefaultFsBenchConfig`, `FsBenchmark`, `FsBenchmarks`, and `RunFsBench` are exported. Internal `fsEnv` owns the filesystem, write buffer, and helpers; `fsBench` owns per-run state. Benchmark constructors include `createBench`, `deleteBench`, `deleteUniformBench`, `writeSyncBench`, and `diskUsageBench`. Execution methods are `init`, `execute`, `tick`, and `done`.

## Control Flow
`FsBenchmarks` builds a named registry. `RunFsBench` selects a benchmark, repeats it `NumTimes`, constructs the run state, and delegates to `RunTestWithoutDB`. Each benchmark closure prepopulates directories/files as needed, defines a `run` function that records one latency sample per operation, and defines cleanup/stop closures. `execute` loops until `run` returns false or `MaxOps` is reached.

## State And Persistence Behavior
This file deliberately creates, writes, syncs, deletes, and recursively removes files/directories. Some benchmarks prepopulate up to hundreds of thousands of files and multi-GiB file sizes. Cleanup tries to remove benchmark directories and close open handles, but interrupted or fatal exits may leave large artifacts.

## Dependencies And Integration Points
It depends on `vfs.FS`, `histogramRegistry`, `RunTestWithoutDB`, OS path/removal functions, atomics, and standard logging. CLI code selects names returned by `FsBenchmarks`.

## Risks And Edge Cases
Risks include very large disk usage, `log.Fatal` aborts before cleanup, shared `numFiles`/file handle state only safe because each `fsBench` currently runs a single worker, and use of `os.RemoveAll` in `fsEnv.removeAll` rather than the configured `vfs.FS`. Directory handles are synced for create/delete timing but platform behavior may differ.

## Test Signals
No direct tests. Outputs are benchmark histograms and `Benchmarkfsbench/...` lines. Manual validation should use small `MaxOps` and scratch directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/fsbench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/histogram.go -->
# sources/storage-engines/pebble/bench/histogram.go

## Purpose
`histogram.go` provides concurrent latency histograms and registry-level periodic/cumulative aggregation for benchmark reporting.

## Important APIs, Types, And Functions
`newHistogram`, `namedHistogram`, `newNamedHistogram`, `Record`, `tick`, `histogramTick`, `histogramRegistry`, `newHistogramRegistry`, `Register`, and `Tick` are the core pieces. Latency range is clamped from 10 microseconds to 10 seconds.

## Control Flow
Workers call `Record`, which clamps duration and records under a mutex. Reporting calls `histogramRegistry.Tick`, snapshots the registered histograms, rotates each current histogram, merges by name, updates cumulative histograms and previous tick timestamps, then invokes the caller's formatting callback in sorted name order.

## State And Persistence Behavior
All state is in-memory. `namedHistogram` protects current interval histograms with a mutex. The registry stores cumulative histograms and previous tick times by name. Nothing is persisted except printed benchmark output produced by callers.

## Dependencies And Integration Points
It depends on `HdrHistogram`, `sync`, `sort`, and Cockroach errors. Most benchmark workloads register operation-specific histograms through this registry.

## Risks And Edge Cases
If a duration still records outside the clamped range, the code panics because that indicates an invariant violation. Empty tick intervals can produce zero counts, and callers must avoid divide-by-zero if no operations occurred. Multiple workers sharing the same histogram name are intentionally merged.

## Test Signals
No direct tests. Indirect signal comes from benchmark output and workload tests that call reporting paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/histogram.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/mvcc.go -->
# sources/storage-engines/pebble/bench/mvcc.go

## Purpose
`mvcc.go` contains CockroachDB-style MVCC scan helpers and a faux MVCC merger used by benchmarks that approximate CockroachDB storage workloads.

## Important APIs, Types, And Functions
Functions `mvccForwardScan` and `mvccReverseScan` scan a `DB` between encoded MVCC bounds. Exported `FauxMVCCMerger` names `cockroach_merge_operator` and delegates to Pebble's default merger.

## Control Flow
Each scan opens an iterator with lower/upper MVCC bounds, iterates forward or reverse, splits keys using `cockroachkvs.Split`, compares the timestamp suffix to the supplied timestamp, copies qualifying logical key/value bytes into `bytealloc.A`, and accumulates count and byte totals.

## State And Persistence Behavior
The helpers are read-only. They allocate transient byte buffers to force materialization of scanned data. The merger affects write/compaction semantics only when configured by benchmark options.

## Dependencies And Integration Points
Dependencies include `pebble`, `cockroachkvs`, and `bytealloc`. `scan.go` uses the scan helpers, and benchmark options in `db.go` and replay merger hooks share the Cockroach merger name.

## Risks And Edge Cases
The helpers count every internal MVCC version visited, not only versions copied after timestamp filtering. Iterator errors are not returned by these helpers, so callers only get count/bytes. The faux merger is not a full Cockroach merge implementation and should be interpreted as benchmark approximation only.

## Test Signals
No direct tests. Indirect validation occurs through scan benchmark sanity checks that expected row counts match.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/mvcc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/queue.go -->
# sources/storage-engines/pebble/bench/queue.go

## Purpose
`queue.go` builds a fixed-size queue workload used by the tombstone benchmark to continually delete old keys and insert new keys, creating point tombstone pressure.

## Important APIs, Types, And Functions
`QueueConfig`, `DefaultQueueConfig`, and `newQueueTest` are the main surfaces. `newQueueTest` returns a `Test` plus an atomic operation counter consumed by `RunTombstone`.

## Control Flow
Initialization fills `cfg.Size` MVCC-encoded queue keys, commits each with `NoSync`, and flushes. The run loop is a single goroutine that repeatedly deletes the current slot with `Sync`, waits on the optional limiter, inserts a new tail key/value with `Sync`, waits again, and increments the operation counter. Tick/done callbacks print instantaneous and cumulative queue ops/sec.

## State And Persistence Behavior
The workload persists an evolving queue keyspace in Pebble. Each cycle creates a point tombstone and a new key, and synchronous commits stress WAL/fsync behavior unless the surrounding config disables WAL elsewhere.

## Dependencies And Integration Points
It depends on `pebble`, `cockroachkvs`, `randvar`, atomics, and `RunTest` callback conventions. `tombstone.go` composes it with YCSB.

## Risks And Edge Cases
The queue slice and RNG are captured by a single worker; adding concurrency would require synchronization. The worker has no internal stop condition, relying on `RunTest` process-level duration/signal completion. Fatal errors abort the process.

## Test Signals
No direct tests. Runtime output and tombstone benchmark behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/replay.go -->
# sources/storage-engines/pebble/bench/replay.go

## Purpose
`replay.go` implements benchmark replay of recorded Pebble workloads. It initializes run directories from checkpoints, parses option overrides, configures pacing, runs `replay.Runner`, emits benchmark metrics/plots, and can exec itself for repeated independent runs.

## Important APIs, Types, And Functions
`ReplayConfig` and `DefaultReplayConfig` configure the benchmark. Methods include `args`, `RunReplay`, `runOnce`, `initRunDir`, `initOptions`, `getCheckpointDir`, `parseHooks`, `ParseCustomOptions`, and `cleanUp`. Helper factories `makeComparer`, `makeMerger`, `PacerFlag.Set`, and `overwriteValueMerger` translate serialized option names.

## Control Flow
`RunReplay` validates checkpoint flags, runs once, decrements count, and uses `syscall.Exec` for additional runs. `runOnce` constructs a `replay.Runner`, initializes a temp or configured run directory, clones checkpoint files unless ignored, parses options from checkpoint and CLI string, starts and waits for the workload, closes resources, then prints benchmark strings and plots. `ParseCustomOptions` converts whitespace-delimited CLI text into newline-delimited Pebble options while preserving section headers.

## State And Persistence Behavior
The code clones checkpoint directories into run directories, may create temporary replay directories under the current working directory, and registers cleanup functions for temp runs. It reads options files from workload checkpoints and mutates `pebble.Options` before opening/running replay. Repeated runs replace the process image.

## Dependencies And Integration Points
It depends on `pebble/replay`, `vfs.Clone`, Pebble option parsing hooks, Cockroach comparer/merger names, table filter policies, OS exec/syscall, and benchmark CLI flag plumbing. `replay_test.go` covers custom option parsing.

## Risks And Edge Cases
Risks include incomplete cleanup for configured `RunDir`, process replacement via `syscall.Exec`, option-string parsing bugs around brackets/whitespace, hard-coded supported comparer/merger names, and failure when checkpoint lacks an OPTIONS file. `MaxCacheSize` silently caps parsed cache size.

## Test Signals
`replay_test.go` validates `ParseCustomOptions` for compaction settings, cache caps, and level-specific options. Full replay execution is not unit-tested here.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/replay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/replay_test.go -->
# sources/storage-engines/pebble/bench/replay_test.go

## Purpose
`replay_test.go` regression-tests CLI option string parsing for replay benchmarks. This matters because replay accepts compact command-line option overrides rather than normal Pebble options files.

## Important APIs, Types, And Functions
`TestParseOptionsStr` constructs `ReplayConfig` cases and compares parsed `pebble.Options.String()` output against expected options after defaults. It specifically exercises `ReplayConfig.ParseCustomOptions`.

## Control Flow
Each case allocates fresh options, parses `OptionsString`, pins `IteratorStack` to avoid invariants-build randomization, calls `EnsureDefaults`, and compares serialized options strings. Cache objects are unreferenced when allocated.

## State And Persistence Behavior
The test is in-memory only. It validates that command-line text mutates `pebble.Options` as intended, including capping cache size through `MaxCacheSize`.

## Dependencies And Integration Points
It depends on `pebble`, `manifest.NumLevels`, `require`, and option parsing hooks reachable through `ReplayConfig`.

## Risks And Edge Cases
Covered edge cases include multiple spaces, adjacent section headers, level-specific fields, old/new compaction concurrency fields, and cache-size caps. It does not test malformed strings or replay checkpoint initialization.

## Test Signals
The primary signal is exact options-string equality after defaults, which catches parsing drift in both replay code and Pebble option formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/replay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/scan.go -->
# sources/storage-engines/pebble/bench/scan.go

## Purpose
`scan.go` implements a DB-backed scan benchmark over Cockroach-style MVCC keys, measuring row throughput, byte throughput, and per-row latency for forward or reverse scans.

## Important APIs, Types, And Functions
`ScanConfig`, `DefaultScanConfig`, and `RunScan` are the exposed surfaces. Config controls reverse scanning, row-count distribution, and value-size distribution.

## Control Flow
`RunScan` preloads 100,000 MVCC keys in batches of 1,000, commits and flushes them, then starts `common.Concurrency` workers. Each worker picks a random start index and row count, encodes start/end keys, calls `mvccForwardScan` or `mvccReverseScan`, validates the scanned count, and atomically accumulates bytes and rows. Tick/done callbacks print instantaneous and cumulative rates.

## State And Persistence Behavior
Initialization writes and flushes a fixed keyspace. The run phase is read-only and repeatedly opens iterators through MVCC scan helpers. WAL sync mode for preload follows `DisableWAL`.

## Dependencies And Integration Points
It uses `RunTest`, the `DB` abstraction, `cockroachkvs`, `randvar`, `mvcc.go` scan helpers, and atomic counters.

## Risks And Edge Cases
The benchmark assumes row distributions never exceed the fixed key count; invalid distributions can panic or fatal on mismatched counts. Workers run indefinitely until the outer harness stops. The use of deterministic RNG seeds by worker index improves reproducibility but can create correlated patterns if concurrency changes.

## Test Signals
No direct tests. Runtime fatal count checks and benchmark output are the main validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/scan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/sync.go -->
# sources/storage-engines/pebble/bench/sync.go

## Purpose
`sync.go` implements a write/fsync latency benchmark. It can either write real key/value records or WAL-only `LogData` records, measuring operation latency and MB/sec.

## Important APIs, Types, And Functions
`SyncConfig`, `DefaultSyncConfig`, and `RunSync` are the public surfaces. Config controls batch-size distribution, WAL-only mode, and value-size distribution.

## Control Flow
`RunSync` creates a histogram registry and byte counter, selects `pebble.Sync` or `NoSync`, and runs workers through `RunTest`. Each worker repeatedly waits on the limiter, creates a batch, generates `count` values, appends either `LogData` or MVCC-encoded `Set` records, commits, records latency, and adds byte totals. Tick/done callbacks report op rate, MB/sec, and latency percentiles.

## State And Persistence Behavior
In normal mode it writes random MVCC keys to Pebble. In WAL-only mode it persists only WAL records that do not enter memtables or sstables. Sync mode stresses durable WAL fsync unless disabled by config.

## Dependencies And Integration Points
It uses `pebble`, `cockroachkvs`, `randvar`, `histogramRegistry`, `RunTest`, and rate limiting from `CommonConfig`.

## Risks And Edge Cases
The workload is unbounded until harness termination. Random keys may overwrite occasionally but are intended as broad write load. `DisableWAL` changes benchmark semantics significantly. Fatal errors stop the process.

## Test Signals
No direct tests. Output histograms and Pebble metrics are used for manual/benchmark validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/sync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/tombstone.go -->
# sources/storage-engines/pebble/bench/tombstone.go

## Purpose
`tombstone.go` composes a YCSB workload with the queue workload to measure behavior under sustained point-tombstone generation and mixed read/write pressure.

## Important APIs, Types, And Functions
`TombstoneConfig`, `DefaultTombstoneConfig`, and `RunTombstone` are the main APIs. The config nests `YCSBConfig` and `QueueConfig`.

## Control Flow
`RunTombstone` validates incompatible wipe/prepopulated-key settings, parses YCSB workload and key distribution, creates a `ycsb` runner and queue `Test`, then uses `RunTest` with combined init/run callbacks. Ticks gather queue operation deltas, YCSB histogram deltas, estimate disk usage for the queue key range, and print both queue and YCSB throughput.

## State And Persistence Behavior
The benchmark persists both YCSB data and queue keys in one Pebble DB. Queue operations continuously add tombstones and new keys; YCSB adds read/write/scan pressure. `EstimateDiskUsage` observes the queue key range's storage footprint.

## Dependencies And Integration Points
It depends on `ycsb.go`, `queue.go`, `pebbleDB` internals, `humanize`, and `RunTest`. It type-asserts the benchmark DB to `pebbleDB` to access `EstimateDiskUsage`.

## Risks And Edge Cases
The type assertion means alternate `DB` implementations cannot run this benchmark unchanged. The queue and YCSB workers run indefinitely until the harness stops. `EstimateDiskUsage` errors are fatal. Wipe/prepopulation validation prevents a nonsensical destructive configuration.

## Test Signals
No direct tests. Runtime output shows queue size and throughput trends.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/tombstone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/util.go -->
# sources/storage-engines/pebble/bench/util.go

## Purpose
`util.go` contains simple big-endian integer encoding helpers used to build lexicographically sortable benchmark keys.

## Important APIs, Types, And Functions
`encodeUint32Ascending` appends a uint32 in big-endian byte order. `encodeUint64Ascending` appends a uint64 in big-endian byte order.

## Control Flow
Both functions append bytes from most significant to least significant, preserving numeric ordering under bytewise comparison.

## State And Persistence Behavior
The helpers are stateless. Their output becomes part of persisted benchmark keys in queue and scan workloads.

## Dependencies And Integration Points
No external imports. Used by `queue.go`, `scan.go`, and MVCC key construction paths.

## Risks And Edge Cases
Callers must manage buffer reuse carefully because the functions append to the supplied slice. The functions intentionally do not allocate a fixed-size destination or validate capacity.

## Test Signals
No direct tests. Correctness is indirectly required by queue ordering and scan range behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/write_bench.go -->
# sources/storage-engines/pebble/bench/write_bench.go

## Purpose
`write_bench.go` implements an adaptive write-throughput benchmark that searches for sustainable insert rates based on L0 file/sublevel thresholds, stalls, and actual-vs-desired rate dips.

## Important APIs, Types, And Functions
`WriteBenchConfig`, `DefaultWriteBenchConfig`, `writeBenchResult`, `RunWriteBench`, `pauseWriter`, and `newPauseWriter` are central. Defaults mirror Cockroach admission-control L0 limits.

## Control Flow
`RunWriteBench` builds a YCSB insert-only workload, starts `pauseWriter` goroutines under rate limiters, and on each tick reads Pebble metrics. Passing a test period increases desired rate exponentially by streak; failure records the rate, backs off to the previous stack entry, pauses writers for a cooloff period, then resumes. Failure is triggered by zero actual rate while not cooling off, L0 file/sublevel limits, or sustained rate dip above the configured fraction.

## State And Persistence Behavior
The benchmark writes real Pebble data through YCSB insert operations. Internal state tracks desired rate, pass/fail history, current cooloff, writer goroutines, and accumulated operation histograms. It does not clean DB state between rate attempts within one run.

## Dependencies And Integration Points
It depends on `ycsb.go`, `ackseq`, `randvar`, `rate`, `RunTest`, and Pebble metrics. It composes with `CommonConfig` but uses its own `Concurrency` field for writer count.

## Risks And Edge Cases
The pause protocol uses unbuffered channels and assumes callers pause/unpause each writer coherently; misuse can block. Search logic can terminate when no backtrack room remains. Metrics thresholds are workload- and option-sensitive, so pass/fail is not portable across hardware. `rateAcc` approximates actual throughput by summing tick rates and may be noisy.

## Test Signals
No direct tests. Benchmark output lines include raw result records and periodic L0/write-amp metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/write_bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/ycsb.go -->
# sources/storage-engines/pebble/bench/ycsb.go

## Purpose
`ycsb.go` implements configurable YCSB-like workloads over Pebble, including load, insert, read, scan, reverse-scan, and update operations with Cockroach-style MVCC keys.

## Important APIs, Types, And Functions
Exports are `YCSBConfig`, `DefaultYCSBConfig`, and `RunYCSB`. Internal components include operation constants, `ycsbWeights`, `ycsbParseWorkload`, `ycsbParseKeyDist`, `ycsbBuf`, `ycsb`, `newYcsb`, `init`, `run`, `worker`, `sampleReadAmp`, key/value helpers, operation methods, `tick`, and `done`.

## Control Flow
`RunYCSB` validates wipe/prepopulation, parses workload weights and key distribution, constructs a `ycsb`, and delegates to `RunTest`. `init` bulk-loads initial keys in roughly 1 MiB batches, flushes, then waits for compactions to stabilize. `run` initializes key sequencing, optional read-amp sampling, and workers. Each worker picks operations from weighted distribution, executes the corresponding method, records latency, and exits only when `NumOps` is reached. Inserts coordinate new key visibility with `ackseq` before expanding the key distribution maximum.

## State And Persistence Behavior
The workload writes persistent MVCC-encoded keys with walltime suffixes. `InitialKeys` loads base data; `PrepopulatedKeys` shifts key numbering for fixture reuse. Write options are sync unless WAL is disabled. Read amplification is sampled from iterator metrics or DB metrics. Histograms and counters are in-memory; final output reports read bytes, write bytes including blob activity, read amp, and write amp.

## Dependencies And Integration Points
It depends on Pebble interfaces from `db.go`, `ackseq`, `randvar`, `rate`, histograms, and `RunTest`. `write_bench.go`, `tombstone.go`, and `ycsb_bench_test.go` reuse `newYcsb` and parsing helpers.

## Risks And Edge Cases
Workload parsing rejects zero weights but ignores unknown operation names by leaving weights at zero, which can surprise malformed strings with at least one valid weight. `latest` distribution uses a default skewed-latest generator independent of total keys. Workers are long-running, and fatal DB errors terminate the process. `NumOps` is checked after each operation, so concurrent workers may overshoot slightly.

## Test Signals
Direct tests are in `ycsb_bench_test.go` as an in-process benchmark harness, not unit assertions. Parsing helpers are indirectly tested by workloads using custom configs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/ycsb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/bench/ycsb_bench_test.go -->
# sources/storage-engines/pebble/bench/ycsb_bench_test.go

## Purpose
`ycsb_bench_test.go` provides an in-process Go benchmark mirroring a Pebble YCSB roachtest. It builds/reuses large fixtures and runs workloads A-F with profiler-friendly local execution.

## Important APIs, Types, And Functions
`BenchmarkYCSB`, `ycsbBenchSizes`, flags `ycsb-bench-fixture-dir` and `ycsb-bench-initial-keys`, `defaultYCSBFixtureDir`, `ensureYCSBFixture`, and `runYCSBWorkload` are the major pieces.

## Control Flow
`BenchmarkYCSB` iterates value sizes 64 and 1024, derives a fixture path by value size, key count, and format version, ensures the fixture exists, then runs workloads A-F. `ensureYCSBFixture` checks a `.ready` marker, removes incomplete fixture state, creates parent directories, loads initial keys through `newYcsb.init`, closes the DB, and writes the marker. `runYCSBWorkload` checkpoints the fixture into `b.TempDir`, opens the checkpoint, configures workload/key distribution/operation cap, starts workers, and waits for them to finish under benchmark timing.

## State And Persistence Behavior
The benchmark may create a multi-gigabyte fixture cache under the user's cache directory by default. The `.ready` marker is the persistence guard against reusing partial fixtures. Each workload uses a hard-linked Pebble checkpoint in a temporary directory to avoid mutating the cached fixture.

## Dependencies And Integration Points
It uses `testing.B`, Pebble checkpointing through `pebbleDB`, `base.NoopLoggerAndTracer`, `randvar`, YCSB helpers, and filesystem flags. It relies on `NewPebbleDB` settings matching the benchmark suite.

## Risks And Edge Cases
The default 10 million key fixture is expensive in disk and time. Hard-link checkpoint behavior depends on filesystem support through Pebble. If a process dies after fixture load but before marker creation, the next run rebuilds. Workload workers may overshoot `b.N` slightly because the stop condition is atomic and checked after operations.

## Test Signals
This is a benchmark, not a normal unit test. Signal is benchmark throughput by workload/value size and the ability to reuse fixtures reproducibly.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/bench/ycsb_bench_test.go -->
