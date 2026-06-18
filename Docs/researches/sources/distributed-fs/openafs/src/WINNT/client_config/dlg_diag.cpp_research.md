# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_diag.cpp

## Purpose
`dlg_diag.cpp` implements the Advanced Diagnostics dialog for trace buffer size, trap-on-panic, and report-session-startups options.

## Important APIs, Types, and Functions
Key routines are `Diag_DlgProc`, `Diag_OnInitDialog`, `Diag_OnOK`, `Diag_OnApply`, `Diag_OnCancel`, and the helper `SetUpYesNoCombo`. It uses `Config_GetTraceBufferSize`, `Config_SetTraceBufferSize`, `Config_GetTrapOnPanic`, `Config_SetTrapOnPanic`, `Config_GetReportSessionStartups`, and `Config_SetReportSessionStartups`.

## Control Flow
On first initialization it reads values into `g.Configuration` and file-static dialog variables. It creates a spinner bounded between 3000 and 32000 for trace buffer size and two yes/no combo boxes. OK copies UI state to static variables; Apply compares those variables with `g.Configuration` and persists only changed values.

## State and Persistence Behavior
Static `fFirstTime` gates one-time reads; cancel resets it. Trace size and panic/session flags are persisted under global registry settings. Trace size and trap-on-panic changes mark `g.fNeedRestart` through `config.cpp`, while report-session-startups does not.

## Dependencies and Integration Points
The dialog is launched by `tab_advanced.cpp`; `Diag_OnApply` is called from `AdvancedTab_OnApply` so changes are committed with the rest of Advanced settings.

## Risks and Edge Cases
Repeated `WM_INITDIALOG` after OK may not reload from registry because `fFirstTime` remains false. Combo selection relies on index 0/1 mapping to `FALSE`/`TRUE`; changes to `CB_AddItem` semantics would break it. There is no validation beyond spinner bounds.

## Test Signals
Tests should check initial defaults, yes/no combo mapping, persistence only when changed, cancel discarding staged state, and restart prompt behavior after trace or trap changes.
