# sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.h

## Purpose
`tab_general.h` declares the General tab dialog procedure.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK GeneralTab_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

## Control Flow
`main.cpp` registers this procedure as the first tab for normal client configuration mode. The implementation handles initialization, apply, refresh, service control, and help messages.

## State and Persistence Behavior
The header has no state. Implementation state spans `g.Configuration`, `g.fNeedRestart`, service status polling, and registry-backed settings.

## Dependencies and Integration Points
It is included by `main.cpp` and `afs_config.h`, placing the General tab in the central UI contract.

## Risks and Edge Cases
The header is low risk. Because there is no separate public commit function, other tabs do not force General changes; instead the property sheet sends `IDAPPLY` to the tab.

## Test Signals
Compile coverage and property-sheet smoke tests for `GeneralTab_DlgProc` are sufficient at the header level.
