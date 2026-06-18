# subset-b-009506 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/lists/linux_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/lists/linux_test.go

## Purpose

This test file regression-tests the registered Linux subsystem list through the public subsystem extractor. It protects expected routing from crash evidence, especially cases where a generic guilty path should be overridden or supplemented by syzkaller reproducer calls.

## Important APIs, Types, And Functions

`TestLinuxUpstreamSubsystems` obtains `subsystem.GetList("linux")`, builds `subsystem.MakeExtractor`, and runs table-driven cases with `[]*subsystem.Crash`. Inputs combine `GuiltyPath` and `SyzRepro`; expected results are subsystem names such as `xfs`, `ntfs3`, `dri`, `usb`, `wireless`, and `v9fs`.

## Control Flow, State, Dependencies, And Integration

Each case calls `group.Extract`, collects subsystem names, and compares with `assert.ElementsMatch`. The test depends on package registration from the generated/static Linux list and the extractor behavior in `pkg/subsystem`. There is no persistence; all state is test-local. Integration coverage is high because it exercises real Linux rules, path matching, syscall extraction from repro programs, voting behavior, and parent removal through the public API.

## Risks And Test Signals

The file is sensitive to Linux list drift: a legitimate subsystem-rule update may require expected-output changes. It intentionally checks ambiguous evidence, stale names such as old NTFS routing to `ntfs3`, broad `mm`/`arm` paths, and overlapping USB/media evidence. Failures here signal user-visible syzbot CC/routing regressions rather than isolated parser problems.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/lists/linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/match.go -->
# sources/test-tools/syzkaller/pkg/subsystem/match.go

## Purpose

`match.go` implements path-to-subsystem matching. It compiles `Subsystem.PathRules` into regular-expression matchers and returns all subsystems whose include and exclude rules admit a source path.

## Important APIs, Types, And Functions

`PathMatcher` stores ordered `*match` entries. `MakePathMatcher` constructs a matcher from a subsystem list. `PathMatcher.register` groups rules without excludes into one alternation to reduce matcher count, while preserving rules that need excludes. `PathMatcher.Match` evaluates all matches and deduplicates by `*Subsystem`. `buildMatch` compiles include/exclude regex strings with `regexp.MustCompile`.

## Control Flow, State, Dependencies, And Integration

All state is in-memory and immutable after construction unless callers mutate referenced subsystems. Matching first rejects excluded paths, then requires included paths when an include regexp exists. Results are collected through a map and returned via `slices.Collect(maps.Keys(...))`, so ordering is intentionally unspecified. The matcher is used by `rawExtractor.FromPath`, Linux coincidence building, and subsystem extraction.

## Risks And Test Signals

Regex compilation panics on invalid rules, making list construction fail fast. Empty include with only exclude would match every non-excluded path; current callers should avoid such rules. Result order is nondeterministic, so callers must not rely on it. Tests in `match_test.go` cover deduplication, include/exclude interaction, and rule order independence.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/match.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/match_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/match_test.go

## Purpose

This file tests `PathMatcher` behavior for overlapping include rules, exclusions, documentation paths, and the intended include-before-exclude semantics.

## Important APIs, Types, And Functions

`TestPathMatcher` creates synthetic `Subsystem` values with path rules for ARM, documentation, and overlapping IRQ/devicetree files. `TestPathMatchOrder` verifies that a rule with include `^a/b/.*$` and exclude `^a/.*$` does not match `a/b/c`.

## Control Flow, State, Dependencies, And Integration

The tests build `MakePathMatcher` directly, call `Match`, and assert with `assert.ElementsMatch` or `assert.Empty`. There is no filesystem or persistence. They isolate `PathMatcher` from the higher-level extractor and Linux subsystem list, making failures easier to attribute to matching logic.

## Risks And Test Signals

The tests catch duplicate returns when multiple include rules match one subsystem and ensure a path can match multiple subsystems. They also enforce that exclusion is scoped per rule, not a global pre-filter. Because the production matcher returns map-key order, the tests correctly ignore result order.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/match_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/raw_extractor.go -->
# sources/test-tools/syzkaller/pkg/subsystem/raw_extractor.go

## Purpose

`raw_extractor.go` provides low-level subsystem lookup by source path and by syzkaller program contents. Higher-level extraction uses it as evidence collection for crash routing.

## Important APIs, Types, And Functions

`rawExtractor` contains a `PathMatcher` and a `perCall` map from syscall name to subsystems. `makeRawExtractor` builds both indexes from a subsystem list. `FromPath` delegates to `PathMatcher.Match`. `FromProg` calls `prog.CallSet`, then maps encountered call names to unique subsystem pointers.

## Control Flow, State, Dependencies, And Integration

Construction is in-memory. `FromProg` ignores parse errors returned by `prog.CallSet`, intentionally extracting whatever call set is available. The result list is built from a map, so order is unspecified. It integrates with `Extractor` voting and with subsystem lists that annotate relevant `Syscalls`.

## Risks And Test Signals

Risks include silent loss of syscall evidence when reproducer parsing fails, nondeterministic ordering, and exact-name dependency between `Subsystem.Syscalls` and `prog.CallSet` output. `raw_extractor_test.go` covers path rules, exclusion, overlapping path matches, and syscall extraction from representative syz programs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/raw_extractor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/raw_extractor_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/raw_extractor_test.go

## Purpose

This test file validates the raw subsystem extractor with a small synthetic subsystem list before higher-level voting or parent filtering is involved.

## Important APIs, Types, And Functions

`TestSubsystemExtractor` defines `ioUring`, `security`, and `net` subsystems. It checks `makeRawExtractor`, `FromPath`, and `FromProg`, including a subsystem mapped by `Syscalls` (`syz_io_uring_setup`) and paths that match multiple subsystems.

## Control Flow, State, Dependencies, And Integration

The test first verifies direct path matching, then feeds syzkaller program text into `FromProg`. It depends on `prog.CallSet` parsing syscall names from repro snippets. Assertions use `ElementsMatch` because result order comes from maps.

## Risks And Test Signals

The file catches regressions in exclude handling (`security/selinux`), overlapping paths (`net/ipv6/calipso.c`), and syscall evidence extraction. It also confirms unrelated syz calls do not spuriously map to subsystems. It does not cover malformed program parsing beyond relying on production tolerance.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/raw_extractor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/service.go -->
# sources/test-tools/syzkaller/pkg/subsystem/service.go

## Purpose

`service.go` wraps subsystem extraction with lookup and hierarchy indexes. It is the package-level service object for consumers that need extraction plus named access, revision tracking, and child lookup.

## Important APIs, Types, And Functions

`Service` embeds `*Extractor` and stores `Revision`, `perName`, and `perParent`. `MakeService` validates non-empty unique subsystem names, builds an extractor, indexes by name, and builds parent-to-children slices. `MustMakeService` panics on construction errors. `ByName`, `List`, and `Children` expose lookup helpers.

## Control Flow, State, Dependencies, And Integration

The service state is computed at construction and then read-only unless callers mutate subsystem objects. `List` iterates a map and therefore returns nondeterministic order. `Children` clones stored slices to protect the internal slice header. The type integrates with registered lists and any syzbot or dashboard code that needs stable named subsystems.

## Risks And Test Signals

Risks include duplicate or missing names failing service construction, pointer identity in `perParent`, and nondeterministic `List` order. `service_test.go` covers child lookup for a single parent but not validation errors or list ordering.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/service_test.go -->
# sources/test-tools/syzkaller/pkg/subsystem/service_test.go

## Purpose

This file tests `Service.Children`, confirming that parent-child indexing is built from each subsystem's `Parents` slice.

## Important APIs, Types, And Functions

`TestServiceChildren` creates an unrelated subsystem, a parent, and two children. It constructs a service with `MustMakeService` and asserts that `Children(parent)` returns both children.

## Control Flow, State, Dependencies, And Integration

The test is entirely in-memory and uses pointer identity for the parent key, matching production behavior. It depends on `MakeService` succeeding and on `slices.Clone` not altering expected contents.

## Risks And Test Signals

The test catches regressions where children are not indexed or parent relationships are ignored. It does not test duplicate names, empty names, mutation safety of returned slices, or the nondeterministic `List` method.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/addr2line.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/addr2line.go

## Purpose

`addr2line.go` implements the `Symbolizer` backend using a persistent `addr2line` subprocess per binary. It translates program counters into function/file/line frames, including inline frames.

## Important APIs, Types, And Functions

`addr2Line` stores a target, subprocess map, and string interner. `Symbolize` obtains a subprocess and calls `symbolize`. `Close` closes pipes, kills subprocesses, and waits. `getSubprocess` invokes `target.Addr2Line()` and starts `addr2line -afi -e <bin>`. `symbolize` writes PCs plus a sentinel invalid PC, reads parsed frames in a goroutine, and returns combined frames. `parse` consumes addr2line output into `Frame` values.

## Control Flow, State, Dependencies, And Integration

State persists across calls in `subprocs` and `Interner`, reducing process startup and string allocation. Parsing treats line `0` as unknown (`-1`), drops `??` or invalid frames, and marks the last frame for a PC as non-inline. Dependencies include `os/exec`, `bufio.Scanner`, `osutil.Command`, and target toolchain metadata. This is the primary implementation returned by `symbolizer.Make`.

## Risks And Test Signals

The implementation is not explicitly synchronized; concurrent `Symbolize` calls on the same `addr2Line` would race on pipes and maps. Scanner token limits can affect very long symbol lines. If `addr2line` exits or emits unexpected format, errors propagate. `addr2line_test.go` covers parsing, inline frames, discriminator suffixes, unknown PCs, batching, and pipe backpressure.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/addr2line.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/addr2line_test.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/addr2line_test.go

## Purpose

This test file validates the `symbolize` and `parse` protocol against a stubbed addr2line stream, including batching and high-volume writes.

## Important APIs, Types, And Functions

`TestParse` defines address-to-response fixtures with expected `Frame` slices. It uses `os.Pipe` pairs to simulate addr2line stdin/stdout, runs a goroutine that responds to PC lines, and calls `symbolize` repeatedly.

## Control Flow, State, Dependencies, And Integration

The test first symbolises each PC individually, then splits the same PC list into two groups at every boundary, then sends 10,000 PCs to exercise pipe overflow avoidance. It uses `reflect.DeepEqual` against exact frames.

## Risks And Test Signals

Coverage includes unknown `??` frames, line zero normalization, inline flag assignment, file-line suffixes such as discriminator text, and sentinel behavior. It catches deadlocks in the goroutine/flush protocol. It does not start a real `addr2line` binary, so toolchain discovery and subprocess lifecycle are covered elsewhere only indirectly.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/addr2line_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/cache.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/cache.go

## Purpose

`cache.go` contains support utilities for symbolization: a thread-safe per-PC cache and a string interner to reduce repeated allocation of function and file names.

## Important APIs, Types, And Functions

`Cache` stores a guarded map from `(bin, pc)` to frames/error. `Cache.Symbolize` checks the cache under an `RWMutex`, calls an `inner` symbolizer on miss, initializes the map if needed, stores both successful frames and errors, and returns the result. `Interner.Do` stores cloned strings in `sync.Map` and returns canonical copies.

## Control Flow, State, Dependencies, And Integration

Cache state persists in memory and is safe for normal concurrent map access. It does not coalesce concurrent cache misses, so two goroutines can symbolize the same key simultaneously before either stores. The interner uses `sync.Map`, but comments say it is not semantically thread-safe; production use in `addr2line` is single stream oriented. Integrates with symbolization consumers that need repeated PC lookup.

## Risks And Test Signals

Cached errors can make transient symbolizer failures sticky. Returned frame slices are not cloned, so callers could mutate cached data. `cache_test.go` verifies hits avoid repeated `inner` calls and that errors are cached per key.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/cache_test.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/cache_test.go

## Purpose

This file tests that `Cache.Symbolize` memoizes both successful symbolization results and errors by binary plus PC.

## Important APIs, Types, And Functions

`TestCache` defines an `inner` function that tracks calls in a `map[cacheKey]bool`, returns frames for normal bins, and returns formatted errors for bin `"error"`. A local `check` helper compares cached results.

## Control Flow, State, Dependencies, And Integration

The test invokes repeated lookups for identical and different keys. It asserts the inner function is not called twice for the same `(bin, pc)` pair. Assertions use testify equality on frame slices and errors.

## Risks And Test Signals

This catches basic cache-key mistakes and confirms negative caching. It does not exercise concurrency, mutation of returned frames, or multi-PC inner calls beyond the one-PC production cache API.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/nm.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/nm.go

## Purpose

`nm.go` reads ELF symbol tables and returns text or rodata symbols in a format syzkaller can use for symbol lookup and matching.

## Important APIs, Types, And Functions

`Symbol` stores `Addr` and `Size`. `ReadTextSymbols` and `ReadRodataSymbols` call `read`. `read` loads symbols, sorts them by descending address, and builds `map[string][]Symbol`. For text symbols, it recomputes size from the next lower symbol address to match Linux kernel symbol sizing. `load` opens an ELF file, reads symbols, filters invalid sections, text sections, or `.rodata`.

## Control Flow, State, Dependencies, And Integration

There is no persistent state. Dependencies are Go's `debug/elf`, `slices`, and `cmp`. Text detection uses section type/flags; rodata detection uses section name because some vmlinux `.rodata` flags resemble writable data. The output map supports duplicate symbol names.

## Risks And Test Signals

Risks include relying on regular ELF symbol tables only, section-name assumptions for rodata, and computed sizes for equal-address symbols. `nm_test.go` verifies duplicate text symbols and computed sizes on a checked-in ELF fixture.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/nm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/nm_test.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/nm_test.go

## Purpose

This test validates text symbol extraction from the `testdata/nm.test.out` ELF fixture.

## Important APIs, Types, And Functions

`TestSymbols` calls `ReadTextSymbols`, checks total symbol-name count, verifies `barfoo` address/size, and verifies two `foobar` symbols with expected addresses and recomputed sizes. `symcmp` compares `Symbol` values.

## Control Flow, State, Dependencies, And Integration

The test depends on the fixture being a readable ELF file with a stable symbol table. It logs extracted symbols and uses fatal assertions for exact failures.

## Risks And Test Signals

The test catches regressions in duplicate-name handling and kernel-style size computation. It does not cover rodata extraction, missing/stripped symbol tables, invalid ELF files, or section filtering edge cases.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/nm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/symbolizer.go -->
# sources/test-tools/syzkaller/pkg/symbolizer/symbolizer.go

## Purpose

`symbolizer.go` defines the public symbolization types and constructor for the package.

## Important APIs, Types, And Functions

`Frame` describes one symbolized frame with PC, function, file, line, and inline status. `Symbolizer` is an interface with `Symbolize` and `Close`. `Make` returns an `addr2Line` implementation for a `targets.Target`.

## Control Flow, State, Dependencies, And Integration

This file has no persistence and no control flow beyond construction. It decouples callers from the concrete addr2line backend, while the `Frame` struct is shared by cache, addr2line parsing, and tests.

## Risks And Test Signals

The API assumes callers will close symbolizers to avoid subprocess leaks in the concrete implementation. The constructor does not return an error; toolchain lookup errors occur during first symbolization. No direct tests target this thin file, but other symbolizer tests depend on the `Frame` contract.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/symbolizer/symbolizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/testutil/norace.go -->
# sources/test-tools/syzkaller/pkg/testutil/norace.go

## Purpose

`norace.go` provides the `RaceEnabled` build-time constant for normal, non-race builds.

## Important APIs, Types, And Functions

Under build tag `!race`, it defines `const RaceEnabled = false` in package `testutil`.

## Control Flow, State, Dependencies, And Integration

There is no runtime control flow or state. The file complements `race.go`; exactly one is selected by Go build tags. `testutil.IterCount` uses this constant to scale randomized test iteration counts.

## Risks And Test Signals

The risk is accidental build-tag mismatch causing duplicate or missing constants. Behavior is implicitly covered wherever `testutil.IterCount` is used in race and non-race builds.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/testutil/norace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/testutil/race.go -->
# sources/test-tools/syzkaller/pkg/testutil/race.go

## Purpose

`race.go` provides the `RaceEnabled` build-time constant for race-detector builds.

## Important APIs, Types, And Functions

Under build tag `race`, it defines `const RaceEnabled = true` in package `testutil`.

## Control Flow, State, Dependencies, And Integration

There is no runtime control flow or state. It is selected by Go's race build tag and influences `IterCount`, allowing expensive randomized tests to run fewer iterations under the slower race detector.

## Risks And Test Signals

The file is small but important for keeping test suites practical under `go test -race`. Build-tag correctness is the main risk and is validated by compilation under race builds.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/testutil/race.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/testutil/testutil.go -->
# sources/test-tools/syzkaller/pkg/testutil/testutil.go

## Purpose

`testutil.go` contains shared test helpers for iteration scaling, deterministic randomness, random value construction, and test-log-backed writers.

## Important APIs, Types, And Functions

`IterCount` returns 1000, reduced in short or race builds. `RandSource` chooses a seed from current time, `SYZ_SEED`, or `0` in CI, and logs it. `RandMountImage` returns up to 1 MiB of random bytes. `RandValue` and `randValue` recursively generate values with special handling for slices, arrays, structs, pointers, maps, and `time.Time`. `Writer.Write` logs bytes through `testing.TB`.

## Control Flow, State, Dependencies, And Integration

Randomness is caller-local except for environment variables. Reflection recurses through type shapes and calls `testing/quick.Value` for primitive/default cases. Integration points are fuzz-like tests and helpers that need reproducible seeds.

## Risks And Test Signals

`randValue` uses package-level `rand.Intn` in some branches instead of the supplied `rnd`, weakening seed determinism for sizes and pointer/map choices. It can panic/fail on unexported struct fields or unsupported quick types. There are no direct tests in this subset; usage across tests is the signal.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/cmdprof.go -->
# sources/test-tools/syzkaller/pkg/tool/cmdprof.go

## Purpose

`cmdprof.go` implements optional CPU and heap profiling setup for syzkaller command-line tools.

## Important APIs, Types, And Functions

`installProfiling(cpuprof, memprof string) func()` creates and starts a CPU profile when requested, returns a cleanup function, and layers heap profile writing after previous cleanup when `memprof` is requested. It uses `runtime.GC` before `pprof.WriteHeapProfile`.

## Control Flow, State, Dependencies, And Integration

State is process-global through `runtime/pprof`. Errors call `tool.Failf`, which writes to stderr and exits. The function is used by `tool.Init`, so command-line binaries can `defer tool.Init()()`.

## Risks And Test Signals

Profiling file creation or writing exits the process, which is appropriate for tools but hard to unit-test. CPU profile file close is omitted if `StartCPUProfile` fails after create, but the process exits. No direct tests cover profiling; integration is through command execution paths.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/cmdprof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/flags.go -->
# sources/test-tools/syzkaller/pkg/tool/flags.go

## Purpose

`flags.go` adds common command-line parsing helpers, especially optional flags for compatibility with older binaries and multi-config flag parsing.

## Important APIs, Types, And Functions

`Flag` stores name/value pairs. `OptionalFlags` serializes optional flags into one `-optional=...` argument. `ParseFlags` parses the flag set, deserializes optional flags, applies only those known to the binary, and logs ignored unknown ones. `ParseArchList` validates/sorts target arches. `serializeFlags`, `deserializeFlags`, `flagEscape`, and `flagUnescape` implement a colon/equal-safe encoding. `CfgsFlag` implements `flag.Value`.

## Control Flow, State, Dependencies, And Integration

Parsing mutates the provided `flag.FlagSet` and any registered `CfgsFlag`. The optional flag encoding escapes controls, spaces, non-ASCII, `:`, `=`, and backslash as `\xNN`, making it safe as a single argument. Dependencies include `targets.List` and syzkaller logging.

## Risks And Test Signals

`ParseFlags` registers the `optional` flag on every call, so repeated calls on the same flag set may conflict. `CfgsFlag.Set` rejects multiple invocations and includes empty entries if given empty comma segments. `flags_test.go` and `flags_fuzz.go` cover compatibility parsing, arch validation, escaping, and round trips.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/flags_fuzz.go -->
# sources/test-tools/syzkaller/pkg/tool/flags_fuzz.go

## Purpose

`flags_fuzz.go` is a fuzz entrypoint for optional flag serialization/deserialization.

## Important APIs, Types, And Functions

`FuzzParseFlags` attempts to `deserializeFlags` from arbitrary bytes, reserializes valid values, asserts the serialized form contains no spaces, and verifies deserializing again preserves the flag slice. `init` keeps the fuzz function alive for deadcode checking.

## Control Flow, State, Dependencies, And Integration

Invalid inputs return `0`; valid round trips return `1`. The function panics on invariant violations, as expected for fuzz targets. It depends on `reflect.DeepEqual` and package-local helpers in `flags.go`.

## Risks And Test Signals

The fuzz target is focused on parser stability and encoding invariants. It does not exercise `flag.FlagSet` integration or optional application behavior. It is useful for catching malformed escape handling, accidental spaces, and lossy encoding changes.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/flags_fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/flags_test.go -->
# sources/test-tools/syzkaller/pkg/tool/flags_test.go

## Purpose

This file unit-tests command flag parsing helpers, arch-list validation, `CfgsFlag`, and optional-flag escaping.

## Important APIs, Types, And Functions

`TestParseFlags` covers normal flags, unknown hard flags, and ignored unknown optional flags. `TestCfgsFlagString`, `TestCfgsFlagSet`, and `TestCfgsFlagAlreadySet` validate `CfgsFlag`. `TestParseArchList` checks bad OS, bad arch, all Linux arches, and selected arches. `TestFlagEscapeUnescape` checks normal, space, special, control, empty, truncated, and invalid hex cases.

## Control Flow, State, Dependencies, And Integration

Tests allocate fresh flag sets and discard parser output. They depend on current `targets.List` contents for Linux arch expectations. Assertions use testify `assert` and `require`.

## Risks And Test Signals

These tests catch command-line compatibility regressions. The Linux arch list is intentionally exact, so target additions/removals require test updates. The tests do not cover repeated `ParseFlags` calls on one flag set or empty comma values in `CfgsFlag.Set`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/flags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/tool.go -->
# sources/test-tools/syzkaller/pkg/tool/tool.go

## Purpose

`tool.go` provides common command-line tool initialization, HTTP serving, and fatal-exit helpers.

## Important APIs, Types, And Functions

`Init` registers profiling flags, parses command-line flags through `ParseFlags`, and returns the profiling cleanup function. `ServeHTTP` listens on a TCP4 address and serves the default HTTP mux in a goroutine. `Failf` prints to stderr and exits with status 1; `Fail` formats an error through `Failf`.

## Control Flow, State, Dependencies, And Integration

`Init` mutates the global `flag.CommandLine` and process profiling state. `ServeHTTP` logs fatal errors and exits the process on listen or serve failure. This package is integrated by syzkaller command binaries that want consistent optional-flag and profiling behavior.

## Risks And Test Signals

The comment misspells `ServeHTTP` as `ServeHTPP`. Because helpers exit the process on errors, direct unit testing is limited. Risks include global flag registration conflicts and ungraceful HTTP server termination. `flags_test.go` covers the parsing layer used by `Init`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/tool/tool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/updater/updater.go -->
# sources/test-tools/syzkaller/pkg/updater/updater.go

## Purpose

`updater.go` maintains syzkaller self-updates and build artifacts for syz-ci-style deployments. It keeps `latest` and `current` syzkaller builds, rebuilds from the configured repository, and can restart the current executable after an update.

## Important APIs, Types, And Functions

`Updater` stores repo/build paths, artifact glob requirements, compiler ID, and config. `Config` controls update behavior, build semaphore, reporting, repository/branch/descriptions, targets, and make targets. `New` validates executable placement, prepares GOPATH-style source directory, computes expected output files, and captures `go version`. `UpdateOnStart`, `waitForUpdate`, `UpdateAndRestart`, `pollAndBuild`, `build`, and `checkLatest` implement the lifecycle.

## Control Flow, State, Dependencies, And Integration

The updater mutates the working directory: `gopath/src/github.com/google/syzkaller`, `syzkaller/latest`, `syzkaller/current`, and the current executable. It polls a `vcs.Repo`, runs `make`, per-target builds, and `go test -short ./...`, copies optional descriptions, writes a `tag` file, and links/copies required artifacts. Autoupdate mode starts a background waiter and closes `updatePending` when a new build is ready.

## Risks And Test Signals

This is operationally risky code: it removes `current`, copies over executables, can `syscall.Exec`, relies on external `go`/`make`, and serializes builds through `BuildSem`. Missing `BuildSem` would panic. Build failures are reported but only latest good builds are promoted. No direct tests are in this subset; integration depends on syz-ci environments and VCS/build helpers.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/updater/updater.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/validator/validator.go -->
# sources/test-tools/syzkaller/pkg/validator/validator.go

## Purpose

`validator.go` defines reusable validation predicates and combinators for user-facing strings such as commit hashes, namespace names, dashboard client credentials, kernel paths, and coverage time periods.

## Important APIs, Types, And Functions

`Result` carries `Ok` and `Err`; `ResultOk` is the success value. `AnyError`, `AnyOk`, and `PanicIfNot` combine validation results. `Allowlisted` checks membership. Exported validators include `EmptyStr`, `AlphaNumeric`, `CommitHash`, `KernelFilePath`, `NamespaceName`, `ManagerName`, `DashClientName`, `DashClientKey`, and `TimePeriodType`. Factory helpers build regexp, length, and combined validators.

## Control Flow, State, Dependencies, And Integration

Validators are package-level closures over compiled regexes. `looksDangerous` rejects strings containing `--` even if the regex would allow them. `DashClientKey` accepts either long alphanumeric keys or the auth OAuth magic prefix. `TimePeriodType` depends on `coveragedb` constants.

## Risks And Test Signals

Regexes are approximate, not full semantic validators. `CommitHash` allows all alphanumeric characters rather than hexadecimal only. `Allowlisted` returns `Ok:false` with an error but does not set `Ok:true` in the named success case except through explicit `Ok:true`. `validator_test.go` covers common good/bad values, error prefixes, combinators, and allowlist errors.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/validator/validator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/validator/validator_test.go -->
# sources/test-tools/syzkaller/pkg/validator/validator_test.go

## Purpose

This test file verifies exported validator predicates and result combinators from an external package perspective.

## Important APIs, Types, And Functions

Tests cover `CommitHash`, `NamespaceName`, `ManagerName`, `DashClientName`, `DashClientKey`, `KernelFilePath`, `AnyError`, `PanicIfNot`, `AnyOk`, and `Allowlisted`. `badResult` is a reusable failing `validator.Result`.

## Control Flow, State, Dependencies, And Integration

Tests call validators with and without object-name prefixes and compare exact error strings. The package is `validator_test`, which exercises the public API rather than internals.

## Risks And Test Signals

Exact error-string assertions protect API messages but can make refactors noisy. Tests highlight intentional `--` rejection for kernel paths and minimum lengths for names/keys. They do not cover `TimePeriodType`, `EmptyStr`, or OAuth magic key acceptance.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/validator/validator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/fuchsia.go -->
# sources/test-tools/syzkaller/pkg/vcs/fuchsia.go

## Purpose

`fuchsia.go` adapts the generic VCS interface for Fuchsia checkouts, where repository setup uses Jiri/bootstrap rather than a plain Git clone.

## Important APIs, Types, And Functions

`fuchsia` stores a directory and embedded `gitRepo`. `newFuchsia` appends `OptPrecious` to avoid destructive cleanup. `Poll` accepts only the Fuchsia main repository and `main`/`master`, runs `jiri update`, initializes on failure, and returns `HEAD`. `initRepo` bootstraps through a curl/base64/bash pipeline and runs `jiri update`. Most other `Repo` methods delegate to `gitRepo`; `PushCommit` returns not implemented.

## Control Flow, State, Dependencies, And Integration

Initialization removes and replaces the checkout directory through a temporary directory. It uses sandboxed command execution for bootstrap and Jiri. The adapter is selected by `NewRepo` for Fuchsia and Linux/Starnix. Persistent state is the checkout itself.

## Risks And Test Signals

The bootstrap command depends on network, curl, base64, bash, and upstream script stability. The first bootstrap `jiri update` error is intentionally ignored. Because repos are precious, generic recovery cleanup is disabled. No direct tests are in this subset.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/fuchsia.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git.go -->
# sources/test-tools/syzkaller/pkg/vcs/git.go

## Purpose

`git.go` is the core Git-backed implementation of syzkaller's `Repo` operations. It handles cloning, polling, checkout, commit metadata parsing, bisection, patch-base discovery, local command execution, and diff parsing.

## Important APIs, Types, And Functions

`gitRepo` wraps `*Git`. `newGitRepo` sets sandboxing, filtered environment, ignored CC map, and repo options. High-level methods include `Poll`, `CheckoutBranch`, `CheckoutCommit`, `FetchTags`, `SwitchCommit`, `Contains`, `GetCommitByTitle`, `GetCommitsByTitles`, `LatestCommits`, `ExtractFixTagsFromCommits`, `Bisect`, `ReleaseTag`, `Object`, `MergeBases`, `CommitExists`, `PushCommit`, and `fetchRemote`. `Git` exposes `Run`, `Apply`, `Reset`, `Commit`, `fetchCommits`, `BaseForDiff`, `BranchesThatContain`, `ContainedIn`, and `Diff`. `ParseGitDiff` extracts changed files and left blob hashes.

## Control Flow, State, Dependencies, And Integration

The implementation persists state in a checkout directory and mutates remotes, tags, branches, worktrees, submodules, and bisect state. It filters Git-related environment variables to avoid acting on the caller's repo. Non-precious repos can be removed and reinitialized on corruption; precious repos skip destructive reset. Most operations shell out with timeouts through `osutil`, optionally sandboxed.

## Risks And Test Signals

Risks include destructive cleanup for non-precious repos, command timeout dependence, shallow assumptions about Git error codes, regex-based metadata parsing, long-running `BaseForDiff`, and non-coalesced remote naming via URL hash. Tests in `git_repo_test.go` and `git_test.go` cover checkout flows, local commit reuse, metadata, bisection, tags, custom refs, short hashes, diff parsing, object extraction, merge bases, file hashes, and patch-base minimization.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git_repo_test.go -->
# sources/test-tools/syzkaller/pkg/vcs/git_repo_test.go

## Purpose

This file integration-tests `gitRepo` behavior against synthetic local repositories.

## Important APIs, Types, And Functions

`init` disables sandboxing for tests. `TestGitRepo` exercises polling, branch checkout, commit checkout across remotes, switching commits, and `Contains`. `TestCheckoutCommitLocal` ensures a commit already present locally is reused even when a requested alternate remote lacks it. `TestMetadata` validates commit metadata and fix-tag extraction using `metadataTests`. `TestBisect` tests conclusive and inconclusive bisection outcomes.

## Control Flow, State, Dependencies, And Integration

Tests create temp Git repositories with `CreateTestRepo` and `MakeTestRepo`, then run real Git commands. They depend on local Git behavior and disable syzkaller sandboxing because test repos are not sandbox-owned.

## Risks And Test Signals

These tests catch high-value regressions in repo lifecycle and metadata parsing. They can be sensitive to Git version differences, especially bisection output order; the test sorts inconclusive results. They do not cover network failures or submodules.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git_test.go -->
# sources/test-tools/syzkaller/pkg/vcs/git_test.go

## Purpose

`git_test.go` provides broad unit/integration coverage for Git metadata parsing, release tag sorting, lookup helpers, diff parsing, object reads, merge-base handling, custom refs, tag fetches, and base-commit inference.

## Important APIs, Types, And Functions

Tests include `TestGitParseCommit`, `TestGitParseReleaseTags`, `TestGetCommitsByTitles`, `TestContains`, `TestLatestCommits`, `TestObject`, `TestMergeBase`, `TestGitCustomRefs`, `TestGitRemoteTags`, `TestGitFetchShortHash`, `TestParseGitDiff`, `TestGitFileHashes`, `TestBaseForDiff`, and `TestBaseForDiffMerge`.

## Control Flow, State, Dependencies, And Integration

The file uses real temp Git repositories through `MakeTestRepo`. It creates branches, tags, custom refs, empty commits, content commits, diffs, merge commits, and conflict resolutions. Assertions verify both metadata values and repository graph behavior.

## Risks And Test Signals

The tests cover many operational edge cases: backported title canonicalization via lookup, short commit fetches, custom refs, tag reachability, newly created files in diffs, unknown blob hashes, repeated file modifications, and merge-derived bases. They depend on Git output formats and wall-clock seconds for one sort test.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git_test_util.go -->
# sources/test-tools/syzkaller/pkg/vcs/git_test_util.go

## Purpose

`git_test_util.go` provides helpers for constructing and manipulating temporary Git repositories in VCS tests.

## Important APIs, Types, And Functions

`TestRepo` stores test state, directory, commit map, and backing `gitRepo`. `Git` runs Git commands. `MakeTestRepo` initializes a repo, configures user identity and disables auto maintenance. `CommitFileChange`, `CommitChange`, `CommitChangeAt`, `CommitChangeset`, `SetTag`, `SupportsBisection`, and `CreateTestRepo` build reusable histories. `FileContent.Apply` writes and stages files.

## Control Flow, State, Dependencies, And Integration

Helpers mutate real temp directories and use `filterEnv` to avoid caller Git environment leakage. `MakeTestRepo` uses `OptPrecious` and `OptDontSandbox` for local test control. The `Commits` map records expected branch/change commits for assertions.

## Risks And Test Signals

These helpers centralize assumptions about Git availability, default branch handling, author identity, and repository maintenance behavior. `FileContent.Apply` writes files directly and assumes parent directories exist. Failures here affect many VCS tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/git_test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux.go -->
# sources/test-tools/syzkaller/pkg/vcs/linux.go

## Purpose

`linux.go` extends `gitRepo` with Linux-kernel-specific bisection, compiler selection, maintainer extraction, release tag handling, and kernel config minimization.

## Important APIs, Types, And Functions

`linux` embeds `*gitRepo` and stores `vmType`. `PreviousReleaseTags` filters old tags by compiler support. `gitParseReleaseTags` and `gitReleaseTagToInt` sort release tags. `EnvForCommit` selects compiler, adjusts config based on tags, and cherry-picks backports. `linuxClangPath` and `linuxGCCPath` map reachable tags to compiler versions. `PrepareBisect`, `Bisect`, `addMaintainers`, `getMaintainers`, `ParseMaintainersLinux`, and `Minimize` implement Linux-specific integration. `minimizeLinuxCtx` manages config minimization and instrumentation dropping.

## Control Flow, State, Dependencies, And Integration

The file mutates the checked-out kernel repo during backport cherry-picks and reads `scripts/get_maintainer.pl`. It parses Kconfig, serializes minimized configs with a syzkaller tag, and runs caller-provided bisection predicates. It depends on `targets`, `kconfig`, `crash.Type`, and `debugtracer`.

## Risks And Test Signals

Risks include stale compiler cutoff rules, upstream tag availability, get_maintainer output variability, expensive/flaky config minimization, and destructive repo operations inherited from Git. `linux_test.go`, `vcs_test.go`, and `linux_configs_test.go` cover compiler selection, maintainer parsing, release parsing, and sanitizer config behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_configs.go -->
# sources/test-tools/syzkaller/pkg/vcs/linux_configs.go

## Purpose

`linux_configs.go` contains rules for disabling Linux kernel config options that break older bisection builds/boots and for removing unneeded sanitizer/instrumentation options based on crash type.

## Important APIs, Types, And Functions

`setLinuxTagConfigs` unsets or alters configs based on reachable release tags, plus always-disabled items such as `LOCALVERSION_AUTO`, `DEBUG_INFO_BTF`, `DEBUG_KOBJECT`, and `BLK_DEV_INITRD`. It can swap `UNWINDER_ORC` to `UNWINDER_FRAME_POINTER`. `setLinuxSanitizerConfigs` maps crash type predicates to sanitizer/config categories and disables those not needed.

## Control Flow, State, Dependencies, And Integration

Both functions mutate a `*kconfig.ConfigFile`. Tag checks disable a config when the required tag is missing; nil tags disable only `disable-always` entries. Sanitizer minimization computes needed categories from `crash.Type` values, applies disablers, and logs disabled groups through `debugtracer`.

## Risks And Test Signals

Rules are historical and can become stale as kernel/toolchain behavior changes. Command-line string editing for `CMDLINE` assumes quoted values and appends RCU stall suppression before the final quote. `linux_configs_test.go` covers key crash-type preservation and duplicate suppression avoidance.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_configs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_configs_test.go -->
# sources/test-tools/syzkaller/pkg/vcs/linux_configs_test.go

## Purpose

This file tests Linux sanitizer config pruning for different crash types.

## Important APIs, Types, And Functions

`TestDropLinuxSanitizerConfigs` feeds a base config to `setLinuxSanitizerConfigs` and asserts that required configs remain for warnings, KASAN, warning plus KASAN, lockdep, and RCU stall cases. `TestNoDoubleRcuSuppress` ensures the RCU stall suppression command-line parameter is not appended twice. `assertConfigs` checks selected config values.

## Control Flow, State, Dependencies, And Integration

Tests parse in-memory Kconfig data and use `debugtracer.NullTracer`. They inspect `kconfig.ConfigFile` values after mutation.

## Risks And Test Signals

The tests protect high-risk bisection behavior where disabling the wrong instrumentation can hide the bug. They do not cover tag-based config disabling, every crash type predicate, or malformed `CMDLINE` values.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_configs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_patches.go -->
# sources/test-tools/syzkaller/pkg/vcs/linux_patches.go

## Purpose

`linux_patches.go` defines conditional backport rules for Linux bisection and the generic helper that cherry-picks needed fix commits.

## Important APIs, Types, And Functions

`BackportCommit` describes optional `GuiltyHash`, required `FixHash`, and human comment. `linuxFixBackports` applies built-in `pickLinuxCommits` plus extras from a default Linux remote. `BackportCommits` checks whether the guilty commit is present, fetches the fix if needed, detects whether a commit with the same original title is already present, and cherry-picks missing fixes. `pickLinuxCommits` lists known build/boot fixes.

## Control Flow, State, Dependencies, And Integration

The function mutates the repo worktree through `cherryPick` without committing. It uses `Contains`, `fetchRemote`, `Commit`, `GetCommitByTitle`, and title-based duplicate detection with a wider since cutoff. It returns whether any patch was applied.

## Risks And Test Signals

Cherry-pick conflicts, title collisions, missing remotes, and stale hashes can fail bisections. Title-based detection can miss retitled fixes or match unrelated commits. `linux_patches_test.go` covers unconditional and guilty-hash-conditional backport behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_patches.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_patches_test.go -->
# sources/test-tools/syzkaller/pkg/vcs/linux_patches_test.go

## Purpose

This file tests the generic backport helper used by Linux bisection.

## Important APIs, Types, And Functions

`TestFixBackport` creates a fix on a separate branch and verifies `BackportCommits` cherry-picks it into `main`. `TestConditionalFixBackport` creates branches with and without the guilty commit and verifies conditional application based on `GuiltyHash`.

## Control Flow, State, Dependencies, And Integration

Tests use temp Git repos, real file writes, real branch switching, and `osutil.IsExist` to validate worktree effects. They pass an empty remote URL because all commits are local.

## Risks And Test Signals

The tests catch accidental unconditional application of conditional fixes and failure to cherry-pick local fix commits. They do not test duplicate-title skip behavior, remote fetching, conflict handling, or built-in Linux backport list freshness.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_patches_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_test.go -->
# sources/test-tools/syzkaller/pkg/vcs/linux_test.go

## Purpose

`linux_test.go` tests Linux compiler selection rules used for bisection environments.

## Important APIs, Types, And Functions

`TestClangVersion` checks `linuxClangPath` with no tags, `v5.9`, and `v6.15`. `TestGCCVersion` checks `linuxGCCPath` with no tags, `v4.12`, and `v5.16`.

## Control Flow, State, Dependencies, And Integration

Tests use a simple tag map and expected path strings built from a fake binary directory or default compiler path. There is no filesystem access.

## Risks And Test Signals

These tests protect bisection compiler compatibility cutoffs. They are intentionally tied to hard-coded historical rules, so adding new compiler thresholds requires test updates. They do not cover `PreviousReleaseTags` cutoff filtering or `EnvForCommit` as a whole.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/testdata/linux/merge_config.sh -->
# sources/test-tools/syzkaller/pkg/vcs/testdata/linux/merge_config.sh

## Purpose

This shell script is a test fixture replacing Linux `merge_config.sh` behavior for config minimization tests.

## Important APIs, Types, And Functions

The script expects the production-like invocation `merge_config.sh -m -O outdir baseline kernelAdditionsConfig`. It sets `OUTDIR=$3`, writes the contents of `$4` to `$OUTDIR/.config`, appends `$5`, and exits success.

## Control Flow, State, Dependencies, And Integration

It performs simple filesystem writes through shell redirection and command substitution. It depends on bash and `cat`. Integration is as executable testdata for VCS/Linux config code that needs a merge script without invoking the kernel's full script.

## Risks And Test Signals

The script intentionally ignores most real merge semantics, quoting, and error handling. It is only suitable for tests that need concatenation behavior. If argument positions change in callers, the fixture will silently write wrong content or fail.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/testdata/linux/merge_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/testos.go -->
# sources/test-tools/syzkaller/pkg/vcs/testos.go

## Purpose

`testos.go` provides a lightweight repository adapter for syzkaller's synthetic TestOS target, mainly to exercise generic VCS and bisection code without Linux-specific behavior.

## Important APIs, Types, And Functions

`testos` embeds `*gitRepo` and implements `ConfigMinimizer`. `newTestos` builds the adapter. `PreviousReleaseTags` delegates to Git release tags. `EnvForCommit` returns the input kernel config. `Minimize` returns the original config without a baseline, uses the baseline if it still reproduces, simulates failure/success for sentinel baseline strings, or falls back to original. `PrepareBisect` is a no-op.

## Control Flow, State, Dependencies, And Integration

The adapter is returned by `NewRepo` for `targets.TestOS`. It can call the provided predicate for baseline/minimized configs but otherwise keeps behavior deterministic and cheap.

## Risks And Test Signals

This is test scaffolding; production risk is low. It intentionally encodes sentinel strings (`minimize-fails`, `minimize-succeeds`) that tests may rely on. It should not be confused with a real OS implementation.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/testos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/vcs.go -->
# sources/test-tools/syzkaller/pkg/vcs/vcs.go

## Purpose

`vcs.go` defines the public VCS abstraction, shared commit/recipient/bisection types, repository factory functions, patch application, validation predicates, release-tag parsing, and web link generation.

## Important APIs, Types, And Functions

`Repo`, `Bisecter`, and `ConfigMinimizer` define repository capabilities. Data types include `Commit`, `CommitShort`, `RecipientInfo`, `Recipients`, `BisectResult`, `BisectEnv`, and `RepoOpt`. Constructors include `NewRepo`, `NewSyzkallerRepo`, and `NewLKMLRepo`. Utilities include `Patch`, `CheckRepoAddress`, `CheckBranch`, `CheckCommitHash`, `ParseReleaseTag`, `CanonicalizeCommit`, and `CommitLink`/`TreeLink`/`LogLink`/`FileLink`.

## Control Flow, State, Dependencies, And Integration

The file mostly contains pure helpers, except `Patch` and `runSandboxed`, which shell out under sandboxing and mutate the target directory. `NewRepo` selects Linux, Fuchsia, generic Git, or TestOS implementations based on target OS and VM type. Link generation normalizes GitHub SSH URLs and handles GitHub, kernel.org, cgit, and googlesource formats.

## Risks And Test Signals

Regex validators are approximate and may accept/reject edge-case repository addresses or branch names. `Patch` first dry-runs, checks reverse application to detect already-applied patches, then applies for real; sandbox correctness is security-sensitive. `vcs_test.go` covers patch safety, validators, canonicalization, link formats, and Linux maintainer parsing.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/vcs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/vcs_test.go -->
# sources/test-tools/syzkaller/pkg/vcs/vcs_test.go

## Purpose

This test file covers shared VCS helpers that are not specific to `gitRepo` internals.

## Important APIs, Types, And Functions

Tests include `TestPatch`, `TestPatchForbidden`, `TestCanonicalizeCommit`, `TestCheckRepoAddress`, `TestCheckBranch`, `TestCheckCommitHash`, `TestCommitLink`, `TestFileLink`, and `TestParseMaintainersLinux`. `testPredicate` is a table helper.

## Control Flow, State, Dependencies, And Integration

Patch tests use temp directories with and without initialized Git repos and verify content changes plus already-applied detection. Forbidden patch tests target `.git` and path traversal. Link tests verify output for GitHub, kernel.org, googlesource, fuchsia, cgit, git SSH, and unsupported URLs.

## Risks And Test Signals

The tests protect security-sensitive patch path handling and public dashboard link generation. They also fix the approximate validation contract for repository strings, branch names, and hashes. Maintainer parsing tests cover role-to-To/Cc behavior, especially LKML handling.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vcs/vcs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/features.go -->
# sources/test-tools/syzkaller/pkg/vminfo/features.go

## Purpose

`features.go` checks executor/VM support for syzkaller runtime features such as coverage, comparisons, sandboxes, net injection, USB/VHCI/Wi-Fi emulation, and memory dump.

## Important APIs, Types, And Functions

`Feature` stores enabled state, setup requirement, and reason. `Features.Enabled` and `NeedSetup` build bitmasks. `startFeaturesCheck` launches one goroutine per feature and submits a simple program with feature-specific flags. `finishFeatures` merges executor setup info with program-run results and enforces required coverage/memory-dump options. `featureToFlags` maps feature IDs to `ExecEnv`/`ExecFlag`. `featureSucceeded` validates execution and coverage/comparison output.

## Control Flow, State, Dependencies, And Integration

Feature checks run concurrently through `queue.Executor` and communicate over `ctx.features`. Disabled-by-user features still produce reasons. The code sanitizes executor output and requires `FeatureSandboxNone` to work at minimum. It integrates with `Checker.Run` and flatrpc feature descriptors.

## Risks And Test Signals

The `go func()` closure uses `feat` from a range over feature names; in current Go semantics this is safe, but older semantics would capture incorrectly. Unknown features panic. Runtime behavior depends on executor fidelity and feature setup reporting. `vminfo_test.go` exercises all features via synthetic successful queue results.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/linux.go -->
# sources/test-tools/syzkaller/pkg/vminfo/linux.go

## Purpose

`linux.go` extracts Linux-specific VM machine information: required/check files, kernel modules, core kernel text range, CPU info, and KVM module parameters.

## Important APIs, Types, And Functions

`linux.RequiredFiles` and `CheckFiles` list VM files/globs. `machineInfos` returns `linuxReadCPUInfo` and `linuxReadKVMInfo`. `parseModules` parses `/proc/modules`, reads per-module `.text` addresses, adds the core kernel from `_stext`/`_etext`, and sorts modules. `linuxModuleTextAddr`, `linuxParseCoreKernel`, `linuxReadCPUInfo`, `allEqual`, and `linuxReadKVMInfo` implement parsing/formatting.

## Control Flow, State, Dependencies, And Integration

The code operates on the virtual `filesystem` built from `flatrpc.FileInfo`, not live host paths. gVisor and Starnix skip module parsing. CPU info groups repeated keys and prints either a single value or comma-joined differing values. KVM info walks virtual `/sys/module/kvm*/parameters`.

## Risks And Test Signals

Regexes assume Linux `/proc/modules` and kallsyms formats. Module size correction can underflow if addresses are inconsistent. CPU parsing ignores lines without exactly one colon. Tests in `linux_test.go` cover Linux syscall checks, host KVM output formatting, and canned CPU info across architectures.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/linux_syscalls.go -->
# sources/test-tools/syzkaller/pkg/vminfo/linux_syscalls.go

## Purpose

`linux_syscalls.go` implements Linux-specific syscall availability checks. It decides whether syzkaller syscall descriptions should be enabled for a VM based on filesystems, devices, sandbox mode, architecture, kernel version, and trial executions.

## Important APIs, Types, And Functions

`linux.syscallCheck` selects a custom check from `linuxSyscallChecks` or falls back to executing the plain syscall. Custom checks include `linuxSupportedLSM`, `linuxSyzOpenDevSupported`, filesystem/mount checks, socket checks, KVM arch checks, pkeys, net injection, USB/VHCI/Wi-Fi/USBIP, BTF, ublk, genetlink, and kernel-version requirements. `matchKernelVersion` parses `/proc/version`.

## Control Flow, State, Dependencies, And Integration

The checks use `checkContext` helpers to read VM snapshot files or submit tiny executor programs. Many pseudo-syscalls are allowed unconditionally, while others require root/sandbox none or device nodes. The map keys are syscall base names, so variants share logic.

## Risks And Test Signals

Several paths panic if syscall descriptions violate assumptions such as constant socket family or string filesystem arguments. Device checks may be time-sensitive because some nodes appear only after setup. Kernel version parsing rejects minor `0`, which may be intentional but is strict. `vminfo/linux_test.go` exercises mount filtering, KVM arch disabling, filesystem checks, and feature success under synthetic executor results.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/linux_syscalls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/linux_test.go -->
# sources/test-tools/syzkaller/pkg/vminfo/linux_test.go

## Purpose

This file tests Linux VM-info syscall filtering and machine-info formatting.

## Important APIs, Types, And Functions

`TestLinuxSyscalls` builds a Linux/amd64 checker with virtual `/proc/version` and `/proc/filesystems`, feeds successful executor results, and verifies expected disabled calls. `TestReadKVMInfo` validates host KVM info formatting on Linux. `TestCannedCPUInfoLinux`, `checkCPUInfo`, `cannedTest`, and `cpuInfoTests` validate CPU info parsing for canned and host data.

## Control Flow, State, Dependencies, And Integration

`TestLinuxSyscalls` runs `Checker.Run` concurrently with `createSuccessfulResults`, so executor queue behavior is part of the signal. CPU tests build virtual filesystems from canned data. Host KVM/CPU checks are conditional on runtime OS.

## Risks And Test Signals

The test catches accidental broad disabling of Linux syscalls, especially mount variants and architecture-specific KVM calls. CPU info expectations are architecture-aware and protect output shape. Host-dependent portions may reveal environmental issues rather than pure logic regressions.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/netbsd.go -->
# sources/test-tools/syzkaller/pkg/vminfo/netbsd.go

## Purpose

`netbsd.go` provides NetBSD-specific syscall support checks on top of the default no-op checker.

## Important APIs, Types, And Functions

`netbsd` embeds `nopChecker`. Its `syscallCheck` handles `openat` through shared `supportedOpenat`, handles USB connect/disconnect pseudo-syscalls by checking root access to `/dev/vhci0`, and treats all other calls as supported.

## Control Flow, State, Dependencies, And Integration

The file integrates through `New` when `cfg.Target.OS` is NetBSD. It uses `checkContext` runtime helpers, so support depends on executor results and VM file/device availability.

## Risks And Test Signals

Coverage is intentionally narrow; unsupported NetBSD-specific resources not modeled here may remain enabled. Generic `TestSyscalls` in `vminfo_test.go` verifies that, under successful synthetic executor results, no NetBSD calls are unexpectedly disabled.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/openbsd.go -->
# sources/test-tools/syzkaller/pkg/vminfo/openbsd.go

## Purpose

`openbsd.go` provides OpenBSD-specific syscall support checks on top of the default no-op checker.

## Important APIs, Types, And Functions

`openbsd` embeds `nopChecker`. Its `syscallCheck` special-cases `openat` through `supportedOpenat` and treats all other calls as supported.

## Control Flow, State, Dependencies, And Integration

The implementation is selected by `New` for OpenBSD targets. It relies on `checkContext` for any `openat` trial execution needed by descriptions with absolute path constants.

## Risks And Test Signals

The narrow implementation can leave unsupported OpenBSD-specific pseudo-devices enabled if not described through `openat`. Generic `TestSyscalls` covers the no-disable path under synthetic success but not real VM behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/syscalls.go -->
# sources/test-tools/syzkaller/pkg/vminfo/syscalls.go

## Purpose

`syscalls.go` orchestrates syscall support checking for a target VM. It provides the shared runtime primitives OS-specific checkers use to read VM files and execute small test programs.

## Important APIs, Types, And Functions

`checkContext` stores context, checker implementation, config, target, executor, virtual filesystem, result channels, and feature channel. `do` starts one goroutine per syscall, starts feature checks, submits required glob requests, collects syscall results, and finishes feature evaluation. Helpers include `rootCanOpen`, `canOpen`, `canWrite`, `supportedSyscalls`, `supportedOpenat`, `allOpenModes`, `callSucceeds`, `execCall`, `anyCallSucceeds`, sandbox guards, `val`, `execRaw`, `readFile`, `alwaysSupported`, and `extractStringConst`.

## Control Flow, State, Dependencies, And Integration

`do` builds a virtual filesystem from `flatrpc.FileInfo`, updates target glob expansions from executor glob requests, and returns enabled/disabled syscall maps plus feature results. `execRaw` chunks generated calls, deserializes them with the target, submits queue requests, and substitutes empty call info on failures.

## Risks And Test Signals

Goroutine-per-syscall behavior depends on executor progress; a blocked executor can block checks. Several helpers panic on malformed target descriptions or missing constants. Failed executor runs are treated as call failures, which can disable syscalls conservatively. `vminfo_test.go` limits program count and checks deduplication indirectly.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/syscalls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/vminfo.go -->
# sources/test-tools/syzkaller/pkg/vminfo/vminfo.go

## Purpose

`vminfo.go` defines the public VM-info checker. It extracts machine information from fetched VM files and checks enabled syscalls/features through a queue executor.

## Important APIs, Types, And Functions

`KernelModule`, `Checker`, and `Config` are the public core types. `New` selects OS-specific checker implementations and wraps a plain queue executor with deduplication. `MachineInfo` parses modules and formatted machine info sections. `Run` executes syscall/feature checks and maps context cancellation to `ErrAborted`. `Next` implements `queue.Source`. `filesystem` models fetched files with `ReadFile` and `ReadDir`; `nopChecker` is the default OS implementation.

## Control Flow, State, Dependencies, And Integration

Callers fetch files listed by `RequiredFiles`/`CheckFiles`, feed them into `MachineInfo` and `Run`, and drive queue requests by consuming `Checker.Next`. Persistent state is the deduplicating queue and checker config. `MachineInfo` ignores missing optional machine-info files but returns other errors.

## Risks And Test Signals

The virtual filesystem `ReadDir` does not sort, so formatted KVM output order can vary. `Run` returns `ErrAborted` after `cc.do` if context is canceled, even if partial data existed. Tests in `vminfo_test.go` cover host file shape, generic syscall support, queue request generation, and synthetic executor success.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/vminfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/vminfo_test.go -->
# sources/test-tools/syzkaller/pkg/vminfo/vminfo_test.go

## Purpose

This file tests the VM-info checker across host machine-info collection and non-Linux syscall checking.

## Important APIs, Types, And Functions

`TestHostMachineInfo` reads host-required files and runs `MachineInfo`. `TestSyscalls` iterates all non-Linux targets and verifies synthetic successful execution enables every syscall. Helpers include `allFeatures`, `createSuccessfulResults`, `hostChecker`, `testConfig`, `readFiles`, and `readFile`.

## Control Flow, State, Dependencies, And Integration

`createSuccessfulResults` drives the checker as a `queue.Source`, responding to program and glob requests, and panics if more than 1000 requests are generated. Host checks read real files where available. Target configs use all non-disabled syscalls and all features.

## Risks And Test Signals

The request-count guard protects deduplication and catches accidental explosion in generated test programs. Host tests are environment-dependent and log read errors rather than failing on missing files. Generic syscall tests do not validate real OS availability because all executor results are synthetic successes.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/vminfo/vminfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/alloc.go -->
# sources/test-tools/syzkaller/prog/alloc.go

## Purpose

`alloc.go` implements internal memory and virtual-memory-area allocation helpers used during syzkaller program generation.

## Important APIs, Types, And Functions

`memAlloc` tracks allocated byte ranges using a two-level bitmap, one bit per 64-byte granule. `newMemAlloc`, `noteAlloc`, `alloc`, `bankruptcy`, `pos`, `set`, and `get` manage allocation. `vmaAlloc` tracks allocated pages with `used` and `m` and provides `newVmaAlloc`, `noteAlloc`, and randomized `alloc`.

## Control Flow, State, Dependencies, And Integration

`memAlloc.alloc` normalizes zero size/alignment, scans from the last position for that alignment, marks a found range, and resets all allocations through `bankruptcy` if full before retrying. `vmaAlloc.alloc` either chooses near the end of address space or near existing used pages, records allocation, and returns the page. State is in-memory and per program-generation instance.

## Risks And Test Signals

`memAlloc` panics if total size exceeds 16 MiB or is not aligned to L0 memory. It assumes allocation requests fit; if `size > ma.size`, unsigned underflow in `end := ma.size - size` would be dangerous. `vmaAlloc.alloc` can underflow for random end placement if `size` approaches `numPages` and `r.rand(4)` is nonzero; later bounds checks panic. `alloc_test.go` covers deterministic memory allocation and randomized VMA smoke behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/alloc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/alloc_test.go -->
# sources/test-tools/syzkaller/prog/alloc_test.go

## Purpose

This file tests internal program memory allocation helpers.

## Important APIs, Types, And Functions

`TestMemAlloc` defines table-driven sequences of `noteAlloc` and `alloc` operations, checking sequential allocation, pre-reserved ranges, and alignment behavior. `TestVmaAlloc` creates a test target and random generator, then performs 30 VMA allocations as a smoke test.

## Control Flow, State, Dependencies, And Integration

`TestMemAlloc` uses negative `size` values to mean allocation requests and positive values to mean reservations. It expects exact addresses from `memAlloc.alloc`. `TestVmaAlloc` uses `testutil.RandSource`, so seeds are logged and can be fixed with `SYZ_SEED`.

## Risks And Test Signals

The memory allocation test catches bitmap scanning, granule rounding, and last-position alignment regressions. The VMA test mainly catches panics and gross bounds errors; it does not assert distribution or exact pages because allocation is randomized.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/alloc_test.go -->
