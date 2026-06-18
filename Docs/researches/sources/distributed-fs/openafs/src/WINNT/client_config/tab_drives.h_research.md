# sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.h

## Purpose
`tab_drives.h` declares the drive-mapping tab dialog procedure.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK DrivesTab_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

## Control Flow
`main.cpp` registers this procedure as the Drives property-sheet page when the mount tab is enabled. All drive and submount workflows are handled inside `tab_drives.cpp`.

## State and Persistence Behavior
The header has no state. Implementation state is stored in `g.Configuration.NetDrives`, HKCU/HKLM mapping registry keys, and live WNet/DOS-device mappings.

## Dependencies and Integration Points
It is included by `main.cpp` and `afs_config.h`. Its presence in the central header makes the Drives tab available to other modules through the property-sheet framework.

## Risks and Edge Cases
The small header is low risk; the main risk is that consumers have no commit function analogous to other tabs, because mapping changes are applied immediately from the tab rather than on property-sheet apply.

## Test Signals
Compile coverage and UI smoke tests confirming `DrivesTab_DlgProc` receives initialization/command/help messages are sufficient for the header.
