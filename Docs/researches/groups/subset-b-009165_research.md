# subset-b-009165 Research

Grouped report for the requested source-tree-aligned files. Each section is bounded by reconciliation markers and preserves the source path in the title.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals.go -->
# sources/sync-backup/restic/internal/ui/signals/signals.go

Purpose: defines the shared progress-signal entry point for restic UI code. `GetProgressChannel()` lazily creates a buffered `chan os.Signal` and calls the platform-specific `setupSignals()` selected by build tags.

Important APIs/types/functions: the only exported API is `GetProgressChannel() <-chan os.Signal`. Package state is a single anonymous global `signals` containing the channel and `sync.Once`.

Control flow: callers receive the same channel on every call. `sync.Once` prevents duplicate `signal.Notify` registration and keeps initialization race-safe.

State and persistence: process-local global state only; no filesystem persistence. The buffer size is one, so bursts can coalesce at the signal package boundary.

Dependencies/integration: integrates with platform files in the same package and with command progress display code that wants a user-triggered refresh.

Risks: the inline comment is important: because one global channel is shared, only one listener consumes each delivered signal. Multiple consumers must fan out externally.

Test signals: no direct tests here; behavior is implicitly covered by platform builds and consumers of the progress signal channel.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals_bsd.go -->
# sources/sync-backup/restic/internal/ui/signals/signals_bsd.go

Purpose: BSD-family implementation of `setupSignals()` for progress refresh notifications.

Important APIs/types/functions: unexported `setupSignals()` registers `signals.ch` with `os/signal.Notify`.

Control flow: selected on `darwin`, `dragonfly`, `freebsd`, `netbsd`, and `openbsd`. It subscribes to both `syscall.SIGINFO` and `syscall.SIGUSR1`, allowing terminal status refresh from the platform's info key as well as explicit user signals.

State and persistence: no independent state; mutates only the global channel created in `signals.go`.

Dependencies/integration: depends on Go build tags, `os/signal`, and `syscall`. It is coupled to `GetProgressChannel()` because `signals.ch` must already exist.

Risks: signal names and availability are platform-specific; the build tag prevents accidental compilation elsewhere.

Test signals: direct signal behavior is not unit-tested, so build coverage on each BSD target is the main validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals_sysv.go -->
# sources/sync-backup/restic/internal/ui/signals/signals_sysv.go

Purpose: SysV-like Unix implementation of progress signal registration.

Important APIs/types/functions: unexported `setupSignals()` calls `signal.Notify(signals.ch, syscall.SIGUSR1)`.

Control flow: selected on `aix`, `linux`, and `solaris`. Unlike BSD, it registers only `SIGUSR1`, because these platforms do not have portable `SIGINFO`.

State and persistence: process-local signal subscription only.

Dependencies/integration: pairs with the global channel from `signals.go`; consumers should not call this directly.

Risks: use of `SIGUSR1` may conflict with embedding applications or wrappers that also rely on that signal. The single global channel still means one consumer receives each signal.

Test signals: no direct tests; validated mainly by successful platform builds and runtime use of progress refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals_sysv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals_windows.go -->
# sources/sync-backup/restic/internal/ui/signals/signals_windows.go

Purpose: no-op signal setup for Windows builds where Unix progress signals are unavailable.

Important APIs/types/functions: unexported `setupSignals()` with an empty body.

Control flow: Go selects this file when the Unix build-tagged files do not match. `GetProgressChannel()` still creates a channel, but no OS signal is registered.

State and persistence: no state beyond the global channel allocated in `signals.go`.

Dependencies/integration: avoids importing `os/signal` or `syscall`, keeping Windows builds simple.

Risks: consumers waiting only for signal events will never receive them on Windows; they must also rely on timers or normal progress update paths.

Test signals: no direct tests; build coverage is the relevant signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/signals/signals_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/stats/progress.go -->
# sources/sync-backup/restic/internal/ui/stats/progress.go

Purpose: implements the progress reporter used by restic's `stats` command.

Important APIs/types/functions: `Progress` embeds `progress.Updater`; `NewProgress()` wires update cadence via `progress.CalculateProgressInterval`; `Update()` accumulates file/blob/byte counters; `ProcessSnapshot()` advances snapshot count and resets per-snapshot counters; `printProgress()` formats terminal status.

Control flow: construction decides whether progress should display based on quiet/json/status capability. Periodic updater calls `printProgress`; non-final output goes to `Terminal.SetStatus`, while final output clears status and prints a normal line.

State and persistence: guarded by `sync.Mutex`; counts are in-memory only. `processedSnapshotCount` is displayed directly, while percent uses one less snapshot during active processing so the current snapshot does not count complete until final.

Dependencies/integration: depends on `internal/ui` formatting helpers and `internal/ui/progress` scheduling. Integrates with any `ui.Terminal`.

Risks: snapshot denominator zero behavior is delegated to `ui.FormatPercent`; concurrent `Update()` and updater callbacks rely on correct mutex use.

Test signals: `progress_test.go` verifies formatting, per-snapshot reset, final 100 percent output, and suppressed JSON mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/stats/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/stats/progress_test.go -->
# sources/sync-backup/restic/internal/ui/stats/progress_test.go

Purpose: validates the stats progress formatter without starting the updater scheduler.

Important APIs/types/functions: `TestStatsProgress` drives `newProgress`, `ProcessSnapshot`, `Update`, and `printProgress`; `TestStatsProgressJSON` verifies `show=false`.

Control flow: tests use `ui.MockTerminal` to inspect the last status or printed output. The main test steps through initial state, first snapshot processing, second snapshot processing, additional counters, and final output.

State and persistence: no persistent state; checks in-memory terminal output slices.

Dependencies/integration: imports restic's test helper aliases and `ui.MockTerminal`, giving a focused unit test for the stats package's terminal contract.

Risks: the tests assert exact human-readable strings, so intentional format changes require test updates. They do not exercise `NewProgress` interval calculation or actual goroutine timing.

Test signals: strong formatting regression coverage for percent behavior, counter reset, byte formatting, and JSON suppression.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/stats/progress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/table/table.go -->
# sources/sync-backup/restic/internal/ui/table/table.go

Purpose: small table-rendering helper for aligned terminal output.

Important APIs/types/functions: `Table` stores column headers, parsed `text/template` templates, row data, footers, and customizable printer callbacks. `New()`, `AddColumn()`, `AddRow()`, `AddFooter()`, `Write()`, and helper `printLine()` form the API. Template funcmap exposes `join`.

Control flow: `Write()` renders templates for all rows, computes display widths across headers and cell lines using `ui.DisplayWidth`, prints a multi-line header, separator, each row, another separator, and optional footers. `printLine()` handles multi-line cells and column padding.

State and persistence: table contents are in-memory. `Write()` uses a reusable `bytes.Buffer` per cell and does not mutate rows.

Dependencies/integration: depends on `text/template`, `strings`, and UI width helpers for Unicode-aware alignment.

Risks: `AddColumn()` panics on bad templates by design. Custom printer callbacks must preserve newline semantics. Multiline and wide-character display depends on `ui.DisplayWidth`.

Test signals: `table_test.go` checks empty tables, spacing, multi-line headers/cells, footers, custom joins, and Unicode width effects.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/table/table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/table/table_test.go -->
# sources/sync-backup/restic/internal/ui/table/table_test.go

Purpose: exact-output regression tests for table rendering.

Important APIs/types/functions: one table-driven `TestTable` builds several `Table` instances and compares `Write()` output to expected strings.

Control flow: each case creates columns/rows/footers, writes to `bytes.Buffer`, trims the leading newline from the expected raw string, and reports a side-by-side mismatch.

State and persistence: no external state; all output is in memory.

Dependencies/integration: relies on `strings.TrimLeft` and Go testing. It indirectly verifies `text/template`, the `join` template helper, and `ui.DisplayWidth` through expected padding.

Risks: tests are intentionally brittle for spacing. They do not cover custom printer callbacks returning errors or template execution errors.

Test signals: strong coverage for empty output, separators, padded headers, multi-row tables, multi-column alignment, multi-line cells, footers, and non-ASCII display width.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/table/table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/terminal.go -->
# sources/sync-backup/restic/internal/ui/terminal.go

Purpose: defines the common `ui.Terminal` interface used by restic components for output, status, and password input.

Important APIs/types/functions: the interface includes `Print`, `Error`, `SetStatus`, `CanUpdateStatus`, raw input/output accessors, terminal detection, `ReadPassword`, `OutputWriter`, and `OutputRaw`.

Control flow: none in this file; it is a contract. Comments specify newline handling, concurrent-safe output writer behavior, and the restriction that `OutputRaw` must not be mixed with managed terminal methods.

State and persistence: no state.

Dependencies/integration: depends only on `context` and `io`. Implemented by `internal/ui/termstatus.terminal` and likely mocked by tests.

Risks: callers using `OutputRaw` can break status rendering if they ignore the contract. Interface expansion has broad compile-time impact across UI consumers.

Test signals: implementation behavior is tested in `termstatus/status_test.go`; this file itself has no unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/terminal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/status.go -->
# sources/sync-backup/restic/internal/ui/termstatus/status.go

Purpose: concrete `ui.Terminal` implementation that serializes normal output, error output, and status-line updates.

Important APIs/types/functions: `Setup()` starts the terminal goroutine and returns a shutdown function; `new()` detects TTY capabilities; methods implement `InputRaw`, `ReadPassword`, `CanUpdateStatus`, `OutputWriter`, `OutputRaw`, `Run`, `Flush`, `Print`, `Error`, `SetStatus`; helpers include `writeStatus`, `runWithoutStatus`, `sanitizeLines`, and `findUnchangedLines`.

Control flow: `Run()` chooses interactive in-place status updates or simple output mode. Interactive mode clears current status before printing messages, redraws status, skips writes while backgrounded, and clears on cancellation. Noninteractive mode prints changed status lines as ordinary lines.

State and persistence: channel-driven goroutine owns terminal state. `lastStatus` tracks redraw diffs; `sync.Once` lazily creates a line-buffering output writer. No persistence.

Dependencies/integration: depends on `internal/terminal` for TTY detection/control codes/password reading and on `ui` formatting helpers.

Risks: channel sends after shutdown are dropped; incorrect terminal width can over-truncate; background-process checks suppress output.

Test signals: tests verify cursor sequences, unchanged-line optimization, sanitization, raw IO, disabled status, password fallback, and `OutputWriter`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/status_test.go -->
# sources/sync-backup/restic/internal/ui/termstatus/status_test.go

Purpose: validates interactive and noninteractive terminal status behavior.

Important APIs/types/functions: `setupStatusTest()` injects POSIX terminal control functions into a test terminal. Tests cover `SetStatus`, unchanged-line optimization, `Print`, `sanitizeLines`, `readPassword`, raw input/output, disabled status, and `OutputWriter`.

Control flow: tests start `term.Run(ctx)` in a goroutine, send status/messages, cancel, wait for `term.closed`, and assert the exact control-code transcript.

State and persistence: in-memory buffers only. The tests exercise goroutine shutdown and channel flushing through cancellation.

Dependencies/integration: uses `internal/terminal` constants/functions and restic test helpers. `TestOutputWriter` covers integration with `stdio_wrapper.go`.

Risks: exact terminal escape output is brittle but valuable. Some real TTY paths are simulated rather than using an actual terminal.

Test signals: strong regression coverage for status clearing, multi-line status, avoiding redundant redraws, newline normalization, terminal capability disabling, and partial output flushing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper.go -->
# sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper.go

Purpose: provides a concurrency-safe line-buffering writer used by `terminal.OutputWriter()`.

Important APIs/types/functions: `lineWriter` contains a mutex, bytes buffer, and `print func(string)`. `newLineWriter()`, `Write()`, and `Close()` implement `io.WriteCloser`.

Control flow: `Write()` appends bytes, finds the last newline, prints all complete lines through the terminal print function, and retains any suffix. `Close()` emits a trailing newline for any remaining partial line.

State and persistence: buffered partial line is in memory and protected by `sync.Mutex`; no persistence.

Dependencies/integration: used by `status.go` so concurrent raw-ish writes are serialized through terminal `Print`, preserving status-line behavior.

Risks: `Close()` does not mark the writer closed, so later writes are still accepted. The callback must itself be safe for the expected call pattern.

Test signals: `stdio_wrapper_test.go` verifies chunked line assembly and race-oriented concurrent writes.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper_test.go -->
# sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper_test.go

Purpose: verifies `lineWriter` buffering and concurrent write safety.

Important APIs/types/functions: `TestStdioWrapper` feeds byte chunks into `newLineWriter`; `TestStdioWrapperConcurrentWrites` uses `errgroup` to write from five goroutines.

Control flow: table cases cover no newline until close, split complete lines, multiple lines in one write, and retained suffix emission on close.

State and persistence: only in-memory `strings.Builder` output. Concurrent test relies on mutex protection and is most useful with `go test -race`.

Dependencies/integration: uses `go-cmp` for diffs and restic test helpers for error assertions.

Risks: concurrent test does not verify line ordering, only absence of returned errors and race safety under race detector.

Test signals: good coverage for complete-line flushing, partial-line retention, close-time newline normalization, and basic thread safety.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/termstatus/stdio_wrapper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/rewriter.go -->
# sources/sync-backup/restic/internal/walker/rewriter.go

Purpose: recursively rewrites restic tree blobs, optionally filtering nodes, replacing failed subtrees, dropping empty directories, and computing rewritten snapshot size.

Important APIs/types/functions: function types `NodeRewriteFunc`, `FailedTreeRewriteFunc`, `NodeKeepEmptyDirectoryFunc`; `SnapshotSize`; `RewriteOpts`; `TreeRewriter`; constructors `NewTreeRewriter()` and `NewSnapshotSizeRewriter()`; method `RewriteTree()`.

Control flow: `RewriteTree()` caches by original tree ID unless disabled, loads the tree, optionally verifies stable serialization by re-saving and comparing IDs, iterates nodes, calls `RewriteNode`, recurses into directories, skips nil rewrites/null subtree rewrites, finalizes a new tree, and optionally drops empty directories.

State and persistence: `replaces` memoizes tree-ID rewrites across calls. Actual persistence happens through injected `restic.BlobSaver`.

Dependencies/integration: uses `internal/data` tree iterators/writers, `internal/restic` IDs, `debug.Log`, and `context` cancellation.

Risks: mutation of `*data.Node` returned by iterators must be safe for callers. Cache can intentionally reuse rewrites for identical subtrees, which changes path-specific rewrite semantics unless `DisableNodeCache` is set.

Test signals: rewriter tests cover order, filtering, cache behavior, size counting, empty-directory retention, unknown-field protection, and failed-tree replacement.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/rewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/rewriter_test.go -->
# sources/sync-backup/restic/internal/walker/rewriter_test.go

Purpose: validates tree-rewrite behavior using in-memory tree maps.

Important APIs/types/functions: helper factories `checkRewriteItemOrder`, `checkRewriteSkips`, `checkIncreaseNodeSize`; tests `TestRewriter`, `TestSnapshotSizeQuery`, `TestRewriterKeepEmptyDirectory`, `TestRewriterFailOnUnknownFields`, and `TestRewriterTreeLoadError`.

Control flow: tests build source and expected trees with helpers from `walker_test.go`, run `RewriteTree`, and compare resulting root IDs. Cache-specific cases demonstrate that identical subtree IDs are rewritten once unless caching is disabled.

State and persistence: in-memory `data.TestWritableTreeMap` acts as both loader and saver.

Dependencies/integration: depends on restic test helpers, `data` tree hashing, and `slices.Values` for failed-tree replacement.

Risks: root-ID comparisons provide strong structural checks but can be opaque when failures occur, hence dump logging.

Test signals: strong coverage for file/dir exclusion, node mutation, cache semantics, snapshot-size accumulation, empty-directory policies, serialization-loss detection, and missing-tree recovery hooks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/rewriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/walker.go -->
# sources/sync-backup/restic/internal/walker/walker.go

Purpose: depth-first traversal of restic tree blobs with callback control.

Important APIs/types/functions: `ErrSkipNode`, `WalkFunc`, `WalkVisitor`, exported `Walk()`, and recursive helper `walk()`.

Control flow: `Walk()` loads the root tree and calls `ProcessNode` for `/` with any root-load error. If the root callback returns `ErrSkipNode`, traversal stops without error. `walk()` iterates tree nodes, validates node type, calls `ProcessNode`, supports `ErrSkipNode` to skip a directory or remaining siblings for non-directories, loads directory subtrees before callback, recurses, and calls optional `LeaveDir`.

State and persistence: no persistent state; traversal is streaming through `data.TreeNodeIterator`. Context cancellation is checked during iteration.

Dependencies/integration: depends on `internal/data`, `internal/restic`, `github.com/pkg/errors`, and path joining.

Risks: directory subtree load errors are passed to the callback along with the node; callback policy determines whether to continue. A nil directory subtree or invalid node type is fatal.

Test signals: `walker_test.go` covers traversal order, parent tree IDs, skip behavior, errors, and leave callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/walker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/walker_test.go -->
# sources/sync-backup/restic/internal/walker/walker_test.go

Purpose: provides reusable in-memory tree builders and tests the walker traversal contract.

Important APIs/types/functions: `TestTree`, `TestFile`, `BuildTreeMap`, `buildTreeMap`, and check factories for item order, parent tree IDs, skips, and callback errors.

Control flow: `BuildTreeMap` sorts names to produce deterministic tree hashes. `TestWalker` defines several tree shapes, runs each check against `Walk`, and validates callback order and error propagation.

State and persistence: in-memory `data.TestTreeMap` only; generated hashes simulate repository tree IDs.

Dependencies/integration: depends on restic `data` builders, `restic.ID`, and test helpers.

Risks: tests depend on exact hash values for parent tree IDs, so builder serialization changes require fixture updates.

Test signals: broad coverage for root visit, directory leave callbacks, deterministic traversal, skip-root/skip-directory/skip-file semantics, empty directories, nested directories, and callback-originated errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/walker/walker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/FUNDING.yml -->
# sources/sync-backup/rsync/.github/FUNDING.yml

Purpose: GitHub funding metadata for the rsync project.

Important APIs/types/functions: YAML keys `github: RsyncProject` and `patreon: AndrewTridgell`.

Control flow: none; GitHub reads this file to render sponsor links.

State and persistence: repository metadata only.

Dependencies/integration: integrates with GitHub Sponsors/Funding UI.

Risks: stale account names would break sponsor routing. No runtime impact.

Test signals: no tests; validation is GitHub's metadata handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/actionlint.yml -->
# sources/sync-backup/rsync/.github/workflows/actionlint.yml

Purpose: lint GitHub Actions workflow YAML.

Important APIs/types/functions: workflow triggers on pushes and pull requests to `master` when workflow/actionlint config files change; job installs pinned `rhysd/actionlint` version `1.7.12`, prints version, and runs `actionlint -color`.

Control flow: single `ubuntu-latest` job with read-only contents permission.

State and persistence: no artifacts; only CI logs.

Dependencies/integration: depends on `actions/checkout@v4`, curl over TLS, and actionlint's embedded checks including shellcheck-like validation.

Risks: download script is remote but version-pinned. Path filters mean workflow issues outside changed workflow files are caught only when those paths trigger.

Test signals: CI status is the signal; catches malformed YAML, expressions, runner references, and many shell mistakes.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/actionlint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/almalinux-8-build.yml -->
# sources/sync-backup/rsync/.github/workflows/almalinux-8-build.yml

Purpose: CI build and test coverage for AlmaLinux 8/RHEL-family compatibility.

Important APIs/types/functions: scheduled weekly plus push/PR path filters. Runs inside `almalinux:8` container on `ubuntu-latest`, installs EPEL/PowerTools deps, switches Python to 3.9, configures `--with-rrsync`, builds, runs `make check`, runs TCP daemon tests, smoke-tests `rsync-ssl`, and uploads binaries/manpages.

Control flow: checkout needs git installed in the container; test suite is run both default stdio-pipe and real TCP daemon transport.

State and persistence: uploads a 45-day `almalinux-8-bin` artifact.

Dependencies/integration: exercises older glibc/toolchain and packaging dependencies.

Risks: repository availability for EPEL/PowerTools and container package names can break CI independently of rsync.

Test signals: `make check`, TCP `runtests.py`, `rsync --version`, ssl listing smoke, and artifact creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/almalinux-8-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/android-static-build.yml -->
# sources/sync-backup/rsync/.github/workflows/android-static-build.yml

Purpose: cross-compile static Android rsync binaries.

Important APIs/types/functions: matrix builds `arm64-v8a` and `armeabi-v7a` using Android NDK clang, API level 24, static linking, bundled popt/zlib, disabled optional libraries/features, and qemu smoke execution.

Control flow: installs autoconf/automake/gawk/qemu, sets cross tools, exports configure cache values for Android cross-probing, builds `proto.h` serially to avoid header races, builds and strips `rsync`, checks file output for static linkage, runs `--version` under qemu, packages SHA256, and uploads artifacts.

State and persistence: artifact per ABI retained 45 days.

Dependencies/integration: integrates with GitHub-hosted NDK variables and qemu-user-static.

Risks: qemu test is best-effort; no full test suite runs for cross builds. Forced configure cache values must track Android behavior.

Test signals: architecture/static checks, qemu `--version`, and artifact checksums.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/android-static-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/asan-build.yml -->
# sources/sync-backup/rsync/.github/workflows/asan-build.yml

Purpose: sanitizer CI for memory safety and undefined behavior.

Important APIs/types/functions: weekly/push/PR/workflow_dispatch triggers. Uses clang with `-fsanitize=address,undefined`, `-fno-sanitize-recover=undefined`, `-DNDEBUG`, ASAN leak detection disabled, UBSan fatal.

Control flow: installs deps, configures `--with-rrsync --disable-md2man`, builds `check-progs`, prints version, runs default and TCP daemon test suites.

State and persistence: no artifacts on success; sanitizer failures surface in logs.

Dependencies/integration: depends on clang, ASan/UBSan runtimes, ACL/xattr/compression/OpenSSL development packages.

Risks: sanitizer/toolchain changes can create new findings; deliberate byteorder unaligned accesses need suppression/attributes in source.

Test signals: `runtests.py` under instrumented binary over both transports.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/asan-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/coverage.yml -->
# sources/sync-backup/rsync/.github/workflows/coverage.yml

Purpose: generate gcov/gcovr coverage reports on Ubuntu.

Important APIs/types/functions: installs coverage-capable dependencies, configures with coverage flags, runs `make coverage` and `make coverage-tcp`, extracts line/function/branch/decision summaries, and uploads HTML reports.

Control flow: triggered weekly and on relevant push/PR changes. The Makefile handles gcda cleanup, parallel test execution, report directories, and gcovr exclusions for vendored code.

State and persistence: uploads `coverage-html` artifact with `coverage` and `coverage-tcp` directories retained 45 days.

Dependencies/integration: integrates Makefile coverage targets, gcovr, gcc coverage instrumentation, and the test suite.

Risks: coverage data can be toolchain-sensitive; failed tests still produce reports but should fail the job through Makefile exit propagation.

Test signals: gcovr summaries and HTML artifacts for default and TCP transports.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/coverage.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/cygwin-build.yml -->
# sources/sync-backup/rsync/.github/workflows/cygwin-build.yml

Purpose: CI for rsync on Cygwin.

Important APIs/types/functions: Windows runner installs Cygwin packages, configures/builds rsync, runs tests, exercises TCP daemon path where supported, and uploads Windows/Cygwin artifacts such as `rsync.exe`.

Control flow: path-filtered push/PR plus schedule. The workflow bridges GitHub Actions Windows execution with Cygwin shell/toolchain commands.

State and persistence: binary/manpage artifacts retained for inspection.

Dependencies/integration: depends on Cygwin package availability, Windows runner behavior, and rsync portability layers.

Risks: Cygwin service/network behavior can differ from Unix; package mirror issues may cause unrelated failures.

Test signals: build, version, test suite, and artifact upload validate Windows-POSIX compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/cygwin-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/fleettest.yml -->
# sources/sync-backup/rsync/.github/workflows/fleettest.yml

Purpose: CI sanity test for rsync's fleettest orchestration script.

Important APIs/types/functions: prepares local SSH to localhost, writes a two-target JSON fleet configuration, runs `testsuite/fleettest.py --list`, then runs fleettest timing against two local targets.

Control flow: creates SSH key, trusts localhost host keys, starts sshd, verifies batch-mode SSH, then exercises parallel target isolation using two build directories.

State and persistence: temporary local SSH config and fleet JSON in the runner; no durable artifacts indicated.

Dependencies/integration: depends on OpenSSH service availability and Python fleettest tooling.

Risks: localhost SSH setup can be runner-sensitive; failures may reflect environment rather than rsync code.

Test signals: list sanity and successful parallel local fleet runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/fleettest.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/freebsd-build.yml -->
# sources/sync-backup/rsync/.github/workflows/freebsd-build.yml

Purpose: FreeBSD portability CI.

Important APIs/types/functions: uses a FreeBSD VM action to install build prerequisites, configure with `--with-rrsync`, build, print version, run default and TCP tests, smoke-test `rsync-ssl`, and upload artifacts.

Control flow: Linux-hosted GitHub runner delegates to a FreeBSD VM; commands run inside the VM.

State and persistence: 45-day artifact containing binaries and manpages.

Dependencies/integration: depends on the third-party VM action and FreeBSD package names.

Risks: VM startup/package instability can affect CI. Platform-specific filesystem/ACL behavior may require expected skips.

Test signals: build, `make check`, TCP `runtests.py`, ssl listing smoke, and artifact upload.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/freebsd-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/macos-build.yml -->
# sources/sync-backup/rsync/.github/workflows/macos-build.yml

Purpose: macOS build and test coverage.

Important APIs/types/functions: runs on macOS hosted runner, installs dependencies as needed, configures/builds rsync with rrsync, runs version and tests, likely includes TCP daemon coverage and artifact upload.

Control flow: path-filtered push/PR plus scheduled execution. Uses platform package manager/toolchain and standard rsync configure/make/test steps.

State and persistence: uploads built binaries/manpages for inspection.

Dependencies/integration: covers Darwin-specific APIs, filesystem metadata, terminal/signal differences, and bundled scripts.

Risks: Homebrew package churn and macOS runner image changes can cause unrelated failures; extended attribute/ACL semantics differ from Linux.

Test signals: build, suite execution, version output, and artifact upload.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/macos-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/netbsd-build.yml -->
# sources/sync-backup/rsync/.github/workflows/netbsd-build.yml

Purpose: NetBSD portability CI.

Important APIs/types/functions: VM-based workflow installs required tools, configures/builds rsync, runs version and tests, and uploads resulting artifacts.

Control flow: scheduled and path-filtered push/PR triggers. Commands run inside a NetBSD VM action from an Ubuntu-hosted job.

State and persistence: retained artifact with binaries/manpages.

Dependencies/integration: validates configure probes and portability code against NetBSD libc, filesystem, and networking.

Risks: third-party VM action and package availability are external failure points; test skips may reflect platform feature gaps.

Test signals: successful configure, make, test suite, TCP smoke where configured, and artifact upload.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/netbsd-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/openbsd-build.yml -->
# sources/sync-backup/rsync/.github/workflows/openbsd-build.yml

Purpose: OpenBSD portability CI.

Important APIs/types/functions: VM workflow builds rsync with OpenBSD packages, runs version/tests, includes TCP daemon and `rsync-ssl` smoke where available, and uploads artifacts.

Control flow: path-filtered push/PR and scheduled weekly run. Uses VM action to execute OpenBSD shell commands.

State and persistence: retained artifact bundle.

Dependencies/integration: checks OpenBSD-specific libc/network/filesystem behavior and security defaults.

Risks: OpenBSD package names, VM availability, and stricter platform semantics can break CI independently of source regressions.

Test signals: configure/build/test success and artifact presence.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/openbsd-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/scan-build.yml -->
# sources/sync-backup/rsync/.github/workflows/scan-build.yml

Purpose: run clang static analyzer and publish findings without gating merges.

Important APIs/types/functions: installs clang/clang-tools and dependencies, runs `scan-build ./configure`, then `scan-build -o scan-report make check-progs`, writes analyzer bug count to the GitHub step summary, and uploads the HTML report.

Control flow: push/PR path-filtered and manual triggers. It deliberately omits `--status-bugs`, so analyzer reports do not fail the job.

State and persistence: `scan-build-report` artifact, ignored if no files.

Dependencies/integration: integrates clang analyzer with configure-generated compiler wrappers.

Risks: informational status can allow real analyzer findings to be ignored; false positives are expected and documented.

Test signals: artifact and summary show static-analysis deltas; build of `check-progs` ensures analyzer sees main/test-helper code.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/scan-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/solaris-build.yml -->
# sources/sync-backup/rsync/.github/workflows/solaris-build.yml

Purpose: Solaris portability CI.

Important APIs/types/functions: uses `vmactions/solaris-vm@v1`, installs bash/automake/m4/python/autoconf/gcc/git, configures with rrsync and disables some optional libraries/man generation, builds, runs default and TCP tests, smokes `rsync-ssl`, and uploads artifacts.

Control flow: scheduled weekly plus path-filtered push/PR. The `usesh: true` option runs shell commands inside the VM.

State and persistence: `solaris-bin` artifact retained 45 days.

Dependencies/integration: validates Solaris configure probes and portability logic.

Risks: one configure command uses `-disable-zstd`, which looks like a single-dash typo and may be ignored or treated unexpectedly depending on configure parsing.

Test signals: build, `make check`, TCP tests, ssl listing smoke, and artifact upload.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/solaris-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/ubuntu-22.04-build.yml -->
# sources/sync-backup/rsync/.github/workflows/ubuntu-22.04-build.yml

Purpose: older Ubuntu LTS compatibility coverage.

Important APIs/types/functions: runs on `ubuntu-22.04`, installs ACL/xattr/compression/OpenSSL/doc dependencies, configures with rrsync, builds, installs, checks installed version, runs `make check`, `check30`, `check29`, TCP daemon tests, `rsync-ssl` smoke, and uploads artifacts.

Control flow: scheduled plus path-filtered push/PR. Root-required tests are run with `sudo` and expected skip lists.

State and persistence: `ubuntu-22.04-bin` artifact retained 45 days.

Dependencies/integration: exercises older runner image and protocol compatibility targets.

Risks: expected skip list can go stale as runner capabilities change.

Test signals: install smoke, three protocol test targets, TCP daemon test, SSL smoke, artifacts.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/ubuntu-22.04-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/ubuntu-build.yml -->
# sources/sync-backup/rsync/.github/workflows/ubuntu-build.yml

Purpose: primary Ubuntu CI and install/uninstall packaging smoke test.

Important APIs/types/functions: installs normal Linux dependencies, configures/builds rsync, runs `make install-all DESTDIR`, verifies expected installed binaries/manpages/stunnel config, runs `make uninstall-all DESTDIR`, checks no files remain, installs system-wide, runs protocol checks and TCP tests, smokes `rsync-ssl`, and uploads artifacts.

Control flow: path-filtered push/PR plus schedule. Uses `sudo` for root-sensitive tests.

State and persistence: temporary DESTDIR removed during smoke; `ubuntu-bin` artifact retained 45 days.

Dependencies/integration: validates Makefile install/uninstall targets as well as runtime suite.

Risks: install path expectations are tied to default configure prefix; runner package churn can affect optional feature coverage.

Test signals: packaging file existence/removal, `make check`, protocol 29/30 checks, TCP daemon tests, ssl smoke, artifact upload.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/ubuntu-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/ubuntu-version-mix.yml -->
# sources/sync-backup/rsync/.github/workflows/ubuntu-version-mix.yml

Purpose: compatibility tests between current rsync and bundled older rsync binaries.

Important APIs/types/functions: builds current `check-progs`, then loops over `old_versions/rsync_*`, matching each to a `testsuite/expect/<name>.expect` file, and runs `runtests.py` with `--rsync-bin2` for both pipe and TCP transports.

Control flow: scheduled weekly at a distinct minute and path-filtered triggers. Failures accumulate in `rc` so all peer/transport combinations run before final exit.

State and persistence: no artifact on success; logs grouped per peer/transport.

Dependencies/integration: depends on old binary executability and expectation files.

Risks: old binaries may be incompatible with new runner libraries; expectation files must track intended differences.

Test signals: matrix of current-vs-old compatibility across transports.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/ubuntu-version-mix.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/valgrind.yml -->
# sources/sync-backup/rsync/.github/workflows/valgrind.yml

Purpose: memory-error CI using Valgrind.

Important APIs/types/functions: configures with `--enable-debug`, builds `check-progs`, runs `runtests.py --valgrind` across a matrix of privilege/transport, preserves scratch, scans `valgrind.*.log` for nonzero error summaries, and uploads logs on failure.

Control flow: suite is allowed to finish even if individual tests fail; the explicit log scan is the gate. Leak checking is disabled because rsync intentionally leaves process-exit allocations.

State and persistence: failure artifact `valgrind-logs-<privilege>-<transport>` retained 7 days.

Dependencies/integration: depends on Valgrind, suppression file, sudo for root matrix, and testtmp log layout.

Risks: missing logs fail the job; suppression drift or Valgrind version changes can add noise.

Test signals: unsuppressed invalid reads/writes, uninitialized uses, bad frees, and syscall parameter issues fail the workflow.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/.github/workflows/valgrind.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/Makefile.in -->
# sources/sync-backup/rsync/Makefile.in

Purpose: autoconf template for building, installing, testing, generating, and cleaning rsync.

Important APIs/types/functions: defines configured variables, object groups, generated headers/docs, install/uninstall targets, build targets for `rsync`, `tls`, test helpers, `rrsync`, generated manpages, `proto.h`, coverage targets, protocol check targets, and maintenance targets.

Control flow: `configure` substitutes placeholders into `Makefile`. Normal `all` builds rsync, stunnel config, optional rrsync, and manpages. `check` depends on helper programs and symlinked fake tests, then runs `runtests.py`. Coverage targets guard for coverage flags, run tests, and invoke gcovr.

State and persistence: creates object files, generated headers, manpages, coverage directories, testtmp dirs, installed files under DESTDIR/prefix, and artifacts consumed by CI.

Dependencies/integration: coordinates C compiler, AWK generators, autoconf, bundled zlib/popt, optional SIMD/asm, test suite, and docs conversion.

Risks: generated-file dependency ordering matters under parallel make; Android workflow explicitly prebuilds `proto.h`. Install/uninstall target drift is caught by Ubuntu CI.

Test signals: `make check`, `check29`, `check30`, `coverage`, `coverage-tcp`, and CI install smoke.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/access.c -->
# sources/sync-backup/rsync/access.c

Purpose: daemon host allow/deny authorization based on hostnames, netgroups, and IP/CIDR address patterns.

Important APIs/types/functions: public `allow_access()`; helpers `match_hostname()`, `match_address()`, `match_binary()`, `make_mask()`, and `access_match()`.

Control flow: `allow_access()` reads module allow/deny lists and forward-DNS policy, then allows explicit allow matches, denies non-matches when only allow is present, rejects deny matches, and allows the rest. `access_match()` tokenizes list entries. Host matching checks reverse DNS/wildcards, optional netgroups, and optional forward DNS of config hostnames. Address matching parses numeric IPv4/IPv6 and masks.

State and persistence: `allow_forward_dns` is a file-static policy cache for the current check; no persistence.

Dependencies/integration: uses daemon config accessors `lp_hosts_allow`, `lp_hosts_deny`, `lp_forward_lookup`, DNS APIs, wildcard matching, logging, and `undetermined_hostname`.

Risks: DNS spoofing/staleness affects decisions; `strtok` and temporary token mutation mean inputs are copied first. IPv6 scope/mask parsing is subtle.

Test signals: covered indirectly by daemon access tests and CI TCP daemon runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/acls.c -->
# sources/sync-backup/rsync/acls.c

Purpose: converts, transmits, caches, receives, and applies filesystem ACLs for rsync transfers.

Important APIs/types/functions: public `get_acl`, `send_acl`, `receive_acl`, `cache_tmp_acl`, `uncache_tmp_acls`, `set_acl`, `match_acl_ids`, `default_perms_for_dir`, and `free_acl`. Internal structures model rsync ACLs (`rsync_acl`, `ida_entries`, `id_access`) and cached system ACL pairs (`acl_duo`).

Control flow: system ACLs are unpacked into portable rsync ACLs, permission bits are stripped when inferable from mode, ACLs are sent with de-duplicated indexes, received ACLs are cached, IDs are mapped, and destination ACLs are packed/applied. Fake-super stores ACLs in xattrs. Default directory ACLs are read to compute inherited permissions.

State and persistence: global `access_acl_list` and `default_acl_list` cache ACL identities during a run; `prior_*_count` tracks temporary entries for rollback. Persistent effects are real filesystem ACLs or xattr-encoded fake-super ACLs.

Dependencies/integration: depends on `lib/sysacls.h`, uid/gid mapping, xattrs, file-list ACL index macros, protocol varints, mode handling, and daemon/root/read-only flags.

Risks: platform ACL semantics differ greatly; mask/group interactions and special mode bits are sensitive. Stream bounds such as `MAX_WIRE_ACL_COUNT` defend against malformed input.

Test signals: exercised by ACL/xattr test suites and many platform CI jobs with ACL packages installed.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/android.c -->
# sources/sync-backup/rsync/android.c

Purpose: Android-specific runtime probe for whether `openat2()` is usable under Bionic/seccomp.

Important APIs/types/functions: public `openat2_usable()`; Android-only static `openat2_probe_handler()` and `sigjmp_buf`.

Control flow: on Android builds with `HAVE_OPENAT2`, the function installs a temporary `SIGSYS` handler, attempts `syscall(SYS_openat2, AT_FDCWD, ".", ...)`, records success/failure in a static cache, restores the old handler, and returns the cached result. On other platforms it returns 1.

State and persistence: static in-process cached result; no persistence.

Dependencies/integration: used by secure relative open code to avoid process death from trapped syscalls. Depends on `setjmp`, `sigaction`, Linux `openat2.h`, and Android compile-time macro.

Risks: temporary signal-handler changes are process-global; the probe is cached but not explicitly synchronized. It is intentionally Android-only because non-Android missing syscalls return errors instead of SIGSYS.

Test signals: Android static workflow compiles this path; runtime behavior is smoke-tested only through `rsync --version` under qemu.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/android.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/authenticate.c -->
# sources/sync-backup/rsync/authenticate.c

Purpose: implements rsync daemon challenge-response authentication.

Important APIs/types/functions: public `base64_encode()` and `auth_client()` plus server-side `auth_server()`; helpers `gen_challenge()`, `generate_hash()`, `check_secret()`, and `getpassf()`.

Control flow: server negotiates auth checksum, creates a time/pid/address challenge, reads `user response`, matches configured auth users or groups with optional `:deny`, `:ro`, `:rw`, verifies secrets file permissions and hashed password, zeros sensitive buffers, and returns authenticated username or NULL. Client chooses password file, `RSYNC_PASSWORD`, or interactive prompt, hashes password+challenge, and sends response.

State and persistence: reads secrets/password files and environment; mutates global `read_only` based on auth rule. Sensitive buffers are wiped where practical.

Dependencies/integration: uses daemon config, checksum negotiation from `checksum.c`, uid/gid group lookup, wildcard matching, IO protocol helpers, and cleanup exits.

Risks: file permission checks are security-critical. `getpass()` may truncate on some systems. Hash strength depends on negotiated digest availability.

Test signals: daemon auth tests and TCP CI runs exercise this path; checksum negotiation tests indirectly protect digest choices.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/authenticate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/backup.c -->
# sources/sync-backup/rsync/backup.c

Purpose: implements `--backup` behavior, creating backup names/directories and preserving replaced destination items.

Important APIs/types/functions: public `get_backup_name()` and `make_backup()`; helpers `validate_backup_dir()`, `copy_valid_path()`, and `link_or_rename()`.

Control flow: backup path construction either appends suffix or maps into `backup_dir`, creating and validating intermediate directories. `make_backup()` stats the existing item, tries hard-link or rename, deletes conflicting backup targets and retries, then falls back to copying or recreating devices/specials/symlinks while preserving selected attrs/ACLs/xattrs.

State and persistence: uses global backup configuration buffers and suffix. Persistent effects include created backup directories/files, links, renamed originals, copied files, and metadata updates.

Dependencies/integration: depends on delete logic, file-list construction, symlink safety, ACL/xattr caches, `set_file_attrs`, root/device flags, and backup logging.

Risks: rename is not atomic for backup semantics and hard-linked files require cleanup. Unsafe symlink handling intentionally skips certain backups. Directory validation deletes non-directory blockers.

Test signals: backup tests in rsync suite plus CI with ACL/xattr/root variants cover major paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/batch.c -->
# sources/sync-backup/rsync/batch.c

Purpose: supports `--write-batch`, `--only-write-batch`, and `--read-batch` stream replay.

Important APIs/types/functions: globals `batch_fd`, `batch_sh_fd`, `batch_stream_flags`; public `write_stream_flags()`, `read_stream_flags()`, `check_batch_flags()`, `open_batch_files()`, and `write_batch_shell_file()`; helpers `write_arg()`, `write_opt()`, and `write_filter_rules()`.

Control flow: writer records a bitmap of stream-affecting options. Reader checks and adjusts local flags to match the batch, with special handling for protocol versions and iconv. Batch-file open creates data and shell wrapper files. Shell script generation quotes arguments, converts write-batch option to read-batch, elides source/destination args, and appends filter rules via heredoc.

State and persistence: creates batch data file and executable `.sh` wrapper; mutates global options to match batch stream flags.

Dependencies/integration: depends on option globals, protocol version, filter lists, shell quoting, file IO, and cleanup error exits.

Risks: generated shell command uses heuristics and does not understand all options. Stream flag mismatch can silently mutate options except iconv, which is fatal.

Test signals: batch-related suite tests and protocol CI runs cover replay compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/byteorder.h -->
# sources/sync-backup/rsync/byteorder.h

Purpose: little-endian byte load/store helpers for rsync's wire and digest formats.

Important APIs/types/functions: macros `CVAL`, `UVAL`, `IVAL`, `SIVAL`, `IVAL64`, `SIVAL64`, plus alignment-sensitive inline implementations. On x86/x86_64, unaligned little-endian access is used; otherwise byte-wise careful access is used.

Control flow: preprocessor selects `CAREFUL_ALIGNMENT`. Non-careful paths use packed/unaligned accessors annotated to avoid UBSan false positives where supported.

State and persistence: no state; affects serialization/deserialization of integers in buffers.

Dependencies/integration: included widely by rsync core and checksum/auth/ACL code through `rsync.h`.

Risks: undefined behavior from unaligned loads is intentionally managed but compiler/UBSan-sensitive. Endianness assumptions must match wire protocol.

Test signals: sanitizer workflow explicitly documents byteorder unaligned accessor suppression; protocol tests and checksum tests indirectly validate correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/case_N.h -->
# sources/sync-backup/rsync/case_N.h

Purpose: macro include file that emits sequential `case N:` labels across repeated inclusions.

Important APIs/types/functions: preprocessor state macros `CASE_N_STATE_0`, `CASE_N_STATE_1`, etc. Each include defines the next state and emits a case label with fallthrough comments.

Control flow: used inside switch statements such as cleanup's reentry-safe state machine. Repeated inclusion advances the emitted case label without hand-maintaining numeric labels.

State and persistence: compile-time preprocessor state only; no runtime state.

Dependencies/integration: requires the includer to place it inside a `switch` and to avoid leaking state across unrelated uses unless reset by compilation unit boundaries.

Risks: unusual pattern is hard to read and can fail if included more times than supported labels or from an unexpected context.

Test signals: `cleanup.c` compile and cleanup-path CI indirectly validate generated labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/case_N.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/checksum.c -->
# sources/sync-backup/rsync/checksum.c

Purpose: checksum algorithm negotiation and digest computation for transfer checksums, file-list checksums, daemon auth, and generic accumulators.

Important APIs/types/functions: checksum registries `valid_checksums` and `valid_auth_checksums`; `parse_csum_name`, `parse_checksum_choice`, `csum_len_for_type`, `canonical_checksum`, `get_checksum1`, `get_checksum2`, `file_checksum`, `sum_init`, `sum_update`, `sum_end`, `init_checksum_choices`.

Control flow: initialization verifies optional OpenSSL/xxhash algorithms, negotiation picks transfer/file checksum names, digest functions dispatch among xxhash, xxh3, MD5, MD4 variants, SHA via OpenSSL, and none. File checksums map files in chunks; streaming sums keep one active accumulator.

State and persistence: globals track chosen algorithms, digest lengths, OpenSSL contexts, xxhash states, and current accumulator. No filesystem persistence except reading files for checksums.

Dependencies/integration: used by transfer matching, `--checksum`, daemon auth, batch output, and protocol negotiation.

Risks: many protocol compatibility branches preserve historical MD4 bugs and seed order. Static contexts are not reentrant. Algorithm availability varies by build.

Test signals: protocol-version tests, sanitizer/valgrind, and checksum-dependent transfer tests exercise this heavily.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/chmod.c -->
# sources/sync-backup/rsync/chmod.c

Purpose: parses and applies rsync's `--chmod` transformation rules.

Important APIs/types/functions: `struct chmod_mode_struct`; public `parse_chmod()`, `tweak_mode()`, `free_chmod_mode()`; helpers `mode_dest_special_bits()` and `mode_copy_bits()`.

Control flow: `parse_chmod()` is a state machine for symbolic and octal modes, supporting `D`/`F` directory/file filters, `u/g/o/a`, `+/-/=`, `r/w/x/X/s/t`, and permission-copy forms. It appends parsed operations to a linked list. `tweak_mode()` applies each operation to a mode while preserving non-permission file type bits.

State and persistence: parsed linked list is heap state owned by caller. Uses global `orig_umask` for unspecified symbolic targets.

Dependencies/integration: used by options/receiver metadata application; relies on rsync mode macros from `rsync.h`.

Risks: parser edge cases can silently reject complex chmod syntax by returning NULL. `X` depends on original executable bits or directory type.

Test signals: chmod-specific tests and `t_chmod_secure` helper in Makefile cover parser/application behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/cleanup.c -->
# sources/sync-backup/rsync/cleanup.c

Purpose: central end-of-run and interrupted-transfer cleanup.

Important APIs/types/functions: public `close_all()`, `_exit_cleanup()`, `cleanup_disable()`, `cleanup_set()`, `cleanup_set_pid()`; globals `called_from_signal_handler`, `shutting_down`, `flush_ok_after_signal`, `cleanup_got_literal`, and `cleanup_child_pid`.

Control flow: `_exit_cleanup()` is a reentry-safe switch state machine using `case_N.h`. It preserves first exit info, waits on cleanup child, preserves partial files when configured, flushes IO, unlinks temp files, removes pid file, derives final exit code from IO flags, logs exit, sends error-exit messages, drains IO, sleeps for daemon errors, closes sockets/files, and exits or `_exit`s when in a signal handler.

State and persistence: tracks current temp/target file and fds. Persistent effects include partial-file finalization, temp-file deletion, pid-file removal, and process termination.

Dependencies/integration: touches transfer finalization, IO messaging, logging, signal handling, daemon config, and process management.

Risks: cleanup can be invoked recursively or from signal context; switch-step discipline is critical. Wrong partial handling can lose resumable data.

Test signals: integration tests, valgrind, coverage, and signal/timeout paths exercise this indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/cleanup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/clientname.c -->
# sources/sync-backup/rsync/clientname.c

Purpose: obtains and validates daemon client IP/hostname, including HAProxy PROXY protocol support.

Important APIs/types/functions: public `client_addr()`, `client_name()`, and `read_proxy_protocol_header()`; helpers `client_sockaddr()`, `compare_addrinfo_sockaddr()`, `check_name()`, and `valid_ipaddr()`.

Control flow: client address uses PROXY-provided address when present, else `getpeername` and `getnameinfo`. `read_proxy_protocol_header()` parses PROXY v2 binary headers and v1 text headers, validates source/destination addresses and ports, and stores source IP. Hostname lookup performs reverse DNS then forward-confirmation to reduce spoofing. IPv4-mapped IPv6 sockets are normalized.

State and persistence: static `ipaddr_buf` stores the current client IP string; no persistent state.

Dependencies/integration: daemon accept/auth/access-control paths use this before host allow/deny and logging. Depends on socket APIs, DNS APIs, rsync IO readers, and cleanup exits.

Risks: PROXY parsing reads from the connection before normal protocol handling; malformed headers must fail closed. DNS validation is security-sensitive and can be slow or unreliable.

Test signals: daemon TCP tests, proxy protocol tests, and CI network runs exercise the path.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/clientname.c -->
