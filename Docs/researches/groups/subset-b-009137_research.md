# subset-b-009137 research

Grouped research report for Kopia Electron UI public/app files and early CLI command files under `sources/sync-backup/kopia`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/electron.js -->
# sources/sync-backup/kopia/app/public/electron.js

## Purpose
Electron main-process entry point for Kopia UI. It owns tray lifecycle, repository BrowserWindow instances, app startup/login handling, native notifications, update checks, release-note launching, dock/tray presentation, and IPC-driven menu refreshes.

## APIs, Types, and Functions
Important APIs include dependencies `electron-updater`, `./utils.js`, `./server.js`, `electron-store`, `electron-log`, `path`, `crypto`; functions `getDisplayConfiguration`, `showRepoWindow`, `checkForUpdates`, `checkForUpdatesNow`, `installUpdate`, `viewReleaseNotes`, `isOutsideOfApplicationsFolderOnMac`, `maybeMoveToApplicationsFolder`, `updateDockIcon`, `showAllRepoWindows`.

## Control Flow, State, and Persistence
Startup initializes single-instance behavior, creates a tray on `app.ready`, loads repository configuration, starts/opens repository windows through `showRepoWindow`, and rebuilds tray menus when server, autostart, or notification state changes. Auto-updater callbacks mutate cached update state and the menu exposes check/download/install actions. State is mainly process-global: `tray`, `repositoryWindows`, `repoIDForWebContents`, update status variables, Electron Store persisted window bounds, last-notified version, and repository credentials passed to server/window helpers. It also persists display-aware window placement and relies on app-data paths for logs.

## Dependencies and Integration
This file integrates with electron-updater, ./utils.js, ./server.js, electron-store, electron-log, path, crypto and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks cluster around stale window/server mappings, persisted bounds outside current displays, update notification duplication, macOS application-folder migration, and credential handling in IPC/window creation. Test hooks in development expose tray/window handles for Playwright coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/electron.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/manifest.json -->
# sources/sync-backup/kopia/app/public/manifest.json

## Purpose
Web app manifest shipped with the React/Electron UI assets. It declares app names, icon files, standalone display mode, start URL, and theme/background colors.

## APIs, Types, and Functions
Important APIs include manifest keys `short_name`, `name`, `icons`, `start_url`, `display`, `theme_color`, and `background_color`.

## Control Flow, State, and Persistence
The file is static JSON consumed by the browser/runtime asset pipeline; there is no executable control flow. It points at `favicon.ico`, `logo192.png`, and `logo512.png` in the public asset directory and carries no mutable state.

## Dependencies and Integration
This file integrates with the web app manifest/runtime asset pipeline and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
The names still use Create React App placeholders, which can affect install/PWA metadata if surfaced outside Electron. Test signal is asset existence and successful app packaging.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/notifications.js -->
# sources/sync-backup/kopia/app/public/notifications.js

## Purpose
Small Electron main-process helper for persisted desktop notification level. It defines disabled, warning/error-only, and all-notification levels and reads/writes the value through the shared app config module.

## APIs, Types, and Functions
Important APIs include dependencies `electron`, `./config.js`.

## Control Flow, State, and Persistence
`getNotificationLevel` lazily loads the level from config once, defaulting if absent. `setNotificationLevel` updates the cached value and persists it, allowing tray/menu code to decide whether to display repository notifications. State is a single cached `level` plus the app configuration file. The file imports Electron `app` and filesystem/path modules only to resolve config through `config.js`.

## Dependencies and Integration
This file integrates with electron, ./config.js and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are stale cache if config changes externally and caller-side interpretation of numeric levels. Its signals are integration with `electron.js` tray refresh and notification-config IPC.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/notifications.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/preload.js -->
# sources/sync-backup/kopia/app/public/preload.js

## Purpose
Electron preload bridge that exposes a tiny, context-isolated `window.kopiaUI` API to renderer code for directory selection and browsing.

## APIs, Types, and Functions
Important APIs include dependencies `electron`.

## Control Flow, State, and Persistence
At preload time, `contextBridge.exposeInMainWorld` publishes `chooseDirectory` and `browseDirectory`; these delegate to `ipcRenderer.invoke("select-dir")` and `ipcRenderer.invoke("browse-dir", path)` in the main process. No persistent state is kept. The security boundary is the exposed API shape, not mutable data.

## Dependencies and Integration
This file integrates with electron and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
The primary risk is widening renderer privileges if more IPC is added without validation. Existing surface is intentionally narrow and should be tested with Electron startup/render IPC coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/preload.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/server.js -->
# sources/sync-backup/kopia/app/public/server.js

## Purpose
Main-process server manager for per-repository `kopia server start` child processes used by the UI. It builds process arguments, tracks status, polls the HTTPS API, tails server logs, and responds to renderer status fetch IPC.

## APIs, Types, and Functions
Important APIs include dependencies `electron`, `./utils.js`, `child_process`, `electron-log`, `./config.js`; functions `newServerForRepo`.

## Control Flow, State, and Persistence
`newServerForRepo` lazily constructs a server object with mutable status fields. It spawns the selected Kopia binary with repository-specific cache/log paths, captures generated server details from stdout/logs, polls `/api/v1/status`, emits status updates, and exposes `serverForRepo` lookup plus IPC refresh handling. The module keeps a `servers` map keyed by repository ID, active child process handles, address/certificate/password/control-password details, status polling intervals, and a bounded in-memory log buffer. State is process-local but depends on repo config files and server-generated credentials/certificates.

## Dependencies and Integration
This file integrates with electron, ./utils.js, child_process, electron-log, ./config.js and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Important risks are leaking child processes or intervals, trusting parsed log details, certificate/password mismatch between runs, and UI reporting stale status after process exit. Integration signals are IPC `status-fetch`, status update messages to Electron, and server log/status transitions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/server.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/utils.js -->
# sources/sync-backup/kopia/app/public/utils.js

## Purpose
Shared Electron utility module for OS-specific resource paths and executable/icon selection.

## APIs, Types, and Functions
Important APIs include dependencies `electron`, `path`.

## Control Flow, State, and Persistence
It computes `osShortName`, resolves public and icons paths relative to the module, chooses the default Kopia server binary for the platform, and exposes `selectByOS` to select per-OS values. State is static process configuration derived from `process.platform`, `app.isPackaged`, and module paths. No repository state is persisted here.

## Dependencies and Integration
This file integrates with electron, path and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are packaging path drift, unsupported platform defaults, and icon/binary names diverging from build artifacts. It integrates directly with tray creation and server child-process launching.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/utils.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/sign.mjs -->
# sources/sync-backup/kopia/app/sign.mjs

## Purpose
Windows signing helper for the Electron build. It invokes `signtool` with SHA-1 fingerprint and retry/backoff behavior around transient signing failures.

## APIs, Types, and Functions
Important APIs include dependencies `child_process`.

## Control Flow, State, and Persistence
The module builds signing arguments, loops attempts, runs child-process signing synchronously, sleeps between failures, and exits with the signing result once success or attempts are exhausted. State is limited to environment/configured certificate identity and attempt counters. The signed artifact is the durable output, outside this script.

## Dependencies and Integration
This file integrates with child_process and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are leaking signing configuration in logs, brittle `signtool` path assumptions, and retry masking persistent certificate/timestamp failures. Build pipeline execution is the main signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/sign.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/tests/main.spec.js -->
# sources/sync-backup/kopia/app/tests/main.spec.js

## Purpose
Playwright Electron end-to-end coverage for Kopia UI startup, tray menu behavior, repository window creation, configuration persistence, and app data isolation.

## APIs, Types, and Functions
Important APIs include dependencies `@playwright/test`, `playwright`, `fs`, `os`, `path`; functions `getKopiaUIDir`, `getMainPath`, `getExecutablePath`, `createTemporaryAppDataDir`, `launchApp`, `waitForKopiaToStartup`.

## Control Flow, State, and Persistence
Helpers locate the UI app, create a temporary app-data directory, launch Electron, wait for startup, drive test hooks such as tray popup/close, and assert windows/config files for default and non-default repositories. The tests create temporary app data and inspect generated config JSON/window state. They intentionally isolate repository IDs and cleanup through Playwright lifecycle.

## Dependencies and Integration
This file integrates with @playwright/test, playwright, fs, os, path and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are packaging-layout assumptions, timing around Electron startup, and reliance on test-only hooks. Strong signals are real Electron launch and renderer/window/tray integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/tests/main.spec.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/app.go -->
# sources/sync-backup/kopia/cli/app.go

## Purpose
Core CLI application wiring for Kopia. It defines the service interfaces, global flags, repository/session action wrappers, output plumbing, maintenance hooks, password persistence strategy, and command registration entry point used by every CLI command.

## APIs, Types, and Functions
Important APIs include types `textOutput`, `appServices`, `advancedAppServices`, `App`, `commandParent`, `repositoryAccessMode`; functions/methods `setup`, `stdout`, `stderr`, `printStdout`, `printStderr`, `enableTestOnlyFlags`, `getProgress`, `SetRestoreProgress`, `getRestoreProgress`, `stdin`, `stdout`, `Stderr`, `SetLoggerFactory`, `RegisterOnExit`, plus more; flags help-full: Show help for all commands, including hidden, auto-maintenance: Automatic maintenance, initial-update-check-delay: Initial delay before first time update check, update-check-interval: Interval between update checks, update-available-notify-interval: Interval between update notifications, config-file: Specify the config file to use, trace-storage: Enables tracing of storage operations., timezone: Format time according to specified time zone (local, utc, original or time zone name), password: Repository password., persist-credentials: Persist credentials, plus 8 more.

## Control Flow, State, and Persistence
Control flow binds flags help-full: Show help for all commands, including hidden, auto-maintenance: Automatic maintenance, initial-update-check-delay: Initial delay before first time update check, update-check-interval: Interval between update checks, update-available-notify-interval: Interval between update notifications, config-file: Specify the config file to use, trace-storage: Enables tracing of storage operations., timezone: Format time according to specified time zone (local, utc, original or time zone name), plus 10 more, then runs through a direct repository write action. The implementation opens a write session, requires direct repository writer access. State and persistence: touches repository manifest metadata, local cache directories and client cache parameters, maintenance params, schedule, and maintenance statistics, notification profiles/templates in repository metadata, snapshot policy manifests, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, errors, fmt, io, os, time, github.com/alecthomas/kingpin/v2, github.com/fatih/color, github.com/mattn/go-colorable, github.com/pkg/errors, plus 13 more. It integrates with Kopia repository internals such as kopia/internal/apiclient, kopia/internal/clock, kopia/internal/passwordpersist, kopia/internal/releasable, kopia/notification, kopia/notification/notifydata, kopia/notification/notifytemplate, kopia/repo, plus 4 more plus external packages context, errors, fmt, io, os, plus 6 more.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. secret-bearing options should avoid accidental output and preserve typed config. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/app.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/auto_upgrade.go -->
# sources/sync-backup/kopia/cli/auto_upgrade.go

## Purpose
Repository auto-upgrade helper invoked while opening repositories. It detects unsupported format parameters, attempts a direct write-session upgrade when allowed, and seeds default maintenance parameters after successful upgrades.

## APIs, Types, and Functions
Important APIs include functions/methods `maybeAutoUpgradeRepository`, `setDefaultMaintenanceParameters`.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The implementation opens a write session, requires direct repository writer access, persists maintenance parameters. State and persistence: touches maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/maintenance plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/auto_upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/cli_progress.go -->
# sources/sync-backup/kopia/cli/cli_progress.go

## Purpose
Terminal progress implementation for snapshot upload workflows. It implements `upload.Progress`, spinner rendering, adaptive estimation flags, byte/file counters, and terminal-aware output throttling.

## APIs, Types, and Functions
Important APIs include types `progressFlags`, `cliProgress`; functions/methods `setup`, `Enabled`, `HashingFile`, `FinishedHashingFile`, `UploadedBytes`, `HashedBytes`, `Error`, `CachedFile`, `maybeOutput`, `output`, `spinnerCharacter`, `StartShared`, `FinishShared`, `UploadStarted`, plus more; flags progress: Enable progress output, progress-estimation-type: Set type of estimation of the data to be snapshotted, progress-update-interval: How often to update progress information, adaptive-estimation-threshold: Sets the threshold below which the classic estimation method will be used.

## Control Flow, State, and Persistence
Control flow binds flags progress: Enable progress output, progress-estimation-type: Set type of estimation of the data to be snapshotted, progress-update-interval: How often to update progress information, adaptive-estimation-threshold: Sets the threshold below which the classic estimation method will be used, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports fmt, os, strconv, strings, sync, sync/atomic, time, github.com/alecthomas/kingpin/v2, github.com/fatih/color, golang.org/x/term, plus 3 more. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/internal/units, kopia/snapshot/upload plus external packages fmt, os, strconv, strings, sync, plus 5 more.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/cli_progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl.go -->
# sources/sync-backup/kopia/cli/command_acl.go

## Purpose
Command group root for server ACL management. It wires the `acl` namespace under the parent command and delegates concrete add/delete/enable/list behavior to sibling files.

## APIs, Types, and Functions
Important APIs include types `commandServerACL`; functions/methods `setup`; Kingpin command(s) acl: Manager server access control list entries.

## Control Flow, State, and Persistence
Control flow registers command(s) acl: Manager server access control list entries, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_add.go -->
# sources/sync-backup/kopia/cli/command_acl_add.go

## Purpose
Implementation of `acl add`, which creates repository ACL entries for a user, target manifest selector, and supported access level, with optional overwrite semantics.

## APIs, Types, and Functions
Important APIs include types `commandACLAdd`; functions/methods `setup`, `run`; Kingpin command(s) add: Add ACL entry; flags user: User the ACL targets, target: Manifests targeted by the rule (type:T,key1:value1,...,keyN:valueN), access: Access the user gets to subject, overwrite: Overwrite existing rule with the same user and target.

## Control Flow, State, and Persistence
Control flow registers command(s) add: Add ACL entry, binds flags user: User the ACL targets, target: Manifests targeted by the rule (type:T,key1:value1,...,keyN:valueN), access: Access the user gets to subject, overwrite: Overwrite existing rule with the same user and target, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/repo plus external packages context, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_delete.go -->
# sources/sync-backup/kopia/cli/command_acl_delete.go

## Purpose
Implementation of `acl delete`, which removes selected ACL entries by ID or all entries, with dry-run output unless the destructive `--delete` flag is supplied.

## APIs, Types, and Functions
Important APIs include types `commandACLDelete`; functions/methods `setup`, `dryRunDelete`, `shouldRemoveACLEntry`, `run`; Kingpin command(s) delete: Delete ACL entry; flags all: Remove all ACL entries, delete: Really delete; arguments id: Entry ID.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Delete ACL entry, binds flags all: Remove all ACL entries, delete: Really delete, accepts arguments id: Entry ID, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_enable.go -->
# sources/sync-backup/kopia/cli/command_acl_enable.go

## Purpose
Implementation of ACL enable/reset, creating or resetting ACL policy manifests and bootstrap entries for the authenticated user.

## APIs, Types, and Functions
Important APIs include types `commandACLEnable`; functions/methods `setup`, `run`; Kingpin command(s) enable: Enable ACLs and install default entries; flags reset: Reset all ACLs to default.

## Control Flow, State, and Persistence
Control flow registers command(s) enable: Enable ACLs and install default entries, binds flags reset: Reset all ACLs to default, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/internal/auth, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/internal/auth, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_list.go -->
# sources/sync-backup/kopia/cli/command_acl_list.go

## Purpose
Implementation of `acl list`, which reads ACL manifest entries and displays entry IDs, users, targets, and access levels.

## APIs, Types, and Functions
Important APIs include types `commandACLList`, `aclListItem`; functions/methods `setup`, `run`; Kingpin command(s) list: List ACL entries.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List ACL entries, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/manifest. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/repo, kopia/repo/manifest plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_acl_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark.go -->
# sources/sync-backup/kopia/cli/command_benchmark.go

## Purpose
Benchmark command root and shared parallel execution helpers. It registers benchmark subcommands and provides worker fan-out helpers plus reusable output buffers for crypto-style benchmarks.

## APIs, Types, and Functions
Important APIs include types `commandBenchmark`, `cryptoBenchResult`; functions/methods `setup`, `runInParallelNoInputNoResult`, `runInParallelNoInput`, `runInParallelNoResult`, `runInParallel`, `makeOutputBuffers`; Kingpin command(s) benchmark: Commands to test performance of algorithms..

## Control Flow, State, and Persistence
Control flow registers command(s) benchmark: Commands to test performance of algorithms., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, sync. It integrates with shared CLI infrastructure plus external packages bytes, sync.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. nearby test file `sources/sync-backup/kopia/cli/command_benchmark_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_compression.go -->
# sources/sync-backup/kopia/cli/command_benchmark_compression.go

## Purpose
Compression benchmark command for measuring Kopia compression algorithms over generated or file-provided data, including compression, decompression, stability verification, sorting, and option-printing.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkCompression`, `compressionBenchmarkResult`; functions/methods `setup`, `readInputFile`, `shouldIncludeAlgorithm`, `run`, `runCompression`, `runDecompression`, `sortResults`, `printResults`, `hashOf`; Kingpin command(s) compression: Run compression benchmarks; flags repeat: Number of repetitions, data-file: Use data from the given file, by-size: Sort results by size, by-alloc: Sort results by allocated bytes, parallel: Number of parallel goroutines, operations: Operations, verify-stable: Verify that compression is stable, print-options: Print out options usable for repository creation, deprecated: Included deprecated compression algorithms, algorithms: Comma-separated list of algorithms to benchmark.

## Control Flow, State, and Persistence
Control flow registers command(s) compression: Run compression benchmarks, binds flags repeat: Number of repetitions, data-file: Use data from the given file, by-size: Sort results by size, by-alloc: Sort results by allocated bytes, parallel: Number of parallel goroutines, operations: Operations, verify-stable: Verify that compression is stable, print-options: Print out options usable for repository creation, plus 2 more, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, hash/fnv, io, os, runtime, sort, strings, github.com/pkg/errors, github.com/kopia/kopia/internal/gather, plus 3 more. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/compression plus external packages bytes, context, hash/fnv, io, os, plus 4 more.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_crypto.go -->
# sources/sync-backup/kopia/cli/command_benchmark_crypto.go

## Purpose
Combined encryption-and-hashing benchmark command for repository format choices, measuring block encryption plus content hashing across algorithms and parallelism.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkCrypto`; functions/methods `setup`, `run`, `runBenchmark`; Kingpin command(s) crypto: Run combined hash and encryption benchmarks; flags block-size: Size of a block to encrypt, repeat: Number of repetitions, deprecated: Include deprecated algorithms, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation.

## Control Flow, State, and Persistence
Control flow registers command(s) crypto: Run combined hash and encryption benchmarks, binds flags block-size: Size of a block to encrypt, repeat: Number of repetitions, deprecated: Include deprecated algorithms, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/alecthomas/units, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo/encryption, github.com/kopia/kopia/repo/format, github.com/kopia/kopia/repo/hashing. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/encryption, kopia/repo/format, kopia/repo/hashing plus external packages context, sort, github.com/alecthomas/units.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_ecc.go -->
# sources/sync-backup/kopia/cli/command_benchmark_ecc.go

## Purpose
ECC benchmark command for repository error-correction providers, measuring encode/decode overhead and printing option strings for repository creation.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkEcc`, `eccBenchResult`; functions/methods `setup`, `run`, `runBenchmark`; Kingpin command(s) ecc: Run ECC benchmarks; flags block-size: Size of a block to encrypt, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation.

## Control Flow, State, and Persistence
Control flow registers command(s) ecc: Run ECC benchmarks, binds flags block-size: Size of a block to encrypt, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, math, sort, github.com/alecthomas/units, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo/ecc. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/ecc plus external packages context, fmt, math, sort, github.com/alecthomas/units.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_ecc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_encryption.go -->
# sources/sync-backup/kopia/cli/command_benchmark_encryption.go

## Purpose
Encryption benchmark command for Kopia encryption algorithms over configurable block sizes, repetitions, parallelism, and deprecated-algorithm inclusion.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkEncryption`; functions/methods `setup`, `run`, `runBenchmark`; Kingpin command(s) encryption: Run encryption benchmarks; flags block-size: Size of a block to encrypt, repeat: Number of repetitions, deprecated: Include deprecated algorithms, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation.

## Control Flow, State, and Persistence
Control flow registers command(s) encryption: Run encryption benchmarks, binds flags block-size: Size of a block to encrypt, repeat: Number of repetitions, deprecated: Include deprecated algorithms, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/alecthomas/units, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo/encryption, github.com/kopia/kopia/repo/format, github.com/kopia/kopia/repo/hashing. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/encryption, kopia/repo/format, kopia/repo/hashing plus external packages context, sort, github.com/alecthomas/units.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_hashing.go -->
# sources/sync-backup/kopia/cli/command_benchmark_hashing.go

## Purpose
Hashing benchmark command for content hash algorithms, reporting throughput and option strings for repository creation.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkHashing`; functions/methods `setup`, `run`, `runBenchmark`; Kingpin command(s) hashing: Run hashing function benchmarks; flags block-size: Size of a block to hash, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation.

## Control Flow, State, and Persistence
Control flow registers command(s) hashing: Run hashing function benchmarks, binds flags block-size: Size of a block to hash, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/alecthomas/units, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo/format, github.com/kopia/kopia/repo/hashing. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/format, kopia/repo/hashing plus external packages context, sort, github.com/alecthomas/units.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_hashing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_splitters.go -->
# sources/sync-backup/kopia/cli/command_benchmark_splitters.go

## Purpose
Splitter benchmark command that generates deterministic random data and measures dynamic content splitter throughput, chunk counts, and fastest option selection.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkSplitters`; functions/methods `setup`, `run`; Kingpin command(s) splitter: Run splitter benchmarks; flags rand-seed: Random seed, data-size: Size of a data to split, block-count: Number of data blocks to split, print-options: Print out the fastest dynamic splitter option, parallel: Number of parallel goroutines.

## Control Flow, State, and Persistence
Control flow registers command(s) splitter: Run splitter benchmarks, binds flags rand-seed: Random seed, data-size: Size of a data to split, block-count: Number of data blocks to split, print-options: Print out the fastest dynamic splitter option, parallel: Number of parallel goroutines, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, math, math/rand, sort, strings, time, github.com/alecthomas/units, github.com/pkg/errors, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, plus 1 more. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/internal/units, kopia/repo/splitter plus external packages context, math, math/rand, sort, strings, plus 3 more.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_splitters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_test.go -->
# sources/sync-backup/kopia/cli/command_benchmark_test.go

## Purpose
Test coverage for `command_benchmark` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestCommandBenchmarkCrypto, TestCommandBenchmarkEncryption, TestCommandBenchmarkHashing, TestCommandBenchmarkSplitter, TestCommandBenchmarkCompression.

## APIs, Types, and Functions
Important APIs include functions/methods `TestCommandBenchmarkCrypto`, `TestCommandBenchmarkEncryption`, `TestCommandBenchmarkHashing`, `TestCommandBenchmarkSplitter`, `TestCommandBenchmarkCompression`; tests TestCommandBenchmarkCrypto, TestCommandBenchmarkEncryption, TestCommandBenchmarkHashing, TestCommandBenchmarkSplitter, TestCommandBenchmarkCompression.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, os, path/filepath, testing, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages bytes, os, path/filepath, testing.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. test signals come from named tests TestCommandBenchmarkCrypto, TestCommandBenchmarkEncryption, TestCommandBenchmarkHashing, TestCommandBenchmarkSplitter, TestCommandBenchmarkCompression.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob.go -->
# sources/sync-backup/kopia/cli/command_blob.go

## Purpose
Command group root for low-level blob storage diagnostics and mutation. It registers `blob` subcommands for listing, showing, deleting, GC, stats, and shard operations.

## APIs, Types, and Functions
Important APIs include types `commandBlob`; functions/methods `setup`; Kingpin command(s) blob: Commands to manipulate BLOBs..

## Control Flow, State, and Persistence
Control flow registers command(s) blob: Commands to manipulate BLOBs., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_delete.go -->
# sources/sync-backup/kopia/cli/command_blob_delete.go

## Purpose
Low-level `blob delete` command that deletes a blob by ID directly from repository blob storage after repository write access is established.

## APIs, Types, and Functions
Important APIs include types `commandBlobDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Delete blobs by ID; arguments blobIDs: Blob IDs.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Delete blobs by ID, accepts arguments blobIDs: Blob IDs, then runs through a direct repository write action. The implementation deletes blob storage objects. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_gc.go -->
# sources/sync-backup/kopia/cli/command_blob_gc.go

## Purpose
Low-level blob garbage-collection command that scans blob storage for unused blobs, supports prefix filtering and parallelism, and only deletes when explicitly requested.

## APIs, Types, and Functions
Important APIs include types `commandBlobGC`; functions/methods `setup`, `run`; Kingpin command(s) gc: Garbage-collect unused blobs; flags delete: Whether to delete unused blobs, parallel: Number of parallel blob scans, prefix: Only GC blobs with given prefix.

## Control Flow, State, and Persistence
Control flow registers command(s) gc: Garbage-collect unused blobs, binds flags delete: Whether to delete unused blobs, parallel: Number of parallel blob scans, prefix: Only GC blobs with given prefix, then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata, maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob, kopia/repo/maintenance plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_list.go -->
# sources/sync-backup/kopia/cli/command_blob_list.go

## Purpose
Low-level blob listing command with prefix, exclusion, size, and data-only filters. It walks storage metadata and formats blob IDs, lengths, timestamps, and storage IDs.

## APIs, Types, and Functions
Important APIs include types `commandBlobList`; functions/methods `setup`, `run`, `shouldInclude`; Kingpin command(s) list: List BLOBs; flags prefix: Blob ID prefix, exclude-prefix: Blob ID prefixes to exclude, min-size: Minimum size, max-size: Maximum size, data-only: Only list data blobs.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List BLOBs, binds flags prefix: Blob ID prefix, exclude-prefix: Blob ID prefixes to exclude, min-size: Minimum size, max-size: Maximum size, data-only: Only list data blobs, then runs through a direct repository read action. The implementation iterates blob storage. State and persistence: touches blob storage objects and metadata, encrypted repository log blobs, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, github.com/kopia/kopia/internal/epoch, github.com/kopia/kopia/internal/repodiag, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/internal/epoch, kopia/internal/repodiag, kopia/repo, kopia/repo/blob, kopia/repo/content/indexblob plus external packages context, strings.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_shards.go -->
# sources/sync-backup/kopia/cli/command_blob_shards.go

## Purpose
Command group root for direct sharded blob-storage layout commands. It registers the `blob shards` namespace and delegates the actual parameter rewrite command.

## APIs, Types, and Functions
Important APIs include types `commandBlobShards`; functions/methods `setup`; Kingpin command(s) shards: Manipulate shards in a blob store.

## Control Flow, State, and Persistence
Control flow registers command(s) shards: Manipulate shards in a blob store, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_shards.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_shards_modify.go -->
# sources/sync-backup/kopia/cli/command_blob_shards_modify.go

## Purpose
Offline sharded-storage layout migration command. It parses shard parameters, computes new blob paths, optionally dry-runs, renames blob files, and removes empty directories after confirmation no Kopia process is running.

## APIs, Types, and Functions
Important APIs include types `commandBlobShardsModify`; functions/methods `setup`, `getParameters`, `parseShardSpec`, `prefixAndShardsWithout`, `applyParameterChangesFromFlags`, `run`, `removeEmptyDirs`, `renameBlobs`; Kingpin command(s) modify: Perform low-level resharding of blob storage; flags i-am-sure-kopia-is-not-running: Confirm that no other instance of kopia is running, path: Sharded directory path, default-shards: Default specification 'n1,..nN' or 'flat'), override: Override specification 'prefix=n1,..nN'), remove-override: Override specification 'prefix=n1,..nN'), unsharded-length: Minimum sharded length, dry-run: Dry run.

## Control Flow, State, and Persistence
Control flow registers command(s) modify: Perform low-level resharding of blob storage, binds flags i-am-sure-kopia-is-not-running: Confirm that no other instance of kopia is running, path: Sharded directory path, default-shards: Default specification 'n1,..nN' or 'flat'), override: Override specification 'prefix=n1,..nN'), remove-override: Override specification 'prefix=n1,..nN'), unsharded-length: Minimum sharded length, dry-run: Dry run, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, os, path, path/filepath, strconv, strings, github.com/pkg/errors, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/blob/sharded. It integrates with Kopia repository internals such as kopia/repo/blob, kopia/repo/blob/sharded plus external packages context, fmt, os, path, path/filepath, plus 3 more.

## Risks and Test Signals
Risks and test signals: filesystem operations are platform and permission sensitive. nearby test file `sources/sync-backup/kopia/cli/command_blob_shards_modify_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_shards_modify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_shards_modify_test.go -->
# sources/sync-backup/kopia/cli/command_blob_shards_modify_test.go

## Purpose
Test coverage for `command_blob_shards_modify` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestBlobShardsModify.

## APIs, Types, and Functions
Important APIs include functions/methods `TestBlobShardsModify`; tests TestBlobShardsModify.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports path/filepath, strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/repo/blob/sharded, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/repo/blob/sharded, kopia/tests/testenv plus external packages path/filepath, strings, testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestBlobShardsModify.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_shards_modify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_show.go -->
# sources/sync-backup/kopia/cli/command_blob_show.go

## Purpose
Low-level blob display command that reads a raw blob, optionally decrypts supported encrypted blob types, and formats JSON blobs through the shared output formatter.

## APIs, Types, and Functions
Important APIs include types `commandBlobShow`; functions/methods `setup`, `run`, `maybeDecryptBlob`, `canDecryptBlob`, `isJSONBlob`; Kingpin command(s) show: Show contents of BLOBs; flags decrypt: Decrypt blob if possible; arguments blobID: Blob IDs.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show contents of BLOBs, binds flags decrypt: Decrypt blob if possible, accepts arguments blobID: Blob IDs, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata, content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, encoding/json, io, github.com/pkg/errors, github.com/kopia/kopia/internal/blobcrypto, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/iocopy, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/blobcrypto, kopia/internal/gather, kopia/internal/iocopy, kopia/repo, kopia/repo/blob plus external packages bytes, context, encoding/json, io, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_blob_show_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_show_test.go -->
# sources/sync-backup/kopia/cli/command_blob_show_test.go

## Purpose
Test coverage for `command_blob_show` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for none.

## APIs, Types, and Functions
Important APIs include functions/methods `TestBlobShow`.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports strings, testing, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/tests/testenv plus external packages strings, testing.

## Risks and Test Signals
Risks and test signals: test signals come from named tests none.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_show_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_stats.go -->
# sources/sync-backup/kopia/cli/command_blob_stats.go

## Purpose
Low-level blob statistics command that counts and sizes blobs grouped by prefix or raw numbers, with optional prefix filtering.

## APIs, Types, and Functions
Important APIs include types `commandBlobStats`; functions/methods `setup`, `run`; Kingpin command(s) stats: Blob statistics; flags raw: Raw numbers, prefix: Blob name prefix.

## Control Flow, State, and Persistence
Control flow registers command(s) stats: Blob statistics, binds flags raw: Raw numbers, prefix: Blob name prefix, then runs through a direct repository read action. The implementation iterates blob storage. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strconv, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/blob plus external packages context, strconv, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_blob_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache.go -->
# sources/sync-backup/kopia/cli/command_cache.go

## Purpose
Command group root for local cache operations. It wires cache clear/info/prefetch/set/sync subcommands into the CLI.

## APIs, Types, and Functions
Important APIs include types `commandCache`; functions/methods `setup`; Kingpin command(s) cache: Commands to manipulate local cache.

## Control Flow, State, and Persistence
Control flow registers command(s) cache: Commands to manipulate local cache, then runs through a test/helper flow. The implementation persists maintenance parameters. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_clear.go -->
# sources/sync-backup/kopia/cli/command_cache_clear.go

## Purpose
Cache-clearing command for local repository caches. It selects partial cache directories, removes files/directories with retry behavior, and reports cleanup errors.

## APIs, Types, and Functions
Important APIs include types `commandCacheClear`; functions/methods `setup`, `run`, `clearCacheDirectory`; Kingpin command(s) clear: Clears the cache; flags partial: Specifies the cache to clear.

## Control Flow, State, and Persistence
Control flow registers command(s) clear: Clears the cache, binds flags partial: Specifies the cache to clear, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, os, path/filepath, github.com/pkg/errors, github.com/kopia/kopia/internal/cache, github.com/kopia/kopia/internal/retry, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/cache, kopia/internal/retry, kopia/repo plus external packages context, os, path/filepath, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: filesystem operations are platform and permission sensitive. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_clear.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_info.go -->
# sources/sync-backup/kopia/cli/command_cache_info.go

## Purpose
Cache information command that prints configured cache directories, usage, limits, and optional path-only output.

## APIs, Types, and Functions
Important APIs include types `commandCacheInfo`; functions/methods `setup`, `run`; Kingpin command(s) info: Displays cache information and statistics; flags path: Only display cache path.

## Control Flow, State, and Persistence
Control flow registers command(s) info: Displays cache information and statistics, binds flags path: Only display cache path, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, os, path/filepath, time, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/content plus external packages context, fmt, os, path/filepath, time, plus 1 more.

## Risks and Test Signals
Risks and test signals: filesystem operations are platform and permission sensitive. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_prefetch.go -->
# sources/sync-backup/kopia/cli/command_cache_prefetch.go

## Purpose
Cache prefetch command that resolves a repository object and asks snapshot filesystem/cache layers to prefetch data according to a hint.

## APIs, Types, and Functions
Important APIs include types `commandCachePrefetch`; functions/methods `setup`, `run`; Kingpin command(s) prefetch: Prefetches the provided objects into cache; flags hint: Prefetch hint; arguments object: Object ID to prefetch.

## Control Flow, State, and Persistence
Control flow registers command(s) prefetch: Prefetches the provided objects into cache, binds flags hint: Prefetch hint, accepts arguments object: Object ID to prefetch, then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/object, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/object, kopia/snapshot/snapshotfs plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_set.go -->
# sources/sync-backup/kopia/cli/command_cache_set.go

## Purpose
Cache configuration command that updates repository client cache limits and directory settings through direct repository parameters.

## APIs, Types, and Functions
Important APIs include types `cacheSizeFlags`, `commandCacheSetParams`; functions/methods `setup`, `setup`, `run`; Kingpin command(s) set: Sets parameters local caching of repository data; flags content-cache-size-mb: Desired size of local content cache (soft limit), content-cache-size-limit-mb: Maximum size of local content cache (hard limit), content-min-sweep-age: Minimal age of content cache item to be subject to sweeping, metadata-cache-size-mb: Desired size of local metadata cache (soft limit), metadata-cache-size-limit-mb: Maximum size of local metadata cache (hard limit), metadata-min-sweep-age: Minimal age of metadata cache item to be subject to sweeping, index-min-sweep-age: Minimal age of index cache item to be subject to sweeping, max-list-cache-duration: Duration of index cache, cache-directory: Directory where to store cache files.

## Control Flow, State, and Persistence
Control flow registers command(s) set: Sets parameters local caching of repository data, binds flags content-cache-size-mb: Desired size of local content cache (soft limit), content-cache-size-limit-mb: Maximum size of local content cache (hard limit), content-min-sweep-age: Minimal age of content cache item to be subject to sweeping, metadata-cache-size-mb: Desired size of local metadata cache (soft limit), metadata-cache-size-limit-mb: Maximum size of local metadata cache (hard limit), metadata-min-sweep-age: Minimal age of metadata cache item to be subject to sweeping, index-min-sweep-age: Minimal age of index cache item to be subject to sweeping, max-list-cache-duration: Duration of index cache, plus 1 more, then runs through a repository writer action. The implementation persists maintenance parameters. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/content plus external packages context, time, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_cache_set_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_set_test.go -->
# sources/sync-backup/kopia/cli/command_cache_set_test.go

## Purpose
Test coverage for `command_cache_set` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestCacheSet.

## APIs, Types, and Functions
Important APIs include functions/methods `TestCacheSet`, `mustGetLineContaining`; tests TestCacheSet.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages strings, testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestCacheSet.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_sync.go -->
# sources/sync-backup/kopia/cli/command_cache_sync.go

## Purpose
Cache synchronization command that flushes cached content/index/blob-list state to durable storage for the connected repository.

## APIs, Types, and Functions
Important APIs include types `commandCacheSync`; functions/methods `setup`, `run`; Kingpin command(s) sync: Synchronizes the metadata cache with blobs in storage; flags parallel: Fetch parallelism.

## Control Flow, State, and Persistence
Control flow registers command(s) sync: Synchronizes the metadata cache with blobs in storage, binds flags parallel: Fetch parallelism, then runs through a direct repository write action. The implementation iterates blob storage. State and persistence: touches content indexes, pack blobs, and content metadata, local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, golang.org/x/sync/errgroup, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob, kopia/repo/content plus external packages context, github.com/pkg/errors, golang.org/x/sync/errgroup.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. nearby test file `sources/sync-backup/kopia/cli/command_cache_sync_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_sync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_sync_test.go -->
# sources/sync-backup/kopia/cli/command_cache_sync_test.go

## Purpose
Test coverage for `command_cache_sync` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestCacheClearSync.

## APIs, Types, and Functions
Important APIs include functions/methods `TestCacheClearSync`; tests TestCacheClearSync.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestCacheClearSync.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_cache_sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content.go -->
# sources/sync-backup/kopia/cli/command_content.go

## Purpose
Command group root for content-addressed repository content operations. It registers list/show/delete/stats/verify/rewrite and range flag sharing.

## APIs, Types, and Functions
Important APIs include types `commandContent`; functions/methods `setup`; Kingpin command(s) content: Commands to manipulate content in repository..

## Control Flow, State, and Persistence
Control flow registers command(s) content: Commands to manipulate content in repository., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_delete.go -->
# sources/sync-backup/kopia/cli/command_content_delete.go

## Purpose
Content deletion command that marks repository content IDs as deleted, with support for range selection through shared content range flags.

## APIs, Types, and Functions
Important APIs include types `commandContentDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Remove content; arguments id: IDs of content to remove.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Remove content, accepts arguments id: IDs of content to remove, then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_list.go -->
# sources/sync-backup/kopia/cli/command_content_list.go

## Purpose
Content listing command that iterates repository content metadata, filters by ID range/deleted state, and renders content length, pack blob, and status information.

## APIs, Types, and Functions
Important APIs include types `commandContentList`; functions/methods `setup`, `run`, `outputLong`, `outputCompressed`, `deletedInfoString`, `compressionInfoStringString`; Kingpin command(s) list: List contents; flags long: Long output, compression: Compression, deleted: Include deleted content, deleted-only: Only show deleted content, summary: Summarize the list, human: Human-readable output.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List contents, binds flags long: Long output, compression: Compression, deleted: Include deleted content, deleted-only: Only show deleted content, summary: Summarize the list, human: Human-readable output, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, github.com/pkg/errors, github.com/kopia/kopia/internal/stats, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/compression, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/stats, kopia/repo, kopia/repo/compression, kopia/repo/content plus external packages context, fmt, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_range_flags.go -->
# sources/sync-backup/kopia/cli/command_content_range_flags.go

## Purpose
Shared flag parser for content ID ranges. It normalizes prefix/start/end options into a content iteration range used by list/show/delete/rewrite/verify commands.

## APIs, Types, and Functions
Important APIs include types `contentRangeFlags`; functions/methods `setup`, `contentIDRange`; flags prefix: Content ID prefix, prefixed: Apply to content IDs with (any) prefix, non-prefixed: Apply to content IDs without prefix.

## Control Flow, State, and Persistence
Control flow binds flags prefix: Content ID prefix, prefixed: Apply to content IDs with (any) prefix, non-prefixed: Apply to content IDs without prefix, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports github.com/alecthomas/kingpin/v2, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/content/index. It integrates with Kopia repository internals such as kopia/repo/content, kopia/repo/content/index plus external packages github.com/alecthomas/kingpin/v2.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_range_flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_rewrite.go -->
# sources/sync-backup/kopia/cli/command_content_rewrite.go

## Purpose
Content rewrite command that rewrites selected content into new packs, supporting deleted-content inclusion and progress output for repository repair/compaction workflows.

## APIs, Types, and Functions
Important APIs include types `commandContentRewrite`; functions/methods `setup`, `runContentRewriteCommand`, `toContentIDs`; Kingpin command(s) rewrite: Rewrite content using most recent format; flags parallelism: Number of parallel workers, short: Rewrite contents from short packs, format-version: Rewrite contents using the provided format version, pack-prefix: Only rewrite contents from pack blobs with a given prefix, dry-run: Do not actually rewrite, only print what would happen; arguments contentID: Identifiers of contents to rewrite.

## Control Flow, State, and Persistence
Control flow registers command(s) rewrite: Rewrite content using most recent format, binds flags parallelism: Number of parallel workers, short: Rewrite contents from short packs, format-version: Rewrite contents using the provided format version, pack-prefix: Only rewrite contents from pack blobs with a given prefix, dry-run: Do not actually rewrite, only print what would happen, accepts arguments contentID: Identifiers of contents to rewrite, then runs through a direct repository write action. The implementation rewrites selected content. State and persistence: touches content indexes, pack blobs, and content metadata, maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob, kopia/repo/content, kopia/repo/maintenance plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_rewrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_show.go -->
# sources/sync-backup/kopia/cli/command_content_show.go

## Purpose
Content display command that opens a content ID from the repository and streams bytes to stdout through the shared output path.

## APIs, Types, and Functions
Important APIs include types `commandContentShow`; functions/methods `setup`, `run`, `contentShow`; Kingpin command(s) show: Show contents by ID.; flags json: Pretty-print JSON content, unzip: Transparently decompress the content; arguments id: IDs of contents to show.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show contents by ID., binds flags json: Pretty-print JSON content, unzip: Transparently decompress the content, accepts arguments id: IDs of contents to show, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/content plus external packages bytes, context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_stats.go -->
# sources/sync-backup/kopia/cli/command_content_stats.go

## Purpose
Content statistics command that summarizes content count and sizes, optionally including deleted entries and pack/blob distribution.

## APIs, Types, and Functions
Important APIs include types `commandContentStats`, `contentStatsTotals`; functions/methods `setup`, `run`, `calculateStats`; Kingpin command(s) stats: Content statistics; flags raw: Raw numbers.

## Control Flow, State, and Persistence
Control flow registers command(s) stats: Content statistics, binds flags raw: Raw numbers, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strconv, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/compression, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/compression, kopia/repo/content plus external packages context, strconv, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_verify.go -->
# sources/sync-backup/kopia/cli/command_content_verify.go

## Purpose
Content verification command that validates content-to-blob backing data, optionally downloading a percentage or all content, with parallel iteration and ETA progress.

## APIs, Types, and Functions
Important APIs include types `commandContentVerify`; functions/methods `setup`, `run`, `getTotalContentCount`; Kingpin command(s) verify: Verify that each content is backed by a valid blob; flags parallel: Parallelism, full: Full verification (including download), include-deleted: Include deleted contents, download-percent: Download a percentage of files [0.0 .. 100.0], progress-interval: Progress output interval.

## Control Flow, State, and Persistence
Control flow registers command(s) verify: Verify that each content is backed by a valid blob, binds flags parallel: Parallelism, full: Full verification (including download), include-deleted: Include deleted contents, download-percent: Download a percentage of files [0.0 .. 100.0], progress-interval: Progress output interval, then runs through a direct repository read action. The implementation verifies content backing data. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sync, sync/atomic, time, github.com/pkg/errors, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/repo, kopia/repo/content plus external packages context, sync, sync/atomic, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_content_verify_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_verify_test.go -->
# sources/sync-backup/kopia/cli/command_content_verify_test.go

## Purpose
Test coverage for `command_content_verify` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for none.

## APIs, Types, and Functions
Important APIs include functions/methods `TestContentVerify`.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, encrypted repository log blobs, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, os, path/filepath, strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages bytes, os, path/filepath, strings, testing, plus 1 more.

## Risks and Test Signals
Risks and test signals: test signals come from named tests none.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_content_verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_diff.go -->
# sources/sync-backup/kopia/cli/command_diff.go

## Purpose
Snapshot diff command that compares two repository object paths and reports added, removed, changed, and metadata-different filesystem entries.

## APIs, Types, and Functions
Important APIs include types `commandDiff`; functions/methods `setup`, `run`, `defaultDiffCommand`; Kingpin command(s) diff: Displays differences between two repository objects (files or directories); flags files: Compare files by launching diff command for all pairs of (old,new), stats-only: Displays only aggregate statistics of the changes between two repository objects, diff-command: Displays differences between two repository objects (files or directories); arguments object-path1: First object/path, object-path2: Second object/path.

## Control Flow, State, and Persistence
Control flow registers command(s) diff: Displays differences between two repository objects (files or directories), binds flags files: Compare files by launching diff command for all pairs of (old,new), stats-only: Displays only aggregate statistics of the changes between two repository objects, diff-command: Displays differences between two repository objects (files or directories), accepts arguments object-path1: First object/path, object-path2: Second object/path, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository connection/session state and command-local option fields. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, encoding/json, fmt, strings, github.com/pkg/errors, github.com/kopia/kopia/fs, github.com/kopia/kopia/internal/diff, github.com/kopia/kopia/repo, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/fs, kopia/internal/diff, kopia/repo, kopia/snapshot/snapshotfs plus external packages context, encoding/json, fmt, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index.go -->
# sources/sync-backup/kopia/cli/command_index.go

## Purpose
Command group root for repository content-index inspection and repair. It wires list/inspect/optimize/recover/epoch subcommands.

## APIs, Types, and Functions
Important APIs include types `commandIndex`; functions/methods `setup`; Kingpin command(s) index: Commands to manipulate content index..

## Control Flow, State, and Persistence
Control flow registers command(s) index: Commands to manipulate content index., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_epoch.go -->
# sources/sync-backup/kopia/cli/command_index_epoch.go

## Purpose
Command group root for index epoch operations. It registers the `index epoch` namespace for epoch-list inspection.

## APIs, Types, and Functions
Important APIs include types `commandIndexEpoch`; functions/methods `setup`; Kingpin command(s) epoch: Manage index manager epochs.

## Control Flow, State, and Persistence
Control flow registers command(s) epoch: Manage index manager epochs, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_epoch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_epoch_list.go -->
# sources/sync-backup/kopia/cli/command_index_epoch_list.go

## Purpose
Index epoch listing command that reads epoch manager state and reports epoch IDs, ranges, compaction state, or related index metadata.

## APIs, Types, and Functions
Important APIs include types `commandIndexEpochList`; functions/methods `setup`, `run`; Kingpin command(s) list: List the status of epochs..

## Control Flow, State, and Persistence
Control flow registers command(s) list: List the status of epochs., then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/blob plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_epoch_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_inspect.go -->
# sources/sync-backup/kopia/cli/command_index_inspect.go

## Purpose
Index inspection command that reads index blobs and prints contained content entries, filtering to requested index blob IDs when supplied.

## APIs, Types, and Functions
Important APIs include types `commandIndexInspect`, `indexBlobPlusContentInfo`; functions/methods `setup`, `run`, `runWithOutput`, `inspectAllBlobs`, `dumpIndexBlobEntries`, `shouldInclude`, `inspectSingleIndexBlob`; Kingpin command(s) inspect: Inspect index blob; flags all: Inspect all index blobs in the repository, including inactive, active: Inspect all active index blobs, content-id: Inspect all active index blobs, parallel: Parallelism; arguments blobs: Names of index blobs to inspect.

## Control Flow, State, and Persistence
Control flow registers command(s) inspect: Inspect index blob, binds flags all: Inspect all index blobs in the repository, including inactive, active: Inspect all active index blobs, content-id: Inspect all active index blobs, parallel: Parallelism, accepts arguments blobs: Names of index blobs to inspect, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, slices, sync, github.com/pkg/errors, golang.org/x/sync/errgroup, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/repo, kopia/repo/blob, kopia/repo/content, kopia/repo/content/indexblob plus external packages context, slices, sync, github.com/pkg/errors, golang.org/x/sync/errgroup.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. nearby test file `sources/sync-backup/kopia/cli/command_index_inspect_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_inspect_test.go -->
# sources/sync-backup/kopia/cli/command_index_inspect_test.go

## Purpose
Test coverage for `command_index_inspect` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for none.

## APIs, Types, and Functions
Important APIs include functions/methods `TestIndexInspect`.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content index blobs and epoch metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/tests/testenv plus external packages strings, testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests none.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_list.go -->
# sources/sync-backup/kopia/cli/command_index_list.go

## Purpose
Index listing command that enumerates active and optionally superseded index blobs, with summary and sort modes by time, size, or name.

## APIs, Types, and Functions
Important APIs include types `commandIndexList`; functions/methods `setup`, `run`; Kingpin command(s) list: List content indexes; flags summary: Display index blob summary, superseded: Include inactive index files superseded by compaction, sort: Index blob sort order.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List content indexes, binds flags summary: Display index blob summary, superseded: Include inactive index files superseded by compaction, sort: Index blob sort order, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, sort, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_optimize.go -->
# sources/sync-backup/kopia/cli/command_index_optimize.go

## Purpose
Index optimization command that runs index compaction with thresholds for small blobs, deleted-content age, all-index forcing, and explicit content dropping.

## APIs, Types, and Functions
Important APIs include types `commandIndexOptimize`; functions/methods `setup`, `runOptimizeCommand`; Kingpin command(s) optimize: Optimize indexes blobs.; flags max-small-blobs: Maximum number of small index blobs that can be left after compaction., drop-deleted-older-than: Drop deleted contents above given age, drop-contents: Drop contents with given IDs, all: Optimize all indexes, even those above maximum size..

## Control Flow, State, and Persistence
Control flow registers command(s) optimize: Optimize indexes blobs., binds flags max-small-blobs: Maximum number of small index blobs that can be left after compaction., drop-deleted-older-than: Drop deleted contents above given age, drop-contents: Drop contents with given IDs, all: Optimize all indexes, even those above maximum size., then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/content/indexblob plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_optimize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_recover.go -->
# sources/sync-backup/kopia/cli/command_index_recover.go

## Purpose
Dangerous index recovery command that reconstructs index entries from pack blobs, optionally deleting old indexes and committing recovered metadata only with explicit flags.

## APIs, Types, and Functions
Important APIs include types `commandIndexRecover`; functions/methods `setup`, `run`, `recoverIndexesFromAllPacks`, `recoverIndexFromSinglePackFile`; Kingpin command(s) recover: Recover indexes from pack blobs; flags blob-prefixes: Prefixes of pack blobs to recover from (default=all packs), blobs: Names of pack blobs to recover from (default=all packs), parallel: Recover parallelism, ignore-errors: Ignore errors when recovering, delete-indexes: Delete all indexes before recovering, commit: Commit recovered content.

## Control Flow, State, and Persistence
Control flow registers command(s) recover: Recover indexes from pack blobs, binds flags blob-prefixes: Prefixes of pack blobs to recover from (default=all packs), blobs: Names of pack blobs to recover from (default=all packs), parallel: Recover parallelism, ignore-errors: Ignore errors when recovering, delete-indexes: Delete all indexes before recovering, commit: Commit recovered content, then runs through a direct repository write action. The implementation iterates blob storage, deletes blob storage objects, reconstructs index entries from pack blobs. State and persistence: touches blob storage objects and metadata, content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sync/atomic, time, github.com/pkg/errors, golang.org/x/sync/errgroup, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/repo, kopia/repo/blob, kopia/repo/content, kopia/repo/content/indexblob plus external packages context, sync/atomic, time, github.com/pkg/errors, golang.org/x/sync/errgroup.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_index_recover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs.go -->
# sources/sync-backup/kopia/cli/command_logs.go

## Purpose
Command group root for encrypted repository log browsing and cleanup. It registers list/show/cleanup commands.

## APIs, Types, and Functions
Important APIs include types `commandLogs`; functions/methods `setup`; Kingpin command(s) logs: Commands to manipulate logs stored in the repository..

## Control Flow, State, and Persistence
Control flow registers command(s) logs: Commands to manipulate logs stored in the repository., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_logs_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_cleanup.go -->
# sources/sync-backup/kopia/cli/command_logs_cleanup.go

## Purpose
Log cleanup command that applies retention limits for encrypted repository log sessions, supporting age/count/total-size limits and dry-run mode.

## APIs, Types, and Functions
Important APIs include types `commandLogsCleanup`; functions/methods `setup`, `run`; Kingpin command(s) cleanup: Clean up logs; flags max-age: Maximal age, max-count: Maximal number of files to keep, max-total-size-mb: Maximal total size in MiB, dry-run: Do not delete.

## Control Flow, State, and Persistence
Control flow registers command(s) cleanup: Clean up logs, binds flags max-age: Maximal age, max-count: Maximal number of files to keep, max-total-size-mb: Maximal total size in MiB, dry-run: Do not delete, then runs through a direct repository write action. The implementation deletes blob storage objects. State and persistence: touches maintenance params, schedule, and maintenance statistics, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/maintenance plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_list.go -->
# sources/sync-backup/kopia/cli/command_logs_list.go

## Purpose
Log listing command that discovers encrypted repository log sessions and prints their identifiers, sizes, timestamps, and summaries.

## APIs, Types, and Functions
Important APIs include types `commandLogsList`; functions/methods `setup`, `run`; Kingpin command(s) list: List logs..

## Control Flow, State, and Persistence
Control flow registers command(s) list: List logs., then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_session.go -->
# sources/sync-backup/kopia/cli/command_logs_session.go

## Purpose
Shared log session discovery and filtering support for log commands. It parses all/latest/age selectors and filters repository log blob sessions.

## APIs, Types, and Functions
Important APIs include types `logSessionInfo`, `logSelectionCriteria`; functions/methods `setup`, `any`, `filterLogSessions`, `getLogSessions`, `filterLogSessions`; flags all: Show all logs, latest: Include last N logs, by default the last one is shown, younger-than: Include logs younger than X (e.g. '1h'), older-than: Include logs older than X (e.g. '1h').

## Control Flow, State, and Persistence
Control flow binds flags all: Show all logs, latest: Include last N logs, by default the last one is shown, younger-than: Include logs younger than X (e.g. '1h'), older-than: Include logs older than X (e.g. '1h'), then runs through a test/helper flow. The implementation iterates blob storage. State and persistence: touches encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, strconv, strings, time, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/internal/clock, github.com/kopia/kopia/internal/repodiag, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/clock, kopia/internal/repodiag, kopia/repo/blob plus external packages context, sort, strconv, strings, time, plus 2 more.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_show.go -->
# sources/sync-backup/kopia/cli/command_logs_show.go

## Purpose
Log show command that selects log sessions, decrypts log blobs, and streams merged or selected log content through the output formatter.

## APIs, Types, and Functions
Important APIs include types `commandLogsShow`; functions/methods `setup`, `run`; Kingpin command(s) show: Show contents of the log. When no flags or arguments are specified, only the last log is shown.; arguments session-id: Log Session ID to show.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show contents of the log. When no flags or arguments are specified, only the last log is shown., accepts arguments session-id: Log Session ID to show, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, slices, github.com/pkg/errors, github.com/kopia/kopia/internal/blobcrypto, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/blobcrypto, kopia/internal/gather, kopia/repo plus external packages context, slices, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_test.go -->
# sources/sync-backup/kopia/cli/command_logs_test.go

## Purpose
Test coverage for `command_logs` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestLogsCommands, TestLogsMaintenance, TestLogsMaintenanceSet.

## APIs, Types, and Functions
Important APIs include functions/methods `TestLogsCommands`, `TestLogsMaintenance`, `TestLogsMaintenanceSet`; tests TestLogsCommands, TestLogsMaintenance, TestLogsMaintenanceSet.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches encrypted repository log blobs, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports strings, testing, time, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages strings, testing, time, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. test signals come from named tests TestLogsCommands, TestLogsMaintenance, TestLogsMaintenanceSet.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_ls.go -->
# sources/sync-backup/kopia/cli/command_ls.go

## Purpose
Repository object listing command analogous to `ls`. It resolves snapshot/object paths and prints directory entries with long, recursive, human-readable, object-ID, and error-summary modes.

## APIs, Types, and Functions
Important APIs include types `commandList`; functions/methods `setup`, `run`, `listDirectory`, `printDirectoryEntry`, `nameToDisplay`; Kingpin command(s) list: List a directory stored in repository object.; flags long: Long output, human-readable: Show human-readable sizes, recursive: Recursive output, show-object-id: Show object IDs, error-summary: Emit error summary; arguments object-path: Path.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List a directory stored in repository object., binds flags long: Long output, human-readable: Show human-readable sizes, recursive: Recursive output, show-object-id: Show object IDs, error-summary: Emit error summary, accepts arguments object-path: Path, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository connection/session state and command-local option fields. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, strings, github.com/pkg/errors, github.com/kopia/kopia/fs, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/object, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/fs, kopia/repo, kopia/repo/object, kopia/snapshot/snapshotfs plus external packages context, fmt, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance.go -->
# sources/sync-backup/kopia/cli/command_maintenance.go

## Purpose
Command group root for repository maintenance commands. It wires info/run/set behavior under `maintenance`.

## APIs, Types, and Functions
Important APIs include types `commandMaintenance`; functions/methods `setup`; Kingpin command(s) maintenance: Maintenance commands..

## Control Flow, State, and Persistence
Control flow registers command(s) maintenance: Maintenance commands., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_info.go -->
# sources/sync-backup/kopia/cli/command_maintenance_info.go

## Purpose
Maintenance information command that reads maintenance params, schedule, owner, and cycle statistics and prints quick/full maintenance status with human-readable messages.

## APIs, Types, and Functions
Important APIs include types `commandMaintenanceInfo`, `MaintenanceInfo`; functions/methods `setup`, `run`, `displayCycleInfo`, `getMessageFromRun`; Kingpin command(s) info: Display maintenance information.

## Control Flow, State, and Persistence
Control flow registers command(s) info: Display maintenance information, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, time, github.com/pkg/errors, github.com/kopia/kopia/internal/clock, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance, github.com/kopia/kopia/repo/maintenancestats. It integrates with Kopia repository internals such as kopia/internal/clock, kopia/internal/units, kopia/repo, kopia/repo/maintenance, kopia/repo/maintenancestats plus external packages context, strings, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_maintenance_info_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_info_test.go -->
# sources/sync-backup/kopia/cli/command_maintenance_info_test.go

## Purpose
Test coverage for `command_maintenance_info` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestMaintenanceInfoSimple.

## APIs, Types, and Functions
Important APIs include functions/methods `TestMaintenanceInfoSimple`; tests TestMaintenanceInfoSimple.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/kopia/kopia/cli, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/cli, kopia/internal/testutil, kopia/tests/testenv plus external packages testing.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestMaintenanceInfoSimple.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_run.go -->
# sources/sync-backup/kopia/cli/command_maintenance_run.go

## Purpose
Maintenance run command that triggers quick or full repository maintenance, with safety flags and optional force override for owner checks.

## APIs, Types, and Functions
Important APIs include types `commandMaintenanceRun`; functions/methods `setup`, `run`; Kingpin command(s) run: Run repository maintenance; flags full: Full maintenance, force: Run maintenance even if not owned (unsafe).

## Control Flow, State, and Persistence
Control flow registers command(s) run: Run repository maintenance, binds flags full: Full maintenance, force: Run maintenance even if not owned (unsafe), then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance, github.com/kopia/kopia/snapshot/snapshotmaintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/maintenance, kopia/snapshot/snapshotmaintenance plus external packages context.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_set.go -->
# sources/sync-backup/kopia/cli/command_maintenance_set.go

## Purpose
Maintenance parameter update command for owner, quick/full enablement, intervals, pauses, log retention, object-lock extension, and blob-list parallelism.

## APIs, Types, and Functions
Important APIs include types `commandMaintenanceSet`; functions/methods `setup`, `setLogCleanupParametersFromFlags`, `setListBlobsParallelismFromFlags`, `setMaintenanceOwnerFromFlags`, `setMaintenanceEnabledAndIntervalFromFlags`, `setMaintenanceObjectLockExtendFromFlags`, `run`; Kingpin command(s) set: Set maintenance parameters; flags owner: Set maintenance owner user@hostname, enable-quick: Enable or disable quick maintenance, enable-full: Enable or disable full maintenance, quick-interval: Set quick maintenance interval, full-interval: Set full maintenance interval, pause-quick: Pause quick maintenance for a specified duration, pause-full: Pause full maintenance for a specified duration, max-retained-log-count: Set maximum number of log sessions to retain, max-retained-log-age: Set maximum age of log sessions to retain, max-retained-log-size-mb: Set maximum total size of log sessions, plus 2 more.

## Control Flow, State, and Persistence
Control flow registers command(s) set: Set maintenance parameters, binds flags owner: Set maintenance owner user@hostname, enable-quick: Enable or disable quick maintenance, enable-full: Enable or disable full maintenance, quick-interval: Set quick maintenance interval, full-interval: Set full maintenance interval, pause-quick: Pause quick maintenance for a specified duration, pause-full: Pause full maintenance for a specified duration, max-retained-log-count: Set maximum number of log sessions to retain, plus 4 more, then runs through a direct repository write action. The implementation iterates blob storage, persists maintenance parameters, persists maintenance schedule. State and persistence: touches maintenance params, schedule, and maintenance statistics, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/maintenance plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_maintenance_set_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_set_test.go -->
# sources/sync-backup/kopia/cli/command_maintenance_set_test.go

## Purpose
Test coverage for `command_maintenance_set` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestMaintenanceSetExtendObjectLocks, TestMaintenanceSetListParallelism.

## APIs, Types, and Functions
Important APIs include functions/methods `TestMaintenanceSetExtendObjectLocks`, `TestMaintenanceSetListParallelism`, `TestInvalidExtendRetainOptions`; tests TestMaintenanceSetExtendObjectLocks, TestMaintenanceSetListParallelism.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, time, github.com/stretchr/testify/require, github.com/kopia/kopia/cli, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/cli, kopia/internal/testutil, kopia/repo/blob, kopia/tests/testenv plus external packages testing, time, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. test signals come from named tests TestMaintenanceSetExtendObjectLocks, TestMaintenanceSetListParallelism.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_maintenance_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest.go -->
# sources/sync-backup/kopia/cli/command_manifest.go

## Purpose
Command group root for raw manifest operations. It wires list/show/delete commands over repository manifest metadata.

## APIs, Types, and Functions
Important APIs include types `commandManifest`; functions/methods `setup`; Kingpin command(s) manifest: Low-level commands to manipulate manifest items..

## Control Flow, State, and Persistence
Control flow registers command(s) manifest: Low-level commands to manipulate manifest items., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest_delete.go -->
# sources/sync-backup/kopia/cli/command_manifest_delete.go

## Purpose
Raw manifest deletion command that removes manifests by ID from repository metadata.

## APIs, Types, and Functions
Important APIs include types `commandManifestDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Remove manifest items; arguments item: Items to remove.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Remove manifest items, accepts arguments item: Items to remove, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest_ls.go -->
# sources/sync-backup/kopia/cli/command_manifest_ls.go

## Purpose
Raw manifest listing command that filters manifests by labels and sorts output by selected label keys.

## APIs, Types, and Functions
Important APIs include types `commandManifestList`; functions/methods `setup`, `listManifestItems`, `sortedMapValues`; Kingpin command(s) list: List manifest items; flags filter: List of key:value pairs, sort: List of keys to sort by.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List manifest items, binds flags filter: List of key:value pairs, sort: List of keys to sort by, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, sort, strings, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, fmt, sort, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest_ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest_show.go -->
# sources/sync-backup/kopia/cli/command_manifest_show.go

## Purpose
Raw manifest show command that fetches manifest payloads by ID and renders them as JSON through the output formatter.

## APIs, Types, and Functions
Important APIs include types `commandManifestShow`; functions/methods `setup`, `toManifestIDs`, `showManifestItems`; Kingpin command(s) show: Show manifest items; arguments item: List of items.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show manifest items, accepts arguments item: List of items, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, encoding/json, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/manifest. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/manifest plus external packages bytes, context, encoding/json, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_manifest_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_mount.go -->
# sources/sync-backup/kopia/cli/command_mount.go

## Purpose
Repository mount command that exposes a snapshot/object path through FUSE or WebDAV, with browse, tracing, cache, and mount-option controls.

## APIs, Types, and Functions
Important APIs include types `commandMount`; functions/methods `setup`, `newFSCache`, `run`; Kingpin command(s) mount: Mount repository object as a local filesystem.; flags browse: Open file browser, trace-fs: Trace filesystem operations, fuse-allow-other: Allows other users to access the file system., fuse-allow-non-empty-mount: Allows the mounting over a non-empty directory. The files in it will be shadowed by the freshly created mount., webdav: Use WebDAV to mount the repository object regardless of fuse availability., max-cached-entries: Limit the number of cached directory entries, max-cached-dirs: Limit the number of cached directories; arguments path: Identifier of the directory to mount., mountPoint: Mount point.

## Control Flow, State, and Persistence
Control flow registers command(s) mount: Mount repository object as a local filesystem., binds flags browse: Open file browser, trace-fs: Trace filesystem operations, fuse-allow-other: Allows other users to access the file system., fuse-allow-non-empty-mount: Allows the mounting over a non-empty directory. The files in it will be shadowed by the freshly created mount., webdav: Use WebDAV to mount the repository object regardless of fuse availability., max-cached-entries: Limit the number of cached directory entries, max-cached-dirs: Limit the number of cached directories, accepts arguments path: Identifier of the directory to mount., mountPoint: Mount point, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters, live mounted filesystem state and cache entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/skratchdot/open-golang/open, github.com/kopia/kopia/fs, github.com/kopia/kopia/fs/cachefs, github.com/kopia/kopia/fs/loggingfs, github.com/kopia/kopia/internal/mount, github.com/kopia/kopia/repo, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/fs, kopia/fs/cachefs, kopia/fs/loggingfs, kopia/internal/mount, kopia/repo, kopia/snapshot/snapshotfs plus external packages context, github.com/pkg/errors, github.com/skratchdot/open-golang/open.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification.go -->
# sources/sync-backup/kopia/cli/command_notification.go

## Purpose
Command group root for notification configuration. It registers profile, template, and sender-specific configuration subcommands.

## APIs, Types, and Functions
Important APIs include types `commandNotification`; functions/methods `setup`; Kingpin command(s) notification: Notifications.

## Control Flow, State, and Persistence
Control flow registers command(s) notification: Notifications, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_common.go -->
# sources/sync-backup/kopia/cli/command_notification_configure_common.go

## Purpose
Generic notification profile configuration helper. It loads any existing profile, validates sender type, merges typed options, optionally sends a test notification, and saves the resulting profile with severity.

## APIs, Types, and Functions
Important APIs include types `commonNotificationOptions`; functions/methods `setup`, `configureNotificationAction`, `mapKeys`; flags send-test-notification: Test the notification, min-severity: Minimum severity.

## Control Flow, State, and Persistence
Control flow binds flags send-test-notification: Test the notification, min-severity: Minimum severity, then runs through a direct repository write action. The implementation persists notification profile metadata. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, maps, slices, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/notification, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification, kopia/notification/notifyprofile, kopia/notification/sender, kopia/repo plus external packages context, maps, slices, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_email.go -->
# sources/sync-backup/kopia/cli/command_notification_configure_email.go

## Purpose
Email notification profile configuration command. It registers SMTP/from/to/cc/bcc and message format flags and delegates merge/save behavior to the common notification helper.

## APIs, Types, and Functions
Important APIs include types `commandNotificationConfigureEmail`; functions/methods `setup`; Kingpin command(s) email: E-mail notification.; flags smtp-server: SMTP server, smtp-port: SMTP port, smtp-identity: SMTP identity, smtp-username: SMTP username, smtp-password: SMTP password, mail-from: From address, mail-to: To address, mail-cc: CC address, format: Format of the message.

## Control Flow, State, and Persistence
Control flow registers command(s) email: E-mail notification., binds flags smtp-server: SMTP server, smtp-port: SMTP port, smtp-identity: SMTP identity, smtp-username: SMTP username, smtp-password: SMTP password, mail-from: From address, mail-to: To address, mail-cc: CC address, plus 1 more, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/notification/sender/email. It integrates with Kopia repository internals such as kopia/notification/sender, kopia/notification/sender/email.

## Risks and Test Signals
Risks and test signals: secret-bearing options should avoid accidental output and preserve typed config. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_email.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_pushover.go -->
# sources/sync-backup/kopia/cli/command_notification_configure_pushover.go

## Purpose
Pushover notification profile configuration command. It collects app token, user key, and format options for the common profile save/test path.

## APIs, Types, and Functions
Important APIs include types `commandNotificationConfigurePushover`; functions/methods `setup`; Kingpin command(s) pushover: Pushover notification.; flags app-token: Pushover App Token, user-key: Pushover User Key, format: Format of the message.

## Control Flow, State, and Persistence
Control flow registers command(s) pushover: Pushover notification., binds flags app-token: Pushover App Token, user-key: Pushover User Key, format: Format of the message, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/notification/sender/pushover. It integrates with Kopia repository internals such as kopia/notification/sender, kopia/notification/sender/pushover.

## Risks and Test Signals
Risks and test signals: secret-bearing options should avoid accidental output and preserve typed config. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_pushover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_testsender.go -->
# sources/sync-backup/kopia/cli/command_notification_configure_testsender.go

## Purpose
Test-sender notification profile configuration command for deterministic notification testing without external delivery infrastructure.

## APIs, Types, and Functions
Important APIs include types `commandNotificationConfigureTestSender`; functions/methods `setup`; Kingpin command(s) testsender: Testing notification.; flags format: Format of the message.

## Control Flow, State, and Persistence
Control flow registers command(s) testsender: Testing notification., binds flags format: Format of the message, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/notification/sender/testsender. It integrates with Kopia repository internals such as kopia/notification/sender, kopia/notification/sender/testsender.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_testsender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_webhook.go -->
# sources/sync-backup/kopia/cli/command_notification_configure_webhook.go

## Purpose
Webhook notification profile configuration command. It parses endpoint, HTTP method, repeated headers, and format options before using the common profile save/test path.

## APIs, Types, and Functions
Important APIs include types `commandNotificationConfigureWebhook`; functions/methods `setup`; Kingpin command(s) webhook: Webhook notification.; flags endpoint: SMTP server, method: HTTP Method, http-header: HTTP Header (key:value), format: Format of the message.

## Control Flow, State, and Persistence
Control flow registers command(s) webhook: Webhook notification., binds flags endpoint: SMTP server, method: HTTP Method, http-header: HTTP Header (key:value), format: Format of the message, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports net/http, strings, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/notification/sender/webhook. It integrates with Kopia repository internals such as kopia/notification/sender, kopia/notification/sender/webhook plus external packages net/http, strings, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_configure_webhook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile.go -->
# sources/sync-backup/kopia/cli/command_notification_profile.go

## Purpose
Command group root and shared profile-name flag for notification profiles. It also supplies autocomplete by listing profiles from the repository.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfile`, `notificationProfileFlag`; functions/methods `setup`, `setup`, `listNotificationProfiles`; Kingpin command(s) profile: Manage notification profiles; flags profile-name: Profile name.

## Control Flow, State, and Persistence
Control flow registers command(s) profile: Manage notification profiles, binds flags profile-name: Profile name, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, github.com/alecthomas/kingpin/v2, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifyprofile, kopia/repo plus external packages context, strings, github.com/alecthomas/kingpin/v2.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_notification_profile_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_configure.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_configure.go

## Purpose
Command group root for configuring notification profile sender types. It delegates email, pushover, test sender, and webhook setup to sibling files.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfileConfigure`; functions/methods `setup`; Kingpin command(s) configure: Setup notifications.

## Control Flow, State, and Persistence
Control flow registers command(s) configure: Setup notifications, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_configure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_delete.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_delete.go

## Purpose
Notification profile delete command that removes a named notification profile from repository metadata.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfileDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Delete notification profile.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Delete notification profile, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifyprofile, kopia/repo plus external packages context.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_internal_test.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_internal_test.go

## Purpose
Test coverage for `command_notification_profile_internal` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationProfileAutocomplete.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationProfileAutocomplete`; tests TestNotificationProfileAutocomplete.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The implementation persists notification profile metadata. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/repotesting, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender. It integrates with Kopia repository internals such as kopia/internal/repotesting, kopia/notification/notifyprofile, kopia/notification/sender plus external packages testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestNotificationProfileAutocomplete.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_list.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_list.go

## Purpose
Notification profile listing command that summarizes configured sender profiles, sender type, severity, and optional raw output.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfileList`; functions/methods `setup`, `run`, `getProfileSummary`; Kingpin command(s) list: List notification profiles; flags raw: Raw output.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List notification profiles, binds flags raw: Raw output, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, github.com/pkg/errors, github.com/kopia/kopia/notification, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification, kopia/notification/notifyprofile, kopia/notification/sender, kopia/repo plus external packages context, fmt, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_send.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_send.go

## Purpose
Notification profile test-send command that loads a named profile, creates its sender, and sends a test notification through repository notification plumbing.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfileTest`; functions/methods `setup`, `run`; Kingpin command(s) test: Send test notification.

## Control Flow, State, and Persistence
Control flow registers command(s) test: Send test notification, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/notification, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification, kopia/notification/notifyprofile, kopia/notification/sender, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_send.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_show.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_show.go

## Purpose
Notification profile show command that displays a named profile either as raw configuration or formatted summary.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfileShow`; functions/methods `setup`, `run`; Kingpin command(s) show: Show notification profile; flags raw: Raw output.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show notification profile, binds flags raw: Raw output, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/notification, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification, kopia/notification/notifyprofile, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_test.go -->
# sources/sync-backup/kopia/cli/command_notification_profile_test.go

## Purpose
Test coverage for `command_notification_profile` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationProfile, TestNotificationProfile_WebHook.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationProfile`, `TestNotificationProfile_WebHook`; tests TestNotificationProfile, TestNotificationProfile_WebHook.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender/webhook, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/notification/notifyprofile, kopia/notification/sender/webhook, kopia/tests/testenv plus external packages testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestNotificationProfile, TestNotificationProfile_WebHook.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_profile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template.go -->
# sources/sync-backup/kopia/cli/command_notification_template.go

## Purpose
Command group root and shared template-name argument for notification templates. It provides repository-backed autocomplete of available template names.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplate`, `notificationTemplateNameArg`; functions/methods `setup`, `listNotificationTemplates`, `setup`; Kingpin command(s) template: Manage templates; arguments template: Template name.

## Control Flow, State, and Persistence
Control flow registers command(s) template: Manage templates, accepts arguments template: Template name, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/alecthomas/kingpin/v2, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context, github.com/alecthomas/kingpin/v2.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_notification_template_test.go` provides direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_internal_test.go -->
# sources/sync-backup/kopia/cli/command_notification_template_internal_test.go

## Purpose
Test coverage for `command_notification_template_internal` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationTemplatesAutocomplete.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationTemplatesAutocomplete`; tests TestNotificationTemplatesAutocomplete.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/repotesting. It integrates with Kopia repository internals such as kopia/internal/repotesting plus external packages testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestNotificationTemplatesAutocomplete.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_list.go -->
# sources/sync-backup/kopia/cli/command_notification_template_list.go

## Purpose
Notification template listing command that enumerates custom notification templates stored in repository metadata.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateList`; functions/methods `setup`, `run`; Kingpin command(s) list: List templates.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List templates, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/pkg/errors, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context, sort, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_remove.go -->
# sources/sync-backup/kopia/cli/command_notification_template_remove.go

## Purpose
Notification template remove command that deletes a custom template override by name.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateRemove`; functions/methods `setup`, `run`; Kingpin command(s) remove: Remove the notification template.

## Control Flow, State, and Persistence
Control flow registers command(s) remove: Remove the notification template, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_set.go -->
# sources/sync-backup/kopia/cli/command_notification_template_set.go

## Purpose
Notification template set command that reads replacement template text from stdin, file, or editor and saves it as a repository template override.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateSet`; functions/methods `setup`, `run`, `launchEditor`; Kingpin command(s) set: Set the notification template; flags from-stdin: Read new template from stdin, from-file: Read new template from file, editor: Edit template using default editor.

## Control Flow, State, and Persistence
Control flow registers command(s) set: Set the notification template, binds flags from-stdin: Read new template from stdin, from-file: Read new template from file, editor: Edit template using default editor, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, io, os, github.com/pkg/errors, github.com/kopia/kopia/internal/editor, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/editor, kopia/notification/notifytemplate, kopia/repo plus external packages context, io, os, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: external editor flow must reject invalid or unchanged JSON safely. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_show.go -->
# sources/sync-backup/kopia/cli/command_notification_template_show.go

## Purpose
Notification template show command that renders custom or original templates, optionally converting markdown/template output to HTML and opening it.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateShow`; functions/methods `setup`, `run`; Kingpin command(s) show: Show template; flags format: Template format, original: Show original template, html: Convert the output to HTML.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show template, binds flags format: Template format, original: Show original template, html: Convert the output to HTML, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, os, path/filepath, strings, github.com/pkg/errors, github.com/skratchdot/open-golang/open, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context, os, path/filepath, strings, github.com/pkg/errors, plus 1 more.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_test.go -->
# sources/sync-backup/kopia/cli/command_notification_template_test.go

## Purpose
Test coverage for `command_notification_template` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationTemplates.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationTemplates`, `verifyTemplateContents`, `verifyHasLine`; tests TestNotificationTemplates.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, os, slices, strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/editor, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/editor, kopia/notification/notifytemplate, kopia/tests/testenv plus external packages context, os, slices, strings, testing, plus 1 more.

## Risks and Test Signals
Risks and test signals: external editor flow must reject invalid or unchanged JSON safely. test signals come from named tests TestNotificationTemplates.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_notification_template_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy.go -->
# sources/sync-backup/kopia/cli/command_policy.go

## Purpose
Command group root and target flag parsing for snapshot policy commands. It selects global, host/user/path, or explicit policy targets for sibling policy operations.

## APIs, Types, and Functions
Important APIs include types `commandPolicy`, `policyTargetFlags`; functions/methods `setup`, `setup`, `policyTargets`; Kingpin command(s) policy: Commands to manipulate snapshotting policies.; flags global: Select the global policy.; arguments target: Select a particular policy (a per-host policy `@host`, a per-user policy `user@host`, a per-path policy `user@host:path` or a local path). Use --global to target the global policy..

## Control Flow, State, and Persistence
Control flow registers command(s) policy: Commands to manipulate snapshotting policies., binds flags global: Select the global policy., accepts arguments target: Select a particular policy (a per-host policy `@host`, a per-user policy `user@host`, a per-path policy `user@host:path` or a local path). Use --global to target the global policy., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches snapshot policy manifests. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/manifest, github.com/kopia/kopia/snapshot, github.com/kopia/kopia/snapshot/policy. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/manifest, kopia/snapshot, kopia/snapshot/policy plus external packages context, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_edit.go -->
# sources/sync-backup/kopia/cli/command_policy_edit.go

## Purpose
Policy edit command that opens an existing snapshot policy as pretty JSON with embedded help text, launches an editor, validates JSON changes, and persists updates if modified.

## APIs, Types, and Functions
Important APIs include types `commandPolicyEdit`; functions/methods `setup`, `run`, `prettyJSON`, `jsonEqual`, `insertHelpText`; Kingpin command(s) edit: Edit policy..

## Control Flow, State, and Persistence
Control flow registers command(s) edit: Edit policy., then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches snapshot policy manifests. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, encoding/json, fmt, strings, github.com/pkg/errors, github.com/kopia/kopia/internal/editor, github.com/kopia/kopia/repo, github.com/kopia/kopia/snapshot/policy. It integrates with Kopia repository internals such as kopia/internal/editor, kopia/repo, kopia/snapshot/policy plus external packages bytes, context, encoding/json, fmt, strings, plus 1 more.

## Risks and Test Signals
Risks and test signals: external editor flow must reject invalid or unchanged JSON safely. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_edit.go -->
