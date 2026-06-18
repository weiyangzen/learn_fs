# subset-b-008177 grouped research

This grouped report covers the requested `sources/object-store/minio-mc/cmd` files. Each section is delimited for deterministic reconciliation into `Docs/researches/<source-path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-status.go -->
# sources/object-store/minio-mc/cmd/replicate-status.go

## Purpose
Implements `mc replicate status`, the bucket server-side replication status command. It gathers live replication metrics, remote target health, replication configuration, and optional per-node transfer rates, then renders either JSON or a detailed terminal table.

## Important APIs, types, and functions
- `replicateStatusFlags` defines `--backlog` and `--nodes`; only `--nodes` is used in this file.
- `replicateStatusCmd` registers the `status` subcommand under replication.
- `checkReplicateStatusSyntax` enforces exactly one `TARGET/BUCKET`.
- `replicateStatusMessage` is the default output payload, carrying `replication.MetricsV2`, remote targets, and the active `replication.Config`.
- `replicateXferMessage` is the `--nodes` output payload around `replication.ReplQueueStats`.
- `getNodeTheme` hashes node names with FNV to assign stable color themes.

## Control flow
`mainReplicateStatus` creates a cancelable context, configures console colors, validates syntax, constructs a regular client plus an admin client, fetches metrics with `GetReplicationMetrics`, fetches remote targets with `ListRemoteTargets`, and fetches replication configuration with `GetReplication`. If `--nodes` is set it prints `replicateXferMessage`; otherwise it prints `replicateStatusMessage`.

`replicateStatusMessage.String` normalizes stale ARN metrics away by comparing metric ARNs against current replication rules and role ARN. It then builds a table of target-specific replication counts, queue depth, transfer rate, target latency, link health, downtime, errors, and optional bandwidth limit state. Multi-target mode adds a summary section. `replicateXferMessage.String` renders node-level large and small object transfer rates and workers.

## State and persistence
The command does not persist local state. It reads remote MinIO server state: bucket replication metrics, remote target definitions, and replication config. Time-dependent fields include uptime, total/current downtime, latency, and queue stats.

## Dependencies and integration points
Integrates with MinIO client abstractions (`newClient`, `GetReplicationMetrics`, `GetReplication`), MinIO admin API (`newAdminClient`, `ListRemoteTargets`), `minio-go/pkg/replication`, `madmin-go/v3`, `console` color themes, `tablewriter`, and global output machinery via `printMsg`.

## Risks and edge cases
- Stale metric ARNs are filtered by rule destination or role ARN; a mismatch between config and metrics can hide historical data.
- `ListRemoteTargets` and `GetReplication` are fatal, so partial status cannot be displayed if one metadata call fails.
- Negative replicated counts and sizes are explicitly clamped after stale target subtraction.
- `--backlog` is declared but unused here, suggesting either implementation elsewhere or a stale flag.

## Test signals
No direct tests in this subset. Coverage would need command-level tests that mock client/admin APIs and formatter tests for stale ARN filtering, single-target vs multi-target output, and node transfer rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-update.go -->
# sources/object-store/minio-mc/cmd/replicate-update.go

## Purpose
Implements `mc replicate update`/`edit`, modifying an existing server-side replication rule and optionally its associated remote target credentials, sync/proxy/path/healthcheck/bandwidth settings.

## Important APIs, types, and functions
- `replicateUpdateFlags` exposes rule fields (`--id`, `--tags`, `--storage-class`, `--state`, `--priority`, `--replicate`) and remote target fields (`--remote-bucket`, `--sync`, `--proxy`, `--bandwidth`, `--healthcheck-seconds`, `--path`).
- `checkReplicateUpdateSyntax` requires exactly one target.
- `modifyRemoteTarget` finds a target by ARN, validates bucket identity, parses replacement credentials/endpoint from `--remote-bucket`, and returns a cloned `madmin.BucketTarget` plus `madmin.TargetUpdateType` operations.
- `replicateUpdateMessage` formats success output.
- `mainReplicateUpdate` coordinates rule update and optional admin target update.

## Control flow
The main command validates arguments, loads the current replication config, requires `--id`, validates optional `--state`, extracts the source bucket from an `S3Client`, builds an admin client, and lists remote targets. It finds the ARN for the requested rule ID, preferring `rcfg.Role` when present.

If `--remote-bucket` is set, `modifyRemoteTarget` updates target credentials and any selected target attributes, then `UpdateRemoteTarget` persists the changes. If target-only flags are set without `--remote-bucket`, the command fails. It then parses `--replicate` into delete-marker, permanent-delete, metadata-sync, and existing-object replication statuses, builds `replication.Options`, and calls `client.SetReplication`.

## State and persistence
Persists remote server state only. `UpdateRemoteTarget` changes MinIO remote target configuration, while `SetReplication` changes bucket replication rules. No local config files are written.

## Dependencies and integration points
Uses MinIO client/admin constructors, `madmin.BucketTarget`, `madmin.TargetUpdateType`, `madmin.ParseARN`, `replication.Options`, `s3utils.CheckValidBucketName`, credential URL parsing, bandwidth parsing, and global fatal/print helpers.

## Risks and edge cases
- If the rule ID is not found, `arn` remains empty and `modifyRemoteTarget` will fail with not found; the replication options later also refer to that empty destination.
- Remote target updates validate target bucket and source bucket against the existing target to avoid accidental retargeting.
- `--sync`, `--proxy`, `--bandwidth`, `--healthcheck-seconds`, and `--path` are rejected unless `--remote-bucket` is also present.
- Credentials are parsed from URLs or aliases; malformed or missing bucket paths are fatal.
- `--replicate ""` intentionally disables all replicate subfeatures.

## Test signals
No direct tests in this subset. Good test coverage would exercise `modifyRemoteTarget` for ARN matching, credential URL parsing, sync/proxy validation, operation list construction, and `--replicate` parsing.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-clear.go -->
# sources/object-store/minio-mc/cmd/retention-clear.go

## Purpose
Implements `mc retention clear`, clearing object retention settings for one object/version or a listed set of objects, plus `--default` bucket object-lock configuration clearing.

## Important APIs, types, and functions
- `retentionClearFlags` defines `--recursive`, `--version-id`, `--rewind`, `--versions`, and `--default`.
- `retentionClearCmd` registers the CLI command.
- `parseClearRetentionArgs` validates one target and rejects object/list flags when bucket default mode is requested.
- `clearRetention` delegates object-level work to `applyRetention` with `lockOpClear`, no mode, zero validity, and governance bypass forced true.
- `clearBucketLock` delegates bucket-level work to `applyBucketLock`.
- `mainRetentionClear` wires validation, object-lock support checking, default rewind behavior, and execution.

## Control flow
The command parses the target and flags, configures retention colors, checks object-lock support with `fatalIfBucketLockNotSupported`, then either clears the bucket default retention config or applies clear retention to the object/list target. If `--versions` is set without `--rewind`, it uses the current UTC time as the list time reference.

## State and persistence
Mutates remote S3/MinIO object-lock state. Object mode clears per-object retention using `PutObjectRetention` through shared code; bucket mode changes the bucket object-lock configuration. No local state is persisted.

## Dependencies and integration points
Depends on `retention-common.go` for shared retention messages and apply logic, `parseRewindFlag`, MinIO object-lock APIs, global context, and CLI/global output helpers.

## Risks and edge cases
- `--default` is mutually exclusive with object-scoped flags, preventing ambiguous bucket/object operations.
- Governance bypass is always enabled for clear, which is powerful and depends on server-side permissions.
- `fatalIfBucketLockNotSupported` runs before bucket mode too; unsupported remotes fail early.
- `--versions` without `--rewind` snapshots at current UTC, which can surprise users expecting all historical versions independent of a time reference.

## Test signals
No direct tests in this subset. Useful tests would cover flag conflict validation, default rewind injection, and that clear delegates with `bypassGovernance=true`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-clear.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-common.go -->
# sources/object-store/minio-mc/cmd/retention-common.go

## Purpose
Provides shared object-lock and retention behavior for `retention set`, `clear`, and `info`: message types, validity parsing, per-object retention application, recursive/version listing, bucket default lock application, and bucket default lock display.

## Important APIs, types, and functions
- `retentionCmdMessage` and `retentionBucketMessage` implement text/JSON output for object and bucket retention operations.
- `lockOpType` and constants `lockOpInfo`, `lockOpClear`, `lockOpSet` identify operation mode.
- `getRetainUntilDate` computes RFC3339 retain-until timestamps from day/year validity.
- `setRetentionSingle` uses `newClientFromAlias` and `PutObjectRetention` for a single object/version.
- `parseRetentionValidity` parses `Nd`/`Ny` retention duration strings.
- `fatalIfBucketLockNotSupported` checks bucket lock support.
- `applyRetention` handles single-object or listed-object retention mutation.
- `applyBucketLock` sets, clears, or fetches bucket object-lock config.
- `showBucketLock` reads bucket object-lock config for display.

## Control flow
`applyRetention` validates that the target resolves to an `S3Client`, computes `retainUntil` only for set operations, expands aliases, and chooses a single-object path when `versionID` is present or neither recursive nor versions is requested. Otherwise it lists with `ListOptions`, optionally including older versions and delete markers for rewind/version mode. It skips delete markers, stops early in non-recursive exact-object mode, calls `setRetentionSingle`, tracks whether any eligible object/version was found, and returns an exit status if none were processed.

`applyBucketLock` creates a client, uses a cancelable global context, calls `SetObjectLockConfig` for set/clear or `GetObjectLockConfig` for info-like behavior, then prints a `retentionBucketMessage`.

## State and persistence
All state changes are remote object-lock mutations. `setRetentionSingle` persists object retention. `applyBucketLock` persists bucket default object-lock configuration. Shared messages include operation status and errors for scriptable output.

## Dependencies and integration points
Uses MinIO client abstractions (`newClient`, `newClientFromAlias`, `List`, `PutObjectRetention`, `SetObjectLockConfig`, `GetObjectLockConfig`), alias utilities, `ClientContent` list metadata, `probe.Error`, and console/global print helpers.

## Risks and edge cases
- `parseRetentionValidity` assumes a non-empty string and indexes the last byte; callers must ensure syntax.
- Delete markers are skipped because object retention cannot be applied to them.
- `applyRetention` fatal-exits for non-S3 clients.
- Non-recursive listed mode compares standardized URLs and breaks once it moves past the target object.
- The bucket message says "Object locking is not enabled" when mode is invalid, even if the raw enabled status has other nuance.

## Test signals
No direct tests in this subset. Important tests would cover validity parsing, zero validity rejection, list filtering, delete marker skipping, S3-only enforcement, and bucket lock set/clear/info branching.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-info.go -->
# sources/object-store/minio-mc/cmd/retention-info.go

## Purpose
Implements `mc retention info`, showing object retention for a single object/version, a recursive/listed set, or the default bucket object-lock configuration.

## Important APIs, types, and functions
- `retentionInfoFlags` mirrors the clear command with `--recursive`, `--version-id`, `--rewind`, `--versions`, and `--default`.
- `parseInfoRetentionArgs` validates one target and bucket-mode flag conflicts.
- `retentionInfoMessage` is the shared data model.
- `retentionInfoMessageList` renders compact list output for multi-object mode.
- `retentionInfoMessageRecord` renders detailed single-object output.
- `retentionInfoMsg` abstracts setters plus the `message` interface.
- `infoRetentionSingle` calls `GetObjectRetention` and prints either list or record style.
- `getRetention` handles single-object, bucket fallback, and listed recursive/version modes.

## Control flow
`mainRetentionInfo` configures colors, parses flags, verifies bucket lock support, dispatches to `showBucketLock` for `--default`, injects current UTC rewind for `--versions` without `--rewind`, then calls `getRetention`.

`getRetention` validates S3-only support and expands aliases. In direct mode it calls `infoRetentionSingle`; if the direct stat represents an empty object name, it falls back to `showBucketLock`, which makes bucket URLs behave as bucket default inspection. In list mode it uses `ListOptions`, skips delete markers, stops in non-recursive exact-object mode, prints list-style records, and returns an error exit status when no object/version is found.

## State and persistence
Read-only against remote retention state. No local persistence. The output status changes to failure for per-object errors but successful no-retention states are represented as mode empty.

## Dependencies and integration points
Depends on shared retention utilities, `newClient`, `newClientFromAlias`, MinIO `GetObjectRetention`, `showBucketLock`, `parseRewindFlag`, and global output/error helpers.

## Risks and edge cases
- `fatalIfBucketLockNotSupported` runs before both bucket and object info.
- `NoSuchObjectLockConfiguration` is treated as a successful "no retention" object response; other errors print failures except `ObjectNameEmpty`.
- List output marks governance entries expired when `now.After(until)` but compliance mode list output does not show an expiration label.
- The error string in list style has a duplicated "get get".

## Test signals
No direct tests in this subset. Coverage should include direct object info, no-lock behavior, bucket URL fallback, version/list traversal, and JSON failure status handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-main.go -->
# sources/object-store/minio-mc/cmd/retention-main.go

## Purpose
Defines the top-level `mc retention` command and wires its subcommands.

## Important APIs, types, and functions
- `retentionSubcommands` contains `retentionSetCmd`, `retentionClearCmd`, and `retentionInfoCmd`.
- `retentionCmd` registers command name, usage, global flags, and `setGlobalsFromContext`.
- `mainRetention` delegates unknown or missing subcommands to `commandNotFound`.

## Control flow
The top-level action does not execute retention logic. Actual behavior lives in the selected subcommand. If invoked without a valid subcommand, it reports command-not-found/help through the shared command dispatcher.

## State and persistence
No state. This file only registers command metadata.

## Dependencies and integration points
Integrates with the MinIO CLI command tree and the subcommands implemented in `retention-set.go`, `retention-clear.go`, and `retention-info.go`.

## Risks and edge cases
Minimal. The main risk is command tree drift if a subcommand is renamed but not updated in `retentionSubcommands`.

## Test signals
No direct tests. CLI command registration tests could assert the three subcommands are present and global setup is attached.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-set.go -->
# sources/object-store/minio-mc/cmd/retention-set.go

## Purpose
Implements `mc retention set`, applying governance/compliance retention to objects or setting default bucket retention.

## Important APIs, types, and functions
- `retentionSetFlags` defines object/list flags and `--bypass` plus `--default`.
- `parseSetRetentionArgs` validates `MODE VALIDITY TARGET`, mode validity, `Nd`/`Ny` retention duration, target, and bucket-mode conflicts.
- `setRetention` delegates object/list mutation to `applyRetention`.
- `setBucketLock` delegates default bucket retention to `applyBucketLock`.
- `mainRetentionSet` wires parsing, support checks, default rewind behavior, and execution.

## Control flow
The command accepts exactly three positional arguments. It uppercases and validates retention mode with MinIO's `RetentionMode.IsValid`, parses validity through `parseRetentionValidity`, and rejects `--default` combined with object/list/bypass flags. Bucket mode directly calls `setBucketLock`; object mode checks object-lock support, injects current UTC rewind for all-versions mode when needed, and applies retention through shared listing/single-object logic.

## State and persistence
Persists remote object retention or bucket default object-lock configuration. No local files are changed.

## Dependencies and integration points
Uses `retention-common.go`, MinIO `RetentionMode` and `ValidityUnit`, CLI/global context, `parseRewindFlag`, and console output helpers.

## Risks and edge cases
- `--bypass` is rejected for bucket defaults but allowed for object governance mutations.
- Validity parsing is byte-suffix based, so callers rely on prior argument count and non-empty input.
- `--versions` without `--rewind` applies to versions visible as of command start time.
- Compliance retention can create irreversible remote state subject to server policy.

## Test signals
No direct tests. Tests should cover mode validation, validity parsing, `--default` conflicts, and delegation parameters for object vs bucket mode.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retention-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retry.go -->
# sources/object-store/minio-mc/cmd/retry.go

## Purpose
Provides a small reusable retry manager for commands that want bounded retry attempts with jitter and cancellation.

## Important APIs, types, and functions
- `retryManager` tracks attempt count, max retries, interval, parent command context, and a retry-specific cancellation context.
- `newRetryManager` creates a retry context independent of the command context and stores its cancel function.
- `retryMessage` formats retry telemetry for text/JSON output.
- `(*retryManager).retry` repeatedly invokes an action until success, max retries, retry cancellation, or command cancellation.

## Control flow
`retry` defers cancellation of its retry context, then loops while `retries <= maxRetries`. It calls the provided action with the manager. A nil error returns immediately. On error it waits for either retry cancellation, parent command cancellation, or a randomized delay between half the retry interval and roughly 1.5x the retry interval, then increments the retry count.

## State and persistence
In-memory only. The manager mutates `retries` and context state. It does not persist attempt data.

## Dependencies and integration points
Uses Go `context`, `time`, `math/rand`, `probe.Error`, color JSON output, and global `fatalIf` for JSON marshalling errors.

## Risks and edge cases
- Loop condition `<= maxRetries` means the action can run `maxRetries + 1` times.
- Uses the package-level `math/rand` source without explicit seeding here; jitter may be deterministic depending on process setup.
- `retryCtx` is based on `context.Background`, so only explicit `cancelRetry` or parent `commandCtx` stops it.

## Test signals
No direct tests. Useful tests would assert attempt counts, cancellation by command context, cancellation by retry context, and jitter path behavior with very small intervals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/rm-main.go -->
# sources/object-store/minio-mc/cmd/rm-main.go

## Purpose
Implements `mc rm`, including single-object deletion, recursive deletion, versioned deletion, incomplete upload deletion, dry-run, stdin-driven deletion, retention governance bypass, non-current version cleanup, dangerous namespace removal protection, and hidden purge behavior.

## Important APIs, types, and functions
- `rmFlags` defines deletion mode, safety, version, rewind, incomplete upload, dry-run, stdin, age filters, bypass, non-current, and hidden purge flags.
- `rmCmd` registers the command.
- `rmMessage` is the output model for removed objects, delete markers, versions, mod time, and dry-run.
- `checkRmSyntax` enforces safety and incompatible flag combinations.
- `removeSingle` handles direct deletion of one object or one version.
- `removeOpts` carries deletion behavior into helpers.
- `printDryRunMsg` prints dry-run output from `ClientContent`.
- `listAndRemove` lists and streams objects/versions into `Client.Remove`.
- `mainRm` parses flags, loops over CLI args, then optional stdin lines.

## Control flow
`checkRmSyntax` rejects `--version-id` with recursive/version/rewind, requires `--non-current` with both recursive and versions, restricts hidden `--purge`, requires target args or `--stdin`, requires `--force` for recursive/version/stdin modes, and requires both `--dangerous` and `--force` for namespace-wide removals.

`removeSingle` expands aliases, stats the object unless purge mode is active, tolerates specific HEAD errors that should not block deletion, applies age filters, prints dry-run if requested, constructs a single-content channel, calls `clnt.Remove`, and prints `rmMessage` results.

`listAndRemove` creates a list channel and a remove result channel. It lists objects according to recursive, incomplete, version, and rewind options. Normal mode filters prefix levels and age limits, then sends eligible contents to the remove channel while draining results. `--non-current` groups versions per object path, skips the latest live version, and removes only older/delete-marker versions matching age filters. It drains all results after closing the channel and emulates `rm -f` by not erroring when no object is found with `--force`.

`mainRm` builds `removeOpts` and applies the chosen helper for each positional target and each stdin line, preserving the first error.

## State and persistence
Mutates remote object storage state through `Client.Remove`. It may create delete markers in versioned buckets, delete specific versions, purge incomplete uploads, or bypass governance if authorized. No local persistence.

## Dependencies and integration points
Uses URL/stat helpers (`url2Stat`, `mustExpandAlias`, `newClientFromAlias`), client listing/removal APIs, `ListOptions`, age filters (`isOlder`, `isNewer`), MinIO S3 error mapping, `ClientContent`, global contexts, and global output/error helpers.

## Risks and edge cases
- Deletion is irreversible unless bucket versioning protects with delete markers, hence the extensive safety checks.
- The code tolerates some stat failures for delete markers and SSE-C but cannot apply age filters without mod time.
- Non-current version mode relies on listing order by object path and version order.
- WORM/object-lock errors are ignored in one recursive path when the message contains a specific string.
- Stdin mode shares global flags for every line and preserves the first error only.
- Hidden `--purge` bypasses normal stat/list behavior and is tightly constrained.

## Test signals
No direct tests in this subset. High-value tests would mock list/remove streaming, flag validation combinations, non-current grouping, dry-run output, age filter behavior, stdin iteration, and permission/WORM error handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/rm-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-db-v1.go -->
# sources/object-store/minio-mc/cmd/share-db-v1.go

## Purpose
Defines the version 1 local JSON database used to persist generated share upload/download URLs.

## Important APIs, types, and functions
- `shareEntryV1` records original object URL, version ID, creation date, expiry duration, and optional content type.
- `shareDBV1` stores DB version, a mutex, and a map keyed by share URL.
- `newShareDBV1` initializes version `1`, the map, and mutex.
- `Set` inserts or replaces a share entry keyed by `shareURL`.
- `Delete` removes a map entry by key, despite the parameter being named `objectURL`.
- `deleteAllExpired` removes expired entries.
- `Load` loads from disk with `quick`, copies entries, prunes expired shares, and saves the pruned DB.
- `save` and `Save` persist through `quick.NewConfig`.

## Control flow
Callers create a DB with `newShareDBV1`, call `Load(filename)`, mutate entries with `Set`/`Delete`, then call `Save(filename)`. `Load` checks file existence, loads using the MinIO `quick` config layer, copies loaded shares into the current DB, prunes expired entries, and writes the cleaned DB back to disk.

## State and persistence
Persists JSON files in the share config directory, normally `uploads.json` and `downloads.json`. Mutexes protect in-process map access, but there is no inter-process file lock.

## Dependencies and integration points
Used by share upload/download/list commands. Depends on `github.com/minio/pkg/v3/quick`, Go `maps.Copy`, `os.Stat`, and `UTCNow`.

## Risks and edge cases
- No cross-process locking, so concurrent `mc share` processes can race and lose updates.
- `Delete(objectURL string)` deletes by map key, which is actually share URL; the parameter name can mislead callers.
- `Load` ignores loaded `Version` except through the target structure; migrations are handled elsewhere.
- `deleteAllExpired` mutates the map without taking a lock itself, but current callers invoke it under the `Load` lock.

## Test signals
No direct tests in this subset. Tests should cover load/save round trips, expired entry pruning and rewrite, Set/Delete key semantics, and concurrent in-process access.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-db-v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-download-main.go -->
# sources/object-store/minio-mc/cmd/share-download-main.go

## Purpose
Implements `mc share download`, generating presigned download URLs for one or more S3 objects or recursively listed object sets, and saving generated shares locally.

## Important APIs, types, and functions
- `shareDownloadFlags` defines `--recursive`, `--version-id`, and `--expire`.
- `checkShareDownloadSyntax` validates target presence, expiry bounds, `--version-id`/`--recursive` conflict, and direct object existence.
- `doShareDownloadURL` expands aliases, stats target, chooses direct or listed object flow, calls `ShareDownload`, prints messages, and saves shares.
- `mainShareDownload` parses encryption keys, initializes share config, sets colors, parses expiry, and processes all targets.

## Control flow
Syntax validation parses expiry duration and enforces 1 second to 7 days. For non-recursive targets it stats objects up front using encryption keys. During execution, `doShareDownloadURL` loads the downloads DB, stats the target via the client, emits one object for file targets or lists a directory/prefix, skips directories, creates a new client per object URL, generates a presigned download URL with optional version ID, stores it in the DB, and prints a `shareMessage`. After all objects are processed, the DB is saved.

## State and persistence
Writes generated download shares to the local downloads DB returned by `getShareDownloadsFile`. It also prunes expired entries as a side effect of `Load`.

## Dependencies and integration points
Depends on share config and DB helpers, MinIO client `Stat`, `List`, and `ShareDownload`, encryption-key parsing for stat validation, alias expansion, `ClientContent`, and global output/fatal helpers.

## Risks and edge cases
- Recursive sharing still calls `Stat` before listing; targets that cannot be statted fail early.
- Version ID is only allowed for non-recursive direct targets.
- The function opens and saves the DB once per target, so multiple targets in one invocation are safe sequentially but separate processes can race.
- Non-S3 clients return `APINotImplemented` and are reported as unsupported.

## Test signals
No direct tests in this subset. Tests should cover expiry validation, recursive/version conflict, direct object existence validation, DB updates, and list/direct generation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-download-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-list-main.go -->
# sources/object-store/minio-mc/cmd/share-list-main.go

## Purpose
Implements `mc share list`/`ls`, listing locally persisted, unexpired upload or download share entries.

## Important APIs, types, and functions
- `shareList` registers the command and `ls` short name.
- `checkShareListSyntax` requires one argument: `upload` or `download`.
- `doShareList` loads the selected share DB and prints each entry as `shareMessage`.
- `mainShareList` validates args, sets colors, initializes share config, and executes listing.

## Control flow
`mainShareList` initializes the share directory and DB files if missing, then calls `doShareList`. The DB `Load` operation prunes expired entries before printing. Each remaining map entry is printed with its object URL, share URL, time left, and optional content type.

## State and persistence
Read-mostly local state. It can update the selected JSON DB indirectly because `Load` deletes expired shares and saves the pruned result.

## Dependencies and integration points
Uses share DB/config helpers, `shareMessage`, MinIO CLI/global output, and `probe.Error`.

## Risks and edge cases
- Map iteration order is nondeterministic, so output ordering can vary.
- Expired entry pruning means a list operation mutates local config files.
- There is no filtering by target, age, or content type.

## Test signals
No direct tests. Useful tests would cover syntax validation, upload vs download DB selection, expired pruning side effect, and message fields.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-list-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-main.go -->
# sources/object-store/minio-mc/cmd/share-main.go

## Purpose
Defines the top-level `mc share` command, subcommand registration, and migration cleanup for legacy share storage.

## Important APIs, types, and functions
- `shareSubcommands` contains `shareDownload`, `shareUpload`, and `shareList`.
- `shareCmd` registers command metadata and hides the help subcommand.
- `migrateShare` deletes the legacy `urls.json` file from the share directory if present.
- `mainShare` reports missing/unknown subcommands via `commandNotFound`.

## Control flow
The top-level command does not perform share generation. Subcommands own their execution. `migrateShare` is intended to run during configuration migration: if the share directory exists and old `urls.json` exists, it removes it and informs the console.

## State and persistence
May delete the legacy local share file `urls.json`. Otherwise no runtime state.

## Dependencies and integration points
Integrates with the CLI command tree and share config helpers. Uses `os.Stat`, `os.Remove`, `filepath.Join`, `probe.NewError`, and console output.

## Risks and edge cases
- `migrateShare` removes legacy data rather than converting it into upload/download DBs.
- Migration does nothing if the share directory does not exist.

## Test signals
No direct tests. Tests could assert subcommand registration and migration deletion behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-upload-main.go -->
# sources/object-store/minio-mc/cmd/share-upload-main.go

## Purpose
Implements `mc share upload`, generating a presigned POST/curl command that allows uploads without exposing credentials, then saving that command in the local share upload DB.

## Important APIs, types, and functions
- `shareUploadFlags` defines `--recursive`, `--expire`, and `--content-type`.
- `shellQuoteRegex` and `shellQuote` escape shell-special characters in generated curl form values.
- `checkShareUploadSyntax` validates targets, expiry bounds, and requires `--recursive` for prefix targets.
- `makeCurlCmd` builds the actual `curl -F ...` command from POST URL and form fields.
- `saveSharedURL` loads, updates, and saves the upload share DB.
- `doShareUploadURL` calls `ShareUpload`, prints output, and persists it.
- `mainShareUpload` parses flags and loops over targets.

## Control flow
Syntax validation enforces at least one target, parses expiry from `--expire`, limits it to 1 second through 7 days, and checks that targets ending in the client URL separator require recursive mode. Execution initializes local share config, parses expiry/content type, and for each target constructs a client, calls `ShareUpload(ctx, isRecursive, expiry, contentType)`, converts the returned POST form into a curl command, prints a `shareMessage`, and stores it in `uploads.json`.

## State and persistence
Writes generated upload curl commands to the local uploads DB. DB load prunes expired entries. No remote object is created; the remote interaction only creates presigned POST data.

## Dependencies and integration points
Uses MinIO client `ShareUpload`, local share DB/config helpers, global output, and shell quoting helpers. Non-S3 targets surface `APINotImplemented`.

## Risks and edge cases
- Map iteration over `uploadInfo` makes curl form field ordering nondeterministic, though semantically equivalent.
- `postURL` is not shell-quoted, so it assumes the presigned URL returned by the client is already safe as a shell token.
- Recursive mode appends `<NAME>` to the key field, which the UI highlights and users must replace.
- `saveSharedURL` ignores the return from `shareDB.Save`, returning nil even if save fails after `Set`.

## Test signals
`share-upload_test.go` covers `makeCurlCmd` escaping of spaces, quotes, ampersands, angle brackets, pipes, parentheses, backticks, tabs, semicolons, dollar signs, and hash characters. Additional tests should cover expiry validation, recursive prefix validation, and save error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-upload-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-upload_test.go -->
# sources/object-store/minio-mc/cmd/share-upload_test.go

## Purpose
Tests shell escaping in upload share curl command generation.

## Important APIs, types, and functions
- `TestMakeCurlCmdEscapesSpecialChars` drives `makeCurlCmd` with keys containing shell-special characters and checks the generated command contains escaped `key=` form fields.

## Control flow
The test table enumerates object keys and expected escaped values. For each case it calls `makeCurlCmd(key, "http://example.com", false, map[string]string{})` and asserts the resulting command string contains ` key=<escaped> `.

## State and persistence
No state. It does not touch share DB files or remote clients.

## Dependencies and integration points
Depends on `makeCurlCmd` and indirectly `shellQuote`. Uses Go `testing` and `strings.Contains`.

## Risks and edge cases
- The test only checks non-recursive command generation with an empty `uploadInfo` map.
- It does not assert POST URL quoting, form field ordering, recursive `<NAME>` behavior, or upload metadata fields.

## Test signals
This is a direct regression signal for command injection/shell escaping risks in generated curl commands.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share-upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share.go -->
# sources/object-store/minio-mc/cmd/share.go

## Purpose
Provides common constants, flags, message formatting, color setup, and local config-file helpers for share upload/download/list commands.

## Important APIs, types, and functions
- `shareDefaultExpiry` is 7 days.
- `shareFlagContentType` and `shareFlagExpire` are shared CLI flags.
- `shareMessage` is the common output type for object URL, share URL, time left, and optional content type.
- `shareMessage.String` prints text output and highlights `<FILE>` and `<NAME>` placeholders.
- `shareMessage.JSON` marshals JSON and unescapes `&`, `<`, and `>` for usable share URLs/templates.
- `shareSetColor` configures console themes.
- `getShareDir`, `mustGetShareDir`, `createShareDir`, `getShareUploadsFile`, `getShareDownloadsFile`, and existence helpers manage local paths.
- `initShareConfig` creates the share directory and empty upload/download DBs.

## Control flow
Subcommands call `initShareConfig` before reading or writing share DBs. It creates the share directory with mode `0700`, initializes `uploads.json` and `downloads.json` using `newShareDBV1().Save`, and prints informational messages unless quiet/JSON mode is active. `shareMessage` handles both text and JSON output paths through the global `message` interface.

## State and persistence
Creates and maintains local files under the mc config directory's shared URLs data directory: `uploads.json` and `downloads.json`. It does not itself add share entries; command files do that through `shareDBV1`.

## Dependencies and integration points
Uses config path helpers (`getMcConfigDir`), global constants (`globalSharedURLsDataDir`), `quick` through DB initialization, console color, global quiet/JSON flags, and `probe.Error`.

## Risks and edge cases
- `mustGetShareDir` fatal-exits on config path errors, so many helper calls can terminate the command.
- JSON output intentionally reverses Go's HTML escaping for generated URLs and placeholders.
- Directory mode is restrictive, but file permissions are controlled by `quick.Save`.

## Test signals
No direct tests in this subset. Tests should cover config initialization, JSON unescaping, placeholder highlighting, and quiet/JSON suppression of init messages.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/share.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/signals.go -->
# sources/object-store/minio-mc/cmd/signals.go

## Purpose
Centralizes OS signal handling for the CLI by canceling global context, stopping profiling, and exiting with signal-specific status codes.

## Important APIs, types, and functions
- `trapSignals(sig ...os.Signal)` registers for supplied signals, waits for one signal, optionally cancels global state, and exits.

## Control flow
The function creates a buffered signal channel, registers it with `signal.Notify`, blocks until a signal arrives, stops notifications, and checks `GlobalTrapSignals`. If trapping is disabled it returns, allowing caller-specific handling. Otherwise it calls `stopProfiling`, cancels `globalContext` via `globalCancel`, maps signal string to global exit status, and calls `os.Exit`.

## State and persistence
Mutates process state only: signal registration, profiling lifecycle, global context cancellation, and process exit. No file or remote persistence.

## Dependencies and integration points
Integrates with global context variables, profiling cleanup, and global exit status constants. Uses Go `os` and `os/signal`.

## Risks and edge cases
- The signal channel is closed by defer after `signal.Stop`, which is safe for this local channel but can be risky if external senders existed.
- It relies on `s.String()` values like `interrupt`, `killed`, and `terminated`.
- `SIGKILL` cannot actually be trapped on Unix, so the `killed` branch is mostly defensive.

## Test signals
No direct tests. Testing would require process-level signal handling or factoring signal-to-exit-code mapping.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/signals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/speedtest-spinner.go -->
# sources/object-store/minio-mc/cmd/speedtest-spinner.go

## Purpose
Implements Bubble Tea UI rendering for MinIO speed test progress and final summaries across object, network, site replication, drive, and client performance tests.

## Important APIs, types, and functions
- `speedTestUI` is the Bubble Tea model with spinner, quit state, and current `PerfTestResult`.
- `PerfTestType` identifies test categories and `Name` maps values to display names.
- `PerfTestResult` carries one of several `madmin` speed test result types, an error, and a final flag.
- `initSpeedTestUI`, `Init`, `Update`, and `View` implement Bubble Tea lifecycle.

## Control flow
`Update` handles key presses (`q`, `esc`, `ctrl+c`) by quitting, handles `PerfTestResult` messages by storing the latest result and quitting when final, and delegates other messages to the spinner. `View` returns an error view if `Err` is set, otherwise builds a table for whichever result pointer/slice is populated. During non-final state it shows an animated spinner; final state shows a tick and, for object tests, appends short and optional verbose results.

## State and persistence
In-memory UI state only. No persistence. It reads global `globalPerfTestVerbose` to decide extra object-test output.

## Dependencies and integration points
Uses Bubble Tea (`tea`), Bubbles spinner, Lip Gloss styles, `madmin-go` performance result structs, `tablewriter`, `humanize`, global symbols such as `tickCell`, `crossTickCell`, `objectTestShortResult`, and `objectTestVerboseResult`.

## Risks and edge cases
- `View` chooses the first non-nil result in a fixed order; malformed messages with multiple populated result fields will hide later fields.
- Site replication rate divides by whole seconds and explicitly handles zero duration.
- Endpoint strings are truncated to 64 characters.
- Drive result ordering is whatever server result order provides; network and site rows are sorted.

## Test signals
No direct tests. UI tests could feed `PerfTestResult` messages and assert rendered output for empty, error, final, and zero-duration cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/speedtest-spinner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/sql-main.go -->
# sources/object-store/minio-mc/cmd/sql-main.go

## Purpose
Implements `mc sql`, running S3 Select SQL expressions against objects or recursively against supported content types under a prefix.

## Important APIs, types, and functions
- `sqlFlags` covers query, recursive mode, CSV/JSON input and output serialization, compression, and optional CSV output headers.
- Valid key lists and abbreviation maps define accepted serialization options.
- `parseKVArgs` parses comma-delimited `key=value` options with escape replacement for `\n`, `\t`, and `\r`.
- `parseSerializationOpts` expands abbreviations and validates keys.
- `getInputSerializationOpts`, `getOutputSerializationOpts`, and `getSQLOpts` build `SelectObjectOpts`.
- `getCSVHeader`, `isSelectAll`, and `getCSVOutputHeaders` infer or use CSV output headers.
- `sqlSelect` runs `Client.Select` and copies result to stdout.
- `validateOpts` rejects CSV/JSON input flags for `.parquet`.
- `mainSQL` coordinates validation, stat/list traversal, and selection.

## Control flow
The command parses encryption keys and requires at least one target. For each target it stats the URL. File targets build query/options once for the first output header and call `sqlSelect`. Directory targets create a client and list with `Recursive` and metadata enabled, choose content type from extension or user metadata, and run select only for supported content type suffixes. CSV headers are written only once across the whole invocation.

Serialization parsing rejects simultaneous CSV/JSON input or output modes, rejects JSON output combined with CSV headers, and normalizes keys to lowercase long names.

## State and persistence
Read-only remote object access plus stdout streaming. No local or remote persistence. Uses encryption keys provided for command execution only.

## Dependencies and integration points
Uses S3 Select through the client abstraction, `SelectObjectOpts`, encryption-key helpers, `url2Stat`, object stream metadata helpers, gzip/bzip2 readers for header inference, MIME DB, global JSON flag, and global output/error helpers.

## Risks and edge cases
- `parseKVArgs` has custom comma parsing and can be sensitive to values containing comma-like sequences.
- Header inference reads the first line of the source object/stdin; for stdin this consumes input before selection.
- In recursive mode, `writeHdr` is set false inside the content-type suffix loop, which means unsupported first objects can still suppress headers.
- `sqlSelect` writes raw result bytes to stdout, bypassing the normal message system.
- Directory traversal silently skips unsupported content types.

## Test signals
`sql-main_test.go` covers `parseKVArgs` and `parseSerializationOpts` including duplicate keys, abbreviation expansion, invalid keys, case-insensitive long keys, and JSON input type parsing. More coverage is needed for recursive flow, header inference, parquet validation, and select invocation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/sql-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/sql-main_test.go -->
# sources/object-store/minio-mc/cmd/sql-main_test.go

## Purpose
Tests parsing of SQL command serialization option strings.

## Important APIs, types, and functions
- `testParseKVArgsCases` and `TestParseKVArgs` validate raw `key=value` parsing.
- `testParseSerializationCases` and `TestParseSerializationOpts` validate accepted keys, abbreviations, duplicate detection, case normalization, and error messages.

## Control flow
Each table-driven test calls the parser, converts `probe.Error` to a Go error, compares the actual error with an expected full or partial string, and checks expected parsed keys/values are present.

## State and persistence
No state or external dependencies.

## Dependencies and integration points
Targets helper functions from `sql-main.go`; uses standard Go `testing` and `strings`.

## Risks and edge cases
- Tests assert error text fragments, which can be brittle across wording changes.
- They do not check exact map size, so extra parsed keys could go unnoticed in some cases.
- They do not exercise command-level option conflict validation.

## Test signals
Good parser-level regression coverage for common CLI serialization strings and malformed inputs.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/sql-main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/stat-main.go -->
# sources/object-store/minio-mc/cmd/stat-main.go

## Purpose
Implements CLI registration and argument parsing for `mc stat`, which displays object, version, prefix, or bucket metadata.

## Important APIs, types, and functions
- `statFlags` defines `--rewind`, `--versions`, `--version-id`, `--recursive`, `--verbose`, and `--no-list`.
- `statCmd` registers the command with encryption-key support.
- `parseAndCheckStatSyntax` validates arguments, flag conflicts, and expands verbose alias-only targets to buckets.
- `mainStat` configures output colors, parses encryption keys, validates args, and calls `statURL` for each target.

## Control flow
Parsing requires non-empty arguments, rejects empty strings, rejects `--version-id` with multiple targets or with recursive/version/rewind flags, and rejects `--no-list` with recursive/version modes. In verbose mode for alias-only targets, it lists buckets and expands the target list to each bucket when possible.

`mainStat` sets object and bucket color themes, validates encryption keys, obtains parsed targets and mode flags, then calls `statURL` with `headOnly` from `--no-list`.

## State and persistence
Read-only. It does not persist local or remote state.

## Dependencies and integration points
Uses `stat.go` for actual metadata retrieval/formatting, encryption-key parsing, `newClient`, `ListBuckets`, global output/fatal helpers, and CLI/global flags.

## Risks and edge cases
- Verbose alias expansion depends on `ListBuckets`; if it fails or returns none, the original alias target is kept.
- `--no-list` is a direct HEAD path and intentionally incompatible with list-based modes.
- The fallback `args = []string{"."}` is unreachable after current syntax validation but preserves old behavior shape.

## Test signals
No direct tests for this file. Tests should cover flag conflict validation and verbose alias bucket expansion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/stat-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/stat.go -->
# sources/object-store/minio-mc/cmd/stat.go

## Purpose
Contains the core metadata retrieval and formatting logic for `mc stat`, including object stat messages and bucket-level metadata/usage display.

## Important APIs, types, and functions
- `statMessage` is the object metadata output model with fields for size, ETag, metadata, version, delete marker, restore state, checksum, expiration, and replication status.
- `statMessage.String` and `JSON` render text/JSON output.
- `parseStat` converts `ClientContent` to `statMessage`.
- `getStandardizedURL` normalizes paths for comparison.
- `statURL` orchestrates HEAD/stat, bucket info, listing, and version handling.
- `BucketInfo` models bucket properties: versioning, encryption, locking, replication, policy, location, tags, ILM, and notifications.
- `bucketInfoMessage` renders bucket info plus usage.
- `prettyPrintBucketMetadata` formats bucket configuration properties.

## Control flow
`statURL` creates a client, expands the target alias, computes prefix path handling, and chooses among several paths:
- `headOnly` or explicit `versionID`: call `url2Stat` directly and print object metadata.
- Non-recursive bucket/prefix without trailing slash: try `GetBucketInfo`, optionally fetch usage from admin `DataUsageInfo`, and print bucket info.
- Otherwise list with `ListOptions`, optionally including versions/delete markers and time reference, then for each listed content call `url2Stat`, trim prefix path, and print parsed stat messages.

It handles selected filesystem/list errors as non-fatal, skips Glacier storage class objects, verifies non-recursive prefix matching, filters by version ID when necessary, and returns object-missing when no entries are found.

## State and persistence
Read-only. It reads object metadata, bucket configuration, and admin data usage. No state is written.

## Dependencies and integration points
Uses client list/stat/admin abstractions, MinIO admin `DataUsageInfo`, lifecycle/notification/replication models, encryption key DB, `humanize`, `colorjson`, console themes, and global time/format constants.

## Risks and edge cases
- Bucket info path is attempted before list path for non-recursive targets without trailing slash.
- `statMessage.String` separates recognized encryption headers from general metadata; unrecognized encryption headers display "Unknown".
- Listing path calls `url2Stat` per object, which can be expensive for large recursive stats.
- `found` increments before filters such as Glacier skip and version ID filtering, so "not found" behavior can differ from "no printable stat".
- Bucket usage is best-effort; admin client failures leave usage zero.

## Test signals
`stat_test.go` covers `parseStat` metadata copying, size, expiry pointer behavior, type detection, and ETag quote trimming. More tests should cover bucket formatting, version/delete marker output, encryption metadata recognition, and `statURL` branch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/stat_test.go -->
# sources/object-store/minio-mc/cmd/stat_test.go

## Purpose
Tests conversion from `ClientContent` to `statMessage`.

## Important APIs, types, and functions
- `TestParseStat` is table-driven over directory and file `ClientContent` examples.

## Control flow
For each case the test calls `parseStat`, checks metadata deep equality, size, optional expiry, file/folder type classification, and ETag quote trimming.

## State and persistence
No external state. Uses synthetic `ClientContent` values and client URLs.

## Dependencies and integration points
Targets `parseStat` from `stat.go`; uses Go `testing`, `reflect`, `strings`, `os`, and `time`.

## Risks and edge cases
- `targetAlias` is part of the test case struct but is unused.
- Does not check version ID, delete marker, expiration rule, restore info, checksums, or replication status.

## Test signals
Useful focused regression coverage for the basic object metadata normalization path.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/status.go -->
# sources/object-store/minio-mc/cmd/status.go

## Purpose
Defines a common `Status` interface and two implementations for command progress/accounting: quiet accounting-only status and visible progress-bar status.

## Important APIs, types, and functions
- `Status` combines output, counts, byte progress, lifecycle, message printing, error/fatal helpers, and `io.Reader`.
- `NewQuietStatus` returns `QuietStatus` around an `accounter`.
- `QuietStatus` tracks counts atomically, wraps a hook reader plus accounter, suppresses live progress, and prints final stats.
- `NewProgressStatus` returns `ProgressStatus` around a progress bar.
- `ProgressStatus` tracks counts atomically, wraps a hook reader plus progress bar, renders live progress, and erases progress lines around errors.

## Control flow
Both implementations call `hook.Read(p)` and then read from their accounting/progress reader in `Read`, which lets commands tap the underlying data stream while counting bytes. Counts are updated via 64-bit atomic operations. Quiet status ignores live UI calls and prints messages normally; progress status suppresses per-message printing and updates the progress bar.

## State and persistence
In-memory counts and byte totals only. No persisted state.

## Dependencies and integration points
Uses local `accounter` and `progressBar` types, global `printMsg`, `errorIf`, `fatalIf`, console erase/print helpers, and `probe.Error`.

## Risks and edge cases
- `Read` ignores the return/error from `hook.Read`, which assumes the hook is side-effect-only and non-authoritative.
- `Total()` returns current bytes (`Get`) in both implementations, not the configured total, which may be intentional or surprising.
- Counts are first field in structs to satisfy 64-bit atomic alignment on 32-bit systems.

## Test signals
No direct tests. Tests should cover atomic counts, read accounting, quiet final stats, progress error rendering behavior, and `Total` semantics.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/subnet-file-uploader.go -->
# sources/object-store/minio-mc/cmd/subnet-file-uploader.go

## Purpose
Provides a multipart uploader for sending local diagnostic/profile/support files to MinIO SUBNET, with optional zstd compression, stream encryption, custom public keys, response credential extraction, and post-upload deletion.

## Important APIs, types, and functions
- `SubnetFileUploader` carries alias, file path/name, request URL, query params, headers, compression/encryption/delete flags, and optional public key.
- `UploadFileToSubnet` builds the upload request, sends it, optionally deletes the local file, and saves credentials returned by SUBNET.
- `updateParams` derives filename, appends `.zst` and/or `.enc`, records query params, and appends them to `ReqURL`.
- `subnetUploadReq` creates a streaming multipart POST request using `io.Pipe`.
- `bytesToPublicKey` decodes PEM if present and parses an RSA PKCS#1 public key.

## Control flow
Upload begins by calling `subnetUploadReq`, which updates URL params and starts a goroutine to stream the file into a multipart form. The goroutine opens the file, creates a form file part, optionally wraps it in an encrypted stream using `madmin/estream` and either the supplied public key or a default key, optionally wraps it in a zstd writer, then copies file bytes. The request is posted via `subnetReqDo`. On success it deletes the source file if requested and extracts/saves SUBNET credentials when an alias is configured.

## State and persistence
Reads local files, can delete the uploaded local file, mutates `SubnetFileUploader` fields (`filename`, `Params`, `ReqURL`, `AutoCompress`), and can persist API key/license config through `extractAndSaveSubnetCreds`.

## Dependencies and integration points
Uses SUBNET HTTP helper `subnetReqDo`, `SubnetHeaders`, `extractAndSaveSubnetCreds`, zstd compression, MinIO `estream` encryption, default public key from elsewhere in the package, and standard multipart streaming.

## Risks and edge cases
- `updateParams` appends query params to `ReqURL` each call; reusing the same uploader can duplicate params.
- `UploadFileToSubnet` ignores errors from `os.Remove` and from `extractAndSaveSubnetCreds`.
- Compression writer creation ignores its error (`z, _ := zstd.NewWriter`).
- Streaming errors are propagated through `CloseWithError`, but request creation succeeds before the file is opened.
- `bytesToPublicKey` only parses PKCS#1 RSA public keys, not PKIX public key blocks.

## Test signals
No direct tests in this subset. Tests should cover URL parameter mutation, compression/encryption filename suffixes, PEM/key parsing, streaming error propagation, delete-after-upload behavior, and credential-save error handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/subnet-file-uploader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/subnet-utils.go -->
# sources/object-store/minio-mc/cmd/subnet-utils.go

## Purpose
Provides shared SUBNET support utilities: URL builders, authentication headers, HTTP request helpers, debug redaction, MinIO server config lookup/mutation for SUBNET keys, mc config fallback, cluster registration metadata, login/MFA flows, credential exchange, license validation, upload URL preparation, and connectivity initialization.

## Important APIs, types, and functions
- URL helpers: `SubnetBaseURL`, `subnetIssueURL`, `SubnetUploadURL`, `SubnetRegisterURL`, unregister/license/login/API key/MFA URL builders.
- HTTP helpers: `checkURLReachable`, `subnetReqDo`, `subnetHeadReq`, `subnetGetReq`, `SubnetPostReq`, `subnetHTTPDo`, `dumpHTTPReq`.
- Auth helpers: `SubnetHeaders`, `addDeploymentIDHeader`, token/license/API-key header builders, `subnetURLWithAuth`.
- Config helpers: `getMinIOSubSysConfig`, `getMinIOSubnetConfig`, `getKeyFromSubnetConfig`, `getSubnetAPIKeyFromConfig`, `getSubnetLicenseFromConfig`, `setGlobalSubnetProxyFromConfig`, `mcConfig`, `setSubnetAPIKey`, `setSubnetLicense`, and lower-level config setters.
- Registration helpers: `GetClusterRegInfo`, `getDriveSpaceInfo`, `generateRegToken`, `registerClusterOnSubnet`, `unregisterClusterFromSubnet`, `removeSubnetAuthConfig`.
- Credential helpers: `subnetLogin`, `getSubnetCreds`, `getSubnetAPIKey`, API-key/license exchange functions, `extractAndSaveSubnetCreds`, `extractSubnetCred`, `parseLicense`, `validateAndSaveLic`.
- Command helpers: `prepareSubnetUploadURL`, `getAPIKeyFlag`, `initSubnetConnectivity`.

## Control flow
SUBNET commands typically call `initSubnetConnectivity`, which validates `--airgap`/`--api-key`, extracts alias, parses UUID API key, applies proxy config unless airgapped, and checks SUBNET base URL reachability when requested. Commands needing upload URLs call `prepareSubnetUploadURL`, which resolves an API key from flag/config/login if necessary and returns authenticated request URL/headers.

HTTP requests go through `subnetReqDo`, which adds headers, defaults content type to JSON, executes via a proxy-aware client, optionally dumps redacted debug HTTP, limits response body to 1 MiB, and treats only HTTP 200 as success.

Credential resolution first checks MinIO server `subnet` subsystem config when supported, otherwise falls back to local mc alias config. If only API key or license is present and not airgapped, it attempts to fetch and save the missing credential. Registration posts a base64-encoded cluster registration token to SUBNET and saves returned license/API key.

## State and persistence
State surfaces include:
- Global process state: `globalSubnetConfig` cache, `GlobalSubnetProxyURL`, `globalAirgapped`, `GlobalDevMode`, `globalDebug`.
- Remote MinIO server config: `subnet api_key`, `subnet license`, and proxy values via admin config APIs.
- Local mc config alias fields: API key and license fallback.
- Interactive terminal input for login/MFA.
No arbitrary files are written directly here; config mutations go through established config/admin APIs.

## Dependencies and integration points
Integrates with MinIO admin APIs (`GetConfigKV`, `SetConfigKV`, `HelpConfigKV`, admin info), SUBNET package base URL and license validator, `madmin.InfoMessage`, `gjson`, `uuid`, terminal password input, HTTP client/proxy helpers, local config loading/saving, and support/license commands.

## Risks and edge cases
- `subnetReqDo` accepts only status 200; APIs returning 201/204 would be treated as failures.
- Debug dumping redacts sensitive headers but uses `query.Add` instead of replacing existing query secrets, which can leave original query values in the dump.
- `extractSubnetCred` treats `result.Index == 0` as missing; a top-level field at byte index 0 could be misdetected depending on gjson behavior, though object fields usually have nonzero indexes.
- `GetClusterRegInfo` indexes `admInfo.Servers[0]` and assumes at least one server.
- `getSubnetCreds` can perform network calls and config writes as a side effect of a credential read.
- `removeSubnetAuthConfig` always writes server config, not local fallback, which may not clear locally stored credentials on older/non-supporting targets.

## Test signals
`subnet-utils_test.go` checks that `SubnetBaseURL` parses as an HTTPS URL. More tests are needed for URL construction, HTTP status handling, redaction, credential extraction, config fallback, registration token generation, and airgap/proxy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/subnet-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/subnet-utils_test.go -->
# sources/object-store/minio-mc/cmd/subnet-utils_test.go

## Purpose
Tests the basic shape of the SUBNET base URL.

## Important APIs, types, and functions
- `TestSubnetBaseURL` calls `SubnetBaseURL`, parses it as a request URI, and asserts the scheme is `https`.

## Control flow
The test obtains the base URL, parses it, fails on parse error, and checks `u.Scheme`.

## State and persistence
No state. It depends on current global dev-mode behavior only through `SubnetBaseURL`.

## Dependencies and integration points
Targets `SubnetBaseURL` from `subnet-utils.go`; uses standard `net/url` and `testing`.

## Risks and edge cases
- It does not assert host, path, dev-mode behavior, or any derived SUBNET endpoint builders.
- If `GlobalDevMode` intentionally returns non-HTTPS in some test mode, this test would fail.

## Test signals
Narrow regression guard ensuring production/default SUBNET base URL is HTTPS and syntactically valid.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/subnet-utils_test.go -->
