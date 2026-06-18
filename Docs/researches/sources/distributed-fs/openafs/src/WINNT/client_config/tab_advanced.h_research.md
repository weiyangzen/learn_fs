# sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.h

## Purpose
`tab_advanced.h` declares the Advanced tab dialog procedure and commit hook.

## Important APIs, Types, and Functions
It exposes `BOOL CALLBACK AdvancedTab_DlgProc(HWND, UINT, WPARAM, LPARAM)` and `BOOL AdvancedTab_CommitChanges(BOOL fForce)`.

## Control Flow
The property sheet uses the dialog procedure for UI messages. Other tabs, especially General, call `AdvancedTab_CommitChanges` to force pending advanced settings to persist before service start/restart logic.

## State and Persistence Behavior
The header has no state. Implementation state lives in `g.Configuration` and subdialog statics.

## Dependencies and Integration Points
It is included by `main.cpp`, `tab_general.cpp`, and `afs_config.h`, binding the Advanced tab into the application tab set and global apply path.

## Risks and Edge Cases
The commit hook returns success if the Advanced tab window does not exist, so hidden or uncreated tabs cannot block apply. That is intentional for modes where the tab is absent, but tests should verify no settings are silently skipped in NT mode.

## Test Signals
Compile coverage and a property-sheet smoke test that invokes `AdvancedTab_CommitChanges(TRUE/FALSE)` with tab present and absent are sufficient.
