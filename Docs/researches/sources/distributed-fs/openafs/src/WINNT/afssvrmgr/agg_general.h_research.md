<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.h

## Purpose
Declares aggregate preference and selection helper APIs.

## Important APIs, Types, And Functions
Exports load/save preferences and focused/selected aggregate retrieval.

## Control Flow
No runtime flow.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Requires `LPIDENT` and `HWND`; used by dispatch, properties, and aggregate UI.

## Risks And Edge Cases
Object kind is not enforced by the signatures.

## Test Signals
Compile integration and aggregate create/preference attach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.h -->
