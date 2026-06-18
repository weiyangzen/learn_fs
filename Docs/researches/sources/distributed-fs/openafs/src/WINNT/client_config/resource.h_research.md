# sources/distributed-fs/openafs/src/WINNT/client_config/resource.h

## Purpose
`resource.h` defines numeric resource identifiers for localized strings, dialogs, icons, and controls used by the Windows AFS client configuration UI.

## Important APIs, Types, and Functions
It defines string IDs for titles, service states, warnings, errors, column labels, and validation messages; dialog IDs such as `IDD_GENERAL_NT`, `IDD_PREFS_NT`, `IDD_HOSTS_NT`, `IDD_DRIVE_EDIT`, and advanced subdialogs; icon IDs; and control IDs such as `IDC_STATUS`, `IDC_CELL`, `IDC_LIST`, `IDC_CACHE_SIZE`, `IDC_GLOBAL_DRIVE_LIST`, and `IDC_NICSELECTION`.

## Control Flow
There is no executable control flow. The IDs are consumed by resource scripts and by code calling `GetString`, `ModalDialog`, `PropSheet_AddTab`, `GetDlgItem`, and WinHelp.

## State and Persistence Behavior
The header has no state. The stability of numeric IDs is a persistence-like contract with compiled resources and help mappings.

## Dependencies and Integration Points
Every UI source file depends on this header indirectly through `afs_config.h`. It must stay synchronized with `afs_config.rc` language files and `help.hid`.

## Risks and Edge Cases
Duplicate control IDs are intentionally reused in different dialogs, so handlers must be scoped to the active dialog. Changing numeric values can break resource binding, help contexts, or saved UI automation tests. Several IDs share the same value for aliases, such as `IDD_DRIVES`/`IDD_DRIVES_NT` and `IDC_ADVANCED`/`IDC_IMPORT`.

## Test Signals
Resource compilation is the primary signal. UI smoke tests should open each dialog and verify controls can be found by the expected IDs, with localized strings loaded for all string IDs referenced by code.
