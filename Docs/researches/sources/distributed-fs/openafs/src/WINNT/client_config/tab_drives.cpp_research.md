# sources/distributed-fs/openafs/src/WINNT/client_config/tab_drives.cpp

## Purpose
`tab_drives.cpp` implements the user drive-mapping tab and the advanced submount editor. It lets users view, activate/deactivate, add/edit/remove AFS drive mappings and manage named submounts.

## Important APIs, Types, and Functions
Main routines are `DrivesTab_DlgProc`, `DrivesTab_OnInitDialog`, `DrivesTab_FillList`, `DrivesTab_OnCheck`, `DrivesTab_EditMapping`, `DriveEdit_*`, `Submounts_*`, and `SubEdit_*`. It relies on `QueryDriveMapList`, `ActivateDriveMap`, `InactivateDriveMap`, `WriteDriveMappings`, `WriteActiveMap`, `AddSubMount`, `RemoveSubMount`, `DoMapShareChange`, and path/submount validators.

## Control Flow
Initialization loads current mappings into `g.Configuration.NetDrives` and renders mapped drives. Checking a row maps or unmaps the live drive and updates active-map persistence. Add/edit opens a drive editor, validates mount-root paths and submount names, unmaps old active mappings, maps the new target, updates the 26-entry map array, writes HKCU mappings, and refreshes. The Advanced button opens a submount property sheet whose apply rewrites all submount registry entries from the list.

## State and Persistence Behavior
User drive mappings persist under HKCU mappings and active-map keys. Machine submount definitions persist under HKLM. Live state is Windows network mappings. `g.Configuration.NetDrives` owns the current list and is freed/refilled during refreshes.

## Dependencies and Integration Points
This tab is conditionally added by `main.cpp` based on `ShowMountTab`. It integrates tightly with `drivemap.cpp`, General service state, LANA NetBIOS naming, and optional integrated-logon remapping.

## Risks and Edge Cases
The list check state is stored as item data but depends on external checklist/list behavior. Editing an active mapping unmaps first, so failure to activate the new mapping can leave no mapping. Submount apply removes all old submounts before adding new ones, making partial registry failures risky. Some string formatting uses ANSI buffers in TCHAR contexts.

## Test Signals
Tests should cover service stopped disabling controls, add/edit/remove of active and inactive mappings, persistent versus nonpersistent mappings, submount in-use deletion prevention, submount rename, registry rewrite failure, and integrated-logon `DoMapShareChange` invocation.
