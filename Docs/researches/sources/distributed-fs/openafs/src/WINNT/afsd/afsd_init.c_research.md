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
