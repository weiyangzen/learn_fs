# sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.h

## Purpose
`tab_hosts.h` declares the Hosts tab dialog procedure and commit hook.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK HostsTab_DlgProc(HWND, UINT, WPARAM, LPARAM)` and `BOOL HostsTab_CommitChanges(BOOL fForce)`.

## Control Flow
The property sheet uses the dialog procedure. General tab apply/start logic calls `HostsTab_CommitChanges` to flush CellServDB edits before validating the configured cell or starting the service.

## State and Persistence Behavior
The header has no state. Implementation state lives in `g.Configuration.CellServDB` until committed to disk.

## Dependencies and Integration Points
It is included by `afs_config.h`, `main.cpp`, and `tab_general.cpp`. The commit hook is part of the cross-tab apply order.

## Risks and Edge Cases
If the Hosts tab window is absent, `HostsTab_CommitChanges` returns success, which is needed for modes without the tab but can hide skipped writes if tab creation fails unexpectedly.

## Test Signals
Compile coverage plus property-sheet tests with the Hosts tab present and absent should verify commit behavior and failure propagation.
