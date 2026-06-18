# subset-b-009139 research

Grouped research report for Kopia CLI/server/snapshot/user/storage helpers and filesystem cache abstractions. Each section preserves the exact source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_start.go -->
# sources/sync-backup/kopia/cli/command_server_start.go

## Purpose
Implements `kopia server start`, including server option assembly, repository initialization, HTTP/GRPC routing, shutdown integration, authentication setup, Prometheus registration, UI/static serving, and optional KopiaUI notification output.

## Important APIs, Types, And Functions
Key symbols are `commandServerStart`, `setup`, `serverStartOptions`, `initRepositoryPossiblyAsync`, `run`, `setupHandlers`, `initPrometheus`, `stripProtocol`, and `getAuthenticator`. It feeds `server.Options`, uses `serverFlags`/`connectOptions`, and composes authenticators from htpasswd, one-shot passwords, server-control credentials, and repository user profiles.

## Control Flow
`setup` registers flags, then `run` validates insecure bind rules, builds `server.Options`, creates `server.Server`, initializes the repository synchronously or via retrying async mode, wires HTTP shutdown callbacks, creates a Gorilla router, optionally wraps it with GRPC routing, handles stdin-driven shutdown, registers SIGHUP refresh, and delegates serving to TLS/listener code.

## State And Persistence Behavior
Repository state is opened through the app service and installed into the server, then cleared on exit. It persists UI preferences path, auth cookie signing key, persistent log preference, scheduler/debug settings, and notification template settings through `server.Options`. Random passwords are intentionally process-local and printed to stderr only.

## Dependencies And Integration Points
Integrates `internal/server`, `internal/auth`, `insecureserverbind`, Gorilla mux, Prometheus `/metrics`, repository open/close services, notification senders, system signal reload hooks, and TLS serving from `command_server_tls.go`.

## Risks And Edge Cases
Security risk is concentrated around `--without-password`, `--insecure`, random credentials printed to stderr, and disabled CSRF checks. `io.ReadFull(rand.Reader, b)` ignores errors, so randomness failure is not surfaced. Shutdown paths must avoid deadlocking repository cleanup while HTTP/GRPC connections drain.

## Test Signals
Covered indirectly by CLI/server tests such as user-hash and terminate tests. High-value tests are insecure bind rejection, auth mode combinations, async repo connection retry, SIGHUP refresh, stdin shutdown, and server-control credentials.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_start.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_status.go -->
# sources/sync-backup/kopia/cli/command_server_status.go

## Purpose
Implements `kopia server status`, a server-client command that lists sources currently known by a running server control API.

## Important APIs, Types, And Functions
Defines `commandServerStatus` with `serverClientFlags`, text output, and a `remote` filter flag. `runServerStatus` calls `KopiaAPIClient.Get` on `control/sources` and decodes `serverapi.SourcesResponse`.

## Control Flow
The command is registered under `server status`. At execution it connects via server action plumbing, requests source status, filters out entries marked `REMOTE` unless `--remote` was provided, and prints status/source pairs.

## State And Persistence Behavior
It does not mutate repository state. It observes transient server-side source status returned by the control endpoint.

## Dependencies And Integration Points
Depends on `internal/apiclient`, `internal/serverapi`, server authentication flags, and the server control API registered by `command_server_start.go`.

## Risks And Edge Cases
The string comparison to `REMOTE` is a loose contract with server API status values. Network/auth errors are wrapped as list failures, and output order is whatever the server returns.

## Test Signals
Useful signals are server integration tests that start a server, register local and remote sources, and verify `--remote` changes filtering without altering API requests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_status.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle.go -->
# sources/sync-backup/kopia/cli/command_server_throttle.go

## Purpose
Provides the parent `kopia server throttle` command and groups runtime throttle inspection and mutation subcommands for a running server.

## Important APIs, Types, And Functions
Defines `commandServerThrottle` with `get` and `set` subcommands. Its only method, `setup`, creates the parent command and delegates setup to `commandServerThrottleGet` and `commandServerThrottleSet`.

## Control Flow
There is no command body beyond registration. Control flow enters the get or set child command after kingpin parses the selected subcommand.

## State And Persistence Behavior
This file has no state of its own. Runtime throttle state lives in the server and is fetched or updated by the child command implementations.

## Dependencies And Integration Points
Integrates with `command_server_throttle_get.go`, `command_server_throttle_set.go`, and shared throttle formatting/parsing helpers in `throttle_get.go` and `throttle_set.go`.

## Risks And Edge Cases
The main risk is only command-surface drift: if a child command changes names or flags, this parent must still register them in the intended CLI tree.

## Test Signals
Test signals should verify command discovery/help and that both child commands are reachable through the `server throttle` namespace.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_get.go -->
# sources/sync-backup/kopia/cli/command_server_throttle_get.go

## Purpose
Implements `kopia server throttle get`, which reads throttling limits from a running server and emits either human-readable text or JSON.

## Important APIs, Types, And Functions
Defines `commandServerThrottleGet`, embeds `serverClientFlags`, and reuses `commonThrottleGet`. `run` uses `KopiaAPIClient.Get` against `control/throttle` into `throttling.Limits`.

## Control Flow
After server-action connection, it performs one GET request, then delegates formatting to `commonThrottleGet.output`.

## State And Persistence Behavior
No persistent state is changed. It reads the server's current in-memory or repository-backed throttling limits as exposed by control API.

## Dependencies And Integration Points
Depends on `internal/apiclient`, `repo/blob/throttling`, server client flag plumbing, and common output helpers.

## Risks And Edge Cases
Failure modes are network/auth/API errors and stale assumptions about the `control/throttle` payload shape. JSON output depends on `throttling.Limits` tags.

## Test Signals
Tests should exercise JSON and text output for unlimited and finite limits, plus server API failure wrapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_get.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_set.go -->
# sources/sync-backup/kopia/cli/command_server_throttle_set.go

## Purpose
Implements `kopia server throttle set`, allowing runtime modification of a running server's throttling limits.

## Important APIs, Types, And Functions
Defines `commandServerThrottleSet`, `serverClientFlags`, and `commonThrottleSet`. `run` GETs current `throttling.Limits`, applies CLI-specified changes, then PUTs to `control/throttle` with `serverapi.Empty` response.

## Control Flow
The command reads current limits first so unspecified flags are preserved. If `commonThrottleSet.apply` reports zero changes, it logs `No changes made` and skips the PUT. Otherwise it sends the changed limits to the server.

## State And Persistence Behavior
Mutates server-side throttle state through the control API. The file itself stores only parsed flag strings and a temporary change count.

## Dependencies And Integration Points
Depends on the shared throttle parser, `internal/apiclient`, `internal/serverapi`, and the server control endpoint.

## Risks And Edge Cases
String parsing accepts any float or int without local nonnegative validation, so backend enforcement matters. Partial update is all-or-nothing at API level, but concurrent writers can race because the command uses read-modify-write.

## Test Signals
Useful tests cover individual fields, `unlimited`/`-`, no-change behavior, parse errors, and preservation of unrelated existing limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_set.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_tls.go -->
# sources/sync-backup/kopia/cli/command_server_tls.go

## Purpose
Holds TLS and listener support for `server start`: certificate generation, socket activation, TCP or Unix listener creation, serving with persisted or in-memory TLS, and insecure HTTP fallback.

## Important APIs, Types, And Functions
Important functions are `generateServerCertificate`, `startServerWithOptionalTLS`, `maybeGenerateTLS`, `startServerWithOptionalTLSAndListener`, `showServerUIPrompt`, and `checkErrServerClosed`. It uses `tlsutil`, systemd socket activation, and insecure-bind validation.

## Control Flow
`startServerWithOptionalTLS` obtains an activated socket or creates one from `httpServer.Addr`, validates the resolved listener address, and delegates. The listener path optionally writes generated cert/key files, serves with provided PEMs, serves with in-memory TLS, or rejects plaintext unless `--insecure` is set.

## State And Persistence Behavior
Persistent state is limited to generated cert/key PEM files when both output paths and `--tls-generate-cert` are provided. In-memory certificates are ephemeral. The server address and certificate fingerprint are printed to stderr for client discovery.

## Dependencies And Integration Points
Integrates `command_server_start.go`, `internal/tlsutil`, `insecureserverbind`, `coreos/go-systemd/activation`, Go `net/http`, and TLS configuration.

## Risks And Edge Cases
Risks include accidentally overwriting certificates, printing sensitive connection bootstrap material to shared stderr, trusting activated sockets with unexpected network exposure, and only using TLS 1.3 in the in-memory config while `ServeTLS` file mode uses Go defaults.

## Test Signals
Tests should cover generated-file refusal when paths exist, Unix socket address formatting, activated socket count errors, HTTP rejection without `--insecure`, fingerprint output, and graceful `http.ErrServerClosed` handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_tls.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session.go -->
# sources/sync-backup/kopia/cli/command_session.go

## Purpose
Provides the hidden `kopia session` command namespace for repository session maintenance commands.

## Important APIs, Types, And Functions
Defines `commandSession` with a single `list` child, and `setup` registers the hidden parent and delegates to `commandSessionList.setup`.

## Control Flow
There is no runtime flow beyond CLI registration. Selecting `session list` enters the child command.

## State And Persistence Behavior
This file has no mutable or persistent state; active session information is read by the child command from repository content state.

## Dependencies And Integration Points
Depends only on local command registration abstractions and `command_session_list.go`.

## Risks And Edge Cases
Because it is hidden, regressions may be missed by normal help/command-surface tests. Adding more session subcommands requires this parent to be updated.

## Test Signals
A command discovery test can assert the hidden parent still accepts the `list` child and aliases from the child.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session_list.go -->
# sources/sync-backup/kopia/cli/command_session_list.go

## Purpose
Implements hidden `kopia session list`, which prints active content sessions from a direct repository.

## Important APIs, Types, And Functions
Defines `commandSessionList` and `run`. It requires `repo.DirectRepository`, calls `ContentReader().ListActiveSessions`, and prints ID, user, host, start time, and checkpoint time.

## Control Flow
The direct repository read action opens the repo, `run` queries active sessions once, then formats each returned session on stdout.

## State And Persistence Behavior
It is read-only. The observed state is repository session metadata maintained by the content manager, not CLI-local state.

## Dependencies And Integration Points
Depends on direct repository access rather than server/client repository interfaces, and on shared timestamp formatting.

## Risks And Edge Cases
The command will not work through indirect/server repositories. Output is plain text only and may expose user/host details.

## Test Signals
Tests should set up active sessions or mock content reader behavior and verify formatting, empty lists, and error wrapping from `ListActiveSessions`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session_list.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_show.go -->
# sources/sync-backup/kopia/cli/command_show.go

## Purpose
Implements `kopia show`/`cat`, which opens a repository object by object ID or object-path syntax and streams its bytes to stdout.

## Important APIs, Types, And Functions
Defines `commandShow` with `path` and text output. `run` uses `snapshotfs.ParseObjectIDWithPath`, `repo.OpenObject`, and `iocopy.JustCopy`.

## Control Flow
At execution the object path argument is parsed, the repository object reader is opened, deferred closed, and copied directly to stdout.

## State And Persistence Behavior
It does not mutate repository data. State is limited to the opened object reader and stdout stream; object identity can include nested snapshotfs path parsing.

## Dependencies And Integration Points
Depends on repository reader actions, `snapshotfs` object ID parsing, and the internal copy helper.

## Risks And Edge Cases
Large objects stream without buffering, but binary output goes directly to stdout. Parse errors and open errors include user input in messages. Consumers must not expect decompression or JSON formatting here; that is handled by other show utilities.

## Test Signals
Test signals are object parse/open failure tests and a successful copy of known object content, including binary-safe output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_show.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot.go -->
# sources/sync-backup/kopia/cli/command_snapshot.go

## Purpose
Registers the `kopia snapshot`/`snap` command namespace and wires all snapshot-management subcommands into the CLI.

## Important APIs, Types, And Functions
The `commandSnapshot` struct owns `copyHistory`, `moveHistory`, `create`, `delete`, `estimate`, `expire`, `fix`, `list`, `migrate`, `pin`, `restore`, and `verify` command objects.

## Control Flow
`setup` creates the parent command, then calls each child setup method. Copy and move history reuse the same command implementation with different mode flags.

## State And Persistence Behavior
This file has no runtime state beyond child command structs. Persistent snapshot behavior is implemented by the child files.

## Dependencies And Integration Points
Integrates many CLI modules under the `advancedAppServices` capability boundary because some children need advanced repository/password services.

## Risks And Edge Cases
Risks are command registration omissions and alias conflicts. A child setup failure or renamed command can make functionality unreachable even if implementation files compile.

## Test Signals
Test signals are CLI help/parse tests and smoke tests for each subcommand under both `snapshot` and `snap` aliases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_copy_move_history.go -->
# sources/sync-backup/kopia/cli/command_snapshot_copy_move_history.go

## Purpose
Implements `snapshot copy-history` and `snapshot move-history`, used to preserve snapshot history when hostnames, usernames, or source paths change.

## Important APIs, Types, And Functions
Key APIs include `commandSnapshotCopyMoveHistory`, `setup`, `snapshotCopyMoveHelp`, `run`, `getCopySnapshotAction`, `getCopySourceAndDestination`, `snapshotExists`, `sameSnapshot`, and `getCopyDestination`.

## Control Flow
The command parses a source and optional destination, rejects destination username/path overrides that would collapse multiple source identities, lists source and destination snapshots, computes destination source info for each manifest, skips already matching destinations, saves copied manifests with a cleared ID, and deletes originals for move mode.

## State And Persistence Behavior
It mutates snapshot manifest metadata only. Copy creates new manifests pointing at existing root object IDs; move additionally deletes source manifests. Dry-run logs intended operations without writes.

## Dependencies And Integration Points
Depends on `snapshot.ParseSourceInfo`, snapshot listing/saving, repository writer deletion, and shared timestamp formatting.

## Risks And Edge Cases
The core risk is accidental history collapse or duplicate history if source/destination matching is too broad. `sameSnapshot` only compares start time and root object ID, so metadata differences are ignored for duplicate detection.

## Test Signals
Tests should cover the documented source/destination matrix, dry-run no-write behavior, duplicate detection, move deletion, and invalid destination path/user cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_copy_move_history.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_create.go -->
# sources/sync-backup/kopia/cli/command_snapshot_create.go

## Purpose
Implements `snapshot create`, the main local backup path. It handles source selection, all-source scheduled backups, uploader setup, tags, pins, time overrides, stdin snapshots, retention application, manual policy marking, reporting, and notifications.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotCreate`, constants `maxSnapshotDescriptionLength` and `timeFormat`, `run`, `setupUploader`, `snapshotSingleSource`, `reportSnapshotStatus`, `getLocalBackupPaths`, `shouldSnapshotSource`, `getContentToSnapshot`, `getTags`, `validateStartEndTime`, and `parseFullSource`.

## Control Flow
`run` validates flags, maybe upgrades the repo, expands `--all`, validates description/timestamps/tags, builds an uploader, iterates sources, prepares local or stdin content, uploads each source, collects errors, optionally sends a multi-snapshot notification, and flushes the repository. `snapshotSingleSource` finds previous manifests, gets the policy tree, uploads, adjusts metadata, saves the manifest unless identical snapshots are ignored, applies retention, optionally sets manual policy, flushes per source, and reports status.

## State And Persistence Behavior
It persists uploaded file/dir objects, snapshot manifests, pins, tags, descriptions, start/end time overrides, retention deletions, manual scheduling policy markers, and repository flush state. Stdin snapshots are modeled as a virtual directory with a streaming file.

## Dependencies And Integration Points
Integrates local filesystem entries, virtualfs, snapshot upload, policy trees, retention, notification templates, progress services, repository writers, and timestamp formatting.

## Risks And Edge Cases
Risks include continuing after `getContentToSnapshot` errors and then calling `snapshotSingleSource` with a nil entry, misuse of source override collapsing identities, timestamp override duration math, retention side effects after each save, and long descriptions/tags needing validation. Flush behavior differs with `--flush-per-source`.

## Test Signals
Tests should cover normal snapshots, `--all`, stdin, tags, pins, time overrides, ignored identical snapshots, fatal/ignored upload errors, notification severity, and flush behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_create.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_delete.go -->
# sources/sync-backup/kopia/cli/command_snapshot_delete.go

## Purpose
Implements snapshot deletion by manifest ID, root object ID, or all snapshots for a source, with explicit confirmation required for actual writes.

## Important APIs, Types, And Functions
Important functions are `run`, `snapshotDeleteSources`, `deleteSnapshot`, and `deleteSnapshotsByRootObjectID`. It uses `snapshot.LoadSnapshot`, `snapshot.ListSnapshotManifests`, `snapshot.FindSnapshotsByRootObjectID`, and `repo.DeleteManifest`.

## Control Flow
`run` dispatches to source deletion when `--all-snapshots-for-source` is set. Otherwise each provided ID is first treated as a manifest ID, then as a root object ID if the manifest is not found. `deleteSnapshot` logs dry-run output unless `--delete` was provided.

## State And Persistence Behavior
Persistent mutation is manifest deletion only; object content remains subject to repository maintenance/garbage collection. Dry-run leaves repository state unchanged.

## Dependencies And Integration Points
Integrates snapshot manifest loading/listing, object ID parsing, repository writer deletion, and timestamp formatting.

## Risks And Edge Cases
A root object ID can match multiple manifests, so confirmation text must be clear. Source deletion errors if no snapshots match. The hidden `--unsafe-ignore-source` alias maps to confirmation and is retained for compatibility.

## Test Signals
Tests should validate dry-run versus confirmed deletion, manifest ID and root ID paths, all-source deletion, invalid IDs, and no-match errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_delete.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate.go -->
# sources/sync-backup/kopia/cli/command_snapshot_estimate.go

## Purpose
Implements `snapshot estimate`, which scans a local directory under effective policy rules and estimates included/excluded data size and upload duration.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotEstimate`, `estimateProgress`, `run`, and `showBuckets`. It uses `upload.Estimate`, `policy.TreeForSource`, local filesystem entry resolution, `snapshot.Stats`, and sample buckets.

## Control Flow
The command resolves the source to an absolute path, builds `snapshot.SourceInfo`, requires the entry to be a directory, loads the effective policy tree, runs estimator callbacks, prints included/excluded file buckets, excluded directories, error counts, and upload-time estimate based on `--upload-speed`.

## State And Persistence Behavior
It is read-only. It observes local filesystem metadata and repository policy state, but does not upload objects or write manifests.

## Dependencies And Integration Points
Integrates policy ignore rules, upload sampling, units formatting, localfs entry construction, and text output.

## Risks And Edge Cases
The path error message uses the `path` variable even if `filepath.Abs` fails before assignment. Upload speed is not locally checked for zero or negative values. Only directories are accepted, not single files.

## Test Signals
Tests cover included/excluded file sizes, ignore rules, excluded directories, and failure for non-directory sources.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_estimate_test.go

## Purpose
Tests user-visible behavior of `snapshot estimate` against a temporary filesystem repository and local directory tree.

## Important APIs, Types, And Functions
The file defines `TestSnapshotEstimate` and `TestSnapshotEstimate_NotADirectory`, using `testenv.NewCLITest`, in-process runner, `testutil.TempDirectory`, and stdout substring assertions.

## Control Flow
The main test creates three files, runs estimate, then adds ignore policies for filename and directory patterns and reruns estimate after each policy change. The second test creates a file and asserts estimation fails when the source is not a directory.

## State And Persistence Behavior
Test state includes a temporary filesystem repository, local temp files, and repository policy records created by `policy set --add-ignore`.

## Dependencies And Integration Points
Integrates the CLI command stack, repository creation, policy CLI, upload estimator, and output formatting.

## Risks And Edge Cases
Assertions depend on exact human-readable sizes and strings such as `Snapshot excludes no directories.`; formatting changes can break tests even when behavior is correct.

## Test Signals
The test is a strong signal for policy-aware estimate output. It does not cover JSON, quiet mode, upload-speed edge cases, or estimator error counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_expire.go -->
# sources/sync-backup/kopia/cli/command_snapshot_expire.go

## Purpose
Implements `snapshot expire`, which applies retention policy to selected sources or all sources and optionally deletes expired snapshots.

## Important APIs, Types, And Functions
Defines `commandSnapshotExpire`, `getSnapshotSourcesToExpire`, and `run`. It uses `snapshot.ListSources`, `snapshot.ParseSourceInfo`, and `policy.ApplyRetentionPolicy`.

## Control Flow
The command resolves target sources from `--all` or path args, sorts them for deterministic processing, applies retention for each source, and logs either dry-run counts or confirmed deletion counts.

## State And Persistence Behavior
Persistent state changes occur only when `--delete` is set; then retention application deletes snapshot manifests selected by policy. Without `--delete`, it is advisory.

## Dependencies And Integration Points
Integrates snapshot source listing, source-info parsing, repository writer actions, retention policy code, and logging.

## Risks And Edge Cases
No explicit validation prevents empty source list without `--all`; that results in a no-op. Retention policy behavior is delegated, so CLI tests need representative policies to detect regressions.

## Test Signals
Tests should cover all-source and explicit-source modes, dry-run messages, confirmed deletion, ordering, empty/no-delete cases, and parse failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_expire.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix.go

## Purpose
Provides the `snapshot fix` parent and shared snapshot-rewrite machinery used by invalid-file repair and file-removal subcommands.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotFix`, `commonRewriteSnapshots`, invalid-entry constants, `failedEntryCallback`, `rewriteMatchingSnapshots`, `snapshotSizeDelta`, and `listManifestIDs`.

## Control Flow
Child commands configure a `snapshotfs.DirRewriter` with a callback, then `rewriteMatchingSnapshots` resolves target manifests from explicit IDs, sources, or all snapshots; groups them by source; computes metadata compression policy; rewrites each manifest; optionally saves updates when `--commit` is set; and logs old/new root IDs and size deltas.

## State And Persistence Behavior
Without `--commit`, rewritten manifests are not persisted. With commit, snapshot manifests are updated and new rewritten directory objects may be written. Directory read failures can fail, stub, or keep based on flags.

## Dependencies And Integration Points
Integrates snapshot manifest listing/loading/updating, policy metadata compression, `snapshotfs.NewDirRewriter`, repository writers, and unit formatting.

## Risks And Edge Cases
Dry-run still performs rewrite work and may create intermediate objects depending on rewriter behavior. Invalid directory handling supports only fail/stub/keep in shared setup, while invalid file handling adds remove in the child. Rewriting all snapshots can be expensive.

## Test Signals
Tests should cover manifest selection, commit versus dry-run, unchanged snapshots, compression policy propagation, size delta logging, and each invalid-directory handling mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_invalid_files.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix_invalid_files.go

## Purpose
Implements `snapshot fix invalid-files`, which verifies file object readability and rewrites snapshots to handle invalid file references.

## Important APIs, Types, And Functions
Defines `commandSnapshotFixInvalidFiles`, `setup`, `rewriteEntry`, and `run`. It creates a `snapshotfs.Verifier`, optionally preloads a blob map for direct repositories, and chooses a failed-file callback from fail/stub/keep/remove.

## Control Flow
`run` configures verifier options, builds the verifier, and delegates to shared rewrite machinery. For each non-directory entry, `rewriteEntry` calls `Verifier.VerifyFile`; failures are logged and transformed using the configured failed-file callback.

## State And Persistence Behavior
With commit, rewritten manifests persist changes such as stubs or removed entries. The verifier may use repository blob-map state to detect missing content efficiently.

## Dependencies And Integration Points
Integrates `snapshotfs.Verifier`, `blob.ReadBlobMap`, shared `commonRewriteSnapshots`, and repository direct/writer interfaces.

## Risks And Edge Cases
Verification percentage can leave some file contents unchecked. Blob-map availability differs for direct versus indirect repositories. Choosing keep can leave known-bad entries in manifests; remove/stub changes tree semantics.

## Test Signals
Test signals are corrupt content or deleted blob scenarios, each invalid-file handling mode, verify-percent behavior, direct-repo blob map use, and commit/no-commit differences.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_invalid_files.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_remove_files.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix_remove_files.go

## Purpose
Implements `snapshot fix remove-files`, which rewrites snapshot trees to remove entries by object ID or filename pattern.

## Important APIs, Types, And Functions
Defines `commandSnapshotFixRemoveFiles`, `setup`, `rewriteEntry`, and `run`. Matching uses `slices.Contains` for object ID strings and `path.Match` for filename wildcard patterns.

## Control Flow
`run` requires at least one object ID or filename flag, then delegates to common snapshot rewrite. `rewriteEntry` returns nil for matched entries, causing the rewriter to omit them; unmatched entries are returned unchanged.

## State And Persistence Behavior
Committed runs persist updated snapshot manifests and rewritten directory trees. Dry-run rewrite work is reported but manifests are not updated.

## Dependencies And Integration Points
Integrates shared `commonRewriteSnapshots`, snapshot directory entry rewriting, repository writers, and Go path wildcard matching.

## Risks And Edge Cases
Filename matching is against `ent.Name`, not full path, so directory context is not matched by `--filename`. Invalid wildcard syntax aborts processing. Removing by object ID can affect multiple paths and snapshots.

## Test Signals
Tests should cover object-ID match, wildcard match, invalid wildcard, no criteria error, and commit versus no-commit behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_remove_files.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix_test.go

## Purpose
Exercises snapshot-fix workflows by creating snapshots, deliberately damaging repository content or selecting files, running repair commands, and inspecting resulting manifests and file maps.

## Important APIs, Types, And Functions
Important helpers include `TestSnapshotFix`, `forgetContents`, `mustGetContentMap`, `mustGetFileMap`, `mustListDirEntries`, and `mustWriteFileWithRepeatedData`. The tests use `testenv.CLITest`, content maps, snapshotfs roots, and directory entry collection.

## Control Flow
The test builds source trees with repeated data, creates snapshots, records object/content identifiers, removes or forgets content blobs to simulate invalid files, runs fix commands in dry-run and commit forms, and checks remaining files/manifests.

## State And Persistence Behavior
Persistent state under test includes repository content indexes/blobs, snapshot manifests, rewritten directory objects, and CLI-visible file presence after repair.

## Dependencies And Integration Points
Integrates CLI commands, snapshot upload, low-level content maps, blob deletion/forgetting, snapshotfs traversal, and test repository helpers.

## Risks And Edge Cases
Because it manipulates repository internals, it is sensitive to content packing/layout changes. Tests must distinguish missing file content from directory metadata damage and ensure cleanup helpers do not hide repair failures.

## Test Signals
Strong regression signal for invalid-file and remove-file behavior, especially commit semantics and resulting snapshot trees. It complements unit-level rewriter tests by going through the CLI.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list.go -->
# sources/sync-backup/kopia/cli/command_snapshot_list.go

## Purpose
Implements `snapshot list`/`ls`, including source/path matching, tag filtering, JSON output, human-readable rows, identical snapshot compaction, retention/pin display, delta display, and optional storage-stat calculation.

## Important APIs, Types, And Functions
Key symbols include `commandSnapshotList`, `findSnapshotsForSource`, `findRelativePathParts`, `findManifestIDs`, `SnapshotManifest`, `outputJSON`, `outputManifestGroups`, `outputManifestFromSingleSource`, `mergeIdenticalRows`, `outputSnapshotRows`, `entryBits`, and `deltaBytes`.

## Control Flow
The command parses tag filters, finds matching manifest IDs for all sources or a requested source/path and its parents, loads manifests, then either emits JSON groups or text groups. Text mode filters to current user/host unless `--all`, computes retention reasons, resolves nested entries from snapshot roots, optionally computes storage stats, builds rows, compacts identical object IDs, and prints formatted bits.

## State And Persistence Behavior
It is read-only unless storage-stat calculation mutates in-memory `StorageStats` fields on manifests. It observes snapshot manifests, policy retention reasons, snapshot root objects, directory summaries, pins, and object IDs.

## Dependencies And Integration Points
Integrates snapshot manifest APIs, policy retention logic, snapshotfs root/nested-entry helpers, storage-stat calculation, object IDs, color output, and shared JSON/timestamp/unit helpers.

## Risks And Edge Cases
Risks include parent-path search returning more manifests than users expect, `--max-results` slicing after sort direction, identical compaction hiding metadata differences, and delta comparing entry size to previous manifest total file size. Loading nested paths can emit per-row errors rather than failing the command.

## Test Signals
Tests should cover JSON, tags, source filtering, `--all`, nested paths, incomplete snapshots, retention/pins, identical compaction, reverse/max-results, and storage-stat output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_list_test.go

## Purpose
Tests CLI snapshot listing output for basic long listing behavior and cases where the same file appears in multiple snapshots.

## Important APIs, Types, And Functions
Defines `TestSnapshotList` and `TestSnapshotListWithSameFileInMultipleSnapshots`, using in-process CLI repositories, temp directories, file mutations, and output line assertions.

## Control Flow
The tests create repository state, make snapshots, run `snapshot list`/`ls` with flags such as `-l`, and verify that output includes expected source paths, snapshot rows, and repeated-file behavior.

## State And Persistence Behavior
Persistent test state is a temporary filesystem repository with created snapshot manifests and local files used to generate those manifests.

## Dependencies And Integration Points
Integrates snapshot create and list commands, test environment helpers, local filesystem state, and text output formatting.

## Risks And Edge Cases
Like most CLI output tests, it is sensitive to line counts, timestamps, and wording. It exercises behavior through the full CLI rather than isolated list helpers.

## Test Signals
Useful as a regression signal for command aliases, row grouping, and identical/repeated output. It does not deeply cover JSON, tags, retention, or storage stats.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_migrate.go -->
# sources/sync-backup/kopia/cli/command_snapshot_migrate.go

## Purpose
Implements `snapshot migrate`, which copies snapshots and optionally policies from a source repository configuration into the currently connected destination repository.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotMigrate`, `openSourceRepo`, `migratePoliciesForSources`, `migrateAllPolicies`, `migrateSinglePolicy`, `findPreviousSnapshotManifestWithStartTime`, `migrateSingleSource`, `migrateSingleSourceSnapshot`, `filterSnapshotsToMigrate`, and `getSourcesToMigrate`.

## Control Flow
`run` opens the source repo with persisted or prompted password, selects sources, starts shared progress, registers termination cancellation over active uploaders, migrates policies if requested, and migrates sources in goroutines bounded by a semaphore. Each snapshot migration skips incomplete or already migrated snapshots, uploads source snapshotfs roots into the destination, preserves start/end/description, and saves complete manifests.

## State And Persistence Behavior
Persistent writes affect destination repository objects, snapshot manifests, and optionally policy records. Source repository is read-only and closed at the end.

## Dependencies And Integration Points
Integrates source/destination repository APIs, password persistence, policy APIs, snapshotfs roots, upload.Uploader, progress services, and cancellation handling.

## Risks And Edge Cases
Errors inside worker goroutines are logged but not returned from `run`, so a migration can finish with logged failures but nil error. Concurrency shares `destRepo` across uploaders. Existing detection uses source/start time and may skip divergent roots with same timestamp.

## Test Signals
Tests should cover all/specific source selection, latest-only, policy overwrite behavior, duplicate skip, incomplete skip, worker error propagation expectations, cancellation, and ignore-rule toggling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_migrate.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin.go -->
# sources/sync-backup/kopia/cli/command_snapshot_pin.go

## Purpose
Implements `snapshot pin`, updating pin labels on snapshots to prevent or allow retention deletion.

## Important APIs, Types, And Functions
Defines `commandSnapshotPin`, `run`, `pinSnapshotsByRootObjectID`, and `pinSnapshot`. It uses manifest ID lookup first, root object ID fallback, `Manifest.UpdatePins`, and `snapshot.UpdateSnapshot`.

## Control Flow
The command requires at least one `--add` or `--remove` flag, then processes each ID. Each matched manifest is updated only if pins actually change; otherwise it logs a no-op.

## State And Persistence Behavior
Persistent state is the snapshot manifest's `Pins` field. Updating a snapshot writes a new/updated manifest record through snapshot APIs.

## Dependencies And Integration Points
Integrates repository writer actions, snapshot manifest loading, root-object reverse lookup, object ID parsing, and policy pin compaction logic inside `UpdatePins`.

## Risks And Edge Cases
A root object ID can update many manifests. Add/remove conflicts are resolved by `UpdatePins`, so caller expectations depend on that method. There is no dry-run flag.

## Test Signals
Tests should verify add, remove, no-op, multiple IDs, root-object matching, and retention interaction for pinned snapshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_pin_test.go

## Purpose
Tests snapshot pinning behavior through the CLI and manifest inspection helpers.

## Important APIs, Types, And Functions
Defines `TestSnapshotPin` and `mustListSnapshots`. The test creates a repository, snapshots data, runs `snapshot pin` with add/remove operations, lists manifests, and checks pin sets.

## Control Flow
The control flow is end-to-end: create snapshots, read manifests, update pins by manifest or root ID, then reload snapshots to assert the persisted `Pins` field reflects requested changes and no-op cases behave correctly.

## State And Persistence Behavior
Persistent state under test is snapshot manifests in the temporary repository. The local filesystem is used only to create initial snapshot content.

## Dependencies And Integration Points
Integrates CLI commands, snapshot creation, snapshot listing APIs, and manifest pin update logic.

## Risks And Edge Cases
Assertions depend on manifest ordering and helper filtering. The test should keep covering both root ID and manifest ID addressing because they use different code paths.

## Test Signals
Strong signal for `command_snapshot_pin.go`; it complements retention tests by focusing on pin metadata persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_restore.go -->
# sources/sync-backup/kopia/cli/command_snapshot_restore.go

## Purpose
Provides the snapshot-specific restore command type by embedding the generic `commandRestore` implementation.

## Important APIs, Types, And Functions
The only type is `commandSnapshotRestore struct { commandRestore }`; behavior and flags are inherited from the shared restore command.

## Control Flow
Control flow is delegated entirely to embedded `commandRestore` setup/run methods when `command_snapshot.go` registers `restore.setup`.

## State And Persistence Behavior
Persistent behavior is inherited: restore writes files to the target filesystem and reads repository snapshot objects, but this wrapper adds no state.

## Dependencies And Integration Points
Integrates the snapshot command namespace with the shared restore implementation elsewhere in the CLI package.

## Risks And Edge Cases
Risk is mostly structural: changes to `commandRestore` must remain compatible with this embedded wrapper and the snapshot command registration.

## Test Signals
Tests for restore should exercise `snapshot restore` command invocation, while this file itself needs only compile/registration coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_restore.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_storage_stats_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_storage_stats_test.go

## Purpose
Tests `snapshot ls --storage-stats` in JSON and text modes, including forward and reverse snapshot ordering.

## Important APIs, Types, And Functions
The test creates two snapshots with overlapping and new file data, parses JSON lines into `cli.SnapshotManifest`, and compares expected `snapshot.StorageStats` values. It also checks text rows for new-data/new-files/new-dirs fields.

## Control Flow
Control flow creates a repo, snapshots a directory, adds duplicate and new content, snapshots again, runs list with storage stats in normal and reverse order, and validates both per-snapshot new data and running totals.

## State And Persistence Behavior
State under test is repository content deduplication, directory object creation, snapshot manifests, and transient storage stats attached during listing.

## Dependencies And Integration Points
Integrates snapshot create, snapshot list, JSON output, storage-stat calculation, units formatting, and test JSON parsing helpers.

## Risks And Edge Cases
Expected packed byte counts are tightly coupled to repository format/packing behavior. Changes in metadata encoding can require updated expected values even when high-level behavior is intact.

## Test Signals
This is a strong regression signal for `snapshotfs.CalculateStorageStats` integration and list output, especially reverse-order semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_storage_stats_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify.go -->
# sources/sync-backup/kopia/cli/command_snapshot_verify.go

## Purpose
Implements `snapshot verify`, which walks snapshot trees, directory object IDs, file object IDs, or selected sources and verifies referenced repository content.

## Important APIs, Types, And Functions
Important functions are `setup`, `run`, `makeVerifyWalkerFunc`, `addExpectedWorkFromDirSummaryToVerifier`, `loadSourceManifests`, `noVerifyTargetArgsProvided`, and `loadSnapIDManifests`. It configures `snapshotfs.VerifierOptions` and uses `Verifier.InParallel`.

## Control Flow
`run` optionally disables index refresh for direct writers, builds verifier options including queue length, parallelism, max errors, JSON stats, and blob map, then runs parallel tree walking. The walker loads target manifests, creates snapshotfs roots, seeds expected totals from directory summaries, processes roots and explicit directory/file object IDs, and returns aggregate verifier errors.

## State And Persistence Behavior
The command is read-only, but it mutates in-memory verifier counters and may disable direct repository index refresh for performance. It observes blob maps, manifests, object graphs, and file content depending on verify percentage.

## Dependencies And Integration Points
Integrates snapshot manifest APIs, snapshotfs verifier/tree walker, direct repository blob map support, JSON output, runtime CPU defaults, and shared timestamp formatting.

## Risks And Edge Cases
Deprecated `--all-sources` has no effect. If no target args are provided, all manifests are verified, which can be expensive. `tw.Process` errors are intentionally ignored locally and aggregated by the verifier. Loading explicit snapshot IDs requires all requested IDs to exist.

## Test Signals
Tests should cover all target modes, JSON result output, max error threshold, verify file percent, missing manifests, blob-map acceleration, and explicit object ID parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_verify_test.go

## Purpose
Tests snapshot verification behavior against intact and deliberately damaged repository content, including JSON verifier results.

## Important APIs, Types, And Functions
Defines `TestSnapshotVerify` and `unmarshalSnapVerify`. The test creates snapshots, removes or damages content through repository/test helpers, runs `snapshot verify` with different targets and `--json`, then validates `snapshotfs.VerifierResult` fields.

## Control Flow
Control flow exercises successful verification, missing data detection, verification by manifest ID, by source, by directory/file object ID, and JSON output parsing.

## State And Persistence Behavior
Persistent test state is a temporary repository with snapshots and manipulated content/blobs to simulate integrity failures.

## Dependencies And Integration Points
Integrates CLI verify command, snapshot creation, low-level repository mutation helpers, JSON output, and snapshotfs verifier result structures.

## Risks And Edge Cases
The test depends on predictable object/content IDs and verifier counters. Repository format changes can alter counts while the integrity signal remains useful.

## Test Signals
Strong signal for verifier target selection and JSON result shape. It should be kept aligned with any changes to verifier aggregation semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user.go -->
# sources/sync-backup/kopia/cli/command_user.go

## Purpose
Registers the `kopia server users`/`user` command namespace for repository user management.

## Important APIs, Types, And Functions
Defines `commandServerUser` with child commands `add`, `set`, `delete`, `hash`, `info`, and `list`. `setup` creates the parent command and delegates to each child.

## Control Flow
There is no command execution logic in this file. Runtime behavior is handled by the child command implementations after parsing.

## State And Persistence Behavior
No persistent state is changed here; child commands create, update, delete, or list user profile manifests.

## Dependencies And Integration Points
Integrates user-management files under the server command tree and relies on `appServices` repository action plumbing.

## Risks And Edge Cases
Registration drift or alias conflicts are the main risks. The parent description typo (`Manager`) is cosmetic.

## Test Signals
Tests should verify the namespace and aliases expose all child commands and that user operations work through this parent path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_add_set.go -->
# sources/sync-backup/kopia/cli/command_user_add_set.go

## Purpose
Implements `server users add/create` and `server users set/update`, including password entry, password hash assignment, and repository user profile persistence.

## Important APIs, Types, And Functions
Key symbols are `commandServerUserAddSet`, `setup`, `getExistingOrNewUserProfile`, `runServerUserAddSet`, `errPasswordsDoNotMatch`, and `askConfirmPass`.

## Control Flow
Setup selects add or set mode, registers password flags and username arg, and uses a repository writer action. Execution loads a new or existing profile, applies plain password, hash, or prompted password, rejects no-op updates, saves the user profile, and logs that running servers need refresh or restart.

## State And Persistence Behavior
Persistent state is the repository user profile, including password hash. Plain passwords are transient and converted through `user.Profile.SetPassword`.

## Dependencies And Integration Points
Integrates `internal/user`, repository writer actions, terminal password prompting from `password.go`, and server auth reload expectations.

## Risks And Edge Cases
Providing both `--user-password` and `--user-password-hash` applies both in order, with the hash winning if set after password. Interactive prompting depends on stdin being a terminal. Bad hashes are rejected by `SetPasswordHash`.

## Test Signals
Tests should cover add versus set, no-op update, ask-password mismatch, plain password hashing, hash validation, and server refresh behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_add_set.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_delete.go -->
# sources/sync-backup/kopia/cli/command_user_delete.go

## Purpose
Implements `server users delete/remove/rm`, deleting a repository user profile.

## Important APIs, Types, And Functions
Defines `commandServerUserDelete`, `setup`, and `run`. `run` calls `user.DeleteUserProfile` and logs successful deletion.

## Control Flow
The command parses a required username and performs one repository writer operation.

## State And Persistence Behavior
Persistent mutation is removal of the user profile from repository metadata. Running servers may continue using cached credentials until refresh/restart, as noted by add/set but not repeated here.

## Dependencies And Integration Points
Depends on `internal/user` and repository writer action plumbing.

## Risks And Edge Cases
There is no confirmation prompt, so accidental deletion is possible. Error wrapping does not distinguish nonexistent user from other delete failures unless the underlying package does.

## Test Signals
Tests should cover successful delete, aliases, nonexistent users, and authentication failure after server refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_delete.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password.go -->
# sources/sync-backup/kopia/cli/command_user_hash_password.go

## Purpose
Implements `server users hash-password`/`hash`, producing a repository user password hash that can be passed to add/set.

## Important APIs, Types, And Functions
Defines `commandServerUserHashPassword`, `setup`, and `runServerUserHashPassword`. It calls `askConfirmPass` when no password flag is provided and `user.HashPassword` to generate the encoded hash.

## Control Flow
The command intentionally requires a connected repository through repository writer action even though the current hashing implementation does not use it, preserving future compatibility.

## State And Persistence Behavior
No repository data is changed. The output password hash is printed to stdout; input password is held in memory in the command struct.

## Dependencies And Integration Points
Depends on `internal/user` hashing and shared password prompting/output helpers.

## Risks And Edge Cases
Hash output is sensitive and can be captured in shell history or logs if mishandled. Interactive mode depends on terminal password input. Future hash implementations may need repository parameters.

## Test Signals
Tests cover hash generation, using the hash to create/update a user, server refresh, and connecting with the resulting password.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password_test.go -->
# sources/sync-backup/kopia/cli/command_user_hash_password_test.go

## Purpose
End-to-end test for hashed repository-user passwords, including server authentication with a hash-created user and password rotation.

## Important APIs, Types, And Functions
`TestServerUserHashPassword` creates a repo, hashes a password, rejects a bad hash, adds a user by hash, starts a TLS server, connects as that user, hashes a second password, updates the user, refreshes the server, and reconnects with the new password.

## Control Flow
The flow uses in-process runners, `testutil.ServerParameters`, server stderr parsing, server-control refresh, and a separate client environment without inherited repository password.

## State And Persistence Behavior
Persistent state includes repository user profiles and password hashes. The running server caches user credentials until refreshed.

## Dependencies And Integration Points
Integrates user hash/add/set commands, server start TLS/random control password, repo connect server, and server refresh.

## Risks And Edge Cases
The test is timing-sensitive around server startup and credential refresh. It depends on stderr parsing for server address, fingerprint, and control password.

## Test Signals
Strong signal for user-hash compatibility and live server authentication. It does not test interactive password prompting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_info.go -->
# sources/sync-backup/kopia/cli/command_user_info.go

## Purpose
Implements `server users info`, printing a repository user profile as indented JSON.

## Important APIs, Types, And Functions
Defines `commandServerUserInfo`, `setup`, and `run`. `run` uses `user.GetUserProfile`, `json.MarshalIndent`, and stdout.

## Control Flow
After parsing the required username, the command loads the profile and serializes it directly.

## State And Persistence Behavior
It is read-only but can expose user profile metadata, including password-hash representation, to stdout.

## Dependencies And Integration Points
Depends on `internal/user`, repository reader action plumbing, and Go JSON encoding.

## Risks And Edge Cases
Output shape is the raw user profile struct, so changes in `user.Profile` fields affect CLI compatibility. Sensitive data exposure is intentional but should be access-controlled by repository access.

## Test Signals
Tests should cover existing and missing users, JSON validity, and whether sensitive fields are present as expected.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_info.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_list.go -->
# sources/sync-backup/kopia/cli/command_user_list.go

## Purpose
Implements `server users list`/`ls`, listing repository user profiles as plain usernames or JSON array entries.

## Important APIs, Types, And Functions
Defines `commandServerUserList`, `setup`, and `runUserList`. It uses `user.ListUserProfiles` and shared `jsonList`.

## Control Flow
The command begins a JSON list wrapper, loads profiles, emits each full profile when `--json` is set or only the username otherwise, and closes the JSON list.

## State And Persistence Behavior
It is read-only and observes repository user profile manifests. JSON mode exposes full profile structs.

## Dependencies And Integration Points
Depends on `internal/user`, `json_output.go`, and repository reader action plumbing.

## Risks And Edge Cases
Plain output order follows `ListUserProfiles`; deterministic sorting depends on that package. JSON mode can leak password hash metadata to authorized users.

## Test Signals
Tests should cover empty and nonempty repositories, plain versus JSON output, alias behavior, and ordering if promised by user APIs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_list.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/config.go -->
# sources/sync-backup/kopia/cli/config.go

## Purpose
Contains shared application helpers for repository opening, config path resolution, fatal/termination callbacks, local filesystem entry construction, and OS detection.

## Important APIs, Types, And Functions
Key functions are `onRepositoryFatalError`, `onTerminate`, `openRepository`, `optionsFromFlags`, `repositoryConfigFileName`, `resolveSymlink`, `getLocalFSEntry`, and `isWindows`.

## Control Flow
`openRepository` checks config existence, optionally reports update notices, obtains a password from flags/persistence/prompt, opens the repository with constructed options, and maps missing config to user-friendly errors. `onTerminate` registers signal or simulated Ctrl-C callbacks.

## State And Persistence Behavior
Persistent state includes the repository config file path and password persistence lookups; this file does not write repository data. `optionsFromFlags` installs fatal-error callbacks that can terminate the process.

## Dependencies And Integration Points
Integrates `repo.Open`, localfs, ospath config directories, password helpers, update checks, signal handling, and test-only simulated Ctrl-C.

## Risks And Edge Cases
`onTerminate` creates a new signal subscription per callback and does not stop notification. Symlink resolution affects snapshot source identity. Fatal error callbacks call `exitWithError`, so tests must override it carefully.

## Test Signals
Tests should cover config path resolution, required versus optional repository open, symlink resolution, password source precedence, and simulated termination callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/config.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/error_notifications.go -->
# sources/sync-backup/kopia/cli/error_notifications.go

## Purpose
Decides whether repository fatal/error notifications should be sent based on CLI configuration and interactivity.

## Important APIs, Types, And Functions
Defines constants `never`, `always`, and `non-interactive`, plus `App.enableErrorNotifications`.

## Control Flow
The function switches on `c.errorNotifications`: never disables, always enables, non-interactive disables for in-process tests and terminals, otherwise enables.

## State And Persistence Behavior
No persistent state is changed. It reads process stdout terminal status and app flags.

## Dependencies And Integration Points
Depends on `intFd` from `password.go`, `os.Stdout`, and `golang.org/x/term`.

## Risks And Edge Cases
Terminal detection errors fall back to enabling notifications for non-interactive mode. In-process tests are always disabled to avoid unwanted sends.

## Test Signals
Tests should mock or isolate terminal status and verify all three modes plus invalid/default behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/error_notifications.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/inproc.go -->
# sources/sync-backup/kopia/cli/inproc.go

## Purpose
Provides in-process CLI execution for tests and embedded callers, returning stdout/stderr readers plus wait and interrupt functions.

## Important APIs, Types, And Functions
Defines `App.RunSubcommand`. It creates pipes, redirects app IO/logging, sets simulated Ctrl-C state, attaches commands, parses args in a goroutine, captures exit errors, closes resources, and returns an interrupt closure.

## Control Flow
The caller receives pipe readers immediately. The goroutine parses and runs the selected command, then sends parse or exit errors on a result channel. Interrupt sends `true` on `simulatedCtrlC`.

## State And Persistence Behavior
State is per-App mutable test state: stdin/stdout/stderr writers, root context logger, simulatedCtrlC channel, `isInProcessTest`, and `exitWithError` override.

## Dependencies And Integration Points
Integrates Kingpin parsing, internal releasable tracking, repository logging to stderr, and termination callback logic in `config.go`.

## Risks And Edge Cases
This mutates the App instance, so concurrent in-process runs on the same App would interfere. If command code blocks writing to pipes and caller does not drain, deadlock is possible.

## Test Signals
Used broadly by CLI tests. Specific tests should verify stdout/stderr capture, parse error propagation, exit error propagation, and simulated interrupt behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/inproc.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/json_output.go -->
# sources/sync-backup/kopia/cli/json_output.go

## Purpose
Defines shared JSON output flags and helpers, including streaming JSON arrays and manifest cleanup for less verbose output.

## Important APIs, Types, And Functions
Key types/functions are `jsonOutput`, `setup`, `cleanupSnapshotManifestForJSON`, `cleanupSnapshotManifestListForJSON`, `cleanupForJSON`, `jsonBytes`, `jsonIndentedBytes`, and `jsonList` methods `begin`, `end`, and `emit`.

## Control Flow
Commands call `setup` to add JSON flags. Before marshaling, manifest values are wrapped so `Stats` is omitted unless `--json-verbose` is set. `jsonList` emits an array wrapper only in JSON mode and manages separators for compact or indented output.

## State And Persistence Behavior
No repository state is changed. It stores output preferences and writer references for command lifetime.

## Dependencies And Integration Points
Integrates Kingpin flags, Go JSON encoding, snapshot manifest structs, and the internal `impossible.PanicOnError` helper.

## Risks And Edge Cases
`jsonIndentedBytes` panics on marshal errors, assuming command values are JSON-safe. Non-JSON mode `jsonList` emits nothing, so callers must handle plain output separately.

## Test Signals
Tests should cover manifest stats omission/inclusion, array formatting for zero/one/many items, indented output, and command-specific JSON consumers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/json_output.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags.go -->
# sources/sync-backup/kopia/cli/observability_flags.go

## Purpose
Implements process-wide diagnostics flags for metrics serving, Prometheus push gateway, OTLP tracing, allocator stats, metrics-on-exit, and profiling coordination.

## Important APIs, Types, And Functions
Important symbols are `observabilityFlags`, `metricsPushFormats`, `setup`, `initialize`, `run`, `start`, `mkSubdirectories`, `maybeStartListener`, `maybeStartMetricsPusher`, `maybeStartTraceExporter`, `stop`, `pushPeriodically`, and `pushOnce`.

## Control Flow
PreAction computes a per-command diagnostics subdirectory. `run` starts observability, starts profiling, optionally creates a root trace span, runs the command, then stops profilers/exporters/pushers and writes metrics if requested. Metrics listener and pusher run in goroutines; pusher sends initial, periodic, and final pushes.

## State And Persistence Behavior
Persistent state can include diagnostics directories, `kopia-metrics.prom`, pprof files via `profile.go`, and remote metrics/traces. Runtime state includes pusher channels/waitgroup and OTLP tracer provider.

## Dependencies And Integration Points
Integrates Kingpin, Prometheus gatherer/listener/push, Gorilla mux, pprof handlers, OpenTelemetry OTLP gRPC, repo build metadata, clock, gather stats, and `profileFlags`.

## Risks And Edge Cases
`http.ListenAndServe` errors are ignored, so listener bind failures can be silent. Push failures are debug logs only. Grouping parsing requires `name:value`. Trace exporter startup can fail commands. Output directory creation is validated only for requested save/profile modes.

## Test Signals
Tests cover push URL/grouping/auth/body, invalid grouping, OTLP flag tolerance, and metrics file creation. Additional tests should cover pprof listener conflicts and trace startup failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags_test.go -->
# sources/sync-backup/kopia/cli/observability_flags_test.go

## Purpose
Tests observability CLI flags for Prometheus push gateway behavior, OTLP flag handling, and metrics save-on-exit output.

## Important APIs, Types, And Functions
Defines `TestMetricsPushFlags`, `TestOTLPFlags`, and `TestMetricsSaveToOutputDirFlags`. It uses `httptest.Server`, in-process CLI runs, temporary directories, and captured HTTP request bodies/auth.

## Control Flow
The push test creates a repo and runs status with push flags, expecting initial and final pushes, grouping path segments, basic auth, and metrics body content. It also asserts invalid grouping syntax fails. OTLP test checks a deprecated flag failure and that `--otlp-trace` does not require a running collector for the crypto benchmark. Metrics save test verifies one diagnostics subdirectory is created.

## State And Persistence Behavior
Persistent test state includes temporary repositories and diagnostics directories. Network state is local httptest only.

## Dependencies And Integration Points
Integrates CLI command execution, Prometheus pusher, metrics gatherer, auth/grouping flags, and diagnostics output.

## Risks And Edge Cases
Assertions depend on push ordering and metric names such as `kopia_cache_hit_bytes_total`. Concurrent metrics can make bodies large but should include stable names.

## Test Signals
Good regression signal for observability flag plumbing and start/stop behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/observability_flags_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password.go -->
# sources/sync-backup/kopia/cli/password.go

## Purpose
Provides shared repository password prompting and selection logic, including create/change/existing prompts, flag/persistent precedence, and file descriptor conversion.

## Important APIs, Types, And Functions
Key functions are `askForNewRepositoryPassword`, `askForChangedRepositoryPassword`, `askForExistingRepositoryPassword`, `setPasswordFromToken`, `getPasswordFromFlags`, `askPass`, and `intFd`.

## Control Flow
`getPasswordFromFlags` prefers `--password`/environment value, prompts twice for create, tries persistent password storage when allowed, and falls back to one existing-password prompt. `askPass` uses terminal password input up to five non-empty attempts.

## State And Persistence Behavior
No repository data is changed here, but selected passwords unlock or create repository state. Passwords are held in memory as strings. Persistent lookup is delegated to password persistence strategy.

## Dependencies And Integration Points
Integrates terminal FD handling, `golang.org/x/term`, password persistence errors, and App IO streams.

## Risks And Edge Cases
Interactive prompting requires `os.Stdin` to be a valid terminal-like file descriptor, which can fail in noninteractive contexts. Empty passwords are silently retried up to five times. `askForChangedRepositoryPassword` prints mismatch to global stdout instead of the provided writer.

## Test Signals
Tests should cover flag precedence, persistent fallback, prompt retry/mismatch, nonterminal errors, and FD overflow handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_darwin.go -->
# sources/sync-backup/kopia/cli/password_darwin.go

## Purpose
Registers macOS-specific password persistence flag support.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags` for Darwin, adding `--use-keychain` with default true and binding it to `c.keyRingEnabled`.

## Control Flow
The function is called during app setup to expose the platform flag. Actual keychain operations are handled by password persistence code elsewhere.

## State And Persistence Behavior
It mutates only CLI flag binding state; persistent password storage is affected later when the app uses `keyRingEnabled`.

## Dependencies And Integration Points
Depends on Kingpin and app setup calling the platform-specific method selected by build tags.

## Risks And Edge Cases
Default-on behavior means macOS users may store repository passwords unless they opt out. Tests running on Darwin need account for the flag name and default.

## Test Signals
Build-tag coverage and CLI flag tests on Darwin are the relevant signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_darwin.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_linux.go -->
# sources/sync-backup/kopia/cli/password_linux.go

## Purpose
Registers Linux-specific password persistence flag support.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags`, adding `--use-keyring`, default false, environment override `KOPIA_USE_KEYRING`, and binding to `c.keyRingEnabled`.

## Control Flow
The app setup exposes the flag; later password persistence chooses whether to use GNOME Keyring based on the boolean.

## State And Persistence Behavior
It changes only flag-bound app state. Any persistent secret writes occur outside this file.

## Dependencies And Integration Points
Depends on Kingpin and service `EnvName` namespacing.

## Risks And Edge Cases
Default-off differs from macOS/Windows defaults, so cross-platform behavior must be documented and tested separately.

## Test Signals
Linux CLI flag tests should verify default, environment override, and interaction with repository connect/create password persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_linux.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_other.go -->
# sources/sync-backup/kopia/cli/password_other.go

## Purpose
Provides the no-op password persistence flag hook for platforms other than Windows, Linux, and Darwin.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags` under build tag `!windows && !linux && !darwin`; it accepts services and app but registers no flags.

## Control Flow
Control flow is intentionally empty, so unsupported platforms do not expose platform keychain flags.

## State And Persistence Behavior
No state or persistence behavior is changed.

## Dependencies And Integration Points
Depends only on build-tag selection and Kingpin types for signature compatibility.

## Risks And Edge Cases
Users on unsupported platforms cannot enable OS keychain storage through these flags. Future platform additions need new build-tag files.

## Test Signals
Build coverage on an `other` GOOS or static analysis of build constraints is the main test signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_other.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_windows.go -->
# sources/sync-backup/kopia/cli/password_windows.go

## Purpose
Registers Windows-specific password persistence flag support.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags`, adding `--use-credential-manager`, default true, bound to `c.keyRingEnabled`.

## Control Flow
The function participates in normal app setup; actual credential manager reads/writes are implemented elsewhere.

## State And Persistence Behavior
It mutates only CLI flag state. Persistent secret behavior follows later from `keyRingEnabled`.

## Dependencies And Integration Points
Depends on Kingpin and Windows build-tag selection.

## Risks And Edge Cases
Default-on behavior can surprise tests or automation that expects no persistent credentials. Flag naming differs from other OSes.

## Test Signals
Windows build/CLI tests should verify the flag exists, defaults true, and disables credential manager when false.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_windows.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/profile.go -->
# sources/sync-backup/kopia/cli/profile.go

## Purpose
Implements runtime profiling flags for CPU, heap, goroutine, threadcreate, block, and mutex profile collection into diagnostics directories.

## Important APIs, Types, And Functions
Key symbols are `profileFlags`, `setup`, `start`, and `stop`. It uses Go `runtime` and `runtime/pprof` APIs and the shared `mkSubdirectories` helper.

## Control Flow
`start` applies requested profiling rates, enables sensible block/mutex defaults when saving profiles, creates the profile output directory, and starts CPU profiling if requested. `stop` closes CPU profiling, optionally forces GC, then writes all available pprof profiles to files.

## State And Persistence Behavior
Persistent output is profile files under `<diagnostics>/<run>/profiles`. Runtime-global profiling rates are changed for the process and not restored by this file.

## Dependencies And Integration Points
Integrates observability flag orchestration, diagnostics directory creation, Go runtime profiling, and CLI logging.

## Risks And Edge Cases
Changing runtime profiling rates is process-global and can affect concurrent in-process tests. CPU profile file creation failures abort command startup; non-CPU profile write failures are logged.

## Test Signals
Tests should cover directory creation, CPU profile start/stop, profile-store-on-exit outputs, GC-before-dump, and rate/fraction flag effects.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/profile.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/restore_progress.go -->
# sources/sync-backup/kopia/cli/restore_progress.go

## Purpose
Provides CLI progress rendering for restore operations, aggregating restore counters and printing throttled stderr status lines with ETA.

## Important APIs, Types, And Functions
Defines `cliRestoreProgress` with atomic counters, throttle, mutex, output writer, and ETA estimator. Methods are `SetCounters`, `Flush`, `maybeOutput`, and `output`.

## Control Flow
Restore code calls `SetCounters` with `restore.Stats`; counters are stored atomically and output is throttled. `output` locks to keep lines monotonic and uses carriage-return rewriting plus padding to erase longer previous lines.

## State And Persistence Behavior
No repository state is changed. State is in-memory progress counters and the last printed line length.

## Dependencies And Integration Points
Integrates `snapshot/restore` stats, `timetrack.Throttle`, ETA estimation, units formatting, and CLI stderr output.

## Risks And Edge Cases
Progress is suppressed until restored size is nonzero, so small metadata-only restores may show little feedback. Atomic counters and mutex protect output, but all callers share the same progress object.

## Test Signals
Tests should validate formatting with skipped/error counts, ETA display, line erasure padding, disabled progress, and flush newline behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/restore_progress.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/show_utils.go -->
# sources/sync-backup/kopia/cli/show_utils.go

## Purpose
Collects formatting and display helpers for content output, human-readable units, timestamps, compression percentage, and multiline indentation.

## Important APIs, Types, And Functions
Key functions are `showContentWithFlags`, `maybeHumanReadableBytes`, `maybeHumanReadableCount`, `formatTimestamp`, `formatTimestampPrecise`, `convertTimezone`, `formatCompressionPercentage`, and `indentMultilineString`. Global `timeZone` controls timestamp conversion.

## Control Flow
`showContentWithFlags` optionally wraps input in a gzip reader, optionally buffers and JSON-indents content, then copies to the output writer. Formatting helpers are used across snapshot/list/report commands.

## State And Persistence Behavior
No repository state is changed. The global `timeZone` is process state and can affect all timestamp formatting.

## Dependencies And Integration Points
Depends on gzip, JSON indentation, internal copy and units helpers, and Go time locations.

## Risks And Edge Cases
JSON indentation buffers the entire stream, which is unsafe for very large objects. Invalid timezone names silently fall back to original timestamp. `timeZone` global is not concurrency-safe for tests changing it.

## Test Signals
Tests should cover gzip, JSON indentation errors, time zone modes, compression percentage edge cases, and human-readable toggles.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/show_utils.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_unix.go -->
# sources/sync-backup/kopia/cli/sighup_unix.go

## Purpose
Implements Unix external configuration reload handling by invoking a callback whenever SIGHUP is received.

## Important APIs, Types, And Functions
Defines `onExternalConfigReloadRequest` under `!windows`, creating a buffered signal channel with `signal.Notify(c, syscall.SIGHUP)` and a goroutine loop that calls the provided function on every signal.

## Control Flow
Once registered, the goroutine waits indefinitely and invokes the callback for each SIGHUP. Server start uses this to refresh server state.

## State And Persistence Behavior
No persistent state is changed. Runtime state is a signal subscription and goroutine for the process lifetime.

## Dependencies And Integration Points
Integrates Go signal handling and server refresh callback registration.

## Risks And Edge Cases
The signal subscription is never stopped, so repeated registrations can accumulate goroutines. Callback execution is synchronous inside the goroutine and can serialize or block future SIGHUP handling.

## Test Signals
Tests on Unix should send SIGHUP or use signal injection carefully; server refresh integration is the key behavioral signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_unix.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_windows.go -->
# sources/sync-backup/kopia/cli/sighup_windows.go

## Purpose
Provides the Windows stub for external configuration reload requests.

## Important APIs, Types, And Functions
Defines `onExternalConfigReloadRequest` as a no-op because SIGHUP is not supported on Windows.

## Control Flow
Control flow intentionally ignores the callback. Server refresh must be triggered by other mechanisms on Windows.

## State And Persistence Behavior
No state or persistence behavior exists.

## Dependencies And Integration Points
Depends on Windows build-tag selection by filename.

## Risks And Edge Cases
Platform behavior differs from Unix; code relying on SIGHUP refresh must not assume it works on Windows.

## Test Signals
Build coverage on Windows and server refresh tests through explicit commands are the relevant signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_windows.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_azure.go -->
# sources/sync-backup/kopia/cli/storage_azure.go

## Purpose
Implements CLI flags and connection creation for Azure Blob Storage repositories.

## Important APIs, Types, And Functions
Defines `storageAzureFlags`, `Setup`, `Connect`, and `init` registration. It fills `azure.Options` with container, account, key/SAS/service-principal/federated-token fields, prefix, throttling limits, storage domain, and optional point-in-time.

## Control Flow
Setup binds flags and parses point-in-time in a pre-action. Connect rejects point-in-time on repository creation and calls `azure.New`.

## State And Persistence Behavior
Persistent state is backend configuration stored by repository connect/create code outside this file. This file constructs transient option structs and may embed credential values from flags/environment.

## Dependencies And Integration Points
Integrates storage provider registry, Kingpin, Azure blob backend, throttling flags, and env-name namespacing.

## Risks And Edge Cases
Credential combinations are mostly validated by the backend. Point-in-time format must be RFC3339 and is read-only only. Sensitive credentials can be present in process args/env.

## Test Signals
Tests should cover required flags, env overrides, point-in-time parsing/rejection on create, throttling propagation, and backend option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_azure.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_b2.go -->
# sources/sync-backup/kopia/cli/storage_b2.go

## Purpose
Registers the deprecated B2 storage provider CLI wrapper.

## Important APIs, Types, And Functions
Defines `storageB2Flags`, `Setup`, `Connect`, and `init`. It maps bucket, key ID, key, prefix, and throttling flags into `b2.Options`.

## Control Flow
Connect simply calls `b2.New` with the collected options and create/read mode.

## State And Persistence Behavior
Persistent repository storage configuration is written by higher-level repository connect/create logic; this file stores only transient parsed flags.

## Dependencies And Integration Points
Integrates B2 blob backend, storage provider registry, Kingpin, environment namespacing, and throttling flags. It is compiled only when extra providers are enabled.

## Risks And Edge Cases
The provider is marked deprecated. Credentials are required and may be provided via env or CLI. Backend handles most validation.

## Test Signals
Tests should verify provider registration under extra-provider builds, required flags/env overrides, and throttling option propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_b2.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_filesystem.go -->
# sources/sync-backup/kopia/cli/storage_filesystem.go

## Purpose
Implements filesystem repository storage flags and option conversion.

## Important APIs, Types, And Functions
Important symbols are `storageFilesystemFlags`, `Setup`, `Connect`, `initialDirectoryShards`, `getIntPtrValue`, `getFileModeValue`, and provider `init`.

## Control Flow
Setup registers path, ownership, file/dir mode, flat layout, list parallelism, and throttling flags. Connect resolves a user-friendly path, requires it to be absolute, parses optional UID/GID and octal modes, selects sharding based on flat/format version, and calls `filesystem.New`.

## State And Persistence Behavior
Persistent behavior is creation/use of repository files on local filesystem with selected modes, ownership, sharding, and throttling. Parsed invalid UID/mode values silently fall back to nil/default.

## Dependencies And Integration Points
Integrates filesystem blob backend, ospath resolution, storage registry, throttling flags, and repository format-version compatibility.

## Risks And Edge Cases
Silent parse fallback can hide bad owner/mode input. Format version 1 forces `{3,3}` sharding for old-client compatibility, while later versions defer to backend defaults unless flat is set.

## Test Signals
Tests should cover absolute path enforcement, user-friendly path resolution, flat/version sharding, mode/owner parsing, and defaults.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_filesystem.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gcs.go -->
# sources/sync-backup/kopia/cli/storage_gcs.go

## Purpose
Implements Google Cloud Storage repository provider flags and connection construction.

## Important APIs, Types, And Functions
Defines `storageGCSFlags`, `Setup`, `Connect`, and registration. Options include bucket, prefix, read-only scope, credentials file, embedded credentials, throttling, and point-in-time.

## Control Flow
Setup binds flags and parses point-in-time pre-action. Connect rejects point-in-time on create, optionally reads the service account credentials JSON into config and clears the file path, then calls `gcs.New`.

## State And Persistence Behavior
Persistent repository config may include embedded service account JSON when requested. Otherwise it references a credentials file path. Storage backend state lives in GCS.

## Dependencies And Integration Points
Integrates GCS blob backend, storage provider registry, JSON raw messages, file reads, and throttling flags.

## Risks And Edge Cases
Embedding credentials copies secret JSON into repository config, which has security implications. Point-in-time is read-only. Missing credentials file errors only occur when embedding or backend validates.

## Test Signals
Tests should cover embedding, read-only flag, point-in-time parsing/rejection, and credential file errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gcs.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gdrive.go -->
# sources/sync-backup/kopia/cli/storage_gdrive.go

## Purpose
Implements Google Drive provider flags for extra-provider builds; the provider is noted as not maintained.

## Important APIs, Types, And Functions
Defines `storageGDriveFlags`, `Setup`, `Connect`, and registration. It maps folder ID, read-only, credentials file, embedded credentials, and throttling into `gdrive.Options`.

## Control Flow
Connect optionally reads service account JSON into `ServiceAccountCredentialJSON`, clears the file path, and calls `gdrive.New`.

## State And Persistence Behavior
Persistent repository config can embed credential JSON. Backend object state lives in Google Drive.

## Dependencies And Integration Points
Integrates gdrive blob backend, storage registry, JSON/file helpers, and throttling flags.

## Risks And Edge Cases
Provider maintenance status is a risk. The flag help says `Embed GCS credentials JSON`, which is confusing for GDrive. Embedded credentials require careful config protection.

## Test Signals
Tests should cover registration, required folder ID, embedded credentials, read-only flag, and backend option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gdrive.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_providers.go -->
# sources/sync-backup/kopia/cli/storage_providers.go

## Purpose
Defines the CLI storage provider registry, provider interfaces, common throttling flags, and app hooks for adding/listing providers.

## Important APIs, Types, And Functions
Key types are `StorageProviderServices`, `StorageFlags`, and `StorageProvider`. Key functions are `mustRegisterStorageProvider`, `registerStorageProvider`, `getRegisteredStorageProviders`, `commonThrottlingFlags`, `App.AddStorageProvider`, and `App.storageProviders`.

## Control Flow
Provider files call `mustRegisterStorageProvider` from init. The registry is guarded by a mutex, rejects duplicate names, and returns providers sorted by name. The App can also append providers at runtime for tests.

## State And Persistence Behavior
Global registry state persists for the process lifetime. App-level provider slices are mutable per app instance.

## Dependencies And Integration Points
Integrates Kingpin provider setup, blob storage interfaces, throttling limits, sync/mapping helpers, and tests that inject providers.

## Risks And Edge Cases
`AddStorageProvider` appends without duplicate checks, unlike global registration. Init-time registration order is normalized by sorting. Global state can leak across tests if tests register names directly.

## Test Signals
Tests should cover duplicate registration, sorted provider order, runtime injection, and common throttling flag binding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_providers.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_rclone.go -->
# sources/sync-backup/kopia/cli/storage_rclone.go

## Purpose
Implements rclone-based provider flags for extra-provider builds; the provider is marked not maintained.

## Important APIs, Types, And Functions
Defines `storageRcloneFlags`, `Setup`, `Connect`, and registration. Flags include remote path, flat layout, executable, args/env, embedded config, debug, transfer close behavior, list parallelism, atomic writes, startup timeout, and throttling.

## Control Flow
Connect sets directory sharding, optionally reads and embeds an rclone config file, then calls `rclone.New`.

## State And Persistence Behavior
Persistent repository config can include embedded rclone config text and backend options. Actual storage is mediated by an external rclone process.

## Dependencies And Integration Points
Integrates rclone blob backend, storage registry, file reading, sharding helper, and throttling.

## Risks And Edge Cases
External process startup, embedded config secrecy, atomic-write assumptions, and not-maintained status are primary risks. Args/env are passed through with limited validation.

## Test Signals
Tests should cover embedded config read failures, flat sharding, option propagation, and startup timeout parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_rclone.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3.go -->
# sources/sync-backup/kopia/cli/storage_s3.go

## Purpose
Implements S3 repository provider flags, including TLS options, custom root CA input, credentials, prefix, endpoint, region, throttling, and point-in-time reads.

## Important APIs, Types, And Functions
Key symbols are `storageS3Flags`, `Setup`, `preActionLoadPEMPath`, `preActionLoadPEMBase64`, `Connect`, and registration.

## Control Flow
Setup binds required bucket/access/secret flags and optional session token, prefix, TLS controls, point-in-time pre-action, and root CA pre-actions. Connect rejects point-in-time for repository creation and calls `s3.New`.

## State And Persistence Behavior
Persistent config can include credentials, TLS verification choices, custom CA bytes, and point-in-time read settings. Backend object state lives in S3-compatible storage.

## Dependencies And Integration Points
Integrates S3 blob backend, storage registry, env-name namespacing, base64 decoding, file reads, throttling, and Kingpin pre-actions.

## Risks And Edge Cases
`--disable-tls-verification` and `--disable-tls` are security-sensitive. `preActionLoadPEMBase64` accepts empty base64 and sets RootCA to empty. Mutual exclusion is enforced only when path pre-action sees RootCA already set.

## Test Signals
Tests cover root CA base64/path loading and mutual exclusion. Additional tests should cover point-in-time create rejection and TLS flag propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3_test.go -->
# sources/sync-backup/kopia/cli/storage_s3_test.go

## Purpose
Unit tests for S3 custom root CA loading from base64 and file path.

## Important APIs, Types, And Functions
Defines fake cert bytes and tests `preActionLoadPEMBase64`, `preActionLoadPEMPath`, and mutual exclusion when both base64 and path are used.

## Control Flow
The tests instantiate `storageS3Flags` directly, set fields, invoke pre-actions, and assert RootCA bytes or expected errors.

## State And Persistence Behavior
No repository or network state is used. Temporary files hold fake certificate content for path loading.

## Dependencies And Integration Points
Integrates the S3 flag helper functions, base64 encoding, temp directories, and testify assertions.

## Risks And Edge Cases
The tests do not validate that bytes are real PEM data; they only check transport into options. Mutual exclusion depends on invocation order.

## Test Signals
Good signal for CLI pre-action behavior. Backend TLS behavior and connect-time S3 options need separate integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp.go -->
# sources/sync-backup/kopia/cli/storage_sftp.go

## Purpose
Implements SFTP storage provider flags and option normalization for extra-provider builds.

## Important APIs, Types, And Functions
Key symbols are `storageSFTPFlags`, `Setup`, `getOptions`, `Connect`, and registration. It supports password, keyfile, key data, known hosts file/data, external SSH, embedded credentials, flat layout, SSH command/args, list parallelism, and throttling.

## Control Flow
`getOptions` optionally embeds key and known_hosts file contents, validates one credential source and one host verification source unless external SSH is used, absolutizes file paths, sets sharding, and returns copied options. `Connect` calls `sftp.New`.

## State And Persistence Behavior
Persistent repository config may embed private key and known_hosts data or reference absolute file paths. Backend state lives on the SFTP server.

## Dependencies And Integration Points
Integrates SFTP blob backend, storage registry, sharding helper, file reads, path absolutization, and throttling flags.

## Risks And Edge Cases
Embedding credentials stores private key material in config. External SSH bypasses local credential/known-host validation. Relative paths are converted at connect time, which can surprise users expecting lazy resolution.

## Test Signals
Tests cover option normalization, required auth/known-host checks, embedding failures/success, and flat sharding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp_test.go -->
# sources/sync-backup/kopia/cli/storage_sftp_test.go

## Purpose
Unit tests for SFTP option normalization and validation.

## Important APIs, Types, And Functions
`TestSFTPOptions` builds cases for keyfile/known_hosts path absolutization, missing files during embedding, missing auth or known-host data, embedding file contents, flat sharding, and password authentication. `mustFileAbs` provides expected absolute paths.

## Control Flow
Each case calls `storageSFTPFlags.getOptions(2)` and compares the resulting `sftp.Options` or expected error substring.

## State And Persistence Behavior
Test state is limited to temporary key and known_hosts files. No network/SFTP server is contacted.

## Dependencies And Integration Points
Integrates the SFTP CLI flag struct, sharded directory options, file embedding, and testify assertions.

## Risks And Edge Cases
Expected structs must track backend option defaults. The test does not cover external SSH mode, SSH args/env, format version 1 sharding, or throttling.

## Test Signals
Strong signal for credential and host-verification validation, which is the main local behavior in `storage_sftp.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_webdav.go -->
# sources/sync-backup/kopia/cli/storage_webdav.go

## Purpose
Implements WebDAV storage provider flags for extra-provider builds.

## Important APIs, Types, And Functions
Defines `storageWebDAVFlags`, `Setup`, `Connect`, and registration. Flags include URL, flat layout, username/password with environment overrides, list parallelism, atomic writes, and throttling.

## Control Flow
Connect copies options, prompts for a WebDAV password when username is provided without password, sets directory sharding, and calls `webdav.New`.

## State And Persistence Behavior
Persistent config stores WebDAV URL, optional credentials, atomic-write assumption, and sharding. Backend data lives on WebDAV storage.

## Dependencies And Integration Points
Integrates WebDAV blob backend, storage registry, password prompting, env-name namespacing, sharding helper, and throttling.

## Risks And Edge Cases
Prompting uses `os.Stdout` directly and terminal stdin from `askPass`, which can fail in noninteractive use. Atomic writes are a provider assumption that can affect repository safety.

## Test Signals
Tests should cover password prompt path, env password path, flat/version sharding, atomic writes, and backend option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_webdav.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/suite_test.go -->
# sources/sync-backup/kopia/cli/suite_test.go

## Purpose
Provides CLI package test-suite bootstrap and format-version parameterization.

## Important APIs, Types, And Functions
Defines `TestMain`, `formatSpecificTestSuite`, and tests `TestFormatV1`, `TestFormatV2`, and `TestFormatV3`, each invoking `testutil.RunAllTestsWithParam` with the corresponding `--format-version` flag and `format.Version`.

## Control Flow
When package tests run, `TestMain` delegates to shared test main setup. The format tests run all parameterized tests under each repository format version.

## State And Persistence Behavior
Persistent state is test-only: temporary repositories created by downstream tests under different format versions.

## Dependencies And Integration Points
Integrates `internal/testutil`, repository format constants, and the package's format-specific test plumbing.

## Risks And Edge Cases
Adding a new repository format requires updating this suite. Parameterized tests must read the provided suite parameter correctly.

## Test Signals
Signals are broad: many CLI tests run against all supported repository formats, catching format-specific command regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/suite_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/terminate_signal_test.go -->
# sources/sync-backup/kopia/cli/terminate_signal_test.go

## Purpose
Tests that an external server process exits cleanly when sent SIGTERM.

## Important APIs, Types, And Functions
`TestTerminate` uses an executable runner, creates a filesystem repository, starts `server start --address=localhost:0 --insecure`, sends SIGTERM through the test runner interrupt hook, and requires `wait()` to return nil.

## Control Flow
The test exercises real process signal handling rather than in-process simulated Ctrl-C.

## State And Persistence Behavior
Persistent test state is a temporary repository. Runtime state includes a started server process and parsed server parameters.

## Dependencies And Integration Points
Integrates server start, repository creation, process runner, OS signals, and graceful shutdown handling in server/config code.

## Risks And Edge Cases
Platform behavior depends on SIGTERM support and process startup timing. It uses insecure server mode to avoid TLS/auth setup.

## Test Signals
Strong signal for termination callbacks and HTTP server shutdown. It does not cover SIGHUP reload or stdin-close shutdown.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/terminate_signal_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_get.go -->
# sources/sync-backup/kopia/cli/throttle_get.go

## Purpose
Provides shared formatting for throttling limits used by server throttle and storage/provider-related commands.

## Important APIs, Types, And Functions
Defines `commonThrottleGet`, `setup`, `output`, `printValueOrUnlimited`, and `floatToString`. It prints `throttling.Limits` as JSON or aligned text.

## Control Flow
Commands call `setup` to register JSON flags and output services, then `output` prints download/upload speeds, request rates, and concurrency limits. Zero values are displayed as `(unlimited)`.

## State And Persistence Behavior
No persistent state is changed. It only formats a provided limits struct.

## Dependencies And Integration Points
Depends on `json_output.go`, text output services, `internal/units`, and `repo/blob/throttling`.

## Risks And Edge Cases
Integer concurrency limits are converted through float64 for common formatting, which is fine for practical values but unnecessary. Text labels are part of CLI compatibility.

## Test Signals
Tests should cover JSON mode, unlimited zeros, finite speeds/rates/concurrency, and formatting stability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_get.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_set.go -->
# sources/sync-backup/kopia/cli/throttle_set.go

## Purpose
Provides shared CLI parsing and application of throttle-setting flags into `throttling.Limits`.

## Important APIs, Types, And Functions
Defines `commonThrottleSet`, `setup`, `apply`, `setThrottleFloat64`, and `setThrottleInt`. It supports download/upload bytes per second, read/write/list request rates, and concurrent reads/writes.

## Control Flow
`apply` calls typed setters for each nonempty flag. A value of `unlimited` or `-` sets the target field to zero; otherwise floats or ints are parsed and assigned. Each assignment increments a caller-provided change count and logs the change.

## State And Persistence Behavior
It mutates only the supplied `throttling.Limits` struct. Persistence depends on the caller, such as `command_server_throttle_set.go`, sending the changed limits to a server.

## Dependencies And Integration Points
Integrates Kingpin flag registration, units formatting for byte speeds, logging, and throttling structs.

## Risks And Edge Cases
No local validation prevents negative speeds/rates/concurrency. The log phrase `to a unlimited` is grammatically odd but harmless. Change count increments even if the new value equals the old value.

## Test Signals
Tests should cover parse failures, unlimited aliases, negative values if allowed/rejected by callers, and change-count behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/throttle_set.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/update_check.go -->
# sources/sync-backup/kopia/cli/update_check.go

## Purpose
Implements optional GitHub update checks, persisted check/notification scheduling, release completeness validation, and update notification logging.

## Important APIs, Types, And Functions
Key symbols are constants for environment and URLs, `updateState`, `updateStateFilename`, `writeUpdateState`, `removeUpdateState`, `getUpdateState`, `maybeInitializeUpdateCheck`, `getLatestReleaseNameFromGitHub`, `verifyGitHubReleaseIsComplete`, `maybeCheckForUpdates`, `maybeCheckGithub`, `maybePrintUpdateNotification`, and `ensureVPrefix`.

## Control Flow
On repository connect/create, initial state may be written or removed. Later repository opens read state, honor `KOPIA_CHECK_FOR_UPDATES=false`, periodically query GitHub latest release, verify checksum signature availability, persist available version, and log a notification when notify interval has elapsed.

## State And Persistence Behavior
Persistent state is `<repo-config>.update-info.json`, written atomically. Network state is GitHub API and release asset availability. No repository data is changed.

## Dependencies And Integration Points
Integrates app config paths, atomic file writes, clock intervals, repo build metadata, semver comparison, HTTP client calls, and environment namespacing.

## Risks And Edge Cases
Network failures are debug-logged and do not block normal use. The code writes next-check time before contacting GitHub to avoid repeated requests. Build versions are normalized with a leading `v`, but unusual version strings may compare unexpectedly.

## Test Signals
Tests should mock HTTP/clock/state files, covering env disable, initial state, due/not-due checks, newer/equal versions, incomplete release checks, and notification throttling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/update_check.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache.go -->
# sources/sync-backup/kopia/fs/cachefs/cache.go

## Purpose
Implements an in-memory LRU-style cache for directory entry lists, keyed by object ID, to speed repeated filesystem traversal.

## Important APIs, Types, And Functions
Key types are `cacheEntry`, `Cache`, `Loader`, `EntryWrapper`, and `Options`. Important methods are `IterateEntries`, `getEntriesFromCacheLocked`, `getEntries`, `removeEntryLocked`, plus list helpers `moveToHead`, `addToHead`, and `remove`.

## Control Flow
`IterateEntries` caches only directories implementing `object.HasObjectID`; others use direct iteration. `getEntries` locks the cache, checks unexpired entries, loads raw entries on miss, wraps entries for storage, skips caching oversized directories, inserts at the head, and evicts tail entries until directory-count and total-entry limits are satisfied.

## State And Persistence Behavior
State is process-local memory: map of cache IDs to entry slices, total entry count, and doubly linked LRU list. Entries expire after 24 hours by default. There is no disk persistence.

## Dependencies And Integration Points
Integrates `fs.GetAllEntries`, object IDs, internal clock/logging, and wrappers from `cachefs.go`.

## Risks And Edge Cases
The function returns `raw` after inserting `wrapped`, so the first miss returns unwrapped entries while later hits return wrapped entries; this appears intentional or at least important to validate. The loader runs while holding the cache lock, limiting concurrency. Nil cache bypasses caching.

## Test Signals
Tests cover LRU ordering, size eviction, oversized non-caching, and lock release on error/hit/miss. Additional tests should cover wrapper behavior and expiration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache_test.go -->
# sources/sync-backup/kopia/fs/cachefs/cache_test.go

## Purpose
Unit tests for cachefs cache insertion, hits, LRU ordering, eviction by directory and entry limits, oversized directories, and lock release behavior.

## Important APIs, Types, And Functions
Defines helper types `cacheSource`, `cacheVerifier`, and `lockState`, plus `TestCache` and `TestCacheGetEntriesLocking`.

## Control Flow
`TestCache` creates fake entry lists of varying sizes, calls `getEntries`, verifies miss/hit counters, and checks LRU order and size invariants after each operation. The locking test swaps in a lock wrapper, forces a loader error, and verifies the cache is unlocked after errors and normal accesses.

## State And Persistence Behavior
State under test is the cache's internal map, total count, head/tail linked list, and lock counter.

## Dependencies And Integration Points
Integrates internal test logging, fake fs entries, maps cloning, and atomic lock-state tracking.

## Risks And Edge Cases
Tests intentionally inspect internals, so refactors of cache representation require test changes. They do not cover expiration timing or object-ID-based `IterateEntries` wrapping.

## Test Signals
Strong signal for eviction and deadlock regressions, especially the historic lock issues referenced by comments.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cache_test.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cachefs.go -->
# sources/sync-backup/kopia/fs/cachefs/cachefs.go

## Purpose
Defines wrapper entry types that add directory-entry caching behavior around existing `fs.Entry` implementations.

## Important APIs, Types, And Functions
Key symbols are `DirectoryCacher`, `cacheContext`, wrapper structs `directory`, `file`, `symlink`, `Wrap`, and `wrapWithContext`. Compile-time assertions ensure wrappers implement fs interfaces.

## Control Flow
`Wrap` creates a shared cache context. Directories override `Child` and `IterateEntries` to wrap returned children with the same context and delegate iteration to the cacher. Files and symlinks embed underlying interfaces without behavior changes but carry the context for type consistency.

## State And Persistence Behavior
No persistent state exists; wrappers hold pointers to the cache context and underlying entries. Cached directory data is owned by the provided `DirectoryCacher`.

## Dependencies And Integration Points
Integrates the `fs` package interfaces and `Cache.IterateEntries` from `cache.go`.

## Risks And Edge Cases
Wrapping preserves only Directory/File/Symlink type categories; entries implementing multiple extra interfaces may lose direct type assertions unless embedded interface exposes them. The cacher must be non-nil for directory iteration.

## Test Signals
Tests should cover Child and IterateEntries wrapping, nested directory reuse of context, and preservation of file/symlink behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cachefs.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/doc.go -->
# sources/sync-backup/kopia/fs/doc.go

## Purpose
Provides the package comment for `github.com/kopia/kopia/fs`, declaring it as virtual filesystem abstractions.

## Important APIs, Types, And Functions
There are no APIs beyond the package declaration and comment.

## Control Flow
No runtime control flow exists.

## State And Persistence Behavior
No state or persistence behavior exists.

## Dependencies And Integration Points
Serves Go documentation integration for the `fs` package, whose concrete interfaces are defined in neighboring files such as `entry.go`.

## Risks And Edge Cases
The only risk is documentation drift if the package scope changes beyond virtual filesystem abstractions.

## Test Signals
Build/doc generation is the only direct test signal; package behavior is tested by other fs files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/doc.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry.go -->
# sources/sync-backup/kopia/fs/entry.go

## Purpose
Defines core virtual filesystem interfaces and utility functions used throughout snapshot, restore, localfs, virtualfs, and snapshotfs code.

## Important APIs, Types, And Functions
Key definitions are `Entry`, `OwnerInfo`, `DeviceInfo`, `Reader`, `File`, `StreamingFile`, `Directory`, `DirectoryIterator`, `DirectoryWithSummary`, `ErrorEntry`, `EntryWithError`, `DirectorySummary`, `Symlink`, `ErrUnknown`, `ErrEntryNotFound`, and `ModBits`. Helpers include `IterateEntries`, `GetAllEntries`, `IterateEntriesAndFindChild`, `DirectorySummary.Clone`, `FindByName`, and `Sort`.

## Control Flow
Directory utilities use the iterator contract: call `Iterate`, defer `Close`, call `Next` until nil entry, propagate iterator or callback errors, and wrap callback failures with entry names.

## State And Persistence Behavior
The file has no persistent state. It defines data shapes that are persisted elsewhere, especially `DirectorySummary` JSON fields in snapshot metadata.

## Dependencies And Integration Points
Integrates Go `os.FileInfo`, `io` interfaces, sort/search utilities, and package timestamp type `UTCTimestamp`.

## Risks And Edge Cases
`FindByName` assumes sorted input; callers using unsorted slices get undefined lookup results. `DirectorySummary.Clone` shallow-copies entry objects but copies the slice. Iterator contract says calling Next after end is undefined.

## Test Signals
Tests cover sort and binary search. Broader integration tests across snapshot upload/restore validate interface contracts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_dir_iterator.go -->
# sources/sync-backup/kopia/fs/entry_dir_iterator.go

## Purpose
Provides a simple static `DirectoryIterator` implementation over a prebuilt entry slice and optional final error.

## Important APIs, Types, And Functions
Defines `staticIterator`, methods `Close` and `Next`, and constructor `StaticIterator`.

## Control Flow
`Next` returns entries in order while `cur < len(entries)`, incrementing each time. It returns the configured `err` alongside each entry, then returns `(nil, nil)` after all entries are consumed.

## State And Persistence Behavior
No persistent state exists beyond iterator position in memory.

## Dependencies And Integration Points
Integrates the `DirectoryIterator` interface from `entry.go` and is useful for virtual or test directories.

## Risks And Edge Cases
Returning `it.err` with every entry is unusual because the iterator contract treats `(entry,nil)` as success and `(nil,err)` as failure. Callers that stop on nonnil error may ignore returned entries when `err` is set.

## Test Signals
Tests should cover normal iteration, empty slices, configured error semantics, and Close idempotence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_dir_iterator.go -->
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_test.go -->
# sources/sync-backup/kopia/fs/entry_test.go

## Purpose
Unit tests for entry sorting and sorted lookup helpers.

## Important APIs, Types, And Functions
Defines a lightweight `testEntry` with a `Name` method and embedded `Entry`, then tests `FindByName` and `Sort`.

## Control Flow
`TestEntriesFindByName` searches a sorted slice for an existing name and several missing positions. `TestEntriesSort` sorts unsorted entries and compares against expected order using pretty diff.

## State And Persistence Behavior
No persistent state is involved.

## Dependencies And Integration Points
Integrates fs helper functions and the `godebug/pretty` diff library.

## Risks And Edge Cases
The lookup test assumes input is sorted, matching the helper contract. It does not test duplicate names or unsorted lookup failure modes.

## Test Signals
Good low-level signal for name ordering helpers used by virtual filesystem and snapshot traversal code.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_test.go -->
