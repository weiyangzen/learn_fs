# Research: subset-b-009778

Grouped research for the source files assigned to `subset-b-009778`. Each section preserves the original source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/sync_test.go -->
# sources/user-network-fs/rclone/fs/sync/sync_test.go

## Purpose
This file is the broad integration test suite for rclone's `fs/sync` package. It exercises `CopyDir`, `Sync`, `MoveDir`, lower-level `moveDir`, rename tracking, delete modes, backup/suffix behavior, empty directory propagation, metadata copying, overlapping remote detection, transfer cutoffs, and the sync logger. The tests are deliberately end-to-end: most construct a `fstest.Run` with local and configured remote filesystems, mutate source/destination state, run a sync operation, and assert final filesystem listings and accounting counters.

## Important APIs, Functions, and Helpers
The suite defines shared test times `t1`, `t2`, and `t3`, plus `TestMain` that delegates to `fstest.TestMain`. Major clusters include copy tests (`TestCopyWithDryRun`, `TestCopy`, `testCopyMetadata`, `TestCopyNoTraverse`, `TestCopyCheckFirst`, files-from and max-depth cases), directory tests for empty dirs and directory modtimes, sync comparison tests (`TestSyncBasedOnCheckSum`, `TestSyncSizeOnly`, `TestSyncIgnoreSize`, `TestSyncIgnoreTimes`, `TestSyncIgnoreExisting`), delete-mode tests, filter/delete-excluded tests, server-side copy/move tests, overlap tests, compare-dest/copy-dest tests, backup/suffix tests, Unicode normalization, immutable and case handling tests, max-transfer/max-duration tests, concurrent delete/truncate tests, and no-op logging tests. Helper functions include `toyFileTransfers`, `testServerSideMove`, `testSyncBackupDir`, `testSyncSuffix`, `testSyncConcurrent`, `testSyncReplaceDirModTime`, `testNothingToTransfer`, `predictDstFromLogger`, `DstLsf`, `LoggerMatchesLsf`, `Diff`, and `testLoggerVsLsf`.

## Control Flow and State
Each test builds state through `fstest.NewRun`, `WriteFile`, `WriteObject`, `WriteBoth`, `Mkdir`, and rclone operations helpers. Context-local config is often created with `fs.AddConfig(ctx)` and then mutated for flags such as `DryRun`, `NoTraverse`, `CheckFirst`, `MaxDepth`, `IgnoreExisting`, `IgnoreTimes`, `TrackRenames`, `DeleteMode`, `CompareDest`, `CopyDest`, `BackupDir`, `Suffix`, `Immutable`, `IgnoreCaseSync`, `FixCase`, `MaxTransfer`, `MaxDuration`, and transfer/checker concurrency. Filters are swapped into context with `filter.ReplaceConfig`. Tests reset `accounting.GlobalStats()` before operations when transfer counts or error state matter.

The sync operations persist changes to temporary local/remote test backends. The expected persistent state is asserted through `r.CheckLocalItems`, `r.CheckRemoteItems`, `r.CheckRemoteListing`, `fstest.CheckItems`, and directory metadata helpers. Some tests intentionally leave global-like knobs temporarily modified and restore them, for example bandwidth limits and log level.

## Dependencies and Integration Points
This file integrates with all registered backends via `_ "github.com/rclone/rclone/backend/all"`, the global accounting subsystem, filtering, hash comparison, operations, server-side move/copy feature detection, metadata APIs, `fserrors`, `bilib.CaptureOutput`, Unicode normalization, and `lib/transform` for logger path handling. It also depends on backend feature flags such as `CanHaveEmptyDirectories`, metadata support, `DirSetModTime`, `DirModTimeUpdatesOnWrite`, `Copy`, `DirMove`, case sensitivity, and local filesystem behavior.

## Risks and Edge Cases
The tests cover high-risk sync behavior: dry-run must not mutate destinations, no-traverse must not deadlock, errors should block deletes unless `IgnoreErrors` is set, excluded files must not be deleted unless delete-excluded is requested, overlapping remotes must fail fatally, backup/suffix paths must not be overwritten incorrectly, rename tracking depends on hash/modtime/server-side move capability, and max-transfer/max-duration cutoffs differ between hard, soft, and cautious modes. The suite also accounts for backend variability, eventual consistency, macOS clone speed, missing hashes, unsupported modtimes, empty-file restrictions, and Unicode normalization differences.

## Test Signals
The file is itself a dense test signal for sync correctness. It uses both state assertions and log/lsf equivalence through `predictDstFromLogger` and `testLoggerVsLsf`. Many tests skip based on backend capabilities rather than weakening assertions. Transfer counters, rename counters, fatal error checks, and captured logs are used to verify behavior that final listings alone cannot prove.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/sync_transform_test.go -->
# sources/user-network-fs/rclone/fs/sync/sync_transform_test.go

## Purpose
This file tests integration between sync/move operations and `lib/transform` path transformations. It verifies that transformed file and directory names are applied consistently during sync, move, check, logging, manual transform repair, base64 round trips, and error handling.

## Important APIs, Functions, and Helpers
`TestTransform` runs a table of transform configurations including NFC, NFD, base64 encode, prefix/suffix, truncate, encoder/decoder, charmap, lowercase, and ASCII transforms. `makeTestFiles` creates many deterministic test names with UTF-8 and ASCII variation, plus extra words that expose split/prefix behavior. `deleteDSStore` removes macOS `.DS_Store` noise. `compareNames` lists remote objects through `walk.ListR`, sorts by transformed name, and checks that actual remote paths match `transform.Path`. `detectEncoding` reports NFC/NFD status for assertion messages.

Specific tests cover transformed copy (`TestTransformCopy`), stacked transforms (`TestDoubleTransform`), file-only, dir-only, all-entry, and no-tag behavior, repeated sync idempotence, syntax validation, canceling transforms, `MoveDir`, `operations.TransformFile` with and without server-side copy/move features, base64 encode/decode round trip, and an illegal path transform error.

## Control Flow and State
Tests set transform options through `transform.SetOptions(ctx, ...)`, create source and destination content with `fstest.Run`, then call `Sync` or `MoveDir` with empty directory copying enabled where needed. Assertions compare both local original paths and remote transformed paths. Some tests deliberately switch transform options mid-test, for example transforming a moved remote file back to its original path with `operations.TransformFile`.

Persistent state is confined to temporary test remotes. Transform options are context/global transform state, so tests must call `SetOptions` before each scenario to avoid relying on prior defaults.

## Dependencies and Integration Points
The suite imports all backends, `fs`, `accounting`, `filter`, `operations`, `walk`, `fstest`, and `lib/transform`. It depends on sync logger helpers from `sync_test.go`, walk recursive listing, filter-based deletion of `.DS_Store`, and backend feature disabling for manual transform paths.

## Risks and Edge Cases
Path transforms are risky because they can affect directory components, file leaves, empty directories, logger output, check comparisons, and reverse operations. The tests cover lossy transforms, conflicting transforms, illegal transformed names containing slash, backend feature fallbacks, repeated runs that should not double-transform names, and Unicode normalization differences. `TestError` confirms a transform error leaves the original file structure intact.

## Test Signals
The strongest signals are exact remote listing checks and `compareNames` validation against `transform.Path`. Logger-vs-lsf checks verify that transformed paths reported by sync match actual destination listings. `operations.Check` in `TestAllTag` proves higher-level comparison understands transformed names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/sync_transform_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/terminalcolormode.go -->
# sources/user-network-fs/rclone/fs/terminalcolormode.go

## Purpose
This file defines the user-facing enum for terminal color handling. It models whether ANSI color should be selected automatically, never used, or always used.

## Important APIs, Types, and Functions
`TerminalColorMode` is a type alias for `Enum[terminalColorModeChoices]`, reusing rclone's generic enum implementation. Constants are `TerminalColorModeAuto`, `TerminalColorModeNever`, and `TerminalColorModeAlways`. The unexported `terminalColorModeChoices` type provides `Choices() []string`, mapping enum ordinals to `"AUTO"`, `"NEVER"`, and `"ALWAYS"`.

## Control Flow and State
There is no runtime control flow beyond enum choice lookup. State is held only in values of the enum type. String parsing, JSON parsing, and unknown-value formatting are supplied by the generic `Enum` implementation elsewhere in `fs`.

## Dependencies and Integration Points
This type integrates with the rclone configuration and flag system through the `Enum` type's expected `String`, `Set`, `Type`, and JSON behavior. It is likely consumed by logging or terminal presentation configuration where color mode must be represented as a stable option.

## Risks and Edge Cases
The main risk is ordinal stability: the `Choices` slice uses constants as indexes, so reordering constants or strings changes serialized numeric meanings. Adding a new mode requires adding both a constant and a string at the matching index. Unknown values are not handled here directly, so behavior depends on `Enum`.

## Test Signals
Coverage is in `terminalcolormode_test.go`, which checks string output, case-insensitive `Set`, JSON string parsing, JSON numeric parsing, and rejection of invalid names and out-of-range ordinals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/terminalcolormode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/terminalcolormode_test.go -->
# sources/user-network-fs/rclone/fs/terminalcolormode_test.go

## Purpose
This file tests the `TerminalColorMode` enum wrapper and, indirectly, the generic enum behavior used by rclone flag/config types.

## Important APIs and Tests
`TestTerminalColorModeString` verifies known constants render as `"AUTO"`, `"ALWAYS"`, and `"NEVER"`, while an unknown ordinal renders as `Unknown(36)`. `TestTerminalColorModeSet` checks case-insensitive parsing for `"auto"`, `"ALWAYS"`, and `"Never"`, and verifies `"INVALID"` returns an error without selecting a meaningful mode. `TestTerminalColorModeUnmarshalJSON` verifies JSON strings and JSON numeric enum values are accepted when valid and rejected when invalid or out of range.

## Control Flow and State
Each test is table-driven. Tests create a fresh `TerminalColorMode` variable per case, call `Set` or `json.Unmarshal`, and assert both error state and final value. There is no persistent state beyond local variables.

## Dependencies and Integration Points
The tests depend on `encoding/json`, `strconv`, and `testify` assertions. They validate the behavior expected by config file decoding, command-line flag parsing, and any code that logs or displays terminal color mode.

## Risks and Edge Cases
Important edge cases are mixed-case input, invalid string input, unknown enum values, and JSON numeric ordinals. Numeric JSON support is useful for backward compatibility but increases risk if enum ordinals change.

## Test Signals
The suite confirms that the enum can be used as a robust config/flag value: user-friendly strings work in any case, invalid values fail, and unexpected stored numeric values do not silently map to unsupported states.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/terminalcolormode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/tristate.go -->
# sources/user-network-fs/rclone/fs/tristate.go

## Purpose
This file implements `Tristate`, a nullable boolean used by configuration and flag code when `true`, `false`, and unset must be distinguished.

## Important APIs, Types, and Functions
`Tristate` has two fields: `Value bool` and `Valid bool`. `String` returns `"unset"` when invalid and `"true"` or `"false"` when valid. `Set` lowercases input and treats `""`, `"nil"`, `"null"`, and `"unset"` as invalid/unset; otherwise it delegates to `strconv.ParseBool`, enabling values such as `true`, `false`, `1`, and `0`. `Type` returns `"Tristate"` for flag integration. `Scan` implements `fmt.Scanner` by tokenizing input and calling `Set`. `UnmarshalJSON` decodes into `*bool`, so JSON `null` maps to unset and JSON booleans map to valid values. `MarshalJSON` writes `null` for unset or a boolean for valid values.

## Control Flow and State
All behavior is value-local. Mutating methods update `Valid` and `Value`; JSON and scanner paths funnel into the same state model. One subtle behavior is that setting an unset value only clears `Valid`; it does not explicitly reset `Value`, so callers should treat `Value` as meaningful only when `Valid` is true.

## Dependencies and Integration Points
The type depends on `encoding/json`, `fmt`, `strconv`, and `strings`. It integrates with rclone's `Flagger` and `FlaggerNP` contracts from `types.go`, standard JSON config serialization, and `fmt.Fscan` style parsing.

## Risks and Edge Cases
The main risk is callers reading `Value` without checking `Valid`. Another edge is invalid textual input: `Set` wraps parse errors with context, while JSON invalid tokens fail through `encoding/json`. Because `Set` lowercases input, case-insensitive unset keywords and booleans work.

## Test Signals
`tristate_test.go` verifies interface satisfaction, string rendering, text parsing, scanning, JSON unmarshal for `null` and booleans, invalid JSON behavior, and JSON marshal output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/tristate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/tristate_test.go -->
# sources/user-network-fs/rclone/fs/tristate_test.go

## Purpose
This file validates `Tristate` as both a nullable boolean and a rclone flag/config value.

## Important APIs and Tests
Compile-time assertions confirm `*Tristate` satisfies `Flagger` and `Tristate` satisfies `FlaggerNP`. `TestTristateString` covers unset and valid value rendering. `TestTristateSet` covers unset spellings, boolean spellings, numeric boolean spellings, uppercase unset, and invalid input. `TestTristateScan` verifies `fmt.Sscan` integration. `TestTristateUnmarshalJSON` covers `null`, booleans, invalid identifiers, and empty input. `TestTristateMarshalJSON` checks unset serializes to `null` and valid states serialize to JSON booleans.

## Control Flow and State
The tests instantiate fresh values per case and assert both error behavior and final struct fields. They explicitly show that `Valid` controls interpretation, not `Value` alone.

## Dependencies and Integration Points
The tests use `encoding/json`, `fmt`, `testing`, and `testify`. They protect behavior used by command-line flag parsing, config file JSON, and scanner-based parsing.

## Risks and Edge Cases
The suite covers the key edge cases: unset values with different spellings, invalid text that must not be accepted, JSON `null`, and invalid JSON. It does not directly test that `Set("unset")` leaves an old `Value` unchanged, but other tests establish that invalid `Valid` should dominate `Value`.

## Test Signals
Signals are strong for serialization and flag integration. Interface assertions catch accidental method signature changes, and table tests catch user-facing parsing regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/tristate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/types.go -->
# sources/user-network-fs/rclone/fs/types.go

## Purpose
This file defines core filesystem interfaces and shared support types for rclone. These interfaces form the contract every backend and many wrappers must implement.

## Important APIs, Types, and Functions
`Fs` embeds `Info` and requires `List`, `NewObject`, `Put`, `Mkdir`, and `Rmdir`. `Info` exposes backend identity, root, precision, supported hashes, and optional `Features`. `Object` embeds `ObjectInfo` and requires `SetModTime`, `Open`, `Update`, and `Remove`. `ObjectInfo` embeds `DirEntry` and adds `Hash` and `Storable`. `DirEntry` defines common listing metadata: filesystem, string description, remote path, modtime, and size. `Directory` extends `DirEntry` with `Items` and `ID`.

Optional interfaces include `MimeTyper`, `IDer`, `ParentIDer`, `ObjectUnWrapper`, tier getters/setters, metadata getters/setters, and directory `SetModTimer`. Aggregate interfaces `FullDirectory`, `FullObjectInfo`, and `FullObject` provide compile-time coverage targets for wrappers. `ObjectOptionalInterfaces` and `DirectoryOptionalInterfaces` return supported/unsupported optional interface names. `ListRCallback` and `ListRFn` define recursive listing callbacks. `Flagger` and `FlaggerNP` define config value contracts. `NewUsageValue` saturates numeric usage values into `*int64`, and `Usage` represents quota/about data. `WriterAtCloser` combines `io.WriterAt` and `io.Closer`. `Unknown` is an `Info` implementation for cases where a real filesystem is unavailable.

## Control Flow and State
Most of the file is declarative interface definition. The optional-interface helper functions use type assertions to build supported and unsupported string slices. `NewUsageValue` guards overflow by clamping values greater than `math.MaxInt64`. `unknownFs` methods return stable placeholder metadata and empty features.

## Dependencies and Integration Points
This is a central dependency for backends, operations, sync, walk, filter, metadata, accounting, and tests. It imports `context`, `encoding/json`, `io`, `math`, `time`, and `fs/hash`. The interfaces encode expectations about object mutability, listing semantics, hash support, unknown-size upload handling, and optional feature discovery.

## Risks and Edge Cases
Changing these interfaces has high blast radius across all backends. Semantics in comments are important: `List` should return `ErrorDirNotFound`, `NewObject` should distinguish objects and directories where possible, `Put`/`Update` must handle unknown sizes safely, and `Mkdir` should be idempotent. Optional interface reporting can drift if new optional interfaces are added elsewhere but not listed here. `NewUsageValue` only handles non-negative-style numeric conversions by type set and clamps high values, so callers should still model unsupported fields as nil.

## Test Signals
Direct tests are distributed across backend and package tests rather than this file. Interface satisfaction is exercised throughout rclone. `tristate_test.go` uses `Flagger`/`FlaggerNP`; walk and sync tests depend on `Fs`, `Object`, `Directory`, `ListRFn`, and `DirEntries` contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/version.go -->
# sources/user-network-fs/rclone/fs/version.go

## Purpose
This file builds the public `Version` string from compile-time version components.

## Important APIs and Variables
`Version` is an exported package variable containing the complete rclone version string. In `init`, if `Version` was not already set by build flags, it is assigned from `VersionTag` alone or `VersionTag + "-" + VersionSuffix` when `VersionSuffix` is non-empty.

## Control Flow and State
The only control flow is package initialization. State is global and intentionally mutable at build/link time: `Version`, `VersionTag`, and `VersionSuffix` can be overridden by release tooling or linker flags. At runtime, consumers read `fs.Version`.

## Dependencies and Integration Points
This file depends on `versiontag.go` and `versionsuffix.go` for defaults. It integrates with CLI version output, release builds, telemetry/logging, and any compatibility checks that need the rclone version.

## Risks and Edge Cases
The main risk is initialization order or build injection: if `Version` is prefilled, the default construction is skipped. If `VersionSuffix` is empty, no trailing hyphen is emitted. Release automation must keep `VersionTag` and `VersionSuffix` consistent.

## Test Signals
There is no direct test in this subset. Behavior is simple and usually verified by build/release tests or CLI version output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/versioncheck.go -->
# sources/user-network-fs/rclone/fs/versioncheck.go

## Purpose
This file is a compile-time Go version gate. Its build tag selects it when compiling with Go versions older than 1.25.

## Important APIs and Functions
The file has build constraint `//go:build !go1.25`. Its `init` function calls `Go_version_1_25_required_for_compilation()`, a deliberately undefined function, causing compilation to fail with a clear symbol name on unsupported Go versions.

## Control Flow and State
There is no normal runtime behavior in supported builds because the file is excluded under Go 1.25 or newer. In unsupported builds, package initialization cannot link/compile due to the undefined function. No persistent state is used.

## Dependencies and Integration Points
It integrates with the Go build system and rclone's minimum compiler policy. It does not import packages. The user-facing comment recommends upgrading to Go 1.25 or later.

## Risks and Edge Cases
This gate is intentionally brittle: once the project's minimum Go version changes, both the build tag and function name/comment must be updated. If the build tag is wrong, supported compilers could fail or unsupported compilers could proceed.

## Test Signals
There are no normal unit tests. The signal is the build matrix: older Go toolchains should fail, and supported toolchains should exclude the file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/versioncheck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/versionsuffix.go -->
# sources/user-network-fs/rclone/fs/versionsuffix.go

## Purpose
This file provides the default pre-release version suffix.

## Important APIs and Variables
`VersionSuffix` is an exported package variable initialized to `"DEV"`. `version.go` appends it to `VersionTag` when constructing `Version`, unless `Version` is set directly or the suffix is overridden to empty.

## Control Flow and State
There is no control flow. The variable is global package state intended to be overridden by release builds or linker flags.

## Dependencies and Integration Points
It integrates with `version.go`, release automation, CLI version reporting, and any code that distinguishes development builds from tagged releases.

## Risks and Edge Cases
If release automation fails to clear or replace this suffix, release binaries may advertise a development-style version. Since it is a variable rather than a constant, runtime mutation is possible but should be avoided outside controlled build/version setup.

## Test Signals
No direct tests are present. Behavior is indirectly visible through `fs.Version`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/versionsuffix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/versiontag.go -->
# sources/user-network-fs/rclone/fs/versiontag.go

## Purpose
This file defines the default base rclone version tag.

## Important APIs and Variables
`VersionTag` is an exported package variable initialized to `"v1.75.0"`. It is combined with `VersionSuffix` by `version.go` to form `Version` when no full version is injected.

## Control Flow and State
There is no control flow. The variable is global build/version state and can be overridden by release tooling.

## Dependencies and Integration Points
This file integrates with `version.go`, release metadata, CLI version output, and any compatibility code that reads `fs.Version`.

## Risks and Edge Cases
The hard-coded tag must be kept in sync with release cadence. A stale tag or incorrect suffix combination would produce misleading version output. Because this is mutable package state, linker-time override is possible and expected.

## Test Signals
No direct tests are present in this subset. Verification is typically through build artifacts or version command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/versiontag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/walk/walk.go -->
# sources/user-network-fs/rclone/fs/walk/walk.go

## Purpose
This package implements directory traversal and recursive listing helpers for rclone filesystems. It chooses between concurrent non-recursive `List` traversal and backend `ListR`, applies filters, handles max-depth behavior, synthesizes directories for bucket-style remotes, and can materialize listings as `dirtree.DirTree`.

## Important APIs, Types, and Functions
`ErrorSkipDir` lets a walk callback skip a directory. `ErrorCantListR` reports unavailable recursive listing. `Func` is the `Walk` callback signature. `Walk` is the main ordered directory traversal API and selects no-traverse/files-from, `ListR`, or sorted `List` paths. `ListType` (`ListObjects`, `ListDirs`, `ListAll`) filters recursive listing entries by object/directory kind. `ListR` is the public recursive listing API that uses backend `Features().ListR` when safe, otherwise falls back to walking. `GetAll` collects all recursive objects and directories.

Internal helpers include `listRwalk`, `dirMap`, `newDirMap`, `parentDir`, `addEntries`, `sendEntries`, `listR`, `walkListDirSorted`, `walkListR`, `walk`, `walkRDirTree`, `walkNDirTree`, `NewDirTree`, and `walkR`.

## Control Flow and State
`Walk` first adjusts filter-aware backend behavior via context, then chooses a path based on config (`NoTraverse`, `UseListR`), filters (`HaveFilesFrom`), max level, and backend features. The non-recursive `walk` path starts `ci.Checkers` workers, sends `listJob` values through a channel, serializes callback calls with a mutex, tracks outstanding traversal jobs with wait groups, and returns the first counted error. `ErrorSkipDir` suppresses child job enqueueing without failing the walk.

`ListR` disables direct backend `ListR` for files-from, bounded recursion, exclude-file, and directory filters. Direct `listR` counts listed entries, optionally synthesizes missing parent directories with `dirMap`, applies object/directory filtering, applies active filters, and serializes callback calls. `walkRDirTree` converts arbitrary-order recursive entries into a sorted `dirtree.DirTree`, including parent synthesis, depth clipping, excluded-object parent preservation, and exclude-file pruning.

## Dependencies and Integration Points
The package depends on `fs`, `accounting`, `dirtree`, `filter`, and `list`. It is used by sync, operations, fstest cleanup/listing, and any code needing recursive enumeration. It integrates tightly with backend features (`ListR`, `BucketBased`, `FilterAware`), global config (`Checkers`, `NoTraverse`, `UseListR`), and filter config.

## Risks and Edge Cases
High-risk areas are concurrency and callback ordering, depth semantics, filter-aware backend behavior, no-traverse/files-from handling, directory synthesis for bucket remotes, and error counting. The non-recursive path guarantees callbacks are not concurrent but listings are concurrent. The `ListR` path does not promise parent-before-child order, while `Walk` does. Exclude-file pruning and max-level clipping are subtle because excluded objects can still require parent directories to avoid destructive sync decisions.

## Test Signals
`walk_test.go` covers empty walks, skip behavior, not-found masking, depth limits, multi-level concurrency, errors, `walkRDirTree`, exclude-file pruning, `ListType.Filter`, direct `listR` filtering and bucket directory synthesis, and `dirMap` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/walk/walk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/walk/walk_test.go -->
# sources/user-network-fs/rclone/fs/walk/walk_test.go

## Purpose
This file unit-tests the walk package's traversal, recursive listing, filtering, synthetic directory, and error behavior using mock filesystem entries.

## Important APIs, Types, and Tests
The test harness defines `listResult`, `listResults`, `errorMap`, and `listDirs`. `newListDirs` creates scripted list/walk expectations. `ListDir` and `ListR` simulate backend listing APIs, `WalkFn` validates callback arguments and returns scripted errors, and `Walk`/`WalkR` run the implementation under test.

Tests cover empty walks, skip behavior, not-found errors and masking, max depth (`SetLevel`), `walkNDirTree`, multi-level trees, terminal errors, `walkRDirTree` from flat recursive entries, root subpaths, max-level clipping, exclude filters, exclude-file pruning, `ListType` object/directory filtering, direct `listR` behavior with filters and bucket directory synthesis, and `dirMap` add/send behavior.

## Control Flow and State
The mock harness uses maps as expected-call ledgers. `ListDir` consumes entries from `results` and records expected callback values in `walkResults`; `WalkFn` consumes `walkResults` and `walkErrors`. `IsFinished` asserts all expectations were consumed unless disabled for early-error cases. This makes the tests sensitive to extra, missing, or incorrectly ordered traversal work while allowing concurrent walk internals.

Filter tests replace context filter config or mutate exclude-file options to check pruning. `TestListR` creates a mock fs and a custom `doListR` callback that returns entries under the requested prefix.

## Dependencies and Integration Points
The tests use `mockdir`, `mockfs`, `mockobject`, `filter`, `fserrors`, and `testify`. They validate integration with `fs.DirEntries`, `fs.Object`, `fs.Directory`, `fs.ListRCallback`, and rclone's error counting wrappers.

## Risks and Edge Cases
The tests specifically guard risky behavior: `ErrorSkipDir` should not be returned as an error, callbacks should receive listing errors and be able to mask them in the non-ListR path, max depth should stop recursion correctly, direct `ListR` must fall back or filter safely, exclude-file should prune entire directories only when appropriate, bucket remotes need synthetic parent dirs, and callback errors must propagate without leaving expectations inconsistent.

## Test Signals
Expected `dirtree.DirTree.String()` output is used as a compact golden signal for tree structure. `dirMap` tests verify exact internal maps and emitted synthetic directories. `TestListR` checks exact callback order/content for object-only, dir-only, filtered, subdir, and bucket-based cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/walk/walk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/fstest.go -->
# sources/user-network-fs/rclone/fstest/fstest.go

## Purpose
This package provides shared test utilities for rclone filesystem/backend tests. It initializes test configuration, creates random remotes, builds expected file items, verifies listings and metadata, handles eventual consistency, and cleans up test remotes.

## Important APIs, Types, and Functions
Global flags include `RemoteName`, `Verbose`, dump flags, `Individual`, `LowLevelRetries`, `UseListR`, `SizeLimit`, and `ListRetries`. `Initialise` configures password behavior, config path, accounting, logging, retry counts, and fast-list behavior. `Item` stores expected path, hashes, modtime, and size; `NewItem` computes hashes from content. Time helpers include `CheckTimeEqualWithPrecision`, `AssertTimeEqualWithPrecision`, and `Time`.

`Items`, `NewItems`, `Find`, and `Done` track expected object matches. Listing helpers include `CheckListingWithRoot`, `CheckListingWithPrecision`, `CheckListing`, `CheckItemsWithPrecision`, `CheckItems`, and `CompareItems`. Remote helpers include `LocalRemote`, `RandomRemoteName`, `RandomRemote`, and `Purge`. Discovery helpers include `NewObject`, `NewDirectoryRetries`, and `NewDirectory`. Metadata helpers include `CheckEntryMetadata` and `CheckDirModTime`. `Gz` returns gzip-compressed string content for tests.

## Control Flow and State
`Initialise` mutates the global rclone config and starts accounting/logging. Listing checks call `walk.GetAll` with retries and exponential backoff-ish sleeps to tolerate eventual consistency, optionally flushing directory caches between attempts. Expected items are tracked in maps normalized for macOS filename behavior. `RandomRemote` creates either a local temp path or a named remote child with a random `rclone-test-...` leaf and returns a finalizer that purges it.

`Purge` first tries a backend purge feature, then falls back to recursive listing, object removal, and reverse-order directory removal. New-object and new-directory helpers retry to handle eventual consistency.

## Dependencies and Integration Points
The package depends on `fs`, `accounting`, config/configfile, `hash`, `log`, `walk`, `random`, `testy`, and Unicode normalization. It is a foundational dependency of sync, walk, backend, and operation tests. It integrates with backend feature flags such as purge, directory cache flush, empty directory support, metadata support, and directory modtime support.

## Risks and Edge Cases
Because these helpers sit under many tests, changes can cause widespread false positives or false negatives. Important edge cases include macOS Unicode normalization, remotes that cannot store empty directories, remotes with eventual consistency, unsupported directory modtimes, CI-specific Windows timestamp precision, cleanup errors that should not affect global stats, and safe random remote naming. `CheckListingWithRoot` also resets a single expected listing error for empty directory checks to avoid poisoning later assertions.

## Test Signals
This is mostly test infrastructure rather than code under direct test in this subset. Its behavior is exercised extensively by `sync_test.go`, `sync_transform_test.go`, backend tests, and walk-related cleanup/listing paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fstest/fstest.go -->
