<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.h

## Purpose
Defines alert types, payloads, storage, timing constants, and alert APIs.

## Important APIs, Types, And Functions
`ALERT`, `ALERTINFO`, `OBJECTALERTS`, `nAlertsMAX`, timing constants, and prototypes for defaults, initialization, query, description/remedy/button, mutation, and Scout scheduling.

## Control Flow
No implementation flow; structures define how alert state is interpreted.

## State And Persistence
`OBJECTALERTS` is embedded in persisted preference structs, with some runtime fields reset on load.

## Dependencies And Integration Points
Requires `LPIDENT`, `FILESETSTATE`, `SYSTEMTIME`, and Windows/AFS types.

## Risks And Edge Cases
Anonymous nested structs rely on compiler support. Fixed-size arrays can truncate alerts. Raw struct persistence is layout-sensitive.

## Test Signals
Compile portability and runtime coverage for every alert variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/alert.h -->
