<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.h

## Purpose
Declares drive-list setup and refresh APIs for AFS partition selection UI.

## Important APIs, Types, And Functions
`SetupDriveList(HWND)` binds and initializes a list control. `UpdateDriveList()` refreshes the bound control.

## Control Flow
No runtime flow; callers must setup before update.

## State And Persistence
Implementation uses a single module-static HWND, so only one active drive list is represented.

## Dependencies And Integration Points
Includes `toolbox.h`; implemented by `volume_utils.cpp`.

## Risks And Edge Cases
Multiple concurrent drive lists or update-before-setup can use stale/null state.

## Test Signals
Dialog create/destroy/recreate flows and update-after-setup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.h -->
