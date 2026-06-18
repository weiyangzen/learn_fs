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
