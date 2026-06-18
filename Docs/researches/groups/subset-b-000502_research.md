# subset-b-000502 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/jobtable.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/jobtable.go

Purpose: provides the `jobsTable` presentation helper used by BeeGFS Remote commands to render job, work request, and work result protobuf data in a consistent table shape.

Important APIs/types/functions: `jobsTable` wraps `cmdfmt.Printomatic`; `newJobsTable` chooses default, job-detail, or debug columns; `Row` renders full `beeremote.JobResult` rows; `MinimalRow` renders path-level errors when no job exists; `getWorkRequestsForCell`, `getWorkResultsForCell`, and `getPartsForCell` format nested protobuf lists; `wrapTextAtWidth` breaks long identifiers/checksums; `convertJobStateToEmoji` and `convertWorkStateToEmoji` map protobuf enum states to icons or text.

Control flow: callers construct the table with options, add rows as job responses arrive, and call `PrintRemaining`. `Row` branches between sync and builder requests, infers operation text, then adds one wide row with job timestamps, IDs, status, work request details, and work result details. Debug mode forces all job and work columns; `withJobDetails` exposes all job columns without work columns.

State and persistence: no durable state is written. Runtime behavior depends on Viper global flags `config.DebugKey` and `config.DisableEmojisKey`. Timestamps are formatted as RFC3339 at render time.

Dependencies and integration points: depends on `cmdfmt` for table/JSON output, `ctl/pkg/config` for global flags, and BeeRemote/Flex protobuf generated types. It is used by push, pull, and job/status commands that present Remote job lifecycle state.

Risks: column names are stringly typed and must stay synchronized with command overrides; default wrapping is byte-based rather than rune-width-aware; unknown enum values render as a replacement marker; `job.Request` is dereferenced in one upload/offload branch after `request := job.GetRequest()`, so malformed nil request data would be risky; multi-line cell formatting can be hard for JSON consumers if selected columns include nested work text.

Test signals: no direct tests in this file. Coverage is likely indirect through command output tests, if any. Useful future tests would cover `wrapTextAtWidth`, debug/default column selection, unknown enum fallback, builder-vs-sync rows, and `DisableEmojisKey` alternatives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/jobtable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/list.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/list.go

Purpose: implements the `beegfs remote list` Cobra command for listing configured Remote Storage Targets and their user-visible configuration.

Important APIs/types/functions: `newListCmd` defines the CLI and `--show-secrets`; `runListCmd` retrieves RST config through `ctl/pkg/ctl/rst.GetRSTConfig`, sorts targets by ID, masks secrets by default, and renders `id`, `name`, `policies`, `type`, and `configuration` columns.

Control flow: command validates no positional args, calls the backend, sorts `response.Rsts`, skips the internal job-builder target, inspects `rst.WhichType`, and for S3 reflects protobuf fields to build a compact configuration string. Unknown types are hidden unless `--show-secrets` is set.

State and persistence: read-only. It surfaces persisted BeeRemote/RST configuration but does not modify it. Secret masking is front-end only.

Dependencies and integration points: integrates Cobra, `cmdfmt.NewPrintomatic`, common `rst.JobBuilderRstId`, Flex protobuf reflection, and the RST backend package.

Risks: the S3 configuration builder slices `stringBuilder.String()[:Len()-2]`; if an S3 message has no reflected fields this would panic. Reflection order is protobuf-defined but may not be ideal for stable human output. `--show-secrets` exposes secret material in stdout/table/JSON output.

Test signals: no direct tests. Important test cases would include S3 with/without secret masking, empty S3 config, unknown target types, sort order, and skipping the job-builder RST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/orphaned.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/orphaned.go

Purpose: implements `beegfs remote cleanup-orphaned`, which removes BeeGFS Remote database entries for paths that no longer exist in BeeGFS.

Important APIs/types/functions: `cleanupOrphanedConfig` holds front-end flags; `newCleanupOrphanedCmd` wires `--yes`, `--recurse`, and `--verbose`; `runCleanupOrphanedCmd` consumes the backend result stream from `rst.CleanupOrphaned`.

Control flow: Cobra requires one path prefix. Recurse mode is blocked unless `--yes` is present. The runner gets result and wait channels, counts scanned/deleted/skipped/error rows, prints verbose rows for deletes/skips and all error rows, prints a summary, waits for backend completion, and returns a partial-success `CtlError` if per-entry errors occurred.

State and persistence: mutates only the Remote database, not BeeGFS files or remote objects. With `--recurse`, all entries matching the prefix may be deleted. It requires a mount to verify path existence; unmounted mode errors are annotated with a hint.

Dependencies and integration points: uses `ctl/pkg/ctl/rst.CleanupOrphaned`, `common/filesystem.ErrUnmounted`, `cmdfmt`, Viper debug flag, and `internal/util.NewCtlError`.

Risks: destructive database cleanup is gated but still prefix-based; users can delete many Remote DB records with one command. Summary waits until after rows are printed, so a backend wait error appears after output. Verbose defaults to debug, which may expose many paths.

Test signals: no direct tests. Valuable tests would cover recurse without `--yes`, unmounted error wrapping, result counting, partial-success exit code, and verbose/non-verbose row emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/orphaned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/pushpull.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/pushpull.go

Purpose: implements `beegfs remote push` and `beegfs remote pull`, the front-end commands for scheduling upload/download Remote jobs.

Important APIs/types/functions: `pushPullCfg`; `newPushCmd`; `newPullCmd`; `runPushOrPullCmd`; `flex.JobRequestCfg`; hidden flags for force, metadata, tagging, and storage class; shared priority and update validation.

Control flow: each command builds a backend job request config, validates argument count and flag combinations, normalizes optional priority and allow-restore only when flags were explicitly changed, sets the path, then calls `rst.SubmitJobRequest` with a buffer of 1024. The runner drains asynchronous responses, handles fatal vs non-fatal errors, updates counters by `SubmitJobResponse` status, prints detailed job rows only in verbose/debug except for not-allowed failures, and returns partial success when any job could not start or a previous failed job blocks scheduling.

State and persistence: schedules remote synchronization jobs and may update persistent file RST configuration when `--update` is used. `push --stub-local` can replace uploaded files with stubs; `pull` may overwrite local contents, create stubs, flatten paths, or restore archived requests.

Dependencies and integration points: integrates Cobra flags, common filesystem filters, common/RST flag names and validation, BeeRemote protobuf statuses, `newJobsTable`, `cmdfmt.Printf`, Viper global flags, and CTL exit-code wrapping.

Risks: hidden force and metadata/tagging/storage-class flags can materially change behavior while being less visible. Tagging is manually joined as `key=value&...` without URL escaping here, so backend expectations matter. `--update` requires a valid remote target but only validates nonzero via common RST validation. Partial success is communicated through an error containing the formatted summary.

Test signals: no direct tests. Key test cases include invalid priority, update without target, fatal response early flush, ignored no-RST/unsupported files, status counter totals, verbose/debug row choices, and disabled-emoji summary text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/pushpull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/rst.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/rst.go

Purpose: defines the top-level Remote Storage Target command group.

Important APIs/types/functions: `NewRSTCmd` constructs the `remote` command with aliases `remote-storage-target` and `rst`.

Control flow: the command accepts no args and registers subcommands from this package: push, pull, job, list, and status.

State and persistence: no state itself; it is the integration point for subcommands that query or mutate Remote jobs/configuration.

Dependencies and integration points: depends only on Cobra and package-local command constructors.

Risks: command discoverability and alias stability affect scripts. Adding a new RST subcommand requires wiring it here.

Test signals: no direct tests. A basic command-tree test could verify aliases, arg rejection, and registered subcommands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/rst.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/status.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/status.go

Purpose: implements `beegfs remote status`, which checks whether BeeGFS files are synchronized with configured or specified Remote targets.

Important APIs/types/functions: `statusConfig`; `newStatusCmd`; `runStatusCmd`; flags for remote targets, recursion, stdin delimiter, verbose, summarize, verify-remote, and filter expression through backend config.

Control flow: the command validates at least one path, enables verbose/debug backend details, determines a `PathInputMethod` from args/recurse/stdin delimiter, calls `rst.GetStatus`, drains result records, categorizes each by sync status, prints only unsynced/not-attempted/warnings by default, prints all in verbose, skips directory rows, prints a summary, waits for backend completion, verifies count consistency, and returns partial success if any files are unsynchronized.

State and persistence: read-only. It can query local Remote DB state and optionally verify against remote storage depending on backend config.

Dependencies and integration points: uses `internal/util.DeterminePathInputMethod`, `ctl/pkg/ctl/rst.GetStatus`, filesystem filter flag support, `cmdfmt`, CTL partial-success errors, Viper global debug/emoji settings, and zap debug logging.

Risks: parallel backend processing can return rows out of input order unless worker count is configured to one. A warning forces row printing even in non-verbose mode. The command treats unsynchronized files as partial success but not no-target/not-supported files.

Test signals: no direct tests. Useful tests would cover path input selection, summary counts, directory skipping, warning row emission, partial-success behavior, and no-target info printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/client.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/client.go

Purpose: implements client and user statistics commands that show per-client or per-user BeeGFS operation counters over time.

Important APIs/types/functions: `clientStats_Config`; `newGenericClientStatsCmd`; `newClientStatsCmd`; `newUserStatsCmd`; `runClientStatsCmd`; `printOps`; `userIDToString`; `clientIPToString`; `printOpsRow`; `printOpsRetro`.

Control flow: optional node argument is parsed as meta/storage entity ID. Each interval fetches current stats for one node or node type, diffs against previous counters, computes a sum, prints the time index, then prints rows filtered by name, nonzero/all, limit, and output style. The loop stops when interval is nonpositive or context is canceled.

State and persistence: read-only. Keeps in-memory previous stats to calculate interval deltas. `--names` performs host/user lookups but does not cache them here.

Dependencies and integration points: uses backend `ctl/pkg/ctl/stats`, BeeGFS entity parsing, `cmdfmt.Printomatic`, unit conversion, Viper raw formatting, OS user lookup, reverse DNS, and protobuf `msg.Uint128` IDs.

Risks: `limit` is applied before `filter`, so a filtered client beyond the limit will not show. `sum[0] > 1` controls summary printing, which may skip summaries with exactly one operation unless `--all`. Native-endian decoding of client IP IDs assumes the server encoding matches local behavior. DNS/user lookup can block or fail silently.

Test signals: no direct tests. Useful tests would isolate IP/user formatting, filter/limit behavior, raw-vs-formatted read/write values, interval cancellation, and retro output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/rebalancing.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/rebalancing.go

Purpose: implements `beegfs stats rebalance`, presenting chunk-balancer/rebalancing job statistics from metadata or storage nodes.

Important APIs/types/functions: `RebalanceStatsCfg`; `newRebalancingStatsCmd`; `runRebalanceStatsCommand`; `cbStatsSingleNode`; `cbStatsMultiNode`; `printCBData`.

Control flow: optional node argument selects single-node mode; otherwise the command queries all nodes of a node type. Debug enables the hidden worker count and UID columns. Each interval collects statuses, sorts multi-node rows by node type and numeric ID, prints status/start/end/work/error/locked/migrated data, then repeats until interval is nonpositive or context is canceled.

State and persistence: read-only. It displays active/cumulative server-side rebalancing job counters.

Dependencies and integration points: uses backend `ctl/pkg/ctl/stats` chunk-balance APIs, BeeGFS entity parsing, go slices sorting, `cmdfmt`, Viper debug flag, and BeeMsg version metadata in help text.

Risks: interval defaults to continuous output, so scripts should set `--interval=0` when a one-shot is needed. Error rows are embedded in the last unnamed column instead of aborting per offline node. `locked_inodes` is only meaningful for meta nodes.

Test signals: no direct tests. Useful coverage would check single vs multi selection, sort order, debug columns, error row formatting, timestamp zero handling, and interval cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/rebalancing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/server.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/server.go

Purpose: implements `beegfs stats server`, showing server request queue, worker, and throughput statistics for one or many metadata/storage nodes.

Important APIs/types/functions: `serverStats_Config`; `newServerStatsCmd`; `runServerstatsCmd`; `singleNode`; `multiNode`; `multiNodeAggregated`; `printData`.

Control flow: optional node argument selects history view for one node; omitting it prints latest rows for many nodes or aggregate history with `--sum`. `--sum` is rejected for a single node. The runner picks a collection function, creates a Printomatic with default/debug columns, collects and prints each interval, and formats raw or IEC unit values.

State and persistence: read-only. The only local state is loop timing and the configured history window. Backend returns server-side history for single/aggregate modes.

Dependencies and integration points: uses backend `ctl/pkg/ctl/stats`, BeeGFS entity parsing, unit conversion, Viper raw/debug flags, Cobra, and `cmdfmt`.

Risks: `History.Seconds()` truncates subsecond durations when slicing history. Timestamps greater than `math.MaxInt64` are printed raw. Continuous interval output defaults to one second. Multi-node rows are sorted by type then numeric ID.

Test signals: no direct tests. Useful tests would cover mode selection, `--sum` validation, history slicing, raw/unit formatting, sort order, and context cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/stats.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/stats.go

Purpose: defines the top-level `stats` command group.

Important APIs/types/functions: `NewCmd` constructs the Cobra command and registers `server`, `client`, `user`, and `rebalance`.

Control flow: the command has no run logic of its own; subcommands own validation and execution.

State and persistence: no state. It exposes read-only statistics subcommands.

Dependencies and integration points: depends on Cobra and package-local command constructors.

Risks: new stats commands must be added here. Aliases or command names affect scripts.

Test signals: no direct tests. A command-tree test can verify registered children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/version.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/version.go

Purpose: implements the `version` command for printing CTL build and protocol compatibility information.

Important APIs/types/functions: package variables `BinaryName`, `Version`, `Commit`, and `BuildTime`; package variable `versionCmd`.

Control flow: command accepts no args and prints version, commit, and build time. It also prints a hint that this is the command-line tool version. When global debug is enabled it prints effective and real UID/GID details.

State and persistence: read-only, no runtime state mutation.

Dependencies and integration points: integrates Cobra, Viper debug config, backend config key constants, and Unix identity syscalls.

Risks: if build variables are not set by linker flags, output contains defaults such as `local-build` and `unknown`. Version output is user/script-facing and should remain stable. Debug mode exposes process identity information.

Test signals: no direct tests. Useful tests would validate no-arg enforcement and that required version fields are present under default and injected build variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/fmt.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/fmt.go

Purpose: provides the command output abstraction used for structured table, JSON, pretty JSON, and NDJSON rendering.

Important APIs/types/functions: `Printf` writes diagnostic text to stderr; `Printer` abstracts table/JSON renderers; `Printomatic` tracks columns, selected columns, page size, output type, and row count; `NewPrintomatic`; `WithEmptyColumns`; `replacePrinter`; `AddItem`; `PrintRemaining`.

Control flow: construction reads Viper global output, columns, debug/page-size settings indirectly through config keys, normalizes spaces in column names to underscores, selects a JSON printer or go-pretty table, hides unselected columns with `table.ColumnConfig`, and prints when page size is zero or reached. JSON with page size zero becomes NDJSON.

State and persistence: no persistence. Per-instance state buffers rows until page flush. Output configuration is global through Viper.

Dependencies and integration points: central integration point for all CLI commands that emit structured output. Depends on go-pretty table/text, Viper, and `ctl/pkg/config` output constants.

Risks: `AddItem` assumes row width matches configured columns; JSON printer panics on mismatch. `NewPrintomatic` mutates the input `columns` and `defaultColumns` slices in place while replacing spaces, so callers reusing those slices may observe changes. Sorting is mentioned in comments but not implemented here. Mixed stderr/stdout behavior matters for scripts.

Test signals: no direct tests in this work item. High-value tests include column selection, all-columns/debug behavior, page-size zero table/NDJSON semantics, empty-column suppression, and mismatch panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/fmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/json.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/json.go

Purpose: implements the JSON/NDJSON backend for `Printomatic`.

Important APIs/types/functions: `jsonPrinter`; `newJSONPrinter`; `SetColumnConfigs`; `AppendRow`; `Render`; `printPrettyJSON`; `printJSON`.

Control flow: rows are appended as maps keyed by visible column names. `Render` emits a single row object for NDJSON (`pageSize == 0`) or an array for JSON modes, with optional indentation.

State and persistence: buffers rows in memory until rendered. No persistence.

Dependencies and integration points: implements enough of the go-pretty `Printer`-like interface to be swapped into `Printomatic`. Uses `table.ColumnConfig` for hidden/name metadata and standard `encoding/json`.

Risks: panics on row/column count mismatch or invalid NDJSON row count, intentionally treating these as programmer bugs. Map key order in JSON is handled by Go's encoder deterministically for strings today, but callers should not rely on display order semantically.

Test signals: no direct tests. Useful tests would assert hidden columns, NDJSON single-object rendering, pretty formatting, and panic conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/json.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/config/config.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/config/config.go

Purpose: defines and binds CTL global CLI flags, environment variables, and cleanup hooks for the command front-end.

Important APIs/types/functions: `InitGlobalFlags`; `Cleanup`. The initializer registers flags for debug/raw/output/columns/page-size, management and BeeRemote addresses, mount handling, TLS/auth, worker count, logging, pprof, proxy use, alerts, and environment binding.

Control flow: flags are registered on the root persistent flag set, hidden developer/proxy/pprof flags are marked hidden, Viper is configured with `BEEGFS_` prefix and hyphen-to-underscore replacement, `BEEGFS_BINARY_NAME` is set, and every persistent flag is bound to both environment and pflag.

State and persistence: mutates process environment and Viper global configuration. `Cleanup` delegates to backend config cleanup to release global resources.

Dependencies and integration points: front-end bridge to `ctl/pkg/config`; uses Cobra, pflag, Viper, runtime CPU count, and internal util validated-string flag for output modes.

Risks: Viper is global, so tests and library consumers must isolate/reset state. Defaults such as management auto-detection, auth file, TLS cert file, and worker count strongly affect backend behavior. Some `MarkHidden` errors are ignored.

Test signals: no direct tests. Useful tests would validate env binding names, defaults, hidden flags, output value validation, and cleanup forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/error.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/error.go

Purpose: defines CTL-specific errors that carry an intended process exit code.

Important APIs/types/functions: `CtlError`; `CtlExitCode`; constants `Success`, `GeneralError`, `PartialSuccess`; `NewCtlError`; `GetExitCode`; `Error`.

Control flow: commands wrap an underlying error and exit-code classification, then the top-level command runner can inspect the error type and choose the exit code.

State and persistence: no state.

Dependencies and integration points: used by command packages such as remote push/status/cleanup to distinguish partial success from fatal failure.

Risks: `GetExitCode` has pointer receiver while `NewCtlError` returns a value; callers using type assertions must account for value vs pointer forms. There is no `Unwrap`, so standard `errors.Is/As` cannot inspect the inner error through `CtlError`.

Test signals: no direct tests. Useful tests would cover string conversion, exit-code values, and top-level error handling for value/pointer assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/flags.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/flags.go

Purpose: provides reusable pflag values for human-readable byte sizes, constrained string choices, and remote target ID lists.

Important APIs/types/functions: `I64BytesVar`; `i64BytesFlag`; `ValidatedStringFlag`; `validatedStringFlag`; `NewRemoteTargetsFlag`; `rstsFlag`.

Control flow: byte-size flags parse defaults and user values through `ParseIntFromStr` and reject values above `math.MaxInt64`. Validated strings lowercase input and compare against allowed `fmt.Stringer` values. RST flags accept `none` as an empty configured list or comma-separated nonzero unique uint32 IDs.

State and persistence: flag values write to caller-provided pointers. No persistence.

Dependencies and integration points: integrates pflag and parser utilities; used by global output flags and Remote target selection.

Risks: `i64BytesFlag.String` returns the default text, not the current parsed value, which may surprise generic flag display. RST `String` returns "unchanged" for nil and empty slices, while `Set("none")` semantically means changed-to-empty. `ValidatedStringFlag` stores the `fmt.Stringer` object from the allowed slice.

Test signals: no direct tests for this file. Parser tests indirectly validate byte parsing. Useful flag tests would cover current-value display, duplicate RST IDs, zero ID rejection, `none`, and case-insensitive string validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/parser.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/parser.go

Purpose: implements parsing and formatting helpers for byte sizes, numeric ranges, and "unlimited" int64 display.

Important APIs/types/functions: `ParseIntFromStr`; `ParseUint64RangeFromStr`; `I64FormatPrefixWithUnlimited`; `UnlimitedText`; SI/IEC multiplier map.

Control flow: byte parsing matches `<number><optional unit>`, validates units, uses integer multiplication for whole numbers to preserve precision, rejects decimal raw bytes, and checks overflow for integer and float paths. Range parsing accepts `min-max` or a single value and enforces configured bounds. Unlimited formatting maps `math.MaxInt64` to infinity text, otherwise delegates to unitconv.

State and persistence: stateless.

Dependencies and integration points: used by flag helpers and other command packages needing size/range parsing. Depends on regex, strconv, math, strings, and unitconv.

Risks: regex allows multiple dots initially and relies on later parsing errors. Float conversion for decimal prefixed values can lose precision for very large values, as documented. Unit spelling is intentionally strict around uppercase `B`, which may reject user expectations.

Test signals: `parser_test.go` covers valid SI/IEC inputs, decimals with prefixes, invalid units, max uint64 boundaries, overflow, raw-byte decimal rejection, and range parsing with bounds/order errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/parser_test.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/parser_test.go

Purpose: unit tests for parser helpers.

Important APIs/types/functions: `TestParseIntFromStr`; `TestParseUintRangeFromStr`.

Control flow: table-driven tests exercise byte-size inputs and range inputs, asserting either errors or exact parsed values. The byte tests include SI/IEC variants, decimal prefixed values, max uint64, overflow, invalid prefixes, and case-sensitive byte suffix behavior. Range tests include trimmed ranges, single values, reversed ranges, invalid separators, negative-looking values, and configured lower/upper bounds.

State and persistence: no state; pure unit tests.

Dependencies and integration points: uses `testing` and `stretchr/testify/assert`.

Risks: tests do not cover `I64FormatPrefixWithUnlimited` or pflag wrappers. `t.Run` subtests are not used for each parser case, so failing cases report through assertion messages rather than subtest names.

Test signals: strong direct coverage for parser edge cases. Additional coverage should target unlimited formatting and flag integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/terminal.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/terminal.go

Purpose: provides terminal refresh and alert helpers for watch-like command output.

Important APIs/types/functions: `TermRefresher`; `StartRefresh`; `FinishRefresh`; `WithTermFooter`; `WithCancelRefresh`; `TerminalAlert`.

Control flow: `StartRefresh` records terminal dimensions, creates a pipe, saves `os.Stdout`, and redirects stdout to the pipe. `FinishRefresh` closes and reads the pipe, restores stdout, optionally clears the terminal, prints buffered output, and draws a colored footer at the bottom. `TerminalAlert` emits a bell.

State and persistence: temporarily mutates global `os.Stdout`; no persistence. The caller must call `FinishRefresh` after successful `StartRefresh`.

Dependencies and integration points: uses `golang.org/x/term` for terminal size and ANSI control sequences for clearing and footer coloring. Intended for commands that repeatedly refresh printed output.

Risks: global stdout redirection is process-wide and not safe with concurrent writers. Errors between `StartRefresh` and `FinishRefresh` can leave stdout redirected if callers do not defer cleanup. Footer width uses `len`, not display width. It requires stdout to be a terminal.

Test signals: no direct tests. Useful tests would require an isolated pseudo-terminal or abstraction for stdout/term size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/terminal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/url.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/url.go

Purpose: builds a deterministic URL query string with an HMAC-SHA256 signature over its encoded parameters.

Important APIs/types/functions: `URLEncodeSignMap`.

Control flow: adds all map entries to `url.Values`, encodes them, signs the encoded string with the value stored at `m[key]`, base64url-encodes the MAC without padding, appends it as `mac`, and returns the final encoded query.

State and persistence: stateless.

Dependencies and integration points: uses standard `net/url`, `crypto/hmac`, `crypto/sha256`, and base64 raw URL encoding. Used where CTL needs signed GET-style argument strings.

Risks: if `key` is absent, the HMAC key is the empty string because `m[key]` returns zero value. The MAC is calculated before adding `mac`, which is correct, but callers must know that all original fields are included. Map iteration order is normalized by `url.Values.Encode`.

Test signals: `url_test.go` validates a fixed UUID-keyed query signature and encoded ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/url_test.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/util/url_test.go

Purpose: unit test for signed URL query generation.

Important APIs/types/functions: `TestURLEncodeSignMap`.

Control flow: builds a map containing capacity, meta/storage counts, net protocol, and UUID; signs using `uuid`; asserts no error and exact encoded output including `mac`.

State and persistence: none.

Dependencies and integration points: uses `testing`, `strconv`, and `stretchr/testify/require`.

Risks: exact string assertion is useful for determinism but will need updates if encoding/signature fields intentionally change. It does not cover missing key, special characters, duplicate keys, or empty maps.

Test signals: confirms deterministic query ordering and HMAC behavior for a representative input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/util/url_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/config/config.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/config/config.go

Purpose: provides the backend/global configuration and process-wide clients used by CTL as both CLI and library.

Important APIs/types/functions: config key constants; output type constants; `GlobalConfig`; `InitViperFromExternal`; `InitLoggerFromExternal`; `ManagementClient`; `BeeRemoteClient`; `BeeRemoteRegistry`; `BeeGFSClient`; `NodeStore`; `Cleanup`; `GetLogger`.

Control flow: external initialization binds a synthetic pflag set into Viper once and rejects later different configs. `ManagementClient` lazily reads TLS cert/auth, auto-discovers management address and auth file from mounted clients when configured as `auto`, then creates a cached gRPC management client. `BeeRemoteClient` reuses management auth secret and creates a cached BeeRemote gRPC client. `BeeGFSClient` lazily determines mounted/unmounted filesystem provider. `NodeStore` initializes once under a mutex by fetching nodes from management and converting protobuf IDs/NICs/root metadata. `GetLogger` lazily creates stderr logging or uses an external logger.

State and persistence: heavy process-global state: cached management client, BeeRemote client, BeeRemote registry, filesystem provider, node store, external-init flags, global config snapshot, and logger. It reads local files (`cert.pem`, auth file, procfs client config) but does not persist changes except setting Viper auth-file when auto-discovered.

Dependencies and integration points: central dependency for nearly every backend package. Integrates Viper, pflag, BeeGFS filesystem/procfs, gRPC client construction, registry feature discovery, BeeMsg node store, management protobuf APIs, logger, and OS/root checks.

Risks: global singleton state complicates tests and dynamic reconfiguration. `NodeStore` has a double-check pattern that reads `nodeStore` before taking the read lock, so race detector scrutiny is warranted. Auto-management discovery can fail with multiple mounts using different mgmtd addresses. BeeRemote access requires management access first. Unmounted BeeGFS mode requires root. `Cleanup` currently cleans node store and nils it, but other cached clients/registry/logger remain.

Test signals: no direct tests in this work item. High-value coverage would mock procfs, management responses, auth-file fallback, TLS cert failures, external initialization idempotency, unmounted root checks, and node-store concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/benchmark/benchmark.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/benchmark/benchmark.go

Purpose: implements backend support for BeeGFS storage benchmark control actions against storage targets or nodes.

Important APIs/types/functions: `NewStorageBenchConfig`; `StorageBenchConfig`; `StorageBenchResult`; `TargetResult`; `ExecuteStorageBenchAction`; `filterTargetsByNode`.

Control flow: execution initializes logging, node store, and mappings, filters targets by explicit target IDs, explicit storage nodes, or all storage targets, builds a base `StorageBenchControlMsg`, sends one TCP request per storage node with its target IDs, validates response target/result lengths, maps response target IDs back to entity ID sets, and returns per-node results.

State and persistence: sends benchmark control messages to storage nodes; depending on `Action`, this may start, stop, or query server-side benchmark activity. Local state is transient.

Dependencies and integration points: uses `config.NodeStore`, `util.GetMappings`, `target.GetTargets`, BeeMsg storage benchmark messages, BeeGFS entity types, and logging.

Risks: RST mapping errors are ignored only for `ErrMappingRSTs`, but the code still passes `mappings` into filtering, so callers rely on mapping availability for target selection. Cannot specify both target IDs and storage nodes. Response target IDs are trusted after length check but must map back to known targets. No parallel fan-out; large node counts are sequential.

Test signals: no direct tests. Useful tests would mock mappings/node store for duplicate target filtering, target-vs-node exclusivity, all-target selection, response length mismatch, and request construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/benchmark/benchmark.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/create.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/create.go

Purpose: creates buddy mirror groups directly or automatically from eligible metadata/storage targets.

Important APIs/types/functions: `Create`; `AutoCreateConfig`; `AutoCreate`.

Control flow: `Create` forwards a protobuf request to management. `AutoCreate` gets logger, node store, existing buddy groups, and targets; filters targets by node type, existing group membership, and equal inode/space constraints unless ignored; checks minimum and even count; greedily pairs primaries and secondaries while enforcing same storage pool for storage and preferring different nodes; swaps meta primary if the root inode owner would otherwise become secondary; creates groups with generated aliases; returns created responses plus warnings for recoverable pairing/creation issues.

State and persistence: mutates management configuration by creating buddy groups. Auto-create can create multiple groups in one call.

Dependencies and integration points: uses management gRPC, target listing, node store root metadata information, BeeGFS entity/pool fields, and sorting/containment helpers.

Risks: greedy pairing may not find an optimal global matching. Documentation says constraint 3 can be removed by `IgnoreSpace`, but code uses `IgnoreUneven` for uneven counts. Results append `res` even if `Create` returns an error, potentially adding nil responses. Auto-generated aliases may collide. Same-node secondary is allowed with warning if no better target exists.

Test signals: no direct tests. Valuable tests would cover filtering, uneven handling, storage-pool pairing, root meta swap, warning accumulation, nil response on creation error, and duplicate/existing group exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/delete.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/delete.go

Purpose: deletes a buddy group through the management service.

Important APIs/types/functions: `Delete`.

Control flow: initializes management client, calls `DeleteBuddyGroup`, returns response or error.

State and persistence: mutates management buddy-group configuration.

Dependencies and integration points: depends on `config.ManagementClient` and management protobuf request/response types.

Risks: no local validation or safety gating; callers must construct safe requests and handle consequences. Returns `resp, err` after checking `err`, which is harmless but redundant.

Test signals: no direct tests. Mock management tests could assert request forwarding and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/initialize.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/initialize.go

Purpose: sends the management request that mirrors the BeeGFS root metadata inode.

Important APIs/types/functions: `MirrorRootInode`.

Control flow: obtains the management client and calls `MirrorRootInode` with an empty request.

State and persistence: mutates cluster metadata mirroring state for the root inode.

Dependencies and integration points: uses backend global management client and management protobuf API.

Risks: no local preflight checks; callers must ensure buddy groups and cluster state are appropriate. Errors are returned directly.

Test signals: no direct tests. Mock tests could verify request dispatch and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/initialize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/list.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/list.go

Purpose: retrieves buddy group information from management and converts protobuf data into CTL-friendly result structs.

Important APIs/types/functions: `GetBuddyGroups_Result`; `GetBuddyGroups`.

Control flow: fetches all buddy groups, converts buddy group/primary/secondary IDs from protobuf, maps protobuf node types to BeeGFS node types, formats consistency-state strings, and returns a slice of results.

State and persistence: read-only.

Dependencies and integration points: depends on `config.ManagementClient`, BeeGFS entity conversion helpers, management protobuf API, target/buddy group protobuf fields, and BeeGFS protobuf node type constants.

Risks: conversion errors abort the whole list. Unknown node types must be handled consistently by conversion logic. Consistency states are strings, so downstream consumers should not parse them as stable enums unless documented.

Test signals: no direct tests. Useful tests would use representative protobuf buddy groups for meta and storage, conversion failures, unknown/zero states, and empty response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/start.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/start.go

Purpose: starts buddy group resynchronization through management.

Important APIs/types/functions: `StartResync(ctx context.Context, group beegfs.EntityId, timestampSec int64, restart bool) error`.

Control flow: obtains management client, converts the buddy group ID to protobuf, sends `StartResyncRequest` with timestamp and restart pointers, discards the response, and returns any error.

State and persistence: triggers server-side resync work for buddy groups.

Dependencies and integration points: uses `config.ManagementClient` and management protobuf resync API.

Risks: no local validation; callers own target/group selection and user confirmation. Errors are direct from management/gRPC.

Test signals: no direct tests. Mock management tests could verify request forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/stats.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/stats.go

Purpose: retrieves metadata or storage buddy resync statistics by resolving a buddy group to its primary target and querying the owning node.

Important APIs/types/functions: `GetMetaResyncStats`; `GetStorageResyncStats`; `getNode`; `GetPrimaryTarget`.

Control flow: stats functions call `getNode` for a primary target, initialize the node store, send the appropriate BeeMsg stats request to the owning node, and return the response. `getNode` uses mappings to map target alias to node. `GetPrimaryTarget` scans buddy groups and matches the provided entity ID by UID, alias, or legacy ID.

State and persistence: read-only; queries live node stats.

Dependencies and integration points: uses `config.NodeStore`, util mappings, buddygroup listing, BeeMsg resync messages, and BeeGFS entity ID variants.

Risks: `getNode` ignores only RST mapping errors but still assumes `mappings` is usable; a nil mappings value after ignored errors would be dangerous if `GetMappings` can return nil. Mapping by `pTarget.Alias` requires alias population. Legacy ID matching calls `ToProto` repeatedly and compares numeric/type fields. Stats should use primary targets only, so stale buddy group state can mislead callers.

Test signals: no direct tests. Useful tests would cover all entity ID match forms, not-found behavior, mapping failures, and correct BeeMsg request target IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/setalias.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/setalias.go

Purpose: changes the alias of a buddy group through management.

Important APIs/types/functions: `SetAlias`.

Control flow: converts the provided entity ID to protobuf, sends `SetAliasRequest` with entity type `BUDDY_GROUP` and new alias string, and returns any error.

State and persistence: mutates management alias metadata.

Dependencies and integration points: uses `config.ManagementClient`, BeeGFS entity ID conversion, and management/beegfs protobuf APIs.

Risks: no local validation beyond the `beegfs.Alias` type already provided by caller. Entity type is fixed to buddy group.

Test signals: no direct tests. Mock tests could verify conversion and request fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/setalias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/debug/debug.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/debug/debug.go

Purpose: sends generic debug commands to a BeeGFS node over the BeeMsg TCP path.

Important APIs/types/functions: `GenericDebugCmd`.

Control flow: gets the global node store, sends `msg.GenericDebug` with the command bytes to the selected node, receives `GenericDebugResp`, and returns the response as a string.

State and persistence: command effects depend entirely on the server-side debug command; this wrapper itself stores nothing.

Dependencies and integration points: depends on `config.NodeStore`, BeeGFS entity IDs, and BeeMsg generic debug request/response types.

Risks: generic debug commands may expose or mutate low-level server state depending on server support. No local allowlist or validation is present here.

Test signals: no direct tests. Mock node-store tests could assert command bytes and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/debug/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/beegfstoolkit.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/beegfstoolkit.go

Purpose: ports BeeGFS toolkit path/hash helpers used to display verbose entry metadata such as chunk, dentry, and inode paths.

Important APIs/types/functions: `getFileChunkPath`; `timestampFromEntryID`; `timestampToPath`; `getMetaDirEntryPath`; `getMetaInodePath`; `getHashPath`; `getBaseHashPath`; `getHashes`.

Control flow: file chunk paths are built from original parent UID, timestamp parsed from parent entry ID, path components derived from timestamp reverse positions, original parent entry ID, and entry ID. Metadata dentry/inode paths are hash-based using fixed BeeGFS directory fanout constants and `hash32`.

State and persistence: pure computation; no filesystem access.

Dependencies and integration points: used by `entry.newVerbose` in `entry.go`. Relies on `hash32.go` to match BeeGFS storage toolkit behavior.

Risks: only supports the 2014.01 style chunk path with user/timestamp directories. Special entry IDs and malformed timestamps produce best-effort `?` plus errors. Hash constants must match server layout.

Test signals: no direct tests in this work item. Useful tests would compare outputs with known C++ BeeGFS toolkit fixtures for normal, root/lost+found, malformed, and short timestamp entry IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/beegfstoolkit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser.go

Purpose: selects migration source/destination target or buddy group IDs for an entry during rebalancing/migration planning.

Important APIs/types/functions: errors `ErrEntryHasNoTargets` and `ErrEntryDetailsUnavailable`; `getRandomIDChooser`; `getMigrationForEntry`.

Control flow: `getMigrationForEntry` rejects entries without details or without stripe targets. It creates a lazy shuffled destination chooser, then branches on stripe pattern: buddy-mirror entries compare pattern IDs against source groups and choose replacement destination groups; RAID0 entries compare against source targets and choose replacement targets. IDs not in source sets are returned as unmodified. Insufficient destination IDs produce explanatory errors. The chooser avoids IDs already present in the original stripe pattern and returns each shuffled candidate once.

State and persistence: no persistence. The chooser closure keeps shuffled candidates, index, and in-use map for one migration decision.

Dependencies and integration points: uses BeeGFS stripe pattern types and BeeMsg `RebalanceIDType`. Consumed by entry migration workflows outside this file.

Risks: `math/rand/v2` default randomness makes destination choice nondeterministic, complicating reproducibility. The in-use map is initialized only once from the initial stripe pattern, not updated with IDs chosen earlier; uniqueness still comes from the shuffled index but it does not prevent choosing two destination IDs that were not in the original pattern when multiple sources are migrated. Unsupported stripe patterns fall through to invalid type behavior in the unseen tail and should be handled carefully.

Test signals: `chooser_test.go` covers missing details, empty targets, source/destination selection, insufficient destinations, buddy-vs-RAID behavior, and unmodified IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser_test.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser_test.go

Purpose: unit tests for entry migration target selection.

Important APIs/types/functions: tests around `getMigrationForEntry`, `ErrEntryDetailsUnavailable`, and `ErrEntryHasNoTargets`.

Control flow: table-driven cases construct `GetEntryCombinedInfo` with stripe pattern variants and source/destination sets, then verify returned rebalance type, source IDs, destination IDs, unmodified IDs, and expected errors. Tests account for random destination ordering by checking membership where appropriate.

State and persistence: no state; pure unit tests.

Dependencies and integration points: uses BeeGFS pattern types, BeeMsg rebalance ID types, and testify assertions.

Risks: random chooser behavior means tests should avoid relying on exact destination order unless constrained. Coverage should continue to include unsupported stripe pattern behavior and multi-source uniqueness.

Test signals: direct coverage of the most important chooser error and selection paths; it is the main safety net for migration planning logic in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/create.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/create.go

Purpose: creates BeeGFS files and directories with explicit ownership, permissions, stripe pattern, storage pool, metadata placement, and Remote target configuration.

Important APIs/types/functions: `CreateEntryCfg`; `CreateFileCfg`; `CreateDirCfg`; `CreateEntryResult`; `generateAndVerifyMakeFileReq`; `checkPoolForPattern`; `checkAndGetTargets`; `generateAndVerifyMkDirRequest`; `CreateEntry`.

Control flow: `CreateEntry` validates paths, loads mappings and node store, sorts paths so parent directories can reuse a base request, initializes the BeeGFS client from the first parent, resolves each path relative to the mount, fetches parent entry info with original message, generates a base make-file or mkdir request when parent changes, sets the per-entry basename, sends the request to the parent metadata owner, and records response status and raw entry info. File request generation inherits parent stripe/RST config then applies user overrides and validates pool/targets/buddy groups. Directory request generation validates preferred meta nodes or buddy groups depending on parent mirroring.

State and persistence: creates files or directories on BeeGFS metadata servers and may configure RST IDs/cooldown on new files. No local persistence.

Dependencies and integration points: uses config BeeGFS client and node store, `GetEntry`, pool/mapping utilities, BeeMsg make-file/mkdir messages, filesystem unmounted error handling, and BeeGFS entity types.

Risks: base request objects are mutated per path by setting `NewFileName`/`NewDirName`; this is safe sequentially but not shareable. `checkAndGetTargets` returns IDs from a map, losing user-specified order, which may matter for stripe ordering. Error message for parent pool lookup formats `*userCfg.FileCfg.Pool` even when `Pool` is nil, which can panic on that error path. Unmounted mode proceeds only if BeeGFS client returns `ErrUnmounted`, but later path behavior depends on provider semantics.

Test signals: no direct tests. High-value tests would mock mappings/node store for file and dir request generation, pool validation, duplicate target detection, forced cross-pool targets, mirrored directory preferred-node lookup, nil pool error path, and path grouping by parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/disposal.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/disposal.go

Purpose: lists or unlinks metadata disposal entries across metadata nodes, including mirrored disposal directories.

Important APIs/types/functions: `DisposalCfg`; `DisposalResult`; `CleanupDisposals`; `disposalCleaner.run`; `disposalCleaner.walkNode`; constants `disposal`, `mdisposal`, and `disposalMaxOutNames`.

Control flow: initialization gets logger, node store, buddy groups, and a meta buddy-group-to-primary-node map, then starts a goroutine. The cleaner iterates metadata nodes, walks non-mirrored disposal entries on each, and walks mirrored entries only on primary nodes. `walkNode` pages with `ListDirFromOffsetRequest` up to 50 names at a time, optionally sends `UnlinkFileRequest` for each entry, emits results, and stops when fewer than max names are returned.

State and persistence: read-only by default; with `Dispose` true it unlinks disposal entries on metadata servers.

Dependencies and integration points: uses BeeMsg node store requests, buddygroup listing, util mapping, logger, and BeeGFS metadata node IDs.

Risks: disposal cleanup is destructive when enabled. Fatal RPC errors stop all processing. Delete response operation errors are returned as per-entry results rather than fatal. Paging assumes the server offset remains valid while entries may be deleted. Mirrored walking relies on primary mapping to avoid duplicate deletion.

Test signals: no direct tests. Useful tests would mock node store pages, dispose vs list behavior, mirrored primary filtering, delete result handling, and fatal list/unlink request errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/disposal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entry.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entry.go

Purpose: core backend for retrieving BeeGFS entry metadata, owner nodes, verbose storage paths, file state, access flags, and Remote target IDs.

Important APIs/types/functions: `GetEntriesCfg`; `GetEntryCombinedInfo`; `Entry`; `EntryDetails`; `patternConfig`; `remoteConfig`; `newEntry`; `Verbose`; `newVerbose`; `GetEntries`; `GetEntry`; `GetEntryAndOwnerFromPath`; ioctl/RPC helpers; `getPrimaryMetaNode`; `GetFileDataState`; `SetFileDataState`; `GetFileAccessFlags`; `SetAccessFlags`; `ClearAccessFlags`; `SetFileRstIds`; `SetDirRstIds`.

Control flow: `GetEntries` wraps path processing and calls `GetEntry`. `GetEntry` resolves entry and owner via ioctl when mounted or RPC when unmounted/no ioctl, fetches full `GetEntryInfoResponse` if needed, builds a combined entry, optionally fetches parent data for verbose paths, and returns structured details. The ioctl path first tries `GetEntryInfoV2` with a one-minute unavailable probe cache, falls back to opening files/directories and `GetEntryInfo`, handles special file types through parent `LookupIntent`, and falls back to RPC on locked regular files. The RPC path walks from root with `FindOwnerRequest` shortcuts up to 128 steps. State setters fetch current file state, compute a new bit field, send `SetFileStateRequest`, and retry once on inode-lock conflicts.

State and persistence: reads live metadata and file state. `SetFileDataState`, access flag setters, `SetFileRstIds`, and `SetDirRstIds` mutate metadata on owner nodes. Global probe cache records ioctl availability. Uses cached mappings and node store from config/util.

Dependencies and integration points: central integration point for filesystem provider, ioctls, BeeMsg TCP requests, mapping cache, BeeRemote RST protobufs, common BeeGFS types, path processing, zap logging, and Unix syscalls.

Risks: many paths require initialized global BeeGFS client and node store. Unmounted/RPC path requires root. `GetEntryInfoV2` fallback behavior must avoid triggering automatic restore on older clients, which is why probe caching matters. Special file handling opens parent directories and performs lookup; concurrent path mutation can produce depth or lookup errors. `SetAccessFlags` retry recomputes `info` but compares against the pre-retry `fs` value, so concurrent state changes deserve careful review. `SetDirRstIds` treats `NOTADIR` as non-fatal despite checking type earlier.

Test signals: no direct tests in this subset. Needed coverage includes ioctl V2 success/unavailable/error, special file lookup, RPC traversal, buddy mirrored owner resolution with mapping refresh, nil `Details` handling, state setter retry behavior, and RST setters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid.go

Purpose: provides compact parsing and a fixed-capacity thread-safe set/map for BeeGFS entry IDs.

Important APIs/types/functions: `packedEntryID`; `newPackedEntryID`; `parseHexToUint32`; `packedEntryMap`; `newPackedEntryMap`; `Add`; `Contains`.

Control flow: entry IDs are split into exactly three hyphen-separated hex sections, each one to eight chars, and parsed without heap allocation into uint32 fields. The map stores packed IDs in a ring buffer and an index map. `Add` returns false for duplicates, evicts the oldest ID when capacity is full, inserts the new ID, and advances the ring position. `Contains` parses and checks under read lock.

State and persistence: in-memory only. `packedEntryMap` is guarded by an RW mutex and bounded by capacity.

Dependencies and integration points: likely used by entry traversal/migration workflows that need duplicate suppression without retaining unbounded strings.

Risks: special IDs such as root/disposal/mdisposal are intentionally unsupported. Capacity <= 0 silently becomes 1. FIFO eviction is by insertion position, not access recency. Parsing accepts uppercase and lowercase hex but rejects any section longer than 8 chars.

Test signals: `entryid_test.go` covers valid/invalid packing, hex parsing, duplicate detection, eviction behavior, ring/index internals, invalid contains input, and zero-capacity normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid_test.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid_test.go

Purpose: unit tests for compact entry ID parsing and bounded entry ID map behavior.

Important APIs/types/functions: `TestNewPackedEntryID`; `TestParseHexToUint32`; `TestPackedEntryMap`; `TestPackedEntryMapCapZero`.

Control flow: tests validate expected packed values for real-looking IDs, reject special/oversized IDs, verify hex parser behavior, exercise map add/contains/duplicate semantics, inspect FIFO eviction ring/index state, and confirm zero capacity behaves as one.

State and persistence: no persistence; tests inspect in-memory state directly because package-private internals are in the same package.

Dependencies and integration points: uses `testing` and testify `assert`.

Risks: subtests use `t.Run(t.Name(), ...)`, so names may not distinguish cases as intended. Direct internal-state assertions are precise but can make refactors noisy even if behavior remains equivalent.

Test signals: strong coverage for this small data structure. Additional race tests could validate concurrent Add/Contains under `go test -race`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/hash32.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/hash32.go

Purpose: implements the BeeGFS-compatible 32-bit hash used by entry toolkit path helpers.

Important APIs/types/functions: `hash32` and any helper constants/tables in the file.

Control flow: accepts a string and computes the deterministic uint32 checksum used by `getHashes` in `beegfstoolkit.go` to map entry IDs into metadata directory fanout paths.

State and persistence: pure computation.

Dependencies and integration points: consumed by `getHashes`, which feeds verbose dentry/inode path rendering. It must match the C++ BeeGFS hashing algorithm to produce correct paths.

Risks: any deviation from server/C++ hash behavior will produce wrong metadata paths. Signedness, byte order, and string-byte treatment are typical compatibility hazards for ported hash functions.

Test signals: no direct tests in this subset. Useful tests should compare known BeeGFS entry IDs to expected level-1/level-2 hash directories and raw hash values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/hash32.go -->
