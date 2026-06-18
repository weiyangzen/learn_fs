# Research: subset-b-007769

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/server.c -->
# sources/distributed-fs/openafs/src/budb/server.c

## Purpose
`server.c` is the executable bootstrap for the OpenAFS Backup Database server (`buserver`). It turns command-line and cell configuration into an Rx/Ubik replicated database service for `BUDB_SERVICE`, opens auditing/logging, initializes the on-disk backup database prefix, starts the service threads, and then donates the main LWP to Rx request handling.

## Important APIs, Types, And Functions
The file exports process-wide state used by other BUDB modules: `BU_dbase`, `BU_conf`, `globalConfPtr`, `lcell`, `myHost`, `rxBind`, `lwps`, and the `dbDir`/`cellConfDir` backing buffers. `initializeArgHandler()` registers the daemon syntax and options. `argHandler()` populates `globalConfPtr`, enforces `-p` bounds (`MINLWP` to `MAXLWP`), configures audit logging, and preserves legacy handling for hidden `-resetdb`. `parseServerList()` converts a command parser list into the `ubik_ParseServerList()` argument vector. `convert_cell_to_ubik()` derives this host address and peer server list from `afsconf_cell`. `BU_rxstat_userok()` and `BU_IsLocalRealmMatch()` integrate Rx statistics and audit user checks with `afsconf`. `main()` orchestrates all process setup. `LogDebug()`, `Log()`, and `LogError()` wrap `FSLog`/`WriteLogBuffer`.

## Control Flow
Startup initializes platform-specific state, directory paths, BUDB error tables, command parsing, defaults, and audit. After `cmd_Dispatch()`, help exits before daemon work begins. The server opens the cell config directory, reads the local cell, and either uses an explicit `-servers` list or discovers Ubik peers from CellServDB via `afsconf_GetExtendedCellInfo()` and `convert_cell_to_ubik()`. It then sets Ubik security callbacks, computes the database name prefix, optionally binds Rx to the primary restricted/netinfo address, calls `rx_InitHost()`, disables jumbograms, initializes Ubik with either cellinfo or an explicit server list, builds server security classes, registers the Rx service with `BUDB_ExecuteRequest`, initializes dump synchronization, starts Rx, runs `InitProcs()`, logs readiness, and enters `rx_ServerProc(NULL)`.

## State And Persistence
The persistent state is the Ubik replicated BUDB database under `globalConfPtr->databaseDirectory` with prefix `DEFAULT_DBPREFIX` unless overridden by `-database`. Cell configuration is read from `globalConfPtr->cellConfigdir`. Global process state includes the active `afsconf_dir`, Ubik database handle, logging options, dump synchronization lock, server list, worker-thread count, and authentication/debug flags. The file does not manipulate database contents directly; it initializes the storage and serving layer used by database procedure modules.

## Dependencies And Integration Points
This file sits at the boundary between platform runtime, OpenAFS command parsing, `afsconf`, audit, Rx, RxKAD, and Ubik. The service callback comes from generated/linked BUDB RPC code as `BUDB_ExecuteRequest`. It relies on `globals.h`, `database.h`, `budb_internal.h`, `error_macros.h`, and external procedures such as `InitProcs()`. Audit integration uses `osi_audit_*`, and logging uses OpenAFS server log utilities.

## Risks And Test Signals
Risks cluster around daemon bootstrap: bad CellServDB contents, hostname resolution failure, incorrect bind address selection, incompatible Ubik peer lists, or unavailable security classes prevent startup. Several fields are process globals, so tests should exercise repeated initialization only in a fresh process. `parseServerList()` builds a temporary argument vector that intentionally aliases parser item strings; lifetime is safe for the call but not beyond it. Test signals include successful startup with default cell discovery, explicit `-servers`, `-rxbind`, auth/noauth, audit log options, bounded `-p`, Ubik database creation/open, and superuser-only Rx statistics access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/struct_ops.c -->
# sources/distributed-fs/openafs/src/budb/struct_ops.c

## Purpose
`struct_ops.c` centralizes BUDB structure diagnostics and conversions. It prints internal and RPC-facing backup database records, converts selected structures between network and host byte order, and copies internal database records into public `budb_*Entry` forms returned to clients.

## Important APIs, Types, And Functions
Print helpers cover `DbHeader`, `dump`, `budb_dumpEntry`, `memoryHashTable`, `budb_principal`, `structDumpHeader`, `tape`, `budb_tapeEntry`, `budb_tapeSet`, `budb_volumeEntry`, `volFragment`, and `volInfo`. Host/network conversion helpers include `volFragment_ntoh()`, `volInfo_ntoh()`, `tape_ntoh()`, `dump_ntoh()`, `DbHeader_ntoh()`, `dumpEntry_ntoh()`, `principal_hton()`, `principal_ntoh()`, `structDumpHeader_hton()`, `structDumpHeader_ntoh()`, `tapeEntry_ntoh()`, `tapeSet_hton()`, `tapeSet_ntoh()`, `textBlock_hton()`, `textBlock_ntoh()`, `textLock_hton()`, `textLock_ntoh()`, and `volumeEntry_ntoh()`. Public-copy helpers are `copy_ktcPrincipal_to_budbPrincipal()`, `dumpToBudbDump()`, `tapeToBudbTape()`, `volsToBudbVol()`, and `default_tapeset()`.

## Control Flow
The print routines are direct field renderers with light interpretation of BUDB flag bits. The byte-order routines perform field-by-field numeric conversion while string fields are copied as-is. Internal-to-public conversion routines assume host-order internal records and copy the subset of fields required by BUDB RPC/client structures. `default_tapeset()` zeroes a `budb_tapeSet`, creates the default `dumpname.%d` format, and initializes sequence fields.

## State And Persistence
The file has no durable state and no own global mutable state. Its effect is by copying, printing, and initializing caller-provided structures. Persistence relevance is indirect: these routines must match the database block layout and RPC structure contracts so dumps, restores, and admin displays interpret persisted BUDB records correctly.

## Dependencies And Integration Points
It depends on BUDB database layout headers (`database.h`, `budb.h`, `budb_internal.h`) and OpenAFS/Rx byte-order utilities. It is used by BUDB diagnostics, dump/restore code, and RPC conversion paths that bridge internal Ubik records to client-facing `budb_*` entries.

## Risks And Test Signals
The dominant risk is fixed-size string copying with `strcpy()`/`strncpy()` into legacy structure fields; callers must ensure source records are valid and bounded. Another risk is schema drift: adding fields to BUDB structures without updating these conversion routines silently loses or misreports data. Test signals should include round-trip byte-order tests on representative structures, default tape-set formatting, flag rendering for dump/tape/volume status combinations, and conversion of internal dump/tape/volume records into public entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/Makefile.in -->
# sources/distributed-fs/openafs/src/butc/Makefile.in

## Purpose
`Makefile.in` defines the LWP-based Tape Coordinator (`butc`) build, plus the `read_tape` and `tdump` utility targets. It selects the object set, OpenAFS library closure, install behavior, clean rules, and one source-specific compiler flag override.

## Important APIs, Types, And Functions
The key build variables are `INCLS`, `HACKS`, `LIBS`, and `SOBJS`. `SOBJS` builds `butc` from `dbentries.o`, `tcprocs.o`, `lwps.o`, `tcmain.o`, `list.o`, `recoverDb.o`, `tcudbprocs.o`, `dump.o`, and `tcstatus.o`. `LIBS` links BUDB, BUTM, volume, VLDB, protection/authentication, Ubik, Rx, audit, LWP, command, error, crypto, USD, util, OPR, and process-management libraries. `CFLAGS_tcudbprocs.o=@CFLAGS_NOERROR@` relaxes error handling for that object.

## Control Flow
The default `all` target builds `butc`, `read_tape`, and `tdump`. `butc` uses `AFS_LDRULE_NOQ`, with a special AIX branch that links `/usr/lib/libc_r.a`. `read_tape` and `tdump` are built directly from their C files. `install` and `dest` create target directories and install `read_tape` everywhere, but skip installing this `butc` binary on platforms where `tbutc` supplies the installed coordinator, except older Darwin variants and fallback systems.

## State And Persistence
The makefile persists no runtime state, but it determines which coordinator implementation and tools are installed into `sbindir` or `${DEST}/etc`. The install platform gates are operationally important because a system may build this target but intentionally not deploy it.

## Dependencies And Integration Points
It includes generated configuration makefiles from `@TOP_OBJDIR@/src/config`, `Makefile.lwp`, and `../config/Makefile.version`. Its library ordering encodes the coordinator's integration with BUDB, volume services, authentication, Rx/Ubik, tape/media handling, and command/audit infrastructure.

## Risks And Test Signals
Risks include stale library ordering, platform install drift, and object lists diverging from source dependencies. Build tests should verify `butc`, `read_tape`, and `tdump` on representative non-XBSA and platform-gated environments. Packaging tests should confirm that install/dest skip or install `butc` exactly as intended for Linux, Solaris, AIX, HP-UX, Darwin, and fallback systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/afsxbsa.c -->
# sources/distributed-fs/openafs/src/butc/afsxbsa.c

## Purpose
`afsxbsa.c` is the in-tree `NEW_XBSA` implementation of the XBSA Data Movement subset for the Tape Coordinator. It adapts the XBSA-style BSA API expected by `butc_xbsa.c` onto IBM TSM/ADSM DSM APIs loaded dynamically at runtime, handling session initialization, transactions, object query/get/send/delete, error translation, and trace/event logging.

## Important APIs, Types, And Functions
The file defines DSM function-pointer globals (`AFSdsmInit`, `AFSdsmBeginTxn`, `AFSdsmSendObj`, `AFSdsmGetData`, `AFSdsmDeleteObj`, and many others) populated by `dsm_MountLibrary()`. Support routines include `buildList()` and `freeList()` for archive deletes, `ourTrace()`, `ourLogEvent_Ex()`, `ourRCMsg()`, `stdXOpenMsgMap()`, `StrUpper()`, `xparsePath()`, `xlateRC()`, `fillArchiveResp()`, and `fillBackupResp()`. The exported BSA subset includes `BSAInit()`, `BSATerminate()`, `BSAChangeToken()`, `BSASetEnvironment()`, `BSAGetEnvironment()`, `BSABeginTxn()`, `BSAEndTxn()`, `BSAQueryApiVersion()`, `BSAQueryObject()`, `BSAGetObject()`, `BSAGetData()`, `BSASendData()`, `BSAEndData()`, `BSACreateObject()`, `BSADeleteObject()`, and `BSAMarkObjectInactive()`.

## Control Flow
Almost every public BSA entry lazily calls `dsm_MountLibrary()` if DSM symbols have not been loaded. `BSAInit()` checks DSM API version compatibility, validates owners/token, converts environment strings into DSM options, calls `AFSdsmInit()`, handles password-expiry cases, queries session info, and records node/session state in global `xopenGbl`. `BSABeginTxn()` marks an XBSA transaction, while DSM transactions are started lazily by create/delete paths. `BSAEndTxn()` commits or aborts active DSM work, terminates active queries, maps reason codes, and clears flags. Query flow maps BSA object descriptors to DSM object names and query buffers, starts a DSM query, returns the first result, and stores one look-ahead response. Read flow begins with `AFSdsmBeginGetData()`/`AFSdsmGetObj()`, continues with `AFSdsmGetData()`, and is cleaned up by `BSAEndData()`. Write flow registers filespace, binds management class, starts a DSM transaction if needed, sends object metadata via `AFSdsmSendObj()`, sends following data with `AFSdsmSendData()`, and ends with `AFSdsmEndSendObj()`. Delete flow either deletes an archive copy by ID or queries all matching archive IDs, while mark-inactive queries active backup objects and deletes them within a DSM transaction.

## State And Persistence
The file keeps process-global adapter state: `xopenGbl`, trace buffers, DSM function pointers, and `dsm_init`. Persistent effects occur in the external TSM/ADSM server: object creation, backup/archive metadata, inactive marking, and deletion. Session flags (`FL_IN_BSA_TXN`, `FL_IN_DSM_TXN`, `FL_IN_BSA_QRY`, `FL_PSWD_EXPIRE`, `FL_RC_WILL_ABORT`, `FL_END_DATA_DONE`) and `xopenGbl.oper` encode call sequencing and cleanup obligations.

## Dependencies And Integration Points
This file is compiled only under `xbsa`. It depends on TSM headers (`dsmapitd.h`, `dsmapifp.h`, `dsmrc.h`) via `afsxbsa.h`, OpenAFS tape coordinator logging (`ELog()`), BUTX error codes, and platform dynamic linking. Library paths are hard-coded by platform: AIX archive member, Linux `/usr/lib64/libApiTSM64.so` or `/usr/lib/libApiDS.so`, and Solaris `/usr/lib/libApiDS.so`.

## Risks And Test Signals
The code is legacy and high-risk around string bounds, global single-session state, and call sequencing. Many paths use `strcpy()`, `strcat()`, and fixed trace buffers; tests must include maximum owner, token, object-space, path, description, and object-info lengths. `BSASendData()` translates DSM errors but currently returns `BSA_RC_SUCCESS` through `XOPENRETURN`, so send-error propagation is a specific risk. Several flag clears use XOR, which can set a flag if sequencing assumptions are violated. Test signals should include dynamic library missing/symbol missing, version mismatch, init with generated/expired password, query no-match and multi-result, read to end-of-data, write with multiple data blocks, `WILL_ABORT` handling, delete by ID and by name, mark-inactive active/no-match cases, and concurrent coordinator scenarios if multiple sessions are ever attempted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/afsxbsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/afsxbsa.h -->
# sources/distributed-fs/openafs/src/butc/afsxbsa.h

## Purpose
`afsxbsa.h` supplies the in-tree XBSA/BSA compatibility header used when `NEW_XBSA` is enabled. It defines the BSA scalar types, constants, return codes, object/query/transaction structures, BSA function prototypes, and adapter-global state used by `afsxbsa.c`.

## Important APIs, Types, And Functions
The header maps BSA integer types to C scalar/paired-word forms and defines API/version constants (`BSA_API_VERSION`, `BSA_API_RELEASE`, `BSA_API_LEVEL`), ADSM-specific bounds, BSA maximum string sizes, and BSA return codes. It defines key data types including `ObjectName`, `ObjectOwner`, `ObjectDescriptor`, `QueryDescriptor`, `DataBlock`, `SecurityToken`, `CopyId`, `Vote`, `ObjectType`, `ObjectStatus`, `CopyType`, schedule/access policy structures, and the adapter `xGlobal`. It declares the BSA data movement functions implemented in `afsxbsa.c` and helper routines such as `xlateRC()`, `xparsePath()`, `StrUpper()`, `ourTrace()`, `ourLogEvent_Ex()`, `ourRCMsg()`, and `stdXOpenMsgMap()`.

## Control Flow
As a header, it has no runtime control flow. It controls compilation by including TSM DSM headers, declaring `extern "C"` linkage for C++, defining call-sequencing flags and operation states, and providing the `XOPENRETURN()` macro that traces and returns from adapter functions.

## State And Persistence
The header declares `xopenGbl` and trace buffers as externs. `xGlobal` holds DSM session info, initial BSA owner, session flags, current operation, current copy type, and query look-ahead storage. Persistent effects are not in the header, but these declarations govern how `afsxbsa.c` tracks external TSM session state while manipulating persistent TSM objects.

## Dependencies And Integration Points
It directly depends on IBM TSM DSM headers and is included by `butc_xbsa.h` under `NEW_XBSA`. The type definitions must match what `butc_xbsa.c` expects from a platform XBSA library so the coordinator can use either the external library or this adapter through the same function-pointer surface.

## Risks And Test Signals
The typedefs use legacy assumptions such as `unsigned long` widths and two-word 64-bit structures, so ABI behavior matters across 32-bit and 64-bit platforms. String typedefs are fixed-size arrays that rely on callers to leave room for terminators. `XOPENRETURN()` uses `sprintf()` into global trace storage and is not thread-local. Test signals include compile checks against supported TSM header versions, ABI/sizeof checks for descriptors and `DataBlock`, and functional tests that verify `butc_xbsa.c` can call the same interface in `NEW_XBSA` and non-`NEW_XBSA` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/afsxbsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_internal.h -->
# sources/distributed-fs/openafs/src/butc/butc_internal.h

## Purpose
`butc_internal.h` is the internal Tape Coordinator prototype header. It shares non-public functions across `butc` compilation units without exporting them as a stable external API.

## Important APIs, Types, And Functions
The header declares database-entry queue functions from `dbentries.c` (`useTape()`, `addVolume()`, `finishTape()`, `flushSavedEntries()`, `waitDbWatcher()`, `finishDump()`, `threadEntryDir()`), XBSA dump initialization when compiled with `xbsa`, task ID allocation, tape/LWP helpers, recovery helpers, authorization checks, and task abort checks.

## Control Flow
It has no runtime flow. It controls cross-file call visibility and conditional compilation. The only type forward declaration is `struct butx_transactionInfo` for the XBSA-specific `InitToServer()` signature.

## State And Persistence
The header declares functions that manipulate coordinator runtime state and backup database persistence, but owns no state itself. Its prototypes document which modules can enqueue BUDB updates, manage tape labels, prompt/unmount media, parse database tapes, and check task abort state.

## Dependencies And Integration Points
It depends on OpenAFS integer and tape/database types being available before inclusion. It is an integration point among `dbentries.c`, `dump.c`, `list.c`, `lwps.c`, `recoverDb.c`, `tcprocs.c`, and `tcstatus.c`.

## Risks And Test Signals
Risks are prototype drift and conditional XBSA mismatches. Because this is a private header, compile coverage of every platform/configuration combination is the primary test signal, especially `xbsa` and non-`xbsa` builds. Runtime tests indirectly cover it through dump, restore, tape label, database recovery, and abort-permission workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_prototypes.h -->
# sources/distributed-fs/openafs/src/butc/butc_prototypes.h

## Purpose
`butc_prototypes.h` declares thread-entry functions and selected globals for the Tape Coordinator. It complements `butc_internal.h` by collecting functions that are passed to LWP/pthread creation or used across coordinator modules.

## Important APIs, Types, And Functions
It declares thread routines `dbWatcher()`, `Dumper()`, `DeleteDump()`, `Restorer()`, `Labeller()`, `ScanDumps()`, `saveDbToTape()`, `restoreDbFromTape()`, and `KeepAlive()`. It also exposes `butc_confdir` and `allow_unauth` from `tcmain.c`.

## Control Flow
The header has no runtime control flow. Its function signatures all use `void *(*)(void *)`-style thread entrypoints, making them suitable for the coordinator's LWP/pthread abstraction.

## State And Persistence
It does not own state, but the declared routines drive major persistent operations: dumping/restoring volumes, saving/restoring the backup database, scanning dump tapes, and asynchronously flushing database entries. The declared globals control configuration and authentication policy access from modules outside `tcmain.c`.

## Dependencies And Integration Points
This header links coordinator modules around task execution and keepalive behavior. It must stay aligned with the actual implementations in `dbentries.c`, `dump.c`, `lwps.c`, `recoverDb.c`, `tcudbprocs.c`, and `tcmain.c`.

## Risks And Test Signals
Risks are wrong thread signatures or stale externs causing build failures or undefined behavior at thread creation. Compile tests with the coordinator's supported threading model are the main signal. Functional signals include successful launch of dump, restore, label, scan, database save/restore, keepalive, and watcher tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_xbsa.c -->
# sources/distributed-fs/openafs/src/butc/butc_xbsa.c

## Purpose
`butc_xbsa.c` is the Tape Coordinator's abstraction layer for XBSA servers. It hides whether BSA functions come from a platform XBSA shared library or the in-tree `NEW_XBSA` adapter, validates coordinator inputs, manages `butx_transactionInfo`, and maps BSA return codes to BUTX errors.

## Important APIs, Types, And Functions
The file declares function pointers for all BSA operations used by the coordinator, with signatures differing between `NEW_XBSA` and external-XBSA builds. `xbsa_error()` maps known BSA/ADSM return codes to operator log messages. Public wrapper functions are `xbsa_MountLibrary()`, `xbsa_Initialize()`, `xbsa_BeginTrans()`, `xbsa_EndTrans()`, `xbsa_Finalize()`, `xbsa_QueryObject()`, `xbsa_ReadObjectBegin()`, `xbsa_ReadObjectEnd()`, `xbsa_WriteObjectBegin()`, `xbsa_DeleteObject()`, `xbsa_WriteObjectEnd()`, `xbsa_WriteObjectData()`, and `xbsa_ReadObjectData()`.

## Control Flow
`xbsa_MountLibrary()` selects an ADSM server type, loads external symbols on old builds or binds directly to in-tree BSA functions under `NEW_XBSA`, queries the API version, rejects an incompatible technical-standard level, and sets server capability flags for multiple-server support. `xbsa_Initialize()` fills environment strings, validates owner/token/server strings, calls `XBSAInit()`, calls `XBSAGetEnvironment()`, and records `maxObjects`. Transaction wrappers begin/end/finalize BSA sessions. Query prepares a backup-file `QueryDescriptor` and stores the resulting object in `info->curObject`. Read and write wrappers convert coordinator buffers to `DataBlock`, enforce `XBSAMAXBUFFER`, and set count/end-of-data outputs. `xbsa_WriteObjectBegin()` also rotates transactions when `numObjects == maxObjects`, fills `ObjectDescriptor` fields, and starts the BSA object. Delete maps to `XBSAMarkObjectInactive()` for backup objects.

## State And Persistence
`butx_transactionInfo` is the central state object: API version, BSA handle, server type/flags, max object count, current object count, server name, security token, owner, and current object descriptor. Persistent effects occur in the external XBSA/TSM server through create, send, mark-inactive, and transaction commit calls.

## Dependencies And Integration Points
It depends on `butc_xbsa.h`, `afs/butx.h`, `afs/tcdata.h`, `bubasics`, coordinator logging (`ELog()`), and platform dynamic linking for non-`NEW_XBSA` AIX/Solaris builds. It is called from dump/restore paths to store and retrieve backup data through XBSA instead of tape media.

## Risks And Test Signals
Risks include dynamic-library path/symbol drift, ABI differences between external XBSA and `NEW_XBSA`, server environment hacks (`envP[0] = NULL` for TSM V5), and transaction rollover at `maxObjects`. Several error messages are misleading copy/pastes, so tests should assert return codes rather than logs alone. Test signals include mount failure, invalid server type, version rejection, successful initialization with server name, begin/end/finalize sequencing, query no-match handling, read/write buffer bounds, transaction rollover, delete no-volume mapping, and both `NEW_XBSA` and external-XBSA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_xbsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_xbsa.h -->
# sources/distributed-fs/openafs/src/butc/butc_xbsa.h

## Purpose
`butc_xbsa.h` defines the Tape Coordinator's XBSA configuration, server-type constants, transaction state, public wrapper prototypes, and global XBSA command-line/configuration variables.

## Important APIs, Types, And Functions
It defines server types and masks (`XBSA_SERVER_TYPE_NONE`, `UNKNOWN`, `ADSM`, `MASK`), conditional `CONF_XBSA`, server flags (`XBSA_SERVER_FLAG_MULTIPLE`, `NONE`), buffer limits (`XBSAMINBUFFER`, `XBSADFLTBUFFER`, `XBSAMAXBUFFER`), ADSM version thresholds for multiple-server support, and XBSA technical-standard version constants. `struct butx_transactionInfo` stores API version, handle, server type, max/active object counts, server name, security token, owner, and current object. The header declares all `xbsa_*` wrapper functions used by coordinator dump/restore code.

## Control Flow
The header itself has no runtime flow, but its macros control whether XBSA code is active and how server type/flag bitfields are read and written. Under `NEW_XBSA` it includes the local `afsxbsa.h`; otherwise it includes the platform `<xbsa.h>`.

## State And Persistence
It declares global XBSA settings with `XBSA_EXT`: `xbsaType`, and when `xbsa` is enabled, `butxInfo`, `dumpRestAuthnLevel`, `xbsaObjectOwner`, `appObjectOwner`, `adsmServerName`, `xbsaSecToken`, and `xbsalGName`. These globals represent coordinator configuration and session state; persistence is in the remote XBSA server accessed through the wrappers.

## Dependencies And Integration Points
The header bridges coordinator code, the BUTX error/API layer, the local XBSA adapter, and external XBSA headers. It is included by both the wrapper implementation and coordinator modules that need to know whether XBSA is configured.

## Risks And Test Signals
The main risks are conditional compilation skew and ABI mismatches between local and external XBSA headers. The handle type changes under `NEW_XBSA`, so tests must cover both configurations. Buffer limits are constrained by BSA's 16-bit `DataBlock` lengths, so boundary tests should cover 0, `XBSAMINBUFFER`, `XBSADFLTBUFFER`, `XBSAMAXBUFFER`, and oversized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/butc_xbsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/config -->
# sources/distributed-fs/openafs/src/butc/config

## Purpose
`config` is a one-line local configuration/data file for the `butc` source directory. Its content is `200000 /tmp`, which appears to describe a numeric capacity or threshold paired with a temporary directory path.

## Important APIs, Types, And Functions
There are no functions or types. The important data fields are the integer-like value `200000` and the path `/tmp`.

## Control Flow
There is no control flow in the file. Any behavior depends on consumers elsewhere in the coordinator or test tooling parsing the line.

## State And Persistence
The file is static repository data. It may influence runtime or test behavior if copied/read as a coordinator configuration input, but this file itself performs no persistence.

## Dependencies And Integration Points
No direct dependency is visible inside the file. Integration must be discovered from consumers that open `src/butc/config` or install it alongside Tape Coordinator tooling.

## Risks And Test Signals
Risks are format ambiguity and hard-coded `/tmp` assumptions. Test signals should search for consumers, verify the expected numeric unit, and confirm behavior when `/tmp` lacks space, is mounted with restrictive options, or the line is malformed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/dbentries.c -->
# sources/distributed-fs/openafs/src/butc/dbentries.c

## Purpose
`dbentries.c` buffers and asynchronously flushes Tape Coordinator backup database updates. Dump, tape, and volume operations enqueue BUDB entry structures while backup work proceeds; `dbWatcher()` drains those queues and calls the BUDB client APIs to create/finish dumps, use/finish tapes, and add volumes.

## Important APIs, Types, And Functions
The module owns two double-linked queues: `savedEntries` for the current dump workflow and `entries_to_flush` for watcher-ready updates. `threadEntry()` and `threadEntryDir()` allocate a queue node plus copied entry payload. Public queue producers are `useDump()`, `finishDump()`, `useTape()`, `finishTape()`, and `addVolume()`. `flushSavedEntries()` moves or drops queued entries based on dump status. `waitDbWatcher()` blocks until the watcher is idle and the flush queue is empty. `dbWatcher()` is the long-running thread entrypoint that applies queued updates to BUDB.

## Control Flow
Producer functions build `budb_dumpEntry`, `budb_tapeEntry`, or `budb_volumeEntry` payloads and enqueue them. Allocation retries up to five times, sleeping a minute between attempts if the watcher is active. `flushSavedEntries()` has special handling for `DUMP_NORETRYEOT`: it removes the just-used tape because the first volume exceeded tape capacity and the tape will be reused. It then drops volume entries on failed dumps while preserving dump/tape metadata for watcher processing. `dbWatcher()` initializes both queues, loops forever, drains `entries_to_flush`, dispatches by `dlq_type`, and sleeps for two seconds when idle. Volume entries are batched up to `MAXVOLUMESTOADD` for `bcdb_AddVolumes()`; a negative batch failure disables batching and falls back to `bcdb_AddVolume()` one entry at a time.

## State And Persistence
Runtime state is the two queues, `dbWatcherinprogress`, `addvolumes`, and `addedDump`. Persistent state changes are made through BUDB client calls: `bcdb_CreateDump()`, `bcdb_FinishDump()`, `bcdb_UseTape()`, `bcdb_FinishTape()`, `bcdb_AddVolumes()`, and `bcdb_AddVolume()`. The `addedDump` flag suppresses dependent tape/volume finishing when dump creation failed.

## Dependencies And Integration Points
The file depends on OpenAFS queue helpers (`dlq*`), LWP/pthread sleep abstractions, `budb_client` APIs, coordinator error logging, and BUDB entry structures. It is integrated with dump/tape workflows through prototypes in `butc_internal.h` and with thread startup through `butc_prototypes.h`.

## Risks And Test Signals
There is no explicit locking around the queues in this file, so correctness depends on the broader coordinator threading model or serialized producer access. Allocation retry paths can still dereference null if both allocations never succeed after the loop, so low-memory behavior is sensitive. `flushSavedEntries()` assumes the first saved entry is `DLQ_USETAPE` for `DUMP_NORETRYEOT`. Test signals include successful dump/tape/volume enqueue and flush, failed dump dropping volume entries, no-retry-EOT tape removal, duplicate dump ID handling, batch add success, batch add negative fallback, watcher idle waiting, and shutdown paths that call `waitDbWatcher()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/dbentries.c -->
