# sources/distributed-fs/openafs/src/bucoord/volstub.c

## Purpose
Provides small VLDB/volserver helper wrappers used by backup commands. It looks up VLDB entries by volume id and determines the timestamp to record for a volume image.

## Important APIs, Types, And Functions
Exports `bc_GetEntryByID` and `volImageTime`. `bc_GetEntryByID` wraps `ubik_VL_GetEntryByID`. `volImageTime` uses `UV_ListOneVolume` for non-RW volumes and interprets `struct volintInfo`.

## Control Flow
`bc_GetEntryByID` directly delegates to VLDB. `volImageTime` returns current time for RW volumes. For RO/BK or unknown requested types it asks the volserver for one volume’s info; RW results again use current time, RO/BK results use `creationDate`, and unknown types return an error after logging.

## State And Persistence
No state is stored and nothing is persisted. The returned clone/image time is written into caller-owned fields such as `bc_volumeDump.cloneDate`.

## Dependencies And Integration Points
Depends on VLDB Ubik stubs, volser/UV helpers, `volintInfo`, and com_err. `commands.c` calls `volImageTime` during dry-run incremental dump checks to warn when a volume timestamp did not change.

## Risks And Test Signals
`UV_ListOneVolume` allocation ownership is not released in this function, which may leak depending on API contract. Returning success with clone date `0` on query failure intentionally lets dump planning continue with a warning. Test signals include RW current-time behavior, backup/readonly creation-date behavior, volserver query failure warning, unknown volume type failure, and VLDB lookup by id/type.
