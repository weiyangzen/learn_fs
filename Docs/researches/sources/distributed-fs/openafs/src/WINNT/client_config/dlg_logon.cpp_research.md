# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_logon.cpp

## Purpose
`dlg_logon.cpp` implements the Advanced Logon dialog for login retry interval and whether failed integrated logons should be reported silently.

## Important APIs, Types, and Functions
The main routines are `Logon_DlgProc`, `Logon_OnInitDialog`, `Logon_OnOK`, `Logon_OnApply`, and `Logon_OnCancel`. It calls `Config_GetLoginRetryInterval`, `Config_SetLoginRetryInterval`, `Config_GetFailLoginsSilently`, and `Config_SetFailLoginsSilently`.

## Control Flow
On first initialization it loads registry-backed values into `g.Configuration` and static dialog state, creates a spinner with 5 to 180 bounds, localizes yes/no labels, and selects the current fail-silently flag. OK captures spinner and combo state. Apply persists changed values and updates `g.Configuration`.

## State and Persistence Behavior
Dialog state is static and reset on cancel. Both options are global registry values. `Config_SetLoginRetryInterval` and `Config_SetFailLoginsSilently` do not set the restart flag in `config.cpp`, implying they are read by logon-provider paths without requiring AFSD restart.

## Dependencies and Integration Points
The dialog is launched by `tab_advanced.cpp`; `Logon_OnApply` is called from the advanced commit path. It depends on custom spinner and combo helpers included through `afs_config.h`.

## Risks and Edge Cases
Like other advanced subdialogs, OK does not reset `fFirstTime`, so subsequent opens in the same process show staged state rather than re-reading registry. Combo indexes are assumed to map directly to boolean values. There is no explicit validation for registry values outside spinner bounds before control initialization.

## Test Signals
Tests should cover default values, min/max spinner behavior, yes/no localization, staged OK plus Advanced Apply persistence, cancel reset, and no unintended restart prompt.
