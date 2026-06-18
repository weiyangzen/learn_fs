# subset-b-008171 research

Grouped source research for MinIO `mc admin` command files under `sources/object-store/minio-mc/cmd`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-status.go -->
# sources/object-store/minio-mc/cmd/admin-decom-status.go

## Purpose
Implements `mc admin decommission status`, the human and JSON status view for MinIO server-pool decommissioning. It can show one pool passed as a second argument or list the decommission state of every pool.

## Important APIs, types, and functions
The command is `adminDecommissionStatusCmd`; `checkAdminDecommissionStatusSyntax` permits one or two arguments. `mainAdminDecommissionStatus` uses `newAdminClient`, `StatusPool`, `ListPoolsStatus`, `json.MarshalIndent`, `console.NewTable`, and `humanize.IBytes/RelTime/Ordinal`.

## Control flow
The handler cleans the target alias, creates an admin client, then branches on an optional pool argument. A single-pool request fetches `StatusPool`, emits JSON directly when requested, otherwise derives a completion, failed, canceled, active-rate, starting, or unscheduled message. A list request fetches all pools and renders a table of pool id, command line, usage, and status.

## State and persistence behavior
The file does not persist local state. It observes server-side decommission metadata, especially `StartTime`, sizes, and terminal booleans, and converts those into display state. Its rate calculation is transient and based on current wall-clock time.

## Dependencies and integration points
It integrates the `cli` command tree, `madmin-go` admin pool APIs through the shared client, global JSON handling, MinIO console tables, and color helpers from the surrounding `cmd` package.

## Risks and edge cases
Total size can be zero, so list output has an explicit zero-capacity branch. Single-pool speed only appears when the used-size delta and elapsed duration are meaningful; otherwise it says startup. The failed/canceled messages are colored as success text, which may be confusing.

## Test signals
Useful tests should cover one-argument list mode, two-argument pool mode, JSON marshal output, zero-size pools, each terminal decommission flag, active rate calculation after ten seconds, and syntax rejection for zero or more than two arguments.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom.go -->
# sources/object-store/minio-mc/cmd/admin-decom.go

## Purpose
Defines the `mc admin decommission` command group and its `decom` alias. It is a router for pool decommission lifecycle subcommands.

## Important APIs, types, and functions
`adminDecommissionSubcommands` registers start, status, and cancel command values. `adminDecommissionCmd` wires the group into `minio/cli`, and `mainAdminDecommission` calls `commandNotFound`.

## Control flow
When a user invokes the group without a valid subcommand, control reaches `mainAdminDecommission`, which delegates error/help behavior to the common command dispatcher. All actual behavior is implemented in the subcommand files.

## State and persistence behavior
No local or remote state is read or written here. The file only exposes the command namespace that lets sibling subcommands mutate or inspect server-side decommission state.

## Dependencies and integration points
It depends on `github.com/minio/cli`, `setGlobalsFromContext`, `globalFlags`, and sibling command variables. It is also registered from the top-level admin command.

## Risks and edge cases
The primary risk is registration drift: missing a new lifecycle subcommand here makes it unreachable even if implemented. The group hides the help command, so `commandNotFound` behavior is important for user feedback.

## Test signals
CLI registration tests should verify `decommission`, `decom`, and the start/status/cancel subcommands are reachable and that an unknown subcommand produces the shared not-found/help path.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-add.go -->
# sources/object-store/minio-mc/cmd/admin-group-add.go

## Purpose
Implements `mc admin group add`, adding members to a new or existing MinIO IAM group. It also defines the shared `groupMessage` renderer used by group add, remove, list, info, enable, and disable commands.

## Important APIs, types, and functions
The command is `adminGroupAddCmd`. `checkAdminGroupAddSyntax` requires target, group name, and at least one member. `groupMessage.String` and `JSON` format group command results. `mainAdminGroupAdd` builds `madmin.GroupAddRemove` and calls `UpdateGroupMembers`.

## Control flow
The handler validates arguments, sets the group output color, creates an admin client for the alias, collects members from argument index two onward, calls the admin API with `IsRemove: false`, and prints a success message with the group and member list.

## State and persistence behavior
The persistent mutation is server-side IAM group membership. The client writes no local files. JSON status is synthesized locally after the server accepts the membership update.

## Dependencies and integration points
The file depends on MinIO admin IAM APIs, `probe` error wrapping, global context cancellation, `printMsg`, console colorization, and `colorjson`.

## Risks and edge cases
Argument parsing does not de-duplicate members or validate user existence locally; server validation is authoritative. Human output joins members with commas without spaces. The shared renderer means changes here can alter output for multiple group commands.

## Test signals
Tests should assert syntax enforcement, correct `GroupAddRemove` payload, fatal handling for admin API failures, JSON output shape, and stable human strings for add/list/remove/info/enable/disable operations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-disable.go -->
# sources/object-store/minio-mc/cmd/admin-group-disable.go

## Purpose
Defines the hidden mechanics for `mc admin group disable`, which disables an existing MinIO IAM group through the shared enable/disable handler.

## Important APIs, types, and functions
`adminGroupDisableCmd` sets command metadata, usage, flags, help text, and `Action: mainAdminGroupEnableDisable`. There are no additional local helpers.

## Control flow
After the CLI matches `disable`, execution is delegated to `mainAdminGroupEnableDisable` in `admin-group-enable.go`. That shared handler validates two arguments and maps the command name to `madmin.GroupDisabled`.

## State and persistence behavior
The file itself has no state logic. The resulting command mutates persistent server-side group status through `SetGroupStatus`.

## Dependencies and integration points
It depends on the group command registration file, global flags, `setGlobalsFromContext`, and the shared enable/disable implementation.

## Risks and edge cases
Because behavior is selected from `ctx.Command.Name`, renaming this command without updating the shared switch would break status selection. Coverage should include the disable path even though the logic lives elsewhere.

## Test signals
CLI tests should verify command registration, exact two-argument syntax via the shared handler, and that invoking `disable` results in `madmin.GroupDisabled` and a disable-specific message.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-enable.go -->
# sources/object-store/minio-mc/cmd/admin-group-enable.go

## Purpose
Implements the shared handler for `mc admin group enable` and `mc admin group disable`, changing a group's active status in MinIO IAM.

## Important APIs, types, and functions
`adminGroupEnableCmd` defines the enable command. `checkAdminGroupEnableSyntax` requires target and group name. `mainAdminGroupEnableDisable` maps command names to `madmin.GroupEnabled` or `madmin.GroupDisabled` and calls `SetGroupStatus`.

## Control flow
The handler validates syntax, initializes output color, opens an admin client, reads the group name, chooses the target status from `ctx.Command.Name`, invokes the server API, then prints a `groupMessage` whose operation is either `enable` or `disable`.

## State and persistence behavior
The only persistent effect is remote group status stored by MinIO. The local message includes `GroupStatus`, but human rendering uses the operation name rather than the status field.

## Dependencies and integration points
It integrates `madmin-go` group status constants, shared client creation, global context, `fatalIf`, `probe`, and the `groupMessage` type from the add file.

## Risks and edge cases
The default switch case handles unexpected command names, which protects against accidental reuse. There is no local existence check; server errors are surfaced. Disable command behavior depends on this file even though the disable command is declared separately.

## Test signals
Good tests mock both enable and disable command names, assert `SetGroupStatus` receives the correct enum, verify invalid command name handling, and check human/JSON output through `printMsg`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-info.go -->
# sources/object-store/minio-mc/cmd/admin-group-info.go

## Purpose
Implements `mc admin group info`, displaying members, policy, and status for a MinIO IAM group.

## Important APIs, types, and functions
The key symbols are `adminGroupInfoCmd`, `checkAdminGroupInfoSyntax`, and `mainAdminGroupInfo`. The handler calls `GetGroupDescription` and prints `groupMessage` with `GroupStatus`, `GroupPolicy`, and `Members`.

## Control flow
The command requires exactly target and group name. It creates an admin client, fetches the group description from the server, then delegates human or JSON rendering to the shared group message type.

## State and persistence behavior
No state is changed. The command reads persistent group metadata from MinIO IAM configuration and exposes it to the terminal or JSON stream.

## Dependencies and integration points
It uses the shared admin client, global context, `probe` error tracing, console color setup, and the message formatter declared in the add command file.

## Risks and edge cases
Large member lists are printed as a single comma-separated line in human output, which can be hard to read. Policy is displayed as returned by the server; missing policy or disabled state is not specially annotated beyond the raw fields.

## Test signals
Tests should cover argument validation, successful mapping from `GetGroupDescription` to output fields, JSON field names, and failures for nonexistent groups or admin API errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-list.go -->
# sources/object-store/minio-mc/cmd/admin-group-list.go

## Purpose
Implements `mc admin group list` and its `ls` short name, listing all MinIO IAM groups for an alias.

## Important APIs, types, and functions
`adminGroupListCmd` defines command metadata. `checkAdminGroupListSyntax` requires one target. `mainAdminGroupList` calls `ListGroups` and prints a `groupMessage` with `op: list`.

## Control flow
The handler validates the single alias argument, creates an admin client, fetches group names, and sends them to the shared renderer. Human output prints one colorized group per line; JSON output includes the `groups` array.

## State and persistence behavior
This is read-only. It observes server IAM group names and writes no local state.

## Dependencies and integration points
It depends on MinIO admin IAM APIs, the global CLI/output plumbing, console colors, and shared group message serialization.

## Risks and edge cases
The command does not sort locally, so output order follows server behavior. Empty group lists render as an empty string in human output, which may be ambiguous.

## Test signals
Tests should check syntax, alias client creation, API error propagation, empty and multi-group output, short-name registration, and JSON array rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-remove.go -->
# sources/object-store/minio-mc/cmd/admin-group-remove.go

## Purpose
Implements `mc admin group remove`/`rm`, removing members from a group or deleting the group when no member names are provided.

## Important APIs, types, and functions
`adminGroupRemoveCmd` defines the command. `checkAdminGroupRemoveSyntax` requires target and group. `mainAdminGroupRemove` builds `madmin.GroupAddRemove{IsRemove: true}` and calls `UpdateGroupMembers`.

## Control flow
After validation and client creation, the handler collects optional member arguments. It sends the group name and member slice to the server as a remove operation, then prints a message that distinguishes member removal from whole-group removal based on whether the member slice is empty.

## State and persistence behavior
Server-side IAM group state is mutated: either membership is changed or the group is removed. The local process keeps only a transient member list for output.

## Dependencies and integration points
It shares the add/remove server API with `admin-group-add.go`, the message renderer, color setup, `probe` errors, and global context.

## Risks and edge cases
Deleting a group is represented by an empty member list, so accidental omission of members changes the operation's impact. Local code does not prompt for confirmation or validate group membership; server-side checks are relied on.

## Test signals
Tests should cover member-removal payloads, empty-member group deletion payloads, short-name registration, server error handling, and the two human output variants.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group.go -->
# sources/object-store/minio-mc/cmd/admin-group.go

## Purpose
Defines the `mc admin group` command namespace for MinIO IAM group management.

## Important APIs, types, and functions
`adminGroupSubcommands` registers add, remove, info, list, enable, and disable. `adminGroupCmd` is the CLI group definition, and `mainAdminGroup` delegates unmatched invocation to `commandNotFound`.

## Control flow
The file performs no group operation directly. It is entered only when no registered subcommand handles the invocation, at which point the common command-not-found path displays the relevant guidance.

## State and persistence behavior
No local or server state is accessed here. State changes are owned by subcommand handlers.

## Dependencies and integration points
It depends on the `cli` package, global flags, command initialization, and sibling command variables. The top-level admin command imports this command group.

## Risks and edge cases
Adding a new group subcommand requires updating this list. Hidden help behavior means registration and `commandNotFound` output are the main user-facing contract.

## Test signals
Tests should verify all group subcommands and aliases are reachable under `mc admin group` and that bare or invalid invocations route to the shared not-found behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-heal-result-item.go -->
# sources/object-store/minio-mc/cmd/admin-heal-result-item.go

## Purpose
Wraps `madmin.HealResultItem` with helper methods that compute health-color transitions and display names for heal output.

## Important APIs, types, and functions
`hri` embeds `*madmin.HealResultItem`. Helpers include `newHRI`, `getObjectHCCChange`, `getBucketHCCChange`, `getReplicatedFileHCCChange`, `makeHealEntityString`, `getHRTypeAndName`, and `getHealResultStr`.

## Control flow
Each color helper inspects before/after drive or shard counts and maps them to `col` values. Object healing uses data and parity blocks plus online counts. Bucket healing classifies drive states as ok, missing, or unavailable. Replicated metadata computes quorum and surplus either per set or per disk count.

## State and persistence behavior
This file is pure presentation logic over server-returned heal records. It does not store state; it derives before/after color state from the `HealResultItem` snapshot.

## Dependencies and integration points
It depends on `madmin-go` heal item types and drive states, the `col` type and `getHColCode` from heal UI code, and formatting conventions used by quiet, JSON, and interactive heal displays.

## Risks and edge cases
Nil heal items return a grey/grey bucket result with an error. Invalid parity or surplus values bubble as errors, so display code must handle malformed server records. Metadata quorum math differs when `SetCount` is positive versus bucket-level healing.

## Test signals
Tests should exercise all heal item types, nil bucket input, missing/unavailable drives, object parity ranges, replicated metadata with and without set count, and unknown item types in name formatting.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-heal-result-item.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-heal-ui.go -->
# sources/object-store/minio-mc/cmd/admin-heal-ui.go

## Purpose
Provides the live, quiet, and JSON display engine for `mc admin heal` task progress. It aggregates heal result records into statistics and terminal UI output.

## Important APIs, types, and functions
Important symbols are `getHColCode`, `uiData`, `updateStats`, `getProgress`, `getPercentsNBars`, `printItemsQuietly`, `printItemsJSON`, `printStatsJSON`, `updateUI`, `UpdateDisplay`, `healResumeMsg`, and `DisplayAndFollowHealStatus`.

## Control flow
The follow loop repeatedly calls `AdminClient.Heal` with the stored client token, updates duration and accumulated stats from returned items, redraws the interactive UI unless quiet or JSON is selected, and exits on `finished`, `stopped`, or global context cancellation.

## State and persistence behavior
`uiData` stores transient counters: bytes scanned, objects/items scanned and healed, counts by online drives, health-color counts, last item, and elapsed duration. Persistent healing state remains on the server and is referenced by the client token.

## Dependencies and integration points
The file integrates `madmin.HealTaskStatus`, heal result helper methods, cursor animation, console rewind/table/color APIs, `colorjson`, humanized sizes, and the global JSON/quiet flags.

## Risks and edge cases
Color classification rejects parity outside 1..8 or surplus above parity. `getProgress` manually computes binary units and assumes an in-range magnitude. Display rewinds a fixed number of lines, so terminal layout changes are fragile. Context cancellation returns a resume hint as an error.

## Test signals
Tests should cover health-color table boundaries, stats accumulation for healed and non-healed items, JSON record shape, quiet output error fallback, final summary output, stopped task error propagation, and context cancellation resume text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-heal-ui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-heal.go -->
# sources/object-store/minio-mc/cmd/admin-heal.go

## Purpose
Implements `mc admin heal`, which reports background healing or starts, stops, and follows explicit heal operations over buckets, prefixes, pools, and sets.

## Important APIs, types, and functions
Key symbols include `adminHealFlags`, `adminHealCmd`, `checkAdminHealSyntax`, `stopHealMessage`, disk/server summary types, `generateSetsStatus`, `generateServersStatus`, `computePoolTolerance`, `verboseBackgroundHealStatusMessage`, `shortBackgroundHealStatusMessage`, `transformScanArg`, and `mainAdminHeal`.

## Control flow
The handler validates one target and scan mode, creates admin and object clients, parses bucket/prefix from the aliased URL, and branches. With no bucket and no recursive flag it fetches `BackgroundHealStatus` and prints short or verbose status. Otherwise it builds `madmin.HealOpts`, handles pool/set indexes, optionally stops a heal, prompts before full recursive namespace scans, starts healing, and hands the client token to `uiData.DisplayAndFollowHealStatus`.

## State and persistence behavior
Server-side healing tasks and background heal state are persistent operational state. Locally the command only tracks selected options, confirmation input, and the UI counters. `force-start`, `force-stop`, `remove`, `dry-run`, and `rewrite` directly affect server behavior.

## Dependencies and integration points
It integrates MinIO admin heal APIs, object URL parsing via `newClient`, terminal confirmation, hidden pool/set scan controls, global context, color themes, humanized summaries, and the heal UI/result helpers.

## Risks and edge cases
Full recursive healing is dangerous enough to require terminal confirmation unless `--force` is used. Pool and set flags are one-based externally and converted to zero-based pointers. Background tolerance calculations depend on parity and disk state accuracy. Some hidden flags have high operational impact.

## Test signals
Tests should cover syntax and scan validation, background status branches, verbose tolerance output, pool/set validation, force-stop payload, confirmation abort and proceed paths, heal option construction, token follow-up calls, and failure-detail tracing.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-heal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-idp.go -->
# sources/object-store/minio-mc/cmd/admin-idp.go

## Purpose
Keeps the deprecated `mc admin idp` command as a hidden compatibility entry point that directs users to the newer `mc idp ldap|openid` commands.

## Important APIs, types, and functions
`adminIDPCmd` defines a hidden command with custom deprecation help. `mainAdminIDP` calls `deprecatedError`.

## Control flow
Any invocation of the command bypasses old IDP management behavior and immediately emits the deprecation error pointing to the replacement command family.

## State and persistence behavior
No state is read or changed. The command intentionally prevents legacy configuration mutation through this path.

## Dependencies and integration points
It depends on the CLI command tree, global flags, `setGlobalsFromContext`, and the shared deprecation helper.

## Risks and edge cases
Hidden deprecated commands still occupy names in the admin namespace. If replacement command names change, this message must be updated to avoid stale guidance.

## Test signals
Tests should assert that `mc admin idp` is hidden, returns the deprecation path, and points to `mc idp ldap|openid`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-idp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-info.go -->
# sources/object-store/minio-mc/cmd/admin-info.go

## Purpose
Implements `mc admin info`, displaying cluster/server health, version, network, drive, pool, erasure, and usage summaries.

## Important APIs, types, and functions
Important symbols are `adminInfoCmd`, `poolSummary`, `clusterInfo`, `clusterSummaryInfo`, `endpointToPools`, `clusterStruct`, `checkAdminInfoSyntax`, and `mainAdminInfo`. The handler calls `ServerInfo`.

## Control flow
The command validates a single target, fetches `madmin.InfoMessage`, wraps errors into `clusterStruct`, and prints through `printMsg`. Human rendering sorts servers, formats offline nodes separately, prints uptime/version/network/drives/pools for online nodes, builds an erasure-pool summary table, and appends cluster usage and online/offline drive counts.

## State and persistence behavior
The command is read-only. It observes server-reported runtime state and stored usage counters. The `--offline` flag filters output locally by skipping online server details.

## Dependencies and integration points
It integrates `madmin.InfoMessage` backend helpers, MinIO set utilities, console tables and colors, humanize/english pluralization, global JSON rendering, and shared admin client creation.

## Risks and edge cases
The cluster summary assumes backend arrays line up with pool indexes. Offline-only mode can hide useful aggregate context for online nodes. Development versions are redacted as `<development>`. Missing server info triggers fatal behavior in `String`.

## Test signals
Tests should exercise JSON success and error output, offline-only filtering, erasure and non-erasure backends, offline server rendering, pool summary capacity math, version redaction, and total usage/pluralization formatting.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-inspect.go -->
# sources/object-store/minio-mc/cmd/admin-inspect.go

## Purpose
Maintains the deprecated hidden `mc admin inspect` command and redirects users to `mc support inspect`.

## Important APIs, types, and functions
`adminInspectCmd` defines the hidden command. `mainAdminInspect` calls `deprecatedError("mc support inspect")`.

## Control flow
The command does not perform inspection. All invocations route directly to the shared deprecation error.

## State and persistence behavior
No server or local state is accessed. The old admin inspection path is disabled in favor of the support command.

## Dependencies and integration points
It depends on `minio/cli`, global initialization, and deprecation plumbing. It remains registered under top-level admin for compatibility.

## Risks and edge cases
Because the command is hidden but still registered, stale documentation or scripts may still hit it. Replacement guidance must remain accurate.

## Test signals
Tests should verify hidden registration and that invocation returns the `mc support inspect` deprecation message without attempting admin API calls.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key-create.go -->
# sources/object-store/minio-mc/cmd/admin-kms-key-create.go

## Purpose
Implements `mc admin kms key create`, creating a new KMS master key by name.

## Important APIs, types, and functions
`adminKMSCreateKeyCmd` declares the command. `mainAdminKMSCreateKey` validates exactly two arguments, calls `newAdminClient`, invokes `CreateKey`, and conditionally prints terminal success.

## Control flow
The handler rejects invalid arity, creates an admin connection for the target, extracts the key ID, sends the create request, and prints a green success line only when stdout is a terminal.

## State and persistence behavior
The persistent mutation is remote KMS key creation through the MinIO admin API. No local state is stored, and non-terminal output is intentionally silent on success.

## Dependencies and integration points
It integrates KMS admin APIs, `probe` errors, terminal detection through `golang.org/x/term`, `os.Stdout`, and console/color output.

## Risks and edge cases
Quiet success for non-terminal stdout may surprise automation that expects a message. Key name validation is delegated to the server/KMS backend. Create is not idempotently handled locally.

## Test signals
Tests should cover arity checks, successful `CreateKey` invocation, server error propagation, terminal versus non-terminal success output, and names containing unusual but server-accepted characters.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key-create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key-list.go -->
# sources/object-store/minio-mc/cmd/admin-kms-key-list.go

## Purpose
Implements `mc admin kms key list`, listing KMS master keys known to the MinIO server.

## Important APIs, types, and functions
`adminKMSKeyListCmd` declares the command. `mainAdminKMSKeyList` calls `ListKeys(globalContext, "*")`. `kmsKeysMsg` serializes JSON and fallback string output.

## Control flow
The command accepts exactly one target, initializes an admin client, lists keys with a wildcard, builds table rows and a plain key-name slice, then either prints JSON via `printMsg` or renders a go-pretty table titled `KMS Keys`.

## State and persistence behavior
The command is read-only. It observes remote KMS key metadata but does not cache it locally.

## Dependencies and integration points
It depends on `madmin-go` KMS list APIs, `go-pretty/table`, global JSON mode, console colors, and shared error handling.

## Risks and edge cases
The table numbering is local and starts at one. Ordering follows the server response. Empty key lists render an empty table, while JSON renders an empty array.

## Test signals
Tests should validate one-argument syntax, wildcard list calls, JSON payload fields, table rendering for zero and multiple keys, and error handling when KMS is unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key-status.go -->
# sources/object-store/minio-mc/cmd/admin-kms-key-status.go

## Purpose
Implements `mc admin kms key status`, checking encryption and decryption availability for the default or named KMS key.

## Important APIs, types, and functions
`adminKMSKeyStatusCmd` defines command metadata. `mainAdminKMSKeyStatus` calls `GetKeyStatus`. `kmsKeyStatusMsg` renders key ID, encryption error, decryption error, and success status.

## Control flow
The command accepts target plus optional key name. It creates an admin client, requests key status, and prints a two-line capability view. If encryption failed, decryption status is shown as unknown because decryption cannot be meaningfully inferred.

## State and persistence behavior
No state is changed. The command reads runtime KMS connectivity and capability state from the server.

## Dependencies and integration points
It integrates `madmin-go` KMS status APIs, global output mode, `colorjson`, console color themes, and `probe` error handling.

## Risks and edge cases
An encryption failure masks decryption as unknown in human output even if a decryption error string is present. The default-key path uses an empty key ID, relying on server semantics.

## Test signals
Tests should cover target-only default key status, named key status, encryption success/failure, decryption failure, JSON status mutation to `success`, and invalid arity rejection.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key.go -->
# sources/object-store/minio-mc/cmd/admin-kms-key.go

## Purpose
Defines the `mc admin kms key` command group for KMS master key management.

## Important APIs, types, and functions
`adminKMSKeySubcommands` registers create, status, and list. `adminKMSKeyCmd` declares the group. `mainAdminKMSKey` delegates invalid invocations to `commandNotFound`.

## Control flow
No KMS operation is implemented directly. The file routes recognized subcommands and otherwise invokes the common command-not-found behavior.

## State and persistence behavior
No state is read or written here. Remote key state is handled by subcommand files.

## Dependencies and integration points
It depends on `minio/cli`, global flags, `setGlobalsFromContext`, sibling KMS command variables, and the parent `admin kms` group.

## Risks and edge cases
Registration drift is the main risk; new key operations must be added to this list. Hidden help behavior means not-found UX depends on shared infrastructure.

## Test signals
Tests should verify the key subcommands are reachable and that a bare or unknown `mc admin kms key` invocation routes to shared help/not-found behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms-key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms.go -->
# sources/object-store/minio-mc/cmd/admin-kms.go

## Purpose
Defines the top-level `mc admin kms` command group for KMS management operations.

## Important APIs, types, and functions
`adminKMSSubcommands` currently contains `adminKMSKeyCmd`. `adminKMSCmd` registers the group, and `mainAdminKMS` delegates unknown subcommands to `commandNotFound`.

## Control flow
The file acts as a namespace router. All behavior is delegated to `mc admin kms key ...` commands.

## State and persistence behavior
No local or remote state is accessed directly.

## Dependencies and integration points
It integrates with the top-level admin command, `minio/cli`, global flags, and the KMS key command group.

## Risks and edge cases
Future KMS subcommands require updates here. Since only one subcommand exists, users invoking `kms` directly rely on the quality of command-not-found/help output.

## Test signals
Registration tests should confirm `mc admin kms key` is reachable and bare or invalid `kms` invocations produce the common not-found path.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-kms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-logs.go -->
# sources/object-store/minio-mc/cmd/admin-logs.go

## Purpose
Implements `mc admin logs`, streaming MinIO server log entries, optionally filtered by node, last count, and log type.

## Important APIs, types, and functions
Key symbols include `logsShowFlags`, `adminLogsCmd`, `checkLogsShowSyntax`, `logMessage`, `getLogTime`, and `mainAdminLogs`. It calls `AdminClient.GetLogs`.

## Control flow
The handler validates arguments, configures colors, parses target and optional node, validates `--last` and `--type`, creates an admin client, opens a cancelable context, then ranges over the log channel. Each successful record with a deployment ID is printed; node names are suppressed when a specific node was requested.

## State and persistence behavior
This command is read-only and streaming. It holds transient context state and reads server logs; it does not persist log data locally.

## Dependencies and integration points
It integrates `madmin.LogInfo`, shared HTTP/admin client setup, global output mode, colorized node names, API/trace formatting, and `probe` fatal handling for stream errors.

## Risks and edge cases
`checkLogsShowSyntax` allows up to three args although usage documents target plus optional node. A `last` flag is only validated when explicitly set, leaving value zero for unlimited/default server behavior. Logs without deployment IDs are dropped.

## Test signals
Tests should cover type validation, positive `--last` validation, node-name suppression, time parsing fallback, trace variable/source formatting, JSON output, stream error handling, and context cancellation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-main.go -->
# sources/object-store/minio-mc/cmd/admin-main.go

## Purpose
Defines the root `mc admin` command and registers the full MinIO server administration command set.

## Important APIs, types, and functions
`adminCmdSubcommands` lists service, update, info, inspect, user, group, policy, replicate, idp, config, decommission, heal, prometheus, kms, health, subnet, bucket, tier, speedtest, profile, scanner, top, trace, console, cluster, rebalance, logs, and accesskey commands. Constants `dot`, `check`, and `dateTimeFormatFilename` provide shared display symbols and filename timestamp format.

## Control flow
The root command invokes `mainAdmin` only when no subcommand handles the invocation. `mainAdmin` delegates to `commandNotFound`, while recognized subcommands own all operational flow.

## State and persistence behavior
This file has no state mutation. It only composes the admin CLI surface and shared flags.

## Dependencies and integration points
It is the integration point for all admin subcommand variables in the `cmd` package and for global option initialization via `setGlobalsFromContext`.

## Risks and edge cases
The command list is a large manual registry; omissions make commands unreachable. Hidden or deprecated commands remain in the namespace for compatibility. Display constants are reused by multiple status formatters.

## Test signals
Tests should verify top-level registration of key command families, correct command-not-found behavior, and that shared flags are present on the root admin command.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-add.go -->
# sources/object-store/minio-mc/cmd/admin-policy-add.go

## Purpose
Preserves the deprecated hidden `mc admin policy add` command and redirects users to `mc admin policy create`.

## Important APIs, types, and functions
`adminPolicyAddCmd` is hidden and uses `mainAdminPolicyAdd`. The handler calls `deprecatedError("mc admin policy create")`.

## Control flow
All invocations immediately emit the deprecation path. No old policy creation API is called.

## State and persistence behavior
No state is read or changed. Policy mutation is intentionally moved to the create command.

## Dependencies and integration points
The file depends on the CLI package, global setup, and shared deprecation helper, and is registered in the policy command group for compatibility.

## Risks and edge cases
Scripts using the old command name will fail with deprecation guidance. The replacement command string must stay synchronized with the active policy command.

## Test signals
Tests should assert the command is hidden, registered, and produces the `mc admin policy create` deprecation message without admin client creation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-attach.go -->
# sources/object-store/minio-mc/cmd/admin-policy-attach.go

## Purpose
Implements `mc admin policy attach` and the shared attach/detach helper for associating IAM policies with a user or group.

## Important APIs, types, and functions
`adminAttachPolicyFlags` defines `--user` and `--group`. `adminPolicyAttachCmd` uses `mainAdminPolicyAttach`, which calls `userAttachOrDetachPolicy(ctx, true)`. The helper builds `madmin.PolicyAssociationReq` and calls either `AttachPolicy` or `DetachPolicy`.

## Control flow
The helper requires target plus at least one policy. It reads user/group flags, treats all remaining args as policies, creates an admin client, calls the chosen association API, tolerates `XMinioAdminPolicyChangeAlreadyApplied`, backfills a response for older servers that returned no timestamp, and prints `policyAssociationMessage`.

## State and persistence behavior
The persistent effect is changing MinIO IAM policy associations for a user or group. Local state is limited to the request and compatibility response construction.

## Dependencies and integration points
It integrates `madmin-go` IAM association APIs, server error-code translation, global context, shared policy output types, and the detach command's implementation.

## Risks and edge cases
The help says exactly one of user or group is required, but this helper does not locally enforce exclusivity; it relies on server behavior. Compatibility backfill may hide old-server response differences. Already-applied changes are treated as success.

## Test signals
Tests should cover attach and detach modes, multiple policy args, user/group flag combinations, already-applied errors, old-server empty responses, and fatal behavior for real API failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-create.go -->
# sources/object-store/minio-mc/cmd/admin-policy-create.go

## Purpose
Implements `mc admin policy create`, uploading a canned IAM policy JSON document to a MinIO server.

## Important APIs, types, and functions
`adminPolicyCreateCmd` declares the command. `checkAdminPolicyCreateSyntax` requires target, policy name, and policy file. `userPolicyMessage` formats create/list/info/remove/legacy attach/detach messages. `mainAdminPolicyCreate` reads the policy file and calls `AddCannedPolicy`.

## Control flow
The handler validates arity, sets output color, reads the policy JSON from disk using `os.ReadFile`, opens an admin client, sends the bytes to `AddCannedPolicy`, and prints a success message naming the policy.

## State and persistence behavior
Remote IAM policy state is created or replaced according to server semantics. The command reads a local policy file but does not persist local output.

## Dependencies and integration points
It integrates local filesystem input, MinIO admin canned-policy APIs, `probe` tracing over CLI args, global context, console colors, and shared policy message serialization.

## Risks and edge cases
Policy JSON validation is delegated to the server; local code only reads bytes. Large or unreadable files fail before the admin call. `userPolicyMessage` is shared, so changes can affect unrelated policy subcommands.

## Test signals
Tests should cover arity validation, unreadable file errors, successful byte payload to `AddCannedPolicy`, JSON and human output, and invalid policy document server errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-detach.go -->
# sources/object-store/minio-mc/cmd/admin-policy-detach.go

## Purpose
Defines `mc admin policy detach`, detaching one or more policies from a user or group through the shared policy association helper.

## Important APIs, types, and functions
`adminDetachPolicyFlags` mirrors attach flags for `--user` and `--group`. `adminPolicyDetachCmd` points to `mainAdminPolicyDetach`, which calls `userAttachOrDetachPolicy(ctx, false)`.

## Control flow
The file delegates all validation and server interaction to the helper in `admin-policy-attach.go`. The helper selects `DetachPolicy`, handles already-applied responses, and prints an association message.

## State and persistence behavior
The resulting command mutates server-side IAM policy associations by removing mappings from the selected user or group.

## Dependencies and integration points
It depends on the attach helper, global flags, CLI command registration, and shared policy output types.

## Risks and edge cases
Attach and detach share validation gaps around user/group exclusivity. Any helper change affects both commands. The short local file can be missed by tests if only attach is covered.

## Test signals
Tests should verify detach command registration, flag names, dispatch with `attach=false`, multiple policy support, and old-server response backfill for detached policies.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-detach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-entities.go -->
# sources/object-store/minio-mc/cmd/admin-policy-entities.go

## Purpose
Implements `mc admin policy entities`, listing policy associations for selected users, groups, policies, or all entities.

## Important APIs, types, and functions
`adminPolicyEntitiesFlags` provides string-slice `--user`, `--group`, and `--policy`. `mainAdminPolicyEntities` builds `madmin.PolicyEntitiesQuery` and calls `GetPolicyEntities`, then prints `policyEntitiesFrom(res)`.

## Control flow
The handler requires exactly one target alias. It reads repeated query flags, creates an admin client, requests association entities from the server, and delegates output shaping to the existing policy-entities renderer.

## State and persistence behavior
This is read-only. It observes IAM association metadata and does not modify policies, users, or groups.

## Dependencies and integration points
It integrates the MinIO admin policy-entities API, CLI string-slice flags, global context, `probe` errors, and renderer helpers defined elsewhere in the command package.

## Risks and edge cases
The command allows all three query dimensions together, relying on server semantics for intersection/union behavior. Empty flag lists mean all relevant associations. Output details depend on `policyEntitiesFrom`, not this file.

## Test signals
Tests should cover one-target syntax, repeated flags, empty query lists, server errors, and output conversion for user, group, and policy association results.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-entities.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-info.go -->
# sources/object-store/minio-mc/cmd/admin-policy-info.go

## Purpose
Implements `mc admin policy info`, retrieving a canned IAM policy and optionally writing its JSON document to a local file.

## Important APIs, types, and functions
Important symbols are `policyInfoFlags`, `adminPolicyInfoCmd`, `checkAdminPolicyInfoSyntax`, `getPolicyInfo`, and `mainAdminPolicyInfo`. `getPolicyInfo` first calls `InfoCannedPolicyV2` and falls back to deprecated `InfoCannedPolicy` when needed.

## Control flow
The handler validates target and policy name, creates an admin client, fetches policy metadata through the compatibility helper, optionally creates and writes a `--policy-file`, then prints `userPolicyMessage` with the full `madmin.PolicyInfo`.

## State and persistence behavior
Server IAM policy state is read. If `--policy-file` is set, local filesystem state is overwritten/created with the policy bytes.

## Dependencies and integration points
It integrates new and old MinIO canned-policy APIs, local file output, global context, console colors, and shared policy serialization.

## Risks and edge cases
`os.Create` truncates existing policy files. The fallback path is necessary for older servers and should not be removed without compatibility review. File close errors are not explicitly checked.

## Test signals
Tests should cover V2 success, old-server fallback, nonexistent policy errors, policy-file creation/write failures, JSON policy info output, and exact two-argument syntax.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-list.go -->
# sources/object-store/minio-mc/cmd/admin-policy-list.go

## Purpose
Implements `mc admin policy list`/`ls`, listing all canned IAM policies on a MinIO server.

## Important APIs, types, and functions
`adminPolicyListCmd` declares the command. `checkAdminPolicyListSyntax` requires one target. `mainAdminPolicyList` calls `ListCannedPolicies` and prints each policy name via `userPolicyMessage`.

## Control flow
The handler validates the alias, opens an admin client, retrieves the map of policies, then iterates map keys and prints one message per policy.

## State and persistence behavior
This command is read-only. It observes server IAM policy names and does not inspect or write local policy files.

## Dependencies and integration points
It depends on the MinIO admin canned-policy list API, shared policy output message, console colors, global context, and `probe` errors.

## Risks and edge cases
Map iteration order is not deterministic, so human output order may vary. Empty policy maps produce no human lines. The comment incorrectly references policy add, which can mislead maintainers.

## Test signals
Tests should cover syntax validation, empty and populated maps, JSON per-message rendering, non-deterministic order tolerance, and server API errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-remove.go -->
# sources/object-store/minio-mc/cmd/admin-policy-remove.go

## Purpose
Implements `mc admin policy remove`/`rm`, deleting a canned IAM policy from a MinIO server.

## Important APIs, types, and functions
`adminPolicyRemoveCmd` declares the command. `checkAdminPolicyRemoveSyntax` requires target and policy name. `mainAdminPolicyRemove` calls `RemoveCannedPolicy` and prints `userPolicyMessage`.

## Control flow
After validation, the handler sets output color, creates an admin client, invokes the server removal API with the policy argument, and prints a success message.

## State and persistence behavior
The persistent mutation is removal of server-side IAM policy definition. Local state is not changed.

## Dependencies and integration points
It integrates MinIO canned-policy removal, global context, shared policy formatting, console colors, and `probe` error tracing.

## Risks and edge cases
The command does not locally check whether the policy is attached to entities; server behavior controls failure or cascading semantics. There is no confirmation prompt.

## Test signals
Tests should cover arity validation, successful API invocation, nonexistent/in-use policy failures, short-name registration, and JSON/human success output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-set.go -->
# sources/object-store/minio-mc/cmd/admin-policy-set.go

## Purpose
Keeps the deprecated hidden `mc admin policy set` command and redirects users to `mc admin policy attach`.

## Important APIs, types, and functions
`adminPolicySetCmd` defines the hidden command and `mainAdminPolicySet` calls `deprecatedError("mc admin policy attach")`.

## Control flow
No legacy policy mapping behavior remains. Invocation immediately emits deprecation guidance.

## State and persistence behavior
No server or local state is changed. Policy association mutation is handled by the attach command.

## Dependencies and integration points
It depends on the CLI command registry and shared deprecation helper, and is included in `adminPolicySubcommands` for compatibility.

## Risks and edge cases
Legacy scripts must migrate. The command name is still reserved, so future reuse would require compatibility care.

## Test signals
Tests should verify hidden registration and deprecation output pointing to `mc admin policy attach`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-unset.go -->
# sources/object-store/minio-mc/cmd/admin-policy-unset.go

## Purpose
Keeps the deprecated hidden `mc admin policy unset` command and redirects users to `mc admin policy detach`.

## Important APIs, types, and functions
`adminPolicyUnsetCmd` defines command metadata. `mainAdminPolicyUnsetErr` invokes `deprecatedError("mc admin policy detach")`.

## Control flow
The command always follows the deprecation path and performs no policy detachment itself.

## State and persistence behavior
No state is read or written. Active policy detachment is implemented by `admin-policy-detach.go`.

## Dependencies and integration points
It depends on CLI registration, global setup, and the shared deprecation mechanism.

## Risks and edge cases
Deprecated hidden commands can still be invoked by automation. Replacement guidance must remain accurate.

## Test signals
Tests should assert hidden command metadata and deprecation output for `mc admin policy detach`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-unset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-update.go -->
# sources/object-store/minio-mc/cmd/admin-policy-update.go

## Purpose
Keeps the deprecated hidden `mc admin policy update` command and redirects users to `mc admin policy attach`.

## Important APIs, types, and functions
`adminPolicyUpdateCmd` declares the hidden command. `mainAdminPolicyUpdateErr` calls `deprecatedError("mc admin policy attach")`.

## Control flow
All invocations terminate through deprecation handling; no policy update API is called.

## State and persistence behavior
No local or remote state is modified.

## Dependencies and integration points
It integrates with policy command registration and shared deprecation messaging.

## Risks and edge cases
The command's legacy wording says attach a new policy, but modern behavior is a hard redirect. Stale scripts need migration.

## Test signals
Tests should verify hidden registration and that invocation produces the attach deprecation guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy-update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy.go -->
# sources/object-store/minio-mc/cmd/admin-policy.go

## Purpose
Defines the `mc admin policy` command group for managing MinIO server IAM policies and their associations.

## Important APIs, types, and functions
`adminPolicySubcommands` registers create, remove, list, info, attach, detach, entities, and deprecated add/set/unset/update entries. `adminPolicyCmd` defines the group. `mainAdminPolicy` delegates to `commandNotFound`.

## Control flow
The file routes recognized policy subcommands. Bare or invalid invocations enter the shared command-not-found path.

## State and persistence behavior
No state is accessed here. Policy creation, removal, association, and queries happen in subcommand files.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling command variables, and the top-level admin command registry.

## Risks and edge cases
Manual subcommand registration can drift from implemented files. Deprecated commands remain present but hidden, which affects command discovery and compatibility.

## Test signals
Tests should verify active and deprecated policy subcommands are registered, aliases work where defined, and bare `mc admin policy` uses common not-found/help behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-profile-start.go -->
# sources/object-store/minio-mc/cmd/admin-profile-start.go

## Purpose
Maintains the deprecated hidden `mc admin profile start` command and redirects to `mc support profile start`.

## Important APIs, types, and functions
`adminProfileStartCmd` defines command metadata. `mainAdminProfileStart` calls `deprecatedError("mc support profile start")`.

## Control flow
The command performs no profiling action. Invocation immediately reports the replacement command.

## State and persistence behavior
No profiling state is started locally or remotely through this path.

## Dependencies and integration points
It depends on CLI registration, global setup, and the deprecation helper. It is a subcommand of the hidden admin profile group.

## Risks and edge cases
Legacy automation will no longer start profiles through `mc admin`. Replacement guidance must track the support command.

## Test signals
Tests should verify hidden command metadata and deprecation output pointing to `mc support profile start`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-profile-start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-profile-stop.go -->
# sources/object-store/minio-mc/cmd/admin-profile-stop.go

## Purpose
Maintains the deprecated hidden `mc admin profile stop` command and redirects to `mc support profile stop`.

## Important APIs, types, and functions
`adminProfileStopCmd` defines command metadata with global flags. `mainAdminProfileStop` calls `deprecatedError("mc support profile stop")`.

## Control flow
The command does not stop or download profile data. It immediately emits replacement-command guidance.

## State and persistence behavior
No profile collection state or local profile files are touched.

## Dependencies and integration points
It depends on CLI registration, global flags, and shared deprecation plumbing.

## Risks and edge cases
Keeping global flags on a deprecated command may imply old behavior still exists. Scripts must migrate to support commands.

## Test signals
Tests should assert hidden registration and the exact replacement target in the deprecation message.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-profile-stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-profile.go -->
# sources/object-store/minio-mc/cmd/admin-profile.go

## Purpose
Defines the deprecated hidden `mc admin profile` command group and redirects users to `mc support profile`.

## Important APIs, types, and functions
`adminProfileSubcommands` includes deprecated start and stop commands. `adminProfileCmd` is hidden. `mainAdminProfile` calls `deprecatedError("mc support profile")`.

## Control flow
Bare group invocation emits group-level deprecation guidance. Start and stop have their own deprecation handlers.

## State and persistence behavior
No profiling state is created, stopped, or downloaded by this group.

## Dependencies and integration points
It integrates with the admin command registry, `minio/cli`, global flags, and deprecation helpers.

## Risks and edge cases
The group remains in the command tree for compatibility while being hidden. New profile functionality should not be added here.

## Test signals
Tests should verify group and subcommands are hidden and all invocations point to the corresponding `mc support profile` replacement.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus-generate.go -->
# sources/object-store/minio-mc/cmd/admin-prometheus-generate.go

## Purpose
Implements `mc admin prometheus generate`, producing Prometheus scrape configuration for MinIO metrics endpoints.

## Important APIs, types, and functions
Important symbols are `defaultJobName`, `metricsV2BasePath`, `prometheusFlags`, `adminPrometheusGenerateCmd`, `PrometheusConfig`, `StatConfig`, `ScrapeConfig`, `checkAdminPrometheusSyntax`, `generatePrometheusConfig`, and `mainAdminPrometheusGenerate`.

## Control flow
The handler validates target plus optional metric type, cleans and validates the alias, reads host config, parses its URL, chooses v2 or v3 metrics path and job name, optionally generates a bearer token, fills scheme and host target, and prints YAML or JSON through `printMsg`.

## State and persistence behavior
No repo or server state is persisted. It reads local alias configuration and may generate a long-lived Prometheus JWT unless `--public` is used.

## Dependencies and integration points
It integrates alias config lookup, Prometheus token generation, v2/v3 metrics validators, YAML/JSON serialization, console colorization, and global output flags.

## Risks and edge cases
The generated default token expiry is very long. `--public` omits bearer token and assumes public metrics access. v2 rejects v3-only flags, and v3 bucket paths are limited to specific subsystems.

## Test signals
Tests should cover invalid aliases, missing host config, v2 default and subsystem paths, v3 default/subsystem/bucket paths, public token omission, YAML and JSON output, and invalid API version handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus-generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus-metrics-v3.go -->
# sources/object-store/minio-mc/cmd/admin-prometheus-metrics-v3.go

## Purpose
Provides v3 Prometheus metrics path construction, validation, and fetching for `mc admin prometheus metrics`.

## Important APIs, types, and functions
`metricsV3Flags` defines `--bucket`. `metricsV3SubSystems` and `bucketMetricsSubSystems` validate subsystem names. `getMetricsV3Path`, `validateV3Args`, and `printPrometheusMetricsV3` implement the behavior.

## Control flow
`getMetricsV3Path` builds `/minio/metrics/v3`, optionally adds `/bucket`, subsystem, and bucket name. `validateV3Args` rejects unknown subsystems and ensures bucket metrics are only requested with supported subsystems. `printPrometheusMetricsV3` fetches the URL and prints the body on HTTP 200.

## State and persistence behavior
The file is read-only and stateless. It streams metrics from the server without local persistence.

## Dependencies and integration points
It integrates the shared metrics request struct, `fetchMetrics`, `prometheusMetricsReader`, CLI bucket flag, HTTP status handling, and MinIO set utilities.

## Risks and edge cases
Bucket names are inserted into the path without URL escaping in this helper, so unusual bucket strings rely on prior CLI/server constraints. Non-200 responses return only status text. Empty subsystem means all v3 metrics unless a bucket is specified.

## Test signals
Tests should cover path construction for all/bucket/subsystem variants, invalid subsystem messages, bucket-without-subsystem rejection, unsupported bucket subsystem rejection, HTTP 200 streaming, and non-200 errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus-metrics-v3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus-metrics.go -->
# sources/object-store/minio-mc/cmd/admin-prometheus-metrics.go

## Purpose
Implements `mc admin prometheus metrics`, fetching raw Prometheus metrics from MinIO v2 or v3 endpoints and optionally converting them to JSON.

## Important APIs, types, and functions
Key symbols include `metricsFlags`, `metricsV2SubSystems`, `adminPrometheusMetricsCmd`, `prometheusMetricsReq`, `checkSupportMetricsSyntax`, `fetchMetrics`, `validateV2Args`, `printPrometheusMetricsV2`, `prometheusMetricsReader`, and `mainSupportMetrics`.

## Control flow
The handler validates target plus optional metric type, resolves local alias config, obtains a Prometheus bearer token, builds a request object, and dispatches to v2 or v3 printing. V2 defaults to cluster metrics and rejects v3-only flags. Successful responses stream the body; JSON mode parses Prometheus results before marshaling.

## State and persistence behavior
No state is modified. The command reads local alias configuration and remote metrics, and streams data to stdout.

## Dependencies and integration points
It uses `httpClient`, bearer-token auth, `madmin.ParsePrometheusResults`, global JSON mode, v3 helpers, v2 subsystem validation, and shared fatal/probe error handling.

## Risks and edge cases
Metrics streaming writes directly to stdout in string mode, making output handling unusual for `String`. Non-200 responses lose response body details. Token generation failures stop the command before any HTTP call.

## Test signals
Tests should cover syntax, alias validation, missing alias config, v2 default and invalid subsystem, v3 dispatch, bearer header injection, JSON parse failures, non-200 status errors, and raw body streaming.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus-metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus.go -->
# sources/object-store/minio-mc/cmd/admin-prometheus.go

## Purpose
Defines the `mc admin prometheus` command group for metrics configuration generation and metrics printing.

## Important APIs, types, and functions
`adminPrometheusSubcommands` registers generate and metrics. `adminPrometheusCmd` defines the group. `mainAdminPrometheus` calls `commandNotFound` for invalid invocations.

## Control flow
The group routes recognized subcommands. Bare or unknown invocations use the common not-found/help path.

## State and persistence behavior
This file has no state behavior. Subcommands read local alias config and remote metrics as needed.

## Dependencies and integration points
It integrates with the top-level admin command, global flags, and the generate/metrics command files.

## Risks and edge cases
New Prometheus subcommands require updating this registry. The group help is sparse, so subcommand help carries most user guidance.

## Test signals
Tests should verify generate and metrics are reachable and that invalid subcommands route through `commandNotFound`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-prometheus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-main.go -->
# sources/object-store/minio-mc/cmd/admin-rebalance-main.go

## Purpose
Defines the `mc admin rebalance` command group for starting, stopping, and inspecting MinIO rebalance operations.

## Important APIs, types, and functions
`adminRebalanceSubcommands` registers start, status, and stop. `adminRebalanceCmd` declares the group. `mainAdminRebalance` delegates invalid invocations to `commandNotFound`.

## Control flow
No rebalance API is called directly here. The file provides command routing and common global setup.

## State and persistence behavior
No state is read or mutated in this file; rebalance state lives on the server and is handled by subcommands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling rebalance command variables, and top-level admin registration.

## Risks and edge cases
Manual registry drift can make lifecycle operations unreachable. The group hides the help command, so shared not-found output is important.

## Test signals
Tests should verify start/status/stop registration and common behavior for bare or unknown `mc admin rebalance` invocations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-start.go -->
# sources/object-store/minio-mc/cmd/admin-rebalance-start.go

## Purpose
Implements `mc admin rebalance start`, initiating a MinIO rebalance operation for a deployment.

## Important APIs, types, and functions
`adminRebalanceStartCmd` defines the command. `rebalanceStartMsg` serializes success output. `mainAdminRebalanceStart` calls `RebalanceStart`.

## Control flow
The handler requires exactly one alias, creates an admin client, starts rebalance through the server API, and prints a success message containing the target and returned rebalance ID.

## State and persistence behavior
The persistent state change is server-side creation/start of a rebalance operation. The returned ID is only displayed locally.

## Dependencies and integration points
It integrates `madmin-go` rebalance APIs, global context, console colors, `probe` errors, and global JSON output.

## Risks and edge cases
The help template contains `xEXAMPLES`, likely a typo. The human message does not include the rebalance ID, while JSON does. Existing rebalance conflicts are handled only by the server.

## Test signals
Tests should cover single-argument validation, client initialization failure, server start error, JSON ID output, and human success rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-status.go -->
# sources/object-store/minio-mc/cmd/admin-rebalance-status.go

## Purpose
Implements `mc admin rebalance status`, summarizing per-pool and aggregate progress for an ongoing rebalance.

## Important APIs, types, and functions
`adminRebalanceStatusCmd` defines the command. `mainAdminRebalanceStatus` calls `RebalanceStatus`, uses `console.NewTable`, `humanize.IBytes`, and aggregates progress fields.

## Control flow
The handler validates a single alias, creates an admin client, fetches rebalance info, returns raw JSON when requested, otherwise renders a per-pool usage table. It marks pools with status `Started`, sums bytes/objects/versions, tracks maximum elapsed and ETA, and prints a summary.

## State and persistence behavior
The command is read-only. It observes server-side rebalance progress and does not persist local state.

## Dependencies and integration points
It integrates admin rebalance status APIs, standard `encoding/json` for raw JSON, console tables/colors, humanized byte formatting, and global context.

## Risks and edge cases
Column headers are zero-based (`Pool-0`) while other commands often display one-based pool ordinals. Empty pool lists produce empty table inputs. Summary ETA chooses the maximum ETA across pools.

## Test signals
Tests should cover JSON output, per-pool table output, started marker, aggregate totals, max elapsed/ETA selection, client initialization errors, and empty or completed rebalance states.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-stop.go -->
# sources/object-store/minio-mc/cmd/admin-rebalance-stop.go

## Purpose
Implements `mc admin rebalance stop`, stopping an ongoing MinIO rebalance operation.

## Important APIs, types, and functions
`adminRebalanceStopCmd` defines the command. `rebalanceStopMsg` handles JSON and human success messages. `mainAdminRebalanceStop` calls `RebalanceStop`.

## Control flow
The handler validates exactly one alias, creates an admin client, invokes the stop API, and prints a target-specific success message.

## State and persistence behavior
The persistent mutation is server-side transition of rebalance state toward stopped/canceled. No local state is stored.

## Dependencies and integration points
It depends on MinIO admin rebalance APIs, global context, console color setup, `colorjson`, and `probe` error wrapping.

## Risks and edge cases
Stopping when no rebalance is active is left to server error semantics. Human output does not include a rebalance ID.

## Test signals
Tests should cover arity validation, client failure, stop API failure, JSON status/target output, and human success output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-rebalance-stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-add.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-add.go

## Purpose
Implements `mc admin replicate add`, configuring cluster-level site replication across two or more MinIO aliases.

## Important APIs, types, and functions
`adminReplicateAddFlags` defines `--replicate-ilm-expiry`. `successMessage` wraps `madmin.ReplicateAddStatus`. `mainAdminReplicateAdd` builds `madmin.PeerSite` entries and calls `SiteReplicationAdd`.

## Control flow
The command requires at least two aliases. It creates an admin client for the first alias, then creates admin clients for every provided alias to extract endpoint URL and access/secret keys. It sends the peer list plus `SRAddOptions` to the first site's admin API and prints status, error detail, and initial sync messages.

## State and persistence behavior
The persistent effect is server-side site replication configuration, including credentials and optional ILM expiry replication. Local credentials are transient in memory.

## Dependencies and integration points
It integrates alias credential resolution, `madmin-go` site replication add APIs, global context, colorized user messages, and JSON serialization.

## Risks and edge cases
Every alias must be configured and accessible locally before the server call. Passing credentials from each alias is sensitive. Partial initial-sync errors can appear in a success response and must be visible.

## Test signals
Tests should cover minimum argument enforcement, peer-site payload construction, ILM expiry flag propagation, credential extraction, server error handling, and output containing `ErrDetail`/`InitialSyncErrorMessage`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-info.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-info.go

## Purpose
Implements `mc admin replicate info`, displaying cluster-level site replication configuration and peer details.

## Important APIs, types, and functions
`adminReplicateInfoCmd` declares the command. `srInfo` wraps `madmin.SiteReplicationInfo` and renders JSON or a table of deployment ID, site name, endpoint, sync state, bandwidth, and ILM expiry replication.

## Control flow
The handler requires exactly one alias, configures table colors, creates an admin client, calls `SiteReplicationInfo`, and prints `srInfo`. Human output shows a disabled message or a two-line header plus one row per peer.

## State and persistence behavior
This command is read-only. It observes site replication metadata stored by the server.

## Dependencies and integration points
It integrates MinIO site replication APIs, pretty-table helpers from the command package, humanized bandwidth formatting, sync-state constants, and global JSON mode.

## Risks and edge cases
The endpoint column uses fixed widths and can truncate or misalign long URLs. A zero bandwidth limit is shown as `N/A`, which means no cluster bandwidth configured rather than unknown.

## Test signals
Tests should cover enabled and disabled replication, peer row formatting, sync check marker, bandwidth formatting, ILM expiry boolean output, JSON serialization, and arity validation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-remove.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-remove.go

## Purpose
Implements `mc admin replicate remove`/`rm`, removing selected sites or all sites from site replication configuration.

## Important APIs, types, and functions
`adminReplicateRemoveFlags` defines `--all` and `--force`. `srRemoveStatus` wraps `madmin.ReplicateRemoveStatus`. `checkAdminReplicateRemoveSyntax` enforces dangerous-operation constraints. `mainAdminReplicationRemoveStatus` calls `SiteReplicationRemove`.

## Control flow
The syntax checker rejects `--all` with extra site args, requires sites unless `--all`, and requires `--force` for all removals. The handler builds `madmin.SRRemoveReq`, calls the server, and prints a full, partial, or all-sites success message.

## State and persistence behavior
The persistent mutation is removal of site replication configuration from the active cluster or all participating sites, depending on request flags.

## Dependencies and integration points
It integrates MinIO site replication removal APIs, global context, colorized output, JSON serialization, and CLI dangerous-operation safeguards.

## Risks and edge cases
The operation is irreversible and only protected by `--force`; there is no interactive prompt. Partial failures are reported through status detail and must be surfaced to users.

## Test signals
Tests should cover `--force` requirement, `--all` exclusivity, site list requirements, payload construction, full and partial response messages, JSON output, and server failure propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync-cancel.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-resync-cancel.go

## Purpose
Implements `mc admin replicate resync cancel`, canceling an ongoing resync operation from one replicated site to another.

## Important APIs, types, and functions
`adminReplicateResyncCancelCmd` defines the command. `resyncCancelMessage` wraps `madmin.SRResyncOpStatus`. `mainAdminReplicateResyncCancel` calls `SiteReplicationInfo`, peer `ServerInfo`, and `SiteReplicationResyncOp` with `SiteResyncCancel`.

## Control flow
The command requires source and peer aliases. It fetches replication info from the source, gets the peer deployment ID through `getClient(...).ServerInfo`, matches that ID to a configured peer, rejects non-members, sends the cancel operation, and prints success or error detail.

## State and persistence behavior
The persistent state change is server-side cancellation of a resync identified by the peer deployment. Local state is transient peer lookup data.

## Dependencies and integration points
It integrates site replication metadata, peer client/server info APIs, resync operation constants, global context, and shared console/JSON output.

## Risks and edge cases
Peer matching depends on deployment IDs rather than alias names. If the peer is unreachable, cancellation cannot proceed. The `ResyncErr` color is not set in this file, unlike start.

## Test signals
Tests should cover arity validation, peer deployment matching, non-member rejection, source or peer API failures, cancel operation payload, success message with resync ID, and error-detail output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync-cancel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync-start.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-resync-start.go

## Purpose
Implements `mc admin replicate resync start`, starting a bucket-data resync toward a peer site.

## Important APIs, types, and functions
`adminReplicateResyncStartCmd` defines the command. `resyncMessage` wraps `madmin.SRResyncOpStatus`. `mainAdminReplicateResyncStart` uses `SiteReplicationInfo`, peer `ServerInfo`, and `SiteReplicationResyncOp` with `SiteResyncStart`.

## Control flow
The command requires source and peer aliases. It opens the source admin client, fetches configured sites, obtains peer deployment ID from the peer alias, finds the matching `PeerInfo`, rejects aliases outside replication, starts resync, and prints the returned resync ID or error detail.

## State and persistence behavior
The persistent effect is a server-side resync job for the selected peer deployment. Local state is limited to lookup and output.

## Dependencies and integration points
It integrates source and peer admin clients, site replication info, resync operation constants, global context, and colorized/JSON status output.

## Risks and edge cases
Alias names are not trusted; deployment ID matching is authoritative. Unreachable peer aliases prevent lookup. The command does not accept bucket filters; resync scope is determined by server API semantics.

## Test signals
Tests should cover exactly two arguments, peer matching, non-member failure, resync start API errors, returned resync ID output, and error-detail rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync-start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync-status.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-resync-status.go

## Purpose
Implements `mc admin replicate resync status`, showing real-time resync metrics for a replicated peer site.

## Important APIs, types, and functions
Important symbols include `adminReplicateResyncStatusCmd`, `mainAdminReplicationResyncStatus`, `initResyncMetricsUI`, `resyncMetricsUI`, and its Bubble Tea `Init`, `Update`, and `View` methods.

## Control flow
The handler validates source and peer aliases, fetches site replication info, resolves the peer by deployment ID, starts a cancelable metrics stream filtered with `madmin.MetricsSiteResync` and `ByDepID`, and either prints JSON metrics or sends `SiteResyncMetrics` into an interactive Bubble Tea UI until complete, canceled, or interrupted.

## State and persistence behavior
The command is read-only against server resync state. Local UI state stores the current metrics snapshot, spinner, quitting flag, and peer deployment ID.

## Dependencies and integration points
It integrates MinIO realtime metrics APIs, `metricsMessage` from scanner status for JSON output, Bubble Tea, bubbles spinner, lipgloss styles, tablewriter, humanized byte rates, global context, and peer resolution from replication info.

## Risks and edge cases
The disabled-replication branch colorizes a string but does not print it. Versions display uses `ReplicatedCount`, which may be intentional or a bug if versions differ. UI and metrics goroutine coordination relies on context cancellation.

## Test signals
Tests should cover peer lookup, disabled replication behavior, JSON streaming, UI update on complete/canceled metrics, ctrl-c handling, throughput calculation with elapsed time, and non-canceled metrics errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-resync.go

## Purpose
Defines the `mc admin replicate resync` subcommand group for starting, checking, and canceling site resync operations.

## Important APIs, types, and functions
`adminReplicateResyncSubcommands` registers start, status, and cancel. `adminReplicateResyncCmd` declares the group. `mainAdminReplicateResync` delegates invalid invocations to `commandNotFound`.

## Control flow
The file performs only routing. Recognized subcommands execute their own source/peer alias logic.

## State and persistence behavior
No state is read or changed in this file. Resync jobs are server-side state managed by child commands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling resync command variables, and the parent replicate command group.

## Risks and edge cases
Registration drift could make a resync lifecycle action unreachable. Bare group invocation depends on shared not-found/help output.

## Test signals
Tests should verify start/status/cancel registration and shared behavior for bare or unknown resync subcommands.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-resync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-status.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-status.go

## Purpose
Implements `mc admin replicate status`, the main site-replication health view for buckets, policies, users, groups, ILM expiry rules, and object replication metrics.

## Important APIs, types, and functions
Key symbols include `adminReplicateStatusFlags`, `srStatus`, `srStatus.String`, `siteHeader`, `getTheme`, per-entity summary helpers, `srStatusOpts`, `mainAdminReplicationStatus`, and `syncStatus`. It calls `SRStatusInfo`.

## Control flow
The command validates exactly one alias and mutually exclusive group versus individual entity flags. `srStatusOpts` defaults to all categories and metrics unless a specific selector is provided. The handler fetches `madmin.SRStatusInfo` and prints `srStatus`, whose renderer sorts site names, builds deployment-name maps, emits category summaries, optional per-entity detail tables, and object replication metrics including queue, worker, transfer, latency, link, and error data.

## State and persistence behavior
The command is read-only. It observes server-side replication configuration, metadata sync status, and realtime/summary replication metrics. Local state is only the selected options and formatting maps.

## Dependencies and integration points
It integrates MinIO site replication status APIs, replication metric types, pretty-table helpers, console color themes, humanized sizes/durations, global JSON mode, and global UTC time helpers.

## Risks and edge cases
Flag validation is complex and easy to regress. Some maps are indexed without explicit existence checks, so missing site/entity entries rely on zero-value stats. `strings.ToTitle` is deprecated in Go style. Queue warning logic compares current to average counts only.

## Test signals
Tests should cover default all view, category-only flags, individual entity flags, mutually exclusive validation, multiple individual selector rejection, disabled replication, bucket/user/group/policy/ILM mismatch rendering, metrics for single and multiple targets, offline link duration, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-update.go -->
# sources/object-store/minio-mc/cmd/admin-replicate-update.go

## Purpose
Implements `mc admin replicate update`/`edit`, modifying site replication peer endpoint, sync mode, bucket bandwidth defaults, or ILM expiry replication behavior.

## Important APIs, types, and functions
`adminReplicateUpdateFlags` defines deployment, endpoint, mode/sync, bandwidth, and ILM expiry toggles. `updateSuccessMessage` wraps `madmin.ReplicateEditStatus`. `checkAdminReplicateUpdateSyntax` and `mainAdminReplicateUpdate` perform validation and call `SiteReplicationEdit`.

## Control flow
The handler requires one alias, creates an admin client, enforces required flag combinations, rejects conflicting mode/sync or ILM toggles, parses deprecated `--sync` or modern `--mode`, parses bandwidth with `getBandwidthInBytes`, validates endpoint URL, builds `madmin.PeerInfo` plus `SREditOptions`, calls the server, and prints status.

## State and persistence behavior
The persistent mutation is server-side site replication peer metadata or global ILM expiry replication setting. Local state is transient parsed flags.

## Dependencies and integration points
It integrates URL parsing, bandwidth parsing helpers, MinIO site replication edit APIs, sync-state constants, global context, colorized output, and JSON serialization.

## Risks and edge cases
ILM expiry toggles must not be combined with deployment ID. Deprecated `--sync` remains hidden for compatibility. URL parsing accepts syntactically valid but semantically unusable endpoints; deeper validation is server-side.

## Test signals
Tests should cover required flag validation, conflict validation, sync/mode mapping, bandwidth parsing failures, endpoint parsing, ILM-only updates, deployment-specific updates, server errors, and output with `ErrDetail`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate-update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate.go -->
# sources/object-store/minio-mc/cmd/admin-replicate.go

## Purpose
Defines the `mc admin replicate` command group for MinIO site replication administration.

## Important APIs, types, and functions
`adminReplicateSubcommands` registers add, update, remove, info, status, and resync. `adminReplicateCmd` declares the group. `mainAdminReplicate` delegates invalid invocations to `commandNotFound`.

## Control flow
The file routes recognized replication lifecycle commands and has no direct server interaction.

## State and persistence behavior
No state is read or changed here. Replication configuration and metrics are handled by subcommands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling replicate command variables, and top-level admin registration.

## Risks and edge cases
Replication is a broad feature area, so missing a subcommand in this registry can hide significant functionality. Hidden aliases on child commands must still be registered correctly.

## Test signals
Tests should verify all child commands are reachable and that bare or unknown `replicate` invocations use shared not-found/help behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-replicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-scanner-status.go -->
# sources/object-store/minio-mc/cmd/admin-scanner-status.go

## Purpose
Implements `mc admin scanner status`/`info`, displaying scanner activity, bucket scan history, live metrics, or replayed saved metrics.

## Important APIs, types, and functions
Important symbols are `adminScannerInfoFlags`, `adminScannerInfo`, `checkAdminScannerInfoSyntax`, `bucketScanMsg`, `mainAdminScannerInfo`, `metricsMessage`, `initScannerMetricsUI`, `scannerMetricsUI`, `metricsDuration`, `metricsUint64`, and `metricsTitle`.

## Control flow
The handler validates either an input replay file or one target alias. Replay mode opens plain or `.zst` JSON lines, sleeps according to recorded collection time, and sends scanner metrics into the UI. Live mode creates an admin client, optionally fetches `BucketScanInfo`, otherwise streams `madmin.MetricsScanner` with node, count, interval, and path-display options. JSON mode prints each metrics snapshot; interactive mode runs Bubble Tea.

## State and persistence behavior
The command is read-only. It observes server scanner metrics and bucket scan timestamps. Local UI state stores the current metrics snapshot, spinner, quit flag, and max path count.

## Dependencies and integration points
It integrates realtime metrics APIs, bucket scan info APIs, Bubble Tea, spinner/lipgloss, zstd replay, tablewriter, humanize, global terminal dimensions, and shared `metricsMessage` used by resync status.

## Risks and edge cases
Replay mode calls `os.Exit(0)` after playback, bypassing normal returns. Rate calculation uses a fixed minute denominator in `getRate`, which should be checked. Active path output is clipped by terminal size and `max-paths`.

## Test signals
Tests should cover syntax for live and replay modes, zstd replay decoding, bucket scan full-scan detection, JSON metrics output, UI quit/final handling, max-path clipping, no-data view, and metrics formatting helpers.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-scanner-status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-scanner-trace.go -->
# sources/object-store/minio-mc/cmd/admin-scanner-trace.go

## Purpose
Implements `mc admin scanner trace`, streaming MinIO service trace events filtered to scanner operations.

## Important APIs, types, and functions
`adminScannerTraceFlags` defines verbose, function, node, path, size, request/response, and duration filters. `adminScannerTraceCmd`, `checkAdminScannerTraceSyntax`, and `mainAdminScannerTrace` drive the command.

## Control flow
The handler requires one target and enforces that size filters include `--filter-size`. It initializes trace colors, creates an admin client, builds tracing options scoped to `scanner`, builds matching options from CLI flags, then ranges over `ServiceTrace` events and prints only those matching the filters.

## State and persistence behavior
The command is streaming and read-only. It holds a cancelable context but persists no trace data.

## Dependencies and integration points
It integrates shared tracing helpers (`tracingOpts`, `matchingOpts`, `printTrace`), MinIO admin service trace API, global context, and console node/color themes.

## Risks and edge cases
Some examples reference request-header filtering that is not declared in this file, implying shared flags or stale help text. Long-running streams depend on user cancellation. Filter-size parsing is delegated to shared tracing helpers.

## Test signals
Tests should cover syntax, missing filter-size rejection, tracing option scope of `scanner`, matching filter behavior, verbose versus normal trace output, stream errors, and cancellation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-scanner-trace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-scanner.go -->
# sources/object-store/minio-mc/cmd/admin-scanner.go

## Purpose
Defines the `mc admin scanner` command group for scanner status and trace tooling.

## Important APIs, types, and functions
`adminScannerSubcommands` registers status/info and trace. `adminScannerCmd` declares the group. `mainAdminScanner` delegates invalid invocations to `commandNotFound`.

## Control flow
The file routes scanner subcommands and has no direct server interaction.

## State and persistence behavior
No state is read or modified here. Scanner metrics and trace streams are handled by child commands.

## Dependencies and integration points
It depends on `minio/cli`, global flags, sibling scanner command variables, and top-level admin registration.

## Risks and edge cases
Adding scanner tooling requires updating this registry. Hidden alias `info` is owned by the status command, not this group.

## Test signals
Tests should verify status/info and trace registration and shared behavior for bare or unknown `mc admin scanner` invocations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-freeze.go -->
# sources/object-store/minio-mc/cmd/admin-service-freeze.go

## Purpose
Implements the hidden `mc admin service freeze` command, sending a request to freeze S3 API calls on a MinIO cluster.

## Important APIs, types, and functions
`adminServiceFreezeCmd` defines the hidden command. `serviceFreezeCommand` formats success output. `checkAdminServiceFreezeSyntax` requires a single target, and `mainAdminServiceFreeze` calls `ServiceFreezeV2`.

## Control flow
The handler validates one alias, sets success/failure colors, creates an admin client, invokes the server freeze API, and prints a success message with the server URL.

## State and persistence behavior
The persistent operational effect is remote: S3 API calls are frozen on the target MinIO cluster according to server semantics. No local state is written.

## Dependencies and integration points
It integrates the admin service API, global context, hidden command registration under service management, `probe` error handling, `colorjson`, and console output.

## Risks and edge cases
The command is hidden on purpose and can disrupt cluster availability. There is no confirmation prompt or unfreeze path in this file. The comment contains a typo in `service`.

## Test signals
Tests should cover hidden metadata, syntax validation, admin client creation, freeze API failure, JSON output, and human success output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-service-freeze.go -->
