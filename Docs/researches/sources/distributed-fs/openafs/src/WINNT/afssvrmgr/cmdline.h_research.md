<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.h

## Purpose
Declares command-line parser outcomes and entry point.

## Important APIs, Types, And Functions
`CMDLINEOP` values are close app, normal, no cell dialog, and lookup error code. `ParseCommandLine` returns one of them.

## Control Flow
No runtime flow.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Requires `LPTSTR`; used by startup code.

## Risks And Edge Cases
Startup must distinguish `opNOCELLDIALOG` from `opNORMAL` to avoid duplicate cell UI.

## Test Signals
Startup integration for every enum value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.h -->
