# Research: subset-b-009478

Grouped research for the requested syzkaller manager, mgrconfig, osutil, and report files. Each section preserves its source path and is bounded by the reconciliation markers used to split per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/crash_test.go -->
# sources/test-tools/syzkaller/pkg/manager/crash_test.go

Purpose: Exercises `CrashStore` behavior for crash persistence, listing, repro report assembly, memory dump handling, and subsystem extraction from saved reports. It is a manager package test file, so it validates the public behavior of crash storage rather than defining production APIs.

Important APIs and functions: `TestCrashList`, `TestEmptyCrashList`, `TestMaxCrashLogs`, `TestCrashRepro`, `TestCrashMemoryDump`, and `TestGetSubsystems`. These tests instantiate `CrashStore`, call `SaveCrash`, `BugList`, `BugInfo`, `SaveRepro`, `Report`, and the internal `getSubsystems`, and validate `crashHash`-based addressing.

Control flow and state: Tests create temporary workdirs, save synthetic reports under stable titles, and then inspect derived lists or report payloads. `TestMaxCrashLogs` stresses retention by saving 20 crashes while expecting only five crash entries to remain. `TestCrashRepro` verifies that a saved repro enriches the final report with tag, syz repro, C repro, and kernel report. `TestCrashMemoryDump` writes a fake vmcore and expects it copied into crash storage.

Dependencies and integration points: Uses `mgrconfig`, `report.NewReporter`, `repro.Result`, `prog.Prog`, `subsystem.MakeExtractor`, and `osutil.WriteFile`. The four `testdata/*` crash reports feed subsystem extraction, linking this test to report parsing and subsystem path rules.

Risks: The tests depend on filesystem ordering and crash hash layout through public behavior. Subsystem extraction correctness depends on report symbolization/guilty-file heuristics, so fixture drift can cause unrelated failures. Memory dump tests only validate copy/link existence, not cleanup or large dump behavior.

Test signals: Strong regression coverage for `CrashStore` persistence contracts, crash-log retention, repro report formatting inputs, and subsystem mapping for block, HID/USB, mm, and nil cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/crash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/diff_test.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/diff_test.go

Purpose: Provides the test harness for the patch-diff fuzzer package. It defines `testEnv`, mock kernels, mock repro runners, and repro callbacks used by `manager_test.go`.

Important APIs and types: `testEnv` owns `context`, `diffContext`, base/new `MockKernel`, and a completion channel. `newTestEnv` wires default `DiffFuzzerStore`, `PatchedOnly`, `BaseCrashes`, and a mock runner. `MockKernel` implements the package `Kernel` interface: `Loop`, `Crashes`, `TriageProgress`, `ProgsPerArea`, `CoverFilters`, `Config`, `Pool`, `Features`, and `Reporter`. `mockRunner` implements the internal `runner` interface, and `mockRepro`/`mockReproCallback` emulate `repro.Run`.

Control flow and state: Tests call `env.start()` to run `diffContext.Loop` in a goroutine, inject crash reports into `CrashesCh`, and use `waitForStatus` to poll `DiffFuzzerStore.List`. The new kernel is given a one-VM dispatcher and blank manager config, enough for repro loop construction without real VM boot.

Dependencies and integration points: Imports `flatrpc`, manager store/repro types, `mgrconfig`, `report`, `repro`, `prog/test`, and VM dispatcher. It decouples diff state-machine tests from real RPC servers and VMs while preserving the production interfaces.

Risks: Polling waits can hide race-sensitive failures until timeout. The mock dispatcher has minimal behavior, so it does not validate real VM reservation interactions. `ReporterVal` is often nil, which is acceptable in mocked paths but not representative of production repro execution.

Test signals: Establishes deterministic scaffolding for diff-fuzzer tests and validates that the package can be exercised through interfaces rather than concrete kernel contexts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/kernel.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/kernel.go

Purpose: Implements one side of patch-diff fuzzing: a `kernelContext` that runs a manager RPC server, VM dispatcher, focused fuzzer, coverage filter setup, and crash extraction for either the base or patched kernel.

Important APIs and types: `kernelContext` implements the `Kernel` interface consumed by `diffContext` and `reproRunner`. `setup` builds the reporter, RPC server, VM pool, dispatcher, and report generator cache. Public interface methods expose crashes, triage progress, focus-area stats, coverage filters, config, pool, features, and reporter. RPC-manager callbacks include `MachineChecked`, `MaxSignal`, `BugFrames`, and `CoverageFilter`.

Control flow: `Loop` starts RPC listening, RPC serving, VM dispatcher looping, and boot-error draining under an errgroup. `MachineChecked` records executor features, validates enabled syscalls, creates either a local fuzzer source or injected queue source, and wraps it with default executor options. `setupFuzzer` creates a focused corpus, disables fault injection for reproducibility, pulls candidate seeds, filters disabled calls, feeds candidates, and periodically distributes coverage signal deltas. VM instances are handled by `fuzzerInstance` and `runInstance`, which forward RPC, copy the executor, run the executor in runner mode, stop fuzzing after early crash detection, and send the first report to `crashes`.

State and persistence: Uses atomic pointers for the current fuzzer and candidate counts, buffered crash channel, stored `features`, `coverFilters`, optional shared/duplicated queue sources, and HTTP atomic pointers. It does not persist directly; persistence is handled by manager stores reached through higher-level loops.

Dependencies and integration: Integrates `corpus`, `fuzzer`, `queue`, `rpcserver`, `signal`, `vminfo`, `vm/dispatcher`, `report`, and manager coverage helpers. HTTP integration publishes fuzzer, enabled syscalls, corpus, modules, report generator, and executor cover filters.

Risks: Candidate delivery blocks until `setupFuzzer` receives from `kc.candidates`; cancellation must be respected. Coverage filtering must be initialized before patched-coverage monitoring expects populated areas. The fuzzer pointer is nil until machine check completes, so triage progress must handle startup. Boot errors are logged and discarded, not reported as diff bugs.

Test signals: Indirectly covered by diff harness mocks rather than real VM tests. Behavior relies on package-level manager and VM tests elsewhere.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/kernel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/manager.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/manager.go

Purpose: Orchestrates differential patch fuzzing across base and patched kernels. It loads seeds, runs both kernel contexts, feeds patched programs into the base queue, schedules reproductions, verifies whether reproducers crash the base kernel, and reports patched-only bugs.

Important APIs and types: `Config` contains channels (`PatchedOnly`, `BaseCrashes`), store, artifact directory, triage and patched-coverage deadlines, external `IgnoreCrash`, and injectable `runner`/`runRepro`. `Bug` carries a patched report and repro. `Run` is the package entry point. `Kernel` abstracts concrete kernel contexts. `diffContext` owns runtime state and implements `manager.ReproManagerView` through `NeedRepro`, `RunRepro`, and `ResizeReproPool`.

Control flow: `Run` sets up base/new kernels, loads immutable seeds for the patched kernel, creates a random queue so patched-generated programs can be duplicated to the base source, initializes repro callbacks, optionally creates an HTTP server, then runs `diffContext.Loop`. The loop starts the HTTP server, delayed repro loop after 90% triage or timeout, patched-coverage monitor after 99% triage, and both kernel loops. It handles base crashes, patched crashes, repro completion on patched, and base-verification runner results.

State and persistence: `DiffFuzzerStore` receives `PatchedCrashed`, `BaseCrashed`, `BaseNotCrashed`, `UpdateStatus`, and `SaveRepro` calls. `reproAttempts` is mutex-protected and caps attempts per title. Status moves through pending/verifying/completed/ignored. Patched-only bugs are emitted only after a reliable patched repro does not crash base.

Dependencies and integration: Uses manager repro loop, report/repro packages, flatrpc features, VM dispatcher capacity, stats logging, seed loading, HTTP dashboard, and optional external ignore service.

Risks: False positives are mitigated but still depend on repro reliability and base runner behavior. External `IgnoreCrash` failures are logged and treated as non-ignore. `NeedRepro` uses a background timeout rather than caller context. A typo in a log message is harmless but visible. Patched-coverage monitoring assumes focus areas were prepared.

Test signals: `manager_test.go` covers base-crash interception, external ignore, successful patched-only flow, failed repro, base crash after repro, early base crash dedupe, and retry cap behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/manager_test.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/manager_test.go

Purpose: Validates the diff-fuzzer state machine under mocked kernels, repro callbacks, and base-verification runners.

Important tests: `TestNeedReproForTitle` verifies title filters for no output, SYZ failures, lost connection, stalls, and real kernel warnings/KASAN bugs. `TestDiffBaseCrashInterception` checks base crashes are surfaced on `BaseCrashes`. `TestDiffExternalIgnore` ensures ignored patched crashes are not reproduced. `TestDiffSuccess` checks patched crash -> repro -> base no-crash -> `PatchedOnly`. `TestDiffFailNoRepro` marks failed repro attempts completed. `TestDiffFailBaseCrash` reports base-affected repros instead of patched-only. `TestDiffFailBaseCrashEarly` avoids repro when base already saw the title. `TestDiffRetryRepro` checks retries until `maxReproAttempts`, then ignored.

Control flow and state: Tests finish corpus triage by setting mock progress to 1.0, start the diff loop, inject crash reports into channels, and assert store statuses or emitted channels. Repro callbacks and runner callbacks simulate success, failure, and base crash.

Dependencies and integration: Uses the harness from `diff_test.go`, `manager.DiffBugStatus*`, `report.Report`, and `repro.Result`. These tests pin the contract between `diffContext`, `DiffFuzzerStore`, and `ReproLoop`.

Risks: The tests focus on control-flow decisions, not real kernel execution, coverage filters, HTTP output, or filesystem artifact content. The retry test depends on timing and buffered channels but has a generous timeout.

Test signals: Strong coverage of high-risk duplicate/ignore/retry paths that prevent wasting VM time and prevent reporting bugs that also affect the base kernel.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/patch.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/patch.go

Purpose: Converts patch information and symbol-hash differences into manager focus areas so patch fuzzing biases generation toward modified functions, directly changed files, and source files transitively affected by changed headers.

Important APIs: `PatchFocusAreas` mutates `cfg.Experimental.FocusAreas`. `affectedFiles` extracts changed files from git diffs and greps `.c` files including changed headers. `modifiedSymbols` compares base and patched symbol hash maps and returns changed symbol names if the changed-symbol ratio is specific enough.

Control flow: `PatchFocusAreas` first adds a high-weight `symbols` area for modified functions, then a medium-weight `files` area for directly changed patch files, then a lower-weight `included` area for `.c` files including changed headers. If any focus area exists, it appends a final empty-filter area with weight 1.0 so the rest of the kernel remains fuzzable. `affectedFiles` skips transitive header expansion if `KernelSrc` is empty and suppresses very widespread headers after 50 matches. `modifiedSymbols` returns nil once changes exceed 5% of patched symbols.

State and persistence: No persistence; the function mutates in-memory manager config before coverage filter preparation.

Dependencies and integration: Uses `vcs.ParseGitDiff`, `osutil.GrepFiles`, `mgrconfig.FocusArea`, and manager coverage-filter logic later consumed by `kernelContext.CoverageFilter`.

Risks: Header include detection is textual and only looks for `<trimmed-header>`, so quoted includes or generated dependencies can be missed. The 5% symbol threshold avoids overbroad focus but can discard useful symbol focus for medium-sized patches. Direct file names must match coverage report file naming.

Test signals: `patch_test.go` covers modified function focus, direct changed files, header transitive include expansion, fallback area, and symbol threshold behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/patch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/patch_test.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/patch_test.go

Purpose: Tests patch-derived focus-area construction and modified-symbol filtering.

Important tests and helpers: `TestPatchFocusAreas` creates a temporary kernel tree with one header and `.c` files, builds synthetic git diffs for a `.c` file and a header, modifies dummy symbol hashes, and asserts the exact focus-area sequence. `dummySymbolHashes` creates 100 stable symbol hashes so small deltas stay below threshold. `TestModifiedSymbols` validates both over-threshold suppression and sorted below-threshold output.

Control flow and state: The test mutates a `mgrconfig.Config` in place through `PatchFocusAreas` and checks that focus areas are appended with names `symbols`, `files`, `included`, and the final empty fallback. It also validates sorted direct and transitive file lists.

Dependencies and integration: Uses `osutil.FillDirectory` for fixture setup, `mgrconfig.FocusArea`/`CovFilterCfg` for expected values, and testify assertions. The synthetic diff format verifies integration with `vcs.ParseGitDiff` without requiring a git repository.

Risks: The test encodes exact weights and area ordering, so intended tuning changes require updates. It covers only one header include style and does not exercise the widespread-header cutoff.

Test signals: Provides high confidence that patch focus metadata reaches the manager config in the shape expected by coverage filtering.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/patch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/repro.go -->
# sources/test-tools/syzkaller/pkg/manager/diff/repro.go

Purpose: Verifies patched-kernel reproducers against the base kernel to determine whether a crash is patch-specific or also affects the base.

Important APIs and types: `reproRunner` implements the internal `runner` interface with `Run` and `Results`. `reproRunnerResult` carries the patched repro report, optional base crash report, repro object, and whether the repro was a full repro. Constants `reliabilityCutOff` and `reliabilityThreshold` control how many base runs are required.

Control flow: `Run` skips reproducers below 40% reliability. Reproducers at or above 80% reliability run three times; lower but accepted reproducers run six times. For each run it reserves base VMs according to concurrent runner count, copies repro options, forces repeated execution, forces threaded mode two out of every three runs, then uses `instance.SetupExecProg` and `RunSyzProg`. Any base crash is enough to mark the bug as affecting base, regardless of exact title.

State and persistence: Maintains a `running` atomic counter to reserve VMs in the base dispatcher and emits results over a buffered `done` channel. It does not write artifacts; `diffContext.handleReproResult` updates store state.

Dependencies and integration: Uses `Kernel` for config/reporter/pool access, `instance` for execprog setup, `repro.Result` options/programs, and VM dispatcher pool execution.

Risks: Run errors do not increment `doneRuns`, so persistent VM/setup errors can loop until context cancellation. Accepting any base crash minimizes false patched-only reports but can hide title-specific differences. Reliability thresholds are policy constants with probabilistic assumptions.

Test signals: Diff manager tests mock this runner; direct VM behavior is not covered in this file’s tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff/repro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff_store.go -->
# sources/test-tools/syzkaller/pkg/manager/diff_store.go

Purpose: Provides an in-memory plus filesystem artifact store for patch-diff fuzzing results. It tracks per-title base and patched crash counts, verification status, repro files, repro logs, reports, and crash logs.

Important APIs and types: `DiffBugStatus` defines `pending`, `verifying`, `completed`, and `ignored`. `DiffBug` has `PatchedOnly` and `AffectsBoth` classifiers. `DiffBugInfo` records counts, a base-not-crashed proof, and relative artifact paths. `DiffFuzzerStore` exposes `UpdateStatus`, `BaseCrashed`, `EverCrashedBase`, `BaseNotCrashed`, `PatchedCrashed`, `SaveRepro`, `List`, and `PlainTextDump`.

Control flow and state: All mutations go through `patch`, which initializes the `bugs` map and locks `mu`. `BaseCrashed` marks completed and increments base count; `BaseNotCrashed` records proof only if no base crash exists. `PatchedCrashed` increments patched count and saves first crash log. `SaveRepro` stores crash logs using Unix timestamp names, switches to repro title when the repro title differs, and stores syzkaller repro plus stats log.

Persistence: Files are saved under `BasePath/crashes/<crashHash(title)>/<name>`, while stored paths are relative (`crashes/...`). File writes use `osutil.MkdirAll` and `osutil.WriteFile`; errors are ignored by `saveFile`, which is a risk.

Dependencies and integration: Consumed by diff manager and HTTP dashboard diff tables. Reuses `crashHash` and `reproFileName` from manager crash storage.

Risks: Store is not durable across manager restart because the bug map is not reloaded from disk. Timestamp filenames can collide if multiple saves for the same title occur within one second. Ignoring write errors can make UI paths point at missing files.

Test signals: Indirectly covered by diff manager tests for status transitions; no dedicated persistence tests in this shard.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/diff_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/http.go -->
# sources/test-tools/syzkaller/pkg/manager/http.go

Purpose: Implements the syz-manager HTTP dashboard and API surface for runtime status, crashes, corpus, coverage, VM state, job state, raw files, and patch-diff fuzzing summaries.

Important APIs and types: `HTTPServer` owns config, start time, crash/diff stores, repro loop, VM pools, pause callback, and atomic pointers for corpus, fuzzer, coverage, and enabled syscalls. `CoverageInfo` carries modules, report generator, and executor cover filter. UI data types include `UISummaryData`, `UICrashType`, `UIDiffBug`, `UIVMData`, `UISyscallsData`, `UICorpusPage`, `UIRawCoverPage`, and `UIJobList`.

Control flow: `Serve` registers compressed handlers on the default HTTP mux and shuts down when context ends. `httpMain` builds the summary page from stats, crash store, repro loop, subsystem filters, and diff store. `httpAction` toggles expert/pause state and redirects through `localRedirectURL` to prevent open redirects. Config/stats/syscalls/VM handlers render JSON or templates. Corpus handlers list, download, fetch, and debug inputs. Coverage handlers require initialized coverage and corpus, build `cover.HandlerParams`, optionally filter PCs, serialize programs, and dispatch to report-generator methods for HTML/text/JSONL outputs. File/report handlers restrict ids/paths and expose saved crash artifacts. `httpAddCandidate` accepts multipart seed uploads and adds enabled-call-only candidates to the fuzzer. Diff handlers classify store entries into patched-only, affects-both, and in-progress tables. Job handlers expose running fuzzer job details.

State and persistence: The server reads persistent crash/corpus files from `Cfg.Workdir`, but mostly presents atomic in-memory manager state. It can reset cached coverage generator on `flush` and mutate pause/expert flags.

Dependencies and integration: Integrates `corpus`, `cover`, `fuzzer`, `html/pages`, `prometheus`, `report`, `stat`, `vcs`, `prog`, `vm/dispatcher`, crash store, diff store, and report generator cache.

Risks: Uses global `http.Handle`, so multiple servers in one process can collide. `httpAddCandidate` assumes `Fuzzer.Load()` is non-nil. `httpFile` allows only `crashes/` and `corpus/` prefixes after `filepath.Clean`, but path traversal must remain carefully reviewed. Coverage generation can be expensive; large program serialization strips filesystem images after 100 MB.

Test signals: `http_test.go` executes all registered templates with random data and checks redirect hardening.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/http_test.go -->
# sources/test-tools/syzkaller/pkg/manager/http_test.go

Purpose: Provides focused tests for HTTP template validity and same-site redirect protection.

Important tests: `TestHttpTemplates` iterates over `templTypes`, fills each template data type with randomized values from `testutil.RandValue`, and executes the template into `io.Discard`. `TestLocalRedirectURL` validates accepted local paths and rejection of absolute URLs, protocol-relative URLs, slash/backslash variants, and `javascript:` strings.

Control flow and state: Template registration happens at package init through `createPage`, which appends each template/data pair into `templTypes`. The redirect test calls the pure helper `localRedirectURL`.

Dependencies and integration: Ties the embedded manager HTML templates to their Go UI structs. The redirect test protects `httpAction`, which redirects after expert/pause actions.

Risks: Random data checks template execution but not semantic rendering, browser behavior, route coverage, or handler status codes. Redirect validation currently allows only one path segment with word/dot/hyphen characters and optional query; expanding allowed URLs needs test updates.

Test signals: Good guard against template field drift and open-redirect regressions in the action endpoint.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/http_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/report_generator.go -->
# sources/test-tools/syzkaller/pkg/manager/report_generator.go

Purpose: Wraps lazy initialization and caching of `cover.ReportGenerator` for coverage reports, with explicit module initialization and reset support.

Important APIs and types: `ReportGeneratorWrapper` stores manager config, kernel modules, a mutex, initialization flag, and cached generator. `ReportGeneratorCache` constructs the wrapper. `Get` returns a cached or newly created generator. `Init` records modules and marks initialized. `Reset` drops the cached generator. `CoverToPCs` converts raw coverage PCs to previous-instruction PCs.

Control flow and state: `Get` locks, rejects calls before `Init`, and lazily calls `cover.MakeReportGenerator`. `Init` panics on double initialization to catch inconsistent module discovery. `Reset` is used by HTTP coverage `flush` to force rebuilding and release memory. `CoverToPCs` loops raw PCs through `backend.PreviousInstructionPC` using the target and VM type from config.

Dependencies and integration: Used by `kernelContext.CoverageFilter` to initialize filters and by HTTP coverage handlers to generate HTML/text/JSONL coverage reports. Depends on `cover`, `cover/backend`, `mgrconfig`, `vminfo`, and logging.

Risks: Double `Init` panic is intentional but can crash the manager if module setup is retried. `Get` serializes generator creation and may block coverage requests. Reset while another caller uses a returned generator is safe for the pointer but can increase memory churn.

Test signals: No direct tests in this shard; exercised indirectly by manager coverage paths and HTTP template coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/report_generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/repro.go -->
# sources/test-tools/syzkaller/pkg/manager/repro.go

Purpose: Defines manager crash/repro data structures and the generic reproduction scheduler used by normal manager mode and patch-diff mode.

Important APIs and types: `ReproResult` captures the original crash, syz repro, strace result, stats, and error. `Crash` wraps `report.Report` with source flags, manual/full repro flags, ext request id, tail reports, and memory dump path. `Crash.FullTitle` creates a stable scheduling key. `ReproManagerView` abstracts manager callbacks. `ReproLoop` owns queue, running set, attempt counts, VM slot channel, and stats.

Control flow: `NewReproLoop` initializes stats and capacity. `Enqueue` records dedupe in `onlyOnce` mode, appends a crash, and pings the loop. `popCrash` selects the best runnable crash: full repros first, fewer attempts first, manual before automatic, non-hub before hub, and never same title while already reproducing. `Loop` seeds reproduction slots based on `calculateReproVMs`, repeatedly selects needed crashes, waits for a slot, marks them reproducing, adjusts reserved VM count, and runs `handle` in a goroutine. On completion it clears state, releases slot, and pings the queue. `adjustPoolSizeLocked` reserves roughly 1.33 VMs per unique active/pending title.

State and persistence: All scheduling state is in memory under `mu`. Persistence of repro artifacts is delegated to the concrete manager’s `RunRepro` path.

Dependencies and integration: Used by `diffContext`, HTTP dashboard (`Reproducing`, `Empty`, `CanReproMore`), manager crash handling, `report`, `repro`, and `stat`.

Risks: `CanReproMore` reads channel length without lock and is advisory only. Queue priority is O(n). A manager callback that blocks indefinitely consumes slots until context cancellation. Same-title serialization prevents redundant work but can delay independent crashes with identical titles.

Test signals: `repro_test.go` covers scheduling capacity, order, dedupe race with `NeedRepro`, cancellation, and skipping unneeded queued crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/repro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/repro_test.go -->
# sources/test-tools/syzkaller/pkg/manager/repro_test.go

Purpose: Tests the generic `ReproLoop` scheduler behavior with a mock `ReproManagerView`.

Important tests and helpers: `TestReproManager` checks initial capacity, VM reservation scaling, running set, and shutdown to zero reservations. `TestReproOrder` verifies manual dashboard crashes are prioritized over ordinary dashboard, which are prioritized over hub crashes, and that repeat entries can be processed after prior runs finish. `TestReproRWRace` validates same-title serialization and `NeedRepro` rechecking after a repro appears. `TestCancelRunningRepro` verifies loop exit while a repro is running. `TestEnqueueTriggersRepro` checks that the loop skips queued crashes that no longer need repro and reaches a later needed crash. `reproMgrMock` records reserved VMs and exposes run callbacks.

Control flow and state: Tests enqueue crashes, run `Loop` in goroutines, receive `runCallback` objects from the mock, then unblock them by sending `ReproResult`. `onVMShutdown` polls reservation count until the loop returns reserved VMs.

Dependencies and integration: Uses `report.Report`, context cancellation, atomics, and testify assertions. It validates scheduler-to-manager callback contracts without real repro execution.

Risks: Some tests rely on goroutine scheduling and polling. They do not validate `calculateReproVMs` over many pool sizes or HTTP reporting of repro state.

Test signals: Strong coverage for concurrency-sensitive scheduler decisions, especially same-title races and dynamic queue rechecking.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/repro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/seeds.go -->
# sources/test-tools/syzkaller/pkg/manager/seeds.go

Purpose: Loads and prepares initial fuzzing candidates from the corpus database and built-in syzkaller seed programs, parses seed requirements, filters disabled syscalls, and periodically marks subsets for re-minimization/re-smashing.

Important APIs and types: `Seeds` returns `CorpusDB`, `Fresh`, and `Candidates`. `LoadSeeds` is the main entry. `readInputs` reads DB records and `sys/<targetOS>/test` seed files concurrently. `CurrentDBVersion` and `versionToFlags` define corpus flag migration. `ParseSeed`, `ParseSeedWithRequirements`, `parseRequires`, `checkArch`, `MatchRequirements`, and `parseProg` handle seed parsing. `FilteredCandidates`, `FilterCandidates`, `ReminimizeSubset`, and `ResmashSubset` post-process candidates.

Control flow: `LoadSeeds` opens `corpus.db`, starts worker goroutines based on `GOMAXPROCS`, parses DB and seed inputs, classifies broken/skipped inputs, deduplicates seeds already in corpus by hash, deletes broken DB entries when mutable, flushes DB, discards record data to save memory, and returns candidates. `parseProg` checks requirements before strict/non-strict deserialization, rejects too-long programs and any call with `fail_nth`. `FilterCandidates` removes disabled calls in place and optionally clears minimization for changed corpus programs.

State and persistence: Reads and mutates `corpus.db`; deletes broken corpus records only when `immutable` is false. Candidate flags encode whether programs came from corpus, were minimized, or were smashed.

Dependencies and integration: Used by normal and diff managers to seed fuzzers. Depends on `db`, `fuzzer`, `hash`, `mgrconfig`, `osutil`, and `prog`.

Risks: Requirement parsing is comment/text based. Filtering mutates program objects in place. Random subset resets are nondeterministic by design. Skipped seeds are not errors, while broken corpus entries can be deleted.

Test signals: `seeds_test.go` covers requirement architecture handling; broader behavior is covered through manager/fuzzer integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/seeds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/seeds_test.go -->
# sources/test-tools/syzkaller/pkg/manager/seeds_test.go

Purpose: Tests seed `# requires:` architecture matching.

Important test: `TestRequires` parses positive and negative architecture requirements and checks `checkArch` behavior for `amd64` and `riscv64`.

Control flow and state: The test calls `parseRequires` on synthetic comment lines and then evaluates the resulting map. It validates that `arch=amd64` admits only amd64, and that negative architecture requirements can exclude riscv64 while allowing amd64.

Dependencies and integration: Directly covers helpers used by `parseProg` before seed deserialization. This is important because requirements are checked early to avoid deserializing unsupported programs on the wrong architecture.

Risks: It does not cover `MatchRequirements` combinations, manual constraints, strict vs non-strict deserialization, long program rejection, `fail_nth`, corpus DB cleanup, or candidate flag migration.

Test signals: Narrow but useful coverage for architecture gating in seed files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/seeds_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/0 -->
# sources/test-tools/syzkaller/pkg/manager/testdata/0

Purpose: Crash-report fixture used by `TestGetSubsystems` in `crash_test.go`. It represents a Linux hung task / lock contention report whose stack includes block-layer paths.

Important content: The report begins with a blocked `syz.*` task, shows `bdev_open`, `blkdev_open`, `block/bdev.c`, and `block/fops.c`, then includes extensive lock and NMI backtrace data plus the report separator marker.

Control flow and state: The fixture is read as bytes, saved as a crash report through `CrashStore.SaveCrash`, then fed into `getSubsystems`. The expected subsystem result is `block`.

Dependencies and integration: Exercises the Linux reporter’s guilty-file extraction and subsystem extractor path rules. It also exercises report truncation/tail handling because the file contains a tail report separator.

Risks: Large kernel logs can include many unrelated subsystem paths; the test expects the extractor to choose the relevant block path rather than noise from lock listings or secondary NMI traces.

Test signals: Validates that a realistic hung-task report maps to the block subsystem.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/1 -->
# sources/test-tools/syzkaller/pkg/manager/testdata/1

Purpose: Minimal crash-report fixture containing only the syzkaller tail-report separator.

Important content: The file is effectively empty aside from `<<<<<<<<<<<<<<< tail report >>>>>>>>>>>>>>>`.

Control flow and state: `TestGetSubsystems` saves it as a report and expects no subsystem classification.

Dependencies and integration: Exercises `CrashStore.getSubsystems`, reporter parsing, and subsystem extraction when a report has no useful stack or guilty file.

Risks: Empty/minimal reports must not produce bogus subsystem matches or crash the parser.

Test signals: Negative fixture for nil subsystem output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/2 -->
# sources/test-tools/syzkaller/pkg/manager/testdata/2

Purpose: Crash-report fixture for HID/USB subsystem extraction.

Important content: The report contains a general protection fault in `logi_dj_probe` at `drivers/hid/hid-logitech-dj.c:1910`, with a stack through HID and USB probe paths (`drivers/hid`, `drivers/hid/usbhid`, `drivers/usb/core`). It includes a disassembly block and tail-report separator.

Control flow and state: `TestGetSubsystems` saves the fixture and expects subsystem names `input` and `usb` based on configured path rules.

Dependencies and integration: Exercises Linux report guilty-file parsing, path-rule matching with overlapping include rules, and multi-subsystem output.

Risks: The stack contains both HID and USB paths; path-rule ordering and deduplication must preserve the expected two subsystems. Report parser changes could choose a different guilty frame.

Test signals: Positive fixture for multi-subsystem classification from a realistic probe crash.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/3 -->
# sources/test-tools/syzkaller/pkg/manager/testdata/3

Purpose: Crash-report fixture for memory-management subsystem extraction.

Important content: The report centers on `WARNING: mm/rmap.c:528 at unlink_anon_vmas`, with stack frames through `free_pgtables`, `exit_mmap`, and related `mm/` paths.

Control flow and state: Used by `TestGetSubsystems`, which expects subsystem `mm`.

Dependencies and integration: Verifies that warning-style reports with file/line titles can be parsed into a guilty file and matched against subsystem path rules.

Risks: The fixture starts mid-log before the warning marker, so parser resilience to partial preceding context matters. If guilty-file ranking changes, subsystem extraction may change.

Test signals: Positive fixture for `mm/` path classification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/manager/testdata/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/config.go -->
# sources/test-tools/syzkaller/pkg/mgrconfig/config.go

Purpose: Defines the syz-manager JSON configuration schema and derived runtime fields used across manager, VM, report, corpus, dashboard, hub, coverage, and experimental systems.

Important types: `Config` contains user-provided fields such as `name`, `target`, `http`, `rpc`, workdir paths, kernel object/source paths, VM image and SSH settings, hub/dashboard settings, syzkaller checkout, procs, sandbox, snapshot/coverage/repro flags, syscall filters, suppressions/interests, strace/executor-on-target settings, asset storage, memory dumps, VM type/raw config, and embedded `Experimental` plus `Derived`. `Experimental` includes reset accumulated state, remote coverage, edge coverage, descriptions mode, focus areas, and KFuzzTest. `FocusArea`, `Subsystem`, and `CovFilterCfg` model coverage and subsystem filters.

Control flow and state: This file defines data only; loading, defaults, validation, and derived field population happen in `load.go`.

Dependencies and integration: Imported by nearly every manager package. JSON tags form the external config contract. `asset.Config` integrates crash asset upload configuration.

Risks: Schema changes affect user configs, canned tests, dashboard/hub behavior, and VM-type-specific parsing. Some fields are deprecated (`CovFilter`) or experimental and may have compatibility concerns. Misdocumented path semantics could cause coverage/report failures.

Test signals: `mgrconfig_test.go` loads canned configs into this schema and VM-specific schemas.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/load.go -->
# sources/test-tools/syzkaller/pkg/mgrconfig/load.go

Purpose: Loads, defaults, validates, and completes `mgrconfig.Config` objects, including target resolution, absolute paths, binary locations, service prerequisites, syscall filters, focus areas, and timeouts.

Important APIs and types: `Derived` stores target objects, parsed OS/arch/vmarch, binary paths, enabled syscall ids, no-mutate ids, timeouts, VM-less flag, and modules. Entry points are `LoadData`, `LoadFile`, `LoadPartialData`, `LoadPartialFile`, `DefaultValues`, `SetTargets`, and `Complete`. Helpers include `CompleteKernelDirs`, `KernelDirs`, `checkSSHParams`, `completeBinaries`, `completeFocusAreas`, `SplitTarget`, `ParseEnabledSyscalls`, `ParseNoMutateSyscalls`, and `MatchSyscall`.

Control flow: Partial load applies defaults, parses config with comment-tolerant config loader, and resolves target. `Complete` enforces required fields, absolutizes workdir/image/syzkaller/kernel paths, validates binaries and SSH key permissions, completes service settings, parses description mode, computes enabled syscalls and no-mutate calls, normalizes focus areas and legacy cover filter, initializes target-specific timeouts with slowdown heuristics, and rejects reproduction in VM-less mode.

State and persistence: No persistence; mutates config in memory. `osutil.Abs` enforces stable process working directory. Asset storage validation depends on dashboard configuration.

Dependencies and integration: Depends on syzkaller `prog`, `targets`, config loader, os utilities, and vminfo. Used before manager, repro, HTTP, VM, and report construction.

Risks: `completeServices` error is currently swallowed by `Complete` (`return nil`) if service completion fails, which can hide invalid hub/dashboard/asset config. Path existence checks can make tests/environment setup brittle. Syscall matching patterns are prefix-based and exact-dollar aware; unexpected patterns may enable more calls than intended.

Test signals: `load_test.go` covers description-mode and snapshot filtering. `mgrconfig_test.go` covers canned config loading and syscall pattern matching.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/load_test.go -->
# sources/test-tools/syzkaller/pkg/mgrconfig/load_test.go

Purpose: Tests syscall selection behavior under different description modes and snapshot handling.

Important test: `TestParseEnabledSyscalls` uses the synthetic test target and table-driven cases for wildcard enablement, exact snapshot-only enablement, manual/automatic modes, and expected enabled/disabled syscall names.

Control flow and state: Each subtest calls `ParseEnabledSyscalls(target, enable, nil, mode)` and asserts target syscall ids are present or absent in the returned slice.

Dependencies and integration: Uses `prog.GetTarget` for `targets.TestOS`/`TestArch64`, plus testify assertions. It protects manager config parsing from accidentally fuzzing automatic-only, manual-only, or snapshot-only descriptions under the wrong mode.

Risks: Disable-list behavior is noted as TODO and not covered. Ordering of returned syscall ids is intentionally map-derived and not asserted.

Test signals: Strong targeted coverage for mode filtering, including the special exact-match behavior that bypasses snapshot checks for exact names.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/mgrconfig_test.go -->
# sources/test-tools/syzkaller/pkg/mgrconfig/mgrconfig_test.go

Purpose: Tests canned manager configs and syscall pattern matching from an external-package perspective.

Important tests: `TestCanned` loads every `testdata/*.cfg`, then parses the raw VM config into the correct VM-specific config type (`qemu`, `gce`, or `proxyapp`). `TestMatchSyscall` validates exact, base-name, and wildcard matching against syscall names with optional `$variant` suffixes.

Control flow and state: Canned configs are loaded through `LoadFile`, which runs full completion. VM raw JSON is loaded with `config.LoadData` into typed VM structs. Pattern tests call `MatchSyscall(call, pattern)`.

Dependencies and integration: Ensures mgrconfig stays compatible with VM package schemas and real example config files. Uses dot-import of `mgrconfig` to exercise exported API.

Risks: Canned configs rely on testdata syzkaller binaries/images existing. Pattern coverage is concise and does not include malformed or empty patterns.

Test signals: Good regression guard for config schema drift and syscall filter semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/mgrconfig_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce1.cfg -->
# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce1.cfg

Purpose: Canned Windows/GCE manager config fixture used by `TestCanned`.

Important content: Includes comments, `name` `windows-gce`, target `windows/amd64`, HTTP address, absolute workdir, syzkaller testdata path, non-root SSH user, procs 8, type `gce`, dashboard client/address, and VM config with count, machine type, and `gce_image`.

Control flow and state: Loaded through full config completion, then the `vm` object is parsed into `gce.Config`.

Dependencies and integration: Tests comment-tolerant config parsing, Windows target support, GCE VM schema, dashboard required fields, and syzkaller binary resolution in testdata.

Risks: Fixture paths must match repository testdata layout. It does not include image upload settings or SSH key permissions.

Test signals: Positive fixture for GCE image-name based config.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce1.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce2.cfg -->
# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce2.cfg

Purpose: Canned Linux/GCE manager config fixture for `TestCanned`.

Important content: Defines `linux-gce`, target `linux/amd64`, HTTP/workdir/syzkaller/image paths, SSH user, procs 8, type `gce`, and VM config with count, machine type, and `gcs_path` for image upload.

Control flow and state: Full config loading verifies image path existence and GCE VM config parsing.

Dependencies and integration: Exercises GCE mode that uploads a local disk image to GCS rather than referencing an existing GCE image name.

Risks: Depends on `testdata/disk.raw` existence. Does not include dashboard/hub settings.

Test signals: Positive fixture for Linux GCE local-image upload config.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce2.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/proxyapp.cfg -->
# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/proxyapp.cfg

Purpose: Canned proxyapp manager config fixture for `TestCanned`.

Important content: Defines target `linux/amd64`, workdir, syzkaller path, HTTP address, type `proxyapp`, VM command and nested proxyapp config (`count`, kernel tarball, manager host), procs 32, disabled `clock_settime`, and `reproduce: false`.

Control flow and state: Loaded through `LoadFile`, then raw VM config is parsed into `proxyapp.Config`.

Dependencies and integration: Exercises proxyapp VM schema and a high-procs config with reproduction disabled.

Risks: Uses placeholder paths that are accepted by schema parsing but may not represent runnable local state. Does not cover SSH/image fields.

Test signals: Positive fixture for proxyapp config compatibility and disabled-syscall parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/proxyapp.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu-example.cfg -->
# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu-example.cfg

Purpose: Comment-heavy QEMU example config fixture used by `TestCanned`.

Important content: Provides target `linux/amd64`, bind-all HTTP address, workdir under testdata, kernel object/source placeholders, testdata image, syzkaller path, procs 4, type `qemu`, and VM config with count, kernel path, CPU, and memory.

Control flow and state: Validates that commented example-style config remains parseable and that QEMU VM raw JSON can be decoded.

Dependencies and integration: Exercises comment handling in config loader, QEMU schema, image path validation, and binary path resolution.

Risks: Contains documentation comments with external URLs and placeholders; test success depends on only fields that completion validates.

Test signals: Guards against breaking the documented example config format.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu-example.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu.cfg -->
# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu.cfg

Purpose: Compact QEMU canned config fixture used by `TestCanned`.

Important content: Defines target `linux/amd64`, HTTP host, workdir, kernel object path, testdata disk image, syzkaller path, disabled key-management syscalls, suppressions, procs 4, type `qemu`, and VM settings for count, CPU, memory, kernel, and initrd.

Control flow and state: Loaded and completed by mgrconfig, then VM raw config parsed into `qemu.Config`.

Dependencies and integration: Exercises disabled syscall list parsing, suppressions, QEMU kernel/initrd fields, and path normalization.

Risks: Absolute kernel/workdir paths are placeholders; completion does not require kernel object existence in this fixture path set.

Test signals: Positive fixture for common Linux QEMU manager configuration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/fileutil.go -->
# sources/test-tools/syzkaller/pkg/osutil/fileutil.go

Purpose: Provides filesystem helpers for atomic file copying/renaming, test directory population, temporary file writing, and simple content grep across source trees.

Important APIs: `CopyFile`, `Rename`, `FillDirectory`, `WriteTempFile`, and `GrepFiles`.

Control flow: `CopyFile` opens the source, preserves mode and modification time, writes to `<new>.tmp`, closes, sets times, and renames into place. `Rename` tries `os.Rename`, then falls back to copy/remove for cross-device moves. `FillDirectory` creates parent directories and writes files from a map, mainly for tests. `WriteTempFile` creates a temp file with a `syzkaller` prefix and cleans up on write failure. `GrepFiles` walks a root tree, filters by extension, reads files into memory, and returns relative paths containing a target byte sequence.

State and persistence: Mutates the filesystem. Copy operations are near-atomic for the destination but not fsync-backed. `Rename` removes the old file even if fallback copy succeeds but remove fails is ignored.

Dependencies and integration: Used by patch focus-area header scanning, tests, crash memory dump copy paths, and general repository utilities.

Risks: `GrepFiles` skips all files whose extension does not exactly equal `ext`; empty `ext` still filters out files with non-empty extensions due to current condition. It loads entire files into memory. `CopyFile` defers close and also closes explicitly, which is usually harmless.

Test signals: `fileutil_test.go` covers `GrepFiles`; `osutil_test.go` indirectly covers copy/link pattern behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/fileutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/fileutil_test.go -->
# sources/test-tools/syzkaller/pkg/osutil/fileutil_test.go

Purpose: Tests process temp directory allocation and file-content grep utility behavior.

Important tests: `TestProcessTempDir` repeatedly pre-creates stale instance directories, writes fake stale pid files, then concurrently requests new process temp dirs and asserts uniqueness. `TestGrepFiles` builds nested `.c` and `.txt` files and checks that only `.c` files containing target bytes are returned.

Control flow and state: The temp-dir test relies on `ProcessTempDir` cleanup of pid files whose process no longer exists. It uses goroutines and a mutex-protected set to detect duplicate directories. The grep test uses `FillDirectory` and `GrepFiles`.

Dependencies and integration: Covers Unix `ProcessTempDir` behavior from `osutil_unix.go` and `GrepFiles` from `fileutil.go`.

Risks: Fake pid `999999999` assumes no such process exists. The test is concurrency-sensitive but repeated to catch races.

Test signals: Good coverage for lock-protected temp instance allocation and extension-filtered grep.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/fileutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil.go

Purpose: Core OS utility package for subprocess execution, file/path helpers, JSON helpers, atomic writes, gzip writing, temp files, absolute paths, monotonic time, and recursive disk usage.

Important APIs: `RunCmd`, `Run`, `CommandContext`, `Command`, `GraciousCommand`, `VerboseError`, `VerboseMessage`, `IsExist`, `FilesExist`, `CopyFiles`, `CopyDirRecursively`, `LinkFiles`, `MkdirAll`, `WriteFile`, `WriteFileAtomically`, `WriteJSON`, `ReadJSON`, `ParseJSON`, `JSONDeepCopy`, `WriteGzipStream`, `WriteExecFile`, `TempFile`, `TempFileIn`, `ListDir`, `Abs`, `FileTimes`, `MonotonicNano`, and `DiskUsage`.

Control flow: Command helpers set platform death-signal behavior, kill process groups on timeout/cancel, and return combined output with `VerboseError` on failure. Copy/link helpers expand slash-form glob patterns from a source tree into a destination tree, with required/optional pattern handling. JSON parsing disallows unknown fields. `Abs` caches the initial working directory and panics if it changes. `DiskUsage` walks recursively and sums platform-specific usage.

State and persistence: Performs real filesystem and process mutations. Uses package-level cached working directory and `sync.Once`.

Dependencies and integration: Heavily used by manager config, diff patch scanning, report decompilation, coverage, crash storage, VM setup, tests, and cron-like helpers.

Risks: `Run` with zero timeout times out immediately. `WriteFileAtomically` uses a fixed `.tmp` suffix and can conflict with concurrent writers. `Abs` intentionally panics if cwd changes, which enforces process invariants but surprises libraries. `CopyFiles` removes destination before rename, so replacement is not fully atomic on Linux.

Test signals: `osutil_test.go` covers existence checks, copy/link glob behavior, monotonic time, JSON round-trip, disk usage on Linux, and verbose error formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_fuchsia.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil_fuchsia.go

Purpose: Fuchsia-specific interrupt and process-exit helpers.

Important APIs: `HandleInterrupts` is a no-op on Fuchsia. `ProcessExitStatus` currently returns 0 with a TODO to parse status text.

Control flow and state: No state; both functions are simple platform shims selected by `//go:build fuchsia`.

Dependencies and integration: Provides the platform-specific functions expected by code using osutil process helpers.

Risks: Returning 0 for all Fuchsia process statuses can hide failures in callers relying on exit codes. No-op interrupt handling means graceful shutdown semantics differ from Unix.

Test signals: No direct tests in this shard.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_fuchsia.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_linux.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil_linux.go

Purpose: Linux-specific implementations for file timestamps, robust recursive removal, memory size, command sandboxing, parent-death/process-group handling, pipe sizing, and disk usage.

Important APIs: `fileTimes`, `RemoveAll`, `SystemMemorySize`, `Sandbox`, `SandboxChown`, plus internal `removeImmutable`, `initSandbox`, `usernameToID`, `setPdeathsig`, `killPgroup`, `prolongPipe`, and `sysDiskUsage`.

Control flow: `fileTimes` uses `statx` for birth and mtime. `RemoveAll` recursively attempts to unmount children, removes the tree, and retries after clearing immutable/append flags. `Sandbox` lazily resolves the `syzkaller` user unless not root, CI, or disabled by env; it can set new namespaces and/or credentials on an exec command. Command helpers set `Pdeathsig` and process group. `prolongPipe` tries increasing pipe sizes. Disk usage uses allocated blocks and handles inline/small file cases.

State and persistence: Uses package-level sandbox cache guarded by `sync.Once`. Mutates command `SysProcAttr`, file ownership, mount state, and filesystem flags.

Dependencies and integration: Supports `osutil.Run`, manager process spawning, cleanup, VM preparation, and disk accounting.

Risks: Sandbox requires a `syzkaller` user when enabled. `killPgroup` assumes process started and process group exists. `RemoveAll` ignores errors from recursive child removals/unmount attempts until final removal. Disk usage uses Linux stat details and can vary by filesystem.

Test signals: `TestDiskUsage` covers Linux usage accounting; command/sandbox behavior is not directly tested here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_nonlinux.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil_nonlinux.go

Purpose: Non-Linux fallbacks for OS helpers whose Linux implementation depends on statx, namespaces, process groups, or block accounting.

Important APIs: `fileTimes`, `RemoveAll`, `SystemMemorySize`, `prolongPipe`, `Sandbox`, `SandboxChown`, `setPdeathsig`, `killPgroup`, and `sysDiskUsage`.

Control flow and state: Uses modification time for both creation and modification time, delegates removal to `os.RemoveAll`, returns 0 for memory size, no-ops sandbox/PDEATHSIG/pipe behavior, and reports disk usage as file size.

Dependencies and integration: Allows packages using osutil to build and run on non-Linux platforms with reduced semantics.

Risks: Process timeout/cancel on non-Linux cannot kill full process groups via `killPgroup`. Disk usage is logical size rather than allocated blocks. Sandbox calls silently do nothing.

Test signals: Many osutil tests skip Linux-specific disk usage on non-Linux; no direct non-Linux behavior tests in this shard.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_test.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil_test.go

Purpose: Tests broad `osutil` helper behavior for existence checks, copy/link pattern expansion, monotonic time, JSON helpers, Linux disk usage, and verbose error formatting.

Important tests: `TestIsExist`, `TestCopyFiles`, `TestMonotonicNano`, `TestReadWriteJSON`, `TestDiskUsage`, and `TestVerboseMessage`.

Control flow and state: `TestCopyFiles` table-drives required/optional glob patterns across both `CopyFiles` and `LinkFiles`, removes the source tree, and verifies destination existence. `TestDiskUsage` incrementally creates dirs/files/symlinks and asserts usage increases within ranges, skipping non-Linux. `TestVerboseMessage` checks wrapped `VerboseError` output inclusion.

Dependencies and integration: Covers core helpers used throughout syzkaller manager and test code.

Risks: Disk usage expected ranges are filesystem-dependent and only run on Linux. Copy/link tests verify existence but not file contents, permissions, or atomicity.

Test signals: Good utility-level regression coverage for common filesystem and error-message contracts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_unix.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil_unix.go

Purpose: Unix-family helpers for process temp directories, interrupt handling, and long pipes.

Important APIs: `ProcessTempDir`, `HandleInterrupts`, and `LongPipe`; internal `cleanupTempDir`.

Control flow: `ProcessTempDir` takes an exclusive flock on `instance-lock`, scans `instance-0` to `instance-999`, tries to create a directory, cleans stale directories whose `.pid` process no longer exists, writes the current pid, and returns the path. `HandleInterrupts` closes a shutdown channel on first SIGINT/SIGTERM, prints escalating messages on second/third signal, and exits on third. `LongPipe` creates an `os.Pipe` and calls platform `prolongPipe`.

State and persistence: Creates instance directories and `.pid` files under a caller-provided root. Signal handling mutates process behavior.

Dependencies and integration: Used for VM/process workspace allocation and graceful manager shutdown on Unix platforms.

Risks: Stale cleanup depends on pid reuse and `.pid` integrity. The 1000-instance limit is fixed. Signal handler assumes it owns shutdown channel closure and can exit the process.

Test signals: `fileutil_test.go` stress-tests concurrent `ProcessTempDir` allocation and stale cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_windows.go -->
# sources/test-tools/syzkaller/pkg/osutil/osutil_windows.go

Purpose: Windows-specific process helper shims.

Important APIs: `HandleInterrupts` is a no-op. `ProcessExitStatus` extracts the exit status from `syscall.WaitStatus`.

Control flow and state: No persistent state; functions are simple platform-specific implementations.

Dependencies and integration: Satisfies osutil API for Windows builds.

Risks: No interrupt handling means graceful shutdown-by-signal behavior differs from Unix. Exit status extraction assumes the `ProcessState.Sys()` type.

Test signals: No direct tests in this shard.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/osutil_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/semaphore.go -->
# sources/test-tools/syzkaller/pkg/osutil/semaphore.go

Purpose: Implements a simple counting semaphore backed by a buffered channel.

Important APIs: `NewSemaphore`, `Wait`, `WaitC`, `Available`, and `Signal`.

Control flow and state: `NewSemaphore(count)` creates a channel of capacity `count` and fills it with `count` tokens. `Wait` receives one token. `WaitC` exposes the receive channel for select statements. `Available` returns current buffered token count. `Signal` sends a token back and panics if the semaphore already appears full.

Dependencies and integration: General utility for bounded concurrency in syzkaller packages.

Risks: `Available`/capacity check is not a synchronization guarantee under concurrent `Signal` calls, as the comment notes. Exposing `WaitC` allows callers to receive without paired signaling discipline.

Test signals: No direct tests in this shard.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/semaphore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/tar.go -->
# sources/test-tools/syzkaller/pkg/osutil/tar.go

Purpose: Archives a directory as tar or tar.gz, including directories and regular files while skipping other filesystem object types.

Important APIs: `TarGzDirectory` wraps `tarDirectory` with a gzip writer. `tarDirectory` writes tar headers and regular file contents.

Control flow: `TarGzDirectory` creates a gzip writer, defers close, and delegates to `tarDirectory`. `tarDirectory` walks the input directory, skips the root path, ignores non-directory/non-regular entries, computes slash-form relative paths, creates tar headers from file info, appends `/` to directory names, writes headers, and copies file data for regular files.

State and persistence: Reads filesystem contents and writes archive bytes to the supplied writer. It does not preserve symlink targets or special files.

Dependencies and integration: Used where syzkaller needs portable archive output, likely for artifacts or VM data transfer.

Risks: Walk order is filesystem-defined. Closing gzip/tar writers can surface errors only through deferred close timing; `TarGzDirectory` does not capture gzip close errors separately. Symlinks are skipped.

Test signals: `tar_test.go` verifies regular files in nested directories round-trip through raw tar generation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/tar_test.go -->
# sources/test-tools/syzkaller/pkg/osutil/tar_test.go

Purpose: Tests tar archive creation for regular files.

Important test: `TestTarDirectory` creates three files, including nested and empty files, calls uncompressed `tarDirectory`, reads the tar stream back, and asserts the found regular-file contents equal the original map.

Control flow and state: Uses `FillDirectory` for setup, `bytes.Buffer` as archive sink, and `archive/tar.Reader` for verification.

Dependencies and integration: Directly covers `tarDirectory`, while `TarGzDirectory` is indirectly trusted because it only wraps gzip around the tar writer.

Risks: Does not verify directory headers, permissions, mtimes, gzip wrapper, symlink skipping, or deterministic order.

Test signals: Basic correctness guard for archive content.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/osutil/tar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/bsd.go -->
# sources/test-tools/syzkaller/pkg/report/bsd.go

Purpose: Shared BSD-style report implementation for crash detection, parsing, and symbolization used by Darwin/OpenBSD-like reporters.

Important APIs and types: `bsd` stores config, oops definitions, regexes for symbolizable lines, kernel object path, and text symbols. `ctorBSD` constructs the reporter implementation. Methods `ContainsCrash`, `Parse`, `Symbolize`, and `symbolizeLine` implement reporter behavior.

Control flow: `ctorBSD` reads text symbols from `<kernel_obj>/<target.KernelObject>` when a kernel object directory is configured. `ContainsCrash` delegates to common `containsCrash`; `Parse` delegates to `simpleLineParser`. `Symbolize` iterates report lines, calls `symbolizeLine`, and adjusts `reportPrefixLen` if symbolization changes bytes before the prefix boundary. `symbolizeLine` matches configured regexes, extracts function and hex offset, finds the function in text symbols, constructs a kernel PC, calls symbolizer, and inserts file:line and inline function annotations.

State and persistence: Symbol table is cached in the reporter instance. No filesystem writes.

Dependencies and integration: Uses common report parsing helpers, `symbolizer`, and `mgrconfig.KernelDirs`. Darwin uses this via `ctorDarwin`.

Risks: Assumes a 32-bit-style high-half address calculation when building `fnStart`. Symbolization depends on regex capture group layout. Missing symbols or symbolizer errors silently leave lines unchanged.

Test signals: `bsd_test.go` supplies synthetic symbols and frames to validate line symbolization and inline frame expansion.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/bsd_test.go -->
# sources/test-tools/syzkaller/pkg/report/bsd_test.go

Purpose: Provides a reusable helper for BSD reporter line-symbolization tests.

Important types and functions: `symbolizeLineTest` holds input and expected line strings. `testSymbolizeLine` constructs a fake symbol table, fake symbolizer callback, invokes a reporter constructor, injects symbols/kernel object, and compares `bsd.symbolizeLine` output against expectations.

Control flow and state: The fake symbolizer recognizes two PCs and returns either a single frame or inline plus outer frames. The helper trims `/bsd/src` build paths through reporter config. Tests using this helper can validate constructor-specific regex matching while sharing symbolization mechanics.

Dependencies and integration: Depends on `mgrconfig.KernelDirs`, `symbolizer.Symbol`, and the report package constructor type `fn`.

Risks: This file defines helper infrastructure but no top-level `Test*` itself in the read section, so actual coverage depends on other platform-specific test files invoking it. Synthetic PC calculation mirrors `bsd.go` assumptions.

Test signals: When invoked by platform tests, it validates file/line insertion and inline frame handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/bsd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/crash/title_to_type.go -->
# sources/test-tools/syzkaller/pkg/report/crash/title_to_type.go

Purpose: Defines ordered mappings from syzkaller crash title prefixes to normalized crash `Type` values.

Important data: `titleToType` is an ordered slice of include-prefix groups. It maps KFENCE, KMSAN, KASAN, null pointer, memory-safety, KCSAN, lockdep, atomic-sleep, leak, BUG/WARNING, hang, DoS, no-output, reboot, and syzkaller failure prefixes to crash types, followed by broad defaults for `WARNING:`, `BUG:`, `INFO:`, sanitizer families, and UBSAN.

Control flow and state: This file is data-only. Runtime lookup is implemented by `TitleToType` in `types.go`, which returns the first prefix match. Ordering is therefore semantically important: more specific prefixes must precede broader prefixes.

Dependencies and integration: Used by report impact scoring, dashboards, analytics, and any logic grouping crashes by class.

Risks: Prefix overlap can shadow later mappings. Broad defaults intentionally classify unknown sanitizer titles but can hide the need for more specific types. Comments mention keep-sorted regions, but global ordering is priority-driven rather than purely alphabetical.

Test signals: `title_to_type_test.go` validates non-empty prefixes, duplicate prevention, and that no prefix is already matched by an earlier prefix.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/crash/title_to_type.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/crash/title_to_type_test.go -->
# sources/test-tools/syzkaller/pkg/report/crash/title_to_type_test.go

Purpose: Validates structural correctness of crash-title prefix definitions.

Important tests and helpers: `TestTitleToTypeDefinitions` iterates over `titleToType`, ensuring each definition has prefixes, no prefix is empty, no duplicate prefix exists, and no new prefix is already matched by a previously seen broader prefix. `hasPrefix` performs the shadowing check.

Control flow and state: The test relies on the production ordering of `titleToType`, matching the first-prefix-wins behavior in `TitleToType`.

Dependencies and integration: Protects `report/crash` classification from accidental shadowing and duplicate definitions.

Risks: It does not assert specific title-to-type examples or type group predicate behavior. It can reject intentional broad-before-specific changes unless ordering is updated.

Test signals: Strong guard for the most common maintenance error in ordered prefix tables.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/crash/title_to_type_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/crash/types.go -->
# sources/test-tools/syzkaller/pkg/report/crash/types.go

Purpose: Defines normalized crash type constants, title classification, string rendering, and grouping predicates.

Important APIs and types: `Type` is a string alias. Constants include unknown, sanitizer categories, lockdep/atomic sleep, DoS, hang, leak, warning/bug families, no output, reboot, and syzkaller failure. `TitleToType` maps a title through `titleToType`. `String` renders unknown as `UNKNOWN`. Predicate methods include `IsKASAN`, `IsUAF`, `IsKMSAN`, `IsKCSAN`, `IsUBSAN`, `IsBUG`, `IsWarning`, `IsBugOrWarning`, `IsMemSafety`, `IsMemoryLeak`, `IsLockingBug`, `IsDoS`, `IsHang`, `IsLockdep`, and `IsAtomicSleep`.

Control flow and state: `TitleToType` loops definitions in order and returns on first `strings.HasPrefix`. Predicates use exact comparisons or small `slices.Contains` lists.

Dependencies and integration: Consumed by report classification, impact scoring, dashboards, triage, and analytics.

Risks: `IsUAF` currently only covers KASAN UAF types, not KFENCE/KMSAN UAF reads/writes. `IsDoS` includes `Bug` and `DoS`, which is a policy choice that callers must understand. Adding new constants requires updating predicates.

Test signals: Prefix-table structure is tested in `title_to_type_test.go`; predicate methods do not have direct tests here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/crash/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/darwin.go -->
# sources/test-tools/syzkaller/pkg/report/darwin.go

Purpose: Defines Darwin crash reporter construction and Darwin-specific oops patterns.

Important APIs and data: `ctorDarwin` calls `ctorBSD` with `darwinOopses` and no symbolization regexes. `darwinOopses` matches `panic(cpu ...)` forms, assertion failures, kernel traps, known route/zalloc panic formats, generic quoted/unquoted panics, debugger unexpected trap numbers, Go runtime errors, and common oopses.

Control flow and state: Runtime behavior is inherited from `bsd`: `ContainsCrash`, `Parse`, and symbolization support. Since `symbolizeRes` is empty, line symbolization will not modify Darwin reports through this constructor.

Dependencies and integration: Registered through the report package constructor map in `report.go` (outside this shard). Uses shared oops parsing helpers and BSD implementation.

Risks: Regex ordering matters; generic panic patterns can catch titles that might deserve more specific handling. No symbolization regexes means Darwin reports depend on raw logs for source detail.

Test signals: No direct Darwin test in this shard; BSD helper can support platform tests elsewhere.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/decompile.go -->
# sources/test-tools/syzkaller/pkg/report/decompile.go

Purpose: Converts raw opcode bytes into human-readable assembly descriptions by invoking target `objdump`.

Important APIs and types: `DecompilerFlagMask` and `FlagForceArmThumbMode` control decompilation. `DecompiledOpcode` records offset, bad-instruction flag, instruction text, and full objdump line. `DecompileOpcodes` is the main entry. Internal helpers are `objdumpExecutor`, `objdumpParseOutput`, and `objdumpBuildArgs`.

Control flow: `DecompileOpcodes` builds architecture-specific objdump arguments, writes raw bytes to a temp file, runs `target.Objdump` with a 10-second timeout, parses assembly lines, and errors if non-empty input yields no instructions. `objdumpParseOutput` scans lines with a regexp, parses hex offsets, marks `(bad)` instructions, and trims trailing whitespace. `objdumpBuildArgs` sets binary disassembly mode and architecture flags for arm64, arm, i386, amd64, mips64le, ppc64le, s390x, and riscv64.

State and persistence: Creates and removes a temporary file. No persistent state.

Dependencies and integration: Used by report parsing paths that decompile kernel opcode bytes, especially Linux report code outside this shard. Depends on `osutil.RunCmd` and `targets.Target`.

Risks: Requires a usable target objdump in PATH/config. Raw objdump output parsing is regex-sensitive. Unsupported architectures return errors. Temporary file creation/writing errors block decompilation.

Test signals: `decompile_test.go` validates objdump output parsing including `(bad)` instruction detection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/decompile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/decompile_test.go -->
# sources/test-tools/syzkaller/pkg/report/decompile_test.go

Purpose: Tests parsing of objdump text output into `DecompiledOpcode` records.

Important test: `TestParseObjdumpOutput` feeds a synthetic binary disassembly with offsets 0, 1, 2, 4, and 9, including a `(bad)` instruction, then compares the parsed slice to expected offsets, instruction strings, `IsBad`, and full descriptions.

Control flow and state: Calls only `objdumpParseOutput`; it does not invoke external objdump or create temp files.

Dependencies and integration: Protects the parser used by `DecompileOpcodes` and report opcode decompilation paths.

Risks: Does not cover architecture argument building, command timeouts, unsupported architectures, empty-output error handling, or multiline/variant objdump formats.

Test signals: Focused guard for regex parsing and bad-instruction classification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/decompile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/freebsd.go -->
# sources/test-tools/syzkaller/pkg/report/freebsd.go

Purpose: Implements FreeBSD crash detection and parsing patterns.

Important APIs and data: `freebsd` wraps config. `ctorFreebsd` returns the reporter. Methods `ContainsCrash`, `Parse`, and `Symbolize` implement reporter behavior. `freebsdStackParams` is an empty stack-parameter set. `freebsdOopses` includes fatal trap and panic patterns, Go runtime errors, and common oopses.

Control flow: `ContainsCrash` delegates to `containsCrash` using FreeBSD oopses and ignores. `Parse` delegates to `simpleLineParser` with FreeBSD stack params. `Symbolize` is currently a no-op. Oops regexes extract titles from fatal traps, KDB stack backtraces, destroyed locks, SCTP/socket panics, ASan invalid access, and other known FreeBSD panic messages.

State and persistence: No persistent state beyond reporter config.

Dependencies and integration: Registered by the report package for FreeBSD targets. Uses common report parser utilities and regex helpers.

Risks: No symbolization means title quality relies on regex extraction. Regexes are specific to known FreeBSD log formats and can miss new panic variants. Generic common oopses may classify unexpected runtime failures.

Test signals: No direct FreeBSD-specific tests in this shard; general report parser tests elsewhere likely cover fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/freebsd.go -->
