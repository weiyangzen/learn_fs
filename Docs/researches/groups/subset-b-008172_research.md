# subset-b-008172 Research

Grouped source research for MinIO Client command files under `sources/object-store/minio-mc/cmd`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-restart.go -->
# sources/object-store/minio-mc/cmd/admin-service-restart.go

## Purpose

`admin-service-restart.go` implements `mc admin service restart`, including dry-run support, optional post-restart readiness waiting, JSON output, and an interactive Bubble Tea status UI. It is the main restart path for MinIO clusters from `mc`.

## Important APIs, Types, and Functions

The command is declared as `adminServiceRestartCmd` with `--dry-run` and `--wait` flags. `serviceRestartUI` is a Bubble Tea model driven by a `spinner.Model` and an `atomic.Value`. `serviceRestartMessage` serializes restart result state, durations, server URL, and `madmin.ServiceActionResult`. Key functions are `checkAdminServiceRestartSyntax`, `initServiceRestartUI`, and `mainAdminServiceRestart`.

## Control Flow

The handler validates exactly one target alias, creates an admin client, starts a goroutine that calls `client.ServiceAction` with `madmin.ServiceActionRestart`, and falls back to the older `ServiceRestart` API if needed. It sends a restart message immediately, then, when `--wait` is set, creates an anonymous admin client and polls `Healthy` every 500 ms under a 2-second health timeout until the cluster reports healthy. Non-JSON mode runs a Bubble Tea UI; JSON mode drains messages until state `done`.

## State and Persistence Behavior

The file does not persist client-side state. Cluster state is changed through admin service APIs. Local runtime state is held in channels, contexts, durations, and the UI model. JSON output includes a deprecated `timeTaken` field for compatibility.

## Dependencies and Integration Points

It integrates `madmin-go` service actions, the local `newAdminClient` and `newAnonymousClient` helpers, `globalContext`, console color configuration, `printMsg`, `fatalIf`, Bubble Tea, Bubbles spinner, Lip Gloss, and color JSON encoding.

## Risks and Edge Cases

The health-wait goroutine has no max timeout and depends on the process context or user cancellation. The fallback to the legacy API intentionally hides version differences. In non-JSON mode, UI completion is driven by the `quitting` flag from `View`, so terminal rendering paths are part of command completion. Dry-run still reports restart-style messages.

## Test Signals

Useful tests would cover syntax arity, new API success, legacy fallback, dry-run option propagation, JSON sequence in wait mode, no-wait immediate completion, cancellation on UI errors, and health polling transitions from failing to healthy.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-restart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-stop.go -->
# sources/object-store/minio-mc/cmd/admin-service-stop.go

## Purpose

`admin-service-stop.go` implements the hidden `mc admin service stop` command that stops a MinIO cluster through the admin API.

## Important APIs, Types, and Functions

`adminServiceStopCmd` is a hidden `cli.Command` wired to `mainAdminServiceStop`. `serviceStopMessage` supplies plain text and JSON output. `checkAdminServiceStopSyntax` accepts one or two arguments, though the handler uses only the first target.

## Control Flow

The handler validates arguments, configures success color, extracts the target alias, builds an admin client, calls `client.ServiceStopV2(globalContext)`, and prints a success message.

## State and Persistence Behavior

There is no local persistence. The command mutates remote cluster process state by sending a stop request. Output state is limited to the target URL and status string.

## Dependencies and Integration Points

The file depends on `newAdminClient`, `madmin.AdminClient.ServiceStopV2`, `fatalIf`, `printMsg`, global flags, color JSON, and console colorization. It is registered by `admin-service.go`.

## Risks and Edge Cases

The command is intentionally hidden because stopping a cluster is disruptive. The syntax checker allows a second argument that is ignored, which can hide accidental extra input. There is no fallback to an older stop API in this file.

## Test Signals

Tests should assert hidden command registration, syntax behavior for zero and three arguments, success message encoding, and that `ServiceStopV2` is invoked exactly once for the resolved alias.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-unfreeze.go -->
# sources/object-store/minio-mc/cmd/admin-service-unfreeze.go

## Purpose

`admin-service-unfreeze.go` implements `mc admin service unfreeze`, which resumes S3 API calls on a MinIO cluster after a freeze operation.

## Important APIs, Types, and Functions

`adminServiceUnfreezeCmd` defines the CLI command. `serviceUnfreezeCommand` is the output message type. `checkAdminServiceUnfreezeSyntax` enforces one target, and `mainAdminServiceUnfreeze` performs the admin operation.

## Control Flow

The command validates the target, builds an admin client, creates a cancellable context, calls `ServiceUnfreezeV2`, falls back to deprecated `ServiceUnfreeze` on error, converts the final error through `probe`, and prints a success message.

## State and Persistence Behavior

No local files are written. Remote server state is changed by unfreezing service calls. The only runtime state is the cancellable context and message payload.

## Dependencies and Integration Points

It depends on `newAdminClient`, `madmin-go` unfreeze APIs, `globalContext`, command registration in `admin-service.go`, and shared console/message helpers.

## Risks and Edge Cases

The fallback is unconditional on any V2 error, so non-version failures may trigger a second request. Correctness depends on server-side idempotence for unfreeze. There is no wait/verification path after sending the command.

## Test Signals

Tests should exercise exact arity, V2 success, V2 failure with legacy fallback, final error reporting, and text/JSON output content.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-unfreeze.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service.go -->
# sources/object-store/minio-mc/cmd/admin-service.go

## Purpose

`admin-service.go` is the command group definition for `mc admin service`. It wires service lifecycle subcommands into the admin command tree.

## Important APIs, Types, and Functions

`adminServiceSubcommands` contains restart, stop, unfreeze, and freeze commands. `adminServiceCmd` is a `cli.Command` with global flags and no help subcommand. `mainAdminService` delegates unknown command handling to `commandNotFound`.

## Control Flow

The top-level command does not perform service operations itself. The CLI dispatcher invokes a subcommand when present; otherwise `mainAdminService` reports valid subcommands.

## State and Persistence Behavior

This file owns only static command registration state and has no persistence.

## Dependencies and Integration Points

It depends on sibling command variables, `setGlobalsFromContext`, `globalFlags`, and `commandNotFound`. It integrates with the root admin command tree elsewhere in the package.

## Risks and Edge Cases

Registration order affects help display and command discovery. Hidden subcommands such as stop still exist in the slice and may be reachable by name.

## Test Signals

Command-tree tests should confirm that visible subcommands are registered, hidden subcommands remain hidden where expected, and bare `mc admin service` reports command-not-found help rather than performing an action.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-subnet-health.go -->
# sources/object-store/minio-mc/cmd/admin-subnet-health.go

## Purpose

`admin-subnet-health.go` preserves the hidden deprecated `mc admin subnet health` command and redirects users toward `mc support diag`.

## Important APIs, Types, and Functions

`adminSubnetHealthCmd` is a hidden `cli.Command` using `supportDiagFlags`. `mainSubnetHealth` builds a replacement command string. It uses `set.CreateStringSet` to detect boolean flag values.

## Control Flow

The handler starts with `mc support diag`, appends original positional args, then iterates command flags that were set. It maps deprecated `--offline` to `--airgap`, quotes non-boolean flag values, and calls `deprecatedError` with the new command.

## State and Persistence Behavior

There is no state mutation or persistence. The command exists only for compatibility messaging.

## Dependencies and Integration Points

It integrates with support diagnostic flags, `deprecatedError`, MinIO set utilities, and the hidden subnet group.

## Risks and Edge Cases

The generated replacement command is a display string, not shell-escaped robustly for every possible value. Boolean detection uses string values `"true"` and `"false"`, so unusual flag renderings could be quoted differently.

## Test Signals

Tests should verify hidden registration, `offline` to `airgap` translation, omission of unset flags, quoting of string values, and the final replacement string for common diagnostic options.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-subnet-health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-subnet-register.go -->
# sources/object-store/minio-mc/cmd/admin-subnet-register.go

## Purpose

`admin-subnet-register.go` preserves the hidden deprecated `mc admin subnet register` command and points users to `mc support register`.

## Important APIs, Types, and Functions

`adminSubnetRegisterCmd` defines the hidden command. `mainAdminRegister` calls `deprecatedError("mc support register")`.

## Control Flow

The CLI invokes the handler for the deprecated command; the handler emits the replacement-command error and returns.

## State and Persistence Behavior

No local or remote state is changed.

## Dependencies and Integration Points

It depends on `deprecatedError`, `setGlobalsFromContext`, and registration in `admin-subnet.go`.

## Risks and Edge Cases

Because the command is hidden but still registered, automation using the old command will receive a deprecation failure rather than silently performing registration.

## Test Signals

Tests should confirm hidden status, replacement message content, and that no admin/support API client is created.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-subnet-register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-subnet.go -->
# sources/object-store/minio-mc/cmd/admin-subnet.go

## Purpose

`admin-subnet.go` defines the hidden deprecated `mc admin subnet` group and bridges old SUBNET commands to the newer `mc support` namespace.

## Important APIs, Types, and Functions

`subnetHealthSubcommands` contains hidden health and register commands. `adminSubnetCmd` is the hidden top-level command. `mainAdminSubnet` reports deprecation to `mc support`. `adminHealthCmd` returns a hidden copy of the health command.

## Control Flow

The top-level command never performs health or registration itself. It delegates to subcommands when matched; otherwise it reports the deprecation target.

## State and Persistence Behavior

Only static command-tree state is defined.

## Dependencies and Integration Points

It integrates with the admin command tree, support diagnostics/register migration, `globalFlags`, and the command deprecation helper.

## Risks and Edge Cases

The copied command returned by `adminHealthCmd` can diverge if future code mutates fields after copy. Hidden command behavior must stay aligned with support command replacements.

## Test Signals

Useful tests verify hidden group and subcommands, bare group deprecation, and that `adminHealthCmd` returns a hidden command even if the base command changes.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-subnet.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-tier-deprecated.go -->
# sources/object-store/minio-mc/cmd/admin-tier-deprecated.go

## Purpose

`admin-tier-deprecated.go` declares the hidden legacy `mc admin tier` subcommands for remote tier targets. The actual handlers are shared with newer ILM tier functionality, while this file keeps old help text and compatibility wiring.

## Important APIs, Types, and Functions

`adminTierDepCmds` includes `info`, `ls`, `add`, `edit`, `verify`, and `rm`. Each command is hidden, uses `setGlobalsFromContext`, and points to handlers such as `mainAdminTierInfo`, `mainAdminTierAdd`, and `mainAdminTierRm`. Add/edit append specialized tier flags from sibling ILM tier code.

## Control Flow

There is no executable business logic beyond command dispatch metadata. If a hidden legacy subcommand is invoked, the CLI dispatcher calls the shared handler. Bare `mc admin tier` is handled by `admin-tier-main.go`.

## State and Persistence Behavior

The file defines static CLI metadata only. Remote tier configuration persistence is performed by shared handler functions declared elsewhere.

## Dependencies and Integration Points

It integrates legacy admin-tier names with the ILM tier implementation, global flags, custom help templates, and handler functions from other files.

## Risks and Edge Cases

The hidden commands can continue to modify tier state through shared handlers despite the top-level namespace being deprecated. Help examples must stay consistent with actual flag names. Add/edit flag slices are shared dependencies and can affect this legacy namespace.

## Test Signals

Command-tree tests should verify hidden status, correct handler binding for each legacy subcommand, expected flag composition for add/edit, and no accidental visibility in normal help.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-tier-deprecated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-tier-main.go -->
# sources/object-store/minio-mc/cmd/admin-tier-main.go

## Purpose

`admin-tier-main.go` defines the hidden deprecated `mc admin tier` command group and redirects users to `mc ilm tier`.

## Important APIs, Types, and Functions

`adminTierCmd` is a hidden `cli.Command` with `adminTierDepCmds` as subcommands. `mainAdminTier` emits the deprecation target.

## Control Flow

The top-level action runs only for a bare or invalid group invocation. Subcommands dispatch through the hidden command definitions in `admin-tier-deprecated.go`.

## State and Persistence Behavior

Only static command registration is present.

## Dependencies and Integration Points

The file depends on legacy subcommand metadata, `deprecatedError`, `globalFlags`, and admin command registration.

## Risks and Edge Cases

Because subcommands are still registered, legacy automation may still reach hidden tier handlers. Any migration policy must consider both the top-level deprecation and hidden subcommand execution.

## Test Signals

Tests should assert hidden group status, replacement text, and correct subcommand attachment.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-tier-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-top-api.go -->
# sources/object-store/minio-mc/cmd/admin-top-api.go

## Purpose

`admin-top-api.go` preserves the hidden deprecated `mc admin top api` command and redirects users to `mc support top api`.

## Important APIs, Types, and Functions

`adminTopAPIFlags` defines legacy filters for API name, path, node, and errors. `adminTopAPICmd` is hidden and bound to `mainAdminTopAPI`, which calls `deprecatedError`.

## Control Flow

The command does not contact the server. When invoked, it emits a deprecation error with the support command replacement.

## State and Persistence Behavior

No local or remote state is changed.

## Dependencies and Integration Points

The file integrates with `admin-top.go`, global flags, CLI usage handling, and the support namespace migration.

## Risks and Edge Cases

Legacy flags remain declared even though the handler only reports deprecation. Scripts relying on the old command must migrate to support top.

## Test Signals

Tests should confirm hidden status, flag names retained for parsing, and replacement message content.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-top-api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-top-locks.go -->
# sources/object-store/minio-mc/cmd/admin-top-locks.go

## Purpose

`admin-top-locks.go` defines the legacy `mc admin top locks` command and redirects users to `mc support top locks`.

## Important APIs, Types, and Functions

`topLocksFlag` declares `--stale` and hidden `--count`. `adminTopLocksCmd` is wired to `mainAdminTopLocks`, which emits the deprecation message.

## Control Flow

The CLI parses the command and flags, then the handler immediately calls `deprecatedError("mc support top locks")`.

## State and Persistence Behavior

No state is read or written by this file.

## Dependencies and Integration Points

It is registered by `admin-top.go` and shares global flags plus usage-error behavior.

## Risks and Edge Cases

Unlike `admin top api`, this command is not marked hidden in the command declaration in this file, so visibility depends on parent grouping and current CLI help behavior. The retained hidden `count` flag has no effect after deprecation.

## Test Signals

Tests should check command visibility expectations, flag parsing, and deprecation target.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-top-locks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-top.go -->
# sources/object-store/minio-mc/cmd/admin-top.go

## Purpose

`admin-top.go` groups `mc admin top` subcommands that provide top-like MinIO statistics, with current subcommands redirected to support equivalents.

## Important APIs, Types, and Functions

`adminTopSubcommands` contains API and locks commands. `adminTopCmd` defines the group. `mainAdminTop` calls `commandNotFound`.

## Control Flow

The group action is only used for invalid or missing subcommands. Real behavior is delegated to `adminTopAPICmd` or `adminTopLocksCmd`.

## State and Persistence Behavior

Only static command metadata is defined.

## Dependencies and Integration Points

It integrates with the admin command tree, top API/locks subcommands, global flags, and command-not-found handling.

## Risks and Edge Cases

Subcommand deprecations must remain synchronized with support command implementations. Parent command help can expose or hide deprecated children depending on their own visibility flags.

## Test Signals

Tests should verify subcommand list composition and bare group behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-top.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-trace.go -->
# sources/object-store/minio-mc/cmd/admin-trace.go

## Purpose

`admin-trace.go` implements `mc admin trace`, a live and replayable trace viewer for MinIO service events. It supports trace-type selection, path/method/status/node/header/query/size/duration filters, concise and verbose output, JSON output, and statistical aggregation.

## Important APIs, Types, and Functions

`adminTraceFlags` declares the CLI filter and replay flags. `traceCallTypes` and `traceCallTypeAliases` map user call names into `madmin.ServiceTraceOpts`. `matchOpts.matches` applies local filtering. `tracingOpts` builds server-side trace options. `mainAdminTrace` orchestrates live service tracing or `--in` replay. Output types include `shortTraceMsg`, `traceMessage`, `requestInfo`, `responseInfo`, `callStats`, `verboseTrace`, `statItem`, and `statTrace`.

## Control Flow

The handler validates arity and incompatible flags, configures colors, creates a cancellable context, then chooses input mode. In replay mode it reads newline-delimited JSON, optionally through zstd, decodes short trace records, skips bootstrap records, and sends reconstructed `ServiceTraceInfo` values through a buffered channel. In live mode it creates an admin client, builds trace options, and consumes `client.ServiceTrace`. If `--stats` or replay is active, traces are filtered and sent to a Bubble Tea stats UI. Otherwise each matching trace is printed as verbose or short output.

## State and Persistence Behavior

Live mode does not persist trace data. Replay mode reads a saved JSON or `.zst` file but does not write it. Runtime aggregation is held in `statTrace` with a mutex, tracking per-function counts, durations, errors, byte totals, TTFB, and time bounds.

## Dependencies and Integration Points

The file is tightly integrated with `madmin-go` trace types, `newAdminClient`, `globalContext`, MinIO path/name/pattern matching helpers, `humanize.ParseBytes`, `zstd`, Bubble Tea stats UI hooks, color JSON, and shared message printing. It depends on server-side trace option support for selected call families.

## Risks and Edge Cases

`shortTrace` assumes HTTP details exist for S3/internal traces; malformed server data could panic. Replay reconstruction loses HTTP request/response details and uses an unexported `trcType` field that cannot be recovered from JSON, so stats from saved short JSON are less complete. Header and query filters support negation with `!`, but matching semantics are local and pattern-based. The replay goroutine closes the channel then blocks forever with `select {}`, relying on process exit. Verbose string rendering mutates request headers by deleting `Host`.

## Test Signals

Good tests should cover syntax validation, `--all` versus `--call`, trace call alias mapping, size parsing, positive and negated header/query filters, path/name matching, JSON encoding with HTML escaping disabled, non-HTTP trace formatting, stats aggregation, and replay of plain and zstd trace files.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-trace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-update.go -->
# sources/object-store/minio-mc/cmd/admin-update.go

## Purpose

`admin-update.go` implements `mc admin update`, which asks a MinIO cluster to update all servers, optionally using a supplied update URL.

## Important APIs, Types, and Functions

`adminUpdateFlags` defines `--yes/-y`. `adminServerUpdateCmd` wires the command. `serverUpdateMessage` wraps `madmin.ServerUpdateStatusV2` and renders host-level results in a table. `mainAdminServerUpdate` performs confirmation and calls `ServerUpdateV2`.

## Control Flow

The handler validates one or two args, builds an admin client, reads the optional update URL from arg 2, prompts for confirmation on terminals unless `--yes` is set, and aborts on non-yes answers. It then calls `client.ServerUpdateV2` with `DryRun` and `UpdateURL`, and prints the formatted update result.

## State and Persistence Behavior

No local state is persisted. The command triggers remote update state and renders per-peer statuses, including upgraded versions, errors, and waiting drives.

## Dependencies and Integration Points

It uses `newAdminClient`, `madmin.ServerUpdateOpts`, terminal input, console/table formatting, `fatalIf`, and global flags. It references `ctx.Bool("dry-run")` even though this file only declares `--yes`, so it depends on a global or shared dry-run flag if present.

## Risks and Edge Cases

Cluster update is disruptive, so terminal confirmation is important. Non-terminal runs without `--yes` proceed without prompting. Missing or absent dry-run flag registration would make `ctx.Bool("dry-run")` inert. Waiting drives are reported as upgraded but needing OS reboot.

## Test Signals

Tests should cover arity, confirmation yes/no handling, non-terminal behavior, update URL propagation, message rendering for success/error/waiting drives, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-add.go -->
# sources/object-store/minio-mc/cmd/admin-user-add.go

## Purpose

`admin-user-add.go` implements `mc admin user add` and defines shared user output types used by other user subcommands.

## Important APIs, Types, and Functions

`adminUserAddCmd` defines the command. `userGroup` and `userMessage` model user display and JSON output across add/list/info/remove/enable/disable. `fetchUserKeys` obtains credentials from args, terminal prompts, hidden password input, or piped stdin. `mainAdminUserAdd` calls `AddUser`.

## Control Flow

The handler accepts target plus optional access and secret keys. If keys are missing, `fetchUserKeys` prompts or reads stdin based on terminal detection. The handler creates an admin client, calls `client.AddUser(globalContext, accessKey, secretKey)`, and prints an enabled user message.

## State and Persistence Behavior

Local state is not persisted. Remote IAM user state is created on the MinIO server. In JSON mode the `SecretKey` field may be emitted, so output handling is sensitive.

## Dependencies and Integration Points

It depends on `madmin` through the admin client, terminal password reading from `x/term`, shared console helpers, and user message rendering used by sibling user files.

## Risks and Edge Cases

Credentials passed as command-line args can leak into shell history; the help warns about this. `fetchUserKeys` ignores read errors from `ReadLine` and `ReadPassword`. JSON output includes secrets after add.

## Test Signals

Tests should cover one-, two-, and three-argument credential input, terminal and piped stdin paths, invalid arity, `AddUser` arguments, and text/JSON rendering for user messages.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-disable.go -->
# sources/object-store/minio-mc/cmd/admin-user-disable.go

## Purpose

`admin-user-disable.go` implements `mc admin user disable`, changing a MinIO user account status to disabled.

## Important APIs, Types, and Functions

`adminUserDisableCmd` declares the command. `checkAdminUserDisableSyntax` enforces target and username. `mainAdminUserDisable` calls `SetUserStatus` with `madmin.AccountDisabled`.

## Control Flow

The handler validates two args, creates an admin client for the target, sends the status update for the username, and prints a `userMessage` with operation `disable`.

## State and Persistence Behavior

Remote IAM account status is persisted by the server. The client writes no local files.

## Dependencies and Integration Points

It uses the shared `userMessage` type from `admin-user-add.go`, `newAdminClient`, `madmin-go`, `fatalIf`, and global flags.

## Risks and Edge Cases

The command has no confirmation, so accidental disables take effect immediately. It does not inspect the previous status.

## Test Signals

Tests should verify arity, status value `AccountDisabled`, error propagation, and output message content.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-enable.go -->
# sources/object-store/minio-mc/cmd/admin-user-enable.go

## Purpose

`admin-user-enable.go` implements `mc admin user enable`, changing a MinIO user account status to enabled.

## Important APIs, Types, and Functions

`adminUserEnableCmd` declares the command. `checkAdminUserEnableSyntax` enforces target and username. `mainAdminUserEnable` calls `SetUserStatus` with `madmin.AccountEnabled`.

## Control Flow

The handler validates two args, creates an admin client, updates the user status, and prints a shared user success message.

## State and Persistence Behavior

The server persists the enabled account status. No local files are touched.

## Dependencies and Integration Points

It integrates with the admin user command group, shared `userMessage`, `madmin-go`, and common error/output helpers.

## Risks and Edge Cases

There is no prior-state check or confirmation. Enabling an externally managed account may depend on server-side IAM behavior.

## Test Signals

Tests should assert syntax, `AccountEnabled` propagation, and output for successful enablement.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-info.go -->
# sources/object-store/minio-mc/cmd/admin-user-info.go

## Purpose

`admin-user-info.go` implements `mc admin user info`, displaying a user's status, policies, group membership, and authentication source.

## Important APIs, Types, and Functions

`adminUserInfoCmd` defines the command. `mainAdminUserInfo` calls `GetUserInfo` and then `GetGroupDescription` for each group. `authInfoToUserMessage` formats `madmin.UserAuthInfo`.

## Control Flow

The handler validates target and username, creates an admin client, fetches user info, expands each group into a `userGroup` with policy list, converts authentication info, and prints a `userMessage` with operation `info`.

## State and Persistence Behavior

The command reads remote IAM state only. No local persistence occurs.

## Dependencies and Integration Points

It depends on `madmin.UserInfo`, group description APIs, shared user output formatting, console coloring, and global context.

## Risks and Edge Cases

Group expansion requires additional admin API calls; a failure fetching any group fails the whole user-info command. Group policy names are split on commas without trimming.

## Test Signals

Tests should cover users with no groups, multiple groups and policies, builtin and external auth info, group API failures, and JSON output structure.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-list.go -->
# sources/object-store/minio-mc/cmd/admin-user-list.go

## Purpose

`admin-user-list.go` implements `mc admin user list` / `ls`, printing all users and their statuses, policies, and group memberships.

## Important APIs, Types, and Functions

`adminUserListCmd` declares the command and short name. `mainAdminUserList` calls `ListUsers` and emits a `userMessage` for each returned user. `checkAdminUserListSyntax` enforces one target.

## Control Flow

The handler configures colors, creates an admin client, fetches all users, iterates the returned map, expands each user's groups through `GetGroupDescription`, and prints per-user rows/messages.

## State and Persistence Behavior

Remote IAM state is read only. Local state is transient table/message construction.

## Dependencies and Integration Points

It uses shared user message formatting, `madmin` user/group APIs, colorized table fields, `globalContext`, and command group registration.

## Risks and Edge Cases

Map iteration order is not sorted, so output order can be nondeterministic. Fetching group descriptions per user may be expensive and can fail the whole listing.

## Test Signals

Tests should verify arity, empty user set, group policy expansion, JSON rows, and whether output ordering needs stabilization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-policy.go -->
# sources/object-store/minio-mc/cmd/admin-user-policy.go

## Purpose

`admin-user-policy.go` implements `mc admin user policy`, exporting the effective policy document attached directly to a user.

## Important APIs, Types, and Functions

`adminUserPolicyCmd` defines the command. `mainAdminUserPolicy` calls `GetUserInfo`, fetches each named policy with `getPolicyInfo`, unmarshals to `policy.Policy`, merges policies with `policy.MergePolicies`, and writes JSON to stdout.

## Control Flow

The handler validates target and username, fetches user info, fails when no policy name is set, splits comma-separated policy names, fetches each policy document, parses it, merges all non-empty names, and encodes the merged policy directly to `os.Stdout`.

## State and Persistence Behavior

The command reads remote IAM policies and writes only stdout. It does not use the normal `printMsg` JSON wrapper for the final policy document.

## Dependencies and Integration Points

It depends on admin client policy helpers from elsewhere in the package, `github.com/minio/pkg/v3/policy`, color JSON decoding, and standard output.

## Risks and Edge Cases

Group-derived policies are not included here unless present in `user.PolicyName`. Comma splitting does not trim whitespace. Direct stdout encoding bypasses the usual status envelope and color handling.

## Test Signals

Tests should cover missing policy, multiple policy merge semantics, malformed policy JSON, empty names in comma-separated strings, and exact stdout JSON.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-remove.go -->
# sources/object-store/minio-mc/cmd/admin-user-remove.go

## Purpose

`admin-user-remove.go` implements `mc admin user remove` / `rm`, deleting a user from MinIO IAM.

## Important APIs, Types, and Functions

`adminUserRemoveCmd` declares the command and short name. `checkAdminUserRemoveSyntax` enforces target and username. `mainAdminUserRemove` calls `RemoveUser`.

## Control Flow

The handler validates two args, creates an admin client, sends the remove request for the username, and prints a shared `userMessage`.

## State and Persistence Behavior

Remote IAM user state is deleted by the server. No local state is persisted.

## Dependencies and Integration Points

It uses `newAdminClient`, `madmin.AdminClient.RemoveUser`, shared user output, global context, and error helpers.

## Risks and Edge Cases

The command has no confirmation and no dependency check for policies or service accounts; server-side validation determines deletion behavior.

## Test Signals

Tests should assert exact arity, target/user propagation, error path, and remove message rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-sts-info.go -->
# sources/object-store/minio-mc/cmd/admin-user-sts-info.go

## Purpose

`admin-user-sts-info.go` defines `mc admin user sts` and implements `mc admin user sts info` for temporary STS account inspection.

## Important APIs, Types, and Functions

`adminUserSTSAcctCmd` groups STS subcommands. `adminUserSTSAcctInfoCmd` supports `--policy`. `mainAdminUserSTSAcctInfo` calls `TemporaryAccountInfo` and reuses `acctMessage` output from service-account code.

## Control Flow

The group command delegates unknown subcommands. The info handler validates target and STS account, fetches account info, optionally parses and pretty-prints the embedded policy to stdout, otherwise prints an `acctMessage` with status, parent user, implied policy flag, policy raw JSON, and expiration.

## State and Persistence Behavior

The command reads temporary account state and writes stdout only. It does not mutate IAM state.

## Dependencies and Integration Points

It integrates with `madmin` temporary account APIs, shared service-account message types, MinIO policy parsing, and the admin user command group.

## Risks and Edge Cases

The error message refers to service accounts even though the command is for STS accounts. `--policy` fails if no embedded policy exists, even if parent policy applies. Raw policy is passed as `json.RawMessage`.

## Test Signals

Tests should cover no-policy and embedded-policy accounts, parse errors, implied policy output, expiration formatting, and group command-not-found behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-sts-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-add.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-add.go

## Purpose

`admin-user-svcacct-add.go` implements `mc admin user svcacct add` and defines shared service-account output, credential generation, operation constants, and time parsing used by multiple service-account commands.

## Important APIs, Types, and Functions

`adminUserSvcAcctAddFlags` includes access key, secret key, policy, name, description/comment, and expiry. `acctMessage` formats service and STS account records. `acctOp` constants drive output behavior. `supportedTimeFormats` defines accepted expiry formats. `generateCredentials` creates random access and secret keys. `mainAdminUserSvcAcctAdd` calls `AddServiceAccount`.

## Control Flow

The handler validates target and parent account, reads flags, maps deprecated `--comment` into description, generates missing credentials, creates an admin client, validates optional policy JSON with `policy.ParseConfig` and rejects empty policies, parses optional expiry in local time using known formats, calls `client.AddServiceAccount`, and prints generated credentials and expiration.

## State and Persistence Behavior

The server persists the new service account and optional embedded policy/expiration. Local state is limited to random credential material and output. JSON output can include generated secret keys.

## Dependencies and Integration Points

It depends on crypto randomness, base64, MinIO policy parsing, `madmin.AddServiceAccountReq`, shared console output, and sibling service-account commands that reuse `acctMessage`, constants, and `supportedTimeFormats`.

## Risks and Edge Cases

Generated secrets replace `/` with `+` after base64 truncation. Expiry parsing uses the local timezone, which can produce environment-dependent results. Empty policy documents are rejected client-side. Secrets are printed on success and must be handled carefully by callers.

## Test Signals

Tests should cover random credential length/charset, partial credential generation, policy parse and empty-policy rejection, expiry formats and invalid expiry, deprecated comment handling, and output redaction expectations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-disable.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-disable.go

## Purpose

`admin-user-svcacct-disable.go` implements `mc admin user svcacct disable`, turning a service account off.

## Important APIs, Types, and Functions

`adminUserSvcAcctDisableCmd` declares the command. `mainAdminUserSvcAcctDisable` sends `madmin.UpdateServiceAccountReq{NewStatus: "off"}`.

## Control Flow

The handler validates target and service account, creates an admin client, calls `UpdateServiceAccount`, and prints an `acctMessage` with disable operation.

## State and Persistence Behavior

The server persists the disabled status. No local files are changed.

## Dependencies and Integration Points

It uses shared service-account output from `admin-user-svcacct-add.go`, `madmin-go`, global context, and the service-account command group.

## Risks and Edge Cases

Status strings `"off"` and `"on"` are literal client-server contract values. There is no prior-state check or confirmation.

## Test Signals

Tests should assert arity, update payload, error propagation, and output message.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-enable.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-enable.go

## Purpose

`admin-user-svcacct-enable.go` implements `mc admin user svcacct enable`, turning a service account on.

## Important APIs, Types, and Functions

`adminUserSvcAcctEnableCmd` declares the command. `mainAdminUserSvcAcctEnable` sends `madmin.UpdateServiceAccountReq{NewStatus: "on"}`.

## Control Flow

The handler validates two args, creates an admin client, updates account status, and prints a service-account success message.

## State and Persistence Behavior

Remote IAM service-account status is persisted by the server. The command writes no local state.

## Dependencies and Integration Points

It depends on `madmin.UpdateServiceAccount`, shared `acctMessage`, console coloring, and global context.

## Risks and Edge Cases

There is no validation of account type beyond server response. Status string values are not typed constants in this file.

## Test Signals

Tests should cover status payload `"on"`, syntax failures, and message rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-info.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-info.go

## Purpose

`admin-user-svcacct-info.go` implements `mc admin user svcacct info`, showing service-account metadata and optionally its embedded policy.

## Important APIs, Types, and Functions

`adminUserSvcAcctInfoFlags` defines `--policy`. `mainAdminUserSvcAcctInfo` calls `InfoServiceAccount`, parses optional policy with `policy.ParseConfig`, and prints `acctMessage`.

## Control Flow

The handler validates target and service account, fetches account info, and branches on `--policy`. Policy mode requires a non-empty embedded policy and writes indented JSON to stdout. Normal mode prints access key, friendly name, description, status, parent user, implied policy flag, raw policy, and expiration.

## State and Persistence Behavior

The command reads remote service-account state only.

## Dependencies and Integration Points

It integrates with `madmin` service-account APIs, shared `acctMessage`, policy parsing, color JSON, and standard output.

## Risks and Edge Cases

`--policy` fails when the account relies on parent policy. Raw policy JSON is included in message output, so invalid server-side policy JSON could affect JSON encoding.

## Test Signals

Tests should cover policy/no-policy paths, parse errors, implied policy rendering, nil expiration, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-list.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-list.go

## Purpose

`admin-user-svcacct-list.go` implements `mc admin user svcacct list` / `ls`, listing service accounts for a target MinIO or LDAP account.

## Important APIs, Types, and Functions

`adminUserSvcAcctListCmd` declares the command. `mainAdminUserSvcAcctList` calls `ListServiceAccounts`, prints a table header in non-JSON mode, normalizes sentinel expiration values, and emits `acctMessage` rows.

## Control Flow

The handler validates target and parent account, creates an admin client, fetches the account list, prints a header if entries exist and output is not JSON, iterates accounts, converts `timeSentinel` expiration to nil, and prints each row. Empty non-JSON output prints "No service accounts found".

## State and Persistence Behavior

The command reads remote IAM state only.

## Dependencies and Integration Points

It uses shared `acctMessage`, `timeSentinel` from elsewhere in the package, `madmin.ListServiceAccounts`, and console table helpers.

## Risks and Edge Cases

The command requires a parent account and cannot list all service accounts globally. Empty results produce no JSON message. The typo "services accounts" is present in usage text.

## Test Signals

Tests should verify empty output behavior, header suppression in JSON mode, sentinel expiration handling, and row formatting.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-remove.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-remove.go

## Purpose

`admin-user-svcacct-remove.go` implements `mc admin user svcacct remove` / `rm`, deleting a service account.

## Important APIs, Types, and Functions

`adminUserSvcAcctRemoveCmd` declares the command. `mainAdminUserSvcAcctRemove` calls `DeleteServiceAccount` and prints `acctMessage` with remove operation.

## Control Flow

The handler configures color, validates target and service-account access key, creates an admin client, sends the delete request, and prints success.

## State and Persistence Behavior

Remote service-account state is removed by the server. There is no local persistence.

## Dependencies and Integration Points

It depends on `newAdminClient`, `madmin.DeleteServiceAccount`, shared account output, global context, and the service-account command group.

## Risks and Edge Cases

There is no confirmation before deletion. Server-side behavior determines whether deleting an already removed or parent-owned account succeeds.

## Test Signals

Tests should cover arity, delete API call, failure message, and output operation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-set.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct-set.go

## Purpose

`admin-user-svcacct-set.go` implements `mc admin user svcacct edit` and alias `set`, updating mutable fields on a service account.

## Important APIs, Types, and Functions

`adminUserSvcAcctSetFlags` includes secret key, policy, name, description, and expiry. `adminUserSvcAcctSetCmd` binds both `edit` and `set`. `mainAdminUserSvcAcctSet` builds `madmin.UpdateServiceAccountReq`.

## Control Flow

The handler validates target and service account, reads optional fields, creates an admin client, reads optional policy bytes, parses optional expiry using shared `supportedTimeFormats` and local timezone, builds an update request with only provided values, sends `UpdateServiceAccount`, and prints an edit success message.

## State and Persistence Behavior

The server persists updated service-account fields, policy, secret, and expiration. The client reads a local policy file but writes no local files.

## Dependencies and Integration Points

It depends on shared time formats from `admin-user-svcacct-add.go`, `madmin.UpdateServiceAccountReq`, file IO for policy bytes, and shared account output.

## Risks and Edge Cases

Unlike add, this file does not parse or reject empty policy documents client-side; validation is left to the server. There is no way to clear expiration except by server semantics for nil or absent fields. Local timezone affects expiry interpretation.

## Test Signals

Tests should cover each optional field independently, invalid policy path, invalid expiry, alias name `set`, nil versus non-nil expiration pointer, and update payload contents.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct.go -->
# sources/object-store/minio-mc/cmd/admin-user-svcacct.go

## Purpose

`admin-user-svcacct.go` defines the `mc admin user svcacct` command group for service-account management.

## Important APIs, Types, and Functions

`adminUserSvcAcctSubcommands` includes add, list, remove, info, edit/set, enable, and disable. `adminUserSvcAcctCmd` defines the group command. `mainAdminUserSvcAcct` delegates invalid usage to `commandNotFound`.

## Control Flow

No service-account operation happens at the group level. The CLI dispatches to subcommands; otherwise the group action reports valid subcommands.

## State and Persistence Behavior

Only static command metadata is defined.

## Dependencies and Integration Points

It integrates with the admin user command group, sibling service-account command files, global flags, and shared command-not-found behavior.

## Risks and Edge Cases

Subcommand registration order affects help output. The `edit` command also has alias `set`, so completion and help must account for both names.

## Test Signals

Tests should verify subcommand composition and bare group behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user-svcacct.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user.go -->
# sources/object-store/minio-mc/cmd/admin-user.go

## Purpose

`admin-user.go` defines the `mc admin user` command group for user, service-account, and STS account management.

## Important APIs, Types, and Functions

`adminUserSubcommands` contains add, disable, enable, remove, list, info, policy, svcacct, and sts. `adminUserCmd` defines the group. `mainAdminUser` calls `commandNotFound`.

## Control Flow

The group command only handles missing or invalid subcommands. All IAM operations are delegated to subcommands.

## State and Persistence Behavior

Only command registration state is declared.

## Dependencies and Integration Points

It integrates the user family into the admin command tree and pulls in subcommands declared across sibling files.

## Risks and Edge Cases

The code comment says "admin config" rather than "admin user", which is documentation drift only. Registration order affects help and completion.

## Test Signals

Tests should assert subcommand presence, aliases on child commands, and bare group command-not-found behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-user.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-export.go -->
# sources/object-store/minio-mc/cmd/alias-export.go

## Purpose

`alias-export.go` implements `mc alias export`, printing a stored alias configuration as JSON for reuse or import.

## Important APIs, Types, and Functions

`aliasExportCmd` defines the command. `checkAliasExportSyntax` validates exactly one alias and alias syntax. `exportAlias` loads the MinIO Client config and marshals the selected `aliasConfigV10`.

## Control Flow

The handler validates input, cleans the alias, loads config, looks up the alias in `Aliases`, marshals the config with color JSON, and prints it to stdout. Missing aliases fail with an invalid argument error.

## State and Persistence Behavior

The command reads local `mc` config only and writes stdout. It does not contact a server.

## Dependencies and Integration Points

It depends on config helpers such as `loadMcConfig`, `mustGetMcConfigPath`, alias validation helpers, `console.Println`, and `aliasConfigV10`.

## Risks and Edge Cases

Export includes secret keys in plaintext JSON. Environment-only or runtime alias overrides are not exported because the command reads the persisted config map.

## Test Signals

Tests should cover invalid aliases, missing aliases, JSON field preservation, and secret-bearing output expectations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-import.go -->
# sources/object-store/minio-mc/cmd/alias-import.go

## Purpose

`alias-import.go` implements `mc alias import`, loading alias credentials from a JSON file or stdin and saving them into the local config.

## Important APIs, Types, and Functions

`aliasImportCmd` defines the command. `checkAliasImportSyntax` validates arg count and alias. `checkCredentialsSyntax` validates URL, access key, secret key, API signature, and path mode. `importAlias` saves the config and returns an `aliasMessage`.

## Control Flow

The handler validates syntax, chooses the credentials file path or stdin name, reads the JSON, unmarshals into `aliasConfigV10`, validates fields, loads existing config, writes the alias entry, saves config, and prints an import message.

## State and Persistence Behavior

This command mutates the local MinIO Client config file by adding or replacing an alias. It does not probe the remote server.

## Dependencies and Integration Points

It depends on local config load/save helpers, alias validation helpers, `aliasMessage`, and standard JSON/file IO.

## Risks and Edge Cases

Using `os.Stdin.Name()` as a read path for stdin may depend on platform behavior. Import overwrites an existing alias without confirmation. Credentials are validated syntactically but not verified against the server.

## Test Signals

Tests should cover file and stdin import, malformed JSON, invalid credential fields, overwrite behavior, and saved config contents.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-list.go -->
# sources/object-store/minio-mc/cmd/alias-list.go

## Purpose

`alias-list.go` implements `mc alias list` / `ls`, showing one or all configured aliases from environment, custom maps, and persisted config.

## Important APIs, Types, and Functions

`aliasListCmd` defines the command. `mainAliasList` configures colors and prints aliases. `printAliases` aligns aliases and hides incomplete credentials. `byAlias` sorts messages. `buildAliasMessage` converts `aliasConfigV10` into output. `listAliases` gathers sources.

## Control Flow

The handler validates at most one alias, cleans it, gathers matching aliases, marks their operation as `list`, and prints them. Specific alias lookup uses `mustGetHostConfig`. Full listing reads environment variables with `mcEnvHostPrefix`, `aliasToConfigMap`, and persisted config, annotating config-file entries with source path, then sorts by alias.

## State and Persistence Behavior

The command reads local config and environment variables only. It does not mutate config.

## Dependencies and Integration Points

It integrates local alias config, environment alias expansion, global JSON mode, `aliasMessage`, and console table helpers.

## Risks and Edge Cases

Duplicate aliases from different sources can produce multiple rows. Non-JSON output pads the alias field by mutating the message. Credentials may be printed unless blanked because either access or secret key is missing.

## Test Signals

Tests should cover specific alias not found, source precedence/listing, sorted output, deprecated lookup field behavior, JSON versus table formatting, and incomplete credentials.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-main.go -->
# sources/object-store/minio-mc/cmd/alias-main.go

## Purpose

`alias-main.go` defines the `mc alias` command group and the shared output type for alias operations.

## Important APIs, Types, and Functions

`aliasSubcommands` contains set, list, remove, import, and export. `aliasCmd` defines the group. `aliasMessage` carries alias URL, credentials, API, path, source, and deprecated lookup fields. `aliasMessage.String` and `JSON` render operation results.

## Control Flow

The group action reports command-not-found help. Subcommands create `aliasMessage` values with operation names that select list/add/set/remove/import rendering.

## State and Persistence Behavior

The file itself only defines command and message structures. Persistence is handled by alias subcommands through config helpers.

## Dependencies and Integration Points

It integrates the alias command family into the app command tree and is reused by alias set/list/remove/import.

## Risks and Edge Cases

`aliasMessage.JSON` can include secret keys. The deprecated `Lookup` field is still supported for compatibility with older output consumers.

## Test Signals

Tests should verify group command behavior, JSON status injection, list rendering with path/lookup fallback, and success text per operation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-remove.go -->
# sources/object-store/minio-mc/cmd/alias-remove.go

## Purpose

`alias-remove.go` implements `mc alias remove` / `rm`, deleting an alias from the local config file.

## Important APIs, Types, and Functions

`aliasRemoveCmd` declares the command. `checkAliasRemoveSyntax` validates exactly one alias. `aliasMustExist` checks configured aliases. `removeAlias` loads config, deletes the alias, saves config, and returns `aliasMessage`.

## Control Flow

The handler validates syntax, sets success color, calls `removeAlias`, marks the output operation as remove, and prints it.

## State and Persistence Behavior

The persisted local MinIO Client config is mutated by deleting the alias. The command does not contact the remote server.

## Dependencies and Integration Points

It depends on local config load/save helpers, alias validation, `mustGetHostConfig`, and shared alias output.

## Risks and Edge Cases

`aliasMustExist` may find aliases from sources other than the persisted config, but `removeAlias` only deletes from loaded config. That can produce surprising behavior for environment-provided aliases. Deletion is immediate and unconfirmed.

## Test Signals

Tests should cover missing alias, invalid alias, persisted alias deletion, env-only alias behavior, save failures, and output text/JSON.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-set.go -->
# sources/object-store/minio-mc/cmd/alias-set.go

## Purpose

`alias-set.go` implements `mc alias set`, creating or updating local aliases and probing S3 signature compatibility when the API signature is not explicitly provided.

## Important APIs, Types, and Functions

`aliasSetFlags` defines path and API options. `checkAliasSetSyntax` validates alias, URL, credentials, API, and path or deprecated lookup. `setAlias` writes config. `probeS3Signature` tries S3v4 then S3v2 against a random probe bucket. `BuildS3Config` builds and optionally probes a `Config`. `fetchAliasKeys` reads credentials from args, prompts, or stdin. `configurePeerCertificate` injects a trusted peer certificate into transport roots.

## Control Flow

The handler normalizes deprecated lookup into path mode, fetches credentials, validates syntax, creates a cancellable context, optionally prompts to trust a self-signed certificate, builds/probes S3 config, saves the alias with resolved URL/signature/path, sets operation `set` or deprecated `add`, and prints output.

## State and Persistence Behavior

The command persists alias credentials in the local MinIO Client config. It may also mutate in-memory TLS root CA pools or transport settings to trust a peer certificate. It contacts the remote endpoint during signature probing unless API is specified.

## Dependencies and Integration Points

It integrates with S3 config creation, minio-go error responses, prompt trust logic, TLS transport helpers, config load/save, validation helpers, and global networking/debug settings.

## Risks and Edge Cases

Credentials can leak through args or JSON output. Signature probing treats `BucketDoesNotExist` and `AccessDenied` as success, which is intentional but depends on server behavior. The random probe bucket uses `math/rand` seeded by time, not crypto randomness, but only for a probe name. Peer certificate trust mutates shared CA state in some branches.

## Test Signals

Tests should cover credential prompt paths, validation failures, explicit API bypassing probe, S3v4-to-S3v2 fallback, self-signed certificate configuration, deprecated lookup mapping, and saved config fields.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/alias-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/anonymous-main.go -->
# sources/object-store/minio-mc/cmd/anonymous-main.go

## Purpose

`anonymous-main.go` implements `mc anonymous`, managing anonymous bucket/prefix access policies and listing public links.

## Important APIs, Types, and Functions

`anonymousCmd` supports `set`, `set-json`, `get`, `get-json`, `list`, and `links` with `--recursive`. Message types are `anonymousRules`, `anonymousMessage`, and `anonymousLinksMessage`. Core helpers include `checkAnonymousSyntax`, `accessPermToString`, `stringToAccessPerm`, `doSetAccess`, `doSetAccessJSON`, `doGetAccess`, `doGetAccessRules`, `runAnonymousListCmd`, `runAnonymousLinksCmd`, and `runAnonymousCmd`.

## Control Flow

The main handler validates operation-specific arity and permission names, sets output color, and dispatches by operation. Set operations create a client and call `SetAccess`, optionally reading a JSON policy file capped at 120 KiB. Get operations call `GetAccess`. List retrieves access rules and prints resource-policy mappings. Links retrieves rules, filters readable rules under the requested path, lists matching objects, encodes public URLs, and prints them.

## State and Persistence Behavior

Anonymous policy state is persisted remotely by the S3-compatible server. Locally, the command reads optional JSON files and writes output only.

## Dependencies and Integration Points

It depends on generic `newClient`, client `SetAccess`, `GetAccess`, `GetAccessRules`, `List`, URL/alias helpers, `accessPerms` definitions from elsewhere, probe errors, and global context.

## Risks and Edge Cases

`set-json` uses `io.ReadFull` with a fixed buffer and treats a file larger than 120 KiB as too large. `links` filters rules by string prefix and only includes download/public permissions. Error handling maps `APINotImplemented` to clearer messages for non-S3 targets. Custom anonymous JSON is passed through server-side validation.

## Test Signals

Tests should cover operation arity, permission mapping, custom JSON size limit, non-S3 API errors, list/links filtering, recursive behavior, and get-json unmarshalling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/anonymous-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/arg-kvs.go -->
# sources/object-store/minio-mc/cmd/arg-kvs.go

## Purpose

`arg-kvs.go` defines a small ordered key-value collection used by command argument wrappers.

## Important APIs, Types, and Functions

`argKV` stores a JSON-serializable key and value. `argKVS` is a slice with methods `Empty`, `Set`, `Get`, and `Lookup`.

## Control Flow

`Set` scans for an existing key and replaces it in-place; if missing, it appends a new entry. `Get` delegates to `Lookup` and returns an empty string for absent keys. `Lookup` performs a linear scan.

## State and Persistence Behavior

State is in-memory only. JSON tags make the structures suitable for output or serialization by callers, but this file does not persist them.

## Dependencies and Integration Points

There are no external dependencies. It is a package-level utility for command code that needs simple ordered key-value state.

## Risks and Edge Cases

Lookups are O(n), which is fine for small argument lists but not large maps. Empty string values are indistinguishable from missing keys when using `Get`; callers needing that distinction must use `Lookup`.

## Test Signals

Tests should cover empty state, append and overwrite behavior, duplicate prevention through `Set`, and `Get` versus `Lookup` semantics.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/arg-kvs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/auto-complete.go -->
# sources/object-store/minio-mc/cmd/auto-complete.go

## Purpose

`auto-complete.go` builds shell completion support for `mc` commands, including filesystem paths, S3 paths, aliases, and admin config keys.

## Important APIs, Types, and Functions

Predictor types are `fsComplete`, `adminConfigComplete`, `s3Complete`, and `aliasComplete`. Key helpers are `completeAdminConfigKeys`, `completeS3Path`, `flagsToCompleteFlags`, `cmdToCompleteCmd`, and `mainComplete`. `completeCmds` maps command paths to predictors.

## Control Flow

Filesystem completion delegates to `posener/complete`, with special handling for `~/`. S3 completion loads config, predicts aliases until a slash is present, then lists remote path contents and recurses into a single matching directory. Admin config completion predicts aliases and config keys from `HelpConfigKV`. `cmdToCompleteCmd` recursively converts `cli.Command` trees into `complete.Command`, skipping hidden subcommands and adding aliases. `mainComplete` builds the root completion tree from `appCmds` and runs the completion engine.

## State and Persistence Behavior

The code reads local config and may contact remote S3/admin endpoints for path and config-key predictions. It writes no persistent state.

## Dependencies and Integration Points

It integrates with the full CLI command tree, `posener/complete`, local config loading, `newClient`, `newAdminClient`, object listing, admin config help APIs, global flags, and many command path names.

## Risks and Edge Cases

Completions can trigger network calls and may be slow or fail silently. The `completeCmds` map must stay synchronized with visible leaf commands. S3 recursive completion can expand into remote listings when exactly one directory matches. Hidden commands are skipped in command conversion.

## Test Signals

Tests should verify command coverage, flag conversion for long and short flags, hidden command skipping, alias completion sorting, tilde restoration, deep-level stopping, and graceful nil predictions on config/client failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/auto-complete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/auto-complete_test.go -->
# sources/object-store/minio-mc/cmd/auto-complete_test.go

## Purpose

`auto-complete_test.go` verifies that every visible leaf command has a registered completion predictor in `completeCmds`.

## Important APIs, Types, and Functions

The single test `TestAutoCompletionCompletness` recursively walks `appCmds` and checks `completeCmds` for visible commands without subcommands.

## Control Flow

The nested `checkCompletion` function skips hidden command branches, recurses into subcommands, and fails when a visible leaf command path is missing from `completeCmds`.

## State and Persistence Behavior

There is no persistence. The test reads the static command tree and completion map.

## Dependencies and Integration Points

It depends on `appCmds`, `cli.Command`, and the path naming convention used by `cmdToCompleteCmd`.

## Risks and Edge Cases

The check uses `if cmd.Hidden` inside the subcommand loop instead of checking `subCmd.Hidden`, so hidden child behavior relies partly on recursive logic. It only checks presence, not correctness of predictors.

## Test Signals

The primary signal is failure naming the missing command path. Additional tests could validate predictor behavior for representative commands.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/auto-complete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-cancel.go -->
# sources/object-store/minio-mc/cmd/batch-cancel.go

## Purpose

`batch-cancel.go` implements `mc batch cancel`, canceling an ongoing batch job by ID.

## Important APIs, Types, and Functions

`batchCancelCmd` defines the command and an unused-looking `--id` flag while usage expects positional job ID. `batchCancelMessage` renders success. `mainBatchCancel` calls `CancelBatchJob`.

## Control Flow

The handler validates target and job ID, creates an admin client, creates a cancellable context, calls `adminClient.CancelBatchJob`, and prints a success message.

## State and Persistence Behavior

The server changes batch job state to canceled. The client writes no local state.

## Dependencies and Integration Points

It uses `madmin` batch job APIs, `newAdminClient`, shared message/output helpers, and the batch command group.

## Risks and Edge Cases

The declared `--id` flag is not used by the handler, which can confuse callers. Cancellation outcome and idempotence are server-defined.

## Test Signals

Tests should cover arity, positional job ID propagation, unused flag behavior, API errors, and JSON/text message output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-cancel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-describe.go -->
# sources/object-store/minio-mc/cmd/batch-describe.go

## Purpose

`batch-describe.go` implements `mc batch describe`, printing the stored job definition for a batch job.

## Important APIs, Types, and Functions

`batchDescribeCmd` declares the command. `checkBatchDescribeSyntax` enforces target and job ID. `mainBatchDescribe` calls `DescribeBatchJob`.

## Control Flow

The handler validates args, creates an admin client, calls `DescribeBatchJob` with a cancellable context, and prints the returned job definition directly with `fmt.Println`.

## State and Persistence Behavior

The command reads remote batch job definition state only and writes stdout.

## Dependencies and Integration Points

It integrates with `madmin.AdminClient.DescribeBatchJob`, batch command registration, and common error handling.

## Risks and Edge Cases

Direct printing bypasses `printMsg`, so JSON mode does not wrap or transform output. Output format depends on server-returned string content.

## Test Signals

Tests should cover exact arity, API call arguments, direct stdout behavior, and error handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-describe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-generate.go -->
# sources/object-store/minio-mc/cmd/batch-generate.go

## Purpose

`batch-generate.go` implements `mc batch generate`, producing batch job templates or listing supported job types.

## Important APIs, Types, and Functions

`batchGenerateCmd` defines the command. `mainBatchGenerate` calls `GetSupportedBatchJobTypes`, `GenerateBatchJobV2`, or legacy `GenerateBatchJob` depending on input and server capability.

## Control Flow

The handler validates target and job type. For `list`, it asks the server for supported types and falls back to `madmin.SupportedJobTypes` when the API is unavailable, printing JSON or one type per line. For templates, it tries V2 generation first; if unavailable it verifies the job type against static supported types and calls the legacy generator.

## State and Persistence Behavior

The command reads server capabilities/templates and writes stdout only.

## Dependencies and Integration Points

It uses `madmin.GenerateBatchJobOpts`, static `madmin.SupportedJobTypes`, color JSON, and batch group registration.

## Risks and Edge Cases

Server API availability affects output source. Unknown job types are rejected only after V2 reports unavailable. Direct stdout bypasses normal message wrapping.

## Test Signals

Tests should cover supported type list in JSON/plain modes, V2 success, V2 unavailable fallback, unsupported type failure, and API errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-list.go -->
# sources/object-store/minio-mc/cmd/batch-list.go

## Purpose

`batch-list.go` implements `mc batch list` / `ls`, listing batch jobs and deriving a current status for each job.

## Important APIs, Types, and Functions

`batchListFlags` defines `--type`. `batchListMessage` stores `[]madmin.BatchJobResult` plus an admin client used during rendering. Its `String` and `JSON` methods call `BatchJobStatus` per job to derive completed, in-progress, failed, or unknown status. `mainBatchList` calls `ListBatchJobs`.

## Control Flow

The handler validates one target, creates an admin client, lists jobs filtered by job type, and prints a `batchListMessage`. Rendering builds a table or JSON array and performs additional status lookups for each job.

## State and Persistence Behavior

The command reads remote batch job state only. Runtime output rendering performs network calls via the embedded admin client.

## Dependencies and Integration Points

It integrates `madmin.ListBatchJobs`, `BatchJobStatus`, tablewriter output, humanized times, global JSON mode, and batch command registration.

## Risks and Edge Cases

Rendering has side effects: `String` and `JSON` can make network calls and print errors with `println`. It uses `context.Background()` rather than command context for status lookups. Job ordering depends on server response.

## Test Signals

Tests should cover empty jobs, type filter propagation, status derivation, status lookup failure, JSON shape, and avoiding network calls during pure serialization if refactored.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-main.go -->
# sources/object-store/minio-mc/cmd/batch-main.go

## Purpose

`batch-main.go` defines the `mc batch` command group for MinIO batch job lifecycle management.

## Important APIs, Types, and Functions

`batchSubcommands` includes generate, start, list, status, describe, and cancel. `batchCmd` declares the group. `mainBatch` delegates to `commandNotFound`.

## Control Flow

No batch operation occurs at group level. Subcommands handle all behavior.

## State and Persistence Behavior

Only command metadata is defined.

## Dependencies and Integration Points

It integrates sibling batch command files into the app command tree and completion coverage.

## Risks and Edge Cases

The commented suspend/resume placeholder signals incomplete or removed functionality. Registration order controls help output.

## Test Signals

Tests should verify subcommand presence and bare group behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-start.go -->
# sources/object-store/minio-mc/cmd/batch-start.go

## Purpose

`batch-start.go` implements `mc batch start`, submitting a batch job definition file to the server.

## Important APIs, Types, and Functions

`batchStartCmd` defines the command. `batchStartMessage` wraps `madmin.BatchJobResult`. `mainBatchStart` reads the job file and calls `StartBatchJob`.

## Control Flow

The handler validates target and job-file path, creates an admin client, reads the entire file into memory, creates a cancellable context, sends the file content as a string to `StartBatchJob`, and prints the result.

## State and Persistence Behavior

The server persists or starts the batch job. Locally, the command reads a YAML/JSON definition file but writes no files.

## Dependencies and Integration Points

It uses file IO, `madmin.StartBatchJob`, shared output helpers, and batch command registration.

## Risks and Edge Cases

The whole job file is loaded into memory. File content validation is server-side. Success text includes `Started` with `%s`, relying on its string formatting.

## Test Signals

Tests should cover missing file, invalid arity, file content propagation, API errors, and result message rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-status.go -->
# sources/object-store/minio-mc/cmd/batch-status.go

## Purpose

`batch-status.go` implements `mc batch status`, showing real-time or last-known metrics for a batch job.

## Important APIs, Types, and Functions

`batchStatusCmd` defines the command. `batchJobStatusMessage` wraps `madmin.JobMetric`. `mainBatchStatus` orchestrates live metrics or completed-job lookup. `batchJobMetricsUI` is a Bubble Tea model that renders job metrics for replication, expiration, and catalog jobs.

## Control Flow

The handler validates target and job ID, creates an admin client, calls `DescribeBatchJob` to decide whether the job is active, and creates a metrics UI. If the job no longer exists as active, it calls `BatchJobStatus` once. Otherwise it streams `client.Metrics` with `MetricsBatchJobs`, `ByJobID`, and one-second interval. JSON mode prints each metric and cancels on complete/failed; non-JSON mode sends metrics to the Bubble Tea UI.

## State and Persistence Behavior

Remote metrics are read only. Local runtime state is the UI model's latest metric, spinner, and quitting flag.

## Dependencies and Integration Points

It depends on `madmin` batch metrics APIs, Bubble Tea, Bubbles spinner, humanize formatting, tablewriter, context cancellation, and global JSON mode.

## Risks and Edge Cases

The UI assumes known job type metric substructures. Catalog scan speed divides by elapsed seconds, which can be zero for early metrics. JSON mode waits on context cancellation and depends on streaming callback cancellation behavior.

## Test Signals

Tests should cover active versus historical job branch, JSON status transitions, context cancellation, UI quitting on complete/failed, each job type rendering, and missing job metrics.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/batch-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/build-constants.go -->
# sources/object-store/minio-mc/cmd/build-constants.go

## Purpose

`build-constants.go` provides build-time metadata variables for version, release tag, commit, short commit, and copyright year.

## Important APIs, Types, and Functions

Package variables are `Version`, `ReleaseTag`, `CommitID`, `ShortCommitID`, and `CopyrightYear`. Defaults are development placeholders, and build tooling can override them with linker flags.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The values are static process state compiled into the binary. No persistence occurs.

## Dependencies and Integration Points

These variables are typically used by version, help, user-agent, and app-info code elsewhere in `mc`.

## Risks and Edge Cases

`ShortCommitID = CommitID[:12]` assumes `CommitID` is at least 12 bytes. The default value satisfies this, but malformed linker injection could panic at initialization.

## Test Signals

Tests should verify defaults are non-empty and build pipelines inject a long enough commit ID.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/build-constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cat-main.go -->
# sources/object-store/minio-mc/cmd/cat-main.go

## Purpose

`cat-main.go` implements `mc cat`, streaming object, file, zip member, versioned, or stdin content to stdout with range/tail support and terminal-safe output.

## Important APIs, Types, and Functions

`catFlags` includes rewind, version-id, zip, offset, tail, and part-number. `prettyStdout` replaces non-printable runes with `^?` for terminals. `catOpts` stores parsed options. `parseCatSyntax`, `catURL`, `catOut`, and `mainCat` are the core flow.

## Control Flow

The handler creates a cancellable context, validates encryption keys, parses syntax and incompatible flags, handles stdin, preserves argument order when `-` is present, then streams each URL. `catURL` stats remote/local content to determine size, version ID, and tail offset, opens a source stream with `GetOptions`, and calls `catOut`. `catOut` copies to stdout or `prettyStdout`, handles broken pipes gracefully, and verifies the byte count when expected size is known.

## State and Persistence Behavior

The command reads object/file/stdin data and writes stdout only. It does not modify source objects. It may read encrypted object metadata and version information through stat/get paths.

## Dependencies and Integration Points

It integrates with encryption key validation, `url2Stat`, `getSourceStreamFromURL`, `GetOptions`, rewind parsing, object versioning, zip extraction support, terminal detection, and typed client errors such as `UnexpectedEOF`.

## Risks and Edge Cases

`checkCatSyntax` requires at least one arg, making `stdinMode` in `parseCatSyntax` unreachable unless call structure changes. `prettyStdout` preserves invalid UTF-8 replacement runes but masks control characters. Tail/offset/part-number combinations are carefully rejected. Size verification is disabled for part downloads and unknown sizes.

## Test Signals

Tests should cover pretty stdout, incompatible flags, rewind versus version ID, tail offset calculation, offset beyond object size, broken pipe handling, stdin `-` ordering, and encrypted/versioned object options.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cat-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cat_test.go -->
# sources/object-store/minio-mc/cmd/cat_test.go

## Purpose

`cat_test.go` tests `prettyStdout`, the terminal-safe writer used by `mc cat`.

## Important APIs, Types, and Functions

`TestPrettyStdout` copies test strings through `newPrettyStdout` into a buffer and compares expected output.

## Control Flow

The table-driven test covers empty text, plain text, CRLF, tabs/newlines, Unicode, ANSI escape sequences, clear-screen control sequence, and random bytes. It verifies copy byte count and final buffer content.

## State and Persistence Behavior

No persistence is involved; the test uses in-memory readers and buffers.

## Dependencies and Integration Points

It tests `prettyStdout.Write` from `cat-main.go`, indirectly guarding terminal output safety for `mc cat`.

## Risks and Edge Cases

The test expects invalid byte sequences to be transformed according to Go UTF-8 decoding behavior. It does not test partial writes or writer errors.

## Test Signals

The main signal is exact output substitution for control bytes and preservation of printable/space Unicode.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/certs.go -->
# sources/object-store/minio-mc/cmd/certs.go

## Purpose

`certs.go` manages MinIO Client certificate and CA directory paths and loads trusted root CAs.

## Important APIs, Types, and Functions

Functions include `getCertsDir`, `isCertsDirExists`, `createCertsDir`, `getCAsDir`, `mustGetCAsDir`, `isCAsDirExists`, `createCAsDir`, and `loadRootCAs`.

## Control Flow

Path helpers derive `certs` and `CAs` directories from the mc config directory. Existence helpers call `os.Stat`. Creation helpers use `os.MkdirAll` with mode `0700`. `loadRootCAs` calls `certs.GetRootCAs` with the CAs directory and stores the result in `globalRootCAs`.

## State and Persistence Behavior

The file creates local certificate directories and updates in-memory `globalRootCAs`. CA files themselves are read by the certs package.

## Dependencies and Integration Points

It depends on config directory helpers, global constants `globalMCCertsDir` and `globalMCCAsDir`, `github.com/minio/pkg/v3/certs`, and `fatalIf`.

## Risks and Edge Cases

`is*Exists` treats all `os.Stat` errors as non-existence. `mustGetCAsDir` suppresses errors by returning an empty string, so callers must tolerate that. Directory permissions are restrictive by design.

## Test Signals

Tests should cover path construction, create permissions, stat error behavior, missing config directory errors, and CA load failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/certs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cli_test.go -->
# sources/object-store/minio-mc/cmd/cli_test.go

## Purpose

`cli_test.go` verifies that visible leaf commands define `OnUsageError`, ensuring consistent usage-error handling across the CLI.

## Important APIs, Types, and Functions

`TestCLIOnUsageError` recursively walks `appCmds` and checks `cli.Command.OnUsageError` for visible leaves.

## Control Flow

The nested `checkOnUsageError` recurses into subcommands, skips hidden command branches, and records an error when a visible leaf command lacks usage-error handling.

## State and Persistence Behavior

No persistence; it inspects static CLI metadata.

## Dependencies and Integration Points

It depends on `appCmds`, `cli.Command`, and the convention that user-invokable leaf commands should set `OnUsageError`.

## Risks and Edge Cases

Like the autocomplete test, the hidden-check inside the loop checks the parent command rather than the child before recursion. It only validates presence, not behavior of the handler.

## Test Signals

The signal is a test failure naming the command path missing `OnUsageError`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cli_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-admin.go -->
# sources/object-store/minio-mc/cmd/client-admin.go

## Purpose

`client-admin.go` constructs and caches MinIO admin clients and anonymous admin clients from aliases.

## Important APIs, Types, and Functions

`NewAdminFactory` returns a closure that caches `*madmin.AdminClient` by config hash under a mutex. `newAdminClient` expands aliases and builds a signed admin client. `newAnonymousClient` expands aliases and builds an unsigned `madmin.AnonymousClient`. `s3AdminNew` is the package-level cached factory.

## Control Flow

The admin factory parses host URL, computes a config hash, checks the cache, builds transport and credential chain, creates `madmin.NewWithOptions`, sets custom transport and app info, caches it, and returns it. `newAdminClient` rejects raw URLs without alias config, builds an S3 config, and calls the factory. `newAnonymousClient` similarly rejects unknown URLs, parses TLS mode, creates an anonymous client, installs a custom transport, and wraps debug tracing when enabled.

## State and Persistence Behavior

The factory holds an in-memory client cache for the process lifetime. No local files are written. Alias config is read through `expandAlias`.

## Dependencies and Integration Points

It integrates with alias resolution, `Config` transport/credentials helpers, `madmin-go`, minio-go credential chains, ieproxy, TLS/root CA globals, custom dialers, HTTP tracing, app metadata, and global debug/insecure settings.

## Risks and Edge Cases

Cache invalidation depends entirely on `getConfigHash`; changed global state not included in the hash could reuse stale clients. Raw URLs are intentionally rejected for admin operations. Anonymous transport constructs TLS config from global roots and insecure flag.

## Test Signals

Tests should cover cache reuse by equivalent config, cache miss for changed config, invalid alias/raw URL rejection, custom transport installation, app info propagation, and anonymous client TLS mode.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-admin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-admin_test.go -->
# sources/object-store/minio-mc/cmd/client-admin_test.go

## Purpose

`client-admin_test.go` provides an HTTP handler helper for admin policy request tests.

## Important APIs, Types, and Functions

`adminPolicyHandler` stores endpoint, policy name, and expected policy bytes. Its `ServeHTTP` handles authenticated PUT requests and validates content length and body length.

## Control Flow

The handler rejects missing `Authorization` with 403. On PUT, it parses `Content-Length`, copies exactly that many bytes from the body, checks that received length matches expected policy length, and returns 200 with zero content length. Other methods return 403.

## State and Persistence Behavior

There is no persistence. The handler stores expected test state in memory.

## Dependencies and Integration Points

It integrates with tests that exercise admin policy upload behavior through HTTP.

## Risks and Edge Cases

The handler checks body length but not byte equality. Unused fields such as endpoint/name may be for compatibility with broader tests.

## Test Signals

Useful signals are status codes for missing auth, bad length, short body, correct PUT, and unsupported methods.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-admin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-errors.go -->
# sources/object-store/minio-mc/cmd/client-errors.go

## Purpose

`client-errors.go` defines typed error values used across filesystem, S3, object, and stream operations.

## Important APIs, Types, and Functions

Error types include `APINotImplemented`, `InvalidArgument`, bucket errors, object errors, file path errors, symlink errors, `ObjectMissing`, `ObjectIsDeleteMarker`, `UnexpectedShortWrite`, `UnexpectedEOF`, `UnexpectedExcessRead`, and `SameFile`. Each implements `Error() string`.

## Control Flow

There is no branching beyond `ObjectMissing.Error`, which includes a time reference when present. The types are designed for `errors.As` or type switches, as seen in anonymous command handling.

## State and Persistence Behavior

No persistence. Error values carry contextual fields such as bucket, object, path, sizes, and time.

## Dependencies and Integration Points

These errors are used by client implementations and commands to provide typed failures and user-facing messages. `APINotImplemented` is explicitly handled by anonymous access commands; `UnexpectedEOF` is used by `catOut`.

## Risks and Edge Cases

Messages are user-visible API contracts for tests and scripts. `UnexpectedExcessRead` is a distinct type alias with its own text. Some comments contain old errno references but the code is platform-neutral.

## Test Signals

Tests should cover exact error strings, type assertions through `probe.Error`, time-specific object missing text, and stream size error formatting.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-errors.go -->
