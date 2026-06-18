# Research: subset-b-007698

Grouped research for OpenAFS Windows `afsd` initialization, service, ACL, firewall, icon, and Kerberos bridge headers. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.c

## Purpose

`afsd_init.c` performs the Windows OpenAFS client cache manager bootstrap. It owns early init logging, global cache manager defaults, registry-driven configuration, RX callback service startup, root cell/root volume resolution, SMB interface parameters, daemon startup, cache manager shutdown, and crash trace/minidump support.

## Important APIs, Types, and Functions

- Global state exported or consumed across the Windows client includes `cm_data`, `cm_rootVolumeName`, `cm_mountRoot`, `cm_mountRootC`, `cm_readonlyVolumeVersioning`, `cm_logChunkSize`, `cm_chunkSize`, `cm_virtualCache`, `cm_verifyData`, `cm_shortNames`, `cm_directIO`, `rdr_ReparsePointPolicy`, `smb_UseV3`, `smb_Enabled`, `LANadapter`, `numBkgD`, `numSvThreads`, `rx_mtu`, `traceOnPanic`, `cm_HostName`, `cm_callbackport`, `cm_NetbiosName`, `cm_CachePath`, `cm_sysNameList`, `cm_sysName64List`, and `TraceOption`.
- `afsi_start()` creates `%TEMP%\afsd_init.log`, truncates it when registry `MaxLogSize` is exceeded, records PATH/OEM code page/locale, and initializes the file handle used by `afsi_log()`.
- `afsi_log()` is the initialization logger, using `StringCbVPrintfA` and optionally date/time prefixes.
- `afsd_ForceTrace()` dumps the in-memory `osi_log_t` trace to `%TEMP%\afsd.log`.
- `afsd_InitServerPreferences()` reads `HKLM\...\Server Preferences\VLDB` and `...\File`, resolves names or IPv4 addresses, and sets admin ranks on `cm_server_t` records via `cm_FindServer`, `cm_NewServer`, `cm_RankServer`, `cm_ChangeRankCellVLServer`, and `cm_ChangeRankVolume`.
- `afsd_InitRoot()` resolves or fakes the root fid, obtains the root scache, and reports startup failure text through `reasonP`.
- `afsd_InitCM()` is the main cache manager initializer. It configures process priority and affinity, trace logging, cache geometry, daemon/thread counts, SMB defaults, sysname lists, RX tuning, security options, CellServDB/DNS/freelance behavior, memory mapped cache, RX services, RPC services, server preferences, and root scache setup.
- `afsd_InitSMB()` reads SMB-specific registry values and either starts `smb_Init()` or disables Microsoft redirector helper settings when SMB is not enabled.
- `afsd_InitDaemons()` starts cache manager background daemons.
- `afsd_ShutdownCM()` shuts down MSRPC, releases the root scache, cleans utilities, and sets `cm_shutdown`.
- `afsd_printStack()`, `GenerateMiniDump()`, `afsd_ExceptionFilter()`, and `afsd_SetUnhandledExceptionFilter()` implement unhandled exception diagnostics through ImageHlp, DbgHelp, Faultrep, and Windows SEH.

## Control Flow

The normal path starts with `afsi_start()` from the service wrapper, then `afsd_InitCM()`. `afsd_InitCM()` initializes Winsock and AFS utility layers, rejects 32-bit service execution under WOW64, reads registry configuration from `AFSREG_CLT_SVC_PARAM_SUBKEY`, applies process/runtime tuning, creates `afsd_logp`, computes cache size/chunk/block geometry, allocates sysname arrays, sets security and SMB/RX options, and records configuration in `cm_initParams`. It then initializes user, connection, server, ioctl, callback, normalization, mapped memory, DNS, RX parameters, RX itself, callback and rxstats services, root cell/freelance state, RPC/MSRPC, server preferences, and finally the root volume/scache.

Startup failures return `-1` and a reason string for the service wrapper to panic/log. Shutdown is intentionally shorter: release RPC state and root cache references, clean utilities, then mark cache manager shutdown for other subsystems.

## State and Persistence Behavior

The file is heavily registry-driven. It reads persistent service/client parameters such as `PriorityClass`, `LockOrderValidation`, `MaxCPUs`, `TraceOption`, `TraceBufferSize`, `SMBRequestMonitor`, `NonPersistentCaching`, `ValidateCache`, `CacheSize`, `ChunkSize`, `blockSize`, `Daemons`, `ServerThreads`, `Stats`, `Volumes`, `Cells`, `LogoffTokenTransfer`, `NetbiosName`, `RootVolume`, `MountRoot`, `CachePath`, `TrapOnPanic`, `SysName`, `SysName64`, `SecurityLevel`, `VerifyData`, `UseDNS`, freelance settings, SMB settings, RX window/MTU/UDP/stat settings, callback port, cache manager policy bits, executable prefetch extensions, and redirector reparse policy. It persists runtime evidence to `%TEMP%\afsd_init.log`, `%TEMP%\afsd.log`, and timestamped `%TEMP%\afsd-*.dmp` files. Cache content itself is initialized through `cm_InitMappedMemory()` using either file-backed or virtual cache state at `cm_CachePath`.

## Dependencies and Integration Points

This code integrates Windows registry, Winsock, process affinity/priority, ImageHlp/DbgHelp/Faultrep, RX/RXAFSCB/RXSTATS, cache manager modules (`cm_*`), SMB modules (`smb_*`), RPC/MSRPC, CellServDB/DNS discovery, optional B+ directories, freelance root support, and the Windows redirector policy surface. It is called by `afsd_service.c` and exposes prototypes through `afsd_init.h`.

## Risks

- `gethostbyname(cm_HostName)` is dereferenced without checking `thp`, so local hostname resolution failure can crash startup.
- Many registry values are trusted after light validation; malformed multi-string/sysname values and oversized counts can pressure fixed arrays.
- `smb_ExecutableExtensions` points into the allocated `pSz` buffer intentionally; later ownership must preserve that buffer for process lifetime.
- RX startup retries on a random port when the configured callback port is unavailable, which may surprise firewall and callback expectations.
- Crash dump generation writes to `%TEMP%` or Windows directory fallback, so permissions and disk exhaustion affect diagnostics.
- Stack walking uses architecture-specific assumptions and `IMAGE_FILE_MACHINE_I386` even around conditional register setup, making non-x86 behavior a compatibility risk.

## Test Signals

- Unit or integration tests should cover registry defaulting and bounds for cache size, chunk size, block size, daemon counts, SMB auth type, RX options, callback port, and sysname parsing.
- Startup tests should exercise file cache and virtual cache paths, missing registry key failure, missing root cell with/without freelance mode, and RX port fallback.
- Service-level tests should verify `afsd_InitSMB()` behavior when redirector initialization disables SMB, when SMB is explicitly enabled/disabled, and when async store sizes are outside valid range.
- Diagnostics tests can trigger `GenerateMiniDump(NULL)` and `afsd_ForceTrace()` with controlled temp paths and invalid handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.h

## Purpose

`afsd_init.h` is the public local header for Windows AFSD initialization. It exposes startup, cache manager, SMB, daemon, shutdown, trace, crash dump, and selected global identity variables to the service wrapper and neighboring modules.

## Important APIs, Types, and Functions

- `afsi_start()` starts the initialization log.
- `afsd_InitCM(char **reasonP)` initializes the cache manager and returns failure context through `reasonP`.
- `afsd_InitSMB(char **reasonP, void *aMBfunc)` initializes or skips the SMB interface using a caller-provided message box callback.
- `GenerateMiniDump(PEXCEPTION_POINTERS ep)`, `afsd_ForceTrace(BOOL flush)`, and `afsd_SetUnhandledExceptionFilter()` expose diagnostics.
- `afsd_InitDaemons(char **reasonP)` starts background daemons.
- `afsd_ShutdownCM(void)` tears down cache-manager state.
- Extern globals include `cm_HostName`, `cm_callbackport`, `cm_NetbiosName`, and `cm_NetbiosNameC`.

## Control Flow

Consumers call these declarations in staged service startup: initialize logging, install exception handling, initialize CM, start SMB or redirector interfaces, start daemons, and later shut down CM. The header itself contains no control flow.

## State and Persistence Behavior

The header exposes mutable process-global identity/network state but does not persist anything. Its declarations allow other compilation units to read or alter the host name, callback port, and NetBIOS names initialized in `afsd_init.c`.

## Dependencies and Integration Points

The prototypes depend on Windows types (`PEXCEPTION_POINTERS`, `BOOL`) and OpenAFS `clientchar_t`. It is included by `afsd_service.c`, binding the Windows service lifecycle to initialization implementation.

## Risks

- There is no include guard in this header, so repeated inclusion relies on compatible declarations.
- The old-style `void afsi_start();` declaration does not specify a prototype argument list in C, which is weaker than `void afsi_start(void)`.
- Exposing global buffers encourages cross-module mutation without local invariants.

## Test Signals

- Build tests should compile with strict prototype warnings.
- Link tests should verify the service binary resolves all declarations from `afsd_init.c`.
- Static analysis should flag global buffer access paths and missing include guard if project policy requires guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_service.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_service.c

## Purpose

`afsd_service.c` is the Windows service executable entry point for the OpenAFS client. It registers with the Service Control Manager, sequences `afsd_init.c` startup and shutdown, handles stop/shutdown/power/custom dump controls, verifies module versions/signatures, manages global drive mappings, adjusts network provider order, loads optional hook DLL callbacks, and supports console-mode execution when not launched by SCM.

## Important APIs, Types, and Functions

- Service globals include `ServiceStatus`, `StatusHandle`, `bRunningAsService`, `hAFSDMainThread`, `WaitToTerminate`, `GlobalStatus`, `powerEventsRegistered`, `powerStateSuspended`, and `RDR_Initialized`.
- `afsd_notifier()` is registered through `osi_InitPanic()`. It logs service errors, forces AFSD and buffer traces, optionally captures a stack, dumps cache manager/SMB/RX state, generates a minidump, signals termination, and exits.
- `afsd_ServiceControlHandler()` is the legacy SCM handler for stop, shutdown, and interrogate.
- `afsd_ServiceControlHandlerEx()` handles stop/shutdown/interrogate, power suspend/resume events, and `SERVICE_CONTROL_CUSTOM_DUMP`.
- `MountGlobalDrivesThread()`, `MountGlobalDrives()`, and `DismountGlobalDrives()` implement registry-driven global drive mappings from `GlobalAutoMapper`.
- `GetVersionInfo()`, `LoadCrypt32()`, `UnloadCrypt32()`, `GetCertCtx()`, `VerifyTrust()`, `LogCertCtx()`, and `AFSModulesVerify()` verify executable and DLL version/signature consistency.
- `npi_CheckAndAddRemove()`, `InstNetProvider()`, and `clientServiceProviderKeyExists()` maintain Windows Network Provider order for `AFSRedirector` and `TransarcAFSDaemon`.
- `afsd_Main()` is the service main routine and the central lifecycle coordinator.
- `afsdMain_thread()` runs `afsd_Main()` for console mode.
- `main()` supports `--validate-cache <cache-path>`, SCM dispatch, and interactive fallback.

## Control Flow

`main()` first handles `--validate-cache` by calling `cm_ValidateMappedMemory()`. Otherwise it calls `StartServiceCtrlDispatcher()`. If not attached to SCM, it starts `afsd_Main()` on a thread and waits for Enter to signal `WaitToTerminate`.

`afsd_Main()` installs diagnostics, creates the termination event, registers the best available service control handler, reports `SERVICE_START_PENDING`, verifies loaded AFS modules, runs optional init hook callbacks, initializes volume status notifications, calls `afsd_InitCM()`, calls post-RX hooks, initializes the redirector, sets sysname lists for the redirector, updates network provider order, chooses SMB default based on redirector success, calls `afsd_InitSMB()`, requires at least one of RDR or SMB, runs post-SMB hooks, mounts global drives, starts daemons, reports `SERVICE_RUNNING`, runs started hooks, then blocks on `WaitToTerminate`.

Shutdown reverses visible integration surfaces: service status moves to stop pending, stopping hooks run, freelance shutdown runs if built, global drives dismount, redirector receives shutdown notification, SMB shuts down, locks/daemons/buffers/cache manager/RPC/mapped memory/RDR/RX are shut down, directory stats are dumped, volume status handlers are stopped/finalized, stopped hooks run, exception filtering is removed, and final SCM status is reported.

## State and Persistence Behavior

Persistent configuration comes from registry keys under `AFSREG_CLT_SVC_PARAM_SUBKEY`, `AFSREG_CLT_OPENAFS_SUBKEY`, `AFSREG_NP_ORDER`, and provider subkeys. The file mutates persistent Network Provider order and uses Windows network connection APIs to create and remove global drive mappings. It writes service events, initialization logs, trace files, minidumps, and module/signature audit messages. Runtime state is coordinated through `WaitToTerminate`, `GlobalStatus`, SCM service status fields, and redirector/SMB power-suspend flags.

## Dependencies and Integration Points

The file integrates with Windows SCM (`StartServiceCtrlDispatcher`, `RegisterServiceCtrlHandlerEx`, `SetServiceStatus`), power broadcasts, registry APIs, WNet drive mapping, WinTrust/Crypt32/PSAPI dynamic loading, OpenAFS cache manager/SMB/RDR/RX/RPC/volume status modules, hook DLL entry points from `cm_LoadAfsdHookLib()`, and `afsd_init.h`.

## Risks

- `AFSModulesVerify()` has several early returns after loading `psapi` or opening resources that can skip cleanup; failure paths are service-start blockers.
- `VerifyTrust()` uses `GetLastError()` after `WinVerifyTrust()` even though the returned status is the primary error value, so logs can misclassify trust failures.
- `GetCertCtx()` returns a certificate context while closing the source store; this relies on Windows certificate context lifetime behavior and must be paired with `pCertFreeCertificateContext()`.
- `MountGlobalDrives()` waits only 15 seconds, leaving a live mapping thread to be handled at shutdown if slow.
- Network provider order editing is string-based and assumes enough slack in the allocated buffer for insertions.
- Power transition handling changes SMB listeners, redirector state, and cache scache state from SCM callbacks, so race coverage with active IO is critical.

## Test Signals

- Service integration tests should verify SCM transitions for start, stop, shutdown, interrogate, custom dump, and console fallback.
- Power tests should cover suspend/resume event ordering with both SMB and RDR enabled, including repeated suspend/resume idempotence.
- Module verification tests should cover matching/mismatching versions, disabled signature verification, unsigned DLLs, and certificate mismatch.
- Registry tests should check provider order insertion/removal before `LanmanWorkstation` and fallback when provider keys are absent.
- GlobalAutoMapper tests should verify mapping retries, disconnect behavior, long submount values, and unavailable SMB listener behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsdacl.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsdacl.c

## Purpose

`afsdacl.c` is a small Windows command-line utility for inspecting or changing the service DACL on `TransarcAFSDaemon`. It can grant ordinary users start/stop/read-control access through the `Everyone` ACE while ensuring `AFS Client Admins` receives broad service rights, or revoke the `Everyone` ACE.

## Important APIs, Types, and Functions

- Constants define actions `SETDACL` and `RESETDACL`, service name `TransarcAFSDaemon`, group names `AFS Client Admins` and `Everyone`.
- `show_usage()` prints CLI syntax for `-set`, `-reset`, and `-show`.
- `show_last_error()` formats Windows errors through `FormatMessage()`.
- `set_dacl(int action)` opens the SCM and AFSD service, queries the current DACL, builds two `EXPLICIT_ACCESS` entries, merges them with `SetEntriesInAcl()`, and writes the new DACL with `SetServiceObjectSecurity()`.
- `show_dacl()` opens the service, reads the DACL, converts it to SDDL with `ConvertSecurityDescriptorToStringSecurityDescriptor()`, and prints it.
- `main()` parses mutually exclusive `-set`/`-reset` plus optional `-show`.

## Control Flow

The tool parses arguments, requires at least one action or show request, applies `set_dacl()` first if requested, then calls `show_dacl()` if requested. Both service operations use a two-step `QueryServiceObjectSecurity()` pattern: first call for required size, allocate a descriptor, second call to populate it, then process or display the DACL.

## State and Persistence Behavior

The only persistent change is the Windows service object's discretionary ACL. `-set` grants `Everyone` `SERVICE_START | SERVICE_STOP | READ_CONTROL`; `-reset` revokes that entry. Both modes set `AFS Client Admins` to `SPECIFIC_RIGHTS_ALL | STANDARD_RIGHTS_ALL`. No repository files are modified.

## Dependencies and Integration Points

The utility depends on Windows SCM, ACL APIs, SDDL conversion, heap/local allocation, and localized account/group names. It is operationally tied to the service name used by `afsd_service.c`.

## Risks

- `rv` is initialized to `1` in both `set_dacl()` and `show_dacl()` and is never set to success, so the program appears to exit with failure even when operations succeed.
- Localized Windows installations may not resolve literal `Everyone` or `AFS Client Admins` names as expected.
- The code logs errors but continues after some failures such as `SetEntriesInAcl()` or `SetSecurityDescriptorDacl()`, risking a later write with invalid or stale ACL data.
- `QueryServiceObjectSecurity()` has an `else : shouldn't happen` path where `psdesc` can remain NULL before `GetSecurityDescriptorDacl()`.
- Granting service start/stop to `Everyone` is intentionally broad and should be treated as a security-sensitive deployment choice.

## Test Signals

- CLI tests should assert usage failures, mutually exclusive `-set`/`-reset`, combined action plus `-show`, and correct process exit codes.
- ACL tests should verify exact ACE additions/removals using SDDL before and after each action.
- Negative tests should cover missing service, insufficient privileges, unresolved group names, and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsdacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsdicon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsdicon.h

## Purpose

`afsdicon.h` is a minimal resource/menu identifier header for the Windows AFSD icon or UI resources. It currently defines a help command identifier.

## Important APIs, Types, and Functions

- Include guard `OPENAFS_WINNT_AFSD_AFSDICON_H`.
- `IDM_HELP` is defined as `100`.

## Control Flow

There is no executable control flow. Resource scripts or UI code include this header to keep numeric command IDs consistent.

## State and Persistence Behavior

The header has no runtime state and no persistence behavior.

## Dependencies and Integration Points

It integrates with Windows resource compilation and any tray/icon/menu code that handles `IDM_HELP`.

## Risks

- Numeric resource IDs must remain unique across the resource set; this file alone does not show collisions.
- Removing or renumbering `IDM_HELP` can break resource scripts or command handlers.

## Test Signals

- Resource build tests should verify this header is included successfully and no duplicate resource ID warnings occur.
- UI smoke tests should verify the help command still maps to the intended handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsdicon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.cpp

## Purpose

`afsicf.cpp` configures Windows Firewall exceptions for OpenAFS client and server ports. It supports modern `INetFwPolicy2` rule-based configuration and falls back to older `INetFwProfile` globally-open-port APIs.

## Important APIs, Types, and Functions

- `global_afs_port_t` describes an AFS port rule: display name, numeric port, string port, and protocol.
- `afs_clientPorts` defaults to callback port 7001 UDP and optionally TCP.
- `afs_serverPorts` lists AFS server ports 7000 through 7009 for file, protection, VLDB, auth, volume, error, bos, update, and remote cache manager services, with optional TCP variants under `AFS_TCP`.
- `icf_CheckAndAddPorts2()` uses `INetFwPolicy2`, `INetFwRules`, and `INetFwRule` to add or update application-scoped allow rules grouped as `OpenAFS Firewall Rules`.
- `icf_OpenFirewallProfile()` opens the legacy current firewall profile through `INetFwMgr` and `INetFwPolicy`.
- `icf_CheckAndAddPorts()` uses legacy `INetFwOpenPorts` and `INetFwOpenPort` to enable or create globally open ports.
- `icf_CheckAndAddAFSPorts(int port)` is the exported C-callable entry point. `AFS_PORTSET_SERVER` selects server ports; other values configure the client callback port.
- A `TESTMAIN` block provides standalone manual testing.

## Control Flow

`icf_CheckAndAddAFSPorts()` chooses server or client port descriptors, initializes COM, tries `icf_CheckAndAddPorts2()`, and falls back to `icf_OpenFirewallProfile()` plus `icf_CheckAndAddPorts()` if the policy2 path fails. Return codes are coarse: `0` on accepted path, `1` invalid client port formatting, `2` legacy profile unavailable, and `3` legacy port creation failure.

For policy2, each port is looked up by rule name. Missing rules are created, associated with the current executable path, configured for protocol/local port/all profiles/allow/enabled/edge traversal/all interface types, and grouped. Existing rules have service name cleared, application, edge traversal, interface types, protocol, local ports, grouping, and action refreshed.

## State and Persistence Behavior

The persistent state is Windows Firewall configuration. The code creates or updates named allow rules or globally open ports. In non-test builds the application path comes from `GetModuleFileNameW(NULL, ...)`, tying rules to the installed executable. Client callback port state mutates the global `afs_clientPorts[0]` descriptor for the duration of the call.

## Dependencies and Integration Points

The file depends on Windows COM, `netfw.h`, BSTR allocation, `OutputDebugString`, and the public `afsicf.h` declaration. It is used by service/install code that needs firewall holes for the cache manager callback or server suite.

## Risks

- `icf_CheckAndAddPorts2()` unconditionally returns `0`, so failures from COM/rule operations are hidden and fallback is usually not triggered.
- `icf_CheckAndAddPorts2()` calls `CoUninitialize()` based on a local `hrComInit` that is never assigned from `CoInitializeEx()` in that function; COM lifetime is actually handled by the caller, so this can unbalance COM initialization.
- `pFwRule` is reused in a loop and only released once at cleanup, so existing per-port rule references can leak or be overwritten.
- `icf_CheckAndAddPorts()` releases `fwPorts` before `cleanup`, then may release it again because the pointer is not nulled.
- For client ports, `afs_clientPorts[0].str_port` is set to a stack buffer. It is safe only because the descriptor is consumed synchronously before return.
- Enabling edge traversal and all interface types broadens firewall exposure and should be validated against deployment expectations.

## Test Signals

- Tests should mock or integration-test both Policy2 and legacy firewall APIs, including forced Policy2 failure to prove fallback.
- Verify idempotence: running twice should update existing rules without duplicates.
- Validate non-default callback ports, server portset behavior, optional `AFS_TCP`, and returned error codes on COM/firewall failures.
- Static analysis should flag COM lifetime imbalance and double-release risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.h

## Purpose

`afsicf.h` exposes the Windows firewall configuration entry point for OpenAFS components and defines the selector for the server port set.

## Important APIs, Types, and Functions

- `long icf_CheckAndAddAFSPorts(int portset);` is declared with C linkage when included from C++.
- `AFS_PORTSET_SERVER` is defined as `0`, selecting the predefined AFS server ports in `afsicf.cpp`.

## Control Flow

There is no executable control flow. Callers pass `AFS_PORTSET_SERVER` to configure server rules, or a concrete callback port value to configure the client cache manager callback port.

## State and Persistence Behavior

The header itself has no state. Its exported function causes persistent Windows Firewall rule changes in the implementation.

## Dependencies and Integration Points

The `extern "C"` wrapper makes the C++ implementation callable from C code. It integrates service/install code with `afsicf.cpp`.

## Risks

- The parameter name `portset` can obscure the dual meaning: `0` is a selector, nonzero values are actual client callback ports.
- Only `AFS_PORTSET_SERVER` is named; there is no symbolic client selector, so callers must know to pass a port number.

## Test Signals

- C and C++ build tests should include this header and link against `afsicf.cpp`.
- API tests should cover `AFS_PORTSET_SERVER`, default client callback port 7001, and non-default callback ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afskfw-int.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afskfw-int.h

## Purpose

`afskfw-int.h` is an internal Windows Kerberos for Windows integration header. It centralizes includes, constants, dynamic service-control function pointer types, token/cache mapping structures, and prototypes for KFW/MSLSA/AFS token operations used by AFSD-adjacent authentication code.

## Important APIs, Types, and Functions

- Includes Windows, optional MS2MIT LSA security headers, Winsock/process/time headers, AFS standards, Kerberos 5, and RXKAD.
- Service dynamic-load typedefs include `FP_OpenSCManagerA`, `FP_OpenServiceA`, `FP_QueryServiceStatus`, and `FP_CloseServiceHandle`.
- Constants include `KRB5_DEFAULT_LIFE`, `LSA_CCTYPE`, `LSA_CCNAME`, `REALM_SZ`, and fallback `KTC_*` error codes.
- `struct textField` models prompted user input fields with buffer, length, label, default, and echo behavior.
- `struct principal_ccache_data` tracks principal-to-ccache records, whether imported from LSA, expiration, and renew behavior.
- `struct cell_principal_map` maps AFS cell names to principals with an active flag.
- Prototypes cover service status (`GetServiceStatus`), error reporting (`KFW_AFS_error`, `KFW_error`), cache operations (`KFW_get_ccache`, `KFW_import_ccache_data`), Kerberos lifecycle (`KFW_kinit`, `KFW_renew`, `KFW_destroy`), MSLSA import (`KFW_ms2mit`, `MSLSA_IsKerberosLogon`, `KFW_get_default_mslsa_import`), AFS token operations (`KFW_AFS_unlog`, `KFW_AFS_klog`), realm/lifetime/DES helpers (`afs_realm_of_cell`, `KFW_get_default_lifetime`, `KFW_enable_DES`).

## Control Flow

The header has no executable control flow, but it defines the operation set expected by authentication flows: discover service/login state, locate or acquire a Kerberos credential cache, optionally import MSLSA tickets, obtain or renew Kerberos credentials, convert them into AFS tokens, and destroy/unlog credentials as requested.

## State and Persistence Behavior

Structures describe linked-list process memory state for principal caches and cell mappings. Persistent state is external: Kerberos credential caches, MSLSA logon sessions, AFS tokens, service state, and registry/default configuration read by implementation files.

## Dependencies and Integration Points

This header is tightly coupled to MIT Kerberos (`krb5_context`, `krb5_principal`, `krb5_ccache`, `krb5_deltat`), AFS config/cell structures, RXKAD security, Windows service APIs, and optional MS2MIT LSA APIs. It bridges Windows logon credentials to AFS token acquisition.

## Risks

- It is an internal header with broad includes and many prototypes, so include-order or macro conflicts with Windows/Kerberos headers are likely.
- Fallback `KTC_*` definitions can diverge from canonical token error definitions if upstream values change.
- DES enablement support (`KFW_enable_DES`) is legacy-sensitive and should be constrained by modern security policy.
- Linked-list structures rely on implementation-owned allocation and lifetime discipline not visible in the header.

## Test Signals

- Build matrix tests should cover `USE_MS2MIT` on/off and supported `_WIN32_WINNT` values.
- Authentication integration tests should cover MSLSA import, explicit ccache selection, kinit/renew/destroy, AFS klog/unlog, expired credentials, and cell realm discovery.
- Security tests should verify default lifetime, DES behavior, and error translation for `KTC_*` and Kerberos failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afskfw-int.h -->
