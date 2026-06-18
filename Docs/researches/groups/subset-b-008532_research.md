# subset-b-008532 Research

This grouped report covers the exact source files assigned to work item `subset-b-008532`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings.go -->
# sources/storage-engines/pebble/internal/manifest/virtual_backings.go

Purpose: implements `VirtualBackings`, the manifest-side state holder for physical table backings that are referenced by virtual sstables in the latest version. It tracks backing membership by `base.DiskFileNum`, virtual table usage, protection counts used by concurrent external ingestion, aggregate stats by placement, unused backings, and local rewrite candidates.

Important APIs and types: `MakeVirtualBackings`, `AddAndRef`, `Remove`, `AddTable`, `RemoveTable`, `Protect`, `Unprotect`, `Stats`, `Usage`, `Unused`, `Get`, `All`, `DiskFileNums`, `ReplacementCandidate`, `String`; internal `backingWithMetadata` and `virtualBackingRewriteCandidatesHeap`.

Control flow and state: adding a backing takes a ref, inserts it into `m`, records placement stats, and marks it unused until protected or used by a virtual table. `AddTable` validates `TableMetadata.Virtual`, increments `virtualizedSize`, records `tableAndLevel`, removes the backing from `unused`, and pushes or fixes the local-only heap. `RemoveTable` subtracts size, re-adds to `unused` if no virtual tables or protections remain, and removes/fixes heap membership. `Protect` and `Unprotect` maintain `protectionCount`, preventing a backing from being returned by `Unused`.

Persistence and integration: this is in-memory manifest/version bookkeeping; persistence happens indirectly through version edits that add/remove backing tables and table refs. It integrates with `TableBacking`, `TableMetadata`, `base.Placement`, `metrics.CountAndSizeByPlacement`, and compaction/rewrite logic that asks for replacement candidates. Risks include invariant-sensitive ref lifecycle, panics on unknown/duplicate state, heap index correctness, division by zero if a zero-size backing were admitted, and the assumption that only local backings are rewrite candidates. Test signals come from datadriven coverage in `virtual_backings_test.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings_test.go -->
# sources/storage-engines/pebble/internal/manifest/virtual_backings_test.go

Purpose: datadriven tests for `VirtualBackings`, exercising state transitions and panic paths through a compact command language under `testdata/virtual_backings`.

Important APIs/functions: `TestVirtualBackings` creates a fresh `MakeVirtualBackings` for each test file and interprets commands `add`, `remove`, `add-table`, `remove-table`, `protect`, and `unprotect`. It builds minimal `TableBacking` and virtual `TableMetadata` values with scanned `n`, `size`, `table`, `blobValueSize`, and `level` args.

Control flow and state: every datadriven command executes under a `defer` that converts panics into output strings, allowing fixture coverage for invalid transitions. Successful commands return `bv.String()`, so expected files assert backing counts, stats, unused ordering, table lists, protection counts, and heap printouts.

Dependencies and integration: uses `github.com/cockroachdb/datadriven`, `base.DiskFileNum`, `base.TableNum`, and package-local manifest types. The tests do not exercise remote placement because all added backings use `base.Local`; remote-specific stats and exclusion from the rewrite heap remain weaker signals. Risk coverage is strong for command-level state transitions but depends on fixture breadth for heap ordering and panic wording.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual.go -->
# sources/storage-engines/pebble/internal/manual/manual.go

Purpose: defines the shared API and metrics for Pebble's manually managed byte buffers. Platform-specific allocation and freeing live in cgo and non-cgo files, while this file owns `Buf`, allocation purposes, and accounting.

Important APIs/types: `Buf` stores an `unsafe.Pointer` and length; `MakeBufUnsafe` reconstructs a `Buf` from externally retained data/length; `Data`, `Len`, and `Slice` expose the buffer. `Purpose` enumerates `BlockCacheMap`, `BlockCacheEntry`, `BlockCacheData`, `MemTable`, and `NumPurposes`. `Metrics` reports `InUseBytes` by purpose through `GetMetrics`.

Control flow and state: `recordAlloc` and `recordFree` update padded atomic counters. `recordFree` checks for negative counters under invariants, catching mismatched purpose/size frees in invariant builds. `Slice` uses `unsafe.Slice`, so callers must not call it on arbitrary or stale pointers.

Persistence and integration: state is process-local memory accounting, not durable. This file is integrated by `manual_cgo.go`, `manual_nocgo.go`, block cache, and memtable allocation paths. Risks are unsafe reconstruction, mismatched `Free`, non-GC memory visibility, and metrics representing requested bytes rather than allocator overhead or fragmentation. No direct tests are in this subset; validation is mostly from callers and invariant builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_cgo.go -->
# sources/storage-engines/pebble/internal/manual/manual_cgo.go

Purpose: cgo-backed implementation of manual allocation using `C.calloc` and `C.free`, with a race-enabled alternate mode that sometimes uses Go allocations so the race detector can observe accesses.

Important APIs/functions: `New(purpose, n)` returns a `Buf` of size `n`; `Free(purpose, b)` releases it. The file linknames `runtime.throw` as `throw` to terminate on out-of-memory in the same style as the Go runtime. `useGoAllocation` is selected randomly in race builds.

Control flow and state: zero-size allocations return an empty `Buf` without accounting. Non-zero allocations call `recordAlloc`. Race/go-allocation mode returns a pointer into a Go byte slice; normal mode calls `calloc` so memory is zeroed before Go sees it. `Free` mangles bytes in invariant builds, records the free, and calls `C.free` only for cgo allocations.

Dependencies and integration: depends on cgo, `math/rand/v2`, `unsafe`, and `invariants`. It is the production path where cgo is available and supports block cache and memtable manual memory. Risks include strict requirement to free exactly the original `Buf`, memory leaks on missed free, dangling pointers after free, and cgo pointer rules if Go pointers are stored in C memory. The race-mode all-or-none policy mitigates mixed Go/C pointer storage in manually allocated structs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_nocgo.go -->
# sources/storage-engines/pebble/internal/manual/manual_nocgo.go

Purpose: fallback manual allocator used when cgo is unavailable, such as cross-compilation. It emulates manual allocation with per-size-class `sync.Pool`s of Go-allocated byte slices.

Important APIs/functions: `New`, `Free`, package-level `pools`, `init`, and `sizeClass`. `New` records allocation bytes and returns a pooled pointer whose backing capacity is the next power-of-two size class. `Free` mangles, clears, records free bytes, and returns the pointer to the appropriate pool.

Control flow and state: `init` installs a `New` function on every pool, allocating a byte slice of size `1 << i` and boxing its data pointer. `sizeClass` computes `bits.Len(uint(size-1))` and panics on zero in invariant builds. `Free` ignores nil data after attempting to mangle the slice, matching the empty `Buf` path.

Dependencies and integration: uses `math/bits`, `sync`, `unsafe`, errors, and invariants. It integrates behind the same `manual.New/Free` API as the cgo implementation. Risks include larger retained memory due to power-of-two classes, GC-managed lifetime despite manual API semantics, stale data exposure if clearing were skipped, and caller misuse of exact-size/purpose pairing. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual_nocgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/crossversion/crossversion_test.go -->
# sources/storage-engines/pebble/internal/metamorphic/crossversion/crossversion_test.go

Purpose: implements cross-version metamorphic testing by chaining `internal/metamorphic` test binaries from multiple Pebble SHAs. It exercises upgrade and migration paths by running an older version, retaining database states, and using those states as initial inputs to later versions.

Important APIs/types: flags `-seed`, `-factor`, repeated `-version`, `-artifacts`, and `-stream-output`; `TestMetaCrossVersion`, `runCrossVersion`, `runVersion`, `metamorphicTestRun.run`, `pebbleVersions.Set`, artifact helpers `dirsToSave`, `saveDirs`, and `fatalf`.

Control flow and state: a deterministic PRNG derives per-version seeds. For each version, the test runs all current initial states through a metamorphic test binary. It gathers every subrun directory and `history`, compares histories from same-version runs with different initial states, prunes retained states to `factor`, and carries those database directories plus prior `ops` paths forward. Failures clone artifacts once under a `sync.Once`.

Persistence and integration: state lives in temp directories with `_meta` subtrees, run histories, options, ops files, and optionally copied artifacts. It integrates with external compiled test binaries, `metamorphic.CompareHistories`, `vfs.Clone`, and shell scripts described by `reproductionCommand`. Risks include flaky subprocess timeouts, missing/mismatched binaries, high disk usage from retained DBs, path assumptions around `_meta`, and deterministic reproduction requiring the same commits. Test signal is this test itself; it is usually driven by CI scripts rather than ordinary unit runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/crossversion/crossversion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/doc.go -->
# sources/storage-engines/pebble/internal/metamorphic/doc.go

Purpose: package documentation for `internal/metamorphic`, identifying it as the entry point for Pebble's internal metamorphic tests.

Important APIs/types/functions: no executable APIs are defined here. The file declares package `metamorphic` and points readers to the public-ish `pebble/metamorphic` package where the core generator, runner, compare logic, and options live.

Control flow and state: none. This file affects documentation and package identity only.

Dependencies and integration: the package contains `meta_test.go` and reduction helpers in this subset, plus many external dependencies in `github.com/cockroachdb/pebble/metamorphic`. Risks are documentation drift if entry points or package layering change. Test signal is indirect: if the package name or comments became inconsistent, Go tooling would still compile, so only human review catches most doc drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/meta_test.go -->
# sources/storage-engines/pebble/internal/metamorphic/meta_test.go

Purpose: main Go test entry point for Pebble metamorphic testing. It dispatches between generating/running a full suite, re-running one run directory, comparing existing runs, and optional reduction.

Important APIs/functions: package globals `runOnceFlags, runFlags = metaflags.InitAllFlags()`, tests `TestMeta`, `TestMetaTwoInstance`, `TestMetaCockroachKVs`, interface `option`, and `runTestMeta`. The three tests differ by additional options: default, multi-instance, or Cockroach key format.

Control flow and state: each test optionally installs leaktest. `runTestMeta` first handles `--compare`, rejecting run-only flags, optionally reducing, then calling `metamorphic.Compare`. Next it handles `--run-dir`, similarly rejecting run-only flags and calling `metamorphic.RunOnce`. Otherwise it rejects run-once-only flags, builds `RunOptions`, appends test-specific options, and calls `metamorphic.RunAndCompare`.

Persistence and integration: generated state is under the configured `_meta` directory, including ops, options, histories, and DB directories. It integrates with `metaflags`, `leaktest`, and the core `pebble/metamorphic` package. Risks include global flag initialization side effects, invalid flag combinations, long-running generated workloads, and reproducibility depending on seed plus commit. Test signal is broad system-level coverage rather than narrow unit assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/meta_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metaflags/meta_flags.go -->
# sources/storage-engines/pebble/internal/metamorphic/metaflags/meta_flags.go

Purpose: centralizes command-line flags for metamorphic tests and translates parsed flag values into `metamorphic.RunOption` and `RunOnceOption` slices.

Important APIs/types: `CommonFlags`, `RunOnceFlags`, `RunFlags`, `KeyFormats`, `InitRunOnceFlags`, `InitAllFlags`, `RunOnceOnlyFlagNames`, `RunOnlyFlagNames`, `MakeRunOnceOptions`, `MakeRunOptions`, and `ParseCompare`. Flags cover directories, seeds, error injection, fail regexes, retention, max threads, instance count, op timeout, key format, initial state, leaktest, treesteps, filesystem forcing, runtime trace, op-count distribution, inner binary, previous ops, compare, run-dir, and reducer attempts.

Control flow and state: initialization registers flags on `flag.CommandLine`. Run-once and run flag sets share `CommonFlags`. `MakeRunOptions` validates split-version initial-state/previous-ops pairing and handles forced filesystem names. `ParseCompare` parses `root/{run1,run2}` and exits on invalid input.

Dependencies and integration: depends on `buildtags`, `randvar.Flag`, `errors`, regexp, and `pebble/metamorphic`. It is used by `meta_test.go` and `metarunner`. Risks include global flag collisions, `os.Exit` in parsing helpers, panic on unknown key format or filesystem, and flag compatibility drift when adding new modes. Test signals are mostly integration-level through metamorphic tests, not dedicated unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metaflags/meta_flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metarunner/main.go -->
# sources/storage-engines/pebble/internal/metamorphic/metarunner/main.go

Purpose: small command-line runner for executing `metamorphic.RunOnce` or `metamorphic.Compare` outside `go test`, primarily for coverage instrumentation while maintaining flag compatibility with `TestMeta`.

Important APIs/types: package global `runOnceFlags = metaflags.InitRunOnceFlags()`, ignored `-test.run` flag, `main`, and `mockT` implementing `metamorphic.TestingT`.

Control flow and state: `main` parses flags, builds run-once options, and dispatches to compare mode if `--compare` is set, single-run mode if `--run-dir` is set, or reports an error otherwise. It writes failures through `mockT.Errorf`; if any failure occurred, `FailNow` exits with status 2.

Persistence and integration: uses the same run directories, history paths, and compare root directories as `internal/metamorphic` tests. It integrates with `metaflags` and `pebble/metamorphic` without a real `testing.T`. Risks include limited test-like behavior in `mockT`, hard process exit on failure, and reliance on run-once flags only. No local tests are included; confidence comes from the shared option builder and use by coverage workflows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metarunner/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/reduce_test.go -->
# sources/storage-engines/pebble/internal/metamorphic/reduce_test.go

Purpose: implements a reducer for metamorphic failures, attempting to remove operations and simplify keys while preserving a reproduction.

Important APIs/types: `tryToReduce`, `tryToReduceCompare`, `reducer`, `testConfig`, `makeReducer`, `setupRunDirs`, `getKeyFormat`, `try`, `Run`, `randomSubset`, and `shellJoin`.

Control flow and state: the reducer reads an existing `ops` file and selected run `OPTIONS`, creates fresh reduce directories under the configured test state root, and re-runs the current test binary with either `--run-dir` or `--compare`. If the reduced run still fails for the target reason, it saves logs and optional diagrams, deletes the previously saved reduced directory, and continues. `Run` decreases random removal probability over time, then tries key simplification with and without suffix retention.

Persistence and integration: writes new `reduce-*` directories, `ops`, `OPTIONS`, `log`, and optional `diagram`. It integrates with the current test binary via `os.Args[0]`, `metamorphic.TryToGenerateDiagram`, and `TryToSimplifyKeys`. Risks include nondeterministic failures, hard-coded internal-error filters, fixed 10s timeout during reduction, potentially many subprocesses, and deletion of previous saved reductions. Test signal is operational rather than unit-tested here.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/reduce_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford.go -->
# sources/storage-engines/pebble/internal/metricsutil/welford.go

Purpose: provides numerically stable online calculation of mean, sample variance, and standard deviation for unweighted and frequency-weighted samples.

Important APIs/types: `Welford` with `Add`, `Count`, `Mean`, `Variance`, `StdDev`; `WeightedWelford` with `Add(x, frequency)`, `Mean`, `Variance`, and `StdDev`.

Control flow and state: `Welford.Add` updates count, mean, and `m2` using Welford's incremental algorithm. `Variance` returns sample variance `m2/(n-1)` and guards counts below 2. `WeightedWelford.Add` ignores zero frequency, converts frequency to `float64`, tracks total weight, sum of squared weights, mean, and accumulated squared deviation `s`; variance uses `s/(wSum-1)`.

Persistence and integration: all state is in-memory and caller-owned. Dependencies are only `math`. Risks include no synchronization, possible precision loss or overflow for extreme values/frequencies, and `w2Sum` currently being maintained but unused in the reported variance formula. Tests cover basic means and sample variances, including equivalence to repeated samples.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford_test.go -->
# sources/storage-engines/pebble/internal/metricsutil/welford_test.go

Purpose: unit tests for unweighted and weighted Welford statistics.

Important APIs/functions: `almostEqual`, `TestWelfordBasic`, and `TestWeightedWelford`. The tests assert empty, single-value, constant, simple 1..5, and mixed repeated distributions.

Control flow and state: table-driven tests instantiate zero-value accumulators, feed input values, and compare count, mean, and sample variance with a small epsilon. The weighted test uses frequency arrays to represent repeated samples and checks that the weighted path matches expected repeated-sample statistics.

Dependencies and integration: uses `math` and `testing` only. Risks not covered include standard deviation specifically, very large values/frequencies, negative values, NaN/Inf behavior, and whether the unused `w2Sum` should matter for an unbiased weighted estimator. The tests are valuable smoke tests for sample variance semantics because expected values explicitly use `M2/(n-1)`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window.go -->
# sources/storage-engines/pebble/internal/metricsutil/window.go

Purpose: generic sliding metrics window that periodically samples a caller-provided metric and returns approximate values from ten minutes and one hour ago.

Important APIs/types: `NewWindow[M]`, `CollectFn[M]`, `Window[M]`, `TenMinutesAgo`, `OneHourAgo`, `Start`, `Stop`, internal `tick`, constants `timeframeA`, `timeframeB`, `resolution`, `tickA`, `tickB`, and `ring[M]`.

Control flow and state: `Start` initializes rings and launches a goroutine to collect the initial sample without risking lock inversion with caller locks. It schedules a single timer at `tickA`; `tick` collects once, appends to the 10-minute and 1-hour rings as many times as required by elapsed time, then resets the timer to the next due sample. `Stop` marks the window stopped and stops the timer while holding the mutex.

Persistence and integration: state is in-memory; timestamps use monotonic `crtime.Mono`. The window is concurrency-safe around its mutex but `collectFn` is invoked under that mutex, so callers must avoid re-entering `Window` from collection. Risks include timer reset after very delayed ticks, zero values until rings wrap, generic metric copying cost, and no panic recovery around `collectFn`. Go 1.25 synctest coverage validates approximate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window_test.go -->
# sources/storage-engines/pebble/internal/metricsutil/window_test.go

Purpose: deterministic time test for `Window` using Go 1.25 `testing/synctest`.

Important APIs/functions: build-tagged `TestWindow` constructs `NewWindow[time.Duration]` with `startTime.Elapsed`, starts and stops it, advances fake time, and checks `TenMinutesAgo` and `OneHourAgo`.

Control flow and state: before ten minutes, `TenMinutesAgo` must return zero metric and zero timestamp. After roughly ten minutes, it expects the timestamp age to be around ten minutes and the sampled value near zero. After more time, it expects the ten-minute sample's metric to reflect about twenty minutes elapsed, and the one-hour sample to be between fifty and seventy minutes old with metric from the first ten minutes.

Dependencies and integration: depends on Go 1.25, `testing/synctest`, `time`, and `crtime`. It validates asynchronous timers without real sleeps. Risks not covered include repeated start/stop races, collect function panics, collection latency, and very long pauses. On older Go versions this test is excluded, so coverage depends on build environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/main.go -->
# sources/storage-engines/pebble/internal/mkbench/main.go

Purpose: root command for `mkbench`, a Pebble benchmark data processing CLI. It converts nightly benchmark raw logs into cooked JSON/JS files consumed by benchmark visualizations.

Important APIs/functions: package global `rootCmd`, `init`, and `main`. `init` registers `ycsb` and `write` subcommands and preserves backward compatibility by copying the YCSB command flags and `RunE` onto the root command.

Control flow and state: process startup initializes Cobra commands, then `main` executes `rootCmd`. Errors are assumed to have already been printed by Cobra and cause exit status 1. The backward-compatible root behavior means invoking `mkbench` without a subcommand runs the YCSB parser using the same flags.

Dependencies and integration: uses `os` and `github.com/spf13/cobra`, plus local `getYCSBCommand` and `getWriteCommand`. It integrates with historical CockroachDB nightly Pebble benchmark scripts. Risks include flag-copy fragility, duplicated `getYCSBCommand` call in `init`, and future removal of root YCSB compatibility requiring call-site updates. Tests focus on parser behavior, not the Cobra root itself.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split.go -->
# sources/storage-engines/pebble/internal/mkbench/split.go

Purpose: computes an ops/sec threshold separating successful and failed write-throughput measurements with minimal misclassification.

Important APIs/functions: constant `increment = 50` and `findOptimalSplit(pass, fail []int) int`.

Control flow and state: the function rejects missing pass or fail data with `-1`, copies and sorts inputs, scans thresholds from minimum pass to maximum fail in 50 ops/sec increments, updates counts of misclassified passes and fails, and records `(threshold, error)` pairs. It sorts candidates by error and threshold, then averages the lowest and highest threshold within the best-error plateau.

Persistence and integration: pure computation with no persistent state. It is used by `rawWriteRun.opsPerSecSplit` in write benchmark cooking. Risks include assumptions that pass values should be below the split and fail values above it, scan bounds using first pass and last fail after sorting, coarse 50 ops/sec resolution, and possible odd behavior if all fails are below all passes. Unit tests cover empty, trivial, documented, and empirical cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split_test.go -->
# sources/storage-engines/pebble/internal/mkbench/split_test.go

Purpose: table-driven tests for `findOptimalSplit`.

Important APIs/functions: `TestFindOptimalSplit` defines pass/fail arrays and expected split values, using `require.Equal`.

Control flow and state: cases cover no data, one side missing, a trivial one-pass/one-fail split, the example from the function comment, and a large empirical data set from an actual run. Each test invokes `findOptimalSplit` and checks the exact threshold.

Dependencies and integration: uses `testing` and `testify/require`. The empirical case gives realistic noisy pass/fail overlap coverage for the write-throughput parser. Risks not covered include negative inputs, pass/fail distributions with reversed ordering, plateau behavior across unusual ranges, and sensitivity to `increment` changes beyond expected fixture updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/split_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/data.js -->
# sources/storage-engines/pebble/internal/mkbench/testdata/data.js

Purpose: expected cooked YCSB benchmark fixture used by mkbench tests.

Important data shape: JavaScript assignment `data = { ... };` mapping workload names like `ycsb/A/values=1024` to newline-delimited CSV strings. Each CSV line encodes day, ops/sec, read bytes, write bytes, read amplification, and write amplification.

Control flow and state: no executable control flow. The file represents merged, sorted, cooked output for two days of fixture data and multiple YCSB workloads/value sizes. It also acts as an existing cooked input in incremental parsing tests.

Dependencies and integration: consumed by `ycsbLoader.loadCooked`, `parseYCSB`, and tests comparing generated output with `filesEqual`. Persistence behavior is fixture-based: parser output must be byte-equivalent after JSON pretty printing and semicolon wrapping. Risks include fixture drift if formatting changes, lack of schema validation beyond parser assumptions, and JavaScript wrapper format being required by older visualization code.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/data.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211027-pebble-write-size=1024-run_1-summary.json -->
# sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211027-pebble-write-size=1024-run_1-summary.json

Purpose: expected per-run write-throughput summary fixture for the 20211027 `write/values=1024` benchmark.

Important data shape: JSON object keyed by original raw log paths. Each value contains `opsSec`, the optimal split computed from pass/fail datapoints, and `rawData`, a newline-delimited CSV series of elapsed seconds, ops/sec, pass flag, bytes, level count, and write amplification.

Control flow and state: no executable control flow. The file captures cooked output from all raw worker logs for one run directory, preserving source path provenance in keys.

Dependencies and integration: compared by `TestParseWrite_FromScratch` and `TestParseWrite_Existing` against output generated by `parseWrite`. It also links from top-level `summary.json` via `summaryPath`. Risks include large embedded CSV strings being fragile to formatting, gzip fixture parsing changes requiring updates, and no independent schema validation beyond JSON decoding/comparison in tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211027-pebble-write-size=1024-run_1-summary.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211028-pebble-write-size=1024-run_1-summary.json -->
# sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211028-pebble-write-size=1024-run_1-summary.json

Purpose: expected per-run write-throughput summary fixture for the 20211028 `write/values=1024` benchmark.

Important data shape: JSON object keyed by raw input paths, each containing `opsSec` and `rawData` CSV. It mirrors the 20211027 fixture for a later day with different optimal split and write amplification results.

Control flow and state: static fixture only. It preserves full raw cooked datapoints so tests can verify both summary scoring and provenance-preserving output filenames.

Dependencies and integration: used by write parser tests through `testdataPerRunSummaryFilenames`. The top-level summary fixture points to this filename, and incremental tests verify it is produced when 20211028 data remains. Risks are the same as the 20211027 fixture: large raw string fragility, byte-for-byte formatting dependence, and limited semantic validation beyond fixture comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211028-pebble-write-size=1024-run_1-summary.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/summary.json -->
# sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/summary.json

Purpose: expected top-level cooked write-throughput summary fixture.

Important data shape: JSON maps workload name `write/values=1024` to sorted day summaries. Each summary includes `name`, `date`, averaged `opsSec`, averaged rounded `writeAmp`, and `summaryPath` pointing to a per-run summary JSON.

Control flow and state: no executable logic. The file is the aggregate output of `writeLoader.cookSummary`, mixing per-day cooked runs into a visualization-friendly time series.

Dependencies and integration: compared against generated `summary.json` by write parser tests. It must remain consistent with per-run fixture filenames and `writeRun.summaryFilename`. Risks include date sorting/merge logic changes requiring expected output updates, no coverage for multiple workloads beyond this single fixture, and byte-for-byte JSON indentation sensitivity.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/summary.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testutil.go -->
# sources/storage-engines/pebble/internal/mkbench/testutil.go

Purpose: shared test helpers for mkbench parser tests.

Important APIs/functions: `filesEqual`, `copyDir`, and `maybeSkip`. `filesEqual` reads two files, normalizes CRLF to LF, and returns a unified diff as an error if contents differ. `copyDir` recursively copies a directory tree using `walkDir`. `maybeSkip` skips tests on Windows because summary fixture paths are Unix-oriented.

Control flow and state: `copyDir` creates directories with mode 0700, copies files with `io.Copy`, and follows the traversal behavior of `walkDir`, including symlinks. `filesEqual` constructs diffs through `go-difflib`.

Dependencies and integration: supports YCSB, write, and walkDir tests. Risks include preserving file mode only loosely, not handling special files beyond `walkDir` behavior, and Windows coverage being intentionally skipped. It is a test-only utility, so production risk is low.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util.go -->
# sources/storage-engines/pebble/internal/mkbench/util.go

Purpose: common mkbench utility functions for JSON formatting and recursive directory walking with symlink handling.

Important APIs/functions: `prettyJSON(v interface{}) []byte` and `walkDir(dir, handleFn)`.

Control flow and state: `prettyJSON` marshals with tab indentation and terminates the process with `log.Fatal` on marshal errors. `walkDir` wraps `filepath.Walk`; for non-regular/non-directory entries it calls `os.Stat`, and if the target is a directory it recursively walks that symlinked directory. For every accepted entry it computes the relative path and calls `handleFn`.

Dependencies and integration: used by YCSB and write loaders and by tests. It integrates with fixtures that include symlinked directories. Risks include potential cycles through symlinked directories, swallowed errors from the recursive symlink walk (`_ = filepath.Walk(...)`), process exit from `prettyJSON`, and deprecated `filepath.Walk` style. Tests validate fixture traversal count across real and symlinked test data.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util_test.go -->
# sources/storage-engines/pebble/internal/mkbench/util_test.go

Purpose: verifies `walkDir` traverses mkbench fixture data, including the symlinked fixture path, with the expected number of entries.

Important APIs/functions: `TestWalkDir` and constant `wantCount = 97`.

Control flow and state: the test calls `maybeSkip`, then for each path in `dataDirPaths` invokes `walkDir`, appending every relative path reported to `paths`. It asserts no error and exact path count.

Dependencies and integration: depends on shared `dataDirPaths` from `ycsb_test.go` and `testify/require`. It gives signal for symlink following and fixture shape. Risks not covered include ordering, path content, symlink cycles, errors from the handler, and non-directory special file behavior. The hard-coded count will need updates when fixtures change.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write.go -->
# sources/storage-engines/pebble/internal/mkbench/write.go

Purpose: implements the `mkbench write` command, parsing raw write-throughput benchmark logs into top-level and per-run JSON summaries.

Important APIs/types: `getWriteCommand`, `writePoint`, `rawWriteRun`, `writeRunSummary`, `writeRun`, `cookedWriteRun`, `writeWorkload`, `writeLoader`, `newWriteLoader`, `loadCooked`, `loadRaw`, `addRawRun`, `cookSummary`, `cookWriteSummary`, `cookWriteRunSummaries`, `outputWriteRunSummary`, and `parseWrite`.

Control flow and state: `parseWrite` loads existing `summary.json` to seed cooked workload/day pairs, walks raw data, skips already-cooked days, parses compressed or plain logs matching `BenchmarkRaw...`, groups points by workload/day/raw path, computes optimal ops/sec splits with `findOptimalSplit`, writes merged top-level summaries sorted by date, and writes per-run raw summaries. Errors reading individual raw files are printed and skipped; output file errors are returned.

Persistence and integration: reads raw `data` trees and previous `write-throughput/summary.json`; writes `summary.json` and provenance-preserving `*-summary.json` files. Integrates with Cobra, gzip/bzip2 readers, `split.go`, `prettyJSON`, and `walkDir`. Risks include division by zero if a writeRun has no raw runs, scanner token limits on very long lines, skipping all files for a cooked workload/day even if new logs appear, stderr-only parse errors, and path-layout assumptions. Tests cover from-scratch and incremental fixture generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write_test.go -->
# sources/storage-engines/pebble/internal/mkbench/write_test.go

Purpose: integration-style fixture tests for the write-throughput parser.

Important APIs/functions: constants and variables for fixture paths, `TestParseWrite_FromScratch`, and `TestParseWrite_Existing`.

Control flow and state: from-scratch tests create a temp output directory, call `parseWrite`, and compare generated top-level and per-run summaries to fixtures. Existing-data tests copy raw fixture data, remove one day, generate partial summaries, assert the top-level summary differs and only remaining-day per-run files exist, then parse the full data into the same summary dir and assert it converges to fixtures.

Dependencies and integration: uses `copyDir`, `filesEqual`, `maybeSkip`, `dataDirPaths`, `os`, `filepath`, `strings`, and `testify/require`. It covers both real and symlinked input roots. Risks not covered include malformed raw lines beyond skip behavior, multiple workloads, corrupt existing JSON, and output directory creation failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb.go -->
# sources/storage-engines/pebble/internal/mkbench/ycsb.go

Purpose: implements `mkbench ycsb`, converting raw YCSB benchmark logs into a `data = {...};` JavaScript data file while preserving previously cooked days.

Important APIs/types: `getYCSBCommand`, `ycsbRun`, `ycsbWorkload`, `ycsbLoader`, `newYCSBLoader`, `addRun`, `loadCooked`, `loadRaw`, `cook`, `cookWorkload`, `cookDay`, and `parseYCSB`.

Control flow and state: `loadCooked` parses an existing JS assignment, unwraps JSON, reconstructs workload/day runs, and marks days as cooked. `loadRaw` walks `$date/pebble/ycsb/$name/$run/$file`, skips cooked days, decompresses `.bz2` or `.gz`, scans benchmark lines, parses metrics, and appends runs. `cookDay` averages multiple runs after excluding ops/sec outliers more than one standard deviation from the mean. `cook` writes pretty JSON with the JS prefix/suffix.

Persistence and integration: reads raw logs plus optional existing cooked file and writes a cooked JS file. Integrates with Cobra, compression readers, `walkDir`, and `prettyJSON`. Risks include `log.Fatal` exits on malformed cooked input or write failures, possible divide by zero if all runs are excluded as outliers, day-level cooked skipping across all workloads, scanner limits, and stderr-only raw parse errors. Tests cover from-scratch and incremental fixtures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb_test.go -->
# sources/storage-engines/pebble/internal/mkbench/ycsb_test.go

Purpose: fixture tests for YCSB parsing and incremental merge behavior.

Important APIs/functions: constants `dataDirPath`, `dataSymlinkedDirPath`, `dataJSPath`, global `dataDirPaths`, `TestParseYCSB_FromScratch`, and `TestYCSB_Existing`.

Control flow and state: from-scratch tests parse each fixture input root into a temp `data.js` and compare against expected. Existing tests copy raw data, remove 20211027, generate a partial output and confirm it differs, then call `parseYCSB` using the full fixture data and expected `data.js` as the cooked input to verify final output matches.

Dependencies and integration: uses shared mkbench test helpers, temp dirs, and symlinked fixture paths. It validates the backward-compatible parser output format indirectly. Risks not covered include malformed existing JS, multiple cooked files, outlier edge cases, raw parse warnings, and Windows path behavior because tests skip on Windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker.go -->
# sources/storage-engines/pebble/internal/overlap/checker.go

Purpose: determines whether a user-key region overlaps table boundaries or actual point/range data in an LSM level or whole version, with a best-effort probe path for external ingestion and splitting decisions.

Important APIs/types: `WithLSM`, `WithLevel`, `Kind` (`None`, `OnlyBoundary`, `Data`), `Checker`, `IteratorFactory`, `MakeChecker`, `LSMOverlap`, `LevelOverlap`, `EmptyRegion`, and internal empty-region helpers.

Control flow and state: `LSMOverlap` checks L0 sublevels first and stops on data overlap; then checks levels 1+. `LevelOverlap` performs a cheap boundary test: no file means `None`, file boundaries inside the region mean pessimistic `Data`, and a single enclosing file may be probed unless `SkipProbe` says not to. `EmptyRegion` checks point keys/range deletions and then range keys by opening iterators only when metadata bounds overlap. Fragment iterators are probed with `First` or `SeekGE` based on known lower bounds.

Persistence and integration: no persistent state; uses manifest metadata and table iterators supplied by callers. Integrates with `manifest.Version`, `LevelSlice`, `base.UserKeyBounds`, `keyspan`, and external ingestion code that can skip remote probes. Risks include false positives by design, iterator errors propagating, assumptions about metadata bounds, empty span assertions, and opening files for probes. Datadriven tests cover boundary/data/range cases and iterator-open behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker_test.go -->
# sources/storage-engines/pebble/internal/overlap/checker_test.go

Purpose: datadriven tests for overlap detection using in-memory fake tables and iterators.

Important APIs/types: `TestChecker`, `testTable`, `testTables`, `newTestTables`, iterator factory methods `Points`, `RangeDels`, `RangeKeys`, helper `splitLinesInSections`, and `boundsFromSpans`.

Control flow and state: `define` commands build table metadata from points, range deletions, range keys, and optional override bounds. `overlap` commands build a `LevelMetadata`, optionally set `SkipProbe`, call `LevelOverlap` for each requested bounds line, and print result plus which iterators were opened. Fake iterator factories sometimes return nil for empty iterators to exercise nil-as-empty behavior.

Dependencies and integration: uses datadriven fixtures, `base.NewFakeIter`, `keyspan.NewIter`, manifest metadata bound extension methods, and `testify/require`. Risks covered include loose external-ingestion bounds, point/range split behavior, skip-probe pessimism, and iterator selection. Remaining gaps include whole-version `LSMOverlap`, real table reader errors, context cancellation, and concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/pebble/main.go -->
# sources/storage-engines/pebble/internal/pacertoy/pebble/main.go

Purpose: standalone simulation of Pebble-style pacing, modeling memtable filling, flush draining, L0 compaction, compaction debt, and adaptive flush-rate throttling.

Important APIs/types: constants for rates, sizes, thresholds, and level counts; `compactionPacer`, `flushPacer`, `DB`, `newDB`, background methods `drainCompaction` and `drainMemtable`, `fillCompaction`, `delayMemtableDrain`, `fillMemtable`, `simulateWrite`, and `main`.

Control flow and state: `newDB` initializes memtables, L0, level sizes, full lower levels, limiters, and starts two background loops. User writes fill mutable memtables, flushers drain immutable memtables into L0, and compaction drains L0 into lower levels. Compaction debt reduces flush max rate when above threshold and gradually restores it otherwise. `main` prints one-second metrics until `simulateWrite` exits after a fixed write amount.

Persistence and integration: no durable DB; all structures are simulation counters protected by mutexes/atomics/conds and `rate.Limiter`. Risks include toy fidelity, infinite goroutines, reliance on `os.Exit`, possible cond signaling subtleties, and measure-latency indexing assumptions. There are no tests; its value is exploratory comparison of pacing dynamics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/pebble/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/rocksdb/main.go -->
# sources/storage-engines/pebble/internal/pacertoy/rocksdb/main.go

Purpose: standalone simulation of RocksDB-style write pacing, used as a contrast with the Pebble pacer toy.

Important APIs/types: constants for compaction/write rates and thresholds; `compactionPacer`, `flushPacer`, `DB`, `newDB`, `drainCompaction`, `fillCompaction`, `drainMemtable`, `delayUserWrites`, `fillMemtable`, `simulateWrite`, and `main`.

Control flow and state: writes pass through an input limiter and a DB `writeLimiter`. Memtable fills block when dirty bytes exceed `memtableStopThreshold`. Flush and compaction loops move bytes through L0 and lower levels. `delayUserWrites` adjusts `writeLimiter`: slows when L0 count or compaction debt is high and growing, speeds when debt shrinks, and rewards recovery after prior debt.

Persistence and integration: no real storage; this is a simulation using mutexes, cond vars, atomics, and `rate.Limiter`. It prints periodic metrics including max write rate. Risks include nondeterministic seeds from time, endless execution, toy assumptions about compaction geometry, possible lock misuse around `len(db.L0)` under `db.mu` rather than `compactionMu`, and no tests. Integration is manual experimentation rather than production code.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/rocksdb/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/private/batch.go -->
# sources/storage-engines/pebble/internal/private/batch.go

Purpose: exposes a package-private hook for tests needing sorted iterators over batch mutations without making the batch internals public.

Important API: variable `BatchSort`, a function accepting an opaque batch-like `interface{}` and returning point, range-delete, and range-key iterators.

Control flow and state: no local control flow. The variable is assigned elsewhere, likely by the main Pebble package or tests, and consumers call it through the `internal/private` import boundary.

Persistence and integration: integrates with `base.InternalIterator` and `keyspan.FragmentIterator`. State is global process state, so tests must manage assignment ordering and cleanup. Risks include nil `BatchSort` panics if called before initialization, type assertion risks in the implementation behind the hook, and global mutation causing test coupling. There are no tests in this file; it is a narrow dependency-inversion point.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/private/batch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level.go -->
# sources/storage-engines/pebble/internal/problemspans/by_level.go

Purpose: concurrency-safe wrapper around per-level `Set`s of expiring problem spans, allowing LSM-level-specific overlap checks and global excision.

Important APIs/types: `ByLevel`, `Init`, `InitForTesting`, `IsEmpty`, `Add`, `Overlaps`, `Excise`, `Len`, and `String`.

Control flow and state: `Init` creates one `Set` per level and initializes the atomic empty fast-path. `Add` locks, clears the empty marker, and adds to the selected level. `Overlaps` returns false immediately if the atomic empty marker is true; otherwise it locks and delegates. `IsEmpty` scans all levels under lock and sets the atomic fast-path when all are empty. `Excise` applies removal to every level.

Persistence and integration: all state is in-memory and expiration is driven by `crtime.Mono`. Integrates with `problemspans.Set` and `base.UserKeyBounds`; likely used in compaction/read paths that need to avoid problematic key spans. Risks include required initialization, level index bounds panics, stale false in the empty fast-path until a scan, and coarse global mutex contention. Datadriven tests cover add/overlap/excise/empty behavior with mocked time.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level_test.go -->
# sources/storage-engines/pebble/internal/problemspans/by_level_test.go

Purpose: datadriven tests for `ByLevel` behavior over mocked monotonic time.

Important APIs/functions: `TestByLevel` initializes seven levels with `InitForTesting`, parses `now` arguments, and supports commands `add`, `excise`, `overlap`, and `is-empty`.

Control flow and state: test time can only move forward. `add` lines include level plus bounds and absolute expiration time; the test converts this to a duration from current time. `excise` applies bounds to all levels. `overlap` checks a specific level and prints result. Every command appends a formatted `ByLevel` dump for fixture verification.

Dependencies and integration: uses datadriven fixtures, `crstrings.LinesSeq`, `parseSetLine` from `set_test.go`, and `testify/require`. Risks not covered include concurrent access, invalid level indexes, and high cardinality/performance. It does strongly validate expiration semantics and per-level isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/doc.go -->
# sources/storage-engines/pebble/internal/problemspans/doc.go

Purpose: package documentation for tracking key spans that are problematic for a bounded time and checking/excising active spans.

Important content: describes span registration with expiration, overlap detection, span excision, and level-based organization with concurrent operations.

Control flow and state: none; package declaration only.

Dependencies and integration: documents the behavior implemented by `Set` and `ByLevel`. Risks are doc drift, especially because concurrency safety differs between `Set` (not safe) and `ByLevel` (safe), and because expiration behavior depends on monotonic time. Test signal is indirect through package tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set.go -->
# sources/storage-engines/pebble/internal/problemspans/set.go

Purpose: maintains a set of user-key spans with expiration times, supports overlap checks against non-expired spans, and removes fragments through excision.

Important APIs/types: `Set`, `expirationTime`, `Init`, internal `init`, `boundsToEndpoints`, `Add`, `Overlaps`, `Excise`, `IsEmpty`, `Len`, and `String`.

Control flow and state: `Set` wraps an `axisds/regiontree` keyed by inclusive/exclusive endpoints with `expirationTime` as the property. The property equality function treats any two expired properties as equal to each other and to zero, enabling GC/coalescing as time advances. `Add` updates a bounds interval to the max of existing and new expiration. `Overlaps` asks whether any region in range has expiration greater than current time, with GC enabled. `Excise` sets the interval to zero.

Persistence and integration: in-memory only, with `nowFn` injected for tests and `crtime.NowMono` in production. Dependencies include `axisds`, `regiontree`, and `base.UserKeyBounds`. Risks include no internal synchronization, initialization required before use, careful endpoint conversion for inclusive/exclusive bounds, and expiration cleanup depending on operations. Datadriven and randomized tests cross-check against a naive model.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set_test.go -->
# sources/storage-engines/pebble/internal/problemspans/set_test.go

Purpose: validates `Set` with datadriven scenarios and randomized comparison to a naive implementation.

Important APIs/types: `TestSet`, `parseSetLine`, `TestSetRandomized`, `naiveSpan`, and `naiveSet` with `Add`, `Overlaps`, and `Excise`.

Control flow and state: datadriven tests maintain mocked monotonic time and support `reset`, `add`, `excise`, `overlap`, and `is-empty`, printing the active set after each command. Randomized tests run 1000 trials of 300 operations over random key bounds, adding expiring spans, excising exclusive bounds, querying overlaps, and advancing time; every query is checked against the naive span list.

Dependencies and integration: uses `base.UserKeyBounds`, `crtime.Mono`, datadriven, and random package. The randomized test is a strong signal for endpoint and expiration semantics. Gaps include concurrent use, inclusive excise in the naive model, and very large span counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck.go -->
# sources/storage-engines/pebble/internal/randvar/deck.go

Purpose: implements a weighted random generator using a shuffled deck so each weight appears exactly its configured number of times per deck cycle.

Important APIs/types: `Deck`, `NewDeck`, and `Int`.

Control flow and state: `NewDeck` expands integer weights into a slice containing each index repeated by its weight, stores an RNG through `ensureRand`, and sets the index to the deck length so the first `Int` shuffles. `Int` locks, reshuffles when the deck is exhausted, returns the current card, advances the index, and unlocks.

Persistence and integration: state is in-memory and concurrency-safe around the deck. It integrates with `math/rand/v2` and local `NewRand`. Risks include panic if all weights sum to zero because `Int` indexes an empty deck, no validation for negative weights, and holding the mutex during shuffle. The test samples values but does not assert distribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck_test.go -->
# sources/storage-engines/pebble/internal/randvar/deck_test.go

Purpose: smoke test for `Deck`.

Important APIs/functions: `TestDeck` creates `NewDeck(nil, 10, 20, 20, 0, 30)`, draws 10,000 samples, and optionally prints a histogram through `dumpSamples` when verbose.

Control flow and state: the test exercises repeated deck reshuffling and confirms only that no panic occurs under a normal non-empty weight set.

Dependencies and integration: reuses `dumpSamples` from `skewed_latest_test.go`. Risk coverage is shallow: it does not assert frequencies, zero-weight exclusion, empty deck behavior, or concurrency. It is primarily a manual visualization aid under verbose test runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/flag.go -->
# sources/storage-engines/pebble/internal/randvar/flag.go

Purpose: command-line flag adapters for numeric random variables and random byte generators.

Important APIs/types: regex `randVarRE`, `Flag`, `NewFlag`, `String`, `Type`, `Set`, `BytesFlag`, `NewBytesFlag`, `BytesFlag.Set`, and `BytesFlag.Bytes`.

Control flow and state: `Flag.Set` parses specs like `uniform:1-10`, `latest:1-10`, `zipf:1-10`, or a single value, constructs the matching `Static`, and stores the original spec. `BytesFlag.Set` parses `sizeSpec[/compressionRatio]`, delegates size parsing to `Flag`, and records target compression. `Bytes` draws a size, fills a unique prefix with random bytes, then repeats that prefix to reach the target size/compressibility.

Persistence and integration: used by metamorphic flags and other randomized test workloads. Dependencies include `flag`, `regexp`, `encoding/binary`, `rand/v2`, and local random-variable constructors. Risks include limited spec grammar, no validation for target compression <= 0, possible panic if callers pass nil RNG to `Bytes` because it uses `r.Uint64()` directly, and generated compression ratio being approximate. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/flag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/rand.go -->
# sources/storage-engines/pebble/internal/randvar/rand.go

Purpose: small RNG helpers for the `randvar` package.

Important APIs/functions: `NewRand` and `ensureRand`.

Control flow and state: `NewRand` constructs a new `math/rand/v2.Rand` using a PCG source seeded with zero stream and a random `rand.Uint64()` seed. `ensureRand` returns its argument when non-nil or a new random generator otherwise.

Persistence and integration: state is caller-owned RNG state. This helper is used by `Deck` and skewed-latest tests. Risks include non-reproducibility when callers pass nil, no way to inject deterministic seed through `NewRand`, and shared RNG thread-safety depending on caller usage. Tests indirectly exercise it through randvar generators.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/rand.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/randvar.go -->
# sources/storage-engines/pebble/internal/randvar/randvar.go

Purpose: declares common interfaces for random variable implementations.

Important APIs/types: `Static` exposes `Uint64(*rand.Rand) uint64`; `StaticBytes` exposes `Bytes(*rand.Rand, []byte) []byte`; `Dynamic` embeds `Static` and adds `IncMax` and `Max`.

Control flow and state: no executable logic. These interfaces define contracts used by flags, metamorphic operation counts, byte generators, Zipf/uniform/skewed-latest generators, and dynamic workloads.

Persistence and integration: interface-only; no persistence. Risks are contract ambiguity around nil RNG handling, thread-safety, inclusivity of bounds, and whether returned byte buffers may alias input buffers. Implementations in this subset vary: `Deck` tolerates nil RNG through `ensureRand`, while `BytesFlag.Bytes` expects non-nil.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/randvar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest.go -->
# sources/storage-engines/pebble/internal/randvar/skewed_latest.go

Purpose: dynamic random variable that returns values in `[min,max]` skewed toward the latest/highest values using a Zipf distribution over distance from max.

Important APIs/types: `SkewedLatest`, `NewDefaultSkewedLatest`, `NewSkewedLatest`, `IncMax`, `Max`, and `Uint64`.

Control flow and state: construction stores `max` and creates a `Zipf` over `[0, max-min]`. `Uint64` locks for reading, draws a Zipfian distance, and returns `max - distance`, so recent high values are favored. `IncMax` locks for writing, expands the underlying Zipf max by `delta`, and increments current max. `Max` reads the current max under lock.

Persistence and integration: state is in-memory and concurrency-protected. Used by `randvar.Flag` for `latest:` specs and randomized workloads. Risks include dependence on `Zipf` implementation not shown here, nil RNG handling delegated to `Zipf.Uint64`, and no direct storage of `min` beyond the initial Zipf range. Tests check max changes and range bounds after increment.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest_test.go -->
# sources/storage-engines/pebble/internal/randvar/skewed_latest_test.go

Purpose: tests and optional visualization helpers for `SkewedLatest`.

Important APIs/functions: `dumpSamples`, `TestSkewedLatest`, and `TestSkewedLatestMax`.

Control flow and state: `dumpSamples` sorts samples and prints a rough histogram using block characters during verbose runs. `TestSkewedLatest` constructs a generator over `[0,99]`, draws 10,000 samples, and optionally dumps the distribution. `TestSkewedLatestMax` verifies initial `Max`, increments by 50, verifies new max, and draws 1,000 samples asserting each lies within `[min, Max()]`.

Dependencies and integration: uses `testify/require` and `NewRand`. The tests give range and smoke coverage but do not assert skew shape statistically. Risks not covered include invalid constructor args, concurrent `IncMax` and reads, deterministic reproducibility, and nil RNG behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest_test.go -->
