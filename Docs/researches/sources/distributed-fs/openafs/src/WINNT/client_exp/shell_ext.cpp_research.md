## sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.cpp

Purpose: Implements the COM shell extension for AFS context menus, icon overlays, infotips, `IPersistFile`, and property-sheet pages.

Important APIs/functions: Interface parts implement `IContextMenu`, `IShellExtInit`, `IShellIconOverlayIdentifier`, `IQueryInfo`, `IPersistFile`, and `IShellPropSheetExt`. `QueryContextMenu` builds the AFS submenu; `InvokeCommand` launches dialogs or calls `gui2fs` operations; `Initialize` captures selected paths and probes AFS/symlink/mount state; `AddPages` adds AFS file, volume, and ACL property pages.

Control flow/state: Per-object state tracks selected files, directory presence, AFS membership, symlink/mountpoint flags, overlay enablement, and tooltip file path. Global counters track COM interface references. Registry `ShellOption` controls overlay enablement, although `IsMemberOf` does not appear to check it.

Dependencies/integration: Uses MFC OLE, Explorer COM interfaces, Shlwapi, AFS registry paths, property page classes, all operation dialogs, and `gui2fs.cpp`.

Risks/tests: Explorer callback paths call cache-manager ioctls synchronously, so unavailable AFS can affect shell responsiveness. Refcounting uses global counters instead of per-interface object state. `Initialize` may leak `STGMEDIUM` on some failure paths, and `GetCommandString` casts narrow output as `LPTSTR`. Test multi-select, non-AFS selection suppression, folder-background init, menu command IDs, overlays disabled/enabled, tooltip allocation, property page lifecycle, and 32/64-bit CLSIDs.
