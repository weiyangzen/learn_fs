# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfigdlg.c

## Purpose

`afsconfigdlg.c` implements NetIDMgr configuration dialog procedures for AFS settings. It handles global AFS enablement, per-identity token configuration via the new-credentials dialog logic, OpenAFS service status/start/stop controls, version/company display, startup shortcut suppression, and context help.

## Important APIs, types, and functions

`afs_cfg_ids_proc` manages the global "obtain AFS tokens" option backed by `csp_params/AFSEnabled`. `afs_cfg_id_proc` wraps `afs_dlg_proc` for identity-specific configuration and writes identity data on apply. `set_service_status` queries `TransarcAFSDaemon`, maps service status through localized CSV strings, updates buttons and progress bar, and schedules polling during pending transitions. `afs_cfg_show_last_error` formats Windows errors for UI display. `afs_cfg_get_afscreds_shortcut` checks the common Startup folder for `AFS Credentials.lnk`. `afs_cfg_main_proc` drives the main service/config page.

## Control flow

`afs_cfg_ids_proc` allocates dialog state on `WM_INITDIALOG`, reads `AFSEnabled`, updates a checkbox, marks the config node modified on click, writes the value on `WMCFG_APPLY`, and frees state on destroy.

`afs_cfg_id_proc` delegates initialization to `afs_dlg_proc`, creates an identity from the selected config node name, populates `afs_dlg_data` with existing credentials and AFS enablement, marks the dialog as configuration mode, and on apply writes per-identity cell data. Destroy releases the identity and delegates cleanup.

`afs_cfg_main_proc` initializes by reading `Disableafscreds`, reading the OpenAFS service `ImagePath` from HKLM, extracting version/company fields from file version resources, and calling `set_service_status`. Button commands call `ServiceControl` to start/stop the daemon, shell out to `AFS_CONFIG.EXE`, or mark shortcut settings modified. Apply writes `Disableafscreds` and deletes the common-startup shortcut if requested. Timer messages refresh service status, and `WM_HELP` routes control-specific help through `afs_html_help`.

## State and persistence behavior

State is stored in per-dialog heap allocations, `DWLP_USER`, NetIDMgr configuration spaces, the Windows service control manager, HKLM service registry metadata, file version resources, and the common Startup folder shortcut. The global enable flag and `Disableafscreds` setting persist in NetIDMgr plugin config.

## Dependencies and integration points

The code depends on `afscred.h`, NetIDMgr configuration UI APIs, `afs_dlg_proc` and credential data helpers from the new-credentials code, `mstring.h` CSV conversion, Windows common controls, Shell APIs, registry APIs, service helpers from `afsfuncs.c`, localized resources, and HTML help.

## Risks and edge cases

`set_service_status` indexes localized CSV strings by raw Windows service status numeric value; malformed resource strings fall back to the first "unknown" entry. Progress calculation uses `GetTickCount` and can behave oddly across wraparound. `RegCloseKey(service_key)` is called only after successful open, but early jumps require careful maintenance. `kmm_get_plugin_config` return values are not always checked before writes. Deleting the startup shortcut is one-way and does not recreate it when the box is unchecked.

## Test signals

UI tests should verify checkbox persistence, per-identity apply behavior, service stopped/running/pending button enablement, timer progress updates, version/company extraction from the service binary, error dialogs for service-control failures, `AFS_CONFIG.EXE` launch failure, startup shortcut deletion, and context help routing.
