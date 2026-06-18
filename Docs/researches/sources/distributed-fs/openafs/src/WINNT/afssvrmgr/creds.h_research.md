<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.h

## Purpose
Declares credential and open-cell operations.

## Important APIs, Types, And Functions
`OpenCellDialog`, `NewCredsDialog`, `CheckForExpiredCredentials`, and `CheckCredentials`.

## Control Flow
No runtime flow.

## State And Persistence
No state declared; implementation updates global credentials and persisted warning/subset settings.

## Dependencies And Integration Points
Used by command, startup, and alert/scout code.

## Risks And Edge Cases
Header declares `OpenCellDialog` as `int`; implementation returns `BOOL`.

## Test Signals
Strict compile/signature checks and runtime truth-value handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.h -->
