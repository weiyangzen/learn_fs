# Research: subset-b-009153

This grouped report covers Kopia end-to-end, recovery, stress, robustness, UI, OS snapshot, and benchmark test files. Each section is bounded by source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/server_start_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/server_start_test.go

## Purpose
Exercises `kopia server start` behavior from the CLI and API client side. It covers authenticated TLS UI startup, server-control credentials, repository connect/create/disconnect via REST API, asynchronous repository connection, scheduler-driven snapshots and maintenance, insecure startup validation, and UI title escaping.

## Important APIs, Types, And Functions
- `TestServerStart` creates a filesystem repository, starts the server with UI/TLS/random passwords, authenticates both normal and server-control API clients, verifies throttling, source/snapshot listing, estimate tasks, upload/cancel APIs, object retrieval, and policy creation through `serverapi`.
- `TestServerStartAsyncRepoConnect` simulates an unavailable filesystem repository by renaming the repo path, verifies normal start failure, then verifies `--async-repo-connect` starts disconnected and later connects once the path returns.
- `TestServerCreateAndConnectViaAPI` and `TestConnectToExistingRepositoryViaAPI` exercise `CreateRepository`, `DisconnectFromRepository`, and `ConnectToRepository` request flows using `blob.ConnectionInfo` with filesystem options.
- `TestServerScheduling` validates server-side scheduling: per-source snapshot intervals and full maintenance scheduling run while the server process is alive.
- `TestServerStartInsecure`, `TestServerStartInsecureUnauthenticatedNonLoopbackRejected`, and `TestServerStartInsecureUnauthenticatedEscapeHatchNonLoopback` define the accepted and rejected insecure/unauthenticated bind combinations.
- Helpers include `verifyServerConnected`, `verifyUIServerConnected`, `waitForSnapshotCount`, `estimateSnapshotSize`, `uploadMatchingSnapshots`, `verifySnapshotCount`, `verifySourceCount`, `verifyUIServedWithCorrectTitle`, and `waitUntilServerStarted`.

## Control Flow
Tests build a `testenv.CLITest` with an in-process runner, run repository CLI setup, start the server with `RunAndProcessStderr`, parse `testutil.ServerParameters` from stderr, then use `apiclient.KopiaAPIClient` to issue `serverapi` calls. Long-running server commands return `wait` and sometimes `kill` callbacks; tests defer shutdown via `serverapi.Shutdown` or explicit process kill. Polling uses `retry.PeriodicallyNoValue` and direct sleep loops around status, task, and snapshot count endpoints.

## State And Persistence Behavior
The file mutates real temporary filesystem repositories, config state, snapshot manifests, policy manifests, maintenance schedules, throttling settings, and server runtime state. API create/connect tests persist repository configuration and verify connected/disconnected state transitions. Scheduling persists per-source policies and maintenance schedule state, then validates additional snapshot manifests and maintenance run records after server execution.

## Dependencies And Integration Points
Depends on `internal/apiclient`, `internal/serverapi`, `repo/blob/filesystem`, `snapshot/policy`, `maintenance`, `testenv`, `testutil.ServerParameters`, and shared test data directories. It bridges CLI process execution with HTTP API calls and UI HTML serving. Server-control authentication uses the constant username `server-control`.

## Risks And Edge Cases
The suite is timing-sensitive: server startup, async connect, estimate tasks, scheduled snapshots, and maintenance are all bounded by polling or sleeps. It depends on localhost bind behavior and on output parsing from server stderr. Security-sensitive cases assert unauthenticated insecure startup is limited to loopback unless a dangerous escape-hatch flag is provided. UI title verification protects HTML escaping of configured title prefixes.

## Test Signals
Strong integration signal for server lifecycle, API compatibility, repository creation/connect semantics, scheduling, security defaults, TLS fingerprint use, CSRF fetching, and UI title escaping. Failures often indicate cross-package regressions rather than isolated unit bugs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/server_start_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/shallowrestore_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/shallowrestore_test.go

## Purpose
Validates Kopia shallow restore semantics: placeholder files/directories, depth handling, shallow minimum-size behavior, mutation/resnapshot cycles, shallowifying safety checks, rejection of malformed placeholders, and detection of foreign repository object references.

## Important APIs, Types, And Functions
- `TestShallowrestore` snapshots a generated tree and restores it at multiple shallow depths, comparing restored placeholders against repository directory entries.
- `TestShallowrestoreWithMinSize` checks `--shallow-minsize` keeps small files real while large files become placeholders.
- `TestShallowFullCycle` applies several `filesystemmutator` operations to both a full restore and a shallow restore, snapshots the mutated shallow tree, restores it, and compares it with the mutated full tree.
- Mutators include `addOneFile`, `moveDirectory`, `moveFile`, `deepenSubtreeDirectory`, `deepenSubtreeFile`, `deepenOneSubtreeLevel`, `removeEntry`, and `addForeignSnapshotTree`.
- `TestShallowifyTree`, `TestPlaceholderAndRealFails`, and `TestForeignReposCauseErrors` cover failure cases for unsafe overwrite, malformed placeholder layouts, and invalid object IDs.
- `repoDirEntryCache` caches `snapshot.DirEntry` values fetched via `kopia show` and validates placeholder JSON through `validatePlaceholder`.
- Helper routines parse placeholder layouts through `getShallowDirEntry`, `getShallowInfo`, `findFileDir`, `findRealFileDir`, and `mustParseID`.

## Control Flow
The tests create random directory trees with files and symlinks, snapshot them, restore shallow views, then walk the original tree and compare expected restored entries. At the shallow boundary, entries should be regular placeholder files containing JSON-encoded `snapshot.DirEntry`; above the boundary entries should be real filesystem files/directories/symlinks; below the boundary entries should be absent. Mutation-cycle tests restore original data, shallow-restore the same snapshot, apply paired mutations, snapshot the shallow tree, fully restore it, and compare with the full mutated original.

## State And Persistence Behavior
Shallow restore state is represented in the filesystem using `localfs.ShallowEntrySuffix` and JSON-encoded snapshot directory entries. Repository state is read through snapshot IDs/root object IDs and `show` output. Mutators intentionally create, move, hard-link, remove, and reify files/directories so the tests verify that placeholder metadata persists through new snapshots.

## Dependencies And Integration Points
Uses `localfs`, `restore`, `snapshot`, `repo/object`, `ospath.SafeLongFilename`, `testdirtree`, `clitestutil`, and `testenv`. It integrates snapshot creation, restore, show, and local filesystem behavior, including symlink and long-name handling.

## Risks And Edge Cases
Filesystem behavior is central: path length limits, hard links, symlink timestamp precision, permissions/modes, and platform-specific path separators can affect results. Long directory names are deliberately treated as not safely suffixable. Placeholder validation is strict and can fail when `snapshot.DirEntry` schema or JSON rendering changes. The test uses deep walking and random directory structures, so failures may be noisy without careful path logs.

## Test Signals
High-value signal for shallow restore correctness, especially placeholder encoding, resnapshot fidelity, foreign object rejection, and partial reification semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/shallowrestore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_actions_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_actions_test.go

## Purpose
Tests snapshot action hooks configured through policies: before/after snapshot root actions, before/after folder actions, embedded/persisted scripts, action enablement controls, async/optional/essential modes, timeout behavior, stdout-driven source redirection, environment variables, and ignore-rule handling after action redirection.

## Important APIs, Types, And Functions
- `TestSnapshotActionsBeforeSnapshotRoot` validates action failure stops snapshots in essential mode, optional/async modes do not, timeout kills long-running hooks, and `KOPIA_SNAPSHOT_PATH` redirection is honored only for synchronous hooks.
- `TestSnapshotActionsBeforeAfterFolder` configures per-folder before/after actions and checks inheritance boundaries and action environment values.
- `TestSnapshotActionsEmbeddedScript` uses `--persist-action-script` and validates successful scripts, failing scripts, and redirect scripts.
- `TestSnapshotActionsEnable` tests repository-level `--enable-actions` / `--no-enable-actions` and snapshot-level `--force-enable-actions` / `--force-disable-actions` precedence.
- `TestSnapshotActionsHonorIgnoreRules` verifies `.kopiaignore` is applied in the redirected snapshot directory.
- Helpers include `tmpfileWithContents`, `verifyFileExists`, `mustReadEnvFile`, and `skipUnlessTestAction`.

## Control Flow
Tests require `TESTING_ACTION_EXE`, create a repository with or without action support, set policy action commands, run `snapshot create`, then inspect marker files, env dump files, snapshot object IDs, and listed entries. Hook behavior is driven through a test action executable that can save env, create files, sleep, exit with a code, or emit stdout.

## State And Persistence Behavior
Policies persist action command configuration and command mode/timeouts. Actions mutate filesystem marker/env files and can redirect snapshot source paths through stdout. Snapshot manifests prove whether redirection occurred by comparing root object IDs against known source snapshots.

## Dependencies And Integration Points
Uses `policy set`, `snapshot create`, `snapshot list`, `ls`, `testenv`, `clitestutil`, `snapshot.Manifest`, and the external `TESTING_ACTION_EXE`. Integrates policy inheritance, command execution, environment propagation, snapshot source selection, and ignore rules.

## Risks And Edge Cases
Tests are skipped if the action executable is missing. Async behavior is timing-sensitive and uses elapsed time checks. Windows embedded scripts use different syntax from Unix scripts. Several marker variable names intentionally reuse paths, so diagnosing failures requires reading action env/marker assertions carefully. Hook stdout parsing is a security-sensitive path because it can redirect snapshot roots.

## Test Signals
Strong signal for action policy execution, source-redirection semantics, action enablement precedence, and action environment compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_actions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_copy_move_history_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_copy_move_history_test.go

## Purpose
Verifies `snapshot copy-history` and `snapshot move-history` rewrite snapshot source identity across user, host, and path selectors while preserving snapshot counts.

## Important APIs, Types, And Functions
- `TestSnapshotCopy` creates two snapshots under `user1@host1`, copies history to another user on the same host, copies all host history to a new host, moves selected history to other host selectors, and copies a specific source path to another source path.
- `assertSnapshotCount` lists all snapshots with `-a` and checks exact counts per `snapshot.SourceInfo`.

## Control Flow
The test incrementally performs history copy/move commands and asserts the full expected source set after each step. It uses explicit `SourceInfo` maps to ensure no extra sources remain after move operations and no copies are missing after copy operations.

## State And Persistence Behavior
Snapshot metadata is duplicated or moved between source identities. Underlying object content is not the main concern; manifest source metadata and history grouping are the persisted state under test.

## Dependencies And Integration Points
Uses `testenv`, `clitestutil.ListSnapshotsAndExpectSuccess`, and `snapshot.SourceInfo`. Integrates CLI source selector parsing for `user@host`, `@host`, and `user@host:path` forms.

## Risks And Edge Cases
Source selector parsing is path-sensitive and can vary across platforms if paths contain separators or drive-like syntax. The test assumes copied histories keep exactly two snapshots and move operations remove the old selected source.

## Test Signals
Good regression signal for source history migration/copy features and selector parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_copy_move_history_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_create_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_create_test.go

## Purpose
Covers broad `snapshot create` CLI behavior: normal snapshot/list flows, JSON manifest output, source grouping, tag filtering and validation, checkpoint interval validation, start/end time overrides, cache-directory exclusion, `.kopiaignore` semantics, `--all` behavior, stdin stream snapshots, flush-per-source indexing, source override parsing, and invalid flag combinations.

## Important APIs, Types, And Functions
- `TestSnapshotCreate` creates snapshots across multiple sources, reconnects repositories, validates JSON `snapshot.Manifest` IDs/root entries, tests `--max-results`, and verifies `--ignore-identical-snapshots`.
- `TestTagging` and `TestTaggingBadTags` verify tag filtering and invalid duplicate/malformed tags.
- `TestSnapshotInterval` validates max accepted checkpoint interval.
- `TestStartTimeOverride`, `TestEndTimeOverride`, and `TestInvalidTimeOverride` verify time parsing and ordering.
- `TestSnapshottingCacheDirectory` confirms cache marker directories snapshot as empty.
- `TestSnapshotCreateWithIgnore` is a table-driven `.kopiaignore` suite covering recursive ignores, negation, rooted/unrooted rules, multiple ignore files, comments, trailing spaces, and empty directories.
- `TestSnapshotCreateWithStdinStream` snapshots a stdin stream as a named file and restores it.
- `TestSnapshotCreateAllFlushPerSource`, `TestSnapshotCreateAllSnapshotPath`, and `TestSnapshotCreateWithAllAndPath` verify `--all` flush counts, manual policies from overridden sources, path normalization, and invalid `--all` plus path.
- Helpers include `appendIfMissing`, `testFileEntry`, and `createFileStructure`.

## Control Flow
Each test creates a temporary filesystem repo, runs CLI operations, and inspects either human output line counts or JSON outputs parsed with `testutil.MustParseJSONLines`. Ignore-rule tests synthesize directory trees, snapshot them, recursively list repository entries from root object IDs, expand expected directory paths, sort, and compare.

## State And Persistence Behavior
Persists snapshot manifests, source policies, global policies, content/index metadata blobs, cache marker state, and manual scheduling policies. `--stdin-file` creates a synthetic snapshot root containing streamed content. `--flush-per-source` is validated by counting index blobs and metadata blobs before and after `--all`.

## Dependencies And Integration Points
Uses `cli.SnapshotManifest`, `snapshot.Manifest`, `policy.TargetWithPolicy`, `cachedir.CacheDirMarkerFile`, `clitestutil`, `testenv`, `testutil`, and shared data dirs. It integrates CLI parsing, repository content/index storage, ignore evaluation, policy storage, and restore.

## Risks And Edge Cases
Large table-driven ignore tests are sensitive to path normalization and directory inclusion rules. `TestSnapshotCreateAllSnapshotPath` has platform-specific Windows path expectations. `TestSnapshotCreateWithStdinStream` depends on runner stdin plumbing and exact byte restoration. Line-count assertions can be brittle if user-facing CLI output formatting changes.

## Test Signals
High coverage for core snapshot creation UX and repository-side effects. Strong signal for ignore rules, policy side effects, JSON output contracts, and `--all` batching behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_delete_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_delete_test.go

## Purpose
Tests snapshot deletion commands, dry-run behavior, manifest type safety, restore behavior after deletion, garbage collection interaction, and deleting all snapshots for a source.

## Important APIs, Types, And Functions
- `deleteArgMaker` abstracts command construction for manifest removal, dry-run delete, actual delete, legacy unsafe source flag, object ID delete, and invalid ID cases.
- `TestSnapshotDelete` iterates delete argument variants through `testSnapshotDelete`.
- `TestSnapshotDeleteTypeCheck` ensures non-snapshot manifests such as policy/maintenance cannot be deleted via `snapshot delete`.
- `TestSnapshotDeleteRestore` verifies restore by root ID works before deletion, restore by snapshot ID fails after deletion, repeated deletion fails, and root object restoration remains possible after full maintenance.
- `TestDeleteAllSnapshotsForSource` validates dry-run versus actual `--all-snapshots-for-source` deletion and nonexistent source failures.
- `assertEmptyDir` verifies failed restore leaves target empty.

## Control Flow
Tests create temp data, snapshot it, list snapshots, execute deletion commands, and assert success/failure per scenario. Restore tests compare source and restored directories before deletion, then check snapshot-ID restore failure and root-ID restore success after maintenance.

## State And Persistence Behavior
Deletes snapshot manifests or snapshot metadata while content may remain recoverable by root object ID. Maintenance can garbage-collect unreachable content but deleted root IDs remain restorable in the tested path. All-source deletion changes multiple snapshot manifests for a source atomically from the user's perspective.

## Dependencies And Integration Points
Uses `testenv`, `clitestutil`, `testdirtree`, `testutil`, and shared `compareDirs`. Integrates manifest listing/removal, snapshot delete, restore, and maintenance.

## Risks And Edge Cases
The distinction between manifest ID, object ID, snapshot ID, and root object ID is subtle and security-sensitive. Output field parsing in `TestSnapshotDeleteTypeCheck` assumes `manifest ls` column ordering. Restore-after-delete behavior intentionally distinguishes snapshot manifest availability from content root recoverability.

## Test Signals
Strong signal for deletion safety, dry-run semantics, type checks, and post-delete recovery behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_fail_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_fail_test.go

## Purpose
Validates snapshot failure handling around permission errors, fail-fast behavior, ignored file/dir errors, partial snapshot reporting, JSON output accounting, and environment/flag overrides.

## Important APIs, Types, And Functions
- `TestSnapshotNonexistent` checks missing source failure.
- `TestSnapshotFail_Default`, `TestSnapshotFail_DefaultJSONOutput`, `TestSnapshotFail_EnvOverride`, `TestSnapshotFail_NoFailFast`, and `TestSnapshotFail_FailFast` run the same permission matrix with different fail-fast and output modes.
- `expectedSnapshotResult`, `parsedSnapshotResult`, `testSnapshotFail`, `testSnapshotFailCases`, and `testPermissions` define expected success/error/partial outcomes.
- `createSimplestFileTree` creates deterministic nested dirs/files/empty dirs.
- `parseSnapshotResultFromLog` parses stderr using regexes for created snapshot, fatal error count, ignored error count, and partial status.
- `parseSnapshotResultJSON` extracts the same fields from `snapshot.Manifest` JSON.

## Control Flow
Tests skip on Windows and root, then create nested directory trees and iterate combinations of `--ignore-dir-errors`, `--ignore-file-errors`, permission modes, and snapshot source/modified entry relationships. Each subtest changes permissions, runs snapshot create, optionally restores successful snapshots, then validates parsed result counters.

## State And Persistence Behavior
Persists policies for ignore-file/dir behavior per source and snapshot manifests, including partial/incomplete metadata and root directory summary counters. The test carefully restores original permissions through cleanup to avoid undeletable temp trees.

## Dependencies And Integration Points
Uses `snapshot.Manifest`, `testenv`, `testdirtree`, `testutil`, OS permission bits, environment variable `KOPIA_SNAPSHOT_FAIL_FAST`, and CLI flags. Integrates filesystem permission errors, policy inheritance, CLI logging, JSON manifest summaries, and restore.

## Risks And Edge Cases
Platform and user identity are major constraints: the suite skips on Windows and root. Permission semantics differ across filesystems, and random `inherit` selection introduces minor non-determinism in case names/configuration. Regexes are coupled to CLI log text, while JSON parsing is coupled to manifest summary fields.

## Test Signals
High signal for error accounting and fail-fast behavior, especially consistency between text output and JSON output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_fail_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_gc_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_gc_test.go

## Purpose
Tests that unreferenced snapshot content is collected only when maintenance safety permits it, across repository format versions.

## Important APIs, Types, And Functions
- `TestSnapshotGC` is a method on `formatSpecificTestSuite`, so it runs for format v1/v2/v3 via `suite_test.go`.
- Uses `content list`, `snap create`, `snap list -m`, `manifest rm`, `snapshot verify`, and `maintenance run --full` with `--safety=full` and `--safety=none`.

## Control Flow
The test records initial content count, creates a one-file snapshot, expects three new content items, removes snapshot manifests by parsing `snap list -m`, verifies snapshots, runs safe maintenance and checks content count remains unchanged, waits two seconds, then runs unsafe maintenance and expects two content items removed.

## State And Persistence Behavior
Manipulates content blobs, snapshot manifests, and maintenance-generated manifests. Safety mode and object age determine garbage collection eligibility.

## Dependencies And Integration Points
Uses `repo/content.Info`, `testutil.MustParseJSONLines`, `testenv`, and format-specific repository flags. Integrates manifest deletion, snapshot verification, content listing, and maintenance GC.

## Risks And Edge Cases
The test relies on content count deltas and a sleep to get past age boundaries. If content packing/indexing changes, exact counts may need adjustment. Manifest output parsing searches for `manifest:` in human output.

## Test Signals
Good signal for GC safety semantics and format-version compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_gc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_migrate_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_migrate_test.go

## Purpose
Tests `snapshot migrate` between repositories, including snapshot/policy count preservation, idempotence, compression effects, overwrite policies, parallel migration, and applying destination ignore rules.

## Important APIs, Types, And Functions
- `TestSnapshotMigrate` creates source snapshots/policies, adds compressible test data, migrates all snapshots to a destination repo with `--parallel=5 --overwrite-policies`, verifies counts, reruns migration as a no-op, and compares destination repository size against source.
- `TestSnapshotMigrateWithIgnores` sets an ignore policy on destination, migrates with `--apply-ignore-rules`, and verifies ignored files are omitted.
- `writeCompressibleFile` creates large repeated UUID-derived content to test compression during migration.

## Control Flow
The tests create separate `CLITest` environments sharing a runner, use the source config path as `--source-config`, then inspect destination snapshots/policies and object listing. The compression test records repository directory sizes before/after migration.

## State And Persistence Behavior
Migrates snapshot manifests, policies, content, and compressed object data between independent filesystem repositories. Destination policies can alter migrated content when ignore rules are applied.

## Dependencies And Integration Points
Uses `cli.SnapshotManifest`, `testenv`, `testutil`, `uuid`, filesystem repository storage, and format-specific suite flags.

## Risks And Edge Cases
Repository size comparison is approximate and may be affected by packing/indexing overhead. Idempotence relies on duplicate detection. Ignore-rule migration tests depend on destination policy lookup for the original source path.

## Test Signals
Strong integration signal for migration correctness, idempotence, policy copy/overwrite, and compression/ignore interactions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_migrate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_verify_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_verify_test.go

## Purpose
Verifies `snap verify` succeeds on a healthy snapshot and fails after deleting a referenced pack blob.

## Important APIs, Types, And Functions
- `TestSnapshotVerifyTest` creates a repository, snapshots shared data, runs `snap verify`, removes the first blob whose ID starts with `p`, and expects verification failure.

## Control Flow
The test lists blobs, selects a pack blob by prefix, deletes it, then reruns verification.

## State And Persistence Behavior
Directly corrupts repository blob storage by removing a pack blob while leaving snapshot metadata in place.

## Dependencies And Integration Points
Uses `testenv`, blob CLI commands, and format-specific suite flags.

## Risks And Edge Cases
Assumes a `p` blob exists and is referenced by snapshot content rather than snapshot metadata. Blob naming scheme changes could break selection.

## Test Signals
Simple high-signal corruption detection test for snapshot verification.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/snapshot_verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/suite_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/suite_test.go

## Purpose
Defines a parameterized test suite that runs selected end-to-end tests against Kopia repository format versions 1, 2, and 3.

## Important APIs, Types, And Functions
- `formatSpecificTestSuite` holds `formatFlags` and `formatVersion`.
- `TestFormatV1`, `TestFormatV2`, and `TestFormatV3` call `testutil.RunAllTestsWithParam` with `--format-version=1`, `2`, and `3` respectively.

## Control Flow
The parameterized runner discovers methods on `formatSpecificTestSuite` such as `TestSnapshotGC`, `TestSnapshotMigrate`, and `TestSnapshotVerifyTest`, running them for each configured format.

## State And Persistence Behavior
No direct repository mutation in this file; it passes format flags into tests that create their own repositories.

## Dependencies And Integration Points
Uses `internal/testutil` and `repo/format`. It is an integration point between suite-level parameterization and individual method-based tests.

## Risks And Edge Cases
Adding a method to `formatSpecificTestSuite` implicitly multiplies it across all formats. Tests must tolerate older format semantics or explicitly gate behavior.

## Test Signals
Ensures format-version coverage for method-based end-to-end tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/endurance_test/endurance_test.go -->
# sources/sync-backup/kopia/tests/endurance_test/endurance_test.go

## Purpose
Runs a long randomized endurance scenario against a WebDAV repository with fake time, multiple independent runners, concurrent snapshot/verify/maintenance actions, and clock jumps simulating two weeks of operation.

## Important APIs, Types, And Functions
- `webdavDirWithFakeClock` wraps `webdav.Dir` and adjusts write mtimes to fake server time.
- `TestEndurance` starts a fake time HTTP server, a WebDAV server, creates a WebDAV repo, and launches three parallel runners.
- `runnerState`, `action`, `actionInfo`, and `actions` define weighted operations.
- Action functions snapshot existing sources, snapshot all, verify snapshots/content, run maintenance, jump fake clock, add sources, and mutate directory trees.
- `pickRandomEnduranceTestAction`, `enduranceRunner`, and `runOneIterationUsingLock` drive weighted randomized execution with shared locks for exclusive actions.

## Control Flow
The test initializes fake time at `2000-01-01` and advances until two simulated weeks pass. Each runner connects to the same WebDAV repo under a distinct username, adds at least one source, then repeatedly selects weighted actions. Exclusive actions acquire a write lock; non-exclusive actions acquire a read lock. Any runner failure increments `failureCount`, causing other runners to stop early.

## State And Persistence Behavior
Persists repository data in a temp WebDAV-backed filesystem, modifies source directories, advances fake repository/server time, writes snapshot manifests, content, and maintenance records. Runner-local source directory lists are kept in memory, while repository data is shared.

## Dependencies And Integration Points
Uses `faketime`, `testenv.FakeTimeServer`, `webdav`, `testdirtree`, CLI executable runner, fake clock env var `KOPIA_FAKE_CLOCK_ENDPOINT`, and WebDAV repository storage.

## Risks And Edge Cases
Randomized action selection and fake-time jumps make failures potentially non-reproducible unless logs are preserved. WebDAV file mtime manipulation relies on concrete `*os.File` returned by `webdav.Dir`. Test duration is potentially long because fake time advances via weighted actions, not wall-clock deadlines.

## Test Signals
Broad stress signal for repository consistency under time advancement, maintenance, concurrent clients, and repeated snapshot/verify operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/endurance_test/endurance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/htmlui_e2e_test/context_test.go -->
# sources/sync-backup/kopia/tests/htmlui_e2e_test/context_test.go

## Purpose
Provides small `chromedp` helper context for HTML UI end-to-end tests: expected dialog handling state, logging actions, download completion wait, and screenshot capture.

## Important APIs, Types, And Functions
- `TestContext` stores `testing.T`, screenshot counter/path, expected dialog text/response, and a download completion channel.
- `expectDialogText` records the next expected JavaScript dialog text and response value.
- `log` wraps `t.Log` as a chromedp action.
- `waitForDownload` blocks on `downloadFinished` or times out.
- `captureScreenshot` writes numbered PNG screenshots under `screenshotsDir`.

## Control Flow
Each helper returns a `chromedp.ActionFunc` so UI tests can compose logging, dialog setup, download waiting, and screenshots inside `chromedp.Run`.

## State And Persistence Behavior
Persists screenshots to disk and tracks per-test screenshot numbering in memory. Dialog expectations are mutable test state read by the `chromedp.ListenTarget` callback in `htmlui_e2e_test.go`.

## Dependencies And Integration Points
Uses `chromedp`, `pkg/errors`, and the parent UI e2e runner. Screenshot paths are set by `runInBrowser`.

## Risks And Edge Cases
Dialog expectation state is mutable and not protected by a mutex, but tests run one browser flow per context. Download wait depends on browser events being enabled before clicking the downloadable link.

## Test Signals
Provides support signal for browser e2e diagnostics and failure artifacts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/htmlui_e2e_test/context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/htmlui_e2e_test/htmlui_e2e_test.go -->
# sources/sync-backup/kopia/tests/htmlui_e2e_test/htmlui_e2e_test.go

## Purpose
Runs opt-in browser end-to-end tests for Kopia HTML UI: repository creation, snapshot creation, snapshot browsing/download, connect/reconnect forms, theme switching, and byte-size representation preferences.

## Important APIs, Types, And Functions
- `runInBrowser` gates tests on `HTMLUI_E2E_TEST`, starts `kopia server start --ui`, configures `chromedp`, listens for JavaScript dialogs and download events, then runs a test callback.
- `createTestSnapshot` drives the UI to create a filesystem repository, estimate a new snapshot, create it, and return to the snapshot list.
- `TestEndToEndTest` browses snapshots and downloads an object.
- `TestConnectDisconnectReconnect` validates password mismatch dialog and repository setup path; disconnect portions are skipped due to timeout.
- `TestChangeTheme` cycles through `light`, `pastel`, `dark`, `ocean`, and back to `light`.
- `TestByteRepresentation` toggles base-2/base-10 byte preferences and checks displayed values.
- `TestPagination` is explicitly skipped.

## Control Flow
The test starts a local server with insecure/no-password settings for browser convenience, optionally points at `HTMLUI_BUILD_DIR`, configures screenshots under `../../.screenshots/htmlui-e2e-test/<test>`, launches Chrome headless in CI, navigates by `data-testid` selectors, and captures screenshots after key steps.

## State And Persistence Behavior
Creates filesystem repositories, source files including a 10 MB sparse/truncated file, UI preferences, screenshots, downloaded files, and browser state. The server process is killed and waited on by deferred callbacks.

## Dependencies And Integration Points
Uses `chromedp`, CDP browser/page events, `testenv`, `testutil.ServerParameters`, Kopia UI selectors, optional `HTMLUI_BUILD_DIR`, and env gates `HTMLUI_E2E_TEST`, `HTMLUI_TEST_PAUSE`, and `CI`.

## Risks And Edge Cases
Highly sensitive to UI selector changes, browser availability, timing, and CI headless behavior. The server flags combine `--insecure` and `--without-password`; this is test-only and should not be generalized. Disconnect flows are currently skipped inline due to timeout, reducing coverage.

## Test Signals
Opt-in high-level signal for critical UI workflows and visual/debug artifacts through screenshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/htmlui_e2e_test/htmlui_e2e_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_nonwindows_test.go -->
# sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_nonwindows_test.go

## Purpose
Defines the non-Windows side of the `os_snapshot_test` package with a build tag excluding Windows.

## Important APIs, Types, And Functions
No runtime code beyond package declaration.

## Control Flow
The `//go:build !windows` tag ensures this file participates on non-Windows platforms so the package exists even though Windows-specific shadow-copy tests are excluded.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Serves build-system/package compatibility for `tests/os_snapshot_test`.

## Risks And Edge Cases
If additional non-Windows tests are expected, this file currently provides no assertions.

## Test Signals
No behavioral test signal; build/package placeholder only.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_nonwindows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_windows_test.go -->
# sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_windows_test.go

## Purpose
Tests Windows Volume Shadow Copy behavior for locked files when Kopia policy enables volume shadow copy.

## Important APIs, Types, And Functions
- `TestShadowCopy` requires `KOPIA_EXE`, creates a filesystem repo, enables `--enable-volume-shadow-copy=when-available`, creates an auto-delete locked file, checks admin/VSS permission, then expects snapshot success as admin or failure as non-admin.
- `createAutoDelete` uses Windows `CreateFile` with `FILE_FLAG_DELETE_ON_CLOSE` and no sharing to create a locked file.

## Control Flow
The test uses the external Kopia binary runner, writes and syncs a locked file, calls `vss.Get` to infer administrative access, snapshots the directory, lists snapshots and root entries, and validates content visibility depending on admin status.

## State And Persistence Behavior
Persists a temporary filesystem repository and a snapshot manifest. The locked file is deleted on close through Windows file-handle semantics.

## Dependencies And Integration Points
Uses `github.com/mxk/go-vss`, `golang.org/x/sys/windows`, `syscall`, `testenv.NewExeRunnerWithBinary`, `clitestutil`, and `KOPIA_EXE`.

## Risks And Edge Cases
Windows-only and depends on admin privileges and VSS availability. Non-admin expectations still require a snapshot/source listing path to exist. Locked-file behavior is specific to Windows handle flags.

## Test Signals
Important platform signal for VSS integration and fallback behavior around inaccessible files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark-setup.sh -->
# sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark-setup.sh

## Purpose
Prepares a Linux benchmark host by installing tools and formatting/mounting a data device for Kopia performance benchmarks.

## Important APIs, Types, And Functions
Shell script with `set -e`; installs `fio` and `python3-pip`, installs Python `psrecord`, formats `/dev/nvme0n1` as ext4, mounts it at `/mnt/data`, and changes ownership to `$USER`.

## Control Flow
Commands run sequentially and abort on first failure. There is no argument parsing or safety confirmation.

## State And Persistence Behavior
Destructively formats `/dev/nvme0n1`, creates `/mnt/data`, mounts it, and changes ownership.

## Dependencies And Integration Points
Depends on Debian/Ubuntu-style `apt`, `pip3`, root/sudo privileges, and a benchmark environment where `/dev/nvme0n1` is safe to wipe.

## Risks And Edge Cases
Very high destructive risk if run on the wrong machine. The script assumes device name and mount point, does not check existing mounts, and uses system Python package installation.

## Test Signals
Operational setup artifact rather than a test; it supports reproducible benchmark environments.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark.sh -->
# sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark.sh

## Purpose
Runs Kopia performance benchmark scenarios for a specified package version/channel and total source size, collecting `psrecord` CPU/RAM logs and repository size logs.

## Important APIs, Types, And Functions
Shell variables `VERSION`, `CHANNEL`, `TOTAL_SIZE`, and `fio_opts` configure the run. The script installs Kopia from the Kopia APT repository, then loops over compressed/uncompressed scenarios with 10/100/1000 files.

## Control Flow
For each scenario, it clears `/mnt/data/{repo,cache,source}`, creates a repo, generates test files with `fio`, optionally enables `s2-default` compression, records an initial snapshot with `psrecord`, clears cache, reconnects, records a second snapshot, and writes `du -bs` repository size output.

## State And Persistence Behavior
Mutates system APT sources, installs/downgrades Kopia, repeatedly removes benchmark data under `/mnt/data`, creates repository/cache/source trees, and writes `psrecord-...log` and `repo-size-...log` files in the current directory.

## Dependencies And Integration Points
Depends on `curl`, `apt-key`, `apt`, `fio`, `psrecord`, `sudo`, `/mnt/data`, and Kopia CLI package repositories.

## Risks And Edge Cases
The cache clear lines use `/mnt/data/cache}` with an extra `}`, likely clearing/creating the wrong path and leaving `/mnt/data/cache` intact. That can invalidate second-run cold-cache measurements. The script assumes APT repository availability and has broad destructive `rm -rfv` operations under `/mnt/data`.

## Test Signals
Produces benchmark logs for throughput/resource comparison rather than pass/fail tests. Output is consumed by `process_results.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/perf_benchmark/process_results.go -->
# sources/sync-backup/kopia/tests/perf_benchmark/process_results.go

## Purpose
Parses benchmark output logs and emits CSV-style rows containing scenario, version, duration, CPU/RAM averages/maxima, and repository size.

## Important APIs, Types, And Functions
- Regexes `psrecordRegex` and `reposizeRegex` match `psrecord-<version>-(initial|second)-<scenario>.log` and `repo-size-<version>-<scenario>.log`.
- `processStats` stores duration, average/max CPU, and average/max RAM.
- `getProcessStats` scans psrecord logs, skipping the header and aggregating timestamp/CPU/RAM fields.
- `parseRepoSize` reads the first field from `du -bs` output.
- `main` scans current directory, stores only initial phase process stats, stores repo sizes, and prints CSV lines.

## Control Flow
The program walks `os.ReadDir(".")`, parses recognized files, populates nested maps by scenario/version, then prints one row per initial-process result with the matching repo size.

## State And Persistence Behavior
Read-only over current directory logs. Results are held in package-level maps and written to stdout.

## Dependencies And Integration Points
Depends on benchmark log naming from `perf-benchmark.sh`, psrecord text format with at least three whitespace fields per sample line, and `du -bs` output.

## Risks And Edge Cases
`repoSizeByScenarioArndVersion` contains a typo in the variable name but works. `getProcessStats` assumes every data line has enough fields; malformed or empty lines can panic. It ignores `second` phase psrecord logs entirely. Missing repo-size entries print zero without error because map lookup defaults to zero.

## Test Signals
Useful post-processing utility for benchmark artifacts; not a test itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/perf_benchmark/process_results.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/recovery/blobmanipulator/blobmanipulator.go -->
# sources/sync-backup/kopia/tests/recovery/blobmanipulator/blobmanipulator.go

## Purpose
Provides a recovery-test helper for creating repositories, generating random data, deleting/corrupting blobs, restoring snapshots, running maintenance, and invoking `snapshot fix` commands.

## Important APIs, Types, And Functions
- `BlobManipulator` holds a `kopiarunner.KopiaSnapshotter`, `snapmeta.KopiaSnapshotter`, optional `fiofilewriter.FileWriter`, repo path, maintenance flag, and current snapshot path.
- `NewBlobManipulator` creates command runner and metadata snapshotter; `getSnapshotter` skips/returns nil when `KOPIA_EXE` is missing.
- `ConnectOrCreateRepo`, `TakeSnapshot`, `DeleteSnapshot`, `VerifySnapshot`, and `RunMaintenance` wrap Kopia CLI operations.
- `DeleteBlob` and `getBlobIDRand` delete a named or first pack (`p`) blob.
- `writeRandomFiles`, `SetUpSystemUnderTest`, `SetUpSystemWithOneSnapshot`, and `GenerateRandomFiles` create test data via FIO.
- `RestoreGivenOrRandomSnapshot` restores a provided or random snapshot ID and returns stderr text on error for later parsing.
- `SnapshotFixRemoveFilesByBlobID`, `SnapshotFixRemoveFilesByFilename`, and `SnapshotFixInvalidFiles` invoke repair commands with `--commit`.

## Control Flow
Recovery tests instantiate `BlobManipulator`, set `DataRepoPath`, generate files/snapshots, optionally delete blobs or snapshots, run maintenance, attempt restores, parse failures, and run fix commands. Blob selection lists repository blobs in JSON and selects the first pack blob.

## State And Persistence Behavior
Creates and mutates filesystem Kopia repositories, writes random file trees through FIO, stores snapshots, deletes snapshots/blobs, and runs full maintenance with `--safety none`. `PathToTakeSnapshot` tracks the current FIO data directory for later snapshot calls.

## Dependencies And Integration Points
Uses `tests/robustness` interfaces, `fiofilewriter`, `snapmeta`, `kopiarunner`, `tests/tools/fio`, `repo/blob.Metadata`, and `snapshot.Manifest`.

## Risks And Edge Cases
`ConnectOrCreateRepo(dataRepoPath string)` ignores its parameter and uses `bm.DataRepoPath`, so callers must set the struct field correctly. `NewBlobManipulator` can return `(nil, nil)` when the snapshotter is unavailable; callers must handle nil. Random snapshot selection assumes non-empty snapshot lists. Blob deletion assumes a pack blob exists.

## Test Signals
Enables corruption/recovery tests with realistic CLI and repository operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/recovery/blobmanipulator/blobmanipulator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/recovery/recovery_test/main_test.go -->
# sources/sync-backup/kopia/tests/recovery/recovery_test/main_test.go

## Purpose
Defines recovery test process setup, build constraints, shared repo-path constants, and `KOPIA_EXE` gating.

## Important APIs, Types, And Functions
- Build tag restricts tests to Darwin or Linux amd64.
- Constants `dataSubPath`, `dirPath`, and `dataPath` define repository subpaths.
- `repoPathPrefix` flag allows placing recovery repositories under a caller-provided prefix.
- `TestMain` initializes a `kopiaRecoveryTestHarness` and then runs tests.
- `kopiaRecoveryTestHarness.init` exits successfully when `KOPIA_EXE` is absent.

## Control Flow
Before tests run, `TestMain` builds the default data repo path and checks for `KOPIA_EXE`. If missing, it logs and exits with status 0, effectively skipping the package.

## State And Persistence Behavior
No direct repository mutation beyond path selection and harness state.

## Dependencies And Integration Points
Uses `flag`, `os`, and package-level recovery tests that rely on external Kopia binary execution.

## Risks And Edge Cases
Exiting 0 from `TestMain` can hide accidental misconfiguration if a caller expected recovery tests to run. Path constants are shared assumptions for tests in `recovery_test.go`.

## Test Signals
Provides environment gating for binary-dependent recovery tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/recovery/recovery_test/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/recovery/recovery_test/recovery_test.go -->
# sources/sync-backup/kopia/tests/recovery/recovery_test/recovery_test.go

## Purpose
Exercises recovery behavior after blob deletion, killed maintenance/snapshot processes, snapshot-fix repair commands, and crash consistency after interrupting a snapshot.

## Important APIs, Types, And Functions
- `TestSnapshotFix` sets up snapshots, starts and quickly kills maintenance, deletes a random blob, runs full maintenance, confirms restore fails, extracts object ID from the error, runs `snapshot fix remove-files --object-id`, then restores successfully.
- `TestSnapshotFixInvalidFiles` similarly corrupts a repository and repairs with `snapshot fix invalid-files --verify-files-percent=100`.
- `TestConsistencyWhenKill9AfterModify` creates a baseline snapshot, adds files, connects repo, starts `snap create --json --parallel=1`, kills it when progress indicates hashing/uploading, verifies repository consistency, restores a random snapshot, and compares with baseline data.
- `killOnCondition` monitors stderr and kills the command after snapshot progress starts.
- `CompareDirs` uses `internal/diff` over `localfs` entries.
- `getBlobIDToBeDeleted` parses restore error text for an object ID after `unable to open object`.

## Control Flow
Tests use `blobmanipulator` to prepare data and run high-level operations, then directly spawn external `KOPIA_EXE` commands for maintenance/snapshot interruption. Repair tests intentionally induce corruption and then verify recovery paths by attempting restores before and after fixes.

## State And Persistence Behavior
Uses persistent filesystem repository paths under `repoPathPrefix`, writes large random datasets, deletes pack blobs, deletes snapshots, runs maintenance with no safety, and stores/restores snapshot metadata. Crash-consistency test mutates source data and ensures interrupted writes do not corrupt existing snapshots.

## Dependencies And Integration Points
Depends on `KOPIA_EXE`, FIO availability through `blobmanipulator`, `kopiarunner`, `testenv.TestRepoPassword`, `internal/diff`, `localfs`, and OS process control.

## Risks And Edge Cases
Timing is intentionally racy: maintenance is killed after 10 ms, and snapshot kill depends on matching progress text containing `hashing`, `hashed`, and `uploaded`. Error parsing in `getBlobIDToBeDeleted` is coupled to human error text. Tests can be expensive due to 40 MB and 200 MB-scale random file generation.

## Test Signals
High-value recovery/crash-consistency signal for repair commands and repository robustness after abrupt process death.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/recovery/recovery_test/recovery_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/open_repository_model.go -->
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/open_repository_model.go

## Purpose
Models the view of a repository opened by one logical client in repository stress tests.

## Important APIs, Types, And Functions
- `OpenRepository` stores a pointer to shared `RepositoryData`, per-open readable content/manifest sets, an `EnableMaintenance` flag, and an `openID`.
- `Refresh` replaces readable sets from committed content/manifest snapshots.
- `NewSession` creates a `RepositorySession` with per-session written content/manifest tracking sets.

## Control Flow
Stress tests call `RepositoryData.OpenRepository` before opening a real repository. Each open repository then creates sessions whose writes are tracked until flushed or refreshed.

## State And Persistence Behavior
In-memory model only. `ReadableContents` and `ReadableManifests` represent what this open repository should be able to see based on refresh/flush events.

## Dependencies And Integration Points
Uses `content.ID`, `manifest.ID`, and repository stress test logic. Logging is module-scoped via `logging.Module("repomodel")`.

## Risks And Edge Cases
`Refresh` accesses `TrackingSet.ids` directly from snapshot sets; this works within the package but assumes no concurrent mutation of those snapshot objects. Model correctness is critical because real repository errors are judged against this expected visibility model.

## Test Signals
Supports stress-test validation of repository visibility across open connections.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/open_repository_model.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_data_model.go -->
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_data_model.go

## Purpose
Models repository-wide committed content and manifest IDs for repository stress tests.

## Important APIs, Types, And Functions
- `RepositoryData` holds `CommittedContents`, `CommittedManifests`, and an atomic `openCounter`.
- `OpenRepository` returns an `OpenRepository` whose readable sets snapshot the current committed sets and whose first opener receives `EnableMaintenance=true`.
- `NewRepositoryData` initializes committed tracking sets and the open counter.

## Control Flow
The stress harness creates one `RepositoryData` shared by all logical repository opens. Each real repo open obtains a model snapshot by calling `OpenRepository`.

## State And Persistence Behavior
In-memory state tracks committed IDs after modeled flushes. It does not persist to disk; persistence is in the real repository being stress-tested.

## Dependencies And Integration Points
Uses `content.ID`, `manifest.ID`, `TrackingSet`, and `sync/atomic`.

## Risks And Edge Cases
The model grants maintenance to only the first open repository using an atomic increment; if the test expects multiple maintenance-capable clients, this would under-model. Snapshot timing around open/real repo open is intentionally ordered in the stress test to avoid seeing writes that happen between model and real open.

## Test Signals
Central expected-state model for repository stress tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_data_model.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_session_model.go -->
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_session_model.go

## Purpose
Models a single writer session in repository stress tests, tracking pending writes and publishing them to open/shared readable sets after flush.

## Important APIs, Types, And Functions
- `RepositorySession` holds its `OpenRepo`, `WrittenContents`, and `WrittenManifests`.
- `WriteContent` and `WriteManifest` add IDs to pending session sets.
- `Refresh` delegates to the open repository to replace readable sets.
- `Flush` adds captured pending IDs to open-readable and repository-committed sets, then removes them from pending sets.

## Control Flow
Real write actions call `WriteContent`/`WriteManifest` after successful repository writes. Before flushing, stress code snapshots pending sets, flushes the real repository, then calls `Flush` with the captured sets so only definitely flushed items become visible.

## State And Persistence Behavior
In-memory expected-state transitions mirror repository flush semantics. `Flush` uses `OpenRepo.mu` to update readable and committed sets consistently.

## Dependencies And Integration Points
Uses `content.ID`, `manifest.ID`, and `TrackingSet`.

## Risks And Edge Cases
Correctness depends on capturing pending sets before real flush, because other goroutines may add more pending writes concurrently. The model intentionally does not publish writes added during the flush unless included in the captured sets.

## Test Signals
Supports validation of pending versus flushed read behavior under concurrency.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_session_model.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/tracking_set.go -->
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/tracking_set.go

## Purpose
Implements a small generic, mutex-protected tracking set used by repository stress models to store content and manifest IDs.

## Important APIs, Types, And Functions
- `TrackingSet[T]` stores a slice of comparable IDs and a set ID for logging.
- `PickRandom` returns a random element or the zero value.
- `Snapshot` copies the current IDs into a new tracking set.
- `Replace`, `Add`, `RemoveAll`, and `Clear` mutate the stored IDs.
- `removeAll` filters a slice using `slices.Contains`.
- `NewChangeSet` creates a named tracking set.

## Control Flow
Stress tests and model code use tracking sets to pick readable/pending IDs and to publish/remove IDs during refresh/flush operations.

## State And Persistence Behavior
In-memory only. The implementation behaves like a bag rather than a strict deduplicating set: `Add` appends without checking for duplicates.

## Dependencies And Integration Points
Uses `context`, `math/rand`, `slices`, and package logger.

## Risks And Edge Cases
Because it stores a slice with no deduplication, duplicate IDs can be picked or removed together. `removeAll` is O(n*m), acceptable for stress scale but not general use. `Snapshot` copies IDs under lock, but callers inside the same package sometimes read `ids` directly from snapshot objects.

## Test Signals
Foundational support for stress-test expected state; bugs here can create false positives or false negatives.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repomodel/tracking_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repository_stress_test.go -->
# sources/sync-backup/kopia/tests/repository_stress_test/repository_stress_test.go

## Purpose
Runs randomized concurrent repository stress tests over direct repository APIs, mixing content writes/reads, manifest writes/reads, listing, flush, refresh, and compaction across multiple configs, open repositories, sessions, and workers.

## Important APIs, Types, And Functions
- `StressOptions` controls number of configs/open repositories/sessions/workers and action weights.
- Test entry points `TestStressRepositoryMixAll`, `TestStressRepositoryRandomMix`, `TestStressRepositoryManifests`, `TestStressContentWriteHeavy`, and `TestStressContentReadHeavy` configure weighted scenarios.
- `runStress` gates on `KOPIA_STRESS_TEST`, initializes filesystem storage/repository, creates multiple config/cache files, starts worker goroutines, and runs for 10 or 120 seconds depending on CI context.
- `longLivedRepositoryTest` opens a repository, creates direct writers per session, and starts worker loops.
- `repositoryTest` roulette-selects actions until stopped.
- Actions implement random content write/read, list/read all, compact indexes, flush, refresh, read/write manifests.

## Control Flow
The harness creates one physical repository and multiple connected configs. For each config/open/session/worker, goroutines execute random actions. The in-memory `repomodel` tracks which content/manifests should be visible pending flush, after flush, or after refresh. Errors other than `errSkipped` fail the worker and test.

## State And Persistence Behavior
Mutates a real filesystem-backed repository, config files, cache directories, worker logs, content blobs, index blobs, and manifest metadata. The model state tracks expected visibility transitions for content and manifests.

## Dependencies And Integration Points
Uses low-level `repo` APIs, `repo.DirectRepositoryWriter`, `content`, `manifest`, `indexblob`, filesystem storage, `errgroup`, `testlogging`, `testutil`, and the `repomodel` package.

## Risks And Edge Cases
Random map iteration plus random weights can make failures hard to reproduce. The test is skipped unless `KOPIA_STRESS_TEST` is set and can run longer in non-PR CI. It assumes model semantics match repository consistency semantics; model bugs can mask or invent failures. Shared log file writes from multiple goroutines are not explicitly synchronized.

## Test Signals
Strong concurrency and consistency signal for direct repository writers, flush/refresh visibility, index compaction, and manifest/content read paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/repository_stress_test/repository_stress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/checker/checker.go -->
# sources/sync-backup/kopia/tests/robustness/checker/checker.go

## Purpose
Defines a robustness checker that wraps snapshot creation, restore verification, deletion, and metadata reconciliation for long-running robustness tests.

## Important APIs, Types, And Functions
- `Checker` holds restore directory, `robustness.Snapshotter`, metadata `Store`, recovery mode flag, delete limit, mutex, and `SnapIDIndex`.
- `NewChecker` creates a temp restore directory and reads `LIVE_SNAP_DELETE_LIMIT`.
- `SnapshotMetadata` stores snapshot ID, start/end times, deletion time, and validation fingerprint.
- `VerifySnapshotMetadata` reconciles live snapshot metadata with live snapshots in the repository and optionally repairs in recovery mode.
- `TakeSnapshot` creates a snapshot and saves validation metadata.
- `RestoreSnapshot`, `RestoreSnapshotToPath`, `safeRestorePrepare`, and `RestoreVerifySnapshot` restore and compare data or recover missing metadata.
- `DeleteSnapshot`, `safeDeletePrepare`, and `safeDeleteFinish` mark snapshots deleted while avoiding races with restores.
- `saveSnapshotMetadata` and `loadSnapshotMetadata` persist JSON metadata by snapshot ID.

## Control Flow
Snapshot operations use the snapshotter to create/restore/delete repository snapshots and update metadata indexes under mutexes. Restore prepares by confirming a snapshot is still live, then compares restored data against saved validation fingerprints. Delete removes IDs from the live index before calling repository delete, then records deletion metadata.

## State And Persistence Behavior
Persists snapshot metadata JSON through `robustness.Store`, maintains in-memory `SnapIDIndex` categories for all/live/deleted snapshots, and creates temporary restore directories. In recovery mode it can delete live repository snapshots with missing metadata or rebuild metadata from restored data.

## Dependencies And Integration Points
Uses `robustness.Snapshotter`, `robustness.Store`, `snapmeta.Index`, `internal/clock`, and JSON metadata.

## Risks And Edge Cases
`VerifySnapshotMetadata` is documented as not concurrently safe despite using some locks; external callers must serialize it. Recovery mode deletes repository snapshots without metadata up to `DeleteLimit`, so misconfigured metadata can cause data loss in a test repo. `NewChecker` logs default delete limit if env var is unset or unparsable.

## Test Signals
Core correctness layer for robustness tests, checking snapshot metadata/data integrity and recovery semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/checker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/action.go -->
# sources/sync-backup/kopia/tests/robustness/engine/action.go

## Purpose
Defines the robustness engine action system: executable action keys, weighted random selection, action repetition, logging/stat accounting, no-op handling, no-space recovery, and concrete snapshot/file/GC actions.

## Important APIs, Types, And Functions
- `ExecAction` executes a named action, repeats it according to `repeat-action`, updates stats/logs, and treats `robustness.ErrNoOp` specially.
- `RandomAction` picks an action using control weights and runs recovery handling.
- `CheckErrRecovery` recovers from no-space errors by deleting data, then restoring a snapshot into the data directory.
- Action keys include snapshot, restore random snapshot, delete random snapshot, write random files, delete random subdirectory, delete files, restore into data dir, and run GC.
- Concrete action functions call `Engine.Checker`, `FileWriter`, or `TestRepo`.
- `defaultActionControls`, `pickActionWeighted`, `errIsNotEnoughSpace`, and `getSnapIDOptOrRandLive` support weighted random execution and option parsing.

## Control Flow
Random actions read weights from `ActionOpts[ActionControlActionKey]`, pick a key using reservoir-style weighted selection, execute the action, and then run recovery logic if needed. Concrete actions populate log command options with snapshot IDs, paths, and file-writer outputs.

## State And Persistence Behavior
Actions mutate the data directory, snapshot repository, metadata repository via `Checker`, engine logs, and stats counters. No-space recovery can delete all data-directory contents and restore from a live snapshot.

## Dependencies And Integration Points
Uses `robustness` interfaces, `checker`, file writer APIs, engine stats/log helpers, and option names from fio/file-writer packages.

## Risks And Edge Cases
`ExecAction` indexes `actions[actionKey]` without validating presence; an unknown key will call a nil function and panic. Weighted picking depends on map iteration randomness but produces correct probabilities statistically. No-space detection includes string matching on `"no space left on device"`.

## Test Signals
Central behavioral layer for robustness random tests and recovery-on-error scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/action.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/engine.go -->
# sources/sync-backup/kopia/tests/robustness/engine/engine.go

## Purpose
Constructs and manages the robustness test engine, tying together metadata persistence, snapshot repository, file writer, checker, logging, stats, initialization, and shutdown.

## Important APIs, Types, And Functions
- `Args` contains `MetaStore`, `TestRepo`, `FileWriter`, `WorkingDir`, and `SyncRepositories`; `Validate` enforces required fields.
- `New` creates an `Engine`, initializes run stats, sets up logging, creates a `checker.Checker`, and configures recovery mode.
- `Engine` stores interfaces, checker, cleanup routines, run/cumulative stats, engine log, and mutexes.
- `Shutdown` optionally takes a final snapshot after writes, prints summary, saves logs/stats/snapshot index, flushes metadata, and runs cleanup.
- `setupLogging`, `formatLogName`, `cleanComponents`, and `Init` handle log file setup, cleanup, and persisted metadata loading/reconciliation.

## Control Flow
Engine construction validates dependencies, opens a new persistent log file under the metadata store directory, then creates the checker. `Init` loads persisted metadata, stats, logs, and snapshot index before verifying metadata against the repository. `Shutdown` inspects current-run logs to decide whether a final snapshot is needed, persists state, flushes metadata, and cleans components.

## State And Persistence Behavior
Persists engine logs, stats, and snapshot ID index through `MetaStore`. Also writes a log file to the metadata persist directory and mutates snapshot repository state through final snapshots. Cleanup removes temp restore/file-writer resources via registered cleanup routines.

## Dependencies And Integration Points
Uses `robustness.Persister`, `robustness.Snapshotter`, `robustness.FileWriter`, `checker.NewChecker`, `internal/clock`, and engine log/stats methods defined elsewhere in the package.

## Risks And Edge Cases
`log.SetOutput` is global, so parallel engine tests can interfere with logging. `Shutdown` ignores errors from the final snapshot action. Cleanup runs via defer after persistence; errors before cleanup can still leave external resources if cleanup routines fail.

## Test Signals
Provides lifecycle and persistence backbone for robustness tests, especially restart/recovery behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/engine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/engine_test.go -->
# sources/sync-backup/kopia/tests/robustness/engine/engine_test.go

## Purpose
Tests the robustness engine and checker over filesystem and S3 repositories, including write/snapshot/restore basics, deletion, validation failures, persistence across engine instances, weighted action selection, random action execution, IO limiting, and persisted stats/logs.

## Important APIs, Types, And Functions
- `TestEngineWriteFilesBasicFS`, `TestWriteFilesBasicS3`, and `TestDeleteSnapshotS3` cover basic write/snapshot/restore/delete behavior.
- `makeTempS3Bucket` creates a temporary AWS S3 bucket and cleanup callback using MinIO client and AWS env credentials.
- `TestSnapshotVerificationFail` swaps validation metadata to ensure restore comparison detects mismatch.
- `TestDataPersistency` persists metadata, creates a second engine on the same repos, restores old data, and compares fingerprints.
- `TestPickActionWeighted` statistically validates weighted random action selection.
- `TestActionsFilesystem` and `TestActionsS3` run random engine actions with realistic file-writer options.
- `TestIOLimitPerWriteAction` verifies file writer IO limit caps non-zero bytes written.
- `TestStatsPersist` and `TestLogsPersist` validate metadata persistence for engine stats/logs.
- `testHarness`, `newTestHarness`, `args`, `FioRunner`, and `Cleanup` encapsulate FIO writer, Kopia snapshotter, metadata persister, and engine construction.

## Control Flow
Tests set `snapmeta` mode/bucket env vars, create harnesses, initialize engines, perform writes via FIO, snapshot/restore through `Checker`, and clean up external resources. S3 tests create and remove real buckets when AWS credentials are available. Persistence tests create new persister/engine instances pointed at the same metadata repo and compare loaded state.

## State And Persistence Behavior
Creates filesystem repos under `/tmp/engine/...` or S3 paths, metadata repos, FIO data directories, persisted logs/stats/snapshot indexes, AWS buckets, and temporary local directories. `Cleanup` calls engine shutdown, FIO cleanup, server process SIGTERM when present, snapshotter/persister cleanup, and base-dir removal.

## Dependencies And Integration Points
Depends on `KOPIA_EXE`, FIO environment, AWS credentials for S3 tests, `snapmeta`, `fiofilewriter`, `kopiarunner`, `fswalker`, `minio-go`, and the engine/checker APIs.

## Risks And Edge Cases
S3 tests are external-service dependent and skip without credentials. Some global paths under `/tmp/engine` can collide if tests run concurrently outside their intended cleanup. Statistical weighted test uses 100,000 iterations and a 10 percent tolerance. `randomString` ignores `io.ReadFull` errors. Cleanup sends SIGTERM to a server process if present, which is platform/build-tag limited.

## Test Signals
Comprehensive signal for robustness engine lifecycle, persistence, random action execution, metadata/data validation, and filesystem/S3 backend support.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/engine_test.go -->
