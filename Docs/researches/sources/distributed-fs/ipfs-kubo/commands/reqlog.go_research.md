# Research: sources/distributed-fs/ipfs-kubo/commands/reqlog.go

Purpose: In-memory request log used by the active requests command and command context.

Important APIs/types/functions: `ReqLogEntry` stores timing, command, options, args, active state, and ID. `Copy` strips the back pointer. `ReqLog` stores entries, next ID, mutex, and retention duration. Methods include `AddEntry`, `ClearInactive`, `SetKeepTime`, `Report`, and `Finish`.

Control flow, state, and persistence: All mutations lock `ReqLog.lock`. `AddEntry` assigns monotonically increasing IDs and appends entries. Finished entries are cleaned opportunistically every 10 entries and by `ClearInactive`; active entries are retained regardless of age. `Report` returns copies to prevent callers from mutating internal entries. State is process-local only and resets on daemon restart.

Dependencies and integration points: Used by `commands.Context.LogRequest` and `core/commands/active.go`. Depends only on `sync` and `time`.

Risks and test signals: Cleanup cadence is approximate; a small number of stale inactive requests can remain until the next cleanup or explicit clear. Large option/argument values are retained in memory while entries are kept. No direct tests in this subset.
