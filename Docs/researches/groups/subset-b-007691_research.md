# subset-b-007691 research

This grouped report covers the requested MooseFS xattr files and OpenAFS Windows setup/admin-server sources. Each source file has a separate section with reconciliation markers so the sections can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/xattr.c -->
# sources/distributed-fs/moosefs/mfsmaster/xattr.c

Purpose: implements MooseFS master-side extended attributes for inodes. It stores each inode's xattrs in an in-memory hash table keyed by inode number, interns attribute names and values through the shared dictionary subsystem, exposes set/get/list/copy/import/export operations, and serializes xattrs into the master metadata stream.

Important APIs/types/functions: internal `xattrentry` holds an inode and linked `xattrpair` list; `xattrpair` holds dictionary handles for name and value. `xattr_namecheck()` rejects embedded NUL bytes. `xattr_setattr()` implements create-only, replace-only, create-or-replace, and remove modes with MooseFS error codes. `xattr_getattr()`, `xattr_listattr_leng()`, `xattr_listattr_data()`, and `xattr_getall()` return individual, name-list, or full packed xattr data. `xattr_check()` compares packed xattr data with current state. `xattr_setall()` replaces all xattrs from packed data, `xattr_copy()` duplicates dictionary references to a destination inode, `xattr_store()` writes metadata records, `xattr_load()` reads them, and `xattr_cleanup()` tears down the table.

Control flow: the file uses the MooseFS `hash_begin.h`/`hash_end.h` glue macros with `LOHASH_BITS` 20 to generate add/find/delete/hash helpers. Set operations first validate name/value/list limits, find or create the inode entry, use dictionary search/insert for canonical name identity, then mutate the linked list. Listing computes total NUL-separated name length first, returns the entry as an opaque cursor, and later copies names from that cursor. Metadata store emits one record per pair as inode, one-byte name length, four-byte value length, name bytes, value bytes, then an all-zero sentinel. Metadata load loops until the sentinel, validates inode existence and size limits, optionally skips bad records when `ignoreflag` is set, and appends records to the current inode entry.

State/persistence: runtime state is only the generated hash table plus dictionary reference counts. Persistent state is the xattr metadata stream written through `bio_write()` and read through `bio_read()`/`bio_skip()`. Inode xattr flags are synchronized through `fs_set_xattrflag()` and `fs_del_xattrflag()` when entries are created or removed in normal paths; `xattr_setall()` returns whether a flag should remain but leaves flag decisions to callers.

Dependencies/integration: depends on MooseFS communication constants and limits (`MFS_XATTR_*`, status/error codes), dictionary interning, datapack endian helpers, metadata BIO, filesystem inode validation and xattr flags, and the generated hash-table glue.

Risks/test signals: boundary handling around `MFS_XATTR_NAME_MAX`, `MFS_XATTR_SIZE_MAX`, and `MFS_XATTR_LIST_MAX` is central. `xattr_listattr_leng()` returns an entry pointer that must not outlive concurrent mutation. Packed data parsers assume trusted lengths after caller-side validation except in `xattr_check()`. `xattr_cleanup()` invokes the generated hash cleanup twice, which is worth regression testing for idempotence. Tests should cover create/replace/remove error codes, dictionary refcount reuse, empty final entry flag clearing, metadata load with missing inodes and ignored corrupt records, full-list size overflow, and copy/setall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/xattr.h -->
# sources/distributed-fs/moosefs/mfsmaster/xattr.h

Purpose: declares the MooseFS master xattr subsystem interface used by filesystem and metadata code.

Important APIs/types/functions: the header exports validation (`xattr_namecheck()`), inode cleanup (`xattr_removeinode()`), CRUD/list calls (`xattr_setattr()`, `xattr_getattr()`, `xattr_listattr_leng()`, `xattr_listattr_data()`), packed transfer helpers (`xattr_getall()`, `xattr_check()`, `xattr_setall()`), duplication (`xattr_copy()`), lifecycle (`xattr_cleanup()`, `xattr_init()`), and persistence (`xattr_store()`, `xattr_load()`).

Control flow: callers initialize the subsystem with `xattr_init()`, mutate per-inode xattrs through the setter/copy/remove APIs, serialize or reload metadata through `xattr_store()`/`xattr_load()`, and release all memory through `xattr_cleanup()`. Listing is a two-step API: first ask for size and opaque node pointer, then copy list data with that pointer.

State/persistence: the header itself has no state, but it exposes APIs that operate on the xattr hash table and metadata stream. The `bio` include makes persistence part of the public contract.

Dependencies/integration: includes `<inttypes.h>` and MooseFS `bio.h`; all returned status values are MooseFS protocol statuses defined outside the header. It integrates with filesystem inode lifecycle, metadata save/load, and client-facing xattr protocol handling.

Risks/test signals: consumers must preserve the `void *xanode` cursor only across a stable list operation and must pass packed buffers that match `xattr_getall()` layout. Tests should verify header prototypes stay synchronized with implementation and that callers handle `uint8_t` status/error returns rather than POSIX `errno` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/NTObjdir -->
# sources/distributed-fs/openafs/src/NTObjdir

Purpose: shell helper for creating the OpenAFS Windows NT object directory tree from a Unix host before the native Windows build tooling was fully ported.

Important APIs/types/functions: it defines a large `dirs` whitespace list covering `config`, many `WINNT/...` components, language-resource folders, and core AFS server/library/test directories. It checks for `src`, `i386_nt40`, and executable `src/WINNT/docs/build/ntobjdirs`, then invokes `ntobjdirs -d <dir>` for each listed path.

Control flow: the script must be run from the directory above `src`. It fails early with explanatory messages if the required source tree, NT object root, or helper script is absent. For each directory entry it echoes and runs the helper command.

State/persistence: no internal state beyond the `dirs` variable. Persistence is external: the helper creates directories under the NT object directory layout.

Dependencies/integration: depends on `/usr/bin/sh`, the OpenAFS source tree layout, the `i386_nt40` object directory, and `src/WINNT/docs/build/ntobjdirs`. It integrates with legacy Windows build preparation rather than runtime OpenAFS behavior.

Risks/test signals: the hard-coded directory list can drift from the real source tree, and whitespace/line-continuation errors would silently skip or split paths. Tests are practical smoke checks: run from a fixture tree and assert every intended directory is passed once to `ntobjdirs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/NTObjdir -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.cpp

Purpose: implements an MFC extension DLL used by setup utilities to download a web page to a file, get the current user logon name, and display a file browser dialog.

Important APIs/types/functions: `CGetWebDllApp` is the MFC application object. `CTearSession` subclasses `CInternetSession` and reports connection status. `CTearException` carries local error codes. `StripTags()` removes HTML tags across buffer boundaries with static tag state. Exported `GetWebPage()` performs HTTP GET and writes response text to `lpFile`; `GetUserLogon()` wraps `GetUserName()`; `BrowseFile()` wraps `GetOpenFileName()`.

Control flow: `GetWebPage()` validates URL/output parameters, creates a `CFile`, parses only `http://` URLs with `AfxParseURL()`, opens a WinINet HTTP request with fixed headers, handles HTTP denied by invoking WinINet's password UI, follows one redirect by parsing `Location:`, then reads strings into a 1024-byte buffer and writes them to the output file. It catches `CInternetException`, `CFileException`, and `CTearException`, cleans up `CHttpFile`, `CHttpConnection`, and session objects, and returns a numeric setup-facing code.

State/persistence: global flags control strip/progress/access behavior, but the exported functions expose no setter in this file. `StripTags()` retains static cross-call tag state. The persistent effect is the downloaded output file. The error-message copy uses the existing length of `lpErrMsg` as the copy bound, so callers must preinitialize that buffer correctly or risk truncation/no copy.

Dependencies/integration: depends on MFC, WinINet, common dialog APIs, and `GetWebDllFun.h` exports. It is likely loaded by InstallShield/custom setup logic needing CellServDB or update data.

Risks/test signals: transport is HTTP-only with hard-coded request headers and minimal redirect handling. The code writes string lengths with `strlen()` even under `TCHAR`, and does not robustly bound URL/file copies. Tests should cover bad parameters, non-HTTP URLs, redirects without `Location`, denied authentication paths, output file errors, tag stripping across reads, and `BrowseFile()` offset calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.h

Purpose: main MFC header for the GetWebDll project.

Important APIs/types/functions: declares `CGetWebDllApp` as the DLL's `CWinApp`, `CTearSession` as the HTTP session subclass with an `OnStatusCallback()` override, and `CTearException` as a dynamic MFC exception carrying `m_nErrorCode`.

Control flow: consumers include `stdafx.h` first, then this header. Runtime behavior is implemented in `GetWebDll.cpp`; the header only binds class declarations and message-map macros.

State/persistence: no direct state. It defines object shapes that use MFC module state and exception allocation.

Dependencies/integration: requires MFC headers through `stdafx.h` and includes local `resource.h`. It is coupled to MFC ClassWizard conventions and the exported procedural functions in `GetWebDllFun.h`.

Risks/test signals: exported functions that call MFC must use `AFX_MANAGE_STATE()` in implementation if this DLL is dynamically linked to MFC; the source comments emphasize this but the exports should be checked. Compile tests should verify include order and message-map linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDllFun.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDllFun.h

Purpose: C ABI export header for GetWebDll setup helper functions.

Important APIs/types/functions: declares `GetWebPage(LPSTR lpErrMsg, LPSTR lpFile, LPSTR lpCmdLine)`, `GetUserLogon(LPSTR lpUserName)`, and `BrowseFile(HWND hwndOwner, LPSTR lpstrTitle, LPSTR lpFileFullName, INT fullsize)` with `__declspec(dllexport)` and `extern "C"` guards.

Control flow: setup code can load/link these functions without C++ name mangling. The functions are implemented in `GetWebDll.cpp`.

State/persistence: no state in the header. `GetWebPage()` persists downloaded content to a file; `BrowseFile()` mutates the caller's filename buffer.

Dependencies/integration: depends on Windows/MFC type definitions being available before inclusion. It forms the boundary between InstallShield/native setup callers and the MFC DLL implementation.

Risks/test signals: this header uses `dllexport`, not an import/export macro, so it is tailored to building the DLL rather than consuming it from all contexts. ABI tests should verify calling convention assumptions, buffer sizes, and unmangled export names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDllFun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/Resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/Resource.h

Purpose: Visual C++ generated resource placeholder for the GetWebDll project.

Important APIs/types/functions: contains only AppStudio default next-resource, control, symbol, and command IDs inside `APSTUDIO_INVOKED` guards.

Control flow: no runtime control flow. Resource compiler and Visual Studio use the values when adding future resources.

State/persistence: no runtime state or persistence.

Dependencies/integration: included by `GetWebDll.h` and the project `.rc` file. It integrates with Microsoft resource tooling.

Risks/test signals: low runtime risk. The main signal is resource-build success and absence of ID collisions if new resources are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/Resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/StdAfx.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/StdAfx.h

Purpose: precompiled-header include for the MFC GetWebDll project.

Important APIs/types/functions: defines `VC_EXTRALEAN`, includes core MFC (`afxwin.h`, `afxext.h`), optional OLE/ODBC/DAO headers, IE4 common controls, common controls, and `afxinet.h` for WinINet/MFC internet classes.

Control flow: no runtime behavior. It controls the compilation environment and must be included before project headers expecting MFC declarations.

State/persistence: no state.

Dependencies/integration: tightly couples the DLL to MFC and Visual C++ precompiled-header conventions.

Risks/test signals: build configuration must match optional `_AFX_NO_*` feature macros. Tests are compile/link checks for MFC dynamic/static configurations and WinINet class availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/StdAfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/_isuser.c -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/_isuser.c

Purpose: minimal InstallShield user DLL entry point.

Important APIs/types/functions: defines `NOCOMM`, includes `windows.h`, and implements `DllMain(PVOID hmod, ULONG ulReason, PCONTEXT pctx)` returning `TRUE` for all reasons.

Control flow: Windows loader calls `DllMain`; the function performs no initialization, cleanup, or reason dispatch and always allows load/unload.

State/persistence: no state and no persistence.

Dependencies/integration: generated/boilerplate InstallShield source, linked into setup support resources that use `_isuser/resource.h`.

Risks/test signals: no runtime logic to fail. Test signal is DLL load success under the expected InstallShield runtime and matching exported entry point signature for the toolchain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/_isuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/resource.h

Purpose: resource ID header for InstallShield custom dialogs used by OpenAFS setup.

Important APIs/types/functions: defines IDs for home/root path controls, drive lists, enable/install/web/file checkboxes, previous/browse file controls, dialog templates (`DLG_TEMPLATE`, `DLG_DRIVEPATH`, `DLG_CELLSERVDB`), and `IDC_STATIC`.

Control flow: no executable flow. Dialog procedures and resource scripts use these numeric constants to map Windows controls to setup behavior.

State/persistence: no state. User choices made through these controls are persisted elsewhere by setup code.

Dependencies/integration: used by `_IsUser.RC` and InstallShield/Visual Studio resource compilation.

Risks/test signals: there are intentional ID aliases such as `IDC_ENABLEROOT`/`IDC_INSTALL` and `IDC_CHECK_FILE`/`IDC_CHECK_BROWSEFILE`; dialog code must disambiguate by template context. Tests should verify resource compilation and correct control lookup for each dialog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afs_setup_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afs_setup_utils.cpp

Purpose: large InstallShield/Windows setup utility DLL for OpenAFS install and uninstall tasks. It handles service install/uninstall, registry cleanup, shared DLL counts, PATH and network-provider updates, config preservation/restoration, legacy 3.4 client eradication, license display, and localized resources.

Important APIs/types/functions: `APPINFO` describes each product's service, registry, path, file, start-menu, and preservation behavior. Exported setup callbacks include `Upgrade34ClientConfigInfo()`, `Eradicate34Client()`, `CheckIfAdmin()`, `WriteToInstallErrorLog()`, `InstallServerService()`, `InstallClientService()`, `AddToNetworkProviderOrder()`, `AddToPath()`, `SetSilentMode()`, `RestoreConfigInfo()`, `ShowLicense()`, `UninstInitialize()`, `UninstUnInitialize()`, and `DllEntryPoint()`. Helpers manage service control manager calls, registry duplication/deletion, in-use file rename/delete-on-reboot, start-menu refresh, path expansion, and RichEdit license streaming.

Control flow: install paths add services and PATH/provider entries. Uninstall initialization detects the product, obtains install directory, runs product-specific hooks, optionally preserves registry configuration, stops/deletes services, remembers install dir, marks in-use files, removes product PATH/provider entries, deletes generated files/directories and registry values, and removes start-menu entries. Uninstall finalization runs only after all AFS products are gone and removes shared roots, documentation, preserved-info keys, common PATH entries, and start-menu roots. License display locates existing AFS installs to suppress repeated display, loads a RichEdit DLL, streams RTF text, and fails setup on cancel.

State/persistence: global `hDlg`, `bPreserveConfigInfo`, `bSilentMode`, and `pszInstallDir` carry setup session state. Persistent effects are extensive: Windows services, registry keys under AFS/Microsoft paths, PATH and network provider order, uninstall temp keys, preserved config keys, log files, start-menu folders, and file removals or delayed delete-on-reboot.

Dependencies/integration: depends on OpenAFS registry helpers (`WINNT/afsreg.h`), software product constants (`afssw.h`), localization (`talocale`), `sutil`, `forceremove`, InstallShield callback conventions (`SUCALLCONV`/`WINAPI`), Windows SCM, shell, registry, RichEdit, and filesystem APIs.

Risks/test signals: the code performs destructive uninstall operations, uses many fixed-size `char[MAX_PATH]` and `strcpy`/`sprintf` paths, and relies on global state. Admin checks and service shutdown must work on old NT/Win9x semantics. Tests should be VM/sandbox based and cover silent vs interactive uninstall, each `APPINFO`, preservation cancellation/failure, in-use file handling, PATH/provider idempotence, service already-deleted cases, legacy 3.4 upgrade/eradication, and license accept/cancel flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afs_setup_utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afsrm.c -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afsrm.c

Purpose: command-line utility to forcibly remove legacy AFS software without InstallShield.

Important APIs/types/functions: `DoClient34()` calls `Client34Eradicate(FALSE)` and prints success/failure. `SetupCmd()` registers the `client34` command through the OpenAFS command package. `main()` initializes command errors, registers syntax, and dispatches arguments.

Control flow: command execution is delegated to `cmd_Dispatch()`. The only supported subcommand removes an AFS 3.4a client and does not preserve config because it passes `FALSE`.

State/persistence: no internal persistent state. The called removal routine can delete services, files, registry keys, PATH/provider entries, and start-menu entries.

Dependencies/integration: depends on OpenAFS `cmd` library, Windows APIs, and `forceremove.h`.

Risks/test signals: a mistaken invocation can destructively remove legacy client artifacts. Tests should mock or sandbox `Client34Eradicate()`, verify command registration, return-code propagation, and printed status for success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afsrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.cpp

Purpose: provides a small Windows control animation helper for setup progress UI.

Important APIs/types/functions: `AnimateIcon(HWND,int*)` lazy-loads stop and eight spinner icons with `TaLocale_LoadIcon()` and sets the static control icon. `AnimationHook()` is a subclass hook that advances frames on `WM_TIMER` and removes itself on `WM_DESTROY`. `StartAnimation()` adds the hook, starts a timer, and displays the first frame. `StopAnimation()` kills the timer, displays the stop icon, and removes the hook.

Control flow: progress dialogs call `StartAnimation()` with an icon control. Timer messages flow through the subclass hook, which calls `AnimateIcon()` and then chains to the previous hook or default window procedure.

State/persistence: static icon handles and `fLoaded` cache loaded resources for process lifetime; `AnimationHook()` uses a static frame index shared by all hooked controls. No disk persistence.

Dependencies/integration: depends on Windows messages/timers, `talocale` resource loading, the OpenAFS subclass helper, and spinner resource IDs in `resource.h`.

Risks/test signals: the frame counter is shared across controls, and `1000 / fps` can divide by zero only because the expression substitutes 8 when `fps` is zero. Tests should verify hook chaining, start/stop idempotence, destroy cleanup, localized icon loading, and timer cadence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.h

Purpose: declares the setup progress icon animation API.

Important APIs/types/functions: exports `AnimateIcon(HWND hIcon, int *piFrameLast = NULL)`, `StartAnimation(HWND hIcon, int fps)`, and `StopAnimation(HWND hIcon)`.

Control flow: UI code can directly set a single frame through `AnimateIcon()` or manage timer-driven animation with start/stop calls.

State/persistence: no header state; implementation caches icons and frame state.

Dependencies/integration: requires Windows `HWND` definitions and is used by `progress_dlg.cpp`.

Risks/test signals: because there is no include guard in this header, repeated inclusion is harmless only due to prototypes but still nonstandard. Compile tests should ensure C++ default argument use is compatible with all callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.c -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.c

Purpose: forcibly removes a legacy AFS 3.4a Windows client when normal InstallShield uninstall is unavailable or incomplete.

Important APIs/types/functions: exported `Client34Eradicate(BOOL keepConfig)` orchestrates removal. Helpers include `ClientSoftwareGet()` for install version/path registry discovery, `ClientServiceDelete()` for SCM stop/delete, `DirectoryForceRemove()` for recursive deletion, `FileForceRemove()` for immediate or reboot-delayed deletion, `FolderLocateInTree()` for start-menu cleanup, and `Client34ZapUninstallKeys()` for Microsoft uninstall key cleanup.

Control flow: the main routine detects installed client version and exits if a newer client exists. It stops/deletes the client service, removes install directories and known log/control-panel/shell-extension files, optionally removes config files, repeatedly finds and removes "Transarc AFS Client" folders, deletes legacy registry values/keys, removes the client from network provider order, and removes its program directory from PATH.

State/persistence: no durable internal state. Persistent effects are deletion or delayed deletion of files/directories, service removal, registry mutation, PATH mutation, and provider-order mutation.

Dependencies/integration: depends on OpenAFS `afsreg` registry helpers, `sutil` PATH/provider helpers, Windows filesystem/SCM APIs, and legacy registry key names.

Risks/test signals: path buffers use `sprintf()` into `MAX_PATH`, removal is intentionally destructive, and partial failures are accumulated while cleanup continues. Tests should run in a disposable Windows fixture and cover missing registry info, newer version no-op, in-use file delayed deletion, same-drive temp fallback, service absent/active/marked-for-delete cases, uninstall-key enumeration, and `keepConfig` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.h

Purpose: public C/C++ header for the forced legacy-client removal helper.

Important APIs/types/functions: declares `DWORD Client34Eradicate(BOOL keepConfig)` inside `extern "C"` guards and protects inclusion with `AFS_FORCEREMOVE_H`.

Control flow: callers invoke the single exported removal routine; implementation handles all sequencing.

State/persistence: no header state. The implementation mutates services, registry, filesystem, PATH, and provider order.

Dependencies/integration: depends on Windows `DWORD` and `BOOL` types being defined before inclusion. Used by setup DLL and `afsrm.c`.

Risks/test signals: consumers need to interpret Win32 error codes, not Boolean success. Compile tests should verify C and C++ linkage and inclusion order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.cpp

Purpose: displays a modal progress dialog with localized UI and animated logo for setup operations that may block.

Important APIs/types/functions: exported `ShowProgressDialog(char *pszMsg)` starts a new thread running `DisplayProgressDlg()`. `HideProgressDialog()` posts `WM_QUIT` to the dialog. `ProgressDlgProc()` handles initialization and quit. `OnInitDialog()` sets message text and starts logo animation; `OnQuit()` stops animation and ends the dialog.

Control flow: caller stores a message pointer in global `pszProgressMsg`, spawns the dialog thread, and later posts quit. The modal dialog is created via `ModalDialog()` with resource `IDD_PROGRESS`.

State/persistence: global `hDlg`, `pszProgressMsg`, and `hLogo` hold dialog state. There is no persistence beyond UI lifetime.

Dependencies/integration: depends on Windows threading/dialog APIs, `talocale`, `resource.h`, and `animate_icon`.

Risks/test signals: `ShowProgressDialog()` calls `CloseHandle(hThread)` before testing `hThread != 0`; if `CreateThread()` fails, closing a null handle is unsafe. The message pointer is not copied, so caller lifetime matters. Tests should cover creation failure, show/hide sequencing, repeated calls, dialog-thread exit, and animation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.h

Purpose: C ABI declaration header for setup progress dialog helpers.

Important APIs/types/functions: declares `BOOL ShowProgressDialog(char *pszMsg)` and `void HideProgressDialog(void)` inside `extern "C"` guards for C++ consumers.

Control flow: callers show the dialog before a long task and hide it afterward.

State/persistence: no header state; implementation owns process-global dialog handles and message pointer.

Dependencies/integration: requires Windows `BOOL` type. Used by `afs_setup_utils.cpp` and implemented by `progress_dlg.cpp`.

Risks/test signals: header has no include guard. Compile tests should catch repeated inclusion issues and C/C++ linkage compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/resource.h

Purpose: central resource ID header for the OpenAFS setup utilities DLL.

Important APIs/types/functions: defines string IDs for install/uninstall failures, service errors, product names, preservation prompts, progress messages, dialogs (`IDD_PROGRESS`, `IDD_LICENSE`), controls (`IDC_LOGO`, `IDC_MSG`, `IDC_PRINT`, `IDC_TEXT`), and spinner icons (`IDI_SPIN1` through `IDI_SPINSTOP`).

Control flow: no executable flow. Resource IDs are consumed by `TaLocale`, message boxes, dialogs, and animation code.

State/persistence: no runtime state.

Dependencies/integration: used by setup resource scripts, `afs_setup_utils.cpp`, `progress_dlg.cpp`, and `animate_icon.cpp`.

Risks/test signals: ID stability matters for localized resource DLLs and dialog/control lookup. Tests should compile all localized `.rc` files and smoke-test resource loading for every ID used by code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.c -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.c

Purpose: Windows install/uninstall utility functions for network provider order and system environment variables, especially PATH.

Important APIs/types/functions: exported `InNetworkProviderOrder()`, `AddToProviderOrder()`, `RemoveFromProviderOrder()`, `ReadSystemEnv()`, `WriteSystemEnv()`, `AddToSystemPath()`, `RemoveFromSystemPath()`, and `IsWinNT()`. Private helpers read/write registry environment values on NT, read/write `c:\autoexec.bat` on Win9x, and perform case-insensitive substring search.

Control flow: provider-order operations open `HKLM...\NetworkProvider\Order`, read `ProviderOrder`, append or remove comma-separated entries, and write it back. Environment operations dispatch to registry or autoexec based on `GetVersion()`. PATH add/remove reads current `Path`, avoids duplicates with substring matching, appends with semicolon, or rebuilds a semicolon-separated list excluding the target.

State/persistence: persistent effects are registry updates to provider order and environment, or edits to `c:\autoexec.bat` via a temp file on Win9x. Allocated strings returned by read helpers must be freed by callers.

Dependencies/integration: depends on OpenAFS `afsreg` alternate registry helpers, Windows registry/filesystem APIs, and C runtime string/memory functions. Used by forced removal and setup utility code.

Risks/test signals: duplicate detection is substring-based, so a shorter path/provider token may match unintended entries. Buffer sizing for provider append allocates old length plus new length plus one comma byte but relies on null accounting from registry length. Tests should cover missing values, empty PATH, case-insensitive exact segment removal, substring false positives, NT vs Win9x dispatch, and autoexec temp-copy failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.h -->
# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.h

Purpose: public header for setup utility functions that manipulate provider order and system environment.

Important APIs/types/functions: declares provider order helpers, system environment read/write helpers, PATH add/remove helpers, and `IsWinNT()` inside `extern "C"` guards with include guard `AFS_SUTIL_H`.

Control flow: callers use these as Boolean-returning utility operations; implementation chooses registry or autoexec behavior.

State/persistence: no header state. Implementations persist registry or autoexec changes.

Dependencies/integration: requires Windows `BOOL` and C string types. Used by setup DLL and forced removal code.

Risks/test signals: APIs return only `BOOL`, losing specific Win32 error details. Compile tests should verify C/C++ consumers and inclusion order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvr.idl -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvr.idl

Purpose: MIDL RPC contract for the OpenAFS Windows administration server interface.

Important APIs/types/functions: defines `ITaAfsAdminSvr` with UUID `ae274620-dea3-11d1-bfb3-00a024c0d1ef`, implicit binding handle `hBindTaAfsAdminSvr`, and imports `ITaAfsAdmSvrTypes.idl`. Operations cover client lifecycle (`Connect`, `Disconnect`, `Ping`), credentials (`Crack/Get/Set/Push`), local cell and error translation, action queries, cell open/close, object find/get/refresh, callback hosting and action callback, random key generation, user/group administration, cell property changes, and refresh-rate configuration.

Control flow: clients connect to obtain an `idClient`, keep it alive with ping every `csecAFSADMSVR_CLIENT_PING`, open a cell with credentials, query or mutate objects, receive callbacks through `AfsAdmSvr_CallbackHost()`, and disconnect. Many calls return Boolean-like `int` plus an out `ULONG *pStatus` for detailed errors.

State/persistence: the IDL defines remote state handles: client cookies, credential handles, ASID object identifiers, server-side object caches, and action lists. Persistence is in the server and underlying AFS cell, not the IDL.

Dependencies/integration: depends on MIDL, RPC runtime, and the shared types file. Generated headers/stubs are consumed by server implementations (`TaAfsAdmSvr*.cpp`) and client wrappers (`TaAfsAdmSvrClient*.cpp`).

Risks/test signals: interface compatibility is critical because IDL changes affect generated ABI and marshaling. Passwords are accepted as plain `STRING` parameters. Tests should include MIDL generation, client/server round trips, callback thread behavior, allocation/free semantics for returned lists, invalid client cookies, and cross-version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvr.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvrTypes.idl -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvrTypes.idl

Purpose: shared MIDL type definitions for the OpenAFS Windows administration server RPC interface.

Important APIs/types/functions: defines `ASID`, `ASOBJTYPE`, fixed `STRING[256]`, volume/account/service/file-set enums, `ASACTION` with discriminated union by action type, `ASOBJPROP` with discriminated union by object type, variable-sized `ASIDLIST`, `ASOBJPROPLIST`, and `ASACTIONLIST`, search/get enums, and parameter structs for changing cells/users/groups and creating/deleting users/groups.

Control flow: these structures are marshaled between client and server for searches, property queries, updates, callbacks, and list management. Version fields such as `verPROP_NO_OBJECT`, `verPROP_RUDIMENTARY`, and `verPROP_FIRST_SCAN` let clients request only changed cached properties.

State/persistence: the file defines wire-format state, not storage. ASIDs are pointer-sized identifiers tied to a server process, and object-property versions represent server cache freshness.

Dependencies/integration: imports `wtypes.idl` for Windows types and uses `cpp_quote` to avoid clashes with Windows/AFS class headers. It is included by the main admin-server IDL and generated client/server C++ code.

Risks/test signals: fixed string lengths can truncate names/passwords; pointer-sized `UINT_PTR` in RPC structures is ABI-sensitive; duplicate `FILESETSTATE_LOCKED` definition appears in the file. Tests should exercise MIDL generation on target compilers, 32-bit pointer assumptions, union discriminants, list allocation lengths, and versioned cache update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvrTypes.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.cpp

Purpose: implements the core server-side RPC entry points declared by `ITaAfsAdmSvr.idl` for connection, credentials, cell/object lookup, object property cache access, refresh invalidation, callbacks, and random key generation.

Important APIs/types/functions: `AfsAdmSvr_Connect/Ping/Disconnect` manage client cookies. Credential APIs wrap `afsclient_TokenQuery`, `afsclient_TokenGetExisting`, `afsclient_TokenGetNew`, and cell credential assignment. Cell APIs call `CELL::OpenCell()`/`CloseCell()`. Object find/get APIs dispatch to `AfsAdmSvr_Search_*`, `AfsAdmSvr_GetCurrentProperties()`, `AfsAdmSvr_ObtainFullProperties()`, and list helpers. `AfsAdmSvr_CallbackHost()` runs the callback manager, and `AfsAdmSvr_GetRandomKey()` delegates to `AfsClass_GetRandomKey()`.

Control flow: most entry points begin an operation, validate `idClient`, perform type checks with `GetAsidType()`, call the AFS class/client subsystem, write `pStatus` on failure through helper macros, and end the operation. Search refreshes scope when requested, uses optimized one-user/one-group lookup where possible, then dispatches based on search scope type and requested object type. Property queries return data only when the server version is newer unless `RETURN_DATA_ALWAYS` is requested.

State/persistence: server state includes client registrations, operation/action tracking, opened cell identities, credentials bound to cells, object property caches, and callback queues. Persistent changes are delegated to AFS cell operations and token management.

Dependencies/integration: depends on winsock headers, roken, AFS client libraries, `AfsClass`, `AfsAppLib`, generated RPC types, and many internal admin-server helpers from `TaAfsAdmSvrInternal.h`.

Risks/test signals: every RPC boundary depends on client-cookie validation and correct `AfsAdmSvr_EndOperation()` balancing. Some copy operations use fixed `STRING` buffers. `asc_CredentialsSet()` clients send plaintext passwords to this interface. Tests should cover invalid ASID/client combinations, search dispatch matrix, cache version filtering, full-property upgrade, operation cleanup on failures, callback host shutdown, and RPC exception behavior from clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.h

Purpose: common public header for the OpenAFS Windows administration server executable and client library.

Important APIs/types/functions: includes RPC/Windows/localization/generated admin-server headers and defines program name, command-line keywords (`Timed`, `Manual`, `Users`, `Volumes`, `Debug`), default RPC namespace entry name, and default endpoint `1025`.

Control flow: admin server startup and client binding code use these constants to decide auto-shutdown/manual startup, auto-open scope, debug behavior, and binding fallback.

State/persistence: no state in the header. The endpoint and entry name define external binding identity.

Dependencies/integration: pulls in generated `iTaAfsAdmSvr.h`, common list helpers, `TaLocale`, and optionally app-library declarations.

Risks/test signals: default endpoint collisions or namespace export failures affect all clients. Tests should verify server command-line parsing, fallback endpoint binding, and generated header inclusion order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.cpp

Purpose: manages server-to-client callback delivery for admin-server events, currently action start/finish notifications.

Important APIs/types/functions: `CALLBACKDATA` stores callback type, finished flag, and optional copied `ASACTION`. `AfsAdmSvr_CallbackManager()` owns the callback loop. `AfsAdmSvr_PostCallback()` queues callback data and signals the event. `AfsAdmSvr_StopCallbackManagers()` requests shutdown. `AfsAdmSvr_FreeCallbackData()` releases copied action data.

Control flow: the first manager creates a manual-reset event and hash list. The manager waits, stops if requested, otherwise copies queued callbacks to a local list while holding the admin lock, clears the shared queue/event, releases the lock, invokes generated callback functions with exceptions swallowed, frees each item, and repeats. The last manager deletes the list and closes the event.

State/persistence: static struct `l` stores event handle, callback list, stop flag, and manager count. No disk persistence.

Dependencies/integration: depends on admin-server locking (`AfsAdmSvr_Enter/Leave`), OpenAFS `HASHLIST`, generated RPC callback `AfsAdmSvrCallback_Action()`, and action structures from the IDL.

Risks/test signals: callbacks are best-effort and exceptions are suppressed, so clients can miss notifications without server failure. `fStopManagers` is not reset when a new manager starts after shutdown. Tests should cover concurrent posting, no-lock callback invocation, manager start/stop cycles, callback exception swallowing, and queue cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.h

Purpose: declares callback manager APIs for the admin server.

Important APIs/types/functions: defines `CALLBACKTYPE` with `cbtACTION`, declares `AfsAdmSvr_CallbackManager()`, `AfsAdmSvr_PostCallback(CALLBACKTYPE, BOOL, LPASACTION)`, and `AfsAdmSvr_StopCallbackManagers()`.

Control flow: server code starts a callback host loop, posts action callbacks as operations change, and stops managers during shutdown.

State/persistence: no header state; implementation uses a process-global callback queue and event.

Dependencies/integration: includes `TaAfsAdmSvr.h` for shared types. Integrated with generated RPC callback routines and action tracking.

Risks/test signals: adding callback types requires updating both enum and dispatch switch. Compile tests should catch mismatches with `TaAfsAdmSvrCallback.cpp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCell.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCell.cpp

Purpose: implements server-side RPC operations for cell-level administration.

Important APIs/types/functions: `AfsAdmSvr_ChangeCell()` changes PTS cell properties from `AFSADMSVR_CHANGECELL_PARAMS`; `AfsAdmSvr_SetRefreshRate()` starts/stops or adjusts the periodic refresh thread for a cell.

Control flow: `ChangeCell` creates an `ACTION_CELL_CHANGE`, begins an operation, validates client, maps IDL parameters to `PTSPROPERTIES`, calls `AfsClass_SetPtsProperties()`, then refreshes/tests cached properties for the cell. `SetRefreshRate` validates client and calls `AfsAdmSvr_StopCellRefreshThread()` when rate is zero or `AfsAdmSvr_SetCellRefreshRate()` otherwise.

State/persistence: mutates the AFS cell's PTS properties through AFS class APIs and server refresh-thread state. No local file persistence.

Dependencies/integration: depends on `TaAfsAdmSvrInternal.h`, AfsClass PTS APIs, operation/action tracking, and cell refresh helpers.

Risks/test signals: property changes must be reflected in cache and notifications after success. Tests should cover invalid clients, invalid cell IDs, AFS class failures, action lifecycle, zero/nonzero refresh rates, and cache update after mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCell.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.cpp

Purpose: implements the main client-side `asc_*` library wrappers for the admin-server RPC interface plus list allocation/free helpers and callback dispatch.

Important APIs/types/functions: `MIDL_user_allocate/free` bridge RPC allocation to OpenAFS `Allocate/Free`. `asc_AsidList*`, `asc_ObjPropList*`, and `asc_ActionList*` wrap common list helpers. `asc_AdminServerOpen/Close` manage sockets, binding, ping and callback threads. Credential, cell, object, action, notification, and random-key wrappers call corresponding `AfsAdmSvr_*` RPCs inside `RpcTryExcept`. Fast object getters read the local cache only. `AfsAdmSvrCallback_Action()` maps server callbacks to local notification listeners.

Control flow: opening initializes Winsock once, binds to an existing server or starts one when local and unavailable, starts ping and callback helper threads, and increments a request count. Cell open creates a local cache and fetches rudimentary cell properties. Object-property getters refresh server data only if local versions are stale, then copy cached properties. Refresh calls invalidate server cache and trigger listener requery. All RPC failures are normalized to `RPC_S_CALL_FAILED_DNE`.

State/persistence: static `l` tracks socket initialization and admin-server open reference count. Client-side caches and listeners live in other modules. No disk persistence, but calls can mutate remote AFS state.

Dependencies/integration: depends on generated RPC stubs, binding/cache/notify/ping internal headers, OpenAFS common list helpers, Windows RPC exception macros, Winsock, and AFS app allocation functions.

Risks/test signals: reference counting is not protected by `asc_Enter()` in open/close, and fixed `STRING` copies can overflow if callers provide long values. A TODO notes passwords are sent without encryption. Tests should cover bind failure and auto-fork paths, repeated open/close, ping/callback thread lifecycle, cache creation failure rollback, RPC exception handling, fast getters with missing/deleted properties, and listener notification delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.h

Purpose: public client-library API for applications that talk to the OpenAFS Windows administration server.

Important APIs/types/functions: defines `ADMINAPI`, notification messages `WM_ASC_NOTIFY_OBJECT` and `WM_ASC_NOTIFY_ACTION`, list helper prototypes, admin-server open/close, credentials, local cell/error translation, cell/object operations, refresh, random key, fast cache getters, critical-section access, notifications, action queries/listeners, and user/group administration functions.

Control flow: consumers open an admin server, obtain credentials, open cells, query/mutate objects, optionally register window notifications, then close cells and server connections.

State/persistence: header has no state. Implementations maintain process-global binding, cache, ping/callback threads, and listener lists.

Dependencies/integration: includes `TaAfsAdmSvr.h` and generated IDL types. Intended for Win32 GUI/admin tools using HWND notifications.

Risks/test signals: API uses fixed buffers and many optional `ULONG *pStatus` outputs; callers must free returned lists with matching `asc_*Free` functions. Tests should compile representative consumers and verify C++ default arguments, notification message contracts, and free/ownership rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.cpp

Purpose: implements client-side binding to the admin server and fallback process launch.

Important APIs/types/functions: `BindToAdminServer()` composes an RPC string binding for TCP endpoint `AFSADMSVR_ENDPOINT_DEFAULT`, validates it, and optionally retries for 15 seconds. `UnbindFromAdminServer()` disconnects and frees the global binding handle. `ForkNewAdminServer()` locates and `WinExec`s `TaAfsAdmSvr.exe Timed Manual`. `ValidateBinding()` temporarily assigns `hBindTaAfsAdminSvr` and calls `AfsAdmSvr_Connect()`. `ResolveAddress()` resolves hostnames to IPv4 strings.

Control flow: binding first tries the well-known endpoint, because namespace export may fail on some Windows versions. If validation succeeds, the binding becomes global. If binding fails with call-failed and caller can wait, it sleeps/retries. Local open code can fork a hidden timed/manual server and then bind again.

State/persistence: mutates global generated RPC binding handle `hBindTaAfsAdminSvr`. Launching the server creates a separate process; no file persistence.

Dependencies/integration: depends on Winsock, Windows RPC, generated admin-server binding globals, command constants in `TaAfsAdmSvr.h`, and client open logic.

Risks/test signals: endpoint 1025 can collide, `ResolveAddress()` has simplistic numeric-IP detection, and `UnbindFromAdminServer()` shadows `status` inside `RpcTryExcept`. Tests should cover remote address, local auto-fork, retry timeout, invalid binding rollback, hostname resolution failures, and RPC exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.h

Purpose: internal client-library header for admin-server binding helpers.

Important APIs/types/functions: declares `BindToAdminServer()`, `UnbindFromAdminServer()`, `ForkNewAdminServer()`, and `ResolveAddress()`.

Control flow: used by `asc_AdminServerOpen()` and `asc_AdminServerClose()` to establish or release the RPC binding.

State/persistence: no header state; implementation mutates the global RPC binding and may launch a server process.

Dependencies/integration: expects `ADMINAPI`, `LPCTSTR`, `UINT_PTR`, and status types from enclosing client headers.

Risks/test signals: this is internal but affects connection reliability. Compile tests should catch include-order dependencies and signature drift from implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.cpp

Purpose: implements the client-side per-cell object property cache for admin-server clients.

Important APIs/types/functions: `CELLCACHE` holds a cell ASID, a hash list of `ASOBJPROP` entries keyed by object ASID, and a reference count. `CreateCellCache()`/`DestroyCellCache()` manage cache lifetime. `GetCachedProperties()` looks up an object. `UpdateCachedProperties()` inserts or replaces cached properties and notifies listeners. `RefreshCachedProperties()` overloads fetch one object or a list from the server using property versions to request only out-of-date data. Hash callbacks compare/hash cell and object ASIDs.

Control flow: cell open creates/increments a cache. Property getters call refresh, which builds version inputs from cached entries, performs `AfsAdmSvr_GetObject(s)` inside RPC exception handling, and updates local cache for returned objects. Destroy decrements reference count and frees all cached `ASOBJPROP` allocations when it reaches zero.

State/persistence: process-global `l` stores all cell caches and their hash key. State is in memory only and tied to ASIDs from a server process.

Dependencies/integration: depends on `HASHLIST`, `asc_Enter/Leave` critical section, generated RPC functions, object notification helpers, and OpenAFS allocation macros.

Risks/test signals: returned pointers from `GetCachedProperties()` are only stable while cache entries remain; callers copy immediately in most paths. Reference-count and hash-list cleanup are key. Tests should cover multiple opens of the same cell, list refresh with version lParams, deleted/no-object properties, notification firing, destroy while listeners exist, and RPC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.h

Purpose: internal header for client-side admin-server object cache operations.

Important APIs/types/functions: declares cache lifecycle (`CreateCellCache`, `DestroyCellCache`), lookup (`GetCachedProperties`), and single/multiple `RefreshCachedProperties()` overloads.

Control flow: higher-level client wrappers use these functions during cell open/close and property retrieval.

State/persistence: no header state; implementation keeps process-global in-memory cache.

Dependencies/integration: requires IDL types such as `ASID`, `LPASOBJPROP`, `LPASIDLIST`, and `AFSADMSVR_GET_LEVEL`.

Risks/test signals: callers must not free or persist `GetCachedProperties()` pointers. Compile tests should verify overloads are only consumed from C++.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCell.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCell.cpp

Purpose: implements client-side wrappers for cell mutation and refresh-rate configuration.

Important APIs/types/functions: `asc_CellChange()` wraps `AfsAdmSvr_ChangeCell()` and refreshes cell properties on success. `asc_CellRefreshRateSet()` wraps `AfsAdmSvr_SetRefreshRate()`.

Control flow: both functions call server RPCs under `RpcTryExcept`, map exceptions to `RPC_S_CALL_FAILED_DNE`, and write `pStatus` on failure. `asc_CellChange()` requests all data for the cell after mutation to update local cache.

State/persistence: no local persistent state beyond cache refresh. Server-side calls can change AFS PTS cell properties or refresh-thread state.

Dependencies/integration: depends on client internal header, generated RPC calls, and `asc_ObjectPropertiesGet()` cache behavior.

Risks/test signals: cache refresh failure after a successful server mutation makes the wrapper report failure even though the cell changed. Tests should cover that partial-success behavior, RPC exceptions, invalid clients, and zero/nonzero refresh rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCell.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientGroup.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientGroup.cpp

Purpose: implements client-side wrappers for PTS group administration through the admin-server RPC interface.

Important APIs/types/functions: wrappers include `asc_GroupChange()`, `asc_GroupMembersGet()`, `asc_GroupMemberAdd()`, `asc_GroupMemberRemove()`, `asc_GroupRename()`, `asc_GroupMembershipGet()`, `asc_GroupOwnershipGet()`, `asc_GroupCreate()`, and `asc_GroupDelete()`.

Control flow: each wrapper calls the corresponding `AfsAdmSvr_*` RPC inside `RpcTryExcept`. Mutating operations refresh or probe object properties afterward: change/rename/create request full group properties for cache update; delete intentionally tries a property get and ignores failure to clean up cached state/listeners.

State/persistence: local cache may be updated after operations. Persistent group membership, ownership, names, and existence are changed on the remote AFS cell by server-side handlers.

Dependencies/integration: depends on generated group RPCs, client cache/property wrappers, and RPC exception macros.

Risks/test signals: post-mutation cache refresh can turn a successful mutation into a failed client return. Fixed `STRING` copy in rename can overflow if caller supplies an oversized name. Tests should cover each RPC wrapper, exception-to-status mapping, cache refresh paths, delete stale-cache behavior, and returned ASID list ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientGroup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.cpp

Purpose: provides a lazily initialized process-wide critical section for the admin-server client library.

Important APIs/types/functions: `asc_Enter()` initializes `l.pcs` if needed and enters it. `asc_Leave()` leaves it. `asc_GetCriticalSection()` returns the initialized critical-section pointer for hash lists and other modules.

Control flow: modules call `asc_Enter/Leave` around shared cache/listener operations or assign the critical section to `HASHLIST` instances for internal locking.

State/persistence: static `l.pcs` is allocated once and never freed in this file. No disk persistence.

Dependencies/integration: depends on Windows `CRITICAL_SECTION` and OpenAFS `New` allocation macro. Used by cache and notification modules.

Risks/test signals: lazy initialization is not itself thread-safe if two threads call before `l.pcs` is set. There is no deletion path. Tests should stress concurrent first use, nested use expectations, and modules sharing the same critical section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.h

Purpose: umbrella internal header for the admin-server client library implementation.

Important APIs/types/functions: includes the public client API plus binding, cache, notification, and ping internal headers.

Control flow: implementation `.cpp` files include this to get all client-library internals and shared type declarations.

State/persistence: no state in the header. Included modules manage binding handles, caches, listeners, ping threads, and callback threads.

Dependencies/integration: depends on `TaAfsAdmSvrClient.h`, `TaAfsAdmSvrClientBind.h`, `TaAfsAdmSvrClientCache.h`, `TaAfsAdmSvrClientNotify.h`, and `TaAfsAdmSvrClientPing.h`.

Risks/test signals: broad inclusion can hide dependency cycles and increase rebuild blast radius. Compile tests should ensure all included headers remain self-consistent and no public/internal macro conflict appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.h -->
