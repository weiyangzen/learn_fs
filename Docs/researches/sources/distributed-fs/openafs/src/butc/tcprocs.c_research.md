# sources/distributed-fs/openafs/src/butc/tcprocs.c

## Purpose
`tcprocs.c` implements TC RPC service entry points. It checks permissions, copies RPC arguments into local state, creates status nodes, starts detached workers, and audits calls.

## Important APIs, Types, and Functions
`callPermitted()` enforces either `allow_unauth` or `afsconf_SuperIdentity()`. Copy helpers are `CopyDumpDesc()`, `CopyRestoreDesc()`, and `CopyTapeSetDesc()`. Public wrappers include `STC_LabelTape`, `STC_PerformDump`, `STC_PerformRestore`, `STC_ReadLabel`, `STC_RestoreDb`, `STC_SaveDb`, `STC_ScanDumps`, `STC_TCInfo`, and `STC_DeleteDump`; static `S*` implementations do the worker setup.

## Control Flow
Each public wrapper calls a static backend and records an audit event. Asynchronous backends check mode and permissions, allocate task id/node and request payloads, initialize a status node with `STARTING` cleared, then create a detached pthread/LWP for the real worker. Failure cleanup deletes status nodes and frees task state. `SReadLabel()` is synchronous and returns task id 0.

## State and Persistence Behavior
This file creates volatile task/status state and audit records. It does not itself write tape media or BUDB dump rows; background workers do that after RPC return. Returned task ids are used by status/abort/end-status RPCs.

## Dependencies and Integration Points
Depends on globals initialized by `tcmain.c`, node management in `list.c`, status functions from shared `bucoord/status.c`, workers in `dump.c`, `lwps.c`, `recoverDb.c`, and DB save/restore code, plus audit infrastructure.

## Risks and Test Signals
Risks include fixed-size `strcpy()` from RPC data, limited argument validation, unlocked task-list insertion, and the asynchronous success contract. Test permission modes, worker status creation and cleanup on spawn failure, mode rejection for tape-only/XBSA-only operations, copy helper correctness, zero-length arrays, append flag behavior under XBSA, and audit event emission.
