# Research: subset-b-007783

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.c -->
# sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.c

## Purpose
This file implements private helpers for the OpenAFS configuration admin library. It validates `cfg_host_t` handles, lazily opens BOS handles, resolves and compares host names/addresses, edits local configuration-side filesystem state, sleeps portably, and, on Windows, starts/stops/queries the AFS client and BOS control services.

## Important APIs, Types, and Functions
- `cfgutil_HostHandleValidate` checks the opaque host handle magic values, validity flag, host/cell names, and cell handle before public cfg entry points use it.
- `cfgutil_HostHandleBosInit` lazily initializes `cfg_host->bosHandle` with `bos_ServerOpen` under `cfg_host->mutex`.
- `cfgutil_HostNameGetFull`, `cfgutil_HostNameIsAlias`, `cfgutil_HostNameIsLocal`, `cfgutil_HostAddressFetchAll`, `cfgutil_HostAddressIsValid`, and `cfgutil_HostNameGetAddressString` provide hostname/address normalization and comparison. Several are Windows-only and return `ADMCFGNOTSUPPORTED` on Unix.
- `cfgutil_HostNameGetCellServDbAlias` opens a null cell, opens BOS on a filesystem database host, iterates the server CellServDB, and returns the entry that aliases a requested host.
- `cfgutil_CleanDirectory` removes non-directory entries from one directory without recursing.
- `cfgutil_HostSetNoAuthFlag` creates or unlinks `AFSDIR_SERVER_NOAUTH_FILEPATH` for local server no-auth mode.
- `cfgutil_WindowsServiceStart`, `cfgutil_WindowsServiceStop`, and `cfgutil_WindowsServiceQuery` wrap the Windows SCM and translate generic service failures through `ServiceCodeXlate`.

## Control Flow and State
Most helpers use the library convention `rc == 1` for success, `rc == 0` for failure, and return a detailed `afs_status_t` through `st` when provided. BOS handle initialization is guarded by a pthread mutex and stores the resulting handle back in the host handle for reuse. Host address helpers allocate address arrays and free them after comparison or conversion. Windows service helpers open SCM/service handles, issue start/stop/query operations, poll until timeout, and close handles before returning.

## Persistence and Side Effects
The file can mutate local server authentication state by creating/truncating or unlinking the server `NoAuth` marker file. `cfgutil_CleanDirectory` unlinks files in a target directory. Windows helpers change local service state. Network and RPC side effects include DNS lookups, BOS connections, and CellServDB iteration.

## Dependencies and Integration Points
The helpers depend on `afs_AdminErrors.h` status codes, BOS admin APIs, client admin null-cell opening, `afs/dirpath.h` canonical paths, pthreads, roken, DNS/socket APIs, and Windows service APIs behind `AFS_NT40_ENV`. `cfgservers.c` and other cfg modules rely on these routines for common validation, BOS setup, host identity checks, and service control.

## Risks
Large parts of host resolution and Windows service logic are platform-specific; Unix callers receive `ADMCFGNOTSUPPORTED` for some address/full-name operations. Several buffers are assumed to be correctly sized by callers (`MAXHOSTCHARS`, `MAXPATHLEN`). The non-recursive cleaner silently ignores disappearing files and directories, which is intentional but can mask unexpected filesystem content. `cfgutil_HostSetNoAuthFlag` bypasses BOS credentials by editing the local flag file directly, so privilege and locality checks are critical. Error handling often preserves only one status, and later cleanup failures can overwrite earlier root causes.

## Test Signals
Useful tests include invalid-host-handle cases for every validation branch, concurrent lazy BOS initialization, host alias comparison with multi-address hosts, `NoAuth` file creation/removal with permission failures, `CleanDirectory` behavior with files/directories/missing directories, and Windows service start/stop timeout/error translation. On Unix, tests should assert the documented `ADMCFGNOTSUPPORTED` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.h -->
# sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.h

## Purpose
This private header defines the configuration library host-handle structure and declares internal helper routines shared by cfg implementation files. It is not a public admin API surface; it exposes internals needed by modules that configure BOS, servers, clients, and host state.

## Important APIs, Types, and Functions
- `cfg_host_t` contains validation magic, `is_valid`, the target `hostName`, `is_local`, an admin `cellHandle`, `cellName`, a pthread mutex, lazy `bosHandle`, and closing magic.
- Declarations cover host validation, BOS initialization, cell-name compatibility, host canonicalization/alias/address queries, directory cleanup, no-auth flag toggling, and portable sleep.
- Under `AFS_NT40_ENV`, declarations expose Windows service start/stop/query helpers using `LPCTSTR`, `DWORD`, service state values, and admin status output.

## Control Flow and State
The header encodes the shared handle lifecycle model used by cfg modules: callers receive an opaque host handle, implementation code casts it to `cfg_host_p`, validates magic and state, and then uses the embedded cell and BOS handles. The mutex specifically protects one-time BOS initialization, not all host-handle fields.

## Persistence and Side Effects
The header itself has no side effects, but it declares functions that mutate BOS/service state, local no-auth files, and directories. It also establishes that host handles retain a reusable BOS connection pointer.

## Dependencies and Integration Points
It depends on prior inclusion of pthread and AFS admin types such as `afs_status_p` and `afs_int32`. Public cfg source files include this header beside `afs_cfgAdmin.h`; client/BOS/adminutil modules provide the types and functions referenced by declarations.

## Risks
Because the struct is shared internally, any ABI or field-order change affects all cfg object files compiled against it. The header relies on include-order for pthread and AFS types. The raw `void *` cell/BOS handles avoid type checking. The `cellName` field is a borrowed `const char *`, so lifetime must follow the owning cell handle.

## Test Signals
Compile coverage is important: every cfg implementation using this header should build on Unix and Windows. Runtime tests should validate that host handles created by the public cfg open path satisfy these declarations and that invalidated handles fail consistently after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfgservers.c -->
# sources/distributed-fs/openafs/src/libadmin/cfg/cfgservers.c

## Purpose
This file implements server-side configuration operations in the cfg admin library: BOS server control, database server setup, fileserver setup, update server setup, update client setup, and quorum checks. It wraps lower-level BOS, VOS, Ubik vote, and service-control APIs into higher-level configuration actions.

## Important APIs, Types, and Functions
- Exported BOS functions: `cfg_BosServerStart`, `cfg_BosServerStop`, and `cfg_BosServerQueryStatus`.
- Database server functions: `cfg_AuthServerStart`, `cfg_DbServersStart`, `cfg_DbServersStop`, `cfg_DbServersQueryStatus`, `cfg_DbServersRestartAll`, `cfg_DbServersWaitForQuorum`, and `cfg_DbServersStopAllBackup`.
- File server functions: `cfg_FileServerStart`, `cfg_FileServerStop`, and `cfg_FileServerQueryStatus`.
- Update server/client functions: `cfg_UpdateServerStart`, `cfg_UpdateServerStop`, `cfg_UpdateServerQueryStatus`, `cfg_SysBinServerStart`, `cfg_UpdateClientStart`, `cfg_UpdateClientStop`, `cfg_UpdateClientStopAll`, `cfg_UpdateClientQueryStatus`, `cfg_SysControlClientStart`, and `cfg_BinDistClientStart`.
- Static helpers `SimpleProcessStart`, `FsProcessStart`, and `BosProcessDelete` create/start/stop/delete BOS instances. `UpdateCommandParse` recognizes configured `etc` and `bin` paths. `UbikQuorumCheck` and `UbikVoteStatusFetch` determine whether Ubik database services have a writable sync site.
- Exported constants such as `cfg_kaserverBosName`, `cfg_ptserverBosName`, `cfg_fileserverBosName`, `cfg_upserverBosName`, `cfg_upclientBosNamePrefix`, and update-client suffixes expose BOS instance names.

## Control Flow and State
All public functions first validate `cfg_host_t` and usually call `cfgutil_HostHandleBosInit`. Start functions create BOS instances if missing and then set execution state to running. Stop functions set instances stopped, wait for transitions, and delete them. Query functions inspect BOS process info, process names, or process command parameters. Database quorum loops call vote debug RPCs repeatedly until all required services are writable or the timeout expires.

## Persistence and Side Effects
The file persistently changes BOS configuration by creating and deleting process instances for `kaserver`, `ptserver`, `vlserver`, `buserver`, `fs`, `upserver`, and `upclient*`. It starts and stops those processes. `cfg_FileServerStop` optionally removes the host's file-server addresses from the VLDB after deleting the fileserver BOS instance. BOS server start/stop on Windows manipulates the local AFS BOS control service. Quorum checks perform network RX calls but do not mutate state.

## Dependencies and Integration Points
The module integrates `cfginternal` host utilities, BOS admin, VOS admin, client admin, util admin, RX, Ubik vote RPCs, OpenAFS directory constants, and Windows registry/service names. It assumes standard canonical server binary paths from `afs/dirpath.h` and standard ports from cellconfig/ubik headers. It is exercised by `cfg/test/cfgtest.c` and linked into `libcfgadmin`.

## Risks
Remote BOS start/stop is explicitly unsupported for some BOS service operations. Many operations use a "try all, last error wins" pattern, which can hide earlier failures. `BosProcessDelete` treats missing instances as success, useful for idempotence but potentially surprising in diagnostics. Command parsing mutates the command string, searches plain text paths, and may be brittle around quoting or unusual path layouts. `UpdateCommandParse` reads the character before a found path and assumes it is inside the command buffer. Quorum checks ignore individual unreachable servers while looking for a writable sync site, which matches availability goals but can mask partial outages. Fileserver readiness is represented by a fixed five-second sleep.

## Test Signals
Tests should cover idempotent start/stop for existing/missing BOS instances, query status with missing/mis-typed process entries, update command parsing for clear/crypt sys/bin path combinations, quorum timeout and old/new vote debug responses, backup server optional behavior, VLDB address cleanup after fileserver stop, and Unix/Windows differences for BOS service start/stop. Integration tests require a BOS-capable cell or mocks for BOS/VOS/RX/Ubik APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/cfgservers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/test/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/cfg/test/Makefile.in

## Purpose
This makefile builds the `cfgtest` command-line test driver for the configuration admin library. It is an Autoconf-era OpenAFS makefile fragment that pulls in project config and pthread build rules.

## Important APIs, Types, and Functions
The key target is `cfgtest`, built from `cfgtest.o` and `CFGTESTLIBS`. The library list links admin utility, client admin, cfg admin, BOS admin, VOS admin, KAS admin, PTS admin, auth/rpc libraries, and `libcmd.a`. `test` and `tests` alias the `cfgtest` target. `clean` removes objects, the binary, and core files.

## Control Flow and State
Build flow is simple: include shared make configuration, define the static libraries needed by the test driver, link with `$(AFS_LDRULE)`, and expose conventional test/clean targets.

## Persistence and Side Effects
The makefile creates a local `cfgtest` binary and object files. It reads installed/destination libraries from `$(DESTDIR)` and removes generated outputs on clean.

## Dependencies and Integration Points
It integrates the cfg test driver with almost every libadmin component because `cfgtest.c` exercises configuration, client, BOS, VOS, KAS, and PTS flows. It depends on `Makefile.config`, `Makefile.pthread`, `AFS_LDRULE`, `XLIBS`, and the admin libraries being built/installed in expected locations.

## Risks
The link rule contains `-LDEST/lib/afs`, which appears literal rather than `-L$(DEST)/lib/afs` or `-L$(DESTDIR)/lib/afs`; the explicit archive paths may hide that in normal builds, but it is a suspicious portability signal. Static library ordering matters for this old-style link line. The `# static library` comment is placed on the `CFGTESTLIBS` continuation line and should be checked by make parsing.

## Test Signals
A useful signal is whether `make test` builds `cfgtest` after all listed libraries are present. Link failures identify missing cross-library dependencies in the admin stack. `make clean` should remove only local generated files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/test/cfgtest.c -->
# sources/distributed-fs/openafs/src/libadmin/cfg/test/cfgtest.c

## Purpose
This file is a command-line test driver for cfg admin operations. It initializes AFS client admin state, obtains tokens, opens a cell, registers libcmd commands, and dispatches individual manual/integration tests for CellServDB, server, host, and client configuration functions.

## Important APIs, Types, and Functions
- Global state: `myCellName`, `myTokenHandle`, and `myCellHandle` hold process-wide admin context.
- `GetErrorText` translates `afs_status_t` values with `util_AdminErrorCodeTranslate`.
- CellServDB commands: `DoCellServDbAddHost`, `DoCellServDbRemoveHost`, `DoCellServDbEnumerate`, plus `CellServDbCallBack` and pthread condition state for async completion.
- Server commands: `DoDbServersWaitForQuorum`, `DoFileServerStart`, and `DoFileServerStop`.
- Host/client commands: `DoHostPartitionTableEnumerate`, `DoClientCellServDbAdd`, `DoClientCellServDbRemove`, `DoClientStart`, `DoClientStop`, `DoClientSetCell`, `DoClientQueryStatus`, and `DoHostQueryStatus`.
- `Setup*Cmd` functions register syntax and parameters with `cmd_CreateSyntax`/`cmd_AddParm`. `main` performs initialization, dispatch, and cleanup.

## Control Flow and State
`main` calls `afsclient_Init`, discovers the local cell, tries to reuse existing tokens, falls back to unauthenticated tokens, opens a cell handle, registers all commands, dispatches the requested command, and closes handles. Command handlers generally open a cfg host handle, call one cfg API, print translated status, and close the handle. CellServDB add/remove handlers wait on a condition variable until the callback reports termination.

## Persistence and Side Effects
The test commands can mutate real cell/server/client configuration: adding/removing CellServDB hosts, starting/stopping fileservers and clients, setting default client cell, and changing client CellServDB entries. It also opens tokens and cell handles. Output is printed to stdout and errors are reported as translated text.

## Dependencies and Integration Points
The driver integrates `afs_clientAdmin`, `afs_cfgAdmin`, `afs_utilAdmin`, pthreads, OpenAFS command parsing, and cellconfig types. It is built by `cfg/test/Makefile.in` and serves as a manual integration harness for cfg APIs rather than a self-checking unit test suite.

## Risks
Because commands operate on live AFS configuration, accidental invocation against production hosts can be destructive. Several handlers overwrite `st` during cleanup, so a close failure may mask the operation result. `DoClientSetCell` builds a multistring in a fixed 1024-byte buffer without length checks. The callback wait assumes the terminal callback always fires after successful async start. Token fallback to unauthenticated mode can make tests pass into no-auth paths unintentionally.

## Test Signals
The command registrations document expected public cfg workflows. Useful signals include successful command parsing, callback completion for CellServDB updates, proper status translation, handle cleanup after each command, and realistic integration runs against a disposable cell or mocked admin APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/cfg/test/cfgtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/client/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/client/Makefile.in

## Purpose
This makefile builds and installs the OpenAFS client admin static library and public header.

## Important APIs, Types, and Functions
`ADMINOBJS` contains `afs_clientAdmin.o`; `LIBOBJS` mirrors it. The `all` target installs `afs_clientAdmin.h` into `$(TOP_INCDIR)/afs` and `libclientadmin.a` into `$(TOP_LIBDIR)`. `install` and `dest` copy the header and archive to configured or destination include/lib trees. `libclientadmin.a` is built with `$(AR)` and indexed with `$(RANLIB)`.

## Control Flow and State
The build compiles `afs_clientAdmin.c` into one object, archives it, and copies the archive/header into build or install destinations. The explicit dependency `afs_clientAdmin.o: afs_clientAdmin.h` ensures public API changes rebuild the object.

## Persistence and Side Effects
Generated artifacts are `afs_clientAdmin.o` and `libclientadmin.a`; install/dest targets create include and library directories and copy outputs. `clean` removes local objects and library archives.

## Dependencies and Integration Points
The file relies on OpenAFS global make configuration and pthread settings. Downstream admin libraries and tests link `libclientadmin.a` for token, cell, mountpoint, ACL, server enumeration, stats, and rxdebug helpers.

## Risks
The library is a single-object archive, so any change in `afs_clientAdmin.c` rebuilds the full archive. Install and dest paths differ (`DESTDIR`/configured prefix versus `DEST` staging), and packaging must invoke the correct target. Missing dependency declarations on internal headers can cause stale builds if those internals change.

## Test Signals
Build tests should confirm the header and archive appear in top-level and install destinations, `ranlib` succeeds, and `make clean` removes local generated outputs without touching installed artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/client/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.c

## Purpose
This file implements client-oriented OpenAFS admin APIs: initialization, token acquisition/use, cell handle creation, mountpoint and ACL editing, server enumeration, RPC stats connections, cache-manager stats connections, and rxdebug handle creation.

## Important APIs, Types, and Functions
- Initialization and validation: `afsclient_Init`, `client_once`, and `IsTokenValid`.
- Token APIs: `afsclient_TokenGetExisting`, `afsclient_TokenPrint`, `afsclient_TokenSet`, `afsclient_TokenGetNew`, `afsclient_TokenQuery`, and `afsclient_TokenClose`, with static `GetAFSToken` and `GetKASToken`.
- Cell APIs: `afsclient_CellOpen`, `afsclient_NullCellOpen`, `afsclient_CellClose`, `afsclient_CellNameGet`, and `afsclient_LocalCellGet`.
- Filesystem helpers: `afsclient_MountPointCreate`, `afsclient_ACLEntryAdd`, and platform-specific `Parent` helpers.
- Server enumeration: `afsclient_AFSServerGet`, `afsclient_AFSServerGetBegin`, `afsclient_AFSServerGetNext`, `afsclient_AFSServerGetDone`, and iterator callbacks over cached server data.
- Stats/debug APIs: `afsclient_RPCStatOpen`, `afsclient_RPCStatOpenPort`, `afsclient_RPCStatClose`, `afsclient_CMStatOpen`, `afsclient_CMStatOpenPort`, `afsclient_CMStatClose`, `afsclient_RXDebugOpen`, `afsclient_RXDebugOpenPort`, and `afsclient_RXDebugClose`.

## Control Flow and State
`afsclient_Init` uses `pthread_once`, initializes path state, RX, and KAS cell config. Token creation either wraps existing kernel tokens, prints server-key tokens from a config dir, creates unauthenticated rxnull tokens, or obtains KAS/AFS rxkad tokens from the auth service. `afsclient_CellOpen` validates tokens, opens ubik clients for KAS, PTS, and VOS, stores token and server-list cache state in `afs_cell_handle_t`, and marks the handle valid. Server enumeration merges database-server data from util admin with file-server data from VOS, deduplicates addresses, reverse-resolves names, caches the result with a ten-minute TTL, and serves it through the common admin iterator.

## Persistence and Side Effects
Token APIs can read kernel tokens and set kernel tokens. Cell open creates RX/Ubik client state. Mountpoint creation creates a symlink on Unix or uses `VIOC_AFS_CREATE_MT_PT` on Windows. ACL addition reads and writes directory ACLs via pioctl. Stats and rxdebug functions open sockets/RX cached connections and close or release them. Server enumeration may populate a per-cell-handle cache.

## Dependencies and Integration Points
The implementation depends on RX/RXKAD/RX null, KAS auth utilities, ktc token APIs, afsconf, VOS admin, util admin, pt/vl headers, pioctl, pthread global locks, and admin iterator utilities. KAS and PTS admin modules consume cell handles created here. cfg modules use null-cell and regular cell handles for host and BOS operations.

## Risks
Callers must invoke `afsclient_Init` first. Many output buffers are assumed large enough. Token security objects are allocated but failure paths mostly free only the token handle, so object ownership must be audited carefully. `afsclient_TokenClose` frees the token handle without destroying individual security classes. `afsclient_NullCellOpen` does not free the partially allocated cell handle if token creation fails. ACL manipulation uses fixed 2 KB buffers, string parsing, and concatenation, creating overflow/truncation risk on large ACLs. Server enumeration relies on global locking around resolver calls and has race handling for the shared cache. `afsclient_RXDebugOpen` stores host-order address/port while `afsclient_RXDebugOpenPort` stores network-order values, a behavioral inconsistency worth testing.

## Test Signals
Tests should cover initialization requirements, authenticated/unauthenticated/existing/server-key token paths, token query fields, cell open/close cleanup on partial failures, null-cell lifecycle, mountpoint creation with/without VLDB checking, ACL replacement for existing users and large ACLs, server enumeration deduplication and cache expiry, stats connection port/type selection, KAS token requirements for KAS stats, and rxdebug open/close byte-order behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.h

## Purpose
This public header declares the client admin API and public data structures for tokens, cell access, mountpoints, ACL edits, AFS server enumeration, stats connections, and rxdebug handles.

## Important APIs, Types, and Functions
- Volume and ACL enums define caller-facing choices for mountpoint type/checking and individual ACL rights.
- `acl_t` groups read/write/lookup/delete/insert/lock/admin rights.
- `afs_server_type_t`, `afs_stat_source_t`, and `afs_serverEntry_t` describe server classes, stats endpoints, and enumerated servers.
- Function declarations expose token management, cell open/close/name/local-cell lookup, mountpoint creation, ACL entry addition, initialization, server get iterators, RPC stats open/close, CM stats open/close, and rxdebug open/close.

## Control Flow and State
The header establishes an opaque-handle API style: callers receive `void *` token/cell/iterator handles from begin/open functions and pass them to close/done functions. Iteration follows `GetBegin`, repeated `GetNext`, and `GetDone`. Stats and debug handles are similarly opened and closed by paired calls.

## Persistence and Side Effects
Declared APIs can create/set tokens, open network connections, create mountpoints, write ACLs, and allocate/free iterator or handle state. The header itself only defines the contract.

## Dependencies and Integration Points
It includes `afs/afs_Admin.h` for common admin calling convention and status types. The KAS, PTS, VOS, BOS, cfg, and test code use these declarations to obtain authenticated cell handles and client-side utility behavior.

## Risks
Use of `void *` handles and caller-supplied buffers limits compile-time checking. Fixed constants such as `AFS_MAX_SERVER_NAME_LEN` and `AFS_MAX_SERVER_ADDRESS` constrain returned server data. The header undefines `DELETE` to avoid macro collisions before defining ACL delete enums, which signals portability sensitivity with platform headers.

## Test Signals
ABI checks should compile representative callers in C and C++-like include environments, especially where `DELETE` may be predefined. API tests should validate handle pairing, iterator termination with `ADMITERATORDONE`, and buffer-size expectations documented by implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/kas/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/kas/Makefile.in

## Purpose
This makefile builds and installs the KAS admin static library and public header.

## Important APIs, Types, and Functions
`ADMINOBJS` is `afs_kasAdmin.o`. `KAUTHOBJS` imports generated/client KAuth support objects `kauth.cs.o`, `kauth.xdr.o`, and `kaaux.o`. `libkasadmin.a` archives both admin and KAuth support objects. `all`, `install`, and `dest` copy `afs_kasAdmin.h` and the archive into build/install destinations.

## Control Flow and State
The build compiles the local admin object and KAuth support sources from `../../kauth`, archives them, runs `ranlib`, and installs the public header/library. The KAuth objects are compiled through `$(AFS_CCRULE)` from source paths outside this directory.

## Persistence and Side Effects
Generated outputs include object files and `libkasadmin.a`; install/dest targets create include/lib directories and copy artifacts. Clean removes local objects and KAS admin archives.

## Dependencies and Integration Points
The KAS admin library depends on KAuth RPC/XDR generated code and `kaaux.c`. Client admin cell handles provide KAS ubik clients consumed by `afs_kasAdmin.c`. Other admin components link this archive for authentication database management.

## Risks
The archive bundles generated KAuth RPC objects, so it must stay in sync with the kauth interface. Relative paths to `../../kauth` are sensitive to build layout. As with other static OpenAFS makefiles, library order matters for downstream link lines.

## Test Signals
Signals include successful rebuild after KAuth RPC source changes, install/dest header and archive placement, and downstream link success for code calling KAS admin APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/kas/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.c

## Purpose
This file implements the OpenAFS KAS admin API over KAuth/Ubik RPCs. It manages KAS server handles, principal creation/deletion/query/iteration, password/key updates, lock status/unlock operations, principal field updates, server stats/debug queries, random key retrieval, and string-to-key/checksum utilities.

## Important APIs, Types, and Functions
- Private `kas_server_t` stores magic, validity, `struct ubik_client *servers`, and cell name.
- Validation/selection helpers: `IsValidServerHandle`, `IsValidCellHandle`, and `ChooseValidServer` enforce that callers use either a cell handle or a KAS server handle, not both.
- Conversion helper `kaentryinfo_to_kas_principalEntry_t` maps KAuth `kaentryinfo` flags, dates, key fields, and packed auth bytes into public `kas_principalEntry_t`.
- Server handle APIs: `kas_ServerOpen` and `kas_ServerClose`.
- Principal APIs: `kas_PrincipalCreate`, `kas_PrincipalDelete`, `kas_PrincipalGet`, iterator trio `kas_PrincipalGetBegin`/`Next`/`Done`, `kas_PrincipalKeySet`, `kas_PrincipalLockStatusGet`, `kas_PrincipalUnlock`, and `kas_PrincipalFieldsSet`.
- Server/crypto APIs: `kas_ServerStatsGet`, `kas_ServerDebugGet`, `kas_ServerRandomKeyGet`, `kas_StringToKey`, and `kas_KeyCheckSum`.

## Control Flow and State
Most exported functions validate arguments, call `ChooseValidServer`, issue a `ubik_KAM_*` RPC, translate/copy output structures, then return `rc` plus `afs_status_t`. `kas_ServerOpen` resolves an explicit server list into KAuth ports and creates a ubik client with `ka_AuthSpecificServersConn`. Principal iteration uses the common admin iterator with `ubik_KAM_ListEntry`, cached `kas_identity_t` slots, and a cleanup callback. Lock status and unlock use `ubik_CallIter` because the lock state is not synchronized like the normal Ubik database.

## Persistence and Side Effects
Principal create/delete, password/key set, unlock, and field-set operations mutate the KAS database or per-server lock state. Server open/close allocate and destroy ubik client state. Stats/debug/random-key/string-to-key/checksum operations are read-only from the database perspective, except for network/RPC activity.

## Dependencies and Integration Points
The implementation depends on `afs_kasAdmin.h`, admin internals, client admin cell handles, KAuth headers/RPC stubs, Ubik, RX, pthread-related build config, and utility address resolution. It is built with the KAuth support objects declared in `kas/Makefile.in`. cfg server setup uses KAS readiness/quorum indirectly, and client admin token creation supplies KAS tokens used by cell handles.

## Risks
The API permits either a cell handle or an explicit server handle; misuse is detected at runtime. `kas_ServerOpen` assumes the given server list belongs to the cell and notes this is not verified. Some public output string copies use `strcpy` into fixed-size fields. `kas_PrincipalUnlock` records `save_tst` but returns the final `tst`, so the first non-terminal failure may be lost. `kas_StringToKey` does not validate null inputs before passing them to KAuth. `kas_KeyCheckSum` does not check `key` or `cksumP` for null. Packed password-policy fields have 255-value limits and lock-time rounding that must match legacy KAS behavior.

## Test Signals
Tests should cover handle selection errors, server-list empty/too-long/name-resolution failures, create/delete/get flows against a disposable KAS database, iterator termination and cleanup, field updates for each optional setting, password-policy bounds, lock status across multiple servers, unlock partial failures, stats/debug structure copying, random key retrieval, and null-input robustness for utility functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.h

## Purpose
This public header defines the KAS admin API, including principal identities, encryption keys, principal metadata, KAS server statistics/debug structures, and function declarations for KAS database administration.

## Important APIs, Types, and Functions
- Constants define name/key lengths, principal flag externs, operation-name lengths, and key-cache debug capacity.
- `kas_identity_t`, `kas_encryptionKey_t`, and enums for admin/TGS/encryption/change-password/password-reuse settings model principal identity and policy.
- `kas_principalEntry_t` exposes principal flags, expiration/modification data, key version/key/checksum, password expiration, failed-login count, and lock time.
- `kas_serverStats_t`, `kas_serverProcStats_t`, `key_keyCacheItem_t`, and `kas_serverDebugInfo_t` expose KAS server telemetry and debug data.
- Function declarations cover server open/close, principal CRUD and iteration, key/password changes, lock status/unlock, field updates, stats/debug/random-key retrieval, string-to-key, and checksum.

## Control Flow and State
The header defines the caller contract for opaque server handles and iterator handles. Principal enumeration follows the standard begin/next/done pattern. Many field-set parameters are pointers so callers can update only selected attributes.

## Persistence and Side Effects
Declared functions can mutate KAS principals, keys, policy fields, and lock state. Stats/debug/key utility calls are mostly read-only but still perform RPC or cryptographic operations in the implementation.

## Dependencies and Integration Points
The header includes AFS base/admin types and `time.h`; Windows builds account for winsock include ordering. It is installed by `kas/Makefile.in` and consumed by admin clients, tests, and any application managing legacy OpenAFS KAS data.

## Risks
KAS is a legacy authentication service, and the API exposes raw fixed-size C buffers and key material. The many `extern const int` flag declarations require matching definitions elsewhere. Callers must observe fixed sizes and pointer-optional update semantics exactly.

## Test Signals
Compile-time ABI checks should verify structure sizes and header inclusion on Unix/Windows. API tests should validate selective field updates, iterator usage, and safe handling of maximum-length principal/instance/debug strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/pts/Makefile.in

## Purpose
This makefile builds and installs the PTS admin static library and public header.

## Important APIs, Types, and Functions
`ADMINOBJS` contains `afs_ptsAdmin.o`. `PTSERVEROBJS` adds generated protection-server RPC/XDR client objects `ptint.xdr.o` and `ptint.cs.o`. `libptsadmin.a` archives all three object groups. `all`, `install`, and `dest` install `afs_ptsAdmin.h` and the static archive. `clean` removes local objects and archives.

## Control Flow and State
The build compiles the local PTS admin implementation and generated ptserver sources from `../../ptserver`, archives them, indexes the archive, and copies artifacts to build or installation destinations.

## Persistence and Side Effects
Generated artifacts include local object files and `libptsadmin.a`; install/dest targets create include/lib directories and copy outputs. Clean deletes local generated files.

## Dependencies and Integration Points
The PTS admin archive depends on ptserver RPC/XDR sources. It is linked by cfg tests and other admin tooling that needs protection database operations. Client admin cell handles provide authenticated PTS ubik clients to the PTS implementation.

## Risks
Generated RPC source paths must remain valid relative to this directory. The object dependency `afs_ptsAdmin.o: afs_ptsAdmin.h` does not mention internal headers. Static library consumers need correct archive ordering with auth/rpc and ubik dependencies.

## Test Signals
Build signals include successful compilation of generated ptserver objects, creation/indexing of `libptsadmin.a`, correct install/dest placement, and downstream link success for cfg or PTS admin tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/Makefile.in -->
