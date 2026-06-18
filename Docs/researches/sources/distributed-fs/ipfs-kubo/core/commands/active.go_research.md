# Research: sources/distributed-fs/ipfs-kubo/core/commands/active.go

Purpose: Implements `ipfs commands`/active request listing and request-log maintenance subcommands.

Important APIs/types/functions: `ActiveReqsCmd`, `clearInactiveCmd`, and `setRequestClearCmd`; option `--verbose`.

Control flow, state, and persistence: The main command emits `ctx.ReqLog.Report()`. Text encoding writes a tabular report with command, active state, start time, runtime, and optionally ID/args/options sorted by option key. `clear` calls `ReqLog.ClearInactive`. `set-time` parses a duration and updates request-log retention. State is in-memory request log only.

Dependencies and integration points: Uses old command `Context` from `commands` package, `go-ipfs-cmds`, tabwriter, and `ReqLogEntry` types. Exposed as a `NoLocal` command for RPC context.

Risks and test signals: Verbose output may expose command arguments/options with sensitive values if such options are logged. Runtime for active requests is computed at encode time and can vary. No direct tests in this subset.
