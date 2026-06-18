# Research Group subset-b-008528

This grouped report covers Pebble internal delete pacing, devtools lint hooks, predicate DSL helpers, EWMA byte estimation, generic cache infrastructure, formatting and observability helpers, iterator test scaffolding, iterv2 span-aware iterators, and selected keyspan wrappers. Each section is delimited for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/delete_pacer_test.go -->
# sources/storage-engines/pebble/internal/deletepacer/delete_pacer_test.go

## Purpose
`delete_pacer_test.go` validates the asynchronous delete pacer’s externally visible pacing behavior. It focuses on datadriven simulations for basic pacing, backlog catch-up, and low-free-space acceleration, plus targeted regression tests for close-time unblocking and queue-overflow fall-behind behavior.

## Important APIs, Types, And Functions
`TestDataDriven` runs the `backlog`, `basic`, and `free-space` datadriven files under Go 1.25 `testing/synctest`. `testState` holds the open `DeletePacer`, atomically mutable baseline rate and disk free space, enqueue/delete logs, and a semaphore used to block delete execution. `executeTest` interprets commands: `del`, `sleep`, `block-deletes`, `unblock-deletes`, `baseline-rate`, and `free-space`. `plot` renders enqueue/delete timelines. `TestCloseWithPacing` and `TestFallingBehind` exercise shutdown and queue pressure.

## Control Flow
Each datadriven `run` command constructs `Options`, `diskFreeSpaceFn`, and `deleteFn`, opens a pacer, executes scripted operations, waits for synctest quiescence after each command, and returns side-by-side enqueue/delete diagrams. The close test enqueues many slow-paced files and requires `Close` to finish within 30 seconds. The falling-behind test fills the queue past `maxQueueSize` and waits for the pacer to disable pacing enough to drain below the threshold.

## State And Persistence Behavior
All state is in-memory test state. Atomic fields model mutable configuration observed by the pacer. The semaphore intentionally serializes or blocks delete callbacks. There is no durable state; testdata golden files are the persistent expectations.

## Dependencies And Integration Points
The test depends on `datadriven`, `diagram`, `crhumanize`, `synctest`, Pebble `base.FileTypeTable`, `testutils.Logger`, and the package-level `Open`, `Enqueue`, and `Close` APIs defined outside this file. It also uses `MB`, `GB`, `RecentRateWindow`, and `maxQueueSize` from the deletepacer package.

## Risks And Edge Cases
Because the tests use synthetic time, any goroutine leak or missing synctest wait can cause flaky diagrams. The plot compresses events into 100 columns and can hide small timing differences. The close test is intentionally wall-clock bounded and would become expensive if pacing were not disabled during close.

## Test Signals
Golden output confirms pacing cadence changes across baseline, backlog, and free-space scenarios. Targeted tests signal that close is prompt even with outstanding debt, and that an oversized queue drops back below `maxQueueSize`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/delete_pacer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/history.go -->
# sources/storage-engines/pebble/internal/deletepacer/history.go

## Purpose
`history.go` implements a fixed-size rolling history used by the delete pacer to track recent byte totals at coarse time granularity. It is optimized for cheap additions and approximate-window sums over a configured timeframe.

## Important APIs, Types, And Functions
`history` stores `epochDuration`, `startTime`, `currEpoch`, a 100-entry `val` ring, and a cached `sum`. `historyEpochs` is fixed at 100. `Init(now, timeframe)` configures the epoch size as `timeframe / 100`. `Add(now, val)` advances to the current epoch and increments that bucket. `Sum(now)` advances and returns the cached rolling sum. Internal helpers `epoch` and `advance` translate monotonic time to epoch indexes and discard expired buckets.

## Control Flow
Every public operation calls `advance`. `advance` increments `currEpoch` until it catches up with the epoch for `now`, subtracting and zeroing the ring bucket that becomes oldest on each step. `Add` then writes into `val[currEpoch % historyEpochs]`; `Sum` only returns `sum`.

## State And Persistence Behavior
The state is process-local and approximate. It retains at most 100 epochs and loses precision by rounding time down to epoch boundaries. It relies on `crtime.Mono`, so it is monotonic-time safe and not wall-clock persistent.

## Dependencies And Integration Points
The delete pacer uses it for recent deletion byte rate estimation, especially `RecentRateWindow`. It depends on `crtime` and `invariants.SafeSub`, which clamps underflow in production and panics in invariant builds.

## Risks And Edge Cases
If `timeframe < 100ns`, `epochDuration` can be zero and division would panic; callers are expected to use meaningful windows. Very large jumps advance one epoch at a time, so pathological time jumps cost O(number of elapsed epochs). Approximation is bounded by the 1 percent epoch granularity.

## Test Signals
Coverage is indirect through deletepacer datadriven pacing behavior and rate/backlog tests. Useful direct tests would verify bucket expiration, large time jumps, and the invariant underflow guard.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/obsolete_file.go -->
# sources/storage-engines/pebble/internal/deletepacer/obsolete_file.go

## Purpose
`obsolete_file.go` defines the delete pacer’s file descriptor type and the rule for whether a file contributes bytes to pacing.

## Important APIs, Types, And Functions
`ObsoleteFile` records `FileType`, `FS`, `Path`, `FileNum`, approximate `FileSize`, and `Placement`. Its unexported `pacingBytes` method returns `FileSize` only for local table and blob files; all other file types or non-local placements return zero.

## Control Flow
There is no asynchronous control flow in this file. Callers construct `ObsoleteFile` values and the pacer consults `pacingBytes` before adding recent history, queued bytes, and debt.

## State And Persistence Behavior
The struct describes existing filesystem objects but does not persist anything itself. `FileSize` is advisory for logs and exact enough for table/blob pacing. The actual deletion is delegated to the pacer’s delete callback and `vfs.FS`.

## Dependencies And Integration Points
It integrates with Pebble `base.FileType`, `base.DiskFileNum`, `base.Placement`, and `vfs.FS`. It is consumed by `DeletePacer.Enqueue` and the rate/debt logic in the deletepacer package.

## Risks And Edge Cases
Remote or shared-object placements are deliberately unpaced because deleting them does not reclaim local disk in the same way. If new reclaim-heavy local file types are added but not included here, the pacer will undercount deletion work. Approximate sizes can skew pacing but not correctness.

## Test Signals
The datadriven deletepacer tests use local table files, exercising the positive path. Additional targeted tests would check non-local, blob, log, and unknown file type behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/obsolete_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/options.go -->
# sources/storage-engines/pebble/internal/deletepacer/options.go

## Purpose
`options.go` defines runtime configuration for the delete pacer: the baseline deletion throughput, backlog drain horizon, and free-space reclaim threshold/horizon.

## Important APIs, Types, And Functions
`Options` exposes `BaselineRate func() uint64`, `BacklogTimeframe`, `FreeSpaceThresholdBytes`, and `FreeSpaceTimeframe`. `EnsureDefaults` installs a zero baseline function, a 5 minute backlog timeframe, a 16 GiB free-space threshold, and a 10 second free-space timeframe when fields are unset.

## Control Flow
Callers pass `Options` to `Open`, which calls `EnsureDefaults` before using them. The dynamic `BaselineRate` closure is intentionally evaluated by the rate calculator, allowing settings changes without reopening the pacer.

## State And Persistence Behavior
Options are process-local configuration. A zero baseline disables pacing. Timeframes and thresholds do not mutate after defaults are applied, but `BaselineRate` can return changing values.

## Dependencies And Integration Points
The options feed `rateCalculator.Update` and delete pacer queue scheduling. They are used directly by tests to exercise baseline changes, backlog acceleration, free-space acceleration, and close-time pacing disablement.

## Risks And Edge Cases
Zero values mean defaults except for baseline, where zero means disabled pacing. Very small timeframes can create aggressive rates; nil `BaselineRate` is safe after defaults. The defaults assume local disk reclamation semantics and may be unsuitable for unusual deployment storage.

## Test Signals
`rate_calc_test.go` validates how options influence computed rates. `delete_pacer_test.go` validates end-to-end pacing behavior with default and overridden thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/rate_calc.go -->
# sources/storage-engines/pebble/internal/deletepacer/rate_calc.go

## Purpose
`rate_calc.go` calculates the delete pacer’s target bytes/sec and pacing debt. It combines a baseline rate, recent deletion feed-forward, backlog drain pressure, and low-free-space pressure.

## Important APIs, Types, And Functions
`rateCalculator` holds options, a disk-free-space callback, `lastUpdate`, `currentRate`, `debtBytes`, `backlogRate`, and `freeSpaceRate`. `makeRateCalculator` initializes it. `Update(now, recentPacingBytes, queuedPacingBytes, disablePacing)` recalculates rate and decays debt. `AddDebt(bytes)` records bytes for a started deletion with a 1 GiB cap. `InDebt` and `DebtWaitTime` expose whether and how long to wait.

## Control Flow
`Update` first computes elapsed time and reads the baseline. If baseline is zero or pacing is disabled, all rate/debt state is cleared. Otherwise it decays debt by the previous current rate, sets the base current rate to max(baseline, recent bytes over `RecentRateWindow`), raises `backlogRate` when queued bytes exceed recent bytes, raises `freeSpaceRate` when disk free space is under threshold, and adds the larger corrective component. `DebtWaitTime` divides debt by current rate and rounds up by 1ns.

## State And Persistence Behavior
All state is in-memory and monotonic-time based. Backlog and free-space corrective rates are sticky upward until their condition clears, implementing a constant-horizon drain model. Debt represents already initiated deletion work and decays over updates.

## Dependencies And Integration Points
It depends on deletepacer `Options`, `DiskFreeSpaceFn`, `RecentRateWindow`, `crtime.Mono`, and `cockroachdb/errors`. The main delete loop calls it before deletes and after enqueue changes.

## Risks And Edge Cases
The calculator assumes callers call `Update` often enough for debt decay. `DebtWaitTime` panics on zero debt and assumes `currentRate > 0`; it should only be called after `InDebt` in paced mode. The 1 GiB debt cap intentionally trades precise pacing for avoiding excessive stalls on huge files.

## Test Signals
`rate_calc_test.go` is the direct test suite, with datadriven simulations covering baseline changes, backlog, free-space deficits, disabled pacing, debt accumulation, and wait-time formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/rate_calc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/rate_calc_test.go -->
# sources/storage-engines/pebble/internal/deletepacer/rate_calc_test.go

## Purpose
`rate_calc_test.go` provides datadriven tests for `rateCalculator`, making rate and debt transitions visible with human-readable byte/sec and byte values.

## Important APIs, Types, And Functions
`TestRateCalculatorDataDriven` runs `testdata/rate-calc`. `runSimulation` parses command arguments into `testConfig`, constructs `Options`, creates a `rateCalculator`, executes scripted lines, and writes formatted state lines. Constants `MB` and `GB` are shared with deletepacer tests.

## Control Flow
The parser supports setup arguments such as `baseline-rate`, `free-space-threshold`, `free-space-timeframe`, `backlog-timeframe`, and `disk-free-space`. Input commands mutate state (`set-baseline-rate`, `set-free-space`, `add-debt`) or call `Update` at an absolute monotonic timestamp with `recent=`, `queued=`, and optional `disable-pacing`. Output reports rounded current rate, backlog/free-space components, debt, and rounded wait time.

## State And Persistence Behavior
Test state is purely in-memory. Time is synthetic `crtime.Mono`, which makes debt decay deterministic. The datadriven file is the persistent expected behavior.

## Dependencies And Integration Points
It uses `datadriven`, `crhumanize`, `crstrings`, `crtime`, `math.Round`, and `testify/require`. It directly tests unexported deletepacer internals because it is in package `deletepacer`.

## Risks And Edge Cases
Rounding to integer bytes/sec and whole-second wait times can hide tiny numerical differences but makes golden output stable. Because command time is absolute, out-of-order timestamps would create negative elapsed time and are not explicitly rejected.

## Test Signals
The golden file detects regressions in feed-forward rate, constant-horizon backlog/free-space rate stickiness, zero-baseline pacing disablement, debt cap/decay, and wait-time calculation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/deletepacer/rate_calc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/devtools/roachvet/forbidden_imports.go -->
# sources/storage-engines/pebble/internal/devtools/roachvet/forbidden_imports.go

## Purpose
`forbidden_imports.go` defines a `go/analysis` analyzer used by Pebble’s roachvet tooling to prevent selected public/top-level packages from directly or transitively importing forbidden packages.

## Important APIs, Types, And Functions
`packagesToCheck` limits analysis to `github.com/cockroachdb/pebble`, `github.com/cockroachdb/pebble/sstable`, and `github.com/cockroachdb/pebble/cmd/pebble`. `forbiddenPackages` currently forbids `testing`. `ForbiddenImportsAnalyzer` is the exported analyzer. `checkDirectImports` reports non-test files importing forbidden packages. `checkTransitiveImports` loads package dependencies and recursively reports forbidden dependency paths. `run` gates analysis to the selected packages.

## Control Flow
The analyzer first scans AST imports for direct violations, skipping `_test.go`. It then calls `packages.Load` for the analyzed package, recursively walks imports with a visited set, skips `_test` package paths, and reports a formatted chain when it reaches a forbidden package.

## State And Persistence Behavior
The analyzer has static maps only. It does not persist state. `packages.Load` observes the module/workspace at analysis time and may perform expensive dependency loading.

## Dependencies And Integration Points
It integrates with `unitchecker` in `main.go` and Go vet-style execution. Dependencies include `go/ast`, `go/token`, `x/tools/go/analysis`, and `x/tools/go/packages`.

## Risks And Edge Cases
The comment has a typo (“dirctly”) but no behavioral impact. Transitive reports use `token.NoPos`, so diagnostics may not be anchored to import statements. Loading dependencies inside an analyzer can be expensive or sensitive to build tags. The package allowlist means internal packages can import `testing` unless they leak into checked packages.

## Test Signals
Coverage is likely through CI vet invocations. Good signals are failing diagnostics for direct `testing` imports and formatted transitive chains from checked public packages.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/devtools/roachvet/forbidden_imports.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/devtools/roachvet/main.go -->
# sources/storage-engines/pebble/internal/devtools/roachvet/main.go

## Purpose
`main.go` assembles Pebble’s custom vet binary. It wires Cockroach/Pebble-specific analyzers and configures `errcheck` exclusions before handing control to Go’s `unitchecker`.

## Important APIs, Types, And Functions
`errcheckExcludes` lists functions and methods whose returned errors are intentionally ignored. `initErrCheck` writes that list to a temporary file, configures `errcheck.Analyzer.Flags` with the `exclude` path, and returns a cleanup closure. `main` defers cleanup and calls `unitchecker.Main` with `deferloop`, `errcheck`, `nocopy`, `returnerrcheck`, and `ForbiddenImportsAnalyzer`.

## Control Flow
Startup creates a temp exclude file and panics on any setup error. `unitchecker.Main` then runs analyzers under the vet/unitchecker protocol. Deferred cleanup removes the temporary file on process exit.

## State And Persistence Behavior
The only persisted state is a temporary excludes file in the system temp directory, removed by cleanup. The analyzer set is static at binary build time.

## Dependencies And Integration Points
It depends on Cockroach lint analyzers, `kisielk/errcheck`, and `golang.org/x/tools/go/analysis/unitchecker`. This file is part of the `internal/devtools/roachvet` command and is typically invoked by build or CI scripts.

## Risks And Edge Cases
Because `errcheck` is configured through a temp file, failure to create/write/close the file panics and prevents vet from running. `errcheck.Analyzer.Flags.Set` errors are ignored; unexpected flag changes upstream would not be reported. The exclusion list must be maintained as APIs and acceptable ignored errors change.

## Test Signals
CI vet runs are the primary signal. A useful smoke test builds the command and confirms all analyzers register and errcheck accepts the generated exclusion file.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/devtools/roachvet/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/devtools/tools.go -->
# sources/storage-engines/pebble/internal/devtools/tools.go

## Purpose
`tools.go` pins tool dependencies for the `internal/devtools` module using the standard Go `tools` build-tag pattern.

## Important APIs, Types, And Functions
The file has build tag `tools` and blank imports `github.com/cockroachdb/crlfmt`, `github.com/jordanlewis/gcassert/cmd/gcassert`, and `honnef.co/go/tools/cmd/staticcheck`.

## Control Flow
There is no runtime control flow. The file is ignored in normal builds and only participates when the `tools` tag is used.

## State And Persistence Behavior
No process state is held. Its effect is on `go.mod`/`go.sum`: tool modules remain tracked as dependencies.

## Dependencies And Integration Points
It integrates with Go module dependency management and development scripts that install or run formatting, static analysis, and assertion checking tools.

## Risks And Edge Cases
Removing or renaming blank imports can silently drop tools from module metadata. Because it is in an internal devtools module, build scripts must run in the correct module context.

## Test Signals
Signals are `go mod tidy` stability and successful installation/build of the pinned tools under the `tools` tag.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/devtools/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/dsl/dsl.go -->
# sources/storage-engines/pebble/internal/dsl/dsl.go

## Purpose
`dsl.go` implements a generic parser for Pebble’s small lisp-like testing DSLs. It provides reusable scanner/parsing infrastructure for constants and parenthesized function calls.

## Important APIs, Types, And Functions
`NewParser[T]` creates a parser with constant and function registries. `NewPredicateParser[E]` creates a predicate parser preloaded with `Not`, `And`, `Or`, `OnIndex`, and `CallStackIncludes`. `Parser[T]` exposes `DefineConstant`, `DefineFunc`, `Parse`, and `ParseFromPos`. `Scanner` wraps `go/scanner.Scanner` with `Scan`, `Consume`, and `ConsumeString`. `Token` captures position, kind, and literal with a formatted `String`. `assertTok` panics on grammar mismatch.

## Control Flow
`Parse` trims input, initializes a Go scanner, parses one expression or constant through `ParseFromPos`, optionally skips one semicolon, and requires EOF. Parser errors are expressed as panics with `error` values and recovered into the returned `err`; non-error panics propagate.

## State And Persistence Behavior
Parser state is in-memory function/constant maps. Parsing produces caller-defined AST/value instances. There is no persistence, and no global registry.

## Dependencies And Integration Points
It depends on Go scanner/token packages, `strconv`, `strings`, and `cockroachdb/errors`. It is used by `internal/itertest` probe DSLs and predicate parsing in tests.

## Risks And Edge Cases
The grammar intentionally uses panics for control flow, so parse function authors must panic with `error` for user-facing parse failures. The parser accepts only constants or parenthesized calls and does not support arbitrary Go-like syntax. Duplicate definitions silently overwrite earlier map entries.

## Test Signals
Coverage is mostly indirect through `itertest` probe datadriven tests and `predicates_test.go`. Useful direct tests would cover unknown identifiers, string unquoting failures, trailing tokens, and semicolon handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/dsl/dsl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/dsl/predicates.go -->
# sources/storage-engines/pebble/internal/dsl/predicates.go

## Purpose
`predicates.go` defines reusable boolean predicate AST nodes and parse functions for the generic DSL parser.

## Important APIs, Types, And Functions
`Predicate[E]` requires `Evaluate(E) bool` and `String() string`. Constructors include `Not`, `And`, `Or`, `OnIndex`, and `CallStackIncludes`. `Index[E]` embeds `atomic.Int32` and fires only on its N-th invocation. Private implementations `not`, `and`, `or`, and `callStackIncludes` implement evaluation/stringification. Parse helpers include `parseNot`, `parseAnd`, `parseOr`, `parseOnIndex`, `parseVariadicPredicate`, and `parseCallStackIncludes`.

## Control Flow
Compound predicates evaluate children left to right, but `and` and `or` intentionally use boolean accumulation instead of short-circuiting, so every child predicate is evaluated. `OnIndex` atomically decrements and returns true when the new value is `-1`. `CallStackIncludes` captures up to 32 caller PCs and searches resolved frame function names for a substring.

## State And Persistence Behavior
Most predicates are immutable. `Index` is stateful and atomic, making repeated evaluation order significant and concurrency-safe at the counter level. No state is persisted.

## Dependencies And Integration Points
The file integrates with `NewPredicateParser` in `dsl.go` and `itertest` probe predicates. It depends on runtime stack inspection, `sync/atomic`, `go/token`, `strconv`, and `errors`.

## Risks And Edge Cases
Non-short-circuit evaluation matters for stateful predicates like `OnIndex`; this is useful for tests but can surprise callers. `CallStackIncludes` is fragile across function renames, inlining, and stack depth. `OnIndex(0)` fires on the first evaluation because decrement reaches `-1`.

## Test Signals
`predicates_test.go` validates call-stack matching. Indirect probe tests exercise parsed `And`, `Or`, `Not`, and `OnIndex` expressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/dsl/predicates.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/dsl/predicates_test.go -->
# sources/storage-engines/pebble/internal/dsl/predicates_test.go

## Purpose
`predicates_test.go` verifies the most fragile predicate: runtime call stack substring matching.

## Important APIs, Types, And Functions
`TestCallStackIncludes` calls `CallStackIncludes[string]` with a test function name, package path substring, and unrelated function substring.

## Control Flow
The test evaluates predicates immediately from within `TestCallStackIncludes`, expecting matches for `"TestCallStackIncludes"` and `"internal/dsl"` and no match for `"pebble.NewIter"`.

## State And Persistence Behavior
No test state persists. The predicate inspects the current runtime stack each time it evaluates.

## Dependencies And Integration Points
The test uses `crlib/testutils/require` and the generic predicate API. It anchors the behavior relied upon by DSL-driven test probes.

## Risks And Edge Cases
The assertions depend on function naming and path formatting in runtime frames. Heavy compiler inlining or path changes could affect the positive package-path assertion.

## Test Signals
Passing tests signal that stack frames include both function and package substrings and that unrelated substrings are not matched.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/dsl/predicates_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ewma/ewma_bytes.go -->
# sources/storage-engines/pebble/internal/ewma/ewma_bytes.go

## Purpose
`ewma_bytes.go` implements a per-byte exponential moving average estimator for values sampled over variably sized byte blocks, such as compression ratios over recently processed data.

## Important APIs, Types, And Functions
`Bytes` stores `alpha`, weighted `sum`, `totalWeight`, and deferred unsampled `gap`. `Init(halfLife)` configures alpha so samples one half-life of bytes old have half weight. `Estimate` returns `sum / totalWeight` and is NaN before sampling. `NoSample(numBytes)` advances the logical byte position without changing the value. `SampledBlock(numBytes, value)` decays prior weights by the gap plus block size and adds the new block’s weight. `decay(n)` returns `(1-alpha)^n`.

## Control Flow
Unsampled bytes accumulate in `gap` to avoid repeated decay work. When a sampled block arrives, the estimator applies one decay for `gap + numBytes`, resets the gap, computes the new block weight as `1 - decay(numBytes)`, and adds weighted value/weight.

## State And Persistence Behavior
State is in-memory and cumulative over calls. Reinitialization clears all prior samples. Negative `NoSample` or nonpositive `SampledBlock` panics only when invariants are enabled; otherwise the call is ignored.

## Dependencies And Integration Points
It depends on `math`, `cockroachdb/errors`, and `invariants`. It is a low-level internal estimator intended for byte-stream metrics elsewhere in Pebble.

## Risks And Edge Cases
`Init` should be called with a positive half-life; zero or negative values produce invalid alpha behavior. `Estimate` before any sample returns NaN by design. Numerical stability is addressed with `Expm1` and `Log1p`, important for large half-lives.

## Test Signals
`ewma_bytes_test.go` validates estimate behavior after samples/gaps and verifies half-life decay over a wide range of byte distances.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ewma/ewma_bytes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ewma/ewma_bytes_test.go -->
# sources/storage-engines/pebble/internal/ewma/ewma_bytes_test.go

## Purpose
`ewma_bytes_test.go` validates the byte-based EWMA estimator’s intuitive behavior and numeric half-life accuracy.

## Important APIs, Types, And Functions
`TestBytes` covers initialization, NaN estimate before sampling, dominance of recent samples after large gaps, averaging of adjacent small blocks, and half-life weighting. `TestBytesHalfLife` iterates half-life values from 1 byte to 1 GiB and verifies `decay(n)` at 1x through 6x half-life.

## Control Flow
The tests build a `Bytes` estimator, call `SampledBlock` and `NoSample` in scripted sequences, and compare estimates using epsilon tolerances. Half-life subtests use `t.Run` with `fmt.Sprint(n)`.

## State And Persistence Behavior
All test state is local. `Init` is tested as a state reset. No persistent files or external resources are used.

## Dependencies And Integration Points
It depends on Go `math`, `testing`, `fmt`, and `testify/require`. It directly accesses unexported `decay` because the test is in package `ewma`.

## Risks And Edge Cases
The epsilon in `TestBytes` is intentionally loose for intuitive estimates, while the decay test uses tighter tolerance. It does not test invalid half-life or invalid sample sizes.

## Test Signals
Passing tests signal that the estimator handles large gaps without changing stale-only estimates, shifts strongly toward recent samples after decay, and preserves half-life math across very large byte windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ewma/ewma_bytes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/cache.go -->
# sources/storage-engines/pebble/internal/genericcache/cache.go

## Purpose
`cache.go` provides the public API for a generic sharded CLOCK-Pro cache with reference-counted values initialized on demand and released on eviction.

## Important APIs, Types, And Functions
`Cache[K,V,InitOpts]` owns shards. `Key` requires comparability and `Shard(numShards) int`. `InitValueFn` initializes a value and receives its `ValueRef`; `ReleaseValueFn` releases a value. `New`, `Init`, `Close`, `FindOrCreate`, `Evict`, `EvictAll`, and `Metrics` are the public methods. `ValueRef` exposes `Value` and `Unref`. `Metrics` reports size, count, hits, and misses.

## Control Flow
`Init` divides capacity across shards and starts each shard’s release loop. `FindOrCreate` routes by key shard, asks the shard for a value, converts initialization errors into returned errors, and returns a reference that callers must unref. `Evict` and `EvictAll` delegate to shards. `Close` closes every shard and requires no outstanding references.

## State And Persistence Behavior
The cache is fully in-memory. Values persist until evicted and no references remain. Metrics are approximate byte accounting based on `unsafe.Sizeof` for metadata and stored `value[V]` objects; caller-owned pointees are not included.

## Dependencies And Integration Points
It depends on `context`, `unsafe`, `errors`, and `invariants`. Integration points are internal Pebble components needing typed caches without duplicating CLOCK-Pro logic.

## Risks And Edge Cases
The caller must always call `Unref`; leaks prevent release. `Evict`, `EvictAll`, and `Close` panic if references remain. `Key.Shard` must return a valid shard index or the cache will panic. Initialization may run concurrently for the same key if eviction races with creation.

## Test Signals
`cache_test.go` covers basic creation, CLOCK-Pro hit/miss behavior, eviction release, outstanding-reference panics, initialization errors, and context cancellation while waiting on another initializer.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/cache_test.go -->
# sources/storage-engines/pebble/internal/genericcache/cache_test.go

## Purpose
`cache_test.go` exercises the generic cache API, CLOCK-Pro policy compatibility, eviction semantics, error handling, and cancellation behavior.

## Important APIs, Types, And Functions
`intKey` implements `Key` with randomized shard distribution for small keys. `TestBasic` validates repeated lookups and miss counts. `TestClockPro` reuses block-cache testdata to compare hit/miss behavior. `TestEvict` verifies explicit eviction and release lists. `TestEvictPanic` confirms outstanding references panic. `TestErrorHandling` tests failed initialization retry. `TestContextCancellation` checks waiting callers can cancel while another goroutine initializes.

## Control Flow
Tests construct caches with simple init/release callbacks, call `FindOrCreate`, inspect values, and unref. The clock-pro test scans `../cache/testdata/cache`, comparing actual hit increments to expected `h`/miss markers. Cancellation test blocks the first initializer and issues canceled/deadline contexts for concurrent waiters.

## State And Persistence Behavior
State is in-memory except the shared hit/miss testdata file. Release callbacks mutate values or append to slices so tests can observe cleanup.

## Dependencies And Integration Points
It depends on `context`, `sync`, `atomic`, `rand/v2`, `testutils.CheckErr`, `testify/require`, and the older block cache’s golden access trace.

## Risks And Edge Cases
The random shard count/distribution increases coverage but can make debugging order-sensitive release lists harder, so tests sort expected slices. The clock-pro test requires a single shard and capacity 200 to match existing golden expectations.

## Test Signals
Passing tests signal stable cache hits, retry after failed initialization, synchronous release on explicit eviction, panic-on-leaked-reference enforcement, and correct context cancellation for waiters without poisoning the eventually successful value.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/node.go -->
# sources/storage-engines/pebble/internal/genericcache/node.go

## Purpose
`node.go` defines the internal linked-list node and value holder used by the generic CLOCK-Pro cache.

## Important APIs, Types, And Functions
`node[K,V]` stores a key, optional `*value[V]`, intrusive `next`/`prev` links, `status`, and an atomic `referenced` bit. `nodeStatus` has `test`, `cold`, and `hot` states with a `String` method. `next`, `prev`, `link`, and `unlink` manage circular list links. `value[V]` stores initialized value/error, an `initialized` channel, and an atomic refcount.

## Control Flow
Nodes move among test/cold/hot states under shard locks. `link` inserts a node before a sentinel/current node; `unlink` removes it and self-links it. Values are published by closing `initialized`, allowing concurrent waiters and the release loop to synchronize.

## State And Persistence Behavior
All state is in-memory. Test nodes may retain keys without values as CLOCK-Pro ghost entries. Values remain alive while their refcount is nonzero and are released when evicted and unreferenced.

## Dependencies And Integration Points
This file is consumed by `shard.go` and measured by `cache.go` metrics. It depends only on `sync/atomic`.

## Risks And Edge Cases
Intrusive circular-list manipulation assumes callers maintain non-nil links and shard locking. A node’s `value` can be nil for test entries, so callers must distinguish cache ghosts from live objects. The `initialized` channel is essential; release before initialization would otherwise race.

## Test Signals
Node behavior is tested indirectly through cache policy, eviction, release, and error/cancellation tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/shard.go -->
# sources/storage-engines/pebble/internal/genericcache/shard.go

## Purpose
`shard.go` implements the cache’s per-shard CLOCK-Pro algorithm, concurrency control, initialization synchronization, eviction, and asynchronous release loop.

## Important APIs, Types, And Functions
`shard` holds hit/miss counters, capacity, locked node map and CLOCK hands, release channel/waitgroup, and init/release callbacks. Key methods include `Init`, `releaseLoop`, `UnrefValue`, `findOrCreateValue`, `addNode`, `evictNodes`, `runHandCold`, `runHandHot`, `runHandTest`, `Evict`, `EvictAll`, `forAllNodesLocked`, and `Close`.

## Control Flow
`findOrCreateValue` uses a read-lock fast path for initialized or initializing hits, waits with context cancellation if needed, and falls back to a write-lock miss path. New misses create cold nodes or resurrect test nodes as hot, create a `value` with two references, unlock, and call `initValueFn`. Failed initialization unlinks and clears the node. CLOCK hands demote hot entries, clear cold unreferenced entries into test ghosts, and prune excess test entries. Release runs asynchronously once refcount reaches zero, waiting for initialization first.

## State And Persistence Behavior
Shard state is in-memory. Live values are held by shard and caller references; ghost test nodes retain keys but no value. `Close` drains nodes, closes the release channel, and waits for all pending releases.

## Dependencies And Integration Points
It depends on `context`, `sync`, `atomic`, `errors`, and `invariants`. It backs all public `Cache` operations.

## Risks And Edge Cases
Outstanding references during `Evict` or `Close` panic. Initialization errors must close `initialized`; waiters rely on that channel. Context-canceled waiters receive synthetic initialized error values and unref the shared value. `EvictAll` requires no matching keys be inserted concurrently and checks that in invariant builds.

## Test Signals
`cache_test.go` directly stresses initialization, concurrent waiters, explicit eviction, close, and policy hit/miss behavior. Race testing is valuable because locks, atomics, and release goroutines interact closely.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/genericcache/shard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/humanize/humanize.go -->
# sources/storage-engines/pebble/internal/humanize/humanize.go

## Purpose
`humanize.go` formats byte and count values into compact human-readable strings that are considered redaction-safe.

## Important APIs, Types, And Functions
`config` stores a numeric base and suffix list. Package variables `Bytes` and `Count` configure IEC-like byte formatting and SI count formatting. `Int64` and `Uint64` format signed/unsigned values. `FormattedString` implements `fmt.Stringer` and `redact.SafeValue`. Helpers `logn` and `humanate` choose suffixes and one-decimal formatting.

## Control Flow
Values below 10 use the base suffix directly. Larger values compute an exponent from logarithms, scale and round to one decimal, and suppress decimals when the rounded value is at least 10. Negative signed values are formatted with a leading minus.

## State And Persistence Behavior
All configuration is immutable package state. No persistence or caching is involved.

## Dependencies And Integration Points
It depends on `fmt`, `math`, and Cockroach `redact`. It is used wherever Pebble logs or displays compact sizes/counts and wants redaction-safe markers.

## Risks And Edge Cases
The suffix arrays cap at exabytes/exa; values beyond the highest suffix can index past the suffix list. Rounding can produce boundary-looking values, such as `1023KB` vs `1.0MB`, based on the exponent chosen before rounding.

## Test Signals
`humanize_test.go` uses datadriven input to verify bytes/count formatting across representative values, including signed values.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/humanize/humanize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/humanize/humanize_test.go -->
# sources/storage-engines/pebble/internal/humanize/humanize_test.go

## Purpose
`humanize_test.go` validates compact formatting for byte and count values against datadriven golden output.

## Important APIs, Types, And Functions
`TestHumanize` dispatches datadriven commands `bytes` and `count`, parses each input line as an `int64`, and writes `config.Int64` output.

## Control Flow
The test chooses `Bytes` or `Count` by command, iterates input rows using `crstrings.LinesSeq`, parses decimal integers, and appends one formatted line per input.

## State And Persistence Behavior
The persistent behavior contract lives in `testdata/humanize`. No runtime state persists.

## Dependencies And Integration Points
It uses `datadriven`, `crstrings`, `bytes.Buffer`, `strconv`, and `fmt`. It directly exercises package-level formatting configs.

## Risks And Edge Cases
The test only covers values present in the golden file. It does not explicitly test `Uint64`, redaction interface behavior, or overflow beyond suffix arrays.

## Test Signals
Passing datadriven output signals stable suffix choice, rounding, negative formatting, and byte/count base differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/humanize/humanize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/inflight/in_flight.go -->
# sources/storage-engines/pebble/internal/inflight/in_flight.go

## Purpose
`in_flight.go` implements a low-overhead tracker for long-running operations. Callers start and stop handles around work, and reports identify operations older than a threshold grouped by caller stack.

## Important APIs, Types, And Functions
`Tracker` owns sharded `xsync.MapOf[Handle, entry]` maps, padded handle counters, and optional polling timer state. `Handle` is an opaque nonzero token. Public APIs include `NewTracker`, `NewPollingTracker`, `Close`, `Start`, `Stop`, and `Report`. `olderThan` yields entries before a cutoff. Internal `entry` stores monotonic start time and a seven-frame `stack`.

## Control Flow
`Start` captures monotonic time and caller PCs, selects a CPU-biased shard, generates a handle with shard index in the high byte, and stores the entry. `Stop` deletes from the shard encoded in the handle. `Report` scans all shards for old entries, groups by stack, keeps occurrence count and oldest start, sorts groups by age, and formats resolved frames. `NewPollingTracker` schedules a timer that periodically reports non-empty summaries and resets itself until `Close`.

## State And Persistence Behavior
All state is in-memory and concurrency-safe. Handles are unique per shard counter until wraparound. Reports are ephemeral strings; polling invokes a caller-supplied function but does not persist.

## Dependencies And Integration Points
It depends on `crsync` shard helpers, `crtime.Mono`, `xsync`, `runtime`, Go 1.23 `iter`, maps/slices helpers, atomics, and timers. It is intended for subsystems that need lightweight stuck-operation diagnostics.

## Risks And Edge Cases
Stopping a zero handle indexes shard 0 after shifting and is not guarded; callers should use valid handles. `runtime.Callers` depth and inlining affect grouping. `Close` stops future polling but `Start`, `Stop`, and `Report` remain usable.

## Test Signals
`in_flight_test.go` checks basic report thresholding and polling timer behavior under synctest. `in_flight_bench_test.go` measures Start/Stop overhead across parallelism.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/inflight/in_flight.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/inflight/in_flight_bench_test.go -->
# sources/storage-engines/pebble/internal/inflight/in_flight_bench_test.go

## Purpose
`in_flight_bench_test.go` benchmarks the common `Tracker.Start`/`Stop` path under different levels of parallelism.

## Important APIs, Types, And Functions
`BenchmarkTracker` reads `GOMAXPROCS`, runs subbenchmarks for parallelism 1, half-procs, procs, and double-procs, and batches operations through a channel to worker goroutines.

## Control Flow
For each subbenchmark, workers consume batch sizes from a buffered channel, repeatedly call `Start` and `Stop`, and the driver feeds enough batches to perform `b.N * parallelism` operations before waiting on a `sync.WaitGroup`.

## State And Persistence Behavior
Only benchmark-local tracker state is used. No persistent output is produced beyond Go benchmark metrics.

## Dependencies And Integration Points
It depends on `runtime`, `sync`, `fmt`, and `testing`. It is useful for comparing vanilla Go and Cockroach runtime overhead as described in the comment.

## Risks And Edge Cases
The benchmark multiplies operations by parallelism, so interpretation of `ns/op` should consider the benchmark’s custom workload shape. Channel batching reduces channel overhead but still includes some scheduling effects.

## Test Signals
Benchmark output signals contention and per-operation overhead of handle generation, stack capture, map store, and delete under varying concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/inflight/in_flight_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/inflight/in_flight_test.go -->
# sources/storage-engines/pebble/internal/inflight/in_flight_test.go

## Purpose
`in_flight_test.go` verifies tracker reporting semantics and polling lifecycle behavior.

## Important APIs, Types, And Functions
`TestTrackerBasic` checks direct `Report` calls around one started operation. `TestPollingTracker` uses `testing/synctest` and an atomic value to observe reports from `NewPollingTracker`.

## Control Flow
The basic test starts a handle, waits past a millisecond threshold, expects non-empty report output, then stops the handle and expects empty output. The polling test advances synthetic time, checks no report before any operation, starts an operation, waits past max age, observes a report, stops it, and verifies no further reports after `Close`.

## State And Persistence Behavior
All state is test-local. Synctest controls time and goroutine scheduling deterministically. No files are used.

## Dependencies And Integration Points
It depends on Go 1.25 `testing/synctest`, `sync/atomic`, `time`, and `testify/require`. It directly tests public `inflight` APIs.

## Risks And Edge Cases
The tests assert report non-emptiness rather than exact stack output, avoiding path and timing brittleness. They do not test duplicate stack grouping or multiple shards directly.

## Test Signals
Passing tests signal threshold filtering, stop removal, periodic reporting, and `Close` suppression of future timer callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/inflight/in_flight_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/intern/intern.go -->
# sources/storage-engines/pebble/internal/intern/intern.go

## Purpose
`intern.go` provides a tiny byte-slice-to-string interning helper intended to avoid repeated allocations for repeated byte content.

## Important APIs, Types, And Functions
Package-level `pool` is a `sync.Pool` of `map[string]string`. `Bytes(b []byte) string` looks up the string content in a pooled map, returns the existing interned string if present, otherwise allocates a string, stores it as both key and value, and returns it.

## Control Flow
`Bytes` gets one map from the pool, performs lookup by `string(b)`, puts the map back before returning, and either reuses an existing canonical string or stores a new one.

## State And Persistence Behavior
Intern maps live in `sync.Pool`, so state is process-local and opportunistically retained; GC may drop pool entries. Interning is not global or durable and may return different backing strings after pool churn.

## Dependencies And Integration Points
It depends only on `sync`. It is useful in paths repeatedly converting equal byte slices to strings where a pooled map can amortize allocations.

## Risks And Edge Cases
The `string(b)` lookup conversion can allocate if the key is absent; the optimization relies on compiler/runtime behavior and pooled map reuse. Under the race detector `sync.Pool` behavior changes enough that allocation tests skip. The maps can grow over time while retained in the pool.

## Test Signals
`intern_test.go` checks zero allocations for repeated `abc` slices outside race builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/intern/intern.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/intern/intern_test.go -->
# sources/storage-engines/pebble/internal/intern/intern_test.go

## Purpose
`intern_test.go` verifies the allocation behavior expected from `intern.Bytes`.

## Important APIs, Types, And Functions
`TestBytes` constructs repeated `abc` byte slices, calls `Bytes` in a loop inside `testing.AllocsPerRun`, and fails if any allocations are observed. It skips when `buildtags.Race` is true.

## Control Flow
The test builds a repeated byte buffer and repeatedly interns 100 adjacent slices. The first warmup behavior of `AllocsPerRun` lets the pool/map become populated before allocation measurement.

## State And Persistence Behavior
The test relies on `sync.Pool` retaining a map during the run, but there is no persistent state. It explicitly avoids race builds because `sync.Pool` is effectively disabled there.

## Dependencies And Integration Points
It depends on `bytes`, `testing`, and Pebble `buildtags`. It directly measures the public `Bytes` helper.

## Risks And Edge Cases
Allocation counts are sensitive to compiler/runtime changes in string conversion and sync.Pool behavior. The test covers repeated equal short strings, not map growth or unique-string workloads.

## Test Signals
Passing outside race builds signals that repeated interning of known content is allocation-free in the intended runtime configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/intern/intern_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/invalidating/iter.go -->
# sources/storage-engines/pebble/internal/invalidating/iter.go

## Purpose
`invalidating/iter.go` wraps `base.InternalIterator` implementations to catch callers that incorrectly retain returned key/value buffers after subsequent iterator movement.

## Important APIs, Types, And Functions
`MaybeWrapIfInvariants` randomly wraps iterators in invariant builds. `Option` and `IgnoreKinds` configure key kinds whose buffers should not be trashed. `NewIter` returns a `base.TopLevelIterator` wrapper. The private `iter` implements the internal iterator methods, copying returned `InternalKV`s in `update` and trashing the previous copy in `trashLastKV`.

## Control Flow
Every positioning method delegates to the wrapped iterator and passes the result to `update`. `update` trashes the prior copy, clones key and lazy value/fetcher state for the new result, and returns the copy. On nil results, it clears `lastKV`. Non-positioning methods mostly delegate.

## State And Persistence Behavior
Wrapper state is in-memory: the underlying iterator, last copied KV, ignored key-kind mask, and an unused local `err` field. The wrapper intentionally mutates prior returned copies to expose unsafe retention bugs.

## Dependencies And Integration Points
It depends on `base`, `invariants`, `treesteps`, `context`, and `slices`. It is used in tests and invariant builds around point iterators, including iterv2 random tests.

## Risks And Edge Cases
`SeekPrefixGEStrict` delegates to `SeekPrefixGE`, matching the underlying interface but not adding different behavior. Ignored key kinds can hide reuse issues for those kinds by design. The wrapper copies visible lazy fetcher fields by assignment and then zeroes on trash.

## Test Signals
Coverage is indirect through invariant/random iterator tests. Bugs surface as corrupted retained keys/values when callers retain slices across operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/invalidating/iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/invariants/invariants.go -->
# sources/storage-engines/pebble/internal/invariants/invariants.go

## Purpose
`invariants.go` centralizes build-tag-controlled invariant flags and finalizer handling for Pebble.

## Important APIs, Types, And Functions
`Enabled` is true for `race` or `invariants` builds. `RaceEnabled` mirrors the race build tag. `UseFinalizers` is true for invariant or tracing builds except race. `SetFinalizer(obj, finalizer)` wraps `runtime.SetFinalizer` and no-ops when `UseFinalizers` is false.

## Control Flow
All values are compile-time constants from `internal/buildtags`. `SetFinalizer` checks `UseFinalizers` at runtime and delegates to `runtime.SetFinalizer` only when enabled.

## State And Persistence Behavior
No persistent state is stored. The effect is compile-time/runtime gating of expensive assertions and finalizer-based lifecycle checks.

## Dependencies And Integration Points
It depends on `runtime` and `buildtags`. Other packages use `invariants.Enabled`, `Sometimes`, `CloseChecker`, `Value`, `SafeSub`, and finalizer helpers from this package.

## Risks And Edge Cases
Comments warn not to substantially change production paths solely under `Enabled`; randomized `Sometimes` wrapping is preferred so production paths still receive coverage. Finalizers are deliberately disabled under race due to historical detector issues.

## Test Signals
Signals are build-tag matrix tests: normal builds should compile away invariant-only behavior, while race/invariant builds should activate checks without finalizer races.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/invariants/invariants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/invariants/off.go -->
# sources/storage-engines/pebble/internal/invariants/off.go

## Purpose
`off.go` provides no-op implementations of invariant helpers for normal builds without `invariants` or `race` tags.

## Important APIs, Types, And Functions
`Sometimes` always returns false. `CloseChecker` has no-op `Close`, `AssertClosed`, and `AssertNotClosed`. Generic `Value[V]` stores nothing; `MakeValue`, `Get`, and `Set` no-op or return zero values. `MaybeMangle`, `Mangle`, and `BufMangler.MaybeMangleLater` do nothing. `CheckBounds` no-ops. `SafeSub` returns zero on underflow instead of panicking. `Integer` defines supported integer constraints.

## Control Flow
All functions are constant or no-op. This allows invariant calls to remain in production code with near-zero behavior.

## State And Persistence Behavior
No invariant state is stored in normal builds. Zero-sized structs can still influence parent struct layout when placed last, as comments note.

## Dependencies And Integration Points
The file has build tag `!invariants && !race`. It imports `errors` only blankly to keep API symmetry or dependency expectations.

## Risks And Edge Cases
`SafeSub` silently clamps underflow to zero in production, so callers must not rely on panic behavior outside invariant builds. Zero-sized fields can affect addressability/layout in subtle ways.

## Test Signals
Normal-build tests should show no invariant panics and should verify code remains correct when invariant helpers do not enforce checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/invariants/off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/invariants/on.go -->
# sources/storage-engines/pebble/internal/invariants/on.go

## Purpose
`on.go` provides active invariant helper implementations for `invariants` or `race` builds.

## Important APIs, Types, And Functions
`Sometimes(percent)` randomly returns true. `CloseChecker` tracks a `closed` bool and panics on double close, missing close, or use-after-close assertions. `Value[V]` stores and returns an invariant-only value. `MaybeMangle`, `Mangle`, and `BufMangler.MaybeMangleLater` corrupt buffers to detect unsafe retention. `CheckBounds` panics on out-of-range indexes. `SafeSub` panics on underflow. `Integer` mirrors the production constraint.

## Control Flow
Invariant helpers panic through `errors.AssertionFailedf` when violations occur. `BufMangler.MaybeMangleLater` mangles the previously returned cloned buffer on the next call and randomly chooses whether to return a clone or original for the current call.

## State And Persistence Behavior
State is in-memory and exists only in invariant/race builds. Random decisions are process-local via `math/rand/v2`.

## Dependencies And Integration Points
It depends on `math/rand/v2`, `slices`, and `errors`. It is used broadly in iterator wrappers, cache lifecycle checks, arithmetic guards, and bounds checks.

## Risks And Edge Cases
Randomized behavior means invariant failures may be probabilistic; seed capture in higher-level tests is important. `CloseChecker` is not synchronized, so callers using it concurrently need external synchronization. Mangle helpers intentionally destroy buffers and must only be used where this is expected.

## Test Signals
Invariant/race build runs should catch unsafe buffer reuse, double close, arithmetic underflow, and bounds violations that normal builds tolerate or no-op.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/invariants/on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/datadriven.go -->
# sources/storage-engines/pebble/internal/itertest/datadriven.go

## Purpose
`itertest/datadriven.go` supplies reusable datadriven command execution for `base.InternalIterator` tests, converting textual commands into iterator operations and formatted output.

## Important APIs, Types, And Functions
`IterOpt` configures `iterCmdOpts`. Options include `Condensed`, `ShowCommands`, `Verbose`, `WithSpan`, and `WithStats`. Formatting helpers are `defaultFormatKV`, `condensedFormatKV`, and `verboseFormatKV`. `RunInternalIterCmd` returns output as a string; `RunInternalIterCmdWriter` writes to an `io.Writer`.

## Control Flow
The runner parses each input line, dispatches commands like `seek-ge`, `seek-prefix-ge`, `seek-lt`, `first`, `last`, `next`, `next-prefix`, `prev`, `set-bounds`, `stats`, `reset-stats`, `is-lower-bound`, and `print`, then formats the returned key/value or error. It tracks the current prefix and previous key to compute `NextPrefix` successor keys.

## State And Persistence Behavior
State is local to one command run: prefix, previous key, formatting options, and optional stats pointer. It mutates the supplied iterator and optional stats but stores no persistent data.

## Dependencies And Integration Points
It depends on `datadriven`, Pebble `base`, `keyspan`, `testkeys`, `blockkind`, `crstrings`, and `testify/require`. Many Pebble iterator tests use it as a common command language.

## Risks And Edge Cases
The command parser assumes non-empty lines and simple whitespace-separated arguments. `next-prefix` requires a previous key and will panic if used after nil. Stats output zeroes nondeterministic timing for stable golden files.

## Test Signals
Stable datadriven outputs across iterator implementations signal consistent seek/next/bounds semantics and error reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/datadriven.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/dsl.go -->
# sources/storage-engines/pebble/internal/itertest/dsl.go

## Purpose
`itertest/dsl.go` defines the DSL used to configure iterator probes that can inject errors, replace returned keys, log operations, or conditionally apply behavior.

## Important APIs, Types, And Functions
`Predicate` aliases `dsl.Predicate[*ProbeContext]`. `NewParser` creates a probe parser and nested predicate parser with operation constants plus `UserKey`. Probe constants/functions include `ErrInjected`, `noop`, `Nil`, `If`, `ReturnKV`, and `Log`. `ErrorProbe`, `ifProbe`, `loggingProbe`, `UserKey`, `returnKV`, and `returnNil` implement the probe/predicate behaviors.

## Control Flow
DSL parsing composes probe wrappers. `If` evaluates its predicate against `ProbeContext` and runs either branch. `ErrorProbe` sets `Return.Err` and clears `Return.KV`. `ReturnKV` replaces the returned KV. `Log` writes operation name, seek key, result, and error into the probe state log.

## State And Persistence Behavior
Probe state is primarily in parser-created values and the shared `ProbeContext`. `OnIndex` predicates from the generic DSL can be stateful. Logs are written to caller-supplied writers; no files are written here.

## Dependencies And Integration Points
It depends on `base`, generic `dsl`, `errorfs.ErrInjected`, Go `token`, and string formatting. It integrates with `probe.go` wrappers and datadriven probe tests.

## Risks And Edge Cases
`ReturnKV` stores a pointer to a parsed KV, so repeated uses return the same object. `Log` panics if value materialization fails. Stack/predicate composition inherits generic DSL panic-on-parse-error behavior.

## Test Signals
`probe_test.go` and `testdata/probes` validate parsing, conditional behavior, error injection, nil returns, return replacement, and logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/dsl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/probe.go -->
# sources/storage-engines/pebble/internal/itertest/probe.go

## Purpose
`probe.go` implements the iterator-probe wrapper that lets tests observe and modify every `base.InternalIterator` operation.

## Important APIs, Types, And Functions
`OpKind` enumerates seek, movement, and close operations and implements predicate evaluation. `Op` describes an operation, seek key, and mutable return KV/error. `Probe` is the injection interface. `ProbeContext` combines `Op` and `ProbeState`, which holds a comparer and log writer. `Attach` wraps iterators with one or more probes. `MustParseProbes` parses DSL strings. `probeIterator` implements `base.InternalIterator`.

## Control Flow
Every positioning method builds an `Op`, delegates to the inner iterator if present, and calls `handleOp`, which populates errors from `iter.Error` for nil results and invokes the probe. `Close` handles the direct close error separately because close does not return a KV. Bounds/context/tree-step/string operations delegate.

## State And Persistence Behavior
`probeIterator` stores the wrapped iterator, one probe, and reusable probe context. Probe modifications persist in `probeCtx.Op.Return.Err` until overwritten by later operations, which is also what `Error()` returns.

## Dependencies And Integration Points
It depends on `base`, `dsl`, `treesteps`, `context`, `io`, and formatting. It is used by itertest probe DSL tests and can wrap nil iterators for pure probe behavior.

## Risks And Edge Cases
Because `Error()` returns probe context error, injected errors can outlive a single operation until another operation updates context. Wrapping multiple probes nests iterators; ordering is the order supplied to `Attach`. Nil inner iterators are supported but only probes provide results.

## Test Signals
`probe_test.go` exercises DSL-attached nil iterators through common iterator commands, checking logged/injected behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/probe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/probe_test.go -->
# sources/storage-engines/pebble/internal/itertest/probe_test.go

## Purpose
`probe_test.go` validates the itertest probe DSL and wrapper behavior through datadriven commands.

## Important APIs, Types, And Functions
`TestProbes` creates a parser and mutable `base.InternalIterator` variable. The `new` command parses each input line as a probe and attaches it around the current iterator. The `iter` command runs `RunInternalIterCmd` in verbose mode.

## Control Flow
The test resets the iterator to nil on `new`, attaches probes line by line with a `ProbeState` containing `testkeys.Comparer`, and then drives the resulting wrapper with iterator commands from `testdata/probes`.

## State And Persistence Behavior
State is the current probe-wrapped iterator and a `strings.Builder` that is reset per command. Persistent expectations live in datadriven testdata.

## Dependencies And Integration Points
It depends on `datadriven`, `crstrings`, Pebble `base`, `testkeys`, and the probe/parser helpers in the same package.

## Risks And Edge Cases
Parse errors are returned as command output rather than failing the test immediately, enabling negative golden cases. Starting from nil iterators means many behaviors are probe-driven rather than underlying-iterator-driven.

## Test Signals
Golden outputs confirm parsing, conditional predicates, operation constants, injected errors, nil results, replacement KVs, and verbose command formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/itertest/probe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/interleaving_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/interleaving_iter.go

## Purpose
`interleaving_iter.go` implements `iterv2.Iter` by combining a point `base.InternalIterator` with a `keyspan.FragmentIterator`, emitting point keys and synthetic span-boundary keys while exposing the current span.

## Important APIs, Types, And Functions
`InterleavingIter` stores comparers, point/span iterators, static range bounds, dynamic bounds, cached point/span positions, direction flags, boundary state, presented `Span`, prefix mode, error, and scratch buffer. Public methods include `Init`, `Span`, `InvalidateCachedSpan`, all internal iterator positioning methods, `SetBounds`, `Error`, `Close`, `SetContext`, `String`, and `TreeStepsNode`. Core helpers include `computeCurrentSpan`, `emitBoundary`, `positionSpanIterForward`, `positionSpanIterBackward`, `resolveForward`, `resolveBackward`, boundary update helpers, direction switch helpers, and invariant checks.

## Control Flow
Forward seeks position the point iterator, position or reuse the span iterator around the seek key, compute the presented span, and return whichever comes first: point key or boundary. `Next` advances point state or, after a boundary, enters the adjacent span/gap and recomputes. Reverse flow mirrors this with span starts. Direction switches reseek/advance to match internal iterator semantics. Prefix seeks restrict point results while still exposing the first relevant boundary needed to discover covering spans.

## State And Persistence Behavior
State is in-memory iterator position only. `presentedSpan` points into current span keys and is invalidated on exhaustion. `InvalidateCachedSpan` is an explicit escape hatch when the underlying span iterator has been reinitialized.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `invariants`, `treesteps`, `crstrings`, and `errors`. It is a central implementation of the span-aware iterator contract documented in `iter.go` and is used by merging/level iterator work.

## Risks And Edge Cases
Boundary ordering with point keys at the same user key is subtle. Prefix iteration must not hide range deletion spans that cover the prefix. Dynamic bounds forbid `First`/`Last` in invariant builds. `TrySeekUsingNext` reuse of span state must not reuse a span past its end.

## Test Signals
Datadriven tests in `interleaving_iter_test.go` cover scripted examples, while `interleaving_iter_rand_test.go` compares random operations against `TestIter` through `CheckIter`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/interleaving_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/interleaving_iter_rand_test.go -->
# sources/storage-engines/pebble/internal/iterv2/interleaving_iter_rand_test.go

## Purpose
`interleaving_iter_rand_test.go` performs randomized differential testing of `InterleavingIter` against the reference `TestIter`.

## Important APIs, Types, And Functions
`TestInterleavingIterRandom` runs 200 random seeds. `runRandomTest` builds random key configs, point keys, non-overlapping spans, optional static start/end bounds, dynamic lower/upper bounds, invalidating wrappers, and an `InterleavingIter`, then calls `CheckIter`.

## Control Flow
For each seed, the test randomly chooses key generation parameters, points/spans, static bounds, dynamic bounds, optional point invalidation, optional nil/invalidating span iterator, initializes the iterator, and runs 500 random operations through `CheckIter`. On failure, deferred logging emits the seed and generated data.

## State And Persistence Behavior
All state is local to a seed. Seeds are logged for reproduction. No golden files are used.

## Dependencies And Integration Points
It depends on `math/rand/v2`, `base`, `invalidating`, `keyspan`, `testkeys`, and the iterv2 random test utilities.

## Risks And Edge Cases
Random coverage is probabilistic and may miss rare arrangements, but seed logging makes failures reproducible. Invalidating wrappers increase sensitivity to unsafe buffer retention.

## Test Signals
Passing random runs signal agreement with the reference model over mixed seeks, movement, prefix mode, bounds, direction switches, spurious nil span iterators, and boundary emission.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/interleaving_iter_rand_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/interleaving_iter_test.go -->
# sources/storage-engines/pebble/internal/iterv2/interleaving_iter_test.go

## Purpose
`interleaving_iter_test.go` provides datadriven, human-readable coverage for `InterleavingIter` behavior.

## Important APIs, Types, And Functions
`TestInterleavingIter` supports `define-points`, `define-spans`, and `iter` commands. It parses point `InternalKey`s, parses `keyspan.Span`s, creates `base.NewFakeIter` and `keyspan.NewIter`, initializes `InterleavingIter`, and runs `RunIterOps`.

## Control Flow
The datadriven file first defines point and span fixtures, then executes iterator command scripts with optional `start`, `end`, `lower`, and `upper` arguments. Output includes returned keys and current spans.

## State And Persistence Behavior
The current points/spans and iterator live in the test closure. Golden behavior persists in `testdata/interleaving_iter`.

## Dependencies And Integration Points
It depends on `datadriven`, `crstrings`, Pebble `base`, `keyspan`, `testkeys`, and `RunIterOps`.

## Risks And Edge Cases
Datadriven tests cover explicit scenarios but not the full state space; the random test complements them. Shared testdata is also used by `TestIter`, so expected output changes can affect multiple suites.

## Test Signals
Golden output signals correct ordering of point and boundary keys, span display, static/dynamic bounds, prefix seeks, and direction changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/interleaving_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/invalidating_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/invalidating_iter.go

## Purpose
`invalidating_iter.go` wraps an `iterv2.Iter` to detect unsafe retention of returned key/value/span buffers by cloning results and corrupting previous clones on subsequent operations.

## Important APIs, Types, And Functions
`InvalidatingIter` stores the inner `Iter`, the last copied `InternalKV`, and a copied `Span`. `NewInvalidating` constructs the wrapper. `MaybeWrapInInvalidating` randomly wraps in invariant builds. `update` copies the inner result and span. `trashLast` corrupts previous key/value and span boundary/key buffers. The wrapper implements all `Iter` methods by delegation through `update` where appropriate.

## Control Flow
Every positioning method calls the inner iterator, then `update`. `update` first trashes prior copies, then deep-copies the current span boundary, span keys, suffixes, values, key, lazy value, and lazy fetcher. Nil results clear `lastKV` but still copy the inner span state.

## State And Persistence Behavior
All state is wrapper-local. Trashed copies are intentionally invalidated; callers must not depend on data after moving the iterator.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `invariants`, `treesteps`, `context`, and `slices`. It is used in randomized iterv2 tests and invariant builds.

## Risks And Edge Cases
Because `Span` returns a stable pointer to the wrapper’s copied span, callers stashing that pointer will see it mutated/trash-updated on later operations, matching iterator contract expectations. It does not alter errors or close behavior.

## Test Signals
Indirect tests wrap iterators randomly and compare behavior; failures usually indicate retained slices or incomplete deep-copy/trash coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/invalidating_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/iter.go -->
# sources/storage-engines/pebble/internal/iterv2/iter.go

## Purpose
`iter.go` defines the `iterv2.Iter` contract: a point iterator augmented with span partition information and synthetic boundary keys.

## Important APIs, Types, And Functions
`Iter` embeds `base.InternalIterator` and adds `Span() *Span`. `BoundaryType` enumerates `BoundaryNone`, `BoundaryEnd`, and `BoundaryStart`. `Span` exposes one boundary direction and sorted `keyspan.Key`s. `Span.Valid` and `Span.String` provide state checks and formatted output.

## Control Flow
This file is mostly contract documentation. It specifies how keyspace is partitioned into spans, when boundary keys are emitted, what `Span` means at boundaries, how prefix iteration exposes boundaries, the legal conditions for `TrySeekUsingNext`, and when `NextPrefix` is legal.

## State And Persistence Behavior
The interface requires implementations to return a stable pointer to embedded span state that updates across operations. Boundary can be nil for unbounded edges. No persistence exists in this file.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, and `strings`. Implementations include `InterleavingIter`, `SingleSpanIter`, `TestIter`, `TriggerIter`, wrappers like `LoggingIter`, `InvalidatingIter`, and `OpCheckIter`.

## Risks And Edge Cases
The contract is intentionally subtle around boundary keys, prefix seeks, and `TrySeekUsingNext`. Implementations must expose range deletion spans even when no point key with the prefix exists. Boundary keys use `SeqNumMax`, affecting ordering with same-user-key point keys.

## Test Signals
The `iterv2` test utilities use this contract as the oracle: `OpCheckIter` enforces legal operations, `TestIter` models expected outputs, and random tests compare implementations against it.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/logging_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/logging_iter.go

## Purpose
`logging_iter.go` provides an `iterv2.Iter` wrapper that records every positioning operation, returned key, and current span for debugging and test failure diagnostics.

## Important APIs, Types, And Functions
`LoggingIter` stores an inner `Iter` and a `strings.Builder`. `NewLoggingIter` constructs it. `logResult` formats `.` or the returned internal key plus the inner span. All iterator methods delegate to the inner iterator and append a line; `String` returns the accumulated log.

## Control Flow
Positioning methods call the inner operation first, then write `Operation(args) = result span`. `SetBounds` logs before delegating. Non-positioning methods (`Span`, `Error`, `Close`, `SetContext`, `TreeStepsNode`) delegate without changing semantics.

## State And Persistence Behavior
The only state is the in-memory log buffer. The wrapper does not reset logs automatically, so one wrapper accumulates history for its lifetime.

## Dependencies And Integration Points
It depends on `base`, `treesteps`, `context`, `fmt`, and `strings`. `CheckIter` wraps implementations in `LoggingIter` so failures include the operation trace.

## Risks And Edge Cases
Logs use the inner `Span` after each operation; if an implementation returns unstable span state, logs reflect that. Large random tests can accumulate substantial log strings on long runs, but they are mainly printed on failure.

## Test Signals
It is a diagnostic tool rather than directly tested here. Useful signal is readable operation history in random test failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/logging_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/op_check_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/op_check_iter.go

## Purpose
`op_check_iter.go` wraps an `iterv2.Iter` and enforces legal operation sequences, especially around direction, exhaustion, bounds, prefix mode, boundary keys, and `TrySeekUsingNext`.

## Important APIs, Types, And Functions
`iterState` tracks unpositioned, forward/backward valid/exhausted, and prefix valid/exhausted states. `IllegalOpError` marks expected illegal operations during random generation. `OpCheckIter` stores inner iterator, comparer, state, boundary flag, last key, bounds, last seek mode, try-seek boundary, and optional prefix-change enforcement. Public APIs include `NewOpCheckIter` and `RequirePrefixChangeForTrySeekUsingNext`; all `Iter` methods are implemented.

## Control Flow
Before delegating, each method validates its preconditions. Seek methods validate bounds and `TrySeekUsingNext` constraints, then set new seek state. `Next`, `Prev`, and `NextPrefix` reject invalid states and update try-seek boundaries. Transition helpers update `lastKey`, `atBoundary`, and state based on returned KV. `SetBounds` resets position state.

## State And Persistence Behavior
The wrapper maintains only operation-state metadata. It does not persist data. On illegal operations it panics before altering the wrapped iterator, which lets random tests skip illegal operations safely.

## Dependencies And Integration Points
It depends on `base`, `treesteps`, `context`, `bytes`, and formatting. `CheckIter` uses it around the reference iterator to determine whether a randomly chosen operation is legal.

## Risks And Edge Cases
The legality rules mirror the long contract in `iter.go`; mistakes here can make tests skip valid operations or allow invalid ones. The special `RequirePrefixChangeForTrySeekUsingNext` mode is not general iterv2 behavior and is only for a merging-iterator-specific test mode.

## Test Signals
Random tests rely on `IllegalOpError` classification. Failures often include operation logs showing which legality rule diverged from implementation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/op_check_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/single_span_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/single_span_iter.go

## Purpose
`single_span_iter.go` implements a low-overhead `iterv2.Iter` for one keyspan containing one `keyspan.Key`, equivalent to interleaving an empty point iterator with a one-span iterator.

## Important APIs, Types, And Functions
`SingleSpanIter` stores comparer, span start/end, up to four partition boundaries, number of regions, key-bearing region index, current region, direction, presented span/KV, one key, and optional prefix. `Init` configures the span and bounds. Helpers include `computeRegions`, `regionKeys`, `emitForward`, `emitBackward`, `exhaust`, and seek helpers. It implements all `Iter` methods.

## Control Flow
`computeRegions` partitions the bounded range into gap/span/gap regions and records which region carries the span key. Forward operations emit boundary keys at region ends; backward operations emit boundary keys at region starts. `SeekGE` and `SeekLT` find the region containing the seek position. `Next`/`Prev` move between regions or handle direction switches. Prefix mode allows one nonmatching boundary before exhaustion.

## State And Persistence Behavior
State is in-memory iterator position. It returns only synthetic boundary keys and never point keys. `SetBounds` recomputes regions and exhausts current position.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `invariants`, `treesteps`, and `errors`. It is intended as an optimized building block for single-range-delete/span cases.

## Risks And Edge Cases
Handling nil unbounded boundaries, empty dynamic ranges, span entirely outside bounds, and direction switches is subtle. `NextPrefix` is illegal and always panics because the iterator never positions at point keys. `Init` invariant-checks non-nil ordered span endpoints.

## Test Signals
`single_span_iter_rand_test.go` compares random operations against `TestIter`, covering bounds and direction changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/single_span_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/single_span_iter_rand_test.go -->
# sources/storage-engines/pebble/internal/iterv2/single_span_iter_rand_test.go

## Purpose
`single_span_iter_rand_test.go` randomized-tests `SingleSpanIter` against the general `TestIter` reference implementation.

## Important APIs, Types, And Functions
`TestSingleSpanIterRandom` runs 200 seeds. `runSingleSpanRandomTest` chooses a random key config, random non-empty span, random range-delete trailer, random dynamic bounds, initializes `SingleSpanIter`, and calls `CheckIter`.

## Control Flow
The test loops until it has two distinct random keys for span start/end, orders them, chooses a sequence number, computes bounds, and runs 500 random operations. On failure it logs seed, config, span, trailer kind, and bounds.

## State And Persistence Behavior
All state is seed-local. No golden files are used; reproducibility is via the logged seed.

## Dependencies And Integration Points
It depends on `math/rand/v2`, `base`, `keyspan`, `testkeys`, and iterv2 test utilities.

## Risks And Edge Cases
Random coverage is probabilistic but broad across bounds, prefixes, and operation sequences. The expected data contains exactly one span and no points, matching the optimized iterator’s contract.

## Test Signals
Passing runs signal that `SingleSpanIter` matches general span-boundary semantics for seeking, movement, exhaustion, and bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/single_span_iter_rand_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/test_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/test_iter.go

## Purpose
`test_iter.go` implements `TestIter`, a simple reference `iterv2.Iter` that precomputes a flat sequence of point and boundary entries from known points/spans for differential testing.

## Important APIs, Types, And Functions
`testEntry` records an `InternalKV`, region index, and directional skip flags. `TestIter` stores immutable input points/spans/bounds plus computed boundaries, region keys, entries, index, direction, current KV/span, prefix filter, and last seek mode. `TestIterData` is the input model. `NewTestIter`, `init`, `emitEntry`, `emitForward`, `emitBackward`, seek helpers, and all `Iter` methods implement the model.

## Control Flow
`init` clips points/spans to dynamic bounds, builds sorted/deduplicated boundaries from bounds, span endpoints, and extra boundaries, assigns span keys to regions, creates point and forward/backward boundary entries, and stable-sorts by internal key order. Forward methods skip entries marked `skipFwd` and optional prefix filters; backward methods skip `skipBwd`. Prefix seeking installs a filter that allows matching-prefix entries and the terminal nonmatching boundary needed by the iterv2 contract.

## State And Persistence Behavior
State is in-memory reference iterator position. `SetBounds` rebuilds computed entries. Values for SET keys are synthetic in random point generation, but `TestIter` mostly compares keys and spans.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `testkeys`, `treesteps`, `slices`, `sort`, and `errors`. It is the oracle for `CheckIter`, `InterleavingIter`, `SingleSpanIter`, and other span-aware iterators.

## Risks And Edge Cases
Because it is the oracle, bugs here can validate incorrect implementations. Prefix `TrySeekUsingNext` backtracking rules are intentionally special and only check reference-model sanity; `OpCheckIter` enforces the full legality contract.

## Test Signals
`test_iter_test.go` validates examples using shared datadriven input. Random tests using `CheckIter` indirectly stress this model continuously.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/test_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/test_iter_test.go -->
# sources/storage-engines/pebble/internal/iterv2/test_iter_test.go

## Purpose
`test_iter_test.go` datadriven-tests the `TestIter` reference implementation itself.

## Important APIs, Types, And Functions
`TestTestIter` supports `define-points`, `define-spans`, and `iter` commands, mirroring `interleaving_iter_test.go`. It constructs `TestIterData` with optional `start`, `end`, `lower`, and `upper` arguments and runs `RunIterOps`.

## Control Flow
The test parses fixtures from input lines, prints normalized definitions, constructs a new `TestIter` for each `iter` command, and executes scripted operations.

## State And Persistence Behavior
Points, spans, and the current test iterator are local to the datadriven closure. Golden output lives in `testdata/interleaving_iter`, shared with the interleaving iterator tests.

## Dependencies And Integration Points
It depends on `datadriven`, `crstrings`, Pebble `base`, `keyspan`, and `RunIterOps`.

## Risks And Edge Cases
Using the same testdata as `InterleavingIter` makes comparison easy but means reference and implementation outputs can co-evolve if expectations are changed carelessly.

## Test Signals
Passing tests increase confidence that the reference model’s boundary and span formatting match the intended contract before it is used in random differential tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/test_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/test_utils.go -->
# sources/storage-engines/pebble/internal/iterv2/test_utils.go

## Purpose
`test_utils.go` provides randomized and scripted test utilities for `iterv2.Iter` implementations, including the differential checker used by random tests.

## Important APIs, Types, And Functions
`TB` abstracts `testing.TB`. `TestOp` enumerates operations and `TestOpWeights` weights them; `AllTestOps` is the default distribution. `CheckIterConfig` configures comparer, key generation, weights, operation count, and special prefix-change behavior. `CheckIter` runs random operations against a reference `TestIter` and implementation. `KeyGenConfig`, `RandKeyConfig`, `RandKey`, `RandPointKeys`, `RandSpans`, `RandBounds`, and `RunIterOps` support fixture generation and scripted execution.

## Control Flow
`CheckIter` creates a reference `TestIter` wrapped in `OpCheckIter` and wraps the implementation in `LoggingIter`. For each random operation, it builds an operation closure, runs it against the checker while catching `IllegalOpError`, skips illegal operations, runs the implementation, and compares returned key/trailer and span string. On panic or mismatch it logs the operation history.

## State And Persistence Behavior
All state is test-local. Random seeds are supplied by callers. `RunIterOps` formats output through a tabwriter but writes no files.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `testkeys`, `crstrings`, `errors`, `rand/v2`, `slices`, `cmp`, `debug`, and formatting packages. It is shared by interleaving, single-span, trigger, and future iterv2 tests.

## Risks And Edge Cases
Comparing `Span.String()` is simple but can hide differences if formatting changes. Illegal-operation filtering depends on `OpCheckIter` correctness. Random generation must keep spans non-overlapping and keys internally sorted/deduplicated to satisfy iterator contracts.

## Test Signals
Mismatches produce high-signal operation logs and expected/actual span/key pairs. Passing random checks are strong evidence of semantic conformance over many operation sequences.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/trigger_iter.go -->
# sources/storage-engines/pebble/internal/iterv2/trigger_iter.go

## Purpose
`trigger_iter.go` implements an `iterv2.Iter` that emits a synthetic boundary before iteration touches a region with nonzero count, then fires a callback and permanently exhausts itself.

## Important APIs, Types, And Functions
`BoundaryTrigger` defines `Trigger(key, dir)`. `TriggerIter` stores a comparer, `regiontree.T[[]byte,int]`, trigger callback, bounds, no-region flag, direction, current boundary KV, and span. Public methods include `Init`, `Reset`, all `Iter` methods, and tree/string helpers. Helpers include `checkNoRegions`, `makeBoundaryKey`, `upperBound`, `lowerBound`, `exhaust`, `fire`, `seekForward`, and `seekBackward`.

## Control Flow
Initialization checks whether any positive-count region intersects bounds. Forward seeks enumerate regions from a lower bound; if the seek key is inside a region, the trigger fires immediately, otherwise the iterator returns a boundary at the next region start. Backward seeks mirror this using region ends. `Next`/`Prev` fire when advancing past a presented boundary; direction switches reseek from the current boundary. `Reset` installs a new trigger and re-evaluates region availability.

## State And Persistence Behavior
State is in-memory and one-shot: after `fire`, `trigger` becomes nil, `noRegions` is true, and the iterator exhausts. Bounds can be changed with `SetBounds`.

## Dependencies And Integration Points
It depends on `axisds/regiontree`, `base`, `invariants`, `treesteps`, and `errors`. It supports lazy combined iteration where reaching a region triggers loading or activation of range-key state.

## Risks And Edge Cases
Seek keys exactly inside regions fire immediately instead of returning a boundary. `TrySeekUsingNext` has a randomized invariant fast path that can expose misuse. Nil trigger disables the iterator. Correct regiontree sentinel bounds are essential for nil lower/upper.

## Test Signals
`trigger_iter_test.go` covers region definition, forward/backward iteration, bounds, continuation after a boundary, and emitted trigger events.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/trigger_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/trigger_iter_test.go -->
# sources/storage-engines/pebble/internal/iterv2/trigger_iter_test.go

## Purpose
`trigger_iter_test.go` datadriven-tests `TriggerIter` boundary emission and trigger callback behavior.

## Important APIs, Types, And Functions
`testTrigger` records `trigger: key(dir)` events and exposes `drain`. `TestTriggerIter` supports `define`, `iter`, and `continue` commands. It builds an `axisds` region tree from `[start, end)=count` lines and drives `TriggerIter` through `RunIterOps`.

## Control Flow
The `define` command initializes a region tree and prints normalized intervals. The `iter` command initializes `TriggerIter` with optional lower/upper bounds and a test trigger, then runs operations and appends drained trigger events. `continue` runs more operations on the existing iterator.

## State And Persistence Behavior
The region tree, iterator, and trigger event buffer live in the test closure. Golden behavior persists in `testdata/trigger_iter`.

## Dependencies And Integration Points
It depends on `axisds`, `regiontree`, `datadriven`, `crstrings`, `testkeys`, and iterv2 scripted utilities.

## Risks And Edge Cases
Parsing is intentionally simple and assumes valid `[start, end)=count` input. Because triggers are one-shot, datadriven command order matters.

## Test Signals
Golden output verifies interval normalization, boundary keys/spans, trigger event direction, bounds, direction switches, and post-trigger exhaustion.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/iterv2/trigger_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/keyspan/assert_iter.go -->
# sources/storage-engines/pebble/internal/keyspan/assert_iter.go

## Purpose
`assert_iter.go` wraps `keyspan.FragmentIterator` implementations with sanity checks for seek/movement ordering and optional user-key/internal-key bounds.

## Important APIs, Types, And Functions
`Assert` wraps with an `assertIter`. `MaybeAssert` randomly composes invalidating and assert wrappers in invariant builds. `AssertUserKeyBounds` and `AssertBounds` enforce span/key bounds. `assertIter` stores the wrapped iterator, comparer, optional bounds, and last span start/end. It implements all `FragmentIterator` methods and `WrapChildren`.

## Control Flow
Each positioning method delegates, validates the returned span relative to the operation, calls `check`, and returns. `check` validates lower/upper bounds, including trailer ordering for spans starting exactly at the lower internal key, and records span start/end for subsequent `Next`/`Prev` ordering checks.

## State And Persistence Behavior
Wrapper state is in-memory last-span metadata and bounds. It does not alter returned spans. Panics signal invariant failures.

## Dependencies And Integration Points
It depends on `base`, `invariants`, `treesteps`, `context`, `errors`, and formatting. It is used around keyspan iterators in tests and invariant builds.

## Risks And Edge Cases
Bounds are asymmetric because span ends are exclusive user keys while lower can be an internal key. `MaybeAssert` randomness means invariant coverage is probabilistic. Incorrect comparer use would produce false positives or negatives.

## Test Signals
`assert_iter_test.go` validates bound enforcement. Broader iterator tests indirectly exercise seek and ordering assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/keyspan/assert_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/keyspan/assert_iter_test.go -->
# sources/storage-engines/pebble/internal/keyspan/assert_iter_test.go

## Purpose
`assert_iter_test.go` datadriven-tests bound checking for `keyspan.AssertBounds` and `AssertUserKeyBounds`.

## Important APIs, Types, And Functions
`TestAssertBoundsIter` supports `define`, `assert-bounds`, and `assert-userkey-bounds`. It parses spans with `ParseSpan`, constructs a `NewIter`, wraps it, iterates forward, and captures panics as output.

## Control Flow
`define` replaces the span fixture. Assertion commands read a two-line lower/upper input, choose internal-key or user-key lower bound mode, iterate from `First` through `Next`, and return `OK` or the panic message.

## State And Persistence Behavior
The span fixture persists across datadriven commands in the test closure. Golden behavior lives in `testdata/assert_iter`.

## Dependencies And Integration Points
It depends on `datadriven`, `base`, `testkeys`, `testify/require`, and keyspan iterator helpers.

## Risks And Edge Cases
The test only iterates forward from first; it focuses on bounds rather than `SeekGE`, `SeekLT`, or reverse ordering assertions. Panic messages include the wrapped type, so type-name changes can affect goldens.

## Test Signals
Golden output confirms lower user-key, lower internal-key trailer, and upper-bound violations are detected while valid spans pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/keyspan/assert_iter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/keyspan/bounded.go -->
# sources/storage-engines/pebble/internal/keyspan/bounded.go

## Purpose
`bounded.go` implements `BoundedIter`, a `keyspan.FragmentIterator` wrapper that enforces lower/upper bounds and optionally restricts spans to a prefix-iteration keyspace.

## Important APIs, Types, And Functions
`boundedIterPos` records whether the wrapper is at the lower limit, at the underlying iterator span, or at the upper limit. `BoundedIter` stores the wrapped iterator, current span, comparer, split function, bounds, optional prefix mode pointers, prefix pointer, and position state. Public methods include `Init`, all `FragmentIterator` methods, `SetBounds`, `WrapChildren`, and `TreeStepsNode`. Helpers enforce prefix start/end and forward/backward bounds.

## Control Flow
Seek/first/last operations delegate then filter spans through prefix and directional bounds. `Next` and `Prev` can return nil without advancing the underlying iterator when the current span already overlaps the bound or prefix edge, recording a limit position so a later direction switch can return the saved span. Prefix mode filters spans whose start is after the prefix or end is at/before the prefix.

## State And Persistence Behavior
All state is in-memory wrapper position. `SetBounds` changes dynamic bounds without resetting the underlying iterator directly. `hasPrefix` and `prefix` are pointers so the owner can update prefix mode externally.

## Dependencies And Integration Points
It depends on `base`, `treesteps`, `context`, and `errors`. It wraps keyspan iterators used alongside point iterators, especially when prefix iteration and dynamic bounds need range-key filtering.

## Risks And Edge Cases
The wrapper relies on callers to use `SeekGE` instead of `First` when lower is set and `SeekLT` instead of `Last` when upper is set. Prefix mode disallows most reverse iteration by contract outside an initial seek shape. The saved limit-position logic is subtle but avoids unnecessary underlying movement.

## Test Signals
Coverage is indirect through keyspan and combined iterator tests. Important signals include correct nil-at-bound behavior, direction switches from limit positions, and filtering of spans outside prefix keyspace.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/keyspan/bounded.go -->
