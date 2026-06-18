# sources/distributed-fs/openafs/src/WINNT/client_config/dlg_automap.cpp

## Purpose
`dlg_automap.cpp` implements the Advanced tab's Global AutoMapper dialog, allowing administrators to view, add, edit, and remove machine-wide drive mappings stored under the `GlobalAutoMapper` registry key and applied as DOS drive mappings.

## Important APIs, Types, and Functions
Key routines are `AutoMap_DlgProc`, `AutoMap_OnInitDialog`, `ShowDriveList`, `UpdateRegistry`, `DefineDosDrive`, `AutoMap_OnAdd/Edit/Remove/Select`, `GetSelectedDrive`, and the nested `AutoMapEdit_*` dialog functions. It uses `DRIVEMAP`, `DRIVEMAPLIST`, `MountDOSDrive`, `DisMountDOSDrive`, `PathToSubmount`, `IsValidSubmountName`, and `AdjustAfsPath`.

## Control Flow
Initialization configures a fastlist, reads the global drive list through `Config_GetGlobalDriveList`, and renders drive/path rows. Add/edit opens `IDD_GLOBAL_DRIVES_ADDEDIT`, validates drive/path/submount inputs, resolves or creates a submount, then calls `DefineDosDrive`. Successful map/unmap operations update the registry and in-memory `GlobalDrives` array before refreshing the list.

## State and Persistence Behavior
`GlobalDrives` is a static snapshot for the dialog. Persistent state is HKLM `...\GlobalAutoMapper`, where value names are drive letters like `X:` and value data is the submount. Live state changes are made through `MountDOSDrive`/`DisMountDOSDrive`.

## Dependencies and Integration Points
The dialog is launched from `tab_advanced.cpp`. It shares validation and mapping primitives with the user drive tab and depends on OpenAFS mount-root globals initialized by `fs_utils_InitMountRoot`.

## Risks and Edge Cases
`UpdateRegistry` writes string lengths without multiplying by `sizeof(TCHAR)`, which is unsafe in Unicode builds. `ShowDriveList` ignores its `drives` parameter and always reads `GlobalDrives`. Editing first removes the old mapping, then tries to add the new one, so a failed add can leave the old mapping gone. Registry update failure after a successful map can leave live and persistent state divergent.

## Test Signals
Tests should exercise add/edit/remove with valid and invalid submounts, paths outside the mount root, drive-letter conflicts, map succeeds/registry fails, registry succeeds/map fails, and list refresh after direct registry edits.
