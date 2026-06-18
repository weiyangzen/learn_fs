# Research: subset-b-007740

Grouped research for OpenAFS Windows Explorer extension and OSI utility files. Each section preserves the source path and is wrapped with reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.cpp

Purpose: Implements the Explorer-facing equivalents of many `fs` commands: flush, ACL read/write/copy/clean, mount point and symlink operations, volume quota/status, token display, server/cell lookup, owner/group lookup, and Unix mode bits.

Important APIs/functions: Public entry points match `gui2fs.h`, including `Flush`, `FlushVolume`, `GetRights`, `SaveACL`, `CopyACL`, `ListMount`, `MakeMount`, `RemoveMount`, `GetVolumeInfo`, `SetVolInfo`, `GetTokenInfo`, `MakeSymbolicLink`, `GetCellName`, `GetServers`, `GetOwner`, `GetGroup`, `GetUnixModeBits`, and `SetUnixModeBits`. Internal helpers handle UTF-8 path conversion, AFS error mapping, ACL list mutation, NetBIOS root repair, freelance-root detection, and AFS Client Admin membership checks.

Control flow/state: Most operations build a `ViceIoctl` blob and call `pioctl_T`/`pioctl_utf8`; results either populate MFC `CStringArray` data for dialogs or show immediate message boxes. Process-local static state includes the VLDB client pointer, RX-init flag, cached NetBIOS name, and cached admin membership. Registry reads provide `NetbiosName` and shell/admin policy.

Dependencies/integration: Bridges MFC dialogs, `msgs.cpp`, `HOURGLASS`, `fs_acl`, cache-manager `VIOC*` ioctls, token APIs, protection-server APIs, registry helpers, and host lookup. `shell_ext.cpp`, property pages, ACL dialogs, and volume dialogs call this file heavily.

Risks/tests: Fixed buffers and manual UTF-8 conversions need long Unicode path tests. `CopyACL` appears to use `normal[i]` while copying negative entries, which can corrupt copied negative ACL names. Several paths ignore return values (`SetCacheSizeCmd`, `SetUnixModeBits`) or rely on global `errno`. Test AFS/non-AFS paths, UNC NetBIOS freelance roots, ACL round trips, symlink/mount create/remove, quota updates, token enumeration, owner/group PRDB lookup, and unavailable cache-manager/service cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.h

Purpose: Declares the GUI shell extension's callable AFS operation layer, turning Explorer and dialog commands into typed C++ functions.

Important APIs/types: Exposes file/cache operations, ACL operations, mount point/symlink operations, volume info setters/getters, server/cell/token lookup, path classification, owner/group lookup, and Unix mode bit access. The `WHICH_CELLS` enum controls server-status scope.

Control flow/state: The header has no runtime state; it defines the contract implemented in `gui2fs.cpp`. Default parameters decide whether path-sensitive queries follow mount points/symlinks.

Dependencies/integration: Requires `CVolInfo`, MFC `CString`/`CStringArray`, and Win32/MFC `BOOL`/`LONG` types. Included by shell extension command handlers and multiple dialogs.

Risks/tests: Any prototype mismatch breaks many Explorer commands. Compile tests should include all consumers, and behavioral tests should cover default `bFollow` values and multi-file array operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/help.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/help.cpp

Purpose: Chooses the appropriate legacy WinHelp file for the shell extension and dispatches help-context requests.

Important APIs/functions: `SetHelpPath` derives a help-file path from the DLL/default help path and chooses `afs-nt.hlp` on NT-family systems or `afs-light.hlp` otherwise. `ShowHelp` calls `WinHelp` with `HELP_CONTEXT`.

Control flow/state: `IsWindowsNT` caches the OS-platform check in static booleans. `strHelpPath` is global process state initialized once by application startup before dialogs invoke help.

Dependencies/integration: Uses MFC `CString`, Win32 `GetVersionEx`, and constants from `help.h`. Dialogs call `ShowHelp` in `IDHELP` handlers.

Risks/tests: `WinHelp` is legacy and may be absent on modern Windows. `SetHelpPath` assumes a backslash exists in the input path. Test startup before help invocation, NT/light selection, missing help file behavior, and every dialog help ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/help.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/help.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/help.h

Purpose: Centralizes help-file names, WinHelp command type, help context IDs, and the two help API declarations used by dialogs.

Important APIs/types: Defines `HELPFILE_NATIVE`, `HELPFILE_LIGHT`, `HELPTYPE`, and context IDs for authentication, tokens, ACLs, volumes, partition info, mount points, server status, submounts, and symlinks. Declares `SetHelpPath` and `ShowHelp`.

Control flow/state: No runtime logic; IDs here must match localized `.hlp` content and dialog handlers.

Dependencies/integration: Included via `stdafx.h`, so most client-exp modules see the help API. Resource and help authoring must remain synchronized.

Risks/tests: Duplicate or stale IDs route users to wrong pages; `DOWN_SERVERS_HELP_ID` intentionally aliases another ID. Test every `IDHELP` button and ensure native/light help files contain the declared contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/help.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/hourglass.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/hourglass.h

Purpose: Provides an RAII helper that switches the cursor to a wait cursor for the lifetime of a stack object.

Important APIs/types: `HOURGLASS` stores the previous `HCURSOR` in its constructor and restores it in its destructor. The default cursor resource is `IDC_WAIT`.

Control flow/state: Used by long-running UI operations around cache-manager ioctls, registry updates, token work, and network lookups. State is only the saved cursor handle.

Dependencies/integration: Depends on `<windows.h>` and Win32 `GetCursor`, `SetCursor`, and `LoadCursor`. Integrated broadly across dialogs and `gui2fs.cpp`.

Risks/tests: Cursor state is thread/UI-message sensitive; nested instances should restore in LIFO order. Test exceptions/early returns, nested hourglasses, and calls from non-UI worker contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/hourglass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.cpp

Purpose: Implements the token-acquisition dialog for Kerberos/AFS authentication from the Explorer extension.

Important APIs/functions: `kl_Authenticate` wraps `ka_UserAuthenticateGeneral`. `CKlogDlg::OnInitDialog` defaults the cell from `cm_GetRootCellName`; `OnOK` validates user input, calls authentication, and reports the returned reason on failure. Change handlers enable OK only when cell, name, and password are present.

Control flow/state: Dialog state is stored in `m_strName`, `m_strPassword`, and `m_strCellName`. No persistent state is written; successful authentication updates AFS token state via the auth library.

Dependencies/integration: Uses MFC DDX, `TaLocale_GetDialogResource`, `HOURGLASS`, OpenAFS `kautils`, and `cm_config`. Help routes to `GET_TOKENS_HELP_ID`.

Risks/tests: Password remains in a `CString` until dialog teardown. ANSI conversion under Unicode uses `CStringA` with process code page rather than UTF-8. Test default-cell failure, bad password reason display, Unicode principal/cell handling, empty-field OK enablement, and unavailable auth/cache manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.h

Purpose: Declares the `CKlogDlg` MFC dialog used to obtain AFS tokens.

Important APIs/types: The class exposes `SetCellName`, dialog ID `IDD_KLOG_DIALOG`, bound controls for OK/name/password/cell, and handlers for initialization, OK, field changes, and help.

Control flow/state: Private `CheckEnableOk` enforces required field state; mutable dialog fields are MFC `CString`s.

Dependencies/integration: Includes `resource.h`; implementation depends on MFC and OpenAFS auth libraries. Called from authentication UI flows.

Risks/tests: Header has no include guard. Test compilation in repeated include contexts and resource/control ID consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.cpp

Purpose: Implements the modal dialog for creating an AFS mount point.

Important APIs/functions: `CMakeMountPointDlg::OnOK` gathers directory, volume, cell, and read/write selection, then calls `MakeMount`. `OnChangeVolume`, `OnChangeDir`, and `OnChangeCell` update cached input and enable OK. `OnInitDialog` seeds fields from setters and defaults the type to regular.

Control flow/state: `m_bMade` records whether `MakeMount` succeeded. The volume edit is limited manually to 63 characters; OK requires non-empty directory and volume.

Dependencies/integration: Uses MFC controls, localized resources, `gui2fs.cpp` mount creation, and help ID `MAKE_MOUNT_POINT_HELP_ID`.

Risks/tests: `OnOK` closes the dialog even when `MakeMount` fails, leaving callers to inspect `MountWasMade`. Cell input is optional but not validated. Test regular/RW mount strings, long volume names, non-AFS parent, freelance admin checks, empty cell, and failed create result handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.h

Purpose: Declares `CMakeMountPointDlg`, the MFC form for mount point creation.

Important APIs/types: Public setters provide directory, cell, and volume defaults; `MountWasMade` reports operation success. Dialog data binds OK, volume, RW radio, directory, cell, and mount type.

Control flow/state: Private cached strings are updated by edit-change handlers; `CheckEnableOk` controls command availability.

Dependencies/integration: Uses MFC and resource IDs from the shell extension resources. The implementation calls `MakeMount`.

Risks/tests: Header has no include guard. Test dialog resource IDs and that caller logic observes `MountWasMade`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_mount_point_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.cpp

Purpose: Implements the dialog for creating an AFS symbolic link from a base Explorer directory.

Important APIs/functions: `CMakeSymbolicLinkDlg::OnOK` validates the base path is in AFS, switches the process current directory to that base, and calls `MakeSymbolicLink`. `CheckEnableOk` tests cached name/target fields, and `OnInitDialog` initializes controls.

Control flow/state: The base path is set through `Setbase`; name and target are DDX-bound strings with max-character validators. The change handlers are present but commented out in the message map, so OK enablement may not update dynamically.

Dependencies/integration: Calls `IsPathInAfs`, `MakeSymbolicLink`, `GetAfsError`, and `ShowMessageBox`. Used by the shell extension symbolic-link menu.

Risks/tests: Changing process current directory from an Explorer extension can affect later relative operations. `m_sBase` length and AFS membership errors must be handled before creation. Test base directory extraction, relative link names, non-AFS bases, long paths, missing change-handler wiring, and create-failure display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.h

Purpose: Declares `CMakeSymbolicLinkDlg`, the MFC dialog for AFS symlink creation.

Important APIs/types: Public `Setbase` stores the base directory; dialog data binds OK, name, target directory, and string fields. Handlers cover name/target changes, OK, and initialization.

Control flow/state: `m_sBase` is protected state used during `OnOK`; input fields are cached through DDX.

Dependencies/integration: Depends on MFC and resource ID `IDD_SYMBOLICLINK_ADD`; implementation integrates with `gui2fs.cpp`.

Risks/tests: Header has no include guard. `Setbase` takes `const char *`, which is narrow even when the rest of the UI may be Unicode. Test Unicode base paths and message-map consistency with declared handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/make_symbolic_link_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.cpp

Purpose: Displays a list of mount point descriptions produced by `ListMount`.

Important APIs/functions: `SetMountPoints` copies caller-provided strings into `m_MountPoints`. `OnInitDialog` configures list-box tab stops and inserts each mount point. `OnHelp` opens the mount point help context.

Control flow/state: All display state is in the copied `CStringArray`; the dialog does not query AFS itself.

Dependencies/integration: Depends on localized dialog resources and MFC list boxes. `gui2fs.cpp` constructs and shows it after probing selected paths.

Risks/tests: Tab stop values assume localized text width and may truncate long volume/cell names. Test empty lists, many selections, long mount targets, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.h

Purpose: Declares the list-only `CMountPointsDlg` class.

Important APIs/types: Public `SetMountPoints` is the only data ingress. Dialog ID `IDD_MOUNT_POINTS` and `IDC_LIST` are bound to an MFC `CListBox`.

Control flow/state: Private `m_MountPoints` stores rows until initialization populates the control.

Dependencies/integration: MFC and shell extension resources; used by `ListMount`.

Risks/tests: Header lacks an include guard. Validate resource ID consistency and copy semantics with caller-owned arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.cpp

Purpose: Provides localized string loading plus custom varargs formatting for message boxes and formatted strings.

Important APIs/functions: `ShowMessageBox` loads a string resource, substitutes `%` format tokens, and calls `AfxMessageBox`. `GetMessageString` performs the same formatting but returns a `CString`. `LoadString` wraps `GetString` into a `CString`.

Control flow/state: The formatter scans the loaded template for `%` tokens and consumes varargs by token type. It allocates temporary buffers for the paste/cut/converted fragments on each substitution.

Dependencies/integration: Uses MFC `CString`, `AfxMessageBox`, `<tchar.h>`, `TaLocale` string resources, and `resource.h`. Most GUI operation files use it for user-facing messages.

Risks/tests: No `va_end`, manual fixed-size buffers, unsupported width/precision, and `CString` passed through varargs are all fragile. `%l` parsing references `pszdone[x+2]`, which is suspicious during initial formatting. Test every resource string containing substitutions, long inserted strings, Unicode strings, invalid format tokens, and both message-box and string-return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.h

Purpose: Declares the message formatting and string-loading helpers shared by the Explorer extension.

Important APIs/types: `ShowMessageBox`, `GetMessageString`, and `LoadString` are exported to local C++ modules. Default parameters let callers omit button flags and help IDs.

Control flow/state: Header has no logic; it defines varargs contracts tied to string-table format tokens.

Dependencies/integration: Includes `resource.h` and assumes MFC `CString` and Win32 `UINT` are in scope from `stdafx.h`.

Risks/tests: Varargs contracts are unchecked by the compiler. Test compile order, default parameters, and all resource format strings against call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.cpp

Purpose: Shows partition size/free/percent-used values for the selected volume.

Important APIs/functions: `SetValues` in the header seeds `m_nSize` and `m_nFree`; `OnInitDialog` formats them into controls and computes percent used. `OnHelp` opens partition help.

Control flow/state: The dialog is pure presentation; values come from `CVolumeInfo::OnPartitionInfo` after `GetVolumeInfo` populated `CVolInfo`.

Dependencies/integration: Uses MFC edit controls, `TaLocale`, and help ID `PARTITION_INFO_HELP_ID`.

Risks/tests: It computes `strPerUsed` twice and never calls `m_PercentUsed.SetWindowText`, so the percent field may remain blank. `ASSERT(m_nSize != 0)` is not runtime protection in release builds. Test zero-size values, large 64-bit values truncated to `LONG`, and percent display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.h

Purpose: Declares `CPartitionInfoDlg`, a simple volume partition information dialog.

Important APIs/types: Public `SetValues(LONG nSize, LONG nFree)` provides data. Dialog ID `IDD_PARTITION_INFO` binds total size, percent used, and free-block edit controls.

Control flow/state: Private `LONG` fields store size/free until `OnInitDialog`.

Dependencies/integration: MFC and resource IDs; launched from `volumeinfo.cpp`.

Risks/tests: Uses `LONG` despite `CVolInfo` storing partition values as `unsigned __int64`. Test large partition sizes and include-order safety, since the header has no include guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/partition_info_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/resource.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/resource.h

Purpose: Defines numeric resource IDs for the AFS shell extension's menus, strings, dialogs, and controls.

Important APIs/types: Contains command help IDs (`ID_*`), string IDs (`IDS_*`), context-menu command offsets (`IDM_*`), dialog IDs (`IDD_*`), and control IDs (`IDC_*`). These constants bind C++ code to `afs_shl_ext.rc` and localized resources.

Control flow/state: No runtime logic; this is compile-time glue. Duplicates and aliases are meaningful because message maps and string loads use exact numeric IDs.

Dependencies/integration: Included by most dialog headers and `msgs.h`; consumed by menu construction, help routing, and DDX control binding.

Risks/tests: Duplicate control IDs exist (`IDC_OTHER_WRITE2`/`IDC_OTHER_EXECUTE`, `IDC_PROP_SMINFO`/`IDC_QUOTA_MAX`, `IDC_PROP_FID`/others nearby), so resource editing can break bindings. Test resource compilation, every dialog template/control mapping, context-menu command IDs, and localized string availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.cpp

Purpose: Implements a reusable two-column results dialog for multi-file operations.

Important APIs/functions: `SetContents` stores dialog title, result column title, file list, and result list. `OnInitDialog` asserts equal list sizes, sets tab stops, and adds `file\tresult` rows. `OnHelp` routes to the caller-supplied help ID.

Control flow/state: The caller prepares all rows; the dialog only displays copied arrays. It is used by operations like cell display, server display, and mount point removal.

Dependencies/integration: Uses MFC list boxes, localized dialog templates, and `ShowHelp`.

Risks/tests: Equal-size mismatch is only asserted; release builds can read past one array. Long filenames/results may not align. Test empty lists, mismatched arrays, many rows, long localized strings, and caller-specific help IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.h

Purpose: Declares `CResultsDlg`, the reusable results list dialog.

Important APIs/types: Constructor takes a help context ID; `SetContents` provides title, column title, file rows, and result rows. Dialog data binds label and list controls.

Control flow/state: Private arrays retain display content between construction and `OnInitDialog`.

Dependencies/integration: MFC and resource IDs; used by `gui2fs.cpp`.

Risks/tests: Header lacks include guards. Test constructor/help ID propagation and ownership independence from caller arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/server_status_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/server_status_dlg.cpp

Purpose: Implements the server-status dialog that triggers cache-manager server probing.

Important APIs/functions: `OnShowStatus` calls `CheckServers` with scope and fast-probe state. Radio handlers switch between local, all, and specified-cell modes. `GetCellNameText` reads the edit control; `CheckEnableShowStatus` gates the command when a specific cell is selected.

Control flow/state: Dialog state is `m_bFast`, `m_nCell`, and the cell-name edit. `Save` is a stub returning `FALSE`.

Dependencies/integration: Calls `gui2fs.cpp::CheckServers`, uses `WHICH_CELLS`, MFC DDX, resources, and `SERVER_STATUS_HELP_ID`.

Risks/tests: The header file is named `server_status_dlg.H` in the source tree while the requested research output covers only the `.cpp`. Test case-sensitive builds, radio state transitions, empty specified-cell behavior, fast/all/local flags, and cache-manager errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/server_status_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.cpp

Purpose: Implements the ACL editing dialog for one AFS directory.

Important APIs/functions: `OnInitDialog` loads ACL entries with `GetRights`; `OnAdd`, `OnClear`, `OnCopy`, `OnRemove`, and `OnClean` perform user actions; `OnPermChange` rewrites selected rights; `OnOK` persists changes with `SaveACL`; `IsNameInUse` implements `CSetACLInterface` validation for the add-entry dialog.

Control flow/state: ACL data is held as paired `CStringArray` entries for normal and negative ACLs, mirrored into two list boxes. `m_bChanges`, `m_bShowingNormal`, and `m_nCurSel` track dirty state and current selection.

Dependencies/integration: Uses add/clear/copy ACL dialogs, `gui2fs.cpp` ACL operations, `msgs`, MFC controls, and help ID `SET_AFS_ACL_HELP_ID`.

Risks/tests: `m_strCellName` is never populated before `SaveACL`, so saved ACLs may use an empty cell name. Multi-select removal and paired-array indexing are fragile. Test normal and negative ACL edits, duplicate-name rejection, clearing one or both lists, copy-with-clear, clean behavior, save failures, and selection edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.h

Purpose: Declares `CSetAfsAcl`, the MFC ACL editor dialog and implementation of the add-entry validation interface.

Important APIs/types: Public `SetDir` chooses the directory under edit, and `IsNameInUse` is exposed to child dialogs. Dialog controls represent ACL lists and permission checkboxes.

Control flow/state: Private helpers render rights, build rights strings, enable/disable permission editing, and respond to selection state.

Dependencies/integration: Includes `add_acl_entry_dlg.h`, resource IDs, and MFC. Implementation depends on `gui2fs.cpp` for actual AFS persistence.

Risks/tests: Header has no include guard and includes another dialog header, increasing coupling. Test compile with repeated includes and child-dialog validation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/set_afs_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.cpp

Purpose: Implements the COM shell extension for AFS context menus, icon overlays, infotips, `IPersistFile`, and property-sheet pages.

Important APIs/functions: Interface parts implement `IContextMenu`, `IShellExtInit`, `IShellIconOverlayIdentifier`, `IQueryInfo`, `IPersistFile`, and `IShellPropSheetExt`. `QueryContextMenu` builds the AFS submenu; `InvokeCommand` launches dialogs or calls `gui2fs` operations; `Initialize` captures selected paths and probes AFS/symlink/mount state; `AddPages` adds AFS file, volume, and ACL property pages.

Control flow/state: Per-object state tracks selected files, directory presence, AFS membership, symlink/mountpoint flags, overlay enablement, and tooltip file path. Global counters track COM interface references. Registry `ShellOption` controls overlay enablement, although `IsMemberOf` does not appear to check it.

Dependencies/integration: Uses MFC OLE, Explorer COM interfaces, Shlwapi, AFS registry paths, property page classes, all operation dialogs, and `gui2fs.cpp`.

Risks/tests: Explorer callback paths call cache-manager ioctls synchronously, so unavailable AFS can affect shell responsiveness. Refcounting uses global counters instead of per-interface object state. `Initialize` may leak `STGMEDIUM` on some failure paths, and `GetCommandString` casts narrow output as `LPTSTR`. Test multi-select, non-AFS selection suppression, folder-background init, menu command IDs, overlays disabled/enabled, tooltip allocation, property page lifecycle, and 32/64-bit CLSIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.h

Purpose: Declares the `CShellExt` COM/MFC shell extension class and overlay variant `CShellExt2`.

Important APIs/types: The class contains nested interface parts for `IContextMenu`, `IShellExtInit`, `IShellIconOverlayIdentifier`, `IQueryInfo`, `IPersistFile`, and `IShellPropSheetExt`. State fields track file selection, AFS classification, overlay object type, allocator, and overlay setting.

Control flow/state: `CShellExt2` derives from `CShellExt` and sets `m_overlayObject = 1` for mount overlays; the base object uses `0` for symlink overlays.

Dependencies/integration: Includes `shlobj.h`, MFC `CCmdTarget`, COM macros, and registry title/path constants. Implementation integrates with Explorer registration and AFS operations.

Risks/tests: Global reference counters are declared here and shared across interface parts. Test COM aggregation/interface querying, object lifetime, overlay selection, and registration constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.cpp

Purpose: Provides the translation unit for the MFC precompiled header used by the Explorer extension project.

Important APIs/functions: It includes `stdafx.h`, Winsock headers, and core AFS configuration headers but defines no functions.

Control flow/state: No runtime control flow or state. Its role is build-time compilation acceleration and include consistency.

Dependencies/integration: Depends on MFC, Winsock, OpenAFS `afsconfig.h`, `param.h`, `roken.h`, and `stds.h`.

Risks/tests: Include order is important because Winsock must precede conflicting Windows socket declarations. Test clean builds with and without precompiled headers and both debug/release configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.h

Purpose: Defines the shared precompiled include surface for client-exp modules.

Important APIs/types: Sets `VC_EXTRALEAN`, `ISOLATION_AWARE_ENABLED`, disables MFC DB/DAO support, includes MFC core/extensions/OLE/common-controls headers, defines `UNCHECKED`/`CHECKED`, and includes `help.h`, `TaLocale.h`, and `afxdlgs.h`.

Control flow/state: No runtime logic; compile-time feature macros influence all including translation units.

Dependencies/integration: Central to all MFC dialog and shell extension builds. Debug builds can remap `new` to `DEBUG_NEW`.

Risks/tests: Global macros can affect Windows/MFC behavior across the project. Test with OLE support enabled/disabled, Unicode/non-Unicode builds, common-control manifests, and include order with Winsock users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.cpp

Purpose: Implements constructors/destructor for the simple submount data object.

Important APIs/functions: Default constructor sets status to `SIS_NULL`; value and copy constructors populate status, share name, and path name through setters; destructor does no extra cleanup.

Control flow/state: State is only the three fields declared in `submount_info.h`; ownership is by callers storing pointers in `SUBMT_INFO_ARRAY`.

Dependencies/integration: Uses `stdafx.h`, AFS base headers, and `CSubmountInfo`. Consumed by `submounts_dlg.cpp` and add-submount workflows.

Risks/tests: Copy behavior is shallow only for `CString` value fields, which is acceptable. Test status propagation and pointer ownership in `CSubmountsDlg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.h

Purpose: Defines the data model for AFS submount registry edits.

Important APIs/types: `SUBMT_INFO_STATUS` distinguishes null, added, changed, and deleted entries. `CSubmountInfo` stores share name, path name, and status. `SUBMT_INFO_ARRAY` is an MFC pointer array of `CSubmountInfo*`.

Control flow/state: Inline getters and setters mutate value fields; no persistence occurs in this class.

Dependencies/integration: Includes `afxtempl.h`; used by submount dialog and add/edit dialog code.

Risks/tests: Pointer-array ownership is external and can leak/double-free if callers disagree. Test add/change/delete lifecycles and copy-constructor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.cpp

Purpose: Implements the submount management dialog backed by the OpenAFS client registry `Submounts` key.

Important APIs/functions: `FillSubmtList` enumerates registry values; `ReadSubmtInfo` reads one value; `OnAdd`, `OnChange`, and `OnDelete` stage work items; `FixSubmts` applies staged add/change/delete operations through `RegSetValueEx` and `RegDeleteValue`; `SetAddOnlyMode` supports a direct create-and-save flow from a selected path.

Control flow/state: The UI list shows current and staged submounts, while `m_ToDo` owns pending `CSubmountInfo*` changes. `AddWork` coalesces operations by share name before `OnOk` persists them.

Dependencies/integration: Uses MFC, `CAddSubmtDlg`, `CSubmountInfo`, registry constants from `afsreg.h`, `WNetGetConnection`, `HOURGLASS`, and `msgs`.

Risks/tests: Registry string byte counts use character counts instead of byte counts in Unicode builds. `RegCreateKeyEx` return status is mostly ignored. Add-only mode immediately calls `OnAdd` and `OnOk`, so cancellation semantics need scrutiny. Test HKLM permission failures, Wow64 registry view, Unicode submount names, staged add-delete coalescing, and network-drive path expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.h

Purpose: Declares the MFC dialog used to view and edit AFS submount registry mappings.

Important APIs/types: Public constructor/destructor and `SetAddOnlyMode` drive full-edit or one-shot-add behavior. Private helpers fill the list, apply changes, stage work, and locate staged entries.

Control flow/state: Private `m_bAddOnlyMode`, `m_strAddOnlyPath`, and `m_ToDo` govern staged registry persistence.

Dependencies/integration: Includes `resource.h` and `submount_info.h`; implementation depends on add-submount dialog and Win32 registry APIs.

Risks/tests: Verify destructor owns and deletes every staged pointer exactly once. Test `WinHelp` override and dialog resource/control ID consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.cpp

Purpose: Displays symlink descriptions produced by `ListSymlink`.

Important APIs/functions: `SetSymlinks` copies caller-provided rows. `OnInitDialog` sets a tab stop and inserts each row into the list. `OnHelp` opens symlink help.

Control flow/state: Presentation-only; all AFS probing is done before the dialog is created.

Dependencies/integration: MFC list box, localized resources, and `SYMLINK_HELP_ID`. Called from `gui2fs.cpp`.

Risks/tests: Long symlink targets may exceed the list layout. Test no symlinks, error rows, long targets, Unicode targets, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.h

Purpose: Declares `CSymlinksDlg`, the list-only dialog for symlink results.

Important APIs/types: Public `SetSymlinks` supplies rows. Dialog ID `IDD_SYMLINKS` binds `IDC_LIST`.

Control flow/state: Private `CStringArray m_Symlinks` stores rows until initialization.

Dependencies/integration: MFC and resource IDs; used by `ListSymlink`.

Risks/tests: Header lacks include guards, and the parameter name still says `mountPoints`. Test repeated include compatibility and display of caller-copied data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.cpp

Purpose: Implements the dialog and helper for discarding AFS tokens.

Important APIs/functions: `kl_Unlog` calls `ktc_ForgetAllTokens` when the cell is empty or `ktc_ForgetToken` for the `afs` service principal in a specific cell. `OnInitDialog` defaults the cell using `cm_GetRootCellName`; `OnOK` invokes token removal and closes only on success.

Control flow/state: Dialog state is the cell-name string and OK control enablement. Token state is external to the process in the AFS credential/cache-manager layer.

Dependencies/integration: Uses MFC, OpenAFS token/auth APIs, `cm_config`, and `ShowHelp` with `DISCARD_TOKENS_HELP_ID`.

Risks/tests: Current UI disables OK for empty cell, preventing the `ktc_ForgetAllTokens` branch from the dialog even though the helper supports it. `strcpy(server.cell, astrCellName)` needs length validation. Test root-cell default, specific-cell unlog, all-token helper use, unavailable AFS service, and long/Unicode cell names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.h

Purpose: Declares `CUnlogDlg`, the token-discard dialog.

Important APIs/types: Public `SetCellName` sets the target cell. Dialog data binds OK and cell-name controls; handlers cover initialization, cell change, OK, and help.

Control flow/state: OK enablement depends on non-empty `m_strCellName`.

Dependencies/integration: Includes `resource.h`; implementation uses OpenAFS token APIs.

Risks/tests: Header has no include guard. Test caller-provided cell prepopulation and whether empty-cell all-token removal should be reachable from UI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/volume_inf.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/volume_inf.h

Purpose: Defines `CVolInfo`, the value object used to move AFS volume status from `gui2fs.cpp` into volume dialogs and property pages.

Important APIs/types: Stores file path/name, volume name, availability string, volume ID, quota, new quota, blocks used, partition size/free, duplicate index, and error message.

Control flow/state: No methods; fields are filled by `GetVolumeInfo`, edited by `CVolumeInfo`, and consumed by `SetVolInfo`.

Dependencies/integration: Requires MFC `CString` and MSVC `unsigned __int64`. Included by `gui2fs.cpp` and `volumeinfo.cpp`.

Risks/tests: Public mutable fields allow inconsistent state, such as an error message with stale quota values. Test duplicate-volume handling and 64-bit formatting/truncation in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/volume_inf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/volume_info.h -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/volume_info.h

Purpose: Declares `CVolumeInfo`, the dialog for viewing and changing volume quotas.

Important APIs/types: Public `SetFiles` provides selected paths. Private `ShowInfo` renders rows and `GetCurVolInfoIndex` resolves duplicate volume selections. Dialog controls include list, quota edit, quota spin, partition info, and OK button.

Control flow/state: The dialog owns an allocated `CVolInfo` array and tracks current selection in `m_nCurIndex`.

Dependencies/integration: Uses `CVolInfo`, MFC controls, and resource ID `IDD_VOLUME_INFO`; implementation calls `GetVolumeInfo`, `SetVolInfo`, and `CPartitionInfoDlg`.

Risks/tests: Header lacks include guard and uses `unsigned __int64` in DDX. Test allocation/destruction, multiple files in same volume, and quota edit/spin behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/volume_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/volumeinfo.cpp -->
## sources/distributed-fs/openafs/src/WINNT/client_exp/volumeinfo.cpp

Purpose: Implements the volume information/quota dialog for selected AFS paths.

Important APIs/functions: `OnInitDialog` allocates `CVolInfo` entries and calls `GetVolumeInfo`; `ShowInfo` renders rows; `OnSelChangeList` loads selected quota into the edit; `OnPartitionInfo` opens partition details; `OnChangeNewQuota` marks changes; `OnOK` persists changed unique volumes with `SetVolInfo`; `OnDeltaPosQuotaSpin` adjusts quota by 1024 blocks.

Control flow/state: The list item data maps display rows to `m_pVolInfo` indexes; duplicate volumes should share quota changes through `m_nDup`.

Dependencies/integration: Uses `gui2fs.cpp`, `partition_info_dlg`, `msgs`, MFC common controls, and localized resources.

Risks/tests: Missing braces in duplicate detection cause `break` to run after the first comparison, so duplicates after index 0 may be missed. `unsigned __int64 nNewQuota < 0` is ineffective, and `%ld` formatting truncates 64-bit IDs/quotas. Test multi-selection duplicates, unlimited quota, spin underflow/overflow, failed `GetVolumeInfo`, and successful/failed quota persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_exp/volumeinfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/basic.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/basic.c

Purpose: Implements a Win32 stress test for the OSI mutex/RW-lock package.

Important APIs/functions: `main_BasicTest` initializes OSI/logging, creates modifier and scanner threads, reports progress, waits for completion, finalizes locks, and closes thread handles. Worker functions `main_Mod1`, `main_Mod2`, `main_Scan1`, and `main_Scan2` exercise mutexes, read/write locks, assertions, logging, and unlocked observation.

Control flow/state: Shared globals `a` and `b` must sum to 100 under lock protection; `done` tracks thread completion under `main_doneRWLock`. Loop counters and event counters feed the UI display.

Dependencies/integration: Uses `osi.h`, `main.h`, Win32 threads, `Sleep`, and OSI logging. Invoked by the OSI test application menu.

Risks/tests: Some thread-create failures leak already-created handles. Loop counters are intentionally unlocked and may display transient values. Test lock correctness under debug/stat lock types, assertion failures, repeated runs, thread-create failures, and final lock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/basic.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/basic.h

Purpose: Declares the OSI basic lock test entry point.

Important APIs/types: `main_BasicTest(HANDLE)` runs the stress test and updates a window display.

Control flow/state: No state or logic; it is a narrow interface from the Win32 test harness to `basic.c`.

Dependencies/integration: Requires `HANDLE` from Windows headers and is included by `main.c`.

Risks/tests: Compile order must define `HANDLE`. Test menu invocation and return-code display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/basic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/dbrpc.idl -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/dbrpc.idl

Purpose: Defines the RPC interface for remote OSI debug/statistics inspection.

Important APIs/types: Constants define remote error codes, string/int array sizes, lock type IDs, format regions, and format flags. Structures include `osi_remFormat_t`, `osi_remHyper_t`, string arrays, and `osi_remGetInfoParms_t`. RPC methods include `dbrpc_Ping`, `Open`, `GetInfo`, `Close`, and `GetFormat`.

Control flow/state: Clients open a named debug object to receive a remote file descriptor, repeatedly fetch status/info, query formatting metadata, and close the descriptor.

Dependencies/integration: Consumed by MIDL and implemented by OSI debug code elsewhere (`osidb`). Uses explicit array sizes and NDR attributes.

Risks/tests: The commented `[length_is]` for `__int64 idata` means the full fixed integer array is transmitted. Test generated stubs, 32/64-bit NDR layout, bounds on `icount`/`scount`, invalid descriptors, EOF/no-entry paths, and format metadata for each region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/dbrpc.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/largeint.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/largeint.h

Purpose: Supplies prototypes and comparison macros for legacy Windows large-integer arithmetic routines used when compiler/platform headers lack them.

Important APIs/types: Declares add, subtract, multiply, divide, negate, conversion, and shift functions for `LARGE_INTEGER`/`ULARGE_INTEGER`, plus macros for comparisons and zero checks.

Control flow/state: Header-only declarations/macros; arithmetic implementations live in external libraries/source. Macros inspect `HighPart` and `LowPart` directly.

Dependencies/integration: Included by `osi.h` for older MSVC versions. Wrapped in `extern "C"` for C++ consumers.

Risks/tests: Direct signed/unsigned comparisons can be subtle around negative high parts and unsigned low parts. Test compiler-version selection, link availability, division remainder semantics, and boundary values around zero, negative, and high-bit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/largeint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/main.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/main.c

Purpose: Provides the Win32 GUI harness for OSI lock/performance/trylock tests.

Important APIs/functions: `WinMain` runs app initialization and the message loop. `InitApplication` registers the window class; `InitInstance` creates the main window, initializes the debug RPC system, and computes display geometry. `MainWndProc` handles menu commands for tests and lock debugging. `main_ClearDisplay` and `main_ForceDisplay` update the text screen.

Control flow/state: Global window/instance handles, `main_screenText`, `screenRect`, and `lineHeight` store UI state. Menu commands synchronously run tests and repaint the status area.

Dependencies/integration: Uses Win32 GDI/window APIs, OSI debug initialization, and test modules `basic`, `perf`, and `trylock`.

Risks/tests: Long-running tests execute on the UI thread, blocking normal message processing. `main_ForceDisplay` deletes a stock brush, which is unsafe. Test menu command dispatch, debug on/off lock type selection, repaint behavior, repeated tests, and RPC debug initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/main.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/main.h

Purpose: Declares menu IDs, Win32 harness functions, and shared screen buffer for the OSI test application.

Important APIs/types: Defines `IDM_*` command IDs, prototypes for initialization/window procedures/about dialog, display helpers, `HW_NLINES`, and `main_screenText`.

Control flow/state: No logic; exposes global display state to test modules.

Dependencies/integration: Used by `main.c`, `basic.c`, and other test modules. Contains compatibility macros for horizontal scroll message extraction.

Risks/tests: Global `main_screenText[10][80]` invites truncation from `wsprintf`. Test all menu IDs against resources and display writes for overflow risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osi.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osi.h

Purpose: Aggregates the Windows OSI utility layer definitions for locks, sleeps, queues, logging, debug RPC, file descriptors, and utilities.

Important APIs/types: Defines `osi_hyper_t` as `LARGE_INTEGER`, `osi_uid_t` as `GUID`, and `int32`. Provides large-integer compatibility declarations/macros for newer MSVC and includes subsystem headers such as `osiutils.h`, `osibasel.h`, `osistatl.h`, `osidb.h`, and `osilog.h`.

Control flow/state: Header has no runtime logic but selects compatibility paths based on compiler version.

Dependencies/integration: Included by OSI implementation and test files. Pulls in RPC/GUID and thread abstractions.

Risks/tests: Aggregated headers can hide dependency cycles and macro conflicts. Test C and C++ consumers, older/newer MSVC versions, and consistency of large-integer comparison macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osi_internal.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osi_internal.h

Purpose: Supplies debug-build x86 fallbacks for interlocked bitwise AND/OR intrinsics.

Important APIs/functions: Inline `osi_InterlockedAnd` and `osi_InterlockedOr` implement compare-exchange loops using `_InterlockedCompareExchange`; macros alias `_InterlockedAnd`/`_InterlockedOr` to these fallbacks when missing.

Control flow/state: Only active under `DEBUG` and `_M_IX86`. Each loop retries until the compare-exchange observes a stable original value.

Dependencies/integration: Included by `osibasel.c`, which uses `_InterlockedOr` and `_InterlockedAnd` against lock flags.

Risks/tests: Availability differs by compiler/architecture/build mode. Test debug x86 builds with older compiler intrinsics, concurrent flag updates, and non-x86 builds where the fallback is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osi_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.c

Purpose: Implements the base OSI mutex and read/write lock primitives for Windows.

Important APIs/functions: `osi_BaseInit` initializes hash critical sections, TLS indexes, and lock-reference free list state. Lock APIs include obtain/release read/write/mutex, try read/write/mutex, convert read/write, sleep while releasing a lock, finalize/init locks, and query lock state. Optional lock-order validation records held locks in thread-local queues.

Control flow/state: Each lock is assigned an atomic critical-section bucket. Obtain paths enter the bucket, inspect flags/readers/waiters, either set ownership or wait via `osi_TWait`; release paths clear ownership and signal sleepers via `osi_TSignalForMLs`. TLS lock-reference queues are maintained only when validation is enabled. Process-global state includes critical sections, TLS indexes, validation flag, atomic index counter, and a free list.

Dependencies/integration: Uses Windows critical sections/interlocked operations, OSI sleep queues, queue helpers, thread ID helpers, panic/assert/log infrastructure, and pluggable lock type operations for non-base lock types.

Risks/tests: Correctness depends on handing the critical section to sleep/signal helpers exactly once. TLS indexes are never freed, acceptable for process lifetime but relevant to repeated init tests. Validation free list can grow without bound. Test read/write fairness under waiters, recursive/self-lock assertions, conversion races, sleep/reacquire paths, try-lock failure with waiters, lock hierarchy violations, and stat-lock delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.c -->
