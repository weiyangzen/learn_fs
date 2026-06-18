# subset-b-009135 research

Grouped research report for subset-b-009135. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools.go -->
# sources/sync-backup/git-lfs/tools/filetools.go

Purpose: core file/path helpers for Git LFS tools, including existence checks, permission-aware directory and temp-file creation, tilde/config expansion, hash verification, concurrent directory walking, write-bit toggling, executable permission derivation, and canonical path handling.

Important APIs/types/functions: `FileOrDirExists`, `FileExists`, `DirExists`, `FileExistsOfSize`, `ResolveSymlinks`, `RenameFileCopyPermissions`, `CleanPaths`, `repositoryPermissionFetcher`, `Mkdir`, `MkdirAll`, `ExpandPath`, `ExpandConfigPath`, `VerifyFileHash`, `FastWalkDir`, `fastWalker`, `SetFileWriteFlag`, `TempFile`, `ExecutablePermissions`, `CanonicalizePath`, and `TrimCurrentPrefix`. Test seams are the package-level `currentUser`, `lookupUser`, and `lookupConfigHome` function variables.

Control flow: simple path helpers delegate to `os.Stat`; rename first mirrors destination permissions onto the source then calls `RobustRename`; path expansion parses `~`/`~user`, consults injected user lookup functions, optionally resolves symlinks, and joins the suffix. `FastWalkDir` starts a goroutine-backed walker, reads directory entries in batches of 100, and uses a configurable goroutine limit from `LFS_FASTWALK_LIMIT`. `CanonicalizePath` first translates Cygwin paths, makes them absolute, then calls the platform-specific canonicalizer, allowing missing paths only when requested.

State and persistence: no durable state is owned here, but file modes, temp files, destination replacement, and filesystem traversal are direct side effects. `TempFile` creates real temp files with repository permissions and cleans up on chmod failure. Fast walk state is held in channels, wait groups, and atomic counters until traversal completes.

Dependencies and integration points: depends on Go `os`, `filepath`, `runtime`, `sync/atomic`; Git LFS `errors` and `tr`; platform files provide `CanonicalizeSystemPath`, `RobustRename`, and `doWithUmask`. Integrates with repository configuration through `RepositoryPermissions`, with transfer code through hash verification and temp-file helpers, and with Cygwin handling in `os_tools.go`.

Risks: `FastWalkDir` is intentionally unordered, so callers must not depend on sorted traversal. The global umask change in `Mkdir`/`MkdirAll` is process-wide during the callback. `CleanPaths` trims separators but does not call `path.Clean` despite the comment. `ExpandPath` relies on package globals that tests mutate. `VerifyFileHash` reads whole files and reports mismatches only after full copy.

Test signals: `filetools_test.go` covers clean paths, tilde/config expansion, fast walking with large directories, write-flag behavior across platforms, and executable permission mapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools_nix.go -->
# sources/sync-backup/git-lfs/tools/filetools_nix.go

Purpose: non-Windows implementation of `CanonicalizeSystemPath`.

Important APIs/types/functions: `CanonicalizeSystemPath(path string) (string, error)`.

Control flow: converts input to an absolute path with `filepath.Abs`, then resolves symlinks with `filepath.EvalSymlinks`.

State and persistence: read-only filesystem metadata access; no persistent state.

Dependencies and integration points: used by `ResolveSymlinks` and `CanonicalizePath` in `filetools.go` on Unix-like builds.

Risks: missing paths return an error from `EvalSymlinks`; callers needing missing-path tolerance must use `CanonicalizePath(..., true)`.

Test signals: indirectly covered by canonicalization callers; no dedicated nix-only test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools_test.go -->
# sources/sync-backup/git-lfs/tools/filetools_test.go

Purpose: unit tests for general file/path utilities.

Important APIs/types/functions: test cases for `CleanPaths`, `ExpandPath`, `ExpandConfigPath`, `fastWalkDir`, `SetFileWriteFlag`, and `ExecutablePermissions`; helpers `createFastWalkInputData`, `collectFastWalkResults`, `getFileMode`, and `uniq`.

Control flow: path-expansion tests replace package-level lookup functions with stubs and restore them with `defer`; fast-walk tests create a temp tree and compare sorted actual/expected entries; write-flag tests branch for Windows permission behavior.

State and persistence: creates temp directories/files, changes the process working directory during fast-walk setup, and mutates package globals for test injection.

Dependencies and integration points: uses `testify/assert`, Go `os`, `filepath`, `runtime`, and package-internal unexported helpers because it is in package `tools`.

Risks: global function replacement and `os.Chdir` would be unsafe with parallel tests; these tests deliberately avoid `t.Parallel`. Permission assertions may vary on filesystems with unusual mode semantics.

Test signals: provides broad behavioral coverage for the path and permission helpers but not for all hash/canonicalization paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools_windows.go -->
# sources/sync-backup/git-lfs/tools/filetools_windows.go

Purpose: Windows path canonicalization that resolves symlink/final paths through Win32 handles.

Important APIs/types/functions: `openSymlink` and `CanonicalizeSystemPath`.

Control flow: opens the path with `CreateFile` and backup semantics, repeatedly calls `GetFinalPathNameByHandle` growing the UTF-16 buffer until it fits, then strips `\?\` and normalizes UNC output.

State and persistence: opens and closes a Windows file handle; no durable writes.

Dependencies and integration points: depends on `golang.org/x/sys/windows`; supplies the Windows implementation consumed by `ResolveSymlinks` and `CanonicalizePath`.

Risks: handle open flags are readless but still may fail on permissions; buffer sizing must remain correct for long paths; prefix stripping is Windows-specific and easy to regress.

Test signals: no direct file in this subset, but Windows path behavior is exercised by platform tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/filetools_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/humanize/humanize.go -->
# sources/sync-backup/git-lfs/tools/humanize/humanize.go

Purpose: parse and format byte sizes and byte rates for user-facing Git LFS progress/config output.

Important APIs/types/functions: constants `Byte` through `Pebibyte` and SI units, `ParseBytes`, `ParseByteUnit`, `FormatBytes`, `FormatBytesUnit`, `FormatByteRate`, and internal `log`.

Control flow: parsing scans the numeric prefix allowing digits, dot, and comma, parses it as float64, maps the suffix through `bytesTable`, multiplies, and rejects values at/above `math.MaxUint64`. Formatting chooses a base-1000 exponent, formats to one decimal for larger units, and rate formatting divides by duration with a one-nanosecond lower bound.

State and persistence: package-level unit tables only; no I/O or durable state.

Dependencies and integration points: used by `tq.Meter` for progress strings. Depends on `math`, `strconv`, `unicode`, Git LFS `errors` and `tr`.

Risks: parsing truncates fractional bytes when casting to `uint64`; rate formatting for zero duration intentionally clamps to nanosecond-scale and can produce very high rates; exponent indexes assume values remain within the defined `sizes` range.

Test signals: `humanize_test.go` covers many unit variants, rounding cases, unknown units, and byte-rate formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/humanize/humanize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/humanize/humanize_test.go -->
# sources/sync-backup/git-lfs/tools/humanize/humanize_test.go

Purpose: table-driven tests for byte parsing and formatting.

Important APIs/types/functions: test-case structs for parse/format operations and tests `TestParseBytes`, `TestFormatBytes`, `TestParseByteUnit`, `TestFormatBytesUnit`, and `TestFormateByteRate`.

Control flow: each test iterates named cases and delegates assertions to a case method. Cases cover IEC and SI suffixes, case-insensitivity, spaces, rounding under/over/exact values, unknown units, non-second durations, and zero-duration rates.

State and persistence: no I/O or persisted state.

Dependencies and integration points: imports the external `humanize` package path, so it validates exported API behavior rather than internals. Uses `testify/assert`.

Risks: expected values encode decimal rather than binary formatting; changes to rounding semantics will require broad fixture updates. The test name has a typo (`Formate`).

Test signals: strong coverage for supported units and presentation boundaries, limited overflow coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/humanize/humanize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/humanize/package.go -->
# sources/sync-backup/git-lfs/tools/humanize/package.go

Purpose: package documentation for `humanize`, stating that it parses and formats humanized numbers with units and is based on `github.com/dustin/go-humanize`.

Important APIs/types/functions: no executable API; declares package `humanize`.

Control flow: none.

State and persistence: none.

Dependencies and integration points: documentation appears in Go package docs and frames `humanize.go` behavior.

Risks: documentation can drift from implementation if unit support changes.

Test signals: not directly tested; package builds with the rest of `humanize`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/humanize/package.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/iotools.go -->
# sources/sync-backup/git-lfs/tools/iotools.go

Purpose: I/O helpers for copying with progress, LFS SHA-256 hashing, retriable read wrapping, stream spooling, and NUL-token scanning.

Important APIs/types/functions: `CopyWithCallback`, `NewLfsContentHash`, `HashingReader`, `NewHashingReader`, `NewHashingReaderPreloadHash`, `RetriableReader`, `NewRetriableReader`, `Spool`, and `SplitOnNul`.

Control flow: `CopyWithCallback` first attempts platform clone-file optimization, then falls back to `io.Copy` or a callback reader. `HashingReader.Read` writes successfully read bytes into its hasher. `RetriableReader` preserves nil/EOF/already-retriable errors and wraps other errors. `Spool` buffers 1 KiB in memory, spills the remainder to a temp file, rewinds, and copies combined data to the destination.

State and persistence: `HashingReader` accumulates hash state; `Spool` creates and removes temporary files; callbacks externalize progress state.

Dependencies and integration points: transfer adapters use copy, hashing, and retriable readers for uploads/downloads. Depends on Git LFS `errors`/`tr` and platform `CloneFile`.

Risks: `SplitOnNul` never emits a final unterminated token at EOF. `Spool` returns byte counts from different phases depending on where errors occur. Clone-file optimization bypasses actual byte copy and relies on callback correctness.

Test signals: `iotools_test.go` covers retriable reader behavior; `util_test.go` covers copy callback; transfer tests indirectly exercise hashing/copy paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/iotools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/iotools_test.go -->
# sources/sync-backup/git-lfs/tools/iotools_test.go

Purpose: tests `RetriableReader`.

Important APIs/types/functions: `TestRetriableReaderReturnsSuccessfulReads`, `TestRetriableReaderReturnsEOFs`, `TestRetriableReaderMakesErrorsRetriable`, `TestRetriableReaderDoesNotRewrap`, and helper `ErrReader`.

Control flow: wraps successful, EOF, plain-error, and already-retriable readers, then asserts returned bytes/errors.

State and persistence: none.

Dependencies and integration points: validates behavior expected by download code where network read errors should enter transfer retry handling.

Risks: does not cover partial reads with simultaneous data and error, nor `Spool`/`SplitOnNul`.

Test signals: good focused coverage of retry wrapping semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/iotools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/kv/keyvaluestore.go -->
# sources/sync-backup/git-lfs/tools/kv/keyvaluestore.go

Purpose: small gob-backed in-memory key/value store with optimistic merge-on-save persistence.

Important APIs/types/functions: `Store`, `NewStore`, `Set`, `Remove`, `RemoveAll`, `Visit`, `Get`, `Save`, `RegisterTypeForStorage`, internal `operation`, `change`, `loadAndMergeIfNeeded`, `loadAndMergeReaderIfNeeded`, and `reapplyChanges`.

Control flow: `NewStore` loads existing gob data when present. Mutations update the map and append to a change log. `Save` opens/creates the file, reloads if the on-disk version differs, replays pending changes onto the disk map, increments version, encodes version then map, truncates old content, and clears the log.

State and persistence: owns an in-memory map, version, change log, and filename; persists via gob. Uses an RW mutex for in-process access but no cross-process file lock despite optimistic conflict detection.

Dependencies and integration points: suitable for lightweight Git LFS metadata caches. Depends on Go `encoding/gob`, `os`, `sync`, Git LFS `errors` and `tr`. Custom stored structs must be registered with gob.

Risks: comment explicitly notes lost-update possibilities beyond read-committed style behavior. Gob schema/type compatibility matters. `Save` ignores the return error from `loadAndMergeReaderIfNeeded` in one path. Truncating before encode completion can leave a corrupt file on write failure.

Test signals: `keyvaluestore_test.go` covers basic types, custom struct registration, remove/remove-all, optimistic conflict merging, and file-size reduction after truncation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/kv/keyvaluestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/kv/keyvaluestore_test.go -->
# sources/sync-backup/git-lfs/tools/kv/keyvaluestore_test.go

Purpose: tests persistence and optimistic merge behavior of the gob key/value store.

Important APIs/types/functions: `TestStoreSimple`, `TestStoreOptimisticConflict`, and `TestStoreReduceSize`.

Control flow: tests create temp files, mutate stores, save/reload, and compare values. The conflict test creates two store instances, saves changes from the second, then saves pending changes from the first to verify merge/replay semantics.

State and persistence: writes actual gob data to temp files and checks reload behavior and file size shrinkage after truncation.

Dependencies and integration points: uses `testify/assert`; exercises public store API plus `RegisterTypeForStorage`.

Risks: does not simulate actual simultaneous writes or corrupt files; conflict expectations document last-writer behavior for overlapping keys.

Test signals: strong coverage of normal persistence and intended optimistic conflict path.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/kv/keyvaluestore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/math.go -->
# sources/sync-backup/git-lfs/tools/math.go

Purpose: tiny integer clamp helper.

Important APIs/types/functions: `ClampInt(n, low, high int) int`.

Control flow: returns `min(high, max(low, n))`.

State and persistence: none.

Dependencies and integration points: generic helper for callers needing bounded integer config values.

Risks: assumes `low <= high`; reversed bounds collapse to `high` after nested min/max semantics.

Test signals: `math_test.go` covers below, above, and inside bounds.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/math.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/math_test.go -->
# sources/sync-backup/git-lfs/tools/math_test.go

Purpose: tests `ClampInt`.

Important APIs/types/functions: `TestClampDiscardsIntsLowerThanMin`, `TestClampDiscardsIntsGreaterThanMax`, and `TestClampAcceptsIntsWithinBounds`.

Control flow: direct assertions for representative boundary behavior.

State and persistence: none.

Dependencies and integration points: uses `testify/assert`.

Risks: no test for reversed bounds or exact low/high endpoints separately.

Test signals: adequate coverage for intended normal use.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/math_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/ordered_set.go -->
# sources/sync-backup/git-lfs/tools/ordered_set.go

Purpose: insertion-ordered unique string set.

Important APIs/types/functions: `OrderedSet`, constructors, `Add`, `Contains`, `ContainsAll`, `IsSubset`, `IsSuperset`, `Union`, `Intersect`, `Difference`, `SymmetricDifference`, `Clear`, `Remove`, `Cardinality`, `Iter`, `Equal`, and `Clone`.

Control flow: maintains slice order plus map from value to index. Set operations build new ordered sets, preserving receiver order where relevant. `Iter` launches a goroutine to emit elements.

State and persistence: in-memory slice/map only; not concurrency-safe.

Dependencies and integration points: internal utility for deterministic ordered membership. Uses built-in `min`.

Risks: `Remove` has subtle index/slice math and must keep map indexes synchronized. `Iter` can leak a goroutine if the caller does not drain the channel. `Equal` compares index maps, so order matters.

Test signals: `ordered_set_test.go` covers all major operations, ordering, equality, and cloning.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/ordered_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/ordered_set_test.go -->
# sources/sync-backup/git-lfs/tools/ordered_set_test.go

Purpose: tests ordered-set behavior and ordering guarantees.

Important APIs/types/functions: tests for add/contains, subset/superset, union/intersection/difference/symmetric difference, clear/remove/cardinality/iter/equal/clone.

Control flow: builds sets from slices and drains `Iter` channels into slices for order assertions.

State and persistence: none beyond in-memory sets.

Dependencies and integration points: uses `testify/assert` and `require`.

Risks: no concurrency tests, which is consistent with the type not advertising concurrency safety.

Test signals: broad coverage of normal ordered-set behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/ordered_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/os_tools.go -->
# sources/sync-backup/git-lfs/tools/os_tools.go

Purpose: working-directory and Cygwin path translation helpers.

Important APIs/types/functions: `Getwd`, `translateCygwinPath`, and `TranslateCygwinPath`.

Control flow: `Getwd` calls `os.Getwd`, then translates through `cygpath -w` when running under Cygwin. Translation uses `subprocess.ExecCommand`, forces `LC_ALL=C.UTF-8`, captures stderr, tolerates missing `cygpath`, and wraps real conversion failures.

State and persistence: no durable state; invokes a subprocess and reads environment.

Dependencies and integration points: used by path canonicalization flows in `filetools.go`; relies on `isCygwin` from another platform file and Git LFS `subprocess`, `tr`, and pkg/errors.

Risks: external `cygpath` behavior and locale availability affect output. Missing executable is silently tolerated, which is intentional but can mask misconfigured Cygwin environments.

Test signals: not directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/os_tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/robustio.go -->
# sources/sync-backup/git-lfs/tools/robustio.go

Purpose: non-Windows wrappers for rename/open/remove.

Important APIs/types/functions: `RobustRename`, `RobustOpen`, and `RobustRemove`.

Control flow: direct delegation to `os.Rename`, `os.Open`, and `os.Remove`.

State and persistence: performs the requested filesystem operation; no retries or extra state on non-Windows.

Dependencies and integration points: called by file replacement and transfer resume cleanup paths; Windows file supplies retry behavior.

Risks: inherits platform `os` semantics with no retry on transient errors.

Test signals: indirectly exercised by file/transfer tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/robustio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/robustio_windows.go -->
# sources/sync-backup/git-lfs/tools/robustio_windows.go

Purpose: Windows retrying wrappers for filesystem operations affected by sharing/access races.

Important APIs/types/functions: `isEphemeralError`, `isFileInUseError`, `robustRemoveRetryDelaysMs`, `RobustRename`, `RobustOpen`, and `RobustRemove`.

Control flow: uses `retry.Do`; rename/open retry sharing violations, remove retries sharing violation and access denied with Git-like millisecond delay pattern.

State and persistence: performs actual filesystem operations; local `result` stores opened file across retry closure.

Dependencies and integration points: used by file replacement and download resume code to tolerate Windows file locking. Depends on `github.com/avast/retry-go` and `x/sys/windows`.

Risks: retry windows are short; persistent antivirus/indexer locks still fail. `RobustOpen` assigns `result` even when an error occurs, so callers rely on final returned error.

Test signals: no direct Windows robustio test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/robustio_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/str_tools.go -->
# sources/sync-backup/git-lfs/tools/str_tools.go

Purpose: string parsing and formatting helpers.

Important APIs/types/functions: `QuotedFields`, `Ljust`, `Rjust`, `Longest`, `Indent`, and `Undent`.

Control flow: `QuotedFields` uses a regexp to extract single-quoted, double-quoted, or non-space tokens. Justification copies the input slice and pads to the byte length of the longest string. `Indent` prepends tabs line-wise; `Undent` removes leading spaces/tabs at line starts.

State and persistence: package regexes only; no I/O.

Dependencies and integration points: useful for command/config parsing and formatted CLI output.

Risks: length calculations are byte-based, not display-width or rune-width based. Quote parsing is regexp-greedy and does not implement shell escaping. `Undent` removes all leading spaces/tabs, not just common indentation.

Test signals: `str_tools_test.go` covers quote variants, nested/mixed quotes, justification, indentation, and linebreak preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/str_tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/str_tools_test.go -->
# sources/sync-backup/git-lfs/tools/str_tools_test.go

Purpose: unit tests for string helper behavior.

Important APIs/types/functions: `QuotedFieldsTestCase`, `TestQuotedFields`, tests for `Longest`, `Rjust`, `Ljust`, `Indent`, and `Undent`.

Control flow: table-driven quote tests exercise leading/trailing whitespace, empty quoted fields, nested quote characters, and mixed quotes; remaining tests assert exact string outputs.

State and persistence: none.

Dependencies and integration points: uses `testify/assert`.

Risks: expected behavior documents a non-shell parser; future changes toward shell semantics would break many cases.

Test signals: good coverage for intended simple parsing/formatting semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/str_tools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/stringset.go -->
# sources/sync-backup/git-lfs/tools/stringset.go

Purpose: unordered string set implementation generated from a generic set template.

Important APIs/types/functions: `StringSet` map type, constructors, `Add`, `Contains`, `ContainsAll`, `IsSubset`, `IsSuperset`, `Union`, `Intersect`, `Difference`, `SymmetricDifference`, `Clear`, `Remove`, `Cardinality`, `Iter`, `Equal`, and `Clone`.

Control flow: map membership backs all operations; set algebra allocates new maps; `Iter` launches a goroutine over map keys.

State and persistence: in-memory map; not concurrency-safe and iteration order is random.

Dependencies and integration points: general utility for membership tests where order does not matter.

Risks: `Iter` order is nondeterministic and can leak if not drained. `ContainsAll` allocates a temporary set unnecessarily.

Test signals: no specific stringset test listed in this subset, but behavior mirrors ordered-set tests conceptually.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/stringset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/sync_writer.go -->
# sources/sync-backup/git-lfs/tools/sync_writer.go

Purpose: wrapper that synchronizes writes when the underlying writer supports `Sync`, and closes when it supports `io.Closer`.

Important APIs/types/functions: `SyncWriter`, `NewSyncWriter`, `Write`, and `Close`.

Control flow: constructor detects optional `Sync()` and `Close()` methods and installs no-op fallbacks. `Write` delegates to the wrapped writer and calls sync only on successful write.

State and persistence: holds function pointers for optional behavior; can force data flushes for file-backed progress logs.

Dependencies and integration points: used by `tq.Meter` for `GIT_LFS_PROGRESS` logging.

Risks: `Write` discards the byte count and cannot report short writes unless the underlying writer returns an error. Sync after every write can be expensive.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/sync_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/time_tools.go -->
# sources/sync-backup/git-lfs/tools/time_tools.go

Purpose: helpers for handling absolute and relative expiration times.

Important APIs/types/functions: `IsExpiredAtOrIn` and `TimeAtOrIn`.

Control flow: `TimeAtOrIn` prefers a relative duration when non-zero, otherwise returns an absolute time. `IsExpiredAtOrIn` computes expiration and compares it to `time.Now().Add(until)`, treating zero time as non-expiring.

State and persistence: no persistent state; uses wall-clock time.

Dependencies and integration points: `tq.Action.IsExpiredWithin` uses this to decide whether transfer actions should be retried before expiry.

Risks: wall-clock dependency can make boundary behavior time-sensitive; when both `at` and `in` are provided, `in` wins.

Test signals: `time_tools_test.go` covers absolute, relative, zero, expired, and ambiguous cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/time_tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/time_tools_test.go -->
# sources/sync-backup/git-lfs/tools/time_tools_test.go

Purpose: tests expiration helper precedence and boundary behavior.

Important APIs/types/functions: tests for `TimeAtOrIn` and `IsExpiredAtOrIn`.

Control flow: constructs `now`, absolute `at`, and relative `in` combinations, then asserts chosen expiration and expired boolean.

State and persistence: no I/O; uses current wall-clock time in test setup.

Dependencies and integration points: validates transfer action expiry behavior indirectly.

Risks: comparisons are exact for values derived from the same `now`, but tests involving `time.Now()` inside implementation could be sensitive near boundaries.

Test signals: good coverage of intended precedence, especially relative duration winning over absolute time.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/time_tools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/umask_nix.go -->
# sources/sync-backup/git-lfs/tools/umask_nix.go

Purpose: Unix implementation for running a function under a temporary umask.

Important APIs/types/functions: `doWithUmask(mask int, f func() error) error`.

Control flow: sets the process umask, defers restoration of the previous mask, and invokes the callback.

State and persistence: mutates process-global umask during callback execution.

Dependencies and integration points: used by `Mkdir`/`MkdirAll` to honor repository permissions.

Risks: umask is process-global, so concurrent file creation in other goroutines during the callback can observe the temporary mask.

Test signals: indirectly covered by directory-permission behavior where platform allows.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/umask_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/umask_windows.go -->
# sources/sync-backup/git-lfs/tools/umask_windows.go

Purpose: Windows no-op implementation of temporary umask wrapper.

Important APIs/types/functions: `doWithUmask`.

Control flow: immediately calls the supplied function.

State and persistence: no umask state on Windows.

Dependencies and integration points: lets shared `Mkdir`/`MkdirAll` compile cross-platform.

Risks: Windows permissions do not mirror Unix umask semantics.

Test signals: write-flag tests include Windows-specific expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/umask_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_darwin.go -->
# sources/sync-backup/git-lfs/tools/util_darwin.go

Purpose: macOS clonefile support for efficient copy-on-write file duplication.

Important APIs/types/functions: `cloneFileSupported`, `checkCloneFileSupported`, `CheckCloneFileSupported`, `CloneFileError`, `CloneFile`, `CloneFileByPath`, and `cloneFileSyscall`.

Control flow: init checks OS release major version; support test creates temp src/dst and calls path-based clone; path clone removes existing destination then invokes `unix.Clonefileat` with `CLONE_NOFOLLOW`. Generic writer/reader clone is unsupported on Darwin.

State and persistence: package global caches OS support; test functions create/remove temp files; path clone creates/replaces destination.

Dependencies and integration points: `CopyWithCallback` can use clone support via platform functions; Darwin only supports by path here.

Risks: filesystem-level support can differ from OS version, so syscall can still return unsupported. Existing destination is removed before clone. Error string in test expectations may drift from implementation wording.

Test signals: Darwin tests cover support probing, unsupported generic clone, and path clone content equality when available.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_darwin_test.go -->
# sources/sync-backup/git-lfs/tools/util_darwin_test.go

Purpose: macOS-specific tests for clonefile helpers.

Important APIs/types/functions: `TestCheckCloneFileSupported`, `TestCloneFile`, and `TestCloneFileByPath`.

Control flow: probes temp dir support, asserts generic `CloneFile` is unsupported without error, and clones a written temp source to a destination when platform/filesystem supports it.

State and persistence: writes temp files in `os.TempDir`; skips when clonefile is unsupported.

Dependencies and integration points: validates Darwin implementation used by copy optimization.

Risks: platform and filesystem dependent; temp file names are fixed (`src`, `dst`) and could collide in unusual concurrent runs.

Test signals: direct coverage of Darwin clone behavior, with skip paths for unsupported environments.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_generic.go -->
# sources/sync-backup/git-lfs/tools/util_generic.go

Purpose: fallback clone-file implementation for platforms other than Linux, Darwin, and Windows.

Important APIs/types/functions: `CheckCloneFileSupported`, `CloneFile`, and `CloneFileByPath`.

Control flow: reports unsupported platform for probing; clone attempts return `(false, nil)`.

State and persistence: none.

Dependencies and integration points: preserves cross-platform API for `CopyWithCallback`.

Risks: callers must correctly fall back to byte copy when clone returns false.

Test signals: `util_test.go` checks these methods exist on all platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_generic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_linux.go -->
# sources/sync-backup/git-lfs/tools/util_linux.go

Purpose: Linux reflink/copy-on-write clone support via `FICLONE` ioctl.

Important APIs/types/functions: `CheckCloneFileSupported`, `CloneFile`, and `CloneFileByPath`.

Control flow: support probe creates temp src/dst and calls `CloneFile`. `CloneFile` succeeds only when both arguments are `*os.File`, then calls `unix.IoctlFileClone`. Path clone opens source, creates/truncates destination, and delegates.

State and persistence: creates/removes probe temp files and writes/truncates destination for path clone.

Dependencies and integration points: used by `CopyWithCallback` to avoid byte copying when filesystem supports reflinks.

Risks: filesystem support varies; ioctl errors are returned to caller, which may affect fallback behavior depending on caller path. Path clone truncates destination.

Test signals: common `TestMethodExists`; no Linux-specific success test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_test.go -->
# sources/sync-backup/git-lfs/tools/util_test.go

Purpose: common tests for copy callback and cross-platform clone helper availability.

Important APIs/types/functions: `TestCopyWithCallback` and `TestMethodExists`.

Control flow: copies a short buffer to discard with a callback and asserts one progress event; calls clone-support functions to ensure platform APIs are present.

State and persistence: no durable state; `CheckCloneFileSupported` may create temp files depending on platform.

Dependencies and integration points: validates `CopyWithCallback` behavior used by transfer adapters.

Risks: callback-count expectation depends on current buffer/copy behavior and clone optimization not firing for a bytes buffer.

Test signals: lightweight smoke coverage for core copy path.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_windows.go -->
# sources/sync-backup/git-lfs/tools/util_windows.go

Purpose: Windows block cloning support using `FSCTL_DUPLICATE_EXTENTS_TO_FILE`.

Important APIs/types/functions: `availableClusterSize`, `GiB`, `fsctlDuplicateExtentsToFile`, `duplicateExtentsData`, `CheckCloneFileSupported`, `CloneFileByPath`, `CloneFile`, `callDuplicateExtentsToFile`, and `roundUp`.

Control flow: probe writes non-empty temp source and clones to temp destination. `CloneFile` requires `*os.File`, truncates destination to source size, clones full GiB chunks, then clones the tail rounded to 64 KiB or 4 KiB cluster sizes.

State and persistence: mutates destination size and extents; creates/removes temp probe files.

Dependencies and integration points: called by `CopyWithCallback` on Windows for ReFS block clone support. Depends on `x/sys/windows` and unsafe IOCTL calls.

Risks: destination is not opened with truncation in `CloneFileByPath` but `CloneFile` truncates to source size. Filesystem cluster requirements are handled by retrying two sizes, but unsupported filesystems return errors. Large-file loop and rounding must avoid overflow.

Test signals: Windows tests cover clone correctness over many sizes when `REFS_TEST_DIR` or current directory supports cloning.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_windows_test.go -->
# sources/sync-backup/git-lfs/tools/util_windows_test.go

Purpose: Windows-specific block clone tests.

Important APIs/types/functions: `TestCloneFile` and helper `fillFile`.

Control flow: chooses `REFS_TEST_DIR` or current working directory, skips if clone support probe fails, then writes deterministic content at several sizes, clones, hashes destination, and compares hashes.

State and persistence: creates temp files in the selected test directory and writes/truncates content.

Dependencies and integration points: validates Windows optimization used by `CopyWithCallback`.

Risks: requires ReFS/block-clone-capable filesystem to run; temp files are not explicitly removed in the shown test body.

Test signals: strong size-boundary coverage when environment supports the feature.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/util_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/adapterbase.go -->
# sources/sync-backup/git-lfs/tq/adapterbase.go

Purpose: shared worker-pool implementation for transfer adapters.

Important APIs/types/functions: `adapterBase`, `transferImplementation`, `newAdapterBase`, `Begin`, `Add`, `End`, `worker`, `newHTTPRequest`, `doHTTP`, `advanceCallbackProgress`, and `endpointURL`.

Control flow: `Begin` configures API client, remote, job channel, debug flags, starts N workers, and uses `authWait` so worker 0 prompts/authenticates before other workers proceed. `Add` sends jobs and closes a result channel after all are done. Workers validate size, call implementation `DoTransfer`, and emit `TransferResult`. HTTP helpers build action requests, optionally rewrite hrefs, attach headers, and choose authenticated/no-retry auth paths.

State and persistence: per-adapter job channel, wait groups, auth gate, callback, and API client state; no durable persistence.

Dependencies and integration points: embedded by basic, tus, SSH, and custom adapters; depends on `fs`, `lfsapi`, `errors`, `tr`, and `tracerx`.

Risks: `Begin` can return after some workers have already started if a later `WorkerStarting` fails. `Add` goroutine can block if `End`/worker lifecycle is misused. Auth gate correctness depends on implementations invoking `authOkFunc`.

Test signals: no direct adapterbase tests; behavior is indirectly covered through adapter/queue tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/adapterbase.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/api.go -->
# sources/sync-backup/git-lfs/tq/api.go

Purpose: Git LFS batch API request/response types and HTTP client adapter.

Important APIs/types/functions: `tqClient`, `batchRef`, `batchRequest`, `BatchResponse`, `Batch`, `BatchClient`, and `tqClient.Batch`.

Control flow: `Batch` upgrades the manifest and sends operation, objects, adapter names, ref, and hash algorithm. `tqClient.Batch` omits `transfers` when only basic is requested, builds a POST to `objects/batch`, executes with auth/retries, decodes JSON, rejects unsupported hash algorithms, checks HTTP 200, and timestamps action creation times.

State and persistence: stores max retry count on `tqClient`; no durable state.

Dependencies and integration points: called by `TransferQueue`; schema tests validate request/response JSON. Integrates with `lfsapi.Client`, `lfshttp.Endpoint`, and remote refs.

Risks: `Batch` calls `remoteRef.Refspec()` without a nil guard. Non-200 responses are checked after JSON decode, so malformed error bodies surface as decode errors first.

Test signals: `api_test.go` covers normal request/response, basic-only transfer omission, empty object short-circuit, and JSON schema validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/api_test.go -->
# sources/sync-backup/git-lfs/tq/api_test.go

Purpose: tests HTTP batch API encoding/decoding and schema conformance.

Important APIs/types/functions: `TestAPIBatch`, `TestAPIBatchOnlyBasic`, `TestAPIBatchEmptyObjects`, schema globals, `sourcedSchema`, `getSchema`, and `assertSchema`.

Control flow: starts `httptest` servers, validates incoming JSON against request schema, emits schema-valid responses, and checks client results. The init function loads schema files from `schemas/`.

State and persistence: no durable state; creates local test servers and reads schema files.

Dependencies and integration points: uses `gojsonschema`, `lfsapi`, and `lfshttp`; ties tests to `http-batch-*.json`.

Risks: content-length assertion in one test is sensitive to JSON encoding changes. Schema loading failures print rather than fail until tests require non-nil schema.

Test signals: good coverage for request transfer-list behavior and schema contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/basic_download.go -->
# sources/sync-backup/git-lfs/tq/basic_download.go

Purpose: basic HTTP download adapter with resume support, hash verification, optional zstd decompression, and atomic-ish rename into place.

Important APIs/types/functions: `basicDownloadAdapter`, worker context with zstd decoder, `tempDir`, `DoTransfer`, `downloadFilename`, `download`, `configureBasicDownloadAdapter`, and `makeRequest`.

Control flow: reserves a temp file, moves any `.part` resume file into it, hashes existing bytes, validates resume range, issues GET/Range request, handles network/416/429 retry cases, validates 206 Content-Range for resumes, optionally decodes zstd, copies through a hashing reader with progress callbacks, compares SHA/OID, closes, and renames to final path.

State and persistence: uses `$LFSStorageDir/incomplete`, `.part` files for resume, temp files for in-progress data, and per-worker zstd decoder.

Dependencies and integration points: registered as `basic` download adapter in the manifest; uses `tools.TempFile`, `RobustRename`, `HashingReader`, `RetriableReader`, `CopyWithCallback`, and `RenameFileCopyPermissions`.

Risks: resume correctness depends on server Content-Range compliance. Existing final file from another process is treated as success after rename failure check. Zstd decoder reuse is per worker and must be closed. Hash mismatch discards partial via deferred cleanup unless moved to `.part` earlier.

Test signals: no dedicated basic-download tests in this subset; queue and transfer integration exercise adapter selection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/basic_download.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/basic_upload.go -->
# sources/sync-backup/git-lfs/tq/basic_upload.go

Purpose: basic HTTP PUT upload adapter with content-type detection, progress callbacks, retry wrapping, and optional verify action.

Important APIs/types/functions: `BasicAdapterName`, `defaultContentType`, `basicUploadAdapter`, `DoTransfer`, `setContentTypeFor`, `startCallbackReader`, `newStartCallbackReader`, `configureBasicUploadAdapter`, and `makeRequest`.

Control flow: obtains upload action, builds PUT request, sets content length unless chunked, opens local file, detects content type unless disabled, wraps body with progress callback and auth-start callback, executes request, maps network/429/403 errors to retriable variants, validates status, drains response body, and calls `verifyUpload`.

State and persistence: reads local object file; no durable writes. Progress body can reset progress on retry.

Dependencies and integration points: registered as `basic` upload adapter; used by `TransferQueue`. Depends on `lfsapi`, `tools.NewFileBodyWithCallback`, URL config, and verify logic.

Risks: recursive auth retry reopens the file and assumes open succeeds (`f, _`). Content-type detection rewinds the file and can fail. HTTP 422 is deliberately non-retriable to trigger content-type guidance.

Test signals: upload behavior is not directly tested here; verify action has separate tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/basic_upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/custom.go -->
# sources/sync-backup/git-lfs/tq/custom.go

Purpose: custom transfer adapter implementation for external line-oriented JSON transfer processes, including standalone file agent support.

Important APIs/types/functions: `customAdapter`, `traceWriter`, worker context, init/transfer/terminate request structs, response struct, constructors, `Begin`, `WorkerStarting`, message exchange helpers, shutdown/abort, `DoTransfer`, `newCustomAdapter`, `configureDefaultCustomAdapters`, `configureCustomAdapters`, and `customAdapterConfig`.

Control flow: `Begin` limits concurrency when adapter config says non-concurrent. Each worker starts an external command, wires stdin/stdout/stderr, sends `init`, and then each transfer sends upload/download JSON and reads progress or complete messages until done. Download completions verify hash and move file; upload completions run verify. Worker shutdown sends terminate and waits up to 30 seconds before killing.

State and persistence: owns subprocesses, pipes, buffered readers, trace buffers, and optional downloaded temp paths returned by the custom adapter.

Dependencies and integration points: custom adapters are registered from Git config keys `lfs.customtransfer.<name>.*`; manifest may use them as standalone transfer agents. Depends on `subprocess`, `tools.VerifyFileHash`, and `RenameFileCopyPermissions`.

Risks: protocol is strict: unexpected OIDs/events fail transfers. External process hangs are bounded only during shutdown, not during normal response reads. Stderr is logged to tracer; sensitive output could leak in trace. Shell formatting/path args require careful quoting.

Test signals: `custom_test.go` covers config registration, direction filtering, args, and concurrency flags, but not subprocess protocol execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/custom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/custom_test.go -->
# sources/sync-backup/git-lfs/tq/custom_test.go

Purpose: tests manifest registration of custom transfer adapters from Git config.

Important APIs/types/functions: `TestCustomTransferBasicConfig`, `TestCustomTransferDownloadConfig`, `TestCustomTransferUploadConfig`, and `TestCustomTransferBothConfig`.

Control flow: builds `lfsapi.Client` with config maps, creates a manifest, requests upload/download adapters, and asserts whether they are `*customAdapter` plus path/args/concurrent fields.

State and persistence: no durable state; client is closed after each test.

Dependencies and integration points: validates `configureCustomAdapters` and manifest adapter lookup behavior.

Risks: tests do not execute external adapter processes or standalone mode. One assertion assigns `cd, _ := u.(*customAdapter)` in the basic download block, which appears to inspect `u` rather than `d`.

Test signals: useful config coverage for direction and defaults.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/custom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/errors.go -->
# sources/sync-backup/git-lfs/tq/errors.go

Purpose: typed errors for missing or corrupt local LFS objects.

Important APIs/types/functions: `MalformedObjectError`, `newObjectMissingError`, `newCorruptObjectError`, `Missing`, `Corrupt`, and `Error`.

Control flow: constructors set `missing`; methods expose missing/corrupt classification and format translated messages.

State and persistence: immutable error values only.

Dependencies and integration points: `TransferQueue.partitionTransfers` and upload batch checks use these errors for missing/corrupt upload objects.

Risks: type assertions are needed to inspect classification; both constructors return `error`, hiding concrete type unless asserted.

Test signals: `errors_test.go` verifies fields and classification methods.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/errors_test.go -->
# sources/sync-backup/git-lfs/tq/errors_test.go

Purpose: tests `MalformedObjectError` classification.

Important APIs/types/functions: `TestMissingObjectErrorsAreRecognizable` and `TestCorruptObjectErrorsAreRecognizable`.

Control flow: creates errors via constructors, type asserts to `*MalformedObjectError`, and checks name/OID plus `Missing` or `Corrupt`.

State and persistence: none.

Dependencies and integration points: validates upload preflight error semantics.

Risks: does not assert formatted `Error()` strings.

Test signals: focused coverage for type fields/classification.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/manifest.go -->
# sources/sync-backup/git-lfs/tq/manifest.go

Purpose: transfer adapter registry and transfer configuration manifest, lazily constructed from Git/LFS configuration.

Important APIs/types/functions: `Manifest`, `lazyManifest`, `concreteManifest`, `NewManifest`, `newConcreteManifest`, retry/concurrency getters, adapter-name getters, `RegisterNewAdapterFunc`, `NewAdapterOrDefault`, `NewAdapter`, `findStandaloneTransfer`, and `Env`.

Control flow: lazy manifest serializes first upgrade. Concrete construction reads retry, retry delay, concurrency, basic-only, standalone, TUS, and custom adapter config; configures SSH batch client when SSH transfer exists; registers basic, optional tus, SSH, and custom adapters; validates standalone custom agent. Adapter lookup falls back to basic when requested adapter is missing.

State and persistence: holds adapter factory maps, custom flags, config values, API client, filesystem, SSH transfer, and batch client; all in memory.

Dependencies and integration points: central dependency for `TransferQueue`, `Batch`, and all adapter registration functions. Integrates with `lfsapi.Client`, Git config, URL config, SSH transfer, and `lfshttp.DefaultConcurrentTransfers`.

Risks: adapter-name order is map iteration order unless basic-only. SSH without multiplexing forces concurrency to 1. Custom/standard name conflicts print warnings. Lazy upgrade must remain race-safe.

Test signals: `manifest_test.go` covers configurable/default retry behavior and concurrent upgrade; `transfer_test.go` covers adapter registration/fallback/basic-only behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/manifest_test.go -->
# sources/sync-backup/git-lfs/tq/manifest_test.go

Purpose: tests manifest configuration defaults and lazy upgrade race safety.

Important APIs/types/functions: `TestManifestIsConfigurable`, `TestManifestClampsValidValues`, `TestLazyManifestConcurrentUpgrade`, and `TestManifestIgnoresNonInts`.

Control flow: builds clients with config maps, creates manifests, asserts retry values, and starts two goroutines that call `Upgrade` concurrently to ensure the same concrete instance is returned.

State and persistence: no durable state; in-memory clients/manifests.

Dependencies and integration points: uses `lfsapi`, `lfshttp`, `sync`, and `testify/assert`.

Risks: concurrency test only checks two goroutines and identity, not race detector output by itself.

Test signals: good coverage of retry config validation and lazy manifest locking.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/meter.go -->
# sources/sync-backup/git-lfs/tq/meter.go

Purpose: progress meter for transfer queues, including tasklog updates and optional `GIT_LFS_PROGRESS` file logging.

Important APIs/types/functions: `Meter`, `LoggerFromEnv`, `LoggerToFile`, `NewMeter`, `Start`, `Pause`, `Add`, `Skip`, `StartTransfer`, `TransferBytes`, `FinishTransfer`, `Flush`, `Finish`, `Updates`, `Throttled`, `str`, `clamp`, `clampf`, and `logBytes`.

Control flow: transfer queue calls `Add`/`Skip`/`StartTransfer`/`TransferBytes`/`FinishTransfer`; each triggers `update` unless dry-run, paused, or no estimated files. `TransferBytes` updates byte totals and rolling average once per second. File logging writes direction, file index, counts, bytes, and name through `SyncWriter`.

State and persistence: atomic counters, average sample state, file-index map with mutex, updates channel, optional sync logger file.

Dependencies and integration points: used by `TransferQueue` and adapters for CLI progress; uses `tools/humanize`, `tasklog`, and config for progress-log directory creation.

Risks: `update` sends on an unbuffered channel and can block if no consumer is reading. `str` reads atomic fields directly in places rather than all via atomic loads. Logger disables itself on write error.

Test signals: no direct meter tests in this subset; progress behavior is indirectly exercised by queue/adapter flows.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/meter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/schemas/http-batch-request-schema.json -->
# sources/sync-backup/git-lfs/tq/schemas/http-batch-request-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS batch API requests.

Important APIs/types/functions: schema fields `transfers`, `operation`, and `objects`; object entries require `oid` and nonnegative numeric `size`, with optional `authenticated`.

Control flow: not executable; consumed by tests through gojsonschema.

State and persistence: static schema file.

Dependencies and integration points: `api_test.go` validates generated `batchRequest` JSON against this schema.

Risks: schema omits newer fields present in Go structs such as `ref` and `hash_algo`, so additional request properties at top level are not rejected because top-level `additionalProperties` is not false.

Test signals: loaded by `TestAPIBatch` and `TestAPIBatchOnlyBasic`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/schemas/http-batch-request-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/schemas/http-batch-response-schema.json -->
# sources/sync-backup/git-lfs/tq/schemas/http-batch-response-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS batch API responses.

Important APIs/types/functions: defines action objects with `href`, headers, expiration fields; response fields `transfer`, `objects`, error object, `message`, `request_id`, and `documentation_url`; each object requires `oid` and nonnegative `size`.

Control flow: static validation schema only.

State and persistence: static file.

Dependencies and integration points: used by `api_test.go` to validate test server responses.

Risks: action `additionalProperties: false` means extensions to action payloads require schema updates. Top-level response allows additional fields unless constrained elsewhere.

Test signals: loaded by API schema tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/schemas/http-batch-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/ssh.go -->
# sources/sync-backup/git-lfs/tq/ssh.go

Purpose: SSH batch client and SSH transfer adapter for Git LFS object transfers over SSH multiplexed connections.

Important APIs/types/functions: `SSHAdapterName`, `SSHBatchClient`, `Batch`, `batchInternal`, `SSHAdapter`, `WorkerStarting`, `DoTransfer`, `download`, `doDownload`, `upload`, `doUpload`, `verifyUpload`, `argumentsForTransfer`, `Begin`, `Trace`, and `configureSSHAdapter`.

Control flow: batch requests send OID/size lines over SSH, parse status/args/lines into `BatchResponse` and actions. Adapter workers reserve SSH connections by worker number. Downloads issue `get-object`, validate status and size arg, copy data through hashing reader, verify OID, and rename into place. Uploads send `put-object` with data and verify with `verify-object`, mapping 403/429 to retriable errors.

State and persistence: uses SSH connection locks, temp files under incomplete storage for downloads, and local object files for uploads.

Dependencies and integration points: manifest swaps batch client to `SSHBatchClient` when API client has SSH transfer; adapter registered for upload/download. Uses `tools` copy/hash/temp helpers and `ssh.SSHTransfer`.

Risks: line parsing sorts server response lines and groups by OID; malformed lines fail the whole batch. Connection locking serializes per connection. Missing SSH transfer causes worker startup failure.

Test signals: `ssh_test.go` covers nil transfer startup error; broader SSH protocol paths are not tested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/ssh_test.go -->
# sources/sync-backup/git-lfs/tq/ssh_test.go

Purpose: minimal SSH adapter startup error test.

Important APIs/types/functions: `TestSSHAdapterWorkerStartingNilTransfer`.

Control flow: constructs an `SSHAdapter` with nil transfer and asserts `WorkerStarting` returns an error mentioning the SSH transfer adapter.

State and persistence: none.

Dependencies and integration points: validates defensive behavior used before SSH worker goroutines process jobs.

Risks: does not cover SSH batch parsing or upload/download behavior.

Test signals: narrow but useful guard for nil dependency handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/ssh_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer.go -->
# sources/sync-backup/git-lfs/tq/transfer.go

Purpose: core transfer domain types and adapter interfaces.

Important APIs/types/functions: `Direction` with `Upload`, `Download`, `Checkout`; `Progress`/`String`; `Transfer`; `Rel`; `ObjectError`; `newTransfer`; `Action`; `IsExpiredWithin`; `ActionSet.Get`; `ActionExpiredErr`; `IsActionExpiredError`; `NewAdapterFunc`; `ProgressCallback`; `AdapterConfig`; `Adapter`; and `TransferResult`.

Control flow: `Transfer.Rel` checks actions then links for a relation and returns nil if absent. `ActionSet.Get` rejects actions expiring within five seconds by returning a retriable `ActionExpiredErr`. `newTransfer` deep-copies transfer metadata/actions for queue processing.

State and persistence: pure in-memory API types mirroring JSON batch data plus local-only fields (`Path`, `Missing`, action creation time).

Dependencies and integration points: used by all transfer queue and adapter code; integrates with `lfsapi.Client`, `tools` time helpers, and translated messages.

Risks: `IsActionExpiredError` only matches `*ActionExpiredErr`, while `ActionSet.Get` constructs `&ActionExpiredErr` wrapped in retriable error; callers usually use generic retriable checks. Action expiry depends on `createdAt` being set by batch clients.

Test signals: `transfer_test.go` focuses on adapter registration via manifest, not these data methods directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer_queue.go -->
# sources/sync-backup/git-lfs/tq/transfer_queue.go

Purpose: orchestration engine for batched Git LFS uploads/downloads, including API calls, adapter selection, duplicate-OID coalescing, progress, retries, delayed retries, watcher notifications, and error collection.

Important APIs/types/functions: `retryCounter`, `batch`, `abortableWaitGroup`, `TransferQueue`, `objects`, `objectTuple`, options (`DryRun`, `WithProgress`, `RemoteRef`, `WithProgressCallback`, `WithBatchSize`, `WithBufferDepth`), `NewTransferQueue`, `Upgrade`, `Add`, `remember`, `collectBatches`, `enqueueAndCollectRetriesFor`, `addToAdapter`, `partitionTransfers`, `handleTransferResult`, `useAdapter`, `ensureAdapterBegun`, `Wait`, `Watch`, retry helpers, and `Errors`.

Control flow: construction starts error and batch collector goroutines. `Add` upgrades manifest, records unique OIDs, sends only first object per OID to the incoming channel, and immediately notifies watchers for duplicates already completed. Collector fills batches, sorts largest first, calls batch API or standalone adapter, validates upload object presence, selects adapter, sends transfers, gathers retryable failures, and merges retries ahead of newly collected items. `Wait` closes incoming, waits for unique OIDs, stops adapter, closes watchers/error channel, flushes meter, and prints content-type advice after HTTP 422 upload failures.

State and persistence: in-memory queues/channels, transfer map guarded by mutex, retry counts, wait groups, adapter lifecycle state, unsupported-content-type flag, errors slice, and meter counters. No durable persistence, but adapters perform file/network side effects.

Dependencies and integration points: central user of `Manifest`, `Batch`, adapters, `Meter`, Git refs, `lfshttp` endpoints, Git LFS errors, and tools callbacks.

Risks: watcher slice is not guarded separately, so callers should set watchers before active concurrent use. Error collector appends without locking but runs single goroutine and is joined before final reads. Serious non-retriable batch errors abort the wait group. Delayed retry timing depends on wall clock. `q.meter` is called without nil checks in some paths, so callers generally supply a meter.

Test signals: `transfer_queue_test.go` covers retry defaults/backoff, batch size, and adapter reuse/switch rules; full concurrent transfer behavior is mostly integration-tested elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer_queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer_queue_test.go -->
# sources/sync-backup/git-lfs/tq/transfer_queue_test.go

Purpose: tests retry counter defaults/backoff and transfer queue adapter switching behavior.

Important APIs/types/functions: tests for manifest retry defaults, `retryCounter`, `BatchSize`, and `useAdapter` reuse/switch cases.

Control flow: constructs retry counters and queues with simple manifests, invokes methods, and asserts counts, durations, and adapter identity/name.

State and persistence: queues start background goroutines, but tests do not enqueue real transfers or call full wait flows in shown cases.

Dependencies and integration points: uses `lfsapi.NewClient`, `NewManifest`, and `testify/assert`.

Risks: tests instantiate queues without exercising cleanup/wait in all cases, which can leave background goroutines in a larger test run if not handled by Go process exit. Does not cover retry integration with actual adapter results.

Test signals: good coverage for retry arithmetic and adapter normalization of empty name to basic.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer_queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer_test.go -->
# sources/sync-backup/git-lfs/tq/transfer_test.go

Purpose: tests adapter registration, fallback, override, and basic-only listing behavior through the manifest.

Important APIs/types/functions: `testAdapter`, `newTestAdapter`, `newRenamedTestAdapter`, `TestBasicAdapterExists`, `TestAdapterRegAndOverride`, and `TestAdapterRegButBasicOnly`.

Control flow: creates manifests, queries adapter lists and specific adapters, registers test factories for upload/download, overrides them, and asserts custom flags plus fallback-to-basic behavior.

State and persistence: in-memory manifest state only.

Dependencies and integration points: validates manifest registry used by transfer queue adapter selection.

Risks: one assertion in `TestBasicAdapterExists` compares upload adapters using `dls` rather than `uls`, which could mask upload-list mismatch.

Test signals: strong registry behavior coverage despite the noted assertion issue.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/transfer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/tus_upload.go -->
# sources/sync-backup/git-lfs/tq/tus_upload.go

Purpose: resumable upload adapter for the tus.io protocol.

Important APIs/types/functions: `TusAdapterName`, `TusVersion`, `tusUploadAdapter`, `DoTransfer`, and `configureTusAdapter`.

Control flow: gets upload action, sends `HEAD` with `Tus-Resumable`, parses `Upload-Offset`, skips if already complete, opens file, emits progress for resumed bytes, sends `PATCH` from offset with tus headers and callback body, maps network/403 errors to retriable, validates status, drains response, and verifies upload.

State and persistence: reads local object file and relies on server-side resumable upload offset; no local persistence beyond progress state.

Dependencies and integration points: registered only when `lfs.tustransfers` config permits; uses basic upload's start callback reader and verify flow.

Risks: does not validate response `Upload-Offset` after PATCH despite comment saying it should. Offset seek uses `io.SeekCurrent` in the start callback after client rewinds; this depends on body rewind behavior. Unsupported/malformed headers fail non-retriably.

Test signals: no direct tus tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/tus_upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/verify.go -->
# sources/sync-backup/git-lfs/tq/verify.go

Purpose: optional post-upload verification request handling.

Important APIs/types/functions: `maxVerifiesConfigKey`, `defaultMaxVerifyAttempts`, and `verifyUpload`.

Control flow: obtains `verify` action if present, builds POST JSON with oid/size, sets Git LFS JSON headers and action headers, clamps configured attempts to at least default, logs request, and retries `Do`/`DoWithAuth` until a request succeeds or attempts are exhausted.

State and persistence: no durable state; consumes response bodies by closing them.

Dependencies and integration points: called by basic, tus, custom, and SSH upload paths after upload completion. Depends on `lfsapi.Client` and action auth metadata.

Risks: successful HTTP response status is not checked, only transport error/close. `t.Oid[:7]` in tracing assumes OID length at least seven. Config uses `max(default, configured)`, so values below 3 cannot reduce attempts.

Test signals: `verify_test.go` covers no-action success and successful POST with headers/auth access mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/verify_test.go -->
# sources/sync-backup/git-lfs/tq/verify_test.go

Purpose: tests upload verification behavior.

Important APIs/types/functions: `TestVerifyWithoutAction` and `TestVerifySuccess`.

Control flow: no-action test expects nil. Success test starts an HTTP server, asserts method/path/header/content length/body, configures endpoint auth access, and calls `verifyUpload`.

State and persistence: local HTTP server and atomic call counter only.

Dependencies and integration points: validates `verifyUpload` request construction and auth routing through `lfsapi`.

Risks: does not test non-2xx status handling, retries on errors, or short OIDs.

Test signals: useful positive-path coverage for verify action.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tq/verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tr/tr.go -->
# sources/sync-backup/git-lfs/tr/tr.go

Purpose: runtime translation locale initialization for Git LFS messages.

Important APIs/types/functions: package global `Tr`, `locales`, `findLocale`, `processLocale`, and `InitializeLocale`.

Control flow: finds locale from `LC_ALL`, `LC_MESSAGES`, then `LANG`; derives full and language-only options; initializes gotext locale/domain; looks up embedded base64 `.mo` data; decodes/parses first matching locale and adds translator.

State and persistence: global translator and embedded locale map; reads environment variables.

Dependencies and integration points: all translated messages in tools/tq use `tr.Tr.Get`; `trgen` generates data into `locales`.

Risks: global `Tr` mutation affects all packages. Invalid base64 data is skipped silently. Locale fallback only checks first matching embedded option.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tr/tr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tr/trgen/trgen.go -->
# sources/sync-backup/git-lfs/tr/trgen/trgen.go

Purpose: generator that embeds compiled `.mo` translation files into Go source.

Important APIs/types/functions: `infof`, `warnf`, `readPoDir`, `verbose` flag, and `main`.

Control flow: searches root candidates for `po/build`, exits successfully if missing, creates `tr/tr_gen.go`, writes package/init boilerplate, scans `.mo` filenames with regex, reads each file, base64-encodes content into `locales[...]`, and reports count in verbose mode.

State and persistence: writes generated Go file and reads translation build artifacts.

Dependencies and integration points: invoked by `go generate` directive in `tr.go`; produced file populates `locales` map used by `InitializeLocale`.

Risks: regex only accepts letters, hyphen, and underscore locale names. Output file is partially written if an error occurs mid-generation. Missing `po/build` is treated as success.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tr/trgen/trgen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/versioninfo.json -->
# sources/sync-backup/git-lfs/versioninfo.json

Purpose: Windows version resource metadata for Git LFS builds.

Important APIs/types/functions: `FixedFileInfo.FileVersion`, `StringFileInfo.FileDescription`, copyright, product name/version, and `IconPath`.

Control flow: static JSON consumed by build/resource tooling.

State and persistence: static configuration file.

Dependencies and integration points: Windows installer/resource generation references product version `3.7.0` and icon path.

Risks: version fields must stay synchronized with release metadata; stale icon path breaks resource generation.

Test signals: no tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/versioninfo.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.chglog/config-htmlui.yml -->
# sources/sync-backup/kopia/.chglog/config-htmlui.yml

Purpose: changelog generator configuration for the Kopia HTML UI repository.

Important APIs/types/functions: GitHub style, `CHANGELOG_HTMLUI.tpl.md`, repository URL `kopia/htmlui`, commit scope filters, group title maps/order, header regex, and breaking-change note keywords.

Control flow: static config for changelog tooling; commits are filtered/grouped by parsed conventional-commit scope.

State and persistence: no runtime state; controls generated changelog output.

Dependencies and integration points: scope list and title maps must align with PR title workflow comments.

Risks: scopes not listed are excluded from changelog output; divergence from PR title regex can drop valid changes.

Test signals: no direct tests; CI title workflow is the consistency signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.chglog/config-htmlui.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.chglog/config.yml -->
# sources/sync-backup/kopia/.chglog/config.yml

Purpose: main Kopia changelog generator configuration.

Important APIs/types/functions: GitHub style, `CHANGELOG.tpl.md`, repository URL `kopia/kopia`, scope filters, custom grouping/title order, conventional header pattern, and `BREAKING CHANGE` notes.

Control flow: static changelog tooling input; parses commit type/scope/subject and groups by scope.

State and persistence: static config only.

Dependencies and integration points: intended to match `.github/workflows/check-pr-title.yml` scopes.

Risks: missing scopes silently omit commits from generated changelog.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.chglog/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.codecov.yml -->
# sources/sync-backup/kopia/.codecov.yml

Purpose: Codecov project coverage policy and ignore list.

Important APIs/types/functions: coverage range `60..80`, project target `62%`, threshold `1%`, and ignored paths for storage providers, generated gRPC API, test utilities, mocks, and benchmarks.

Control flow: static Codecov service configuration applied to uploaded coverage reports.

State and persistence: no runtime state; affects PR/status reporting.

Dependencies and integration points: used by `code-coverage.yml` upload workflow.

Risks: duplicate `repo/blob/gcs/` ignore entry; broad ignores can hide coverage regressions in important packages.

Test signals: Codecov status checks are the operational signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/auto-merge.yml -->
# sources/sync-backup/kopia/.github/auto-merge.yml

Purpose: dependency auto-merge allowlist for Dependabot PRs.

Important APIs/types/functions: match rules by `dependency_name` and `update_type`, covering selected Go, Playwright, telemetry, Prometheus, React, and test/development dependencies. Comments explicitly exclude large Electron dependencies.

Control flow: consumed by the auto-merge GitHub Action; matching Dependabot updates are eligible for approval/merge.

State and persistence: static policy file.

Dependencies and integration points: referenced by `.github/workflows/auto-merge.yml`; relies on dependency-review/test CI for safety.

Risks: regex-like dependency names depend on action matching semantics. Overbroad minor auto-merge rules can admit regressions if tests are insufficient.

Test signals: auto-merge workflow plus CI outcomes are the practical validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/auto-merge.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/config.yml -->
# sources/sync-backup/kopia/.github/config.yml

Purpose: regex configuration for PR titles and commit messages.

Important APIs/types/functions: `PR_TITLE_REGEX` and `COMMIT_MESSAGE_REGEX` with allowed conventional types and scopes.

Control flow: static config for GitHub automation that validates naming conventions.

State and persistence: none.

Dependencies and integration points: aligns with changelog scope filters and check-pr-title workflow.

Risks: regex requires scoped conventional format and may reject valid emergency/nonstandard changes. It lacks optional breaking `!` support that workflow regex includes.

Test signals: PR title workflow enforces a related regex.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/dependabot.yml -->
# sources/sync-backup/kopia/.github/dependabot.yml

Purpose: Dependabot update schedule and grouping policy.

Important APIs/types/functions: version 2 config for gomod root weekly updates, GitHub Actions monthly updates, npm `/app` monthly updates, cooldowns, PR limits, ignored `github.com/kopia/htmluibuild`, and dependency groups.

Control flow: Dependabot reads this to open grouped update PRs on schedules.

State and persistence: static repository automation config.

Dependencies and integration points: feeds auto-merge policy and dependency-review/CI workflows.

Risks: broad npm group can produce large UI PRs; cooldown delays urgent patch adoption unless manually overridden.

Test signals: Dependabot PR behavior and CI are operational signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/auto-merge.yml -->
# sources/sync-backup/kopia/.github/workflows/auto-merge.yml

Purpose: GitHub Actions workflow that runs Dependabot auto-merge automation on pull requests.

Important APIs/types/functions: workflow `auto-merge`, `pull_request` trigger, checkout action pinned by SHA, `ahmadnassri/action-dependabot-auto-merge` pinned by SHA, and `AUTO_MERGE_TOKEN` secret.

Control flow: on PR events, checkout repository and run action using rules from `.github/auto-merge.yml`.

State and persistence: no repo runtime state; may approve/merge PRs through GitHub API.

Dependencies and integration points: depends on secret availability and auto-merge policy file.

Risks: token scope controls blast radius; pinned action versions must be maintained.

Test signals: workflow run results on Dependabot PRs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/auto-merge.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/check-pr-title.yml -->
# sources/sync-backup/kopia/.github/workflows/check-pr-title.yml

Purpose: PR title convention enforcement workflow.

Important APIs/types/functions: trigger on opened/edited/synchronize/reopened pull requests, `deepakputhraya/action-pr-title`, and regex for conventional type/scope with optional breaking `!`.

Control flow: action validates PR title against the regex.

State and persistence: no runtime state.

Dependencies and integration points: scopes should align with changelog config and `.github/config.yml`.

Risks: action is pinned to a SHA but no version comment; regex drift from other config can create inconsistent acceptance.

Test signals: workflow pass/fail on PRs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/check-pr-title.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/code-coverage.yml -->
# sources/sync-backup/kopia/.github/workflows/code-coverage.yml

Purpose: CI workflow for Go test coverage and Codecov upload.

Important APIs/types/functions: triggers on PR and pushes to master, concurrency cancellation, checkout with full history, setup-go from `go.mod`, `make test-with-coverage`, Codecov upload of `coverage.txt`, and log artifact upload on always.

Control flow: executes tests, uploads coverage, then uploads `.logs/**/*.log` regardless of success.

State and persistence: produces coverage artifact/status and uploaded logs.

Dependencies and integration points: uses `.codecov.yml` policy and Makefile target.

Risks: requires Codecov action/token setup as appropriate; full-history checkout costs time.

Test signals: the workflow itself is a primary test signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/code-coverage.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/compat-test.yml -->
# sources/sync-backup/kopia/.github/workflows/compat-test.yml

Purpose: compatibility test workflow for master, tags, and PRs.

Important APIs/types/functions: triggers on master push, version tags, and PRs; checkout, setup-go from `go.mod`, `make compat-tests`, and log upload.

Control flow: runs compatibility test make target and uploads logs regardless of outcome.

State and persistence: CI artifacts/logs only.

Dependencies and integration points: depends on repository Makefile compatibility target.

Risks: broad trigger on tags means release tags depend on this target stability.

Test signals: direct workflow result.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/compat-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/dependency-review.yml -->
# sources/sync-backup/kopia/.github/workflows/dependency-review.yml

Purpose: GitHub dependency review workflow for pull requests.

Important APIs/types/functions: `pull_request` trigger, read-only contents permission, checkout action pinned by SHA, and `actions/dependency-review-action` pinned by SHA.

Control flow: checks dependency manifest changes for vulnerable packages and reports/fails according to action configuration.

State and persistence: no repo state; produces PR check annotations/status.

Dependencies and integration points: complements Dependabot and auto-merge policy.

Risks: only scans changed manifests in PR context; action pin must be updated for fixes.

Test signals: dependency review check result on PRs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/dependency-review.yml -->
