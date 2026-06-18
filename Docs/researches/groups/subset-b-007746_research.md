# subset-b-007746 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.c

## Purpose
Implements the AFS page in the NetIDMgr new-credentials and per-identity configuration UI, plus the credential-acquisition message path that obtains or renews AFS tokens after Kerberos succeeds. It owns the editable list of AFS cells, optional realms, token methods, conflict markers, and per-identity persistence.

## Important APIs, Types, And Functions
The file works around `afs_cred_list`/`afs_cred_row` from `afsnewcreds.h`. Row helpers allocate, flush, delete, and populate rows from KCDB AFS credentials. `afs_cred_get_identity_creds()` merges per-identity configuration, global defaults, root-cell/default-cell discovery, realm registry keys, and live KCDB credentials. `afs_dlg_proc()` is the dialog procedure for the new-credentials panel and identity configuration panel. `afs_msg_newcred()` handles NetIDMgr credential-acquisition submessages and ultimately calls `afs_klog()` for each selected row.

## Control Flow
Initialization creates list columns, image lists, method combo entries, and tooltips. Dialog setup fills LRU cells/realms, selects the root cell, loads rows for the active identity, and updates credential text. Add/delete commands validate cell and realm characters, detect cell ownership conflicts across configured identities, and update the row list. During `KMSG_CRED_PROCESS`, the code refuses to run if Kerberos 5 failed, builds a row list from either dialog state or renewal context, applies global method overrides, obtains tokens cell-by-cell, optionally follows linked cells, refreshes token inventory, annotates new KCDB credentials with identity/realm/method, and persists identity data.

## State And Persistence
Persistent state is stored under NetIDMgr config spaces: per-identity `AfsCred/AFSEnabled`, `AfsCred/Cells`, per-cell `MethodName` and `Realm`, global `LRUCells`, `LRURealms`, `DefaultCells`, and global cell-to-identity mappings. It also reads `HKLM\SOFTWARE\OpenAFS\Client\Realms\<realm>` for realm-scoped defaults. Runtime state includes dialog `dirty`, tooltip visibility, critical section protection, row flags, and `nct->credtext`.

## Dependencies And Integration Points
Depends heavily on NetIDMgr KCDB, configuration, credential wizard, alert, action-context, and message APIs; Win32 common controls/tooltips; resource IDs from `langres.h`; AFS helpers in other plugin files (`afs_klog`, `afs_list_tokens_internal`, `afs_method_describe`, method lookup, root-cell lookup, HTML help); and Kerberos credential types. It is called from `afsplugin.c` when credential-acquisition messages arrive.

## Risks
Memory ownership is manual and row deletion compacts arrays after freeing only the removed slot, so stale pointers would be serious if external code cached row addresses. Configuration reads and registry fallbacks have multiple early exits that can leave partial defaults. Conflict resolution can remove the same cell from other identities. The process path uses UI dialog state while holding `d->cs`; blocking token acquisition under that lock can affect UI responsiveness. Linked-cell handling uses a `goto` loop that relies on `afs_klog()` clearing or setting `linkedCell` correctly.

## Test Signals
Useful tests are UI add/delete validation, identity switching, conflict prompts, persistence round trips for `MethodName`/`Realm`, renewal context filtering, linked-cell token acquisition, Kerberos failure handling, and registry/default-cell fallback. No direct unit tests were present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.h

## Purpose
Declares the dialog and row model used by the AFS new-credentials UI and identity configuration panel.

## Important APIs, Types, And Functions
`afs_cred_row` stores a wide-character cell, optional realm, token method, and row flags. `afs_cred_list` owns the dynamic row array. `afs_dlg_data` binds a credential wizard object, row list, enable/dirty flags, tooltip handle, list-view image indexes, synchronization, and configuration-dialog identity state. Public functions include row lifecycle helpers, context/identity credential loaders, row refresh, persistence, dialog procedure, and `afs_msg_newcred()`.

## Control Flow
This header defines constants that drive `afsnewcreds.c`: list subitem indexes, allocation granularity, tooltip timer ID, and flags representing validation, existence, deletion, token acquisition, ownership conflicts, expiration, and config origin.

## State And Persistence
The header itself stores no state, but its structures model persistent per-identity AFS cell choices and transient UI/token state. `DLGROW_FLAG_DONE` bridges the acquisition loop and persistence because only completed rows are recorded in the global cell map.

## Dependencies And Integration Points
Requires NetIDMgr handles and UI types, Win32 dialog types, `afs_tk_method` from `afspext.h`, and resource/control conventions from the plugin.

## Risks
Flags are bitmasks with overlapping lifecycle meanings; consumers must preserve bits carefully. `afs_dlg_data` is shared between UI messages and credential processing and must remain protected by its critical section.

## Test Signals
Compile-time coverage should verify all declarations match `afsnewcreds.c`. Runtime tests should exercise flag combinations in list rendering and acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsp_version.h.in -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsp_version.h.in

## Purpose
NMAKE-style template that generates `afsp_version.h` by copying a literal header body with substituted build variables for plugin version components.

## Important APIs, Types, And Functions
It emits macros for major, minor, patch, auxiliary version fields, aggregate numeric/string version, and comma-list version data. There are no C functions.

## Control Flow
The make target `afsp_version.h: afsp_version.h.in` uses `$(COPY) << $@` heredoc syntax to produce the final header. Build variables such as `$(AFSPLUGIN_VERSION_MAJOR)` and `$(AFSPLUGIN_VERLIST)` must be defined by the surrounding build system.

## State And Persistence
The generated header becomes build artifact state consumed by resource/version compilation. The template itself is static source.

## Dependencies And Integration Points
Integrated with Windows/NMAKE build rules and version resource files. It assumes Secure Endpoints/OpenAFS plugin version variables are set before target evaluation.

## Risks
Missing or malformed make variables generate invalid C preprocessor output. Because it is not a normal C preprocessor template, tools that expect plain C may misread it.

## Test Signals
Validation is a build of the generated `afsp_version.h` and any version resource using `AFSPLUGIN_VERSION_LST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsp_version.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afspext.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afspext.h

## Purpose
Defines the public extension API between the core AFS NetIDMgr plugin and separate extension plugins that can resolve tokens or provide additional token acquisition methods.

## Important APIs, Types, And Functions
Defines cell/host limits, stock token method IDs (`AFS_TOKEN_AUTO`, `AFS_TOKEN_KRB5`, `AFS_TOKEN_KRB524`, `AFS_TOKEN_KRB4`), plugin API version, message type name `AfsExtMessage`, message subtypes `AFS_MSG_ANNOUNCE`, `AFS_MSG_RESOLVE_TOKEN`, and `AFS_MSG_KLOG`, and payload structures `afs_msg_announce`, `afs_msg_resolve_token`, `afs_conf_cell`, and `afs_msg_klog`.

## Control Flow
Extension plugins first send `AFS_MSG_ANNOUNCE` by synchronous message with a subscription handle and optional token-acquisition description. The core plugin later sends resolve-token broadcasts/unicasts or klog requests to extensions that announced token-acquisition support.

## State And Persistence
The API itself has no persistence, but announcements create runtime extension registry state in the core plugin. `token_acq.method_id` is an output assigned by the core plugin and then used in future method selections.

## Dependencies And Integration Points
Uses NetIDMgr `khm_*` types, AFS `ktc_token` and `ktc_principal` structures, WinSock `sockaddr_in`, and the plugin message queue. The sample extension in this subset includes this header.

## Risks
Structures include raw pointers and require synchronous send for announcement because there is no cleanup callback. Version skew is handled only by `cbsize` and `version`; extensions must check and initialize all fields. ANSI cell/realm fields in klog messages require explicit conversion by Unicode-heavy callers.

## Test Signals
Exercise extension announcement, assigned method IDs, resolve-token fallback, klog dispatch to a method extension, and rejection of incompatible versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afspext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin.c

## Purpose
Core NetIDMgr plugin message dispatcher and registration file. It registers AFS as a credential type, installs custom KCDB data types/attributes, hooks configuration panels and help action, manages extension message type registration, refreshes/destroys tokens, and delegates credential-acquisition work.

## Important APIs, Types, And Functions
Global IDs include AFS/Kerberos credential types, AFS extension message type, custom principal/method KCDB types, transient AFS attributes, the shared AFS credset, subscription, and help action. `afs_plugin_cb()` dispatches messages. Principal type callbacks stringify/validate/compare/duplicate `ktc_principal`. `afs_type_method_toString()` localizes method descriptions. `afs_msg_system()`, `afs_msg_cred()`, and `afs_msg_act()` handle lifecycle, token refresh/destroy, new-credentials routing, and help action launching.

## Control Flow
On `KMSG_SYSTEM_INIT`, it optionally imports newer NetIDMgr APIs, sets an initial service-stopped icon, registers the AFS credential type and KCDB types/attributes, creates `afs_credset`, discovers Kerberos credential type IDs, registers config nodes, registers/subscribes the AFS extension message type, removes an `afscreds.exe` shortcut if configured, adds AFS Help under the Help menu, lists existing tokens, and sets `KERBEROSLOGIN_NEVER_PROMPT=1`. On exit, it removes icons/actions, unregisters message types, credential types, attributes, data types, and deletes the credset.

## State And Persistence
Runtime globals carry registered IDs and handles. It reads plugin configuration for `Disableafscreds` and relies on config schemas opened by `main.c`. It does not itself persist token data.

## Dependencies And Integration Points
Integrates with NetIDMgr KMM/KMQ/KCDB/KHUI/KHERR APIs, resources, config dialog procedures, icon/help helpers, extension dispatch in `afsext.c`, token functions in `afsfuncs.c`, and new-credential logic in `afsnewcreds.c`.

## Risks
Initialization has many registrations with partial-failure exits; rollback is mostly deferred to module unload. API-version compatibility uses dynamic function pointers when compiled against older SDKs. Help menu modification must balance lock/unlock and refresh. Destroying selected AFS credentials calls `afs_unlog_cred()` for each matching cred, so context filtering correctness matters.

## Test Signals
Plugin load/unload under old and new NetIDMgr API versions, token refresh, destroy selected tokens, help action insertion/removal, extension message registration, and new/renew credential dispatch are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin_custom.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin_custom.c

## Purpose
Implements an MSI custom action that strips registry-decoration prefixes from selected installer properties representing DWORD values.

## Important APIs, Types, And Functions
`dword_props` lists `OPENAFSVERSIONMAJOR`, `OPENAFSVERSIONMINOR`, and `KFWVERSIONMAJOR`. `strip_decoration()` removes a leading `#` in-place. `StripRegDecoration()` is exported/stdcall-style MSI custom action code that gets and sets properties through `MsiGetProperty()` and `MsiSetProperty()`.

## Control Flow
For each property, the custom action reads up to 16 TCHARs, strips a leading `#` when present, and writes the property back. It always returns `ERROR_SUCCESS`.

## State And Persistence
State is MSI session property data. The effect is transient within installer execution unless later installer tables consume and persist those property values.

## Dependencies And Integration Points
Depends on Windows Installer `msiquery.h`, TCHAR/UNICODE conventions, and installer sequencing that invokes `StripRegDecoration`.

## Risks
The function ignores read/set failures and reports success, which can hide malformed installer state. The 16-character buffer assumes DWORD string representations only.

## Test Signals
MSI custom-action tests should pass properties with and without `#`, missing properties, and boundary-length numeric strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin_custom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.c

## Purpose
Centralizes delayed loading of Windows/security support libraries needed by the AFS NetIDMgr plugin.

## Important APIs, Types, And Functions
Global `AfsAvailable` records import availability. `init_imports()` calls `DelayLoadLibrary()` for `advapi32.dll`, `secur32.dll`, and, on NT-family Windows, `psapi.dll`. `exit_imports()` is a placeholder for delayed import cleanup.

## Control Flow
Initialization short-circuits to `KHM_ERROR_NOT_FOUND` on any delayed-load failure, otherwise marks AFS as available and returns success. OS version detection gates PSAPI loading.

## State And Persistence
Only runtime process state is affected: delayed DLL imports and the global availability flag.

## Dependencies And Integration Points
Depends on `delayload_library.h`, `krbcompat_delayload.h`, Windows version APIs, and constants from `dynimport.h`. Called by `main.c` during module initialization and cleanup.

## Risks
`GetVersionEx()` is legacy and version-manifest sensitive. `AfsAvailable` is set even though commented code suggests a former `afscompat_init()` check. Cleanup currently does not unload delayed libraries.

## Test Signals
Module startup on NT and non-NT target variants, missing-library simulation, and verifying dependent Kerberos/security imports resolve after `init_imports()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.h

## Purpose
Declares dynamic-import constants and functions for the NetIDMgr AFS plugin, while temporarily raising `_WIN32_WINNT` to expose NT security APIs.

## Important APIs, Types, And Functions
Defines DLL names `SERVICE_DLL`, `SECUR32_DLL`, and `PSAPIDLL`, declares `AfsAvailable`, `init_imports()`, and `exit_imports()`, and includes delayed-load support headers.

## Control Flow
The preprocessor saves any lower `_WIN32_WINNT`, sets it to `0x0501` before including `ntsecapi.h`, then restores the previous value.

## State And Persistence
No persistent state; it exposes runtime import state through `AfsAvailable`.

## Dependencies And Integration Points
Used by `main.c`, `dynimport.c`, and Kerberos compatibility code. It depends on Windows headers, NetIDMgr `khdefs.h`, Toolhelp, and delay-load headers.

## Risks
Temporarily redefining `_WIN32_WINNT` can surprise include-order-sensitive builds. Consumers must call `init_imports()` before relying on delayed imports.

## Test Signals
Compile with multiple `_WIN32_WINNT` definitions and verify restored macro behavior; load plugin on supported Windows targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/Makefile -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/Makefile

## Purpose
NMAKE sample build file for a third-party AFS NetIDMgr extension plugin.

## Important APIs, Types, And Functions
Defines plugin/module/auth method names, DLL basename, version macros, environment checks (`MSSDK`, `KFWSDKDIR`, `AFSPLUGINDIR`, `CPU`), output directories, compiler/resource/message compiler/linker macros, manifest embedding helpers, generated `credacq_config.h`, main DLL target, and language resource DLL target.

## Control Flow
`all` creates directories, generates `credacq_config.h`, builds the plugin DLL from `afspext.obj`, `main.obj`, `plugin.obj`, and `config_main.obj`, then builds language resources. Pattern rules compile C and RC files. Clean targets remove object, destination, generated config, DLLs, and resources.

## State And Persistence
Produces `dest\<CPU>_<debug|release>` and `obj\<CPU>_<debug|release>` trees plus generated headers and DLLs. It does not mutate source beyond generated output directories.

## Dependencies And Integration Points
Requires Visual Studio/Platform SDK `Win32.Mak`, KfW SDK libraries/includes, AFS plugin headers, NetIDMgr import library, Windows resource compiler, linker, manifest tool, and sample language resources.

## Risks
The template ships with TODO placeholder names and version fields. It assumes classic NMAKE syntax and Visual Studio manifest macros. Missing `AFSPLUGINDIR` or SDK layout mismatch stops the build.

## Test Signals
Run debug and release builds with real SDK paths; verify generated `credacq_config.h`, plugin DLL link against `nidmgr32.lib`, manifest embedding, and `*_en_us.dll` resource output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/afspext.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/afspext.c

## Purpose
Sample extension implementation stubs for AFS extension messages.

## Important APIs, Types, And Functions
`handle_AFS_MSG_RESOLVE_TOKEN()` receives `afs_msg_resolve_token` and should set `ident` and `method` if it can identify a token. `handle_AFS_MSG_KLOG()` receives `afs_msg_klog` and should obtain a token. `handle_AFS_MSG()` dispatches extension message subtypes.

## Control Flow
The dispatcher switches on `AFS_MSG_RESOLVE_TOKEN` and `AFS_MSG_KLOG`, returning `KHM_ERROR_NOT_IMPLEMENTED` for both stock stubs and for unknown messages.

## State And Persistence
No persistent state is implemented. A real extension would likely use NetIDMgr identity handles and any external authentication state required by its token method.

## Dependencies And Integration Points
Includes sample `credprov.h` and core `afspext.h`. It is reached through the subscription created during sample plugin initialization in `plugin.c`.

## Risks
As shipped, enabling `provide_token_acq` in the sample registers a method that cannot actually acquire or resolve tokens. Implementers must respect ownership rules for identity handles returned in resolve-token messages.

## Test Signals
After implementing, test resolve-token success/failure, klog success/failure, and Auto-method fallback behavior when this extension is tried after stock methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/afspext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/config_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/config_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/credprov.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/credprov.h

## Purpose
Central header for the sample AFS extension plugin.

## Important APIs, Types, And Functions
Enforces `_UNICODE`, includes generated `credacq_config.h`, derives wide-string plugin/module/auth method macros, defines config node naming, includes Windows, NetIDMgr, `afspext.h`, resources, and `strsafe.h`, and declares globals and message/dialog functions.

## Control Flow
Mostly preprocessor validation and macro derivation. Build fails if generated configuration macros like `MYPLUGIN_NAME`, `MYMODULE_NAME`, `MYPLUGIN_DLLBASE`, or `AUTHMETHOD_NAME` are missing.

## State And Persistence
Declares runtime module/resource handles, assigned token method ID `tk_method`, and logging facility name. No state is stored directly.

## Dependencies And Integration Points
Generated by the sample Makefile, consumed by all sample `.c` files, and tied to NetIDMgr/KMM, the AFS extension API, and sample resources.

## Risks
Because many identifiers derive from make macros, stale generated headers or placeholder names can produce conflicting plugin registrations. `_T()` macro use assumes TCHAR/UNICODE consistency.

## Test Signals
Build with generated config present/missing, Unicode enabled, and custom plugin names. Verify all sample translation units share the same macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/credprov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/langres.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/langres.h

## Purpose
Resource ID header for the sample extension plugin language resource DLL.

## Important APIs, Types, And Functions
Defines string/icon/dialog IDs for plugin description, credential-template text, config descriptions, and token method descriptions. Also contains Visual Studio `APSTUDIO_INVOKED` next-ID defaults.

## Control Flow
No executable control flow; it is included by C and resource compiler inputs.

## State And Persistence
Defines numeric identity of resources embedded into the sample language DLL.

## Dependencies And Integration Points
Used by sample `main.c`, `plugin.c`, config code, and `lang\en_us\langres.rc` built by the sample Makefile.

## Risks
Duplicate or changed IDs can desynchronize C `LoadString()` calls from resource content. The generated-file path in comments is historical and not authoritative.

## Test Signals
Resource compilation and runtime `LoadString()` success for plugin description and token method strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/langres.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/main.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/main.c

## Purpose
Sample NetIDMgr module entry point for an AFS extension DLL.

## Important APIs, Types, And Functions
Declares module/resource handles, facility string, supported locales, `init_module()`, `exit_module()`, and `DllMain()`. `init_module()` sets locale info, obtains the selected resource module, fills a `kmm_plugin_reg`, and calls `kmm_provide_plugin()`.

## Control Flow
On module initialization, it registers US English resources, loads plugin description/icon, declares dependency on `AfsCred`, and provides one miscellaneous plugin whose message processor is `plugin_msg_proc`. `exit_module()` is a placeholder. `DllMain()` records the DLL instance on process attach.

## State And Persistence
Runtime globals hold module and resource handles. No persistent settings are written.

## Dependencies And Integration Points
Depends on KMM module lifecycle, sample resource DLL naming from the Makefile, `credprov.h`, and plugin message handling in `plugin.c`.

## Risks
Failure to load resources aborts module initialization. The sample relies on the core AFS plugin dependency being named `AfsCred`. Icons loaded for registration need ownership behavior consistent with KMM expectations.

## Test Signals
Load sample module in NetIDMgr with core AFS plugin present, verify locale selection, plugin registration, dependency handling, icon/description loading, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/plugin.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/plugin.c

## Purpose
Sample plugin message processor that announces an AFS extension and optionally registers a new token acquisition method.

## Important APIs, Types, And Functions
Globals `msg_type_afs`, `g_credset`, and assigned `tk_method` track extension integration. `handle_kmsg_system()` handles plugin lifecycle. `plugin_msg_proc()` dispatches NetIDMgr system messages and AFS extension messages.

## Control Flow
On `KMSG_SYSTEM_INIT`, the plugin finds the AFS extension message type, creates a unicast subscription for `handle_AFS_MSG`, fills an `afs_msg_announce` structure, loads token method descriptions, synchronously sends `AFS_MSG_ANNOUNCE`, and saves the returned method ID. Optional configuration-panel registration is guarded by `USE_CONFIGURATION_PANELS`. On exit, it removes the optional config node. AFS messages are forwarded to `handle_AFS_MSG()`.

## State And Persistence
Runtime state includes message type ID and token method ID assigned by the core plugin. Optional config registration adds UI state but no sample persistence.

## Dependencies And Integration Points
Integrates with core AFS plugin through `AFS_MSG_TYPENAME`, sample handlers in `afspext.c`, NetIDMgr KMQ/KHUI, and resource strings from `langres.h`.

## Risks
Announcement uses stack-backed string buffers and must remain synchronous, matching the API contract. Since sample handlers return not implemented, registering `provide_token_acq=TRUE` creates a visible method that fails until filled in.

## Test Signals
Core plugin present/absent startup, subscription cleanup on failed announce, assigned method ID availability, optional config registration, and dispatch of AFS messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/help/afsplhlp.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/help/afsplhlp.h

## Purpose
Defines HTML Help context IDs for the AFS NetIDMgr plugin UI.

## Important APIs, Types, And Functions
Maps controls/actions such as obtain, cell, realm, method, add/delete, token list, service status/start/stop/version/company/control panel, and start-afscreds to numeric IDs.

## Control Flow
No executable control flow. `afsnewcreds.c` and configuration dialogs use these IDs in help context arrays passed to `afs_html_help()`.

## State And Persistence
Static numeric resource contract only.

## Dependencies And Integration Points
Integrated with `.chm`/HTML Help topic maps and Win32 `WM_HELP` processing.

## Risks
IDs must stay synchronized with help content; otherwise context help opens wrong or missing topics.

## Test Signals
Press F1/help on each mapped UI control and verify expected popup/topic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/help/afsplhlp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.c

## Purpose
Provides Kerberos 5 helper routines for the AFS NetIDMgr plugin, especially context/cache initialization and finding the best credential cache for a NetIDMgr identity.

## Important APIs, Types, And Functions
`khm_krb5_error()` optionally formats an error and frees context/cache. `khm_krb5_initialize()` initializes a krb5 context, enables DES CRC enctype if valid, resolves an identity-specific cache, optionally falls back to default cache depending on build flags, and sets cache flags. `khm_get_identity_expiration_time()` validates cache principal against a NetIDMgr identity and finds TGT end/renewal expiration. `khm_krb5_find_ccache_for_identity()` scans collection caches, optional MSLSA, and configured FILE caches to pick the cache with the best expiration.

## Control Flow
Cache selection starts with the krb5 collection cursor, then reads Kerberos plugin parameters `MsLsaList` and `FileCCList` from NetIDMgr config. Each candidate cache is opened, checked for matching principal and valid TGT, and compared by expiration. The winning cache name is returned as Unicode.

## State And Persistence
Reads NetIDMgr Kerberos plugin configuration but writes no persistent state. It mutates caller-owned `krb5_context` and `krb5_ccache` pointers.

## Dependencies And Integration Points
Depends on dynamically imported Kerberos functions, NetIDMgr identity/config APIs, string conversion helpers, and `dynimport.h`. Called by `afsfuncs.c` when acquiring tokens from Kerberos credentials.

## Risks
`khm_krb5_get_error_string()` is declared in the header but not implemented here. Error handling is compiled differently under `NO_KRB5` and optional message-box flags. Cache principal string comparison must match NetIDMgr identity formatting exactly. Small fixed cache-name buffers can truncate unusual cache identifiers.

## Test Signals
Test identities with collection, MSLSA, and file caches; valid, expired, renewable, and mismatched TGTs; missing cache files; no default fallback builds; and DES enctype compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.h

## Purpose
Declares Kerberos helper APIs used by the AFS NetIDMgr plugin.

## Important APIs, Types, And Functions
Under `!NO_KRB5`, declares error handling, error-string formatting, context/cache initialization, cache lookup by identity, identity expiration inspection, and `MAX_HSTNM` fallback.

## Control Flow
No runtime control flow; conditional compilation removes declarations when Kerberos support is disabled.

## State And Persistence
No direct state. Declared functions work with caller-owned Kerberos contexts/caches and NetIDMgr identities.

## Dependencies And Integration Points
Includes `krb5.h` and expects NetIDMgr types to be visible from broader plugin headers. Implemented mostly by `krb5common.c` and consumed by AFS token acquisition code.

## Risks
The header declares `khm_krb5_get_error_string()` without a matching implementation in the researched `.c`, so linkage depends on another file or dead code. Conditional declarations can hide missing stubs in `NO_KRB5` builds.

## Test Signals
Compile/link full plugin with and without `NO_KRB5`; call cache initialization and identity lookup from token acquisition paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/lang/en_us/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/lang/en_us/resource.h

## Purpose
Visual Studio generated resource placeholder for the English-US language resource project.

## Important APIs, Types, And Functions
Contains only `APSTUDIO_INVOKED` next-resource defaults; no explicit runtime resource IDs are defined here.

## Control Flow
No executable control flow.

## State And Persistence
Stores resource-editor metadata for future additions.

## Dependencies And Integration Points
Used by `langres.rc` tooling for the English-US resource DLL. Runtime code primarily relies on the top-level `langres.h` IDs.

## Risks
Because it has no active IDs, accidental use from C code would not provide plugin resource constants. Resource editor updates could introduce IDs that must stay coordinated with `langres.h`.

## Test Signals
Resource compile success and no duplicate ID collisions after editing resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/lang/en_us/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/langres.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/langres.h

## Purpose
Central resource ID map for the core AFS NetIDMgr plugin.

## Important APIs, Types, And Functions
Defines IDs for plugin descriptions, dialogs, config panels, icons, method strings, tooltips, credential text, attribute descriptions, errors, help action strings, status tooltips, context menu commands, and dialog controls.

## Control Flow
No runtime control flow; C files call `LoadString()`, `LoadImage()`, and use dialog/control IDs based on this map.

## State And Persistence
Defines the stable numeric contract between compiled code and language/resource DLLs.

## Dependencies And Integration Points
Used by `afsplugin.c`, `afsnewcreds.c`, `main.c`, config/icon/help files, and resource compiler inputs.

## Risks
Duplicate IDs intentionally share values across different resource classes, which is normal for Windows resources but risky if copied into the wrong namespace. Any ID drift breaks UI loading or command dispatch.

## Test Signals
Resource compilation, plugin startup string/icon loads, dialog creation, tooltip text, method descriptions, help action labels, and menu command routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/langres.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/main.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/main.c

## Purpose
Module-level entry point for the core AFS NetIDMgr plugin DLL.

## Important APIs, Types, And Functions
Defines KMM module/resource handles, configuration-space handles (`csp_plugins`, `csp_afscred`, `csp_params`), supported locales, placeholder `init_afs()`/`exit_afs()`, `init_module()`, `exit_module()`, and `DllMain()`.

## Control Flow
`init_module()` sets locale info, delays Heimdal loading, registers the `AfsCred` credential plugin with dependencies and icon/description, initializes delayed imports, opens the NetIDMgr plugin configuration root, loads `schema_afsconfig`, and opens `AfsCred/Parameters`. `exit_module()` calls delayed import cleanup, closes config spaces, unloads the schema, and clears globals. `DllMain()` records `hInstance` and calls the empty AFS attach/detach hooks.

## State And Persistence
Maintains open handles to plugin configuration spaces and loads a configuration schema. It does not directly write configuration values.

## Dependencies And Integration Points
Integrates KMM module lifecycle, `afs_plugin_cb()` from `afsplugin.c`, resource strings/icons from language DLLs, dynamic imports, Kerberos compatibility delay loading, and schema data from `afsconfig.c`.

## Risks
If initialization fails after `kmm_provide_plugin()`, partial registration may rely on KMM cleanup. Config handles must be opened before other plugin code reads `csp_params`. `DllMain()` intentionally does little, which is correct for loader-lock safety.

## Test Signals
Module load with missing resources, missing imports, schema load failure, normal unload, and successful availability of `csp_params` to new-credential/config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/params.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/params.h

## Purpose
Reserved include guard header for AFS NetIDMgr plugin parameters.

## Important APIs, Types, And Functions
Defines only `__KHIMAIRA_KRBAFSCRED_PARAMS_H`; no parameters, functions, or types are currently present.

## Control Flow
No runtime control flow.

## State And Persistence
No state. It likely exists as a placeholder for future shared parameter declarations.

## Dependencies And Integration Points
May be included by plugin sources expecting a params header, but this researched version contributes no symbols.

## Risks
Empty headers can hide dead include dependencies; future additions must avoid colliding with schema-defined configuration names.

## Test Signals
Compile-only signal: removing or editing it should not change behavior unless includes require the guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/pthread.c -->
# sources/distributed-fs/openafs/src/WINNT/pthread/pthread.c

## Purpose
Implements a deliberately limited POSIX pthread compatibility layer for Windows NT, intended to support OpenAFS code without being a complete pthread implementation.

## Important APIs, Types, And Functions
Implements `pthread_once`, mutex, read/write lock, condition variable, thread create/join/self/equal/exit, attributes, and thread-specific data APIs declared in `pthread.h`. Internal `thread_t` records active threads, join state, Win32 handles/IDs, native-thread marker, and per-thread TSD. Waiter and thread structures are cached in `rx_queue` lists.

## Control Flow
`pthread_once()` uses `InterlockedExchange()` and sleep polling. Mutexes wrap `CRITICAL_SECTION` while rejecting recursive self-locks with `EDEADLK`. RW locks combine write/read mutexes and a condition variable. `pthread_create()` allocates a `thread_t`, adds it to `active_Q`, then starts a Win32 thread running `afs_pthread_create_stub()`. The stub initializes TLS, calls the user routine, catches the custom `pthread_exit` exception, runs TSD destructors, then either signals joiners or caches detached thread state. `pthread_self()` creates pseudo-pthread records for native Win32 threads and starts a watcher thread that removes those records when native handles terminate. Condition variables maintain a queue of per-waiter events and convert absolute POSIX waits to relative Win32 waits.

## State And Persistence
All state is process-local: active/cache queues, waiter cache, TLS indexes, key table/destructors, watcher thread/event/list, and initialization once-controls. `DllMain()` initializes caches on attach and cleans waiter/TSD/thread caches on detach.

## Dependencies And Integration Points
Depends on Win32 synchronization/threading/TLS APIs, MSVC structured exception handling, `rx_queue`, C runtime allocation/time, and OpenAFS Windows build macros. Tests in `pthread/test` exercise key behavior.

## Risks
The file explicitly diverges from full POSIX. Busy waiting in `pthread_once`, non-robust native-thread watcher, named event creation with static counters, incomplete cond-destroy waiter validation, and manual cache cleanup are sensitive. `pthread_rwlock_unlock()` infers write ownership by expecting `pthread_mutex_trylock()` to return `EDEADLK`, which depends on this shim’s mutex semantics. `pthread_exit()` on a native thread raises an unhandled exception by design. `WaitForMultipleObjects()` has maximum handle limits not checked here.

## Test Signals
Existing tests include general pthread behavior, TSD, and native-thread interaction. Additional signals should cover recursive mutex errors, timed waits including timeout race paths, detached/joinable cleanup, native thread TSD destructor cleanup, RW lock contention, DLL detach cleanup, and handle-count limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/pthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/pthread.h -->
# sources/distributed-fs/openafs/src/WINNT/pthread/pthread.h

## Purpose
Declares the Windows pthread compatibility subset implemented by `pthread.c`.

## Important APIs, Types, And Functions
Defines `pthread_once_t`, `pthread_attr_t`, `pthread_condattr_t`, `pthread_mutexattr_t`, `pthread_rwlockattr_t`, `pthread_key_t`, `pthread_t`, `timespec_t`, mutex/condition/rwlock structs, `PTHREAD_CREATE_JOINABLE`, `PTHREAD_CREATE_DETACHED`, `PTHREAD_KEYS_MAX`, and `PTHREAD_ONCE_INIT`. Declares all supported pthread-like functions.

## Control Flow
No executable flow. Static initialization is represented by simple integer fields, enabling `pthread_once()` to work without a Win32 initializer.

## State And Persistence
The public structs expose implementation details: mutexes contain owner TID and `CRITICAL_SECTION`, conditions contain a waiter queue, and rwlocks compose shim mutex/condition objects.

## Dependencies And Integration Points
Includes Windows, time, OpenAFS NT errno mapping, and `rx_queue`. Any OpenAFS code including this header receives the shim definitions rather than system pthreads.

## Risks
Public struct layout couples consumers to this implementation and prevents ABI compatibility with real pthread libraries. `pthread_t` is `void *` to internal `thread_t`, which tests exploit by walking queue internals. `PTHREAD_KEYS_MAX` is fixed at 32.

## Test Signals
Compile OpenAFS Windows targets using pthread APIs, plus ABI/layout assumptions in native tests and TSD tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/pthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/test/native.cpp -->
# sources/distributed-fs/openafs/src/WINNT/pthread/test/native.cpp

## Purpose
Native Win32 interoperability test for the pthread shim.

## Important APIs, Types, And Functions
Defines three tests run by `main()`: `Test1()` checks `pthread_self()` on the main thread, `Test2()` checks a Win32 thread joining a pthread-created thread and receiving its return value, and `Test3()` checks that native Win32 threads registered through `pthread_self()` are removed from the active queue after termination.

## Control Flow
`Test2` creates a Win32 waiter thread and a pthread worker thread, coordinates with a shared DWORD, then verifies `pthread_join()`. `Test3` records initial active queue size using a helper pthread that walks the internal queue representation, starts two Win32 threads and two detached pthreads, advances a shared signal so each exits in order, and checks active queue size decreases after each termination.

## State And Persistence
Test state is process-local shared counters/handles. It intentionally inspects internal `pthread_t`/`rx_queue` layout, making it a white-box test of `pthread.c`.

## Dependencies And Integration Points
Depends on Win32 `CreateThread`, `WaitForSingleObject`, `InterlockedIncrement`, the pthread shim, `rx_queue`, and C++ exception handling around queue walking.

## Risks
Busy-wait loops and fixed `Sleep()` delays can be timing-sensitive on slow or highly loaded hosts. It casts pointers through DWORD-sized values, which is unsafe for 64-bit builds. White-box queue traversal couples the test to internal layout rather than public API.

## Test Signals
Passing output for all three tests indicates main/native thread registration, cross-API join, detached pthread cleanup, and native-thread watcher cleanup are working for 32-bit Windows assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/pthread/test/native.cpp -->
