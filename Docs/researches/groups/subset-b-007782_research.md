# subset-b-007782 Research

Grouped research for the listed OpenAFS `src/libadmin` utility, BOS, and configuration-admin files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.c

## Purpose
Implements shared libadmin utilities: error-code translation, database-server enumeration from CellServDB, hostname-to-address translation, the reusable background-prefetch iterator framework, cell-handle validation, RPC statistics wrappers, cache-manager callback introspection, and rxdebug query iterators. This is a support layer used by higher-level admin modules such as BOS, VOS, KAS, PTS, and configuration administration.

## Important APIs, Types, And Functions
Public functions include `util_AdminErrorCodeTranslate`, `util_DatabaseServerGetBegin/Next/Done`, `util_AdminServerAddressGetFromName`, `CellHandleIsValid`, `util_RPCStatsGetBegin/Next/Done`, `util_RPCStatsStateGet`, `util_RPCStatsStateEnable`, `util_RPCStatsStateDisable`, `util_RPCStatsClear`, `util_RPCStatsVersionGet`, `util_CMGetServerPrefsBegin/Next/Done`, `util_CMListCellsBegin/Next/Done`, `util_CMLocalCell`, `util_CMClientConfig`, and the `util_RXDebug*` family. Internal iterator entry points `IteratorInit`, `IteratorNext`, and `IteratorDone` are defined here but declared in `afs_AdminInternal.h`.

Important local state structures are `database_server_get_t`, `rpc_stat_get_t`, `cm_srvr_pref_get_t`, `cm_list_cell_get_t`, `rxdebug_conn_get_t`, and `rxdebug_peer_get_t`; each embeds a `CACHED_ITEMS` array used by the generic iterator. `init_once` initializes many OpenAFS com_err tables and is guarded by `pthread_once_t error_init_once`.

## Control Flow
Error translation lazily initializes error tables, casts the admin status to `afs_int32`, calls `afs_error_message`, and optionally falls back to Kerberos error text when enabled. Database-server enumeration opens `AFSDIR_CLIENT_ETC_DIRPATH`, copies the requested cell name because `afsconf_GetCellInfo` mutates it, loads database host metadata, and feeds one host at a time through the generic iterator.

The iterator framework creates a joinable producer thread when `make_rpc` is non-NULL. `DataGet` waits for an empty cache slot, calls the file-specific RPC/data producer without holding the iterator mutex, stores data in a ring buffer, signals waiting consumers, and marks `ADMITERATORDONE` when the producer reports end-of-stream. `IteratorNext` locks the iterator, validates magic and validity flags, waits for cached data, copies one item using the caller-supplied cache copier, and signals the producer when space opens. `IteratorDone` sets `request_terminated`, wakes the producer if needed, joins the worker, then destroys mutexes/condition variables and frees the iterator-specific data.

RPC stats retrieval performs one bulk RPC into `struct rpcStats`, then iterates through the returned integer vector with `UnmarshallRPCStats`. Cache-manager functions call `RXAFSCB_GetServerPrefs`, `RXAFSCB_GetCellServDB`, `RXAFSCB_GetLocalCell`, and `RXAFSCB_GetCacheConfig`, translating XDR strings/vectors into fixed public structures. Rxdebug functions first discover supported server statistics, then query version/basic/rx stats or iterate connections and peers through UDP rxdebug helper routines.

## State And Persistence
Most state is transient heap memory owned by iterators. Persistent inputs are AFS client configuration files under `AFSDIR_CLIENT_ETC_DIRPATH`, especially CellServDB and local cell metadata. The file does not write persistent configuration, but it observes remote cache-manager and rxdebug state and can enable, disable, or clear RPC statistic counters on remote processes via caller-supplied RPC hooks. `CellHandleIsValid` validates opaque libadmin handles using `BEGIN_MAGIC`, `END_MAGIC`, and `is_valid`.

## Dependencies And Integration Points
The file depends on pthreads, Rx/RxStat, XDR freeing, OpenAFS cell configuration, com_err tables, `afscbint` cache-manager callback RPCs, `rxdebug` helpers, and internal handle/iterator definitions from `afs_AdminInternal.h`. Its generic iterator is reused by BOS and other libadmin modules. Database-server enumeration is used by configuration code to discover CellServDB hosts.

## Risks And Test Signals
Important risks include thread lifecycle bugs in the generic iterator, failures during `pthread_attr_init` after mutex/condition initialization, inconsistent cleanup when `IteratorInit` starts a worker but later fails, and fixed-size destination assumptions for names and cell arrays. `util_AdminServerAddressGetFromName` parses dotted quads with `sscanf` but does not validate octet range; it also serializes `gethostbyname` behind a global mutex because that API is not generally thread-safe. RPC stat unmarshalling assumes the returned vector matches version-1 layout. Test signals should include iterator begin/next/done success and early-done paths, producer error propagation, CellServDB enumeration, hostname parsing/resolution, com_err translation, cache-manager CellServDB and server preference enumeration, rxdebug timeout handling, and memory cleanup under valgrind/asan-like instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.h

## Purpose
Declares the public utility-admin API for libadmin. It exposes error translation, CellServDB database-server iteration, server-name address resolution, cell-handle validation, generic RPC stats controls, cache-manager callback inspection helpers, and rxdebug helper wrappers.

## Important APIs, Types, And Functions
Constants define fixed public buffer sizes: `UTIL_MAX_DATABASE_SERVER_NAME`, `UTIL_MAX_CELL_NAME_LEN`, `UTIL_MAX_CELL_HOSTS`, and `UTIL_MAX_RXDEBUG_VERSION_LEN`. Public data structures include `util_databaseServerEntry_t`, `afs_CMServerPref_t`, `afs_CMListCell_t`, `afs_CMCellName_t`, and `rxdebugVersion_t`. Function prototypes mirror the implementation in `afs_utilAdmin.c` and use the `ADMINAPI` calling convention plus `afs_status_p` error reporting.

The RPC stats prototypes are intentionally generic: callers provide a `struct rx_connection *` and function pointer matching each server's stats RPC, while the utility layer normalizes results into `afs_RPCStats_t`, `afs_RPCStatsState_t`, `afs_RPCStatsClearFlag_t`, and `afs_RPCStatsVersion_t` from `afs_Admin.h`.

## Control Flow
The header defines begin/next/done iterator flows for database servers, RPC stats, cache-manager server preferences, cache-manager cells, rxdebug connections, and rxdebug peers. Single-call helpers retrieve local cell name, cache-manager config, rxdebug version/basic stats/rx stats, RPC stats state, and stats version.

## State And Persistence
No state is stored in the header. It defines caller-visible fixed-size structures used to receive snapshots of configuration, RPC statistics, cache-manager callback state, and rxdebug state. Callers must treat iterator IDs as opaque and terminate them through the matching `Done` functions.

## Dependencies And Integration Points
The header includes `afs_Admin.h` and `afs_AdminErrors.h` and forward-declares `struct rpcStats`. It depends on Rx connection types and rxdebug handle types defined by `afs_Admin.h`. Higher-level admin libraries include it for common validation, enumeration, stats, and cache-manager inspection.

## Risks And Test Signals
The main risks are ABI drift in fixed-size buffers and function-pointer signatures, especially for RPC stats retrieval. Since buffers are caller-provided, tests should compile consumers that allocate the documented sizes and exercise all begin/next/done APIs against empty, one-item, and multi-item data sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/afs_Admin.h -->
# sources/distributed-fs/openafs/src/libadmin/afs_Admin.h

## Purpose
Defines common public libadmin types shared by the OpenAFS administrative libraries. It provides platform-specific export/calling-convention macros, the common `afs_status_t` status type, RPC statistics result structures, cache-manager configuration result structures, and the portable `rxdebugHandle_t`.

## Important APIs, Types, And Functions
`ADMINAPI` is `__cdecl` on Windows and empty on Unix; `ADMINEXPORT` defaults to `__declspec(dllimport)` on Windows and empty elsewhere. `afs_status_t` is an unsigned integer status code. `afs_RPCStatsState_t`, `afs_RPCStatsVersion_t`, `afs_RPCStatsClearFlag_t`, `afs_RPCUnion_t`, and `afs_RPCStats_t` define the public RPC statistics model. `afs_ClientConfigUnion_t` and `afs_ClientConfig_t` define cache-manager configuration retrieval results. `rxdebugHandle_t` stores socket, address, port, first-query flag, and supported-statistics mask; its socket type differs between Windows and Unix.

## Control Flow
The file contains no executable control flow. It establishes the type contract used by utility, BOS, VOS, KAS, PTS, client, and configuration admin APIs.

## State And Persistence
No runtime or persistent state exists here. The structures are snapshots or handles owned by callers and populated by implementation files such as `afs_utilAdmin.c`.

## Dependencies And Integration Points
The header includes `afs/param.h`, `afs/afs_args.h`, and `rx/rx.h`. It couples libadmin public structures to Rx definitions such as `rx_function_entry_v1_t`, `cm_initparams_v1`, and Windows `SOCKET` when building on NT. All public libadmin headers include or depend on this file for consistent status and calling-convention behavior.

## Risks And Test Signals
Any change here is ABI-sensitive because it changes public structure layout or exported function decoration. Useful signals are full libadmin rebuilds on Unix and Windows, compile tests for DLL import/export mode, and binary compatibility checks for public structures consumed by external admin tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/afs_Admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/bos/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/bos/Makefile.in

## Purpose
Builds and installs the BOS admin static library and public header. It compiles the local BOS admin wrapper plus generated bozo RPC client/XDR objects, archives them into `libbosadmin.a`, and installs the library and `afs_bosAdmin.h` into the configured include/lib trees.

## Important APIs, Types, And Functions
Important variables are `BOZO=../../bozo`, `ADMINOBJS=afs_bosAdmin.o`, `BOZOOBJS=bosint.xdr.o bosint.cs.o`, and `LIBOBJS=${ADMINOBJS} ${BOZOOBJS}`. Targets include `all`, header/library staging into `${TOP_INCDIR}` and `${TOP_LIBDIR}`, `install`, `dest`, `libbosadmin.a`, generated-RPC object builds from `${BOZO}/bosint.xdr.c` and `${BOZO}/bosint.cs.c`, and `clean`.

## Control Flow
`all` first ensures the public header is installed in the top include directory and then builds/stages `libbosadmin.a`. The archive target removes any old archive, runs `$(AR) $(ARFLAGS)`, then `$(RANLIB)`. The generated bozo RPC source files are compiled with `$(AFS_CCRULE)`. `install` and `dest` create destination include/lib directories and copy the source header plus archive.

## State And Persistence
The makefile creates object files and `libbosadmin.a` in the build tree and installs copies under `${TOP_INCDIR}`, `${TOP_LIBDIR}`, `${DESTDIR}${includedir}/afs`, `${DESTDIR}${libdir}/afs`, or `${DEST}` depending on target. `clean` removes local objects and `libbosadmin*`.

## Dependencies And Integration Points
It includes OpenAFS build configuration and pthread make fragments. It integrates the libadmin BOS wrapper with generated bozo RPC stubs from `src/bozo`, making the BOS admin library depend on the bozo RPC contract.

## Risks And Test Signals
Risks are ordinary build-system drift: missing regenerated `bosint` sources, stale header installation, and archive contents diverging from implementation. Test signals are `make` in this directory, install/dest dry-runs, and verifying `libbosadmin.a` contains `afs_bosAdmin.o`, `bosint.xdr.o`, and `bosint.cs.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/bos/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.c

## Purpose
Implements the public BOS admin API declared in `afs_bosAdmin.h`. It opens authenticated Rx connections to a BOS server, validates BOS handles, wraps bozo RPCs for process/admin/key/cell/host/executable/log/auth/command operations, uses the shared libadmin iterator framework for BOS enumerations, and orchestrates remote salvage operations.

## Important APIs, Types, And Functions
`bos_server_t` is the private handle with magic fields and three Rx connections: normal BOS service, encrypted BOS service, and stats service. Public lifecycle functions are `bos_ServerOpen` and `bos_ServerClose`; validation is done by `isValidServerHandle` and the local `IsValidCellHandle`. Major API groups include process creation/deletion/state/info/parameters/notifier/restart/all-stop/all-start, admin create/delete/list, key create/delete/list, cell get/set, host create/delete/list, executable install/revert/timestamps/prune/restart-time get/set, log retrieval, noauth setting, remote command execution, and `bos_Salvage`.

Iterators use local structs such as `process_name_get_t`, `param_get_t`, `admin_get_t`, `key_get_t`, and `host_get_t`, each plugged into `IteratorInit`. Secret-key operations use `server_encrypt` and the `kas_to_bozoptr` adapter from the header.

## Control Flow
`bos_ServerOpen` validates that the cell handle has tokens, resolves `serverName` through `util_AdminServerAddressGetFromName`, and creates cached Rx connections to `AFSCONF_NANNYPORT`. Most simple wrappers validate the handle and arguments, call one `BOZO_*` RPC, and return `1` only when the RPC status is zero. Process and host/admin/key enumeration functions allocate iterator-specific state, call a `BOZO_*` enumerate/list RPC by increasing index, translate `BZDOM` or similar end conditions into `ADMITERATORDONE`, and copy cached results into caller buffers.

Executable installation uses a split Rx RPC: it opens a local file, stats it, starts `BOZO_Install`, streams the file in 512-byte chunks with `rx_Write`, and ends the call. Log retrieval starts `BOZO_GetLog`, reads one byte at a time until a NUL terminator, stores up to the caller's buffer size, and reports `ADMMOREDATA` when the caller buffer is too small. Restart-time functions map libadmin restart enums to bozo restart types and `bozo_netKTime`.

`bos_Salvage` validates cell and BOS handles, optionally resolves partition names, opens a local salvage-log output file, temporarily stops the `fs` bnode for non-volume-specific salvages, constructs a salvager command line, creates a temporary cron bnode named `salvage-tmp` with time `now`, polls until the bnode disappears, optionally retrieves the server SalvageLog, and restarts the fileserver if it had been stopped.

## State And Persistence
The private BOS handle owns cached Rx connections and validity markers. Remote persistent state affected by this file includes BosConfig bnodes, process goals, `UserList`, `KeyFile`, server `ThisCell`/CellServDB host list, executable files and `.BAK`/`.OLD` rotations, restart schedules, noauth flag, command execution effects, and salvage results. Local persistent side effects include reading source executable files and writing optional salvage logs. Iterators keep transient heap caches and background worker threads through the shared iterator framework.

## Dependencies And Integration Points
The file depends on Rx, RxStat, bozo RPC stubs from `bosint`, bnode constants, `ktime`, directory-path constants, `afs_utilAdmin`, `afs_AdminInternal`, KAS key types, and VOS partition conversion for salvage. It is used by configuration code in `cfgdb.c` and `cfghost.c` to update CellServDB, UserList, KeyFile, BOS process state, and salvage operations.

## Risks And Test Signals
Several cleanup and correctness risks are visible. `bos_ServerClose` releases only `server`, not `server_encrypt` or `server_stats`, so opened handles can leak cached connections. `bos_ExecutableCreate` does not close the opened local file descriptor on success or failure. `bos_LogGet` can overwrite an earlier `ADMMOREDATA` or read error with the status from `rx_EndCall`, hiding the real reason for failure. `bos_Salvage` builds a command with repeated `sprintf` into a fixed `BOS_MAX_NAME_LEN` buffer and checks length after writes, so long options can overflow before detection. Iterator copies use `strcpy` into caller buffers that are assumed to be `BOS_MAX_NAME_LEN`.

Test signals should cover BOS open/close connection accounting, process create/delete/state transitions, all iterator end conditions, encrypted key create/list/delete, executable upload and revert against a test bosserver, log retrieval with exact/small/large buffers, noauth toggling, restart-time validation, and salvage command construction with long partition/volume/tmp paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.h

## Purpose
Declares the public BOS administration API and BOS-facing types used by libadmin clients. It describes process types/states, authentication/prune/restart/salvage options, process/key/restart-time result structures, and all exported BOS operations.

## Important APIs, Types, And Functions
Constants include `BOS_MAX_NAME_LEN`, `BOS_MAX_PROCESS_PARAMETERS`, and `BOS_ENCRYPTION_KEY_LEN`. Public enums model process type (`simple`, `fs`, `cron`), execution state, error state flags, noauth policy, prune flags, restart schedule type, restart-BOS choice, and salvage flags. Important structures are `bos_ProcessInfo_t`, `bos_encryptionKeyStatus_t`, `bos_KeyInfo_t`, and `bos_RestartTime_t`.

The function surface includes server open/close, process lifecycle and enumeration, admin list mutation/enumeration, key mutation/enumeration, cell/host list mutation/enumeration, executable upload/revert/timestamp/prune/restart schedule, log retrieval, auth policy, command execution, and `bos_Salvage`. `kas_to_bozoptr` casts a KAS encryption key to the bozo key structure expected by generated RPC stubs.

## Control Flow
The header establishes common begin/next/done patterns for process names, parameters, admins, keys, and hosts. Most other functions are synchronous one-shot operations against a BOS server handle.

## State And Persistence
The header stores no state itself. Its API represents persistent BOS server state: BosConfig process definitions, process goals, administrator list, KeyFile keys, CellServDB host list, server cell name, executable revisions, logs, restart schedules, and noauth mode.

## Dependencies And Integration Points
It includes `afs_Admin.h`, `afs_vosAdmin.h`, and `afs_kasAdmin.h`, tying BOS salvage options to VOS force flags and BOS key APIs to KAS encryption key types. It must remain layout-compatible with the bozo RPC implementation because enums and structures are cast or mapped directly in `afs_bosAdmin.c`.

## Risks And Test Signals
The comment notes that `bos_ProcessExecutionState_t` values must match bozo `BSTAT_*` values; enum drift would silently corrupt state mapping. Public fixed-size buffer assumptions require consumer compile/runtime tests. ABI tests should cover structure sizes, enum values, and all exported prototypes on Windows and Unix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/cfg/Makefile.in

## Purpose
Builds and installs the configuration-admin static library and public header. The library combines local configuration modules with generated Ubik RPC client/XDR support.

## Important APIs, Types, And Functions
`UBIKOBJS` contains `ubik_int.cs.o` and `ubik_int.xdr.o`. `CFGOBJS` contains `cfgclient.o`, `cfgdb.o`, `cfghost.o`, `cfgservers.o`, and `cfginternal.o`. `LIBOBJS` archives both groups into `libcfgadmin.a`. Targets stage/install `afs_cfgAdmin.h` and `libcfgadmin.a`, build generated Ubik objects from `../../ubik`, and clean local build outputs.

## Control Flow
`all` installs the header into `${TOP_INCDIR}/afs` and the archive into `${TOP_LIBDIR}`. `libcfgadmin.a` removes any old archive, archives all objects, and runs `ranlib`. All configuration objects depend on `afs_cfgAdmin.h`, while Ubik generated objects are compiled through `$(AFS_CCRULE)`.

## State And Persistence
The makefile writes object files and `libcfgadmin.a` in the build tree and installs copies into top-level or destination include/lib directories. `clean` removes objects and `libcfgadmin*`.

## Dependencies And Integration Points
It includes the OpenAFS standard and pthread build fragments. It integrates configuration APIs with Ubik RPC stubs and with sibling implementation files that call BOS, client, KAS, PTS, and utility-admin libraries.

## Risks And Test Signals
Risks are stale object dependencies and missing generated Ubik sources. Useful signals are directory-level builds, archive-content inspection, and install/dest target checks that confirm `afs_cfgAdmin.h` and `libcfgadmin.a` land under the expected `afs` subdirectories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/afs_cfgAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/cfg/afs_cfgAdmin.h

## Purpose
Declares the public server/client configuration API for libadmin. The header organizes operations for host configuration, client configuration, server CellServDB updates, BOS server control, database/file/update server setup, update clients, and deallocation utilities.

## Important APIs, Types, And Functions
Public data types include `cfg_partitionEntry_t`, `cfg_cellServDbStatus_t`, callback type `cfg_cellServDbUpdateCallBack_t`, and `cfg_dbServersStatus_t`. Exported string constants name standard BOS instances such as `cfg_kaserverBosName`, `cfg_ptserverBosName`, `cfg_vlserverBosName`, `cfg_buserverBosName`, `cfg_fileserverBosName`, `cfg_upserverBosName`, and update-client suffix/prefix constants.

Function groups include `cfg_Host*` for static server config and partition table operations; `cfg_Client*` for cache-manager/client CellServDB operations; `cfg_CellServDb*` for cell-wide server CellServDB updates; `cfg_BosServer*`; database server start/stop/status/quorum helpers; file server start/stop/status; update server/client start/stop/status; convenience `cfg_SysBinServerStart`, `cfg_SysControlClientStart`, and `cfg_BinDistClientStart`; and deallocators for returned strings, partition lists, and CellServDB callback status records.

## Control Flow
The header documents the intended sequence: set static server configuration through `cfg_Host*`, set static client configuration through `cfg_Client*`, then dynamically configure server processes by category. It also documents an idempotence goal for implemented functions.

## State And Persistence
No state is stored in the header. Its API mutates persistent host and cell configuration: ThisCell, CellServDB, KeyFile, UserList, BosConfig, service state, partition tables, server process definitions, and client registry/configuration depending on platform.

## Dependencies And Integration Points
It includes `afs_Admin.h` and relies on opaque host/cell handles created by other libadmin modules. Implementations integrate with BOS, KAS, PTS, VOS, Windows service/registry helpers, CellServDB parsers, and local filesystem configuration paths.

## Risks And Test Signals
Risks are API/implementation drift and platform support assumptions: many implementation paths are local-only and return `ADMCFGNOTSUPPORTED` on Unix or remote hosts. Tests should verify function availability, callback ownership rules, deallocator behavior, and idempotence for repeated configuration calls where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/afs_cfgAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfgclient.c -->
# sources/distributed-fs/openafs/src/libadmin/cfg/cfgclient.c

## Purpose
Implements the `cfg_Client*` portion of the configuration API. It queries local client/cache-manager installation and static configuration, sets the default client cell, edits the local client CellServDB, and starts/stops the cache manager service where supported.

## Important APIs, Types, And Functions
Exported functions are `cfg_ClientQueryStatus`, `cfg_ClientSetCell`, `cfg_ClientCellServDbAdd`, `cfg_ClientCellServDbRemove`, `cfg_ClientStop`, and `cfg_ClientStart`. Local helpers are `ClientCellServDbUpdate`, `CacheManagerStart`, and `CacheManagerStop`. Windows-only code uses `cfgutil_WindowsServiceQuery/Start/Stop`, `afssw_GetClientVersion`, `afssw_SetClientCellName`, and CellServDB parser/writer routines such as `CSDB_ReadFile`, `CSDB_FindCell`, `CSDB_AddCell`, `CSDB_AddCellServer`, `CSDB_RemoveLine`, and `CSDB_WriteFile`.

## Control Flow
`cfg_ClientQueryStatus` validates parameters, requires the target host to be local, checks whether the Windows AFS client service is installed, obtains version information from registry-backed software helpers, then opens client configuration through `afsconf_Open`. It verifies a local cell name, matching CellServDB entry, and at least one database server, returning an allocated cell name only when static configuration is valid.

`cfg_ClientSetCell` validates a local host handle, cell name, and multistring database host list. On Windows, it reads the client CellServDB, creates or replaces the cell entry, resolves each database host to an address string, writes the file, sets the default client cell in the registry, and calls `ka_CellConfig` so underlying packages observe the cell change. `cfg_ClientCellServDbAdd/Remove` call `ClientCellServDbUpdate`, which resolves the database host to a full name, finds matching server lines by address, adds or removes the server entry, and writes the CellServDB. `cfg_ClientStart/Stop` validate the host and delegate to Windows service helpers with a timeout.

## State And Persistence
Persistent state includes the client CellServDB file at `AFSDIR_CLIENT_CELLSERVDB_FILEPATH`, client configuration under `AFSDIR_CLIENT_ETC_DIRPATH`, and Windows registry/service state for the AFS cache manager and default client cell. Returned cell names are heap-allocated and must be released through `cfg_StringDeallocate`. On non-Windows builds most operations return `ADMCFGNOTSUPPORTED`.

## Dependencies And Integration Points
The file depends on OpenAFS cell configuration, KAuth cell configuration refresh, Windows registry/software helpers, CellServDB parsing code, `cfginternal` host utilities, and service-control wrappers. It is typically used during server setup to ensure the local client knows the cell being configured.

## Risks And Test Signals
Risks include local-only behavior despite remote-looking API parameters, Windows-only implementation paths, concurrent edits to CellServDB without explicit locking here, fixed maximum host/cell counts, and multi-string parsing assumptions. Tests should cover valid/invalid local host detection, missing/malformed client config, installed and uninstalled Windows service states, CellServDB add/remove idempotence, duplicate host aliases by address, registry write failures, and start/stop timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfgclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfgdb.c -->
# sources/distributed-fs/openafs/src/libadmin/cfg/cfgdb.c

## Purpose
Implements the `cfg_CellServDb*` API for managing cell-wide server CellServDB membership. It can enumerate database hosts from a server's BOS CellServDB and can add/remove the host being configured across database/file servers using parallel detached worker threads.

## Important APIs, Types, And Functions
Exported functions are `cfg_CellServDbAddHost`, `cfg_CellServDbRemoveHost`, `cfg_CellServDbEnumerate`, and `cfg_CellServDbStatusDeallocate`. Local structures include `cfg_server_iteration_t`, `cfg_csdb_update_ctrl_t`, `cfg_csdb_update_name_t`, and `cfg_csdb_nameblock_iteration_t`. Key helpers are `CellServDbUpdate`, `StartUpdateWorkerThread`, `UpdateWorkerThread`, `CfgHostGetCellServDbAlias`, `NameBlockGetBegin/Next/Done`, and `ServerNameGetBegin/Next/Done`.

## Control Flow
`cfg_CellServDbEnumerate` opens a null cell handle, opens the specified BOS server, iterates its host list with `bos_HostGetBegin/Next/Done`, retrieves the BOS cell name, closes handles, and returns a heap-allocated multistring of database hosts plus a heap-allocated cell name.

`CellServDbUpdate` validates the host handle, callback, optional system-control host, and max-update output. It resolves the system-control host when present, allocates a shared control block, computes the configured host alias as it appears in existing server CellServDB entries, builds server-name blocks of up to `SERVER_NAME_BLOCK_SIZE`, starts one detached worker per block, then atomically releases all workers by changing the disposition from `CSDB_WAIT` to `CSDB_GO` or `CSDB_ABORT` and broadcasting a condition variable. Name enumeration uses database servers only when a system-control host is provided; otherwise it enumerates all AFS servers, then ensures the configuration host and optional system-control host are included.

Each `UpdateWorkerThread` waits for the shared disposition, opens each target BOS server, calls `bos_HostCreate` or `bos_HostDelete` with the alias from the control block, invokes the user callback with an allocated `cfg_cellServDbStatus_t`, and lets the last worker invoke the termination callback with `statusItemP == NULL`.

## State And Persistence
Persistent state modified by workers is the server CellServDB host list on each targeted BOS server. The operation is designed to appear atomic from the worker-start perspective: workers are created first and then released together. The user callback receives heap records that must be deallocated with `cfg_CellServDbStatusDeallocate`. The shared control block and name blocks are transient heap state used by detached threads.

## Dependencies And Integration Points
The file depends on pthreads, BOS admin APIs, client admin APIs for server enumeration, utility database-server enumeration, host utility functions from `cfginternal`, and OpenAFS bnode/cellconfig definitions. It is part of higher-level server setup where adding a new database server must propagate to existing server CellServDB files.

## Risks And Test Signals
The largest risk is threading cleanup: the last worker frees the shared control block before unlocking its mutex, producing a potential use-after-free. Mutexes and condition variables are also not destroyed. Detached workers mean the initiating function returns before updates complete, so callers must rely on callbacks and must not reenter the configuration library except for deallocation as documented. Other risks include callback allocation loops that sleep until memory is available, assuming all server CellServDB aliases are identical, duplicate target names, and treating `BZNOENT` as success for removals.

Test signals should cover zero/one/many target servers, callback ordering including final `NULL` callback, add/remove idempotence, system-control-host and no-system-control paths, alias discovery failures, worker abort after setup error, and thread sanitizer or asan coverage around last-worker cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfghost.c -->
# sources/distributed-fs/openafs/src/libadmin/cfg/cfghost.c

## Purpose
Implements the `cfg_Host*` portion of the configuration API for static server host configuration. It queries server configuration validity, opens/closes host configuration handles, writes server cell membership, provisions AFS and administrator principals into KeyFile/UserList, invalidates local server state, and manages the Windows vice partition table.

## Important APIs, Types, And Functions
Exported functions are `cfg_HostQueryStatus`, `cfg_HostOpen`, `cfg_HostClose`, `cfg_HostSetCell`, `cfg_HostSetAfsPrincipal`, `cfg_HostSetAdminPrincipal`, `cfg_HostInvalidate`, `cfg_HostPartitionTableEnumerate`, `cfg_HostPartitionTableAddEntry`, `cfg_HostPartitionTableRemoveEntry`, `cfg_HostPartitionNameValid`, `cfg_HostDeviceNameValid`, `cfg_StringDeallocate`, and `cfg_PartitionListDeallocate`. Local helpers are `KasKeyIsZero` and `KasKeyEmbeddedInString`.

The file uses the private `cfg_host_t` from `cfginternal.h`, cell handles validated through `CellHandleIsValid`, BOS APIs, KAS principal/key APIs, PTS user/group APIs, and Windows `vptab` functions.

## Control Flow
`cfg_HostQueryStatus` validates that the host is local, checks readability of required server files (`ThisCell`, `CellServDB`, `KeyFile`, `UserList`), opens the server config directory, validates local cell, keys, CellServDB entry, and database-server count, then returns an allocated cell name when valid. `cfg_HostOpen` validates the cell handle, resolves a full local host name, rejects remote hosts, allocates a host handle with magic values, stores the cell handle, obtains the cell name, and initializes a mutex. `cfg_HostClose` invalidates the handle, closes any cached BOS handle, destroys the mutex, and frees strings and handle memory.

`cfg_HostSetCell` builds an `afsconf_cell` from a multistring of database hosts, creates server configuration directories if needed, and writes server `ThisCell`/`CellServDB` through `afsconf_SetCellInfo`. `cfg_HostSetAfsPrincipal` creates or verifies the `afs` KAS principal, derives or fetches the most recent key, supports direct octal-embedded key strings, then opens a noauth BOS connection and writes the key to the host KeyFile. `cfg_HostSetAdminPrincipal` optionally creates the admin KAS principal, sets admin attributes, creates a PTS user, adds it to `system:administrators`, and adds the principal to the host BOS UserList. `cfg_HostInvalidate` requires the Windows BOS control service to be stopped, cleans server config/db/local directories, and removes vice partition table entries.

Partition table functions enumerate, add/update, remove, and validate Windows vice partition table entries. The enumeration result is one allocation containing an array of `cfg_partitionEntry_t` followed by copied `struct vptab` data; returned string pointers point inside that allocation.

## State And Persistence
Persistent state includes local server configuration files under `AFSDIR_SERVER_ETC_DIRPATH`, server database/local directories, KeyFile, UserList, KAS database principals and keys, PTS users/groups, BOS UserList entries, and Windows vice partition table state. The host handle retains the working host name, cell name, local flag, cell handle, optional BOS handle, and mutex. Returned strings and partition tables are caller-owned and freed through the exported deallocators.

## Dependencies And Integration Points
This file integrates OpenAFS local filesystem configuration (`afsconf` and `dirpath`), BOS admin, client admin, KAS admin, PTS admin, Windows registry/service/vice-partition helpers, and shared configuration utilities. Higher-level setup code depends on it before starting database/file/update server processes.

## Risks And Test Signals
Risks include local-only behavior hidden behind general host-name parameters, broad Windows-only implementation for invalidation and partition tables, no remote fallback, fixed-size string copying from multistring entries into `afsconf_cell.hostName`, and partial provisioning across KAS/PTS/BOS when later steps fail. `cfg_HostSetAfsPrincipal` relies on old KAS behavior and key checksums, and embedded-octal key parsing accepts exactly 24 octal digits. Test signals should cover missing/unreadable config files, no-key and no-CellServDB states, first-server and additional-server principal setup, invalid password/key paths, idempotent admin/UserList creation, BOS-stopped requirement for invalidation, partition table enumeration memory ownership, and Unix `ADMCFGNOTSUPPORTED` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfghost.c -->
