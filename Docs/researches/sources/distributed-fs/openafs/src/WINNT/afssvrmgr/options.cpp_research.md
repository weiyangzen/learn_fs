# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.cpp

## Purpose
`options.cpp` implements the modal Options property sheet, specifically the General tab for global Server Manager preferences.

## Important APIs, Types, And Functions
The public entry point is `ShowOptionsDialog`. Internal functions are `Options_General_DlgProc`, `Options_General_OnInitDialog`, and `Options_General_OnApply`. The tab edits `gr.fServerLongNames`, `gr.fDoubleClickOpens`, `gr.fOpenMonitors`, `gr.fCloseUnmonitors`, and `gr.fWarnBadCreds`.

## Control Flow
`ShowOptionsDialog` creates a property sheet and adds the General tab. The dialog registers itself in `PropCache`, initializes checkboxes from `gr`, marks the sheet dirty on control changes, and on apply copies UI state back into `gr`. If long-server-name behavior changed, it calls `AfsClass_RequestLongServerNames` and refreshes the server list. If bad-credential warnings are enabled, it immediately checks credentials and posts the Credentials command when needed.

## State And Persistence
Global restored settings in `gr` are updated and persisted via `StoreSettings(REGSTR_SETTINGS_BASE, REGSTR_SETTINGS_PATH, REGVAL_SETTINGS, &gr, sizeof(gr), wVerGLOBALS_RESTORED)`. The property cache tracks the sheet while open.

## Dependencies And Integration Points
Dependencies include AfsAppLib property sheets/help, the property cache, credentials checking, global registry settings, `UpdateDisplay_Servers`, and the main window command path for `M_CREDENTIALS`.

## Risks And Edge Cases
The local `szCell` in `ShowOptionsDialog` is populated but unused. Applying settings can trigger asynchronous refresh and credential UI while the property sheet remains active. `fDoubleClickOpens` is encoded as numeric values rather than an enum, so radio-button mapping must stay consistent with consumers.

## Test Signals
Test each checkbox/radio path, dirty-state/apply behavior, registry persistence, server-list refresh after long-name toggling, warning-enabled credential prompt, help handling, and property-cache cleanup on sheet destruction.
