# subset-b-009758 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bisync_test.go -->
## sources/user-network-fs/rclone/cmd/bisync/bisync_test.go

Purpose: Implements the script-driven integration test engine for rclone bisync. It runs test cases from `cmd/bisync/testdata/test_*/scenario.txt` against local, remote-local, local-remote, and remote-remote path pairings, captures listings/logs/queues, and compares them with golden artifacts.

Important APIs/types/functions: `bisyncTest` stores per-case paths, temp remotes, workdir, golden/log paths, flags, and backend capability adjustments. `TestMain` normalizes logging/timezone test state. `TestBisyncRemoteLocal`, `TestBisyncLocalRemote`, `TestBisyncRemoteRemote`, and `TestBisyncConcurrent` choose topology. `testBisync` enumerates selected cases, and `runTestCase` prepares remotes, copies initial data, executes scenario steps, and compares results. `runTestStep` is the scenario command interpreter, supporting `bisync`, copy/touch/delete/list commands, saved listings, unicode fixups, and injected test functions. `runBisync` maps scenario flags to `bisync.Options` and fs config. `compareResults`, `mangleResult`, `mangleListing`, `storeGolden`, `toGolden`, and `newReplacer` make cross-backend output comparable.

Control flow: Tests create unique temp workspaces and unique remote subtrees, copy initial fixtures to both paths, then process each scenario line after macro replacement. A `bisync` scenario command calls the package API directly through `bisync.Bisync`, captures stdout/stderr-like log output through `bilib.CaptureOutput`, and writes it to `test.log`. After the scenario, the harness either regenerates golden files or compares every produced listing, queue, filter, and log artifact after normalization. Concurrent coverage uses parallel subtests over the `basic` case and disables log comparison because logs interleave.

State and persistence behavior: The harness intentionally persists bisync work files in a temp workdir during a case by passing `NoCleanup: true` and `SaveQueues: true`. It copies or moves `.lst*`, `.que`, `.flt`, and `.flt.md5` artifacts for golden comparison. It rewrites temporary path names, canonical session names, random remote names, and hash type labels out of output. It fixes initial file and directory times to `initDate` for deterministic listings and restores global fs config after each run.

Dependencies and integration points: This file integrates with rclone fs/cache/filter/walk/sync/operations/accounting, backend/all registration, fstest remote provisioning, bisync's exported `Options`, `Bisync`, `CheckSyncMode`, color/log globals, and `bilib` helpers. It has backend-specific guards for Dropbox, OneDrive, SFTP, Mail.ru, empty-dir support, modtime support, blank hashes, Unicode normalization, and fix-case behavior.

Risks: The harness mutates package-level slices such as `logReplacements` in some cases, so test order and parallelism need care. Golden comparison is necessarily tolerant and may hide backend-specific output drift. Scenario parsing is whitespace-token based with custom escapes, so new commands need explicit parsing support. Backend capability checks are pragmatic and may skip meaningful coverage when feature probing changes. The `runBisync` path returns nil after logging bisync errors so expected-error scenarios are represented by golden logs rather than Go errors.

Test signals: Testdata includes scenarios for basic changes, all-changed safety, backup dirs, check-access, filters, check-sync-only, compare-all, dry-run, equal files, extended paths/filenames, ignore-listing-checksum, max-delete, no-modtime, normalization, rclone args, conflict resolve, resync, resync modes, empty dirs, and volatile concurrent mutation. Strong signals are `go test ./cmd/bisync -remote local`, remote matrix runs through `fstest/test_all`, `-case`, `-golden`, `-ignore-logs`, and `-race -pcount` for concurrent lock/log behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bisync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/checkfn.go -->
## sources/user-network-fs/rclone/cmd/bisync/checkfn.go

Purpose: Selects and implements equality/check functions that bisync uses for conflict checks, rechecks, and sync equality overrides. It extends normal rclone checking with crypt-aware and download-hash fallbacks so bisync can avoid unsafe size-only conclusions.

Important APIs/types/functions: `bisyncCheck` stores selected hash type, source/dest filesystems, and crypt wrapper. `WhichCheck` installs `CheckFn`, `CryptCheckFn`, `ReverseCryptCheckFn`, or `DownloadCheckFn` into `operations.CheckOpt`. `checkconflicts` runs a batched check over potential conflicts and returns identical matches. `WhichEqual` checks one object pair. `EqualFn` injects a custom `operations.EqualFn` that combines rclone equality with bisync checksum and resync-mode rules. `resyncTimeSizeEqual` customizes equality for `PreferOlder`, `PreferLarger`, and `PreferSmaller`.

Control flow: `WhichCheck` first uses ordinary hash checking when a common hash, `--size-only`, or `--ignore-checksum` applies. If hashes do not overlap, it detects crypt remotes and compares encrypted/underlying hashes where possible. If that also fails, it uses download comparison. Conflict checking builds an rclone check option, sets `Match` to a buffer, runs `operations.CheckFn`, resets accounting errors, and converts matched lines into `bilib.Names`. The equality override suppresses the ordinary sync logger temporarily, runs time/size equality, optionally downloads or reads hashes, then emits exactly one match/differ event through the original logger.

State and persistence behavior: There is no direct disk persistence, but `b.check` caches the chosen crypt check context for callback execution, and accounting error counters are reset after conflict checking so read-only check failures do not poison bisync's later error accounting. `EqualFn` mutates context config (`CheckSum = false`) to force modtime evaluation before its own checksum logic.

Dependencies and integration points: Uses `backend/crypt`, `cmd/check`, `fs/operations`, `fs/accounting`, `fs/filter`, `fs/hash`, and `bilib.Names`. It is called by `applyDeltas` for potential conflicts, by `listing.recheck`, and by queue setup when checksum/modtime/download-hash semantics exceed normal sync equality.

Risks: Type assertions in `CryptCheckFn` assume the callback arguments match the selected crypt direction. Download checking can be expensive and data-heavy. Blank hashes deliberately produce "unknown, not different", which reduces false positives but can leave conflicts unresolved. The custom equality logger path must remain aligned with rclone sync logger expectations.

Test signals: Bisync golden tests covering crypt, checksum, compare-all, ignore-listing-checksum, equal conflicts, download-hash, and blank-hash backends exercise this file indirectly. Useful focused tests would assert `WhichCheck` selection for common-hash, dst-crypt, src-crypt, no-hash, size-only, and ignore-checksum combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/checkfn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/cmd.go -->
## sources/user-network-fs/rclone/cmd/bisync/cmd.go

Purpose: Defines the `rclone bisync` CLI command, command flags, option structure, check-sync enum, and option pre-processing for filters, dry-run, workdir, and max-delete behavior.

Important APIs/types/functions: `Options` is the central user-facing configuration consumed by `Bisync`. `CheckSyncMode` supports `true`, `false`, and `only` with `String`, `Set`, and `Type` for flag/RC parsing. Global `Opt` backs cobra flags. `commandDefinition` validates two directory arguments and calls `Bisync`. `Options.applyContext`, `setDryRun`, and `applyFilters` bridge global fs config into bisync-specific options.

Control flow: Package init registers the command, binds all bisync flags, hides debugging flags, and registers the RC endpoint. CLI execution rejects file arguments, copies global `Opt`, applies context-derived defaults, optionally sets listing timezone to local, warns for Dropbox/no common hash/refresh-times, then runs `Bisync` under `cmd.Run`. `applyFilters` validates an external filters file by MD5 sidecar: non-resync runs require an unchanged `.md5`; resync writes or logs the hash depending on dry-run.

State and persistence behavior: `DefaultWorkdir` is under rclone's cache dir. Filter integrity is persisted in `<filters-file>.md5`; changing filters without `--resync` aborts. `applyContext` copies `ci.MaxDelete` into bisync's option and resets the global value to `-1` so lower-level operations do not enforce a separate max-delete policy. `setDryRun` creates a context with `ci.DryRun` set from bisync options.

Dependencies and integration points: Integrates with rclone `cmd`, cobra, flag helpers, fs config, filters, hashes, `bilib`, and `fserrors.FatalError` for aborted runs. Flag comments explicitly require keeping `rc.go`, `help.go`, and user docs synchronized.

Risks: The global `Opt` and `tzLocal` are package state and must be copied before mutation. New flags can drift from RC/help generation if not updated. Filter hash enforcement depends on users preserving the `.md5` sidecar. The Dropbox refresh-times warning is heuristic and name-prefix based.

Test signals: CLI parsing is indirectly covered by scenario flags in `bisync_test.go`; RC parity is covered through generated help and `rcBisync` option mapping. Direct unit tests should cover `CheckSyncMode.Set`, max-delete clamping, filter hash mismatch/resync behavior, and directory-only argument rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/cmd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/compare.go -->
## sources/user-network-fs/rclone/cmd/bisync/compare.go

Purpose: Computes the effective comparison policy for bisync listings, deltas, equality checks, and sync calls. It decides whether size, modtime, checksum, slow hashes, and download-hash are used.

Important APIs/types/functions: `CompareOpt` stores comparison booleans and selected hash types. `setCompareDefaults` derives defaults from global config and bisync flags. `sizeDiffers`, `hashDiffers`, and `timeDiffers` implement conservative difference predicates. `setHashType` chooses common or same-side hash types and handles slow hash settings. `setFromCompareFlag` parses `--compare`. `downloadHashOpt` and `tryDownloadHash` support MD5 computation by downloading objects.

Control flow: Defaults start as size+modtime. Global `--size-only`, `--checksum`, `--ignore-size`, and bisync `--compare` mutate that baseline. Slow-hash detection and no-slow/slow-sync-only flags may suppress listing hashes, keep checksums only for sync, or fall back to size/modtime. If no comparison method remains, setup fails. Unsupported global sync flags such as `--update`, `--no-check-dest`, and `--no-traverse` are logged and disabled.

State and persistence behavior: This file stores no files, but it mutates `Options.Compare`, `Options.IgnoreListingChecksum`, `downloadHashOpt`, and `fs.ConfigInfo` in the active context. `tryDownloadHash` registers accounting checking transfers and emits a first-use "Downloading hashes" notice once.

Dependencies and integration points: Used by `Bisync` before all run setup, by listing and delta comparison, by queue logger hash capture, by conflict resolution, and by recheck/equality code. It depends on rclone fs features (`SlowHash`, precision, hash sets), accounting, operations hash helpers, and terminal coloring.

Risks: Comparison policy has many interacting flags; a small change can alter listing format, delta detection, and sync equality differently. Blank hashes are treated as inconclusive rather than different. `--download-hash` may use large bandwidth and skips unknown-size objects. `--slow-hash-sync-only` intentionally makes listing and sync comparison differ.

Test signals: Existing scenarios `compare_all`, `nomodtime`, `ignorelistingchecksum`, `equal`, and backend matrix runs exercise this. Focused tests should cover `--compare` exclusions, no common hash fallback, slow hash combinations, unknown sizes, unsupported modtime, and download-hash first-use/error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/compare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/deltas.go -->
## sources/user-network-fs/rclone/cmd/bisync/deltas.go

Purpose: Computes per-side changes since the last successful bisync listing and converts two delta sets into copy/delete/rename queues. It is the core decision engine for non-resync runs.

Important APIs/types/functions: `delta` is a bitmask for new, newer, older, larger, smaller, hash-different, and deleted states. `deltaSet` stores per-file delta bits plus changed size/time/hash values, counts for safety checks, and check-access files. `findDeltas` compares prior and current listings. `applyDeltas` resolves cross-side deltas into queued operations and calls copy/delete helpers. `excessDeletes` enforces max-delete. `updateAliases` supplements march aliases for deleted case/unicode variants.

Control flow: `findDeltas` loads the prior listing, validates old and current listings, iterates old files for deletion or modifications, then iterates current files for additions. It records at least one unchanged file to detect "all files changed" safety conditions. `applyDeltas` builds copy/delete/handled sets, loads directory-only listings when empty dir sync is enabled, batches potential same-name conflicts through `checkconflicts`, then iterates Path1 deltas and Path2 leftovers. Non-identical two-sided changes go through `resolve`; one-sided changes become copies or deletes. Finally it executes copy queues through `fastCopy` and directory synchronization through `syncEmptyDirs`; delete queues are saved for listing modification but actual deletion is represented by sync behavior and listing updates.

State and persistence behavior: Delta decisions depend on persisted `.path1.lst` and `.path2.lst` files plus newly written `-new` listings. Optional queue files are saved by `saveQueue` when `SaveQueues` is true. The function mutates `b.aliases` and `b.renames`, and returns `queues` used later by `modifyListing` to update persistent listings.

Dependencies and integration points: Depends on `fileList`, compare predicates, `bilib.Names`, filters, terminal logging, unicode normalization, `checkconflicts`, `resolve`, `listDirsOnly`, `fastCopy`, `retryFastCopy`, and `syncEmptyDirs`. It is called from `runLocked` after both current listings are built.

Risks: This is high-risk data movement logic. Alias handling for deleted files, case-insensitive remotes, and Unicode normalization is subtle. Equality checks skip files with definitely different size/hash, so stale or missing metadata can change conflict handling. Safety aborts rely on prior listings being trustworthy. Directory handling is intentionally different from file handling.

Test signals: Golden scenarios for changes, all_changed, max_delete, resolve, normalization, createemptysrcdirs, volatile, dry_run, and equal conflicts are key. Additional focused tests should cover deleted aliases, both-side delete, identical conflicts with differing modtime, missing hashes, and `--force` bypass behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/deltas.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/help.go -->
## sources/user-network-fs/rclone/cmd/bisync/help.go

Purpose: Build-tagged generator for `rc.md`, the embedded remote-control help text for the bisync RC endpoint.

Important APIs/types/functions: `main` writes generated help to stdout or a named file. `RcHelp` returns word-wrapped RC documentation. `toCamel` converts CLI flag names to RC parameter names. `GenerateParams` locates the cobra `bisync` command and emits non-hidden flags with type and usage.

Control flow: `go generate ./cmd/bisync` runs this file via the directive in `rc.go`. It writes a generated-file warning, static required `path1`/`path2`/`dryRun` docs, generated flag parameter lines, and links to command/manual docs.

State and persistence behavior: The only persistent output is the generated `rc.md` file when a path argument is supplied. It does not run in normal builds because of `//go:build none`.

Dependencies and integration points: Imports the real `cmd` and `bisync` packages so generated help reflects registered cobra flags. Uses `muesli/reflow/wordwrap`, pflag, and Go text casing.

Risks: Generated RC docs can drift if `go generate` is not run after flag changes. `toCamel` is simple hyphen splitting and assumes lowercase CLI flag names. Importing the command package during generation relies on init side effects registering `bisync`.

Test signals: `go generate ./cmd/bisync` followed by a diff of `rc.md` is the primary signal. New flags should appear in generated help unless hidden; hidden debug/localtime flags should not.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/help.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/listing.go -->
## sources/user-network-fs/rclone/cmd/bisync/listing.go

Purpose: Defines bisync's persisted listing format and the machinery for loading, saving, validating, updating, rechecking, and rolling back `.lst` files. These listings are the durable state that lets later runs detect changes on each side.

Important APIs/types/functions: `ListingHeader`, `lineFormat`, `lineRegex`, `timeFormat`, `TZ`, and `LogTZ` define serialization. `fileInfo` and `fileList` store remote name to size/time/hash/id/flags data. Core methods include `has`, `get`, `put`, `remove`, `save`, `loadListing`, `fileInfoEqual`, `checkListing`, `listDirsOnly`, `modifyListing`, `recheck`, `rollback`, `prepareRollback`, `getOldLists`, and generic `Concat`.

Control flow: New listings are created during march or resync. `save` sorts remote names, writes a header, and serializes entries with optional hash type prefix. `loadListing` parses lines defensively, skipping malformed and inconsistent-hash lines, and keeps the newest duplicate. `modifyListing` loads source/destination listings, derives winners and errors from sync `Results`, removes or adds queued files, applies rename bookkeeping, rechecks uncertain files with narrow filters, handles graceful-shutdown rollback, then saves both listings. `recheck` lists selected source/destination objects and uses `WhichEqual` before trusting listing updates; unresolved items roll back to `-old` listings outside resync.

State and persistence behavior: Listing files are persistent state: current `.lst`, temporary `.lst-new`, backup `.lst-old`, dry-run `.lst-dry`, and failure `.lst-err` names are managed elsewhere but parsed here. `saveOldListings`, `replaceCurrentListings`, and `revertToOldListings` copy listing generations. Directory entries are represented with flag `d` and size `-1` when empty-dir sync is enabled. Timezone for persisted times is controlled by `TZ`.

Dependencies and integration points: Used by every bisync mode. Integrates with `bilib.CopyFileIfExists`, rclone filter/list operations, hash APIs, accounting transfer stats, `Results` from `queue.go`, alias and rename maps from delta resolution, and comparison logic from `compare.go`.

Risks: Listing correctness is central to data safety. Malformed lines are ignored rather than fatal, which can hide partial corruption. Duplicate handling keeps the latest modtime. Hash type consistency is enforced per listing, so mixed hash listings lose lines. `modifyListing` must reconcile copies, renames, skipped equal conflicts, empty dirs, dry-run, and graceful shutdown without losing retry state.

Test signals: Most golden tests compare final and saved listings. Important scenarios include dry_run, check_sync, resync, resolve, createemptysrcdirs, rmdirs, normalization, and volatile shutdown/concurrent mutation. Focused tests should cover parsing malformed listings, duplicate entries, rollback from old listings, recheck failures, and mixed hash types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/listing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/lockfile.go -->
## sources/user-network-fs/rclone/cmd/bisync/lockfile.go

Purpose: Provides per-session lock-file creation, expiration, renewal, removal, and failure marking so two bisync runs over the same paths do not overlap.

Important APIs/types/functions: `basicallyforever` represents no practical expiration. `lockFileOpt` stores renewal stopper and JSON lock metadata. `setLockFile`, `removeLockFile`, `setLockFileExpiration`, `renewLockFile`, `lockFileIsExpired`, `startLockRenewal`, and `markFailed` implement lock lifecycle.

Control flow: `setLockFile` clamps `--max-lock`, skips locks in dry-run, derives `<basePath>.lck`, rejects a present non-expired lock, writes the current PID, rewrites it as JSON metadata, and starts background renewal when expiration is finite. `lockFileIsExpired` opens and decodes existing JSON; unreadable files expire only when finite max-lock is configured, and expired/unreadable locks mark listings failed so recovery or resync is required. `removeLockFile` stops renewal before deleting.

State and persistence behavior: The lock file is persisted as JSON containing session, PID, renewal time, and expiration time. Expired/unreadable lock handling renames current listings to `-err` via `markFailed`, deliberately invalidating potentially unsafe state. Renewal rewrites the lock file at `max-lock - 1 minute` intervals.

Dependencies and integration points: Called by `Bisync` around `runLocked` and from atexit signal handling. Uses `bilib.FileExists`, secure file permissions, terminal-colored diagnostics, and `prettyprint` for lock info.

Risks: Lockfiles protect only sessions that share the same canonical `basePath`. Unreadable legacy or corrupt lockfiles without `--max-lock` block forever by design. Renewal uses goroutine lifecycle and must always be stopped before removal. Marking listings failed is conservative but may surprise users after an expired stale lock.

Test signals: `lockfile_test.go` directly covers unreadable with/without max-lock and expired/not-expired JSON. Additional useful tests include max-lock clamping, dry-run no-lock behavior, renewal stop behavior, and lock contention messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/lockfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/lockfile_test.go -->
## sources/user-network-fs/rclone/cmd/bisync/lockfile_test.go

Purpose: Unit tests for `lockFileIsExpired` behavior around corrupt and time-bounded lock files.

Important APIs/types/functions: `newTestLockfileBisyncRun` creates a temp lock file plus placeholder listing files and returns a minimal `bisyncRun`. Tests are `TestLockfileIsExpired_UnreadableWithMaxLock`, `TestLockfileIsExpired_UnreadableWithoutMaxLock`, `TestLockfileIsExpired_ValidExpired`, and `TestLockfileIsExpired_ValidNotExpired`.

Control flow: Each test writes either invalid JSON or JSON matching lock metadata fields, configures `Options.MaxLock`, calls `lockFileIsExpired`, and asserts the expected boolean. The helper also creates listing files because expired/corrupt-with-max-lock cases call `markFailed`.

State and persistence behavior: Tests use `t.TempDir` and write lock/listing files with `0600`. The function under test may rename listing files to `-err`; the current assertions focus on expiration boolean rather than side effects.

Dependencies and integration points: Uses Go testing, testify assert/require, rclone `fs.Duration`, and the package-private `bisyncRun` internals because it is in package `bisync`.

Risks: The tests do not assert listing rename side effects, close-error paths, max-lock clamping, or renewal behavior. They use wall-clock `time.Now`, but windows are wide enough to avoid flake.

Test signals: These are fast unit-level checks complementing the larger golden integration suite. A regression that treats corrupt locks as expired without max-lock, or fails to expire stale JSON locks, should fail here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/lockfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/log.go -->
## sources/user-network-fs/rclone/cmd/bisync/log.go

Purpose: Centralizes bisync-specific logging formatting, path escaping, optional terminal colors, OS path encoding, and JSON pretty-print debugging.

Important APIs/types/functions: `indentf` and `indent` emit aligned Path1/Path2 action logs. `escapePath` and `quotePath` encode and quote paths safely. `Colors`, `ColorsLock`, `Color`, and `ColorX` gate terminal color sequences. `encode` round-trips paths through rclone's OS encoder. `prettyprint` JSON-formats arbitrary debug/info structures.

Control flow: `indent` chooses log severity based on tags: `ERROR` uses `fs.Errorf`, `INFO` removes the tag, `!` prefixes force notice-level `fs.Logf`, and dry-run upgrades output visibility to log level. It colorizes path, tag, and message fragments and highlights queue copy/delete text. Path escaping quotes only when control characters or forced quotes require it, with Windows backslashes normalized for quote testing.

State and persistence behavior: No direct persistence. Global color state is protected by a mutex and is enabled by `Bisync` or tests when terminal color mode allows it. Logs are consumed by CLI, RC capture, and golden tests.

Dependencies and integration points: Used throughout bisync for user-facing decisions and debug dumps. Integrates with rclone fs logging, terminal styles, and encoder path conversions.

Risks: Log text is part of golden test expectations and user diagnostics, so wording/spacing changes have broad test impact. `ColorX` currently duplicates `Color`. `prettyprint` logs empty bytes if marshal fails after debuging the marshal error.

Test signals: Golden log comparison in `bisync_test.go` heavily exercises this. Path escaping is indirectly tested by extended filename/path scenarios and Windows slash normalization rules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/march.go -->
## sources/user-network-fs/rclone/cmd/bisync/march.go

Purpose: Builds current Path1 and Path2 listings by walking both filesystems with rclone's `march` engine and recording files, optional directories, hashes, modtimes, and alias relationships.

Important APIs/types/functions: `bisyncMarch` stores current `fileList`s, first errors, context, and locks for concurrent callbacks. `makeMarchListing` runs the two-sided march and saves `-new` listings. Callback methods `SrcOnly`, `DstOnly`, and `Match` implement `march.March` behavior. `parse`, `ForObject`, and `ForDir` add entries. `findCheckFiles` runs a filtered march for check-access during resync. `ID` extracts object IDs when supported, though current listing code leaves IDs blank.

Control flow: `makeMarchListing` stores the context, initializes listing hash types, configures `march.March` with Path2 as destination and Path1 as source, and runs it. Callbacks parse source-only, destination-only, and matched entries, with matches also adding aliases for normalized/case-varied names. Object callbacks register checking transfers, compute configured hashes and optional download hashes, record first hash error, capture modtime if enabled, and append to the appropriate listing under lock. Successful marches save both new listings.

State and persistence behavior: Writes `b.newListing1` and `b.newListing2`, which later become durable current listings or feed delta detection. Mutates `b.march.ls1`, `b.march.ls2`, `b.aliases`, and `b.march.firstErr`. Directory entries are only persisted when `CreateEmptySrcDirs` is enabled.

Dependencies and integration points: Depends on rclone `fs/march`, `fs/accounting`, filters, hash support, and listing serialization. Called by normal `runLocked`; `findCheckFiles` is used by resync check-access.

Risks: March callbacks may be concurrent, so alias/list/error locks are required. Hash errors are captured as firstErr and can abort later. Download-hash during listing can be expensive. Directory support is conditional and can alter downstream delta/listing behavior.

Test signals: Normal and resync tests exercise listing generation. Empty-dir, normalization, compare-all, download-hash, and check-access scenarios are especially relevant. Focused tests would simulate hash errors, aliases from case/unicode normalization, and directory inclusion toggles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/march.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/operations.go -->
## sources/user-network-fs/rclone/cmd/bisync/operations.go

Purpose: Orchestrates a full bisync run: option finalization, workdir/listing path setup, locking, graceful shutdown, resync or normal sync execution, safety checks, listing updates, final validation, and cleanup.

Important APIs/types/functions: `ErrBisyncAborted` maps critical aborts to fatal CLI exit. `bisyncRun` is the runtime state container for filesystems, options, listings, aliases, contexts, critical/retryable flags, sync cancellation, lock state, queues, comparison/check state, and conflict state. `queues` carries copy/delete/skip sets between delta application and listing modification. `Bisync` is the public package API. `runLocked`, `checkSync`, `checkAccess`, `handleErr`, `setBackupDir`, `overlappingPathsCheck`, `checkSyntax`, `debug`, `debugFn`, and `waitFor` implement the run.

Control flow: `Bisync` copies user options, fills defaults, enables colors, computes compare/resync/resolve defaults, creates the workdir, derives canonical listing paths, validates syntax, takes the lock, registers signal finalization, runs `runLocked`, removes the lock, and maps critical conditions to `ErrBisyncAborted`. `runLocked` supports check-sync-only, dry-run listing copies, filter application, overlapping path checks, resync dispatch, prior-listing recovery, current listing march, delta detection, check-access, max-delete/all-changed safety aborts, applying changes, saving old listings, modifying/replacing listings, optional final check-sync, and optional empty-dir removal.

State and persistence behavior: Persists workdir files named from `b.basePath`: current listings, `-new`, `-old`, `-err`, `-dry`, queue files, filter hash sidecars, and lock files. `--recover` can restore old listings after missing current listings. Critical non-resilient errors rename listings to `-err`. Graceful shutdown attempts to leave listings representing completed transfers and marks failed if cleanup cannot finish.

Dependencies and integration points: This file ties together every bisync subsystem: command options, compare, resolve, resync, lockfile, march, deltas, listing, queue, check functions, rclone fs/accounting/log/operations, backup-dir handling, atexit signal hooks, and terminal output.

Risks: This is the highest-level data safety path. Misclassifying errors as non-critical or retryable can lead to unsafe next runs. Signal handling depends on sync cancellation, transfer accounting, and listing rollback. Workdir/listing naming must remain stable for recovery. Overlapping path and backup-dir checks are essential because bisync uses files-from filters that can otherwise hide dangerous overlaps.

Test signals: The full golden suite is the main coverage. Key scenarios include missing listings/recover, check-sync-only, all_changed, max_delete, filtersfile checks, dry_run, resync, backupdir, rmdirs, and volatile/test-func interruption. Unit tests around `waitFor`, syntax detection, and backup-dir overlap would add focused coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/queue.go -->
## sources/user-network-fs/rclone/cmd/bisync/queue.go

Purpose: Captures rclone sync/copy results as structured records, executes queued file copies and resync directory copies, retries resilient transfers, syncs empty directories, and optionally saves queue files.

Important APIs/types/functions: `Results` represents one logger event side with source/destination paths, canonical name, alternate name, metadata, sigil, error, winner, side booleans, and origin. `ResultsSlice.has`, `bisyncQueueOpt`, `getHashType`, `FsPathIfAny`, `resultName`, `altName`, `WriteResults`, `ReadResults`, `preCopy`, `fastCopy`, `retryFastCopy`, `resyncDir`, `syncEmptyDirs`, `saveQueue`, and `naptime` are the core APIs.

Control flow: `preCopy` configures logger state, hash type lookup, listing metadata suppression, custom equality when needed, and slow-hash sync config. `fastCopy` saves a queue, builds a files-from filter including aliases, installs dry-run and sync logger context, stores `SyncCI` and cancel function for graceful shutdown, invokes `sync.Sync`, then decodes JSON logger results. `retryFastCopy` repeats failed syncs when `--resilient` and retry settings allow. `resyncDir` runs `sync.CopyDir` for resync. `syncEmptyDirs` explicitly mkdirs or removes directory candidates and appends synthetic `Results`.

State and persistence behavior: `WriteResults` encodes JSON into `operations.LoggerOpt.JSON`, later decoded by `ReadResults`; this in-memory log is the source for listing updates. `saveQueue` writes `<basePath>.<jobName>.que` when `SaveQueues` is true. The queue state stores `SyncCI` and `CancelSync` on `bisyncRun` for graceful shutdown.

Dependencies and integration points: Integrates with rclone `fs/sync`, `operations` logger/winner APIs, filters, accounting retry-after, hashes, terminal logging, and `bilib.Names`. Listing modification relies on the exact `Results` fields emitted here.

Risks: `WriteResults` emits one result per side per logger event, so listing code must interpret duplicates and side booleans correctly. Unknown-size files under checksum/size-only are warned because they can sync unreliably. Retry re-runs the whole queue and must reconcile prior partial results. Empty-dir synthetic results must match listing semantics.

Test signals: Golden queues/listings in copy, resync, createemptysrcdirs, rmdirs, dry_run, and resilient/volatile scenarios validate this indirectly. Focused tests should cover `ReadResults` round trip, alternate names, directory result synthesis, retry-after handling, and logger output for errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/rc.go -->
## sources/user-network-fs/rclone/cmd/bisync/rc.go

Purpose: Registers and implements the `sync/bisync` remote-control endpoint, including embedded help text, option parsing from `rc.Params`, execution, captured output, and returned workdir/listing metadata.

Important APIs/types/functions: `addRC` registers the call. `rcHelp` embeds generated `rc.md`. `shortHelp`, `longHelp`, and `MakeHelp` provide shared command/help text. `rcBisync` parses RC parameters and calls `Bisync`. `setEnum` parses optional enum strings with defaults.

Control flow: `rcBisync` creates a derived config context, reads optional booleans, strings, ints, durations, and enum values using camelCase parameter names, validates `maxDelete`, supports backward-compatible `backupdir1/backupdir2`, resolves `path1` and `path2` with `rc.GetFsNamed`, captures bisync output, writes it to the configured rclone log writer, computes canonical workdir/basePath, and returns output/session/workdir/listing/log metadata.

State and persistence behavior: The endpoint itself persists no state beyond whatever `Bisync` writes into the selected workdir. It returns exact listing paths so RC callers can inspect persisted state. It mutates only the derived config context for dry-run and other options.

Dependencies and integration points: Integrates with rclone `fs/rc`, `fs/log`, `bilib.BasePath`, `bilib.CaptureOutput`, command help generation, and the same `Options` structure used by CLI. `cmd.go` init calls `addRC`.

Risks: CLI and RC option parity is manual except for generated docs; adding a new option requires updating this parser. Optional-parameter logging uses `rc.NotErrParamNotFound` patterns that are easy to invert if edited carelessly. Captured output can be large for verbose runs. Defaults for enums depend on zero-value `Options` string methods.

Test signals: RC-specific tests should call `sync/bisync` with minimal params, invalid maxDelete, enum params, dryRun, custom workdir, and backward-compatible backupdir casing. Existing integration tests mainly exercise the package API, not RC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/resolve.go -->
## sources/user-network-fs/rclone/cmd/bisync/resolve.go

Purpose: Defines automatic conflict-resolution strategies and loser actions for files changed on both sides, including conflict suffix generation, winner selection, renaming, deletion, and rename bookkeeping for listing updates.

Important APIs/types/functions: `Prefer` enum supports none, path1, path2, newer, older, larger, and smaller. `ConflictLoserAction` supports numbered suffix, pathname suffix, and delete. `setResolveDefaults` validates suffix and strategy compatibility. `renames`, `renamesInfo`, and `namePair` record old/new names. `resolve`, `SuffixName`, `numerate`, `numerateSingle`, `rename`, `delete`, `conflictWinner`, `resolveNewerOlder`, and `resolveLargerSmaller` implement behavior.

Control flow: For a two-sided non-identical change, `resolve` optionally picks a winning path, computes default suffixed names, adjusts names for pathname or numbered/delete loser policies, and either deletes the loser plus queues winner copy or renames both/non-winner files and queues copies of renamed objects. Numbering probes both listings and aliases until an unused suffix is found. Rename and delete operations honor dry-run/destructive skip checks. The rename map is stored for later listing reconciliation.

State and persistence behavior: Conflict resolution can mutate remote state immediately via `operations.MoveFile` or `DeleteFileWithBackupDir`, with path-specific backup-dir config. It mutates `b.renames`, copy queues, and `renameSkipped`; durable listing state is updated later in `modifyListing`. Suffixes may include expanded time globs captured once per run.

Dependencies and integration points: Called from `applyDeltas`; relies on delta metadata, listing alias maps, fs config `SuffixKeepExtension`, transform suffix/time helpers, rclone destructive-operation safeguards, backup-dir setup, and listing update code.

Risks: Conflict handling is destructive and user-visible. Winner selection can be indeterminate when modtime/size data is missing or equal. Delete-loser only deletes when a winner is known; otherwise both sides are renamed. Naming must account for aliases, case-insensitive remotes, unicode normalization, and extension-preserving suffixes. Errors during rename/delete are critical.

Test signals: `test_resolve`, `test_resync_modes`, normalization/fix-case cases, and backupdir cases are central. Focused tests should cover suffix parsing with one/two/more values, suffix-keep-extension, numbered collision search, no-winner delete fallback, path1/path2/newer/older/larger/smaller winners, and dry-run skip behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/resolve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/resync.go -->
## sources/user-network-fs/rclone/cmd/bisync/resync.go

Purpose: Implements `--resync` and `--resync-mode`, the recovery/initialization mode that rebuilds listings by copying unique or preferred files across both paths before normal incremental bisync can run.

Important APIs/types/functions: `setResyncDefaults` maps legacy `--resync` to `--resync-mode path1` and validates mode support. `resync` runs the two directional copy passes and listing updates. `setResyncConfig` maps resync modes to rclone sync config for path preference/newer behavior. `resyncWhichIsWhich` and `resyncWinningPathToEqual` support custom equality for older/larger/smaller modes.

Control flow: `resync` first writes blank `-new` listings, optionally runs check-access through `findCheckFiles`, then copies Path2 to Path1 and Path1 to Path2 using `resyncDir`. For path preference modes it toggles `IgnoreExisting` between the two passes. For newer it enables `UpdateOlder`; older/larger/smaller are implemented by the equality override in `checkfn.go`. It replaces current listings, derives queues from successful source-side results, calls `modifyListing` for both directions, optionally validates check-sync, and removes temporary new listings unless `NoCleanup`.

State and persistence behavior: Resync creates or replaces durable `.path1.lst` and `.path2.lst` from scratch, saving old listings when present. It writes temporary blank listings to seed `modifyListing`. It respects dry-run through context config and leaves temp files when cleanup is disabled.

Dependencies and integration points: Called from `runLocked` before normal prior-listing checks. Uses queue/resyncDir, listing modification, check-access, check-sync, backup-dir setup, and conflict preference enums from `resolve.go`.

Risks: Resync intentionally establishes the baseline truth, so wrong preference logic can overwrite desired versions. Two-pass copy behavior is sensitive to `IgnoreExisting`, `UpdateOlder`, and custom equality semantics. Check-access is enforced even during resync, which can block recovery if check files are unavailable.

Test signals: `test_resync` and `test_resync_modes` cover the main behavior; check-access and dry-run scenarios add cross coverage. Focused tests should assert mode defaults, unsupported modtime/size fallback to path1, two-pass queue derivation, and final listing equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/resync.go -->
