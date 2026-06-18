# subset-b-008700 research

Grouped research for RocksDB trace replay, trace analysis, write-stress, verification, and release-history helper files. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer_test.cc -->
# sources/storage-engines/rocksdb/tools/trace_analyzer_test.cc

## Purpose

This gflags-gated test suite verifies the RocksDB trace analyzer tool against a generated DB operation trace. It covers per-operation analyzer modes for `Get`, `Put`, `Delete`, `SingleDelete`, `DeleteRange`, `Merge`, iterator seek variants, and `MultiGet`, and it also verifies trace write error propagation when the underlying trace writer has previously failed.

## Important APIs, Control Flow, And Dependencies

The fixture opens a temporary DB, enables `DB::StartTrace`, executes one write batch containing put/merge/delete/single-delete/range-delete operations, performs several `MultiGet` overloads, a `Get`, iterator `Seek` and `SeekForPrev`, then calls `EndTrace`. It writes a whole-key-space file named `0.txt` used by analyzer whole-space reports. `RunTraceAnalyzer` constructs an argv buffer and invokes `trace_analyzer_tool` directly. `AnalyzeTrace` applies common flags such as `-convert_to_human_readable_trace`, `-output_key_stats`, `-output_prefix_cut=1`, `-output_time_series`, `-output_value_distribution`, `-output_qps_stats`, `-no_key`, and `-no_print`.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state includes the temporary RocksDB directory, a binary trace file, analyzer output directories, and whole-key-space input. Output verification uses `LineFileReader` and checks exact or first-character matches for generated text files. Test coverage validates the analyzer's file naming contract and expected records for key stats, access-count distributions, prefix cuts, time series, whole-key reports, value-size distribution, and human-readable trace operation sequence. QPS assertions are mostly commented out because the file notes rare timing-related fragility. The `ExistsPreviousTraceWriteError` case uses `FaultInjectionTestEnv` to inject a filesystem write error and verifies that later trace writes do not crash and that `EndTrace()` returns an `Incomplete` status mentioning the prior injected error. Risks are reliance on gflags, filesystem timing, hard-coded expected output ordering, and partial QPS coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer_tool.cc -->
# sources/storage-engines/rocksdb/tools/trace_analyzer_tool.cc

## Purpose

Implements the `trace_analyzer` command-line tool. It reads RocksDB operation trace files, decodes them into `TraceRecord` objects, dispatches them through a `TraceAnalyzer`, and produces optional text outputs for readable traces, per-operation key statistics, access distributions, key/value size distributions, QPS, prefix cuts, whole-key-space comparisons, and operation correlations.

## Important APIs, Control Flow, And Dependencies

The file is compiled only when `GFLAGS` is available. Command-line flags control trace path, output directory/prefix, selected operation families, sampling ratio, prefix length, whole-key-space directory, corruption tolerance, output suppression, top-k reporting, and individual output files. `AnalyzerOptions::SparseCorrelationInput` parses compact inputs like `[get,put]` into a sparse correlation map. `TraceAnalyzer::PrepareProcessing` opens the `TraceReader` and any global output files. `StartProcessing` reads the trace header, parses trace and DB versions through `TracerHelper`, then reads records until `kTraceEnd` or EOF; supported records are accepted by the analyzer's `TraceRecord::Handler` methods. Write records are expanded by constructing a `WriteBatch` and iterating it through the analyzer's `WriteBatch::Handler` callbacks.

## State, Persistence, Integration, Risks, And Test Signals

The analyzer keeps state in `ta_` as operation-indexed `TypeUnit` objects with per-CF `TraceStats`, plus global counters, CF maps, QPS vectors, sampling counters, and output file handles. `KeyStatsInsertion` is the central mutation path: it updates per-key access counts, success counts, last timestamps, size sums, prefix-QPS maps, unique-key timeline, CF QPS, and optional time-series queues. `MakeStatistics` derives distributions and medians; `ReProcessing` drains time-series queues, reads optional whole-key-space files, and computes top-k keys; `EndProcessing` prints statistics unless `-no_print` is set and closes output files. Dependencies include RocksDB DB/write batch APIs, `TraceReader`, `TracerHelper`, `LineFileReader`, `WritableFile`, LDB hex conversion helpers, gflags, and standard math/formatting routines. Risks include many global flags, exit-on-output-open failure, memory growth proportional to unique keys, use of `log2` on bitmasks, weak validation of malformed payloads inherited from trace decoding, non-robust QPS timing, and a `PutEntityCF` path mapped to `kPutEntity` even though the operation enum count and `ta_` sizing do not allocate a separate enabled slot for that value. Test signals come from `trace_analyzer_test.cc`, which verifies generated files for each supported operation and trace write error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer_tool.h -->
# sources/storage-engines/rocksdb/tools/trace_analyzer_tool.h

## Purpose

Declares the trace analyzer's public tool entry point, option and statistics structures, and the `TraceAnalyzer` class that bridges decoded trace records to per-operation statistics.

## Important APIs, Control Flow, And Dependencies

`TraceOperationType` assigns analyzer IDs to get, write-batch suboperations, iterator seek variants, multiget, and put-entity. `TraceUnit`, `TypeCorrelation`, and `StatsUnit` model individual accesses, correlation counters, and per-key aggregates. `TraceStats` owns per-CF aggregate counters, histograms, priority queues for top-k results, time-series queues, correlation output, whole/accessed-key maps, and many optional `WritableFile` handles. `TypeUnit` groups stats by operation type, while `CfUnit` stores CF-level whole/accessed key counts and QPS maps. `TraceAnalyzer` privately implements both `TraceRecord::Handler` and `WriteBatch::Handler`, exposing the high-level lifecycle `PrepareProcessing`, `StartProcessing`, `MakeStatistics`, `ReProcessing`, and `EndProcessing`.

## State, Persistence, Integration, Risks, And Test Signals

The header shows that analyzer state is mostly in-memory until explicitly flushed through `WritableFile` handles. It depends on RocksDB `Env`, `TraceReader`, `TraceRecord`, `WriteBatch`, and `trace_replay` declarations. Important integration points are the handler overrides for decoded trace records, write-batch callbacks for each write operation, and `trace_analyzer_tool(int argc, char** argv)`. Copying is disabled for the large stats structures to avoid accidental file-handle and queue duplication, while moves are allowed. Risks include enum/index drift because arrays are sized by `kTaTypeNum`, large maps for high-cardinality traces, and many output-file pointers that must be opened and closed consistently. Tests in `trace_analyzer_test.cc` exercise the lifecycle and file outputs rather than the header directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/verify_random_db.sh -->
# sources/storage-engines/rocksdb/tools/verify_random_db.sh

## Purpose

Shell helper that compares two RocksDB directories by dumping each with `./ldb scan` and diffing the resulting text dumps. It is intended to verify that a DB generated by random DB tooling can be reopened and read with the same data as a base DB.

## Important APIs, Control Flow, And Dependencies

The script expects `db_directory`, `compare_base_db_directory`, and optional dump file name, `try_load_options`, and `ignore_unknown_options` flags. It builds `--try_load_options=true|false` and optional `--ignore_unknown_options`, then runs `./ldb scan --db=...` for each DB and finally `diff`s the dump files. `set -e` makes scan or diff failures abort the script.

## State, Persistence, Integration, Risks, And Test Signals

The script writes dump files inside both DB directories, so it mutates test directories even though it is a verification helper. It integrates with the RocksDB `ldb` binary in the current working directory. Risks include unquoted shell variables, a stale `scriptpath` variable that is never used, dependence on local `./ldb`, and dump file collisions if reused. The primary test signal is a zero exit from `diff`; any data mismatch or scan failure returns nonzero.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/verify_random_db.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/write_external_sst.sh -->
# sources/storage-engines/rocksdb/tools/write_external_sst.sh

## Purpose

Shell helper that converts sorted input data files into external SST files using RocksDB's `ldb write_extern_sst` command.

## Important APIs, Control Flow, And Dependencies

The script requires an input data directory, DB path, and external SST output directory. It removes the DB directory, ensures the external SST directory exists, then iterates over files matching `sorted_data*` under the input directory. Each file is piped into `./ldb --db=<db> --create_if_missing write_extern_sst <sst_path>`, with output files named `extern_sst0`, `extern_sst1`, and so on.

## State, Persistence, Integration, Risks, And Test Signals

State changes are destructive for the target DB path because `rm -rf $db_dir` runs before writing. The generated SST files persist under the supplied external SST directory. Integration is through local `./ldb` and the input format expected by `write_extern_sst`. Risks include unquoted paths, unsorted `find` order, no cleanup of old external SST files, and destructive DB removal if arguments are wrong. Success is signaled by zero exit under `set -e`; any failed `ldb` invocation aborts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/write_external_sst.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/write_stress.cc -->
# sources/storage-engines/rocksdb/tools/write_stress.cc

## Purpose

Implements a focused RocksDB stress binary for compaction, flush, obsolete-file deletion, iterator file retention, WAL sync, and table-cache reopen behavior. It is designed to be repeatedly run and killed by `write_stress_runner.py`.

## Important APIs, Control Flow, And Dependencies

With `GFLAGS` unavailable the binary exits with an installation message. With gflags, flags configure key/value sizes, DB path, DB destruction, runtime, RNG seed, prefix mutation periods/probabilities, iterator hold time, sync probability, full-scan obsolete-file deletion, and low-open-files mode. `WriteStress` opens a DB with small write buffers, small target files, many flush/compaction threads, optional `max_open_files=20`, and optional immediate obsolete-file deletion. `Run` starts three threads: `WriteThread` repeatedly writes random keys under a mutable 3-byte prefix; `PrefixMutatorThread` periodically mutates prefix characters at different rates; `IteratorHoldThread` holds an iterator for several seconds before scanning it.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state is the stress DB, which may survive across runs when `--destroy_db=false`. The key prefix and stop flag are atomic state shared by threads. At clean shutdown, the tool pauses background work, gathers live SST file numbers from metadata, lists DB directory children, and aborts if it finds a table file not present in live metadata, then resumes background work. Dependencies include RocksDB DB/options/env/iterator APIs, `ParseFileName`, `SystemClock`, `port::Thread`, random generators, and gflags. Risks include intentionally harsh concurrency, infinite runtime when `--runtime_sec=-1`, abort-on-error semantics, deprecated option names in newer RocksDB versions, and no leak check when the runner kills the process. Test signals are process exit status and absence of orphaned table files after clean runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/write_stress.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/write_stress_runner.py -->
# sources/storage-engines/rocksdb/tools/write_stress_runner.py

## Purpose

Python harness that repeatedly runs `./write_stress` for randomized intervals and modes, sometimes killing it violently, to exercise recovery and file cleanup across restarts.

## Important APIs, Control Flow, And Dependencies

`generate_runtimes` decomposes the requested total runtime into random short durations plus occasional 100/1000 second choices, capped by remaining time. `main` builds a shell command for each duration, randomly chooses kill mode versus clean shutdown, carries the DB across all but the first run with `--destroy_db=false`, and randomly toggles `--delete_obsolete_files_with_fullscan=true` and `--low_open_files_mode=true`. It uses `subprocess.Popen([cmd], shell=True)`, polls once per second, exits on unexpected nonzero child exit, kills in kill mode, then sleeps three seconds before the next run.

## State, Persistence, Integration, Risks, And Test Signals

The runner's state is the runtime schedule, first-run flag, child process, optional DB path, and Python RNG seeded from current time. It depends on a `write_stress` binary in the current directory. Risks include shell-string command construction, nondeterminism, no timeout guard around clean runs beyond the child runtime flag, and no explicit wait after `child.kill()`. The main signal is runner exit code: nonzero child exits are treated as failure, while killed processes in kill mode are expected and not considered errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/write_stress_runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.cc -->
# sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.cc

## Purpose

Implements block cache trace helper logic, binary block cache trace writer/reader, CSV-like human-readable block cache trace writer/reader, and the thread-safe `BlockCacheTracer` controller used by RocksDB table/cache code.

## Important APIs, Control Flow, And Dependencies

`ShouldTrace` spatially downsamples by hashing the block key modulo `sampling_frequency`, preserving full history for sampled blocks. `BlockCacheTraceHelper` classifies user/get/multiget accesses, computes row keys, extracts table IDs and sequence numbers from referenced internal keys, and decodes the last varint64 in a block key as file offset. `BlockCacheTraceWriterImpl::WriteBlockAccess` encodes a `Trace` payload containing block key, size, CF id/name, level, SST number, caller, cache-hit flags, and conditional get/data-block fields before calling `TracerHelper::EncodeTrace`. The reader performs the inverse with detailed `Incomplete` errors. Human-readable writer/reader serialize and reconstruct 21 comma-separated fields for offline analysis.

## State, Persistence, Integration, Risks, And Test Signals

`BlockCacheTracer` owns an atomic raw writer pointer protected by `InstrumentedMutex`; `StartTrace` stores options, resets get-id counter to 1, takes ownership of the writer, and writes the header; `EndTrace` deletes the writer; `WriteBlockAccess` double-checks writer presence around sampling and locking; `NextGetId` returns reserved ID 0 when tracing is off and skips 0 on wrap. Dependencies include RocksDB trace reader/writer APIs, `TraceType`, `TableReaderCaller`, `BlockCacheTraceRecord`, `SystemClock`, coding helpers, internal-key helpers, and hash utilities. Risks include raw pointer ownership, CSV parsing that cannot handle commas in CF names, unchecked trailing bytes after access decode, max-file-size checks allowing one record beyond the limit, and reliance on internal key/block key layouts. Test signals in `block_cache_tracer_test.cc` cover headers, start/stop behavior, get-id behavior, mixed block type field gating, and human-readable round-trip reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.h -->
# sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.h

## Purpose

Declares the block cache tracing API used to capture, write, read, classify, and optionally render RocksDB block cache accesses.

## Important APIs, Control Flow, And Dependencies

The header defines time constants, `BlockCacheTraceHelper`, `BlockCacheLookupContext`, `BlockCacheTraceHeader`, `BlockCacheTraceWriterImpl`, `BlockCacheHumanReadableTraceWriter`, `BlockCacheTraceReader`, `BlockCacheHumanReadableTraceReader`, and `BlockCacheTracer`. `BlockCacheLookupContext` carries table-reader caller, cache hit/insert flags, block metadata, get ID, referenced key, and snapshot state from table reader call sites to the tracer. `BlockCacheTracer` exposes `StartTrace`, `EndTrace`, `is_tracing_enabled`, `WriteBlockAccess`, and `NextGetId`.

## State, Persistence, Integration, Risks, And Test Signals

The declared persistent outputs are binary trace records through a user-provided `TraceWriter` and optional human-readable files through `WritableFile`. Integration points are table-reader call sites such as filter/dictionary/data/index/range-deletion block reads and user `Get`, `MultiGet`, iterator, compaction, prefetch, and checksum callers. The tracer uses an atomic writer pointer plus mutex for cross-thread control. Risks include lifetime ownership of writer objects, callers needing to fill lookup context consistently, and helper assumptions about referenced key and block key encodings. Tests cover the public behavior through generated trace files and decoded records.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/block_cache_tracer_test.cc -->
# sources/storage-engines/rocksdb/trace_replay/block_cache_tracer_test.cc

## Purpose

Unit tests for binary and human-readable block cache tracing. They verify that the tracer writes headers and access records correctly, handles start/stop state, gates optional fields by caller/block type, and generates get IDs only while tracing is enabled.

## Important APIs, Control Flow, And Dependencies

The fixture creates a per-thread test directory, file trace writer/reader, and helper methods to generate records, choose rotating `TableReaderCaller` values, write blocks of a given `TraceType`, and verify decoded fields. Test cases cover writes before `StartTrace`, normal atomic write, consecutive start rejection, no writes after `EndTrace`, `NextGetId`, mixed block types, and human-readable trace round trip.

## State, Persistence, Integration, Risks, And Test Signals

Each test persists a trace file under the temporary directory and deletes it in the fixture destructor. `VerifyAccess` asserts mandatory fields and asserts that get-only fields appear only for `kUserGet`/`kUserMultiGet`, while data-block reference fields appear only for get/multiget data-block accesses. The human-readable test constructs encoded referenced and block keys to validate table ID, sequence number, and block offset helper extraction. Risks include fixture cleanup failing if a test aborts before file creation, and human-readable test expectations tied to internal key encodings. Passing tests signal compatibility between writer and reader formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/block_cache_tracer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/io_tracer.cc -->
# sources/storage-engines/rocksdb/trace_replay/io_tracer.cc

## Purpose

Implements RocksDB IO operation tracing: a binary writer/reader for file-system operation records and an `IOTracer` controller that starts, stops, and writes IO trace records.

## Important APIs, Control Flow, And Dependencies

`IOTraceWriter::WriteIOOp` enforces max trace file size, writes core fields (`io_op_data`, operation name, latency, status, file name), then serializes optional fields according to the set bits in `io_op_data`: file size, length, and offset. It also serializes `IODebugContext` trace data, currently request ID. `WriteHeader` emits a `kTraceBegin` header with magic and RocksDB version. `IOTraceReader` decodes the same format and returns `Incomplete` statuses for missing fields. `IOTracer::StartIOTrace` installs a new `IOTraceWriter`, sets `tracing_enabled`, and writes a header; `EndIOTrace` deletes it; `WriteIOOp` double-checks writer presence under a mutex and ignores writer errors with `PermitUncheckedError`.

## State, Persistence, Integration, Risks, And Test Signals

The controller stores trace options, an atomic raw writer pointer, mutex, and a non-atomic `tracing_enabled` fast path deliberately annotated for TSAN suppression in the header. Dependencies include RocksDB `TraceWriter`/`TraceReader`, `TraceOptions`, `IODebugContext`, `IOStatus`, `SystemClock`, coding helpers, and trace replay encoding. Risks include raw pointer ownership, ignored write errors at the tracer wrapper layer, use of `log2` to find bit positions, asserts rather than graceful errors for unknown future bits, and no trailing-payload validation. Tests in `io_tracer_test.cc` cover optional-field combinations, request ID, start/stop behavior, and multiple records.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/io_tracer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/io_tracer.h -->
# sources/storage-engines/rocksdb/trace_replay/io_tracer.h

## Purpose

Declares IO tracing types for capturing file-system operations in RocksDB trace files.

## Important APIs, Control Flow, And Dependencies

`IOTraceOp` defines bit positions for optional record fields: file size, length, and offset. `IOTraceRecord` contains required operation fields, optional data fields, and debug context fields, with constructors for general/file-size and length/offset records. `IOTraceHeader`, `IOTraceWriter`, `IOTraceReader`, and `IOTracer` declare the writer, reader, and lifecycle controller APIs.

## State, Persistence, Integration, Risks, And Test Signals

Trace records persist through a user-provided `TraceWriter` in the same `Trace` envelope used by other trace replay code. The file-system integration is through `IODebugContext` and RocksDB file-system wrappers that decide which `io_op_data` bits are present. `IOTracer` maintains both an atomic writer pointer and a `tracing_enabled` boolean used as a cheaper check by file-system classes, with comments explaining race tolerance. Risks include bit-position compatibility when adding new optional fields, request-id pointer lifetime in `IODebugContext`, and callers needing to match `io_op_data` to populated fields. Tests validate field round trips and tracing lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/io_tracer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/io_tracer_test.cc -->
# sources/storage-engines/rocksdb/trace_replay/io_tracer_test.cc

## Purpose

Unit tests for IO trace writer, reader, and controller lifecycle.

## Important APIs, Control Flow, And Dependencies

The fixture creates a temporary trace file and helper functions to generate file operation names, write repeated records with length/offset bits, and verify decoded records. Tests cover multiple optional field combinations, request ID through `IODebugContext`, one-record atomic write, write before start, no write after end, and direct writer multiple-record output.

## State, Persistence, Integration, Risks, And Test Signals

Each test writes a trace file and reads it back through `IOTraceReader`, checking header version fields and decoded record data. Required state includes temporary directories and `TraceWriter`/`TraceReader` file objects. The tests assert that optional fields not present in `io_op_data` remain default zero and that missing records produce non-OK reads. Risks are limited coverage for corrupted payloads and unknown bit values, but the suite confirms the normal binary contract and controller start/stop behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/io_tracer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record.cc -->
# sources/storage-engines/rocksdb/trace_replay/trace_record.cc

## Purpose

Implements concrete `TraceRecord` classes used after decoding raw trace envelopes: write, get, iterator seek, and multiget query records.

## Important APIs, Control Flow, And Dependencies

`TraceRecord` stores a timestamp and creates a `TraceExecutionHandler` for replay. `WriteQueryTraceRecord` owns a pinned write-batch representation and dispatches to `Handler::Handle`. `GetQueryTraceRecord` stores a CF ID and pinned key. `IteratorQueryTraceRecord` optionally stores lower and upper bounds; `IteratorSeekQueryTraceRecord` adds seek type, CF ID, and key, and maps seek type back to `TraceType`. `MultiGetQueryTraceRecord` owns vectors of CF IDs and pinned keys and returns vectors of slices for execution or analysis.

## State, Persistence, Integration, Risks, And Test Signals

The classes are in-memory decoded representations; persistence is in the original trace file, while `PinnableSlice` members preserve payload lifetimes after decode. Integration is through the visitor-style `Accept` methods and `TraceRecord::Handler` implementations such as `TraceExecutionHandler` and `TraceAnalyzer`. Risks include copying vectors on getters, ensuring pinned slices are cleared in destructors, and preserving lower/upper iterator bound lifetimes. Coverage is indirect through trace replay/analyzer tests that decode records and accept handlers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record_handler.cc -->
# sources/storage-engines/rocksdb/trace_replay/trace_record_handler.cc

## Purpose

Implements `TraceExecutionHandler`, the DB-backed handler that replays decoded query trace records against a live RocksDB instance and optionally returns execution results with timing and values.

## Important APIs, Control Flow, And Dependencies

The constructor builds a map from column-family ID to `ColumnFamilyHandle*` and grabs the DB system clock. Write handling reconstructs a `WriteBatch` from the trace payload and calls `DB::Write`. Get handling validates CF ID, performs `DB::Get`, treats `NotFound` as replay-success, and returns a `SingleValueTraceExecutionResult` with the actual status/value. Iterator handling applies optional lower/upper bounds to `ReadOptions`, creates an iterator, performs `Seek` or `SeekForPrev`, captures key/value when valid, deletes the iterator, and returns its status. MultiGet handling validates CF IDs and vector sizes, calls `DB::MultiGet`, treats per-key `NotFound` as OK for replay, and returns all statuses/values.

## State, Persistence, Integration, Risks, And Test Signals

The handler holds a non-owning DB pointer, non-owning CF handles, default write/read options, and a CF lookup map. Replay mutates persistent DB state for write records and reads persistent state for get/iterator/multiget records. Dependencies include `rocksdb/db.h`, iterators, write batches, status/result classes, and `SystemClock`. Risks include stale CF handles, non-ownership/lifetime assumptions, iterator bound slices pointing to record-owned memory only for the duration of the call, and replay semantics that suppress `NotFound` errors while preserving them in result objects. Tests exercise this path indirectly through trace replay users rather than this file alone.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record_handler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record_handler.h -->
# sources/storage-engines/rocksdb/trace_replay/trace_record_handler.h

## Purpose

Declares the execution handler for replaying `TraceRecord` objects against a RocksDB `DB`.

## Important APIs, Control Flow, And Dependencies

`TraceExecutionHandler` derives from `TraceRecord::Handler` and overrides handling for write, get, iterator seek, and multiget records. It stores `DB*`, a CF-ID-to-handle map, read/write options, and a system clock pointer. The constructor requires a DB and a non-empty vector of column-family handles.

## State, Persistence, Integration, Risks, And Test Signals

The header shows that replay is stateful because writes apply to the DB and all operations measure execution timestamps. It integrates directly with the trace record class hierarchy and result classes. The `TODO` notes a separate analyzer handler, which in this source set is implemented independently by `TraceAnalyzer` rather than here. Risks are non-owning DB/handle lifetimes and CF ID lookup failures. Test signals are indirect through replay and analyzer behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record_result.cc -->
# sources/storage-engines/rocksdb/trace_replay/trace_record_result.cc

## Purpose

Implements result objects produced by trace execution: status-only, single-value, multivalue, and iterator results with execution timing and trace type metadata.

## Important APIs, Control Flow, And Dependencies

`TraceRecordResult` stores `TraceType`. `TraceExecutionResult` stores start and end timestamps and asserts nondecreasing order. `StatusOnlyTraceExecutionResult`, `SingleValueTraceExecutionResult`, `MultiValuesTraceExecutionResult`, and `IteratorTraceExecutionResult` each own the relevant status/value fields and implement `Accept(Handler*)` for visitor-style result handling. Iterator results store validity plus pinned key/value slices.

## State, Persistence, Integration, Risks, And Test Signals

These are in-memory replay result carriers; they do not persist data themselves. They integrate with `TraceExecutionHandler` and any consumer implementing `TraceRecordResult::Handler`. Destructors clear owned strings/vectors/pinned slices. Risks include value copying/moving costs for large replay results, assert-only timestamp validation, and requiring callers to inspect embedded statuses because replay may return OK while a traced Get/MultiGet item was `NotFound`. Coverage is indirect via replay users and tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_record_result.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_replay.cc -->
# sources/storage-engines/rocksdb/trace_replay/trace_replay.cc

## Purpose

Implements the common RocksDB operation trace envelope, header parsing, trace encoding/decoding, conversion from raw traces to `TraceRecord` subclasses, and the `Tracer` that records DB operations.

## Important APIs, Control Flow, And Dependencies

`TracerHelper::EncodeTrace` writes timestamp, one-byte type, payload length, and payload; `DecodeTrace` decodes the envelope but does not currently validate the payload length against the remaining slice. `ParseTraceHeader` parses tab-separated header fields for trace and RocksDB version. `DecodeTraceRecord` supports legacy version 0.1 payloads and version 0.2 payload maps for write, get, iterator seek/seek-for-prev, and multiget records. The `Tracer` constructor writes a header; `Write`, `Get`, `IteratorSeek`, `IteratorSeekForPrev`, and `MultiGet` build typed payloads with `TracePayloadType` bitmaps and call `WriteTrace`; `Close` writes a footer.

## State, Persistence, Integration, Risks, And Test Signals

The `Tracer` stores trace options, writer ownership, a sampling counter, and the first trace write error. `ShouldSkipTrace` enforces max file size, operation filters, and sampling frequency. Persistent state is the trace file emitted through the supplied `TraceWriter`. Integration points are RocksDB DB tracing APIs, `TraceRecord` decode classes, analyzer tooling, execution replay, block cache tracing, and IO tracing via the shared `Trace` envelope. Risks include payload-length decode not checking length, assert-heavy malformed-payload paths, `log2`-based bit iteration, version parsing that collapses major/minor digits into one integer, and trace write error state that must be propagated through later writes and `EndTrace`. Tests in the analyzer suite explicitly cover previous trace write error propagation, while trace analyzer/replay paths exercise decode behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_replay.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_replay.h -->
# sources/storage-engines/rocksdb/trace_replay/trace_replay.h

## Purpose

Declares the shared tracing envelope and operation `Tracer` used to capture RocksDB query operations for later analysis or replay.

## Important APIs, Control Flow, And Dependencies

The header defines `kTraceMagic`, envelope size constants, trace file version 0.2, `Trace`, `TracePayloadType`, `TracerHelper`, and `Tracer`. `TracePayloadType` assigns stable bitmap positions for write batch data, get CF/key, iterator CF/key/bounds, and multiget size/CFIDs/keys. `Tracer` exposes methods for write, get, iterator seek, seek-for-prev, multiget overloads, max-size checks, write-order preservation, and closing with a footer.

## State, Persistence, Integration, Risks, And Test Signals

`Trace` is the serialized unit persisted by `TraceWriter`. `Tracer` owns a `TraceWriter`, `TraceOptions`, sampling count, and trace write status. It integrates with RocksDB operation hooks and downstream `TracerHelper::DecodeTraceRecord` consumers. Risks include keeping enum bitmap order backward compatible, filter/sampling interactions that can hide operations from analysis, and callers needing to close traces to emit `kTraceEnd`. Test signals come from trace-analyzer tests and any replay users that depend on the common format.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/trace_replay/trace_replay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/unreleased_history/add.sh -->
# sources/storage-engines/rocksdb/unreleased_history/add.sh

## Purpose

Interactive helper for adding a new unreleased RocksDB release-note fragment in the correct category and staging it in git.

## Important APIs, Control Flow, And Dependencies

The script prints release note advice and markdown formatting examples. If a target path is provided as `$1`, it uses that directly after prompting for return. Otherwise it lists one-level directories under `unreleased_history/`, asks the user to choose a group by number, prompts for a file name, replaces spaces with underscores, opens the target with `${EDITOR:-nano}`, and runs `git add "$TARGET"`.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state is the created or edited release-note file and the git index entry. It depends on a shell, `find`, `grep`, `head`, `tail`, `tr`, an editor, and git. Risks include interactive input ambiguity, no validation that a numbered selection is in range, and automatic `git add` even if the edit is incomplete. The script's success signal is zero exit after the file is edited and staged.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/unreleased_history/add.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/unreleased_history/release.sh -->
# sources/storage-engines/rocksdb/unreleased_history/release.sh

## Purpose

Release helper that folds categorized unreleased history fragments into `HISTORY.md` under a new version header derived from `include/rocksdb/version.h`.

## Important APIs, Control Flow, And Dependencies

The script requires the `unreleased_history/` directory. Unless `DRY_RUN` is set, it refuses to run with uncommitted changes under `unreleased_history/` or `HISTORY.md`. It writes `HISTORY.new` from the top of the existing history through the `NOTE` marker, appends a version/date header, then processes known directories in order: new features, public API changes, behavior changes, bug fixes, and performance improvements. `process_file` trims whitespace, ensures the first nonempty line starts with `* `, appends content to `HISTORY.new`, and removes the fragment with `git rm` unless in dry run. It checks for unexpected top-level entries, appends the remainder of existing history, and either diffs or replaces `HISTORY.md`.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state includes `HISTORY.new`, the updated `HISTORY.md`, removed release-note fragments, and git index changes from `git rm`. Dependencies include awk, git, ls, find with GNU/BSD regex differences, uname, diff, and version macros in `include/rocksdb/version.h`. Risks include parsing `HISTORY.md` around the first `NOTE`, shell word splitting over filenames with spaces in release directories, category ordering being hard-coded, and requiring a clean working tree only for selected paths. `DRY_RUN=1` provides a non-mutating diff signal; normal success prints a revert command.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/unreleased_history/release.sh -->
