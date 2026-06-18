# sources/distributed-fs/eos/mgm/proc/admin/Rtlog.cc

## Purpose
`Rtlog.cc` implements the legacy `ProcCommand::Rtlog()` command for retrieving recent in-memory log lines from the current MGM and/or FST endpoints.

## Important APIs, Types, And Functions
`ProcCommand::Rtlog()` reads opaque keys `mgm.rtlog.queue`, `mgm.rtlog.lines`, `mgm.rtlog.tag`, and optional `mgm.rtlog.filter`. It uses `Logging::GetInstance()`, `GetPriorityByString()`, `gLogMemory`, `gLogCircularIndex`, `FsView::gFsView.CollectEndpoints()`, and `gOFS->BroadcastQuery()`.

## Control Flow
The command requires root. It validates required opaque parameters and log priority tag. For local MGM requests (`.`, `*`, or the MGM queue), it iterates log priority buckets up to the requested tag and scans backward through each circular buffer, appending matching lines. For FST requests (`*` or non-local queue), it resolves endpoints, builds a `fst.pcmd=rtlog` query, broadcasts with a 10-second timeout, and appends response payloads.

## State, Persistence, And Dependencies
The command is read-only except for inherited output fields and `mDoSort`. It depends on global in-memory logging buffers protected by `g_logging.gMutex`, filesystem endpoint discovery from `FsView`, and MGM broadcast query transport.

## Integration Points
This is an opaque proc admin command, not a protobuf command. It federates MGM-side log access with FST-side `rtlog` handling by issuing a query to storage endpoints.

## Risks
`lines` is parsed with `atoi()` and lacks range validation, so very large values can scan repeatedly until the circular buffer empties. The local log mutex is locked and unlocked once per priority bucket while building output. Filter defaulting to a single space means blank or unusual log lines can be skipped. Broadcast response aggregation does not annotate endpoint boundaries.

## Test Signals
Test root gating, missing parameters, invalid tags, local-only queues, wildcard queues, FST endpoint misses, broadcast failures, filter behavior, and line limits larger than the circular buffer. Concurrency tests should stress log access while writers append.
