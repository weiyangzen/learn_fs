# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/jobtable.go

Purpose: provides the `jobsTable` presentation helper used by BeeGFS Remote commands to render job, work request, and work result protobuf data in a consistent table shape.

Important APIs/types/functions: `jobsTable` wraps `cmdfmt.Printomatic`; `newJobsTable` chooses default, job-detail, or debug columns; `Row` renders full `beeremote.JobResult` rows; `MinimalRow` renders path-level errors when no job exists; `getWorkRequestsForCell`, `getWorkResultsForCell`, and `getPartsForCell` format nested protobuf lists; `wrapTextAtWidth` breaks long identifiers/checksums; `convertJobStateToEmoji` and `convertWorkStateToEmoji` map protobuf enum states to icons or text.

Control flow: callers construct the table with options, add rows as job responses arrive, and call `PrintRemaining`. `Row` branches between sync and builder requests, infers operation text, then adds one wide row with job timestamps, IDs, status, work request details, and work result details. Debug mode forces all job and work columns; `withJobDetails` exposes all job columns without work columns.

State and persistence: no durable state is written. Runtime behavior depends on Viper global flags `config.DebugKey` and `config.DisableEmojisKey`. Timestamps are formatted as RFC3339 at render time.

Dependencies and integration points: depends on `cmdfmt` for table/JSON output, `ctl/pkg/config` for global flags, and BeeRemote/Flex protobuf generated types. It is used by push, pull, and job/status commands that present Remote job lifecycle state.

Risks: column names are stringly typed and must stay synchronized with command overrides; default wrapping is byte-based rather than rune-width-aware; unknown enum values render as a replacement marker; `job.Request` is dereferenced in one upload/offload branch after `request := job.GetRequest()`, so malformed nil request data would be risky; multi-line cell formatting can be hard for JSON consumers if selected columns include nested work text.

Test signals: no direct tests in this file. Coverage is likely indirect through command output tests, if any. Useful future tests would cover `wrapTextAtWidth`, debug/default column selection, unknown enum fallback, builder-vs-sync rows, and `DisableEmojisKey` alternatives.
