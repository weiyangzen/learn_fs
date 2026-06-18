# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_misc.cpp

## Purpose
`dlg_misc.cpp` implements the Advanced Miscellaneous Parameters dialog for probe interval, server threads, daemon count, sysname, root volume, and mount directory.

## Important APIs, Types, and Functions
Core routines are `Misc_DlgProc`, `Misc_OnInitDialog`, `Misc_OnOK`, `Misc_OnApply`, and `Misc_OnCancel`. It uses `Config_GetProbeInt`, `Config_SetProbeInt`, `Config_GetNumThreads`, `Config_SetNumThreads`, `Config_GetNumDaemons`, `Config_SetNumDaemons`, `Config_GetSysName`, `Config_SetSysName`, `Config_GetRootVolume`, `Config_SetRootVolume`, `Config_GetMountRoot`, and `Config_SetMountRoot`.

## Control Flow
First initialization reads current values into `g.Configuration` and local globals, sets bounded spinners, and populates text fields. OK copies UI values into static globals. Apply compares staged values to `g.Configuration`, applies each changed value in sequence, and updates the global snapshot.

## State and Persistence Behavior
The dialog stores staged values in file-scope globals, with `fFirstTime` reset only on cancel. Probe interval is applied live through a pioctl when the service is running; thread/daemon/root/mount settings are registry-backed and mark restart required. Sysname is applied live and persisted when possible.

## Dependencies and Integration Points
`tab_advanced.cpp` opens this dialog and calls `Misc_OnApply` as part of the Advanced tab commit. The general tab later uses `g.fNeedRestart` to offer service restart after changes.

## Risks and Edge Cases
The file has `#if undef` blocks for old LANA UI, suggesting dead code around adapter selection. `GetDlgItemText` uses `sizeof(szSysName)` for TCHAR count, unsafe under Unicode. Partial apply can leave earlier values persisted if a later setter fails.

## Test Signals
Tests should verify spinner bounds, live probe pioctl behavior, sysname whitespace validation in `config.cpp`, restart flagging for thread/daemon/root/mount changes, and partial-failure UI behavior.
