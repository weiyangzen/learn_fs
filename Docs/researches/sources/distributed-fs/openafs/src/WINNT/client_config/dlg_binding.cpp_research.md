# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_binding.cpp

## Purpose
`dlg_binding.cpp` implements the Advanced Binding dialog for selecting which LANA/NIC the OpenAFS SMB server binds to, or using the default adapter.

## Important APIs, Types, and Functions
Key routines are `Binding_DlgProc`, `Binding_OnInitDialog`, `Binding_OnOK`, `Binding_OnApply`, `Binding_OnCancel`, and `GetAdapterNumber`. It uses `Config_GetLanAdapter`, `Config_SetLanAdapter`, `lana_FindLanaByName`, and `lana_GetAfsNameString`.

## Control Flow
The first initialization loads the configured LAN adapter into static dialog state, enumerates LANA adapters into a combo box, selects the configured adapter if present, and displays the resulting AFS NetBIOS name. Toggling default NIC or selecting a combo entry recalculates `nLanAdapter` and updates the message. OK stores the chosen adapter in static state; Apply persists it if changed.

## State and Persistence Behavior
State is cached in file-static `fFirstTime`, `nLanAdapter`, `isGateway`, and `lanainfo`. Persistence is through the `LANadapter` global registry value via `Config_SetLanAdapter`, which marks the service for restart.

## Dependencies and Integration Points
The dialog is invoked by `tab_advanced.cpp` and participates in `AdvancedTab_OnApply`. It depends on the LANA helper library and the global configuration singleton.

## Risks and Edge Cases
`lanainfo` is allocated by helper code but freed with `delete`, which may not match the allocator. `fFirstTime` is only reset on cancel, so repeated OK/open cycles reuse cached data. If adapter enumeration fails, later combo operations may still assume `lanainfo` is valid. `WM_GETTEXT` length parameters use `sizeof(selected)` as TCHAR count, which is only correct in ANSI builds.

## Test Signals
Tests should cover no adapters, default NIC toggle, explicit adapter selection, stale configured adapter, gateway flag affecting displayed AFS name, cancel without persistence, and apply marking restart-required state through `Config_SetLanAdapter`.
