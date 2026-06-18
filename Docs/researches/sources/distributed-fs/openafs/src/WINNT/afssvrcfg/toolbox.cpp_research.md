<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.cpp

## Purpose
Provides small Win32 dialog/control helper wrappers shared by server configuration pages.

## Important APIs, Types, And Functions
Exports enable/show/text/check wrappers, elapsed-time adapters, listbox/spinner helpers, `ForceUpdateWindow`, `MoveWnd`, `MakeBold`, `MsgBox`, `HideAndDisable`, and `ShowAndEnable`.

## Control Flow
Most functions translate control IDs to HWNDs and call Win32 or AFS app-library helpers. `SecondsToElapsedTime` formats hours/minutes/seconds. `MoveWnd` converts screen coordinates to client coordinates before offsetting.

## State And Persistence
No durable state. Some functions return static buffers. `MakeBold` creates and assigns a new font without explicit deletion here.

## Dependencies And Integration Points
Depends on Win32 controls, `afsapplib` elapsed-time helpers, resource loading, and `ENABLE_STATE`.

## Risks And Edge Cases
Static buffers are overwritten and not thread-safe. Invalid `ENABLE_STATE` can leave `bEnable` undefined. Repeated `MakeBold` calls can leak fonts.

## Test Signals
UI smoke tests for enable/show/text/check behavior, elapsed-time round trips, spinner ranges, bold rendering, and control movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.cpp -->
