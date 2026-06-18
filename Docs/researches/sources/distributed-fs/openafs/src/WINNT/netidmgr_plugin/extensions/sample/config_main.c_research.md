# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/config_main.c

## Purpose
Provides a minimal sample NetIDMgr configuration dialog procedure for an extension plugin.

## Important APIs, Types, And Functions
`config_main_dlg_data` holds the configuration node handle. `config_dlgproc()` handles `WM_INITDIALOG`, `KHUI_WM_CFG_NOTIFY` with `WMCFG_APPLY`, and `WM_DESTROY`.

## Control Flow
On initialization, it allocates and zeroes dialog data, stores the held config node from `lParam`, and saves the pointer in `DWLP_USER`. On apply, it currently returns `TRUE` without applying real settings. On destroy, it frees dialog data and clears `DWLP_USER`.

## State And Persistence
Only transient dialog state exists. No configuration values are read or written in the template.

## Dependencies And Integration Points
Included only if the sample plugin enables configuration panels in `plugin.c`. It relies on NetIDMgr config notifications and Win32 dialog storage.

## Risks
The current implementation is a stub and would falsely accept Apply with no validation or persistence. It uses `assert()` after `malloc`; release builds may continue with null if allocation handling is changed poorly.

## Test Signals
When extended, test config node registration, panel creation/destruction, Apply behavior, modified/applied flags, and persistence of any added fields.
