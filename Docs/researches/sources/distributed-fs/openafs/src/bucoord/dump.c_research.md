# sources/distributed-fs/openafs/src/bucoord/dump.c

## Purpose
Runs dump/restore helper jobs and tape coordinator operations for the backup coordinator. It owns the global dump-task slots, launches asynchronous LWP worker processes, packages volume dumps into butc RPC structures, connects to tape coordinators, and exposes label/read/scan helpers.

## Important APIs, Types, And Functions
Global state is `bc_dumpTasks[BC_MAXSIMDUMPS]`. Main functions are `bc_Dumper`, `bc_StartDmpRst`, `bc_DmpRstStart`, `freeDumpTaskVolumeList`, `bc_LabelTape`, `bc_ReadLabel`, `bc_ScanDumps`, `bc_GetConn`, `CheckTCVersion`, and `ConnectButc`. The central data type is `struct bc_dumpTask`, populated by `bc_StartDmpRst` and consumed by `bc_Dumper` or `bc_Restorer`.

## Control Flow
`bc_StartDmpRst` finds a free task slot, copies command state into it, records destination/parent/level/port/expiration/append/dry-run fields, and creates an LWP helper process. `bc_DmpRstStart` calls the selected worker function, records `lastTaskCode` on failure, frees volume lists and copied strings, releases the port array, and clears `BC_DI_INUSE`. `bc_Dumper` connects to the selected butc, converts each `bc_volumeDump` into a `tc_dumpDesc`, constructs dump/tape naming fields, calls `TC_PerformDump`, and creates a status node for monitoring. Label, read-label, and scan-dumps helpers perform similar butc RPC submission and status setup.

## State And Persistence
The file maintains transient task slot state and status queue nodes. Persistent effects are delegated to tape coordinator operations and later BUDB updates performed by butc. `bc_GetConn` caches the chosen RX security class and index in static variables, so authentication mode is effectively fixed after the first tape coordinator connection.

## Dependencies And Integration Points
Depends on LWP, RX, OpenAFS auth/cell config, butc RPC stubs, TC status constants, `status.c`, `commands.c` utilities, and `tape_hosts.c` configuration state. `commands.c` calls `bc_StartDmpRst` for dump and restore commands, and `restore.c` supplies `bc_Restorer`.

## Risks And Test Signals
Task slots are scanned and marked without an explicit lock, so concurrent command dispatch can race if multiple LWPs enter start logic. Several string copies into RPC fields assume earlier command validation. `bc_LabelTape` and other error paths can return without destroying RX connections. Static security caching in `bc_GetConn` may surprise mixed `-localauth`/`-nobutcauth` sessions. Test signals include slot exhaustion, LWP creation failure cleanup, dump RPC request contents, status node creation, tape coordinator version mismatch, authenticated/null/fallback butc connections, label/read/scantape flows, and cleanup after worker completion.
