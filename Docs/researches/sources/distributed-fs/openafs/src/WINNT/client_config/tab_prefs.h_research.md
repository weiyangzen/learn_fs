# sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.h

## Purpose
`tab_prefs.h` declares the Server Preferences tab dialog procedure and commit hook.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK PrefsTab_DlgProc(HWND, UINT, WPARAM, LPARAM)` and `BOOL PrefsTab_CommitChanges(BOOL fForce)`.

## Control Flow
`main.cpp` registers the dialog procedure on NT systems. General or property-sheet apply paths can use the commit function to force pending preference changes to be sent to the cache manager.

## State and Persistence Behavior
The header has no state. Implementation state is in `g.Configuration.pFServers`, `g.Configuration.pVLServers`, `g.Configuration.fChangedPrefs`, and worker-thread statics.

## Dependencies and Integration Points
It is included by `main.cpp` and `afs_config.h`. It completes the cross-tab commit model along with Hosts and Advanced.

## Risks and Edge Cases
The commit hook succeeds if the tab is absent. This is appropriate for non-NT modes but means missing tab creation will skip preference application.

## Test Signals
Compile coverage and property-sheet tests should verify `PrefsTab_CommitChanges` behavior with no tab, unchanged preferences, changed preferences, and failed `Config_SetServerPrefs`.
