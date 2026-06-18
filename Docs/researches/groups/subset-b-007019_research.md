# subset-b-007019 Research

Grouped source research for Coda file-server RPC procedures, callback tracking, shared vicedep contracts, and volume/vnode persistence helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/srvproc.cc -->
# sources/distributed-fs/coda/coda-src/vice/srvproc.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vice/srvproc.cc` implements the core Coda file-server operation helpers and several RPC entry points for object fetch, attribute lookup, batched validation, ACL retrieval, and ACL mutation. It is the server-side bridge between RPC2 request stubs, authentication/client state, volume/vnode locking, ACL and mode checks, SmartFTP side effects, callback invalidation, COP1/COP2 replicated update tracking, recoverable mutation logs, and final commit/abort of vnode/volume state.

## Important APIs, Types, and Functions

Public RPC handlers include `FS_ViceFetch`, `FS_ViceFetchPartial`, `FS_ViceGetAttr`, `FS_ViceGetAttrPlusSHA`, `FS_ViceValidateAttrs`, `FS_ViceValidateAttrsPlusSHA`, `FS_ViceGetACL`, and `FS_ViceSetACL`. Shared operation APIs exported through `operations.h` include `ValidateParms`, `AllocVnode`, `Check*Semantics` routines for fetch/getattr/ACL/store/setattr/create/remove/link/rename/mkdir/rmdir/symlink, `Perform*` routines for metadata mutation, `FetchBulkTransfer`, `StoreBulkTransfer`, and `PutObjects`. Local helpers include `GrabFsObj`, `GetFsoAndParent`, `NormalVCmp`, `CopyOnWrite`, `Check_CLMS_Semantics`, and `Check_RR_Semantics`.

## Control Flow

The file explicitly documents the common operation template: validate parameters, get objects, check semantics, perform the operation, then put objects. Read paths validate `RPCid` and piggybacked COP2 state with `ValidateParms`, translate replicated volume ids through `XlateVid`, lock the target and parent with `GetFsoAndParent` or `GetFsObj`, compute rights through ACLs, perform SmartFTP transfer if needed, fill `ViceStatus`, optionally add callbacks, and release objects with `PutObjects` without an RVM transaction. Mutation helpers run semantic version checks via a `VCP` comparator, enforce type/parent/name/permission constraints, mutate directory handles or vnode fields in VM/RVM-backed structures, break callbacks, schedule replicated COP pending entries, spool resolution log records when required, and rely on `PutObjects(..., TranFlag=1)` to commit or abort.

## State and Persistence Behavior

Persistent state is held in volume headers, vnode disk objects, directory data, inode containers, ACL blocks, version vectors, and resolution logs. `CopyOnWrite` materializes cloned directories or file inodes before mutation. `PerformStore`, `PerformSetAttr`, `PerformSetACL`, `Perform_CLMS`, `Perform_RR`, and `PerformRename` update vnode length, link count, parent fid, data version, author, owner, mode bits, unix mtime, and volume version vectors. `PutObjects` is the commit coordinator: on success it commits dirty directory pages, appends or aborts recoverable log records, writes changed/deleted vnodes, optionally updates the volume header, and only after the RVM transaction drops old or failed inodes. On error it reverses block accounting, aborts dirty directory state, flushes changed vnodes, drops newly created file inodes, and frees VLE/log record state.

## Dependencies and Integration Points

The implementation depends on RPC2/SmartFTP (`RPC2_InitSideEffect`, `RPC2_CheckSideEffect`), RVM transactions (`rvmlib_begin_transaction`, `rvmlib_end_transaction`), volume/vnode APIs (`GetVolObj`, `PutVolObj`, `VGetVnode`, `VPutVnode`, `VFlushVnode`), directory APIs (`VN_SetDirHandle`, `DH_Create`, `DH_Delete`, `DH_IsEmpty`), ACL/PRS APIs (`AL_CheckRights`, `AL_Internalize`, `AL_Externalize`), version-vector utilities, callback APIs (`CodaAddCallBack`, `CodaBreakCallBack`, `DeleteFile`), resolution logging (`rsle`, `SpoolVMLogRecord`, `TruncateLog`, `PurgeLog`), inode operations (`icreate`, `iopen`, `idec`, `ftruncate`), and global counters/timing from `srv.h`.

## Risks and Edge Cases

The code has high concurrency and recovery risk: lock order is partly explicit but rename ancestry traversal may use non-blocking vnode grabs to avoid deadlock; the code comments note known semantic concerns around rename overwriting directories and directory disk-usage accounting. `ValidateParms` applies piggybacked COP2 before mapping the client and volume, so failures there abort the main operation early. SHA generation is lazy and CPU-heavy and only covers files. Side-effect transfer byte counts are checked, but partial fetch uses unsigned/count sentinel logic and resumed fetch rejects version-vector changes with `EAGAIN`. `PutObjects` must coordinate RVM commits with inode reference changes in the right order; mistakes can leak or prematurely drop containers. Many hard failures are `CODA_ASSERT`, so malformed on-disk state or impossible invariants can terminate the server.

## Test Signals

Useful test signals include RPC smoke tests for fetch/getattr/getattr+SHA/validate attrs/get ACL/set ACL, permission matrix tests across system users, owners, anyuser rights, mode bits, and virgin files, version-vector mismatch tests for replicated and non-replicated operations, partial fetch resume tests, SmartFTP byte-count mismatch tests, callback add/break checks after reads and mutations, quota/disk accounting tests for create/remove/rename/COW/truncate, fault-injection around `PutObjects` error paths, and recovery/salvage tests that verify vnode, directory, inode, and resolution-log consistency after aborts and restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/srvproc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/srvproc2.cc -->
# sources/distributed-fs/coda/coda-src/vice/srvproc2.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vice/srvproc2.cc` implements secondary Coda file-server RPCs for connection lifecycle, volume discovery and status, root-volume configuration, server time probing, connection setup, and runtime statistics. It complements `srvproc.cc` by handling administrative and metadata/status operations rather than object data transfer.

## Important APIs, Types, and Functions

RPC handlers include `FS_ViceDisconnectFS`, `FS_TokenExpired`, `FS_ViceGetStatistics`, `FS_ViceGetVolumeInfo`, `FS_ViceGetVolumeLocation`, `FS_ViceGetVolumeStatus`, `FS_ViceSetVolumeStatus`, `FS_ViceGetRootVolume`, `FS_ViceSetRootVolume`, `FS_ViceGetTime`, `FS_ViceNewConnection`, and `FS_ViceNewConnectFS`. Helpers include `GetROOTVOLUME`, `SetVolumeStatus`, `PerformSetQuota`, `SetViceStats`, `SetRPCStats`, `SetVolumeStats`, `SetSystemStats`, platform-specific `SetSystemStats_linux`/`SetSystemStats_bsd44`, `GetEtherStats`, and `PrintVolumeStatus`.

## Control Flow

Connection RPCs map the `RPC2_Handle` to `ClientEntry`, lock the associated `HostTable`, and either delete the client, clean up an expired host, or build/validate callback connections. Volume info resolves root aliases through `db/ROOTVOLUME`, consults the VRDB for replicated volumes, falls back to `VGetVolumeInfo`, and normalizes type/group-id fields. Volume status fetches the root vnode, checks caller rights or system-user privilege, fills status/name/motd/offline buffers, and releases the vnode and volume. Set-volume-status validates buffers and client identity, obtains an exclusive volume lock, locks the root vnode, requires `SystemUser`, changes quota/name/motd/offline message fields, spools replicated quota log records, and commits through `PutObjects` with volume update enabled.

## State and Persistence Behavior

The file mutates client and host connection state, callback connection handles, volume header fields, and the `db/ROOTVOLUME` configuration file. `FS_ViceSetRootVolume` writes `ROOTVOLUME.new` and atomically renames it over `ROOTVOLUME`. `FS_ViceSetVolumeStatus` persists quota and text fields in the volume header and can add COP pending state for replicated quota updates. Statistics routines read transient counters, RPC2/SFTP packet counters, partition free-space lists, `getrusage`, and `/proc` or kernel memory depending on platform.

## Dependencies and Integration Points

It integrates with `CLIENT_Build`, `CLIENT_Delete`, `CLIENT_CleanUpHost`, `CLIENT_MakeCallBackConn`, RPC2 private pointers, VRDB/VLDB lookup, `VGetVolumeInfo`, `VGetVolumeLocation`, volume/vnode locking, ACL rights checks from `srvproc.cc`, `CodaBreakCallBack`, replicated update helpers (`NewCOP1Update`, `CopPendingMan`, `SpoolVMLogRecord`), `vice_config_path`, global server counters, partition lists, and RPC2/SFTP statistics globals.

## Risks and Edge Cases

`SetVolumeStatus` uses bounded byte-string buffers but some `strncpy` lengths are tied to the wrong bounded object in the offMsg/motd paths, so boundary tests are important. `FS_ViceSetRootVolume` leaves `ROOTVOLUME.new` behind on some write failures and uses `O_EXCL`, which can make retries fail until cleanup. `FS_ViceGetTime` performs callback-channel repair on a timing RPC, so callback connection failures can affect a low-level liveness path. Volume id translation and `IsReplicated` mismatches return generic errors. Statistics collection has wraparound comments and platform-specific parsers that can silently skip fields if `/proc` formats change.

## Test Signals

Exercise connection build/disconnect/token-expiry paths, callback reconnection through `ViceGetTime` and `ViceNewConnectFS`, root volume get/set including stale `.new` files and permission failures, volume info lookup by name/id/root alias/replicated id, volume status buffer-size checks, set-volume-status authorization and replicated quota logging, and statistics output under empty, multi-partition, and Linux `/proc` parser scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/srvproc2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/timecalls.h -->
# sources/distributed-fs/coda/coda-src/vice/timecalls.h

## Purpose

`sources/distributed-fs/coda/coda-src/vice/timecalls.h` defines optional fine-grained timing macros for Coda server operations, including support for a platform-specific NSC hardware/software counter accessed through an ioctl-like device and fallback wall-clock timing.

## Important APIs, Types, and Functions

The header declares `clockFD` and histogram objects for create/remove/link/rename/mkdir/rmdir/symlink, log spooling, and `PutObjects` phases. It defines `NSC_SHOW_COUNTER_INFO`, `NSC_GET_COUNTER`, `START_NSC_TIMING(id)`, and `END_NSC_TIMING(id)`.

## Control Flow

When `_TIMECALLS_` is defined, `START_NSC_TIMING` starts normal `START_TIMING`, captures either `NSC_GET_COUNTER` or `gettimeofday`, and `END_NSC_TIMING` computes elapsed time, handles counter wrap, and updates `id_hg`. Without `_TIMECALLS_`, the macros collapse to the normal `START_TIMING`/`END_TIMING` instrumentation.

## State and Persistence Behavior

The file owns no persistent data. It mutates histogram accumulators and reads `clockFD`. Timing state is macro-local and transient; histogram state lives in the instrumentation module that defines the declared `hgram` globals.

## Dependencies and Integration Points

It depends on `histo.h`-style `struct hgram` declarations, `UpdateHisto`, `START_TIMING`, `END_TIMING`, system `ioctl`, `gettimeofday`, and Mach headers. `srvproc.cc` uses these macros around `PutObjects` phases when timing builds are enabled.

## Risks and Edge Cases

The macros declare local variables by token-pasting the timing id, so they must be used in scopes where repeated ids do not collide. The counter wrap constant and division by 25 are platform-specific. The header uses old-style preprocessor comments on `#else __STDC__`/`#endif __cplusplus`, which may warn on modern compilers.

## Test Signals

Compile both with and without `_TIMECALLS_`; run a timing-enabled server and verify histogram updates for `PutObjects` and mutation operations; test fallback behavior when `clockFD <= 0`; and build on modern compilers with warnings enabled to catch stale preprocessor syntax issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/timecalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/vice.private.h -->
# sources/distributed-fs/coda/coda-src/vice/vice.private.h

## Purpose

`sources/distributed-fs/coda/coda-src/vice/vice.private.h` is a private server header collecting cross-file prototypes for client/host table management, callback management, error formatting, logging, reintegration retry behavior, and RPC timeout selection.

## Important APIs, Types, and Functions

It declares `CLIENT_InitHostTable`, `CLIENT_Build`, `CLIENT_Delete`, `CLIENT_CleanUpHost`, `CLIENT_GetWorkStats`, `CLIENT_PrintClients`, `CLIENT_CallBackCheck`, `CLIENT_MakeCallBackConn`, `ViceErrorMsg`, `Die`, `GetEtherStats`, `InitCallBack`, `ViceLog`, `DeleteCallBack`, `BreakCallBack`, `DeleteVenus`, `DeleteFile`, `check_reintegration_retry`, and `srv_rpc2_timeout`.

## Control Flow

There is no executable control flow. The header provides compile-time linkage between server modules such as `srvproc2.cc`, callback code, connection-management code, and RPC timeout logic.

## State and Persistence Behavior

No storage is defined here except external references. The declared functions manipulate in-memory client/host/callback state and server retry policy in their implementation files.

## Dependencies and Integration Points

The prototypes depend on `RPC2_Handle`, `RPC2_Integer`, `SecretToken`, `ClientEntry`, `HostTable`, `ViceFid`, and `struct timeval`, which are supplied by the surrounding server headers. It is included by files that need private server internals without exposing them as public Coda client ABI.

## Risks and Edge Cases

There is no include guard, and `InitCallBack` is declared twice. This works only because prototypes are identical, but future signature changes can drift. The variadic `ViceLog(int...)` declaration is nonstandard-looking and relies on compiler compatibility.

## Test Signals

Compile all server translation units with warnings enabled, especially duplicate declarations and C/C++ linkage checks; exercise client build/delete/cleanup and callback teardown paths that consume these prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/vice.private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/vicecb.cc -->
# sources/distributed-fs/coda/coda-src/vice/vicecb.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vice/vicecb.cc` implements the file server's in-memory callback promise table. It records which Venus clients have callbacks for individual fids or whole volumes, sends callback breaks over RPC2 multi-RPC, deletes callback promises when clients disconnect or files disappear, and provides debug/statistical dumps.

## Important APIs, Types, and Functions

Private types are `FileEntry`, `FEBlock`, `CallBackEntry`, `CBEBlock`, and `CBStat`. Public functions include `InitCallBack`, `AddCallBack`, `BreakCallBack`, `DeleteCallBack`, `DeleteVenus`, `DeleteFile`, `CodaAddCallBack`, `CodaBreakCallBack`, `CodaDeleteCallBack`, `PrintCallBackState`, and `PrintCallBacks`. Internal helpers include `VHash`, `GetFEBlock`, `GetFE`, `FreeFE`, `FindEntry`, `DeleteFileStruct`, `GetCBEBlock`, `GetCBE`, `FreeCBE`, `SDeleteCallBack`, `order_helist`, and callback dump helpers.

## Control Flow

Callbacks are keyed by fid in a 256-bucket hash table. `AddCallBack` creates a `FileEntry` if necessary, avoids adding duplicates for the same host, and allocates a `CallBackEntry`. `BreakCallBack` locks the file entry, revalidates it after acquiring the lock, sorts target `HostTable` entries by callback connection id for lock ordering, sends `CallBack_OP` with `MRPC_MakeMulti`, cleans up failed hosts, removes volume callbacks when a file callback breaks, and then removes all non-exempt callback entries. Delete paths either remove a single client's callback, all callbacks for a host, or all callback state for a fid. `Coda*` wrappers translate between replica fids and replicated-group fids and also handle volume-level callbacks.

## State and Persistence Behavior

All callback state is transient server memory: `hashTable`, `FEFree`, `CBEFree`, and counters (`CBEs`, `CBEBlocks`, `FEs`, `FEBlocks`, `VEs`, `VCBEs`). There is no disk persistence; callbacks are rebuilt by clients after reconnect/revalidation. Free-list block allocation uses `malloc` and never returns blocks to the system, only to internal free lists.

## Dependencies and Integration Points

The file integrates with `HostTable` locks from `srv.h`, RPC2 callback stubs (`CallBack_OP`, `CallBack_PTR`, `MRPC_MakeMulti`), `srv_rpc2_timeout`, `CLIENT_CleanUpHost`, VRDB volume translation (`XlateVid`, `ReverseXlateVid`), logging, histograms for debug output, and server object mutation paths that call `CodaBreakCallBack`/`DeleteFile` before or after changes.

## Risks and Edge Cases

Concurrency is delicate. The source comments document a race where a second callback breaker may hold a pointer to a `FileEntry` already returned to the free list; the code re-finds the entry after acquiring its lock to reduce this. `SDeleteCallBack` marks callback entries as dead if the file entry is busy, delaying actual free. `BreakCallBack` allocates arrays sized by `tf->users`, so corrupted counts can cause bad allocations. Volume callbacks use fids with vnode and unique zero, which must not be confused with invalid object fids. Failed callback RPCs trigger host cleanup while host locks are held.

## Test Signals

Run callback set/break/delete tests for file and volume callbacks, same-client exemption on mutation, replicated and non-replicated fid translation, client disconnect cleanup, failed callback connection cleanup, concurrent add/break/delete stress tests, and debug dump consistency checks comparing counted CBEs/FEs with active counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/vicecb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/Makefile.am -->
# sources/distributed-fs/coda/coda-src/vicedep/Makefile.am

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/Makefile.am` defines the automake build for generated RPC2 dependency libraries shared by Venus, the file server, and volume utilities.

## Important APIs, Types, and Functions

It declares `libvenusdep.la` unconditionally and `libvicedep.la`/`libvolutildep.la` under `BUILD_SERVER`. It publishes `operations.h`, `recov_vollog.h`, `srv.h`, `venusioctl.h`, and `voltypes.h` as local headers. `RPC2_FILES` lists `callback.rpc2`, `cml.rpc2`, `mond.rpc2`, `res.rpc2`, `vcrcommon.rpc2`, `vice.rpc2`, `voldump.rpc2`, and `volutil.rpc2`, with generated client/server/multi/helper C sources assigned to the noinst libraries.

## Control Flow

There is no runtime control flow. At build time it includes `configs/rpc2_rules.mk`, which generates RPC2 stubs and helpers; automake then compiles the appropriate generated sources into private libraries for the selected build configuration.

## State and Persistence Behavior

No runtime state is owned here. The file controls generated build artifacts in the build tree and determines which generated protocol interfaces are linked into clients/server utilities.

## Dependencies and Integration Points

It depends on automake/libtool, the repository RPC2 generation rules, `$(RPC2_CFLAGS)`, and build-conditional `BUILD_SERVER`. It is the build integration point for the headers and generated stubs consumed by `vice`, `vol`, Venus, and volutil code.

## Risks and Edge Cases

Generated `nodist_*` sources must match the `.rpc2` files and include paths; missing regeneration can cause stale protocol stubs. Server-only libraries disappear when `BUILD_SERVER` is false, so consumers must be correctly guarded. Long source lists are easy to drift when adding an RPC interface.

## Test Signals

Run autoreconf/configure and both server-enabled and client-only builds; verify generated RPC2 files exist, the noinst libraries contain expected stubs, and incremental rebuilds happen when `.rpc2` files change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/operations.h -->
# sources/distributed-fs/coda/coda-src/vicedep/operations.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/operations.h` is the shared declaration header for file-server operation validation, semantic checks, data-transfer helpers, metadata mutation helpers, quota updates, and object release/commit coordination.

## Important APIs, Types, and Functions

It defines `typedef int (*VCP)(int, VnodeType, void *, void *)` for version comparison callbacks. It declares `ValidateParms`, `AllocVnode`, all `Check*Semantics` routines, `PerformFetch`, `FetchBulkTransfer`, `PerformGetAttr`, `PerformGetACL`, `PerformStore`, `StoreBulkTransfer`, `PerformSetAttr`, `PerformSetACL`, `PerformCreate`, `PerformRemove`, `PerformLink`, `PerformRename`, `PerformMkdir`, `PerformRmdir`, `PerformSymlink`, `PerformSetQuota`, `PutObjects`, and `SpoolRenameLogRecord`.

## Control Flow

The header mirrors the server operation pipeline: parameter validation, object allocation/locking, semantic checks, transfer or mutation, and final release. Callers in RPC stubs and resolution/reintegration code compose these functions according to the operation being executed.

## State and Persistence Behavior

The header itself has no state. Its declared functions mutate vnode/volume/directory/inode state, adjust quotas, schedule replicated COP state, and commit/abort changes through `PutObjects`.

## Dependencies and Integration Points

It depends on server types such as `RPC2_Handle`, `ClientEntry`, `Volume`, `Vnode`, `ViceFid`, `ViceVersionVector`, `Rights`, `AL_AccessList`, `dlist`, `vle`, `DirInode`, and transaction annotations. It is included by `srvproc.cc`, `srvproc2.cc`, generated server code, and conflict-resolution modules that need to reuse normal server semantics.

## Risks and Edge Cases

The prototypes encode many raw pointers, optional defaults, and output parameters; argument-order drift between declarations and definitions would be severe. The `VCP` callback receives untyped `void *` version arguments, so callers must pass the correct object for replicated vs non-replicated operations. Some defaults suppress protection checks or target-nonempty checks, which is powerful for repair/resolution but risky if exposed accidentally.

## Test Signals

Compile with strict prototype checking; exercise each declared check/perform pair through both client RPCs and resolution code; add ABI-style tests for expected error returns when version comparison, protection, type, or directory integrity checks fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/operations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/recov_vollog.h -->
# sources/distributed-fs/coda/coda-src/vicedep/recov_vollog.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/recov_vollog.h` declares the recoverable volume log used by Coda resolution. The log lives partly in RVM and partly in VM and records directory mutation history for reintegration, resolution, salvage, truncation, and wrap-around management.

## Important APIs, Types, and Functions

The central type is `class recov_vol_log`, with recoverable fields such as version, allocation flags, administrative size limits, block index, recoverable in-use bitmap, recoverable max sequence number, wrap-around vnode/unique/index, and transient fields such as active count, VM in-use bitmap, max sequence number, and `resstats`. Public methods include custom RVM allocation/deallocation, constructor/destructor, `init`, `ResetTransients`, `Increase_Admin_Limit`, `AllocRecord`, `DeallocRecord`, `AllocViaWrapAround`, `RecovPutRecord`, `RecovFreeRecord`, `bmsize`, `LogSize`, `purge`, `SalvageLog`, and print variants. Exported helpers are `CreateRootLog` and `CreateResLog`.

## Control Flow

Callers allocate VM log slots with `AllocRecord` or reuse slots through `AllocViaWrapAround`, then commit records to recoverable storage with `RecovPutRecord`. RVM-only methods grow/free blocks, advance recoverable sequence numbers, purge logs, and salvage allocation bitmaps. Directory vnode writeback in `cvnode.cc` creates logs when needed, while `srvproc.cc` appends, aborts, truncates, or purges records during `PutObjects`.

## State and Persistence Behavior

The class explicitly separates recoverable RVM state from transient VM state. Recoverable fields survive server restart; `ResetTransients` reconstructs VM bookkeeping. The in-use bitmaps track allocated log entries; admin limits cap log size; wrap-around fields record where old entries can be overwritten after bounded attempts.

## Dependencies and Integration Points

It depends on `bitmap`, resolution record types from `res.h`, `cvnode.h`, `volume.h`, `VolumeDiskData`, `Vnode`, `Volume`, `dlist`, and transaction annotations. Friends such as `RS_LockAndFetch`, `DumpLog`, and `DumpVolDiskData` access internals for resolution fetch and dump utilities.

## Risks and Edge Cases

Recoverable layout changes are high risk because the class stores persistent RVM data. Sequence-number growth, wrap-around selection, and bitmap synchronization between RVM and VM must remain consistent after crashes. Admin-limit growth must happen in a transaction. Friend access broadens the mutation surface and can bypass invariants.

## Test Signals

Test log creation for root and directory vnodes, record allocation/free and sequence growth, admin-limit expansion, wrap-around behavior under a full log, crash/restart `ResetTransients`, salvage bitmap repair, purge/truncate through `PutObjects`, and dump/fetch consumers reading expected records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/recov_vollog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/srv.h -->
# sources/distributed-fs/coda/coda-src/vicedep/srv.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/srv.h` is the main private/public server dependency header for Coda file-server modules. It defines core server macros, client and host connection structures, operation counters, timing helpers, and cross-module prototypes for volume, vnode, callback, RPC, and resolution services.

## Important APIs, Types, and Functions

Key macros include `ThisHostAddr`, `VolToHostAddr`, `VolToServerId`, `ISDIR`, `VSLEEP`, `STREQ`, `STRNEQ`, `SetAccessList`, operation counter aliases, data-size buckets, `START_TIMING`, and `END_TIMING`. Types include `HostTable` and `ClientEntry`. It declares server globals (`HostAddress`, `ThisServerId`, `SystemId`, `AnyUserId`, `SrvDebugLevel`, `StartTime`, `CurrentConnections`, `Authenticate`, `Counters`, `NullFid`, `MaxVols`, `CodaSrvIp`, etc.) and many APIs from codaproc, codaproc2, srv, srvproc2, vicecb, resolution, lookaside, coppend, and volutil.

## Control Flow

There is no executable control flow, but the macros shape runtime flow: `SetAccessList` asserts directory vnodes before returning ACL storage, timing macros wrap operations under `CODA_DEBUG`, and counter IDs are used by RPC dispatch/statistics paths. The declared functions define the flow between RPC handlers, volume/vnode acquisition, version-vector updates, callback breaks, and resolution support.

## State and Persistence Behavior

The header declares in-memory server connection structures and globals. Persistent state is accessed through declared volume/vnode helpers rather than stored in this header. `HostTable` tracks callback connection handles, host address/port, activity timestamps, and synchronization lock; `ClientEntry` tracks RPC connection, CPS/authentication, user id, side-effect type, last op, unbind state, username, and token expiration.

## Dependencies and Integration Points

It integrates RPC2, LWP locks, PRS/auth, Coda wire types, vnode/volume types, and deprecation annotations. Most Coda server translation units include it to share connection structures, counters, callbacks, resolution hooks, and object-management APIs.

## Risks and Edge Cases

Global mutable state and macros make coupling tight. `SetAccessList` assumes a directory vnode and asserts otherwise, so callers must fetch the correct parent/target object. Operation counter aliases depend on generated `srvOPARRAYSIZE` and RPC opcode names. `HostAddress` is marked single-homing-sensitive. `ClientEntry` stores fixed-size usernames and timestamps; connection cleanup must hold the `HostTable` lock consistently.

## Test Signals

Compile all server modules after generated RPC headers are refreshed; run connection lifecycle and callback tests that exercise `HostTable` locking; verify statistics counters map to expected opcodes; test ACL callers with non-directory objects to confirm semantic checks prevent macro assertion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/srv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/venusioctl.h -->
# sources/distributed-fs/coda/coda-src/vicedep/venusioctl.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/venusioctl.h` defines Venus-specific ioctl and pioctl command numbers used by Coda user tools, Venus cache manager code, and kernel interfaces.

## Important APIs, Types, and Functions

The file defines `CFS_PIOBUFSIZE`, file-descriptor ioctls such as `_VIOCCLOSEWAIT`, `_VIOCABORT`, and `_VIOCIGETCELL`, legacy and current pioctl command constants for ACLs, tokens, volume status, flushing, prefetch, group access, repair, hoard database, reintegration, mount points, write-disconnect, ASR, local/global repair, cache listing, kernel unload, and zone limits. It also defines consolidated repair command subcodes `REP_CMD_*`.

## Control Flow

There is no runtime code. Callers wrap the numeric `_VIOC*` constants with the platform pioctl/ioctl encoding macros and pass optional data buffers no larger than `CFS_PIOBUFSIZE`.

## State and Persistence Behavior

No state is owned. The constants select operations that may mutate Venus cache state, tokens, volume status, repair sessions, hoard database entries, mutation logs, or kernel/cache-manager behavior in the receiving subsystem.

## Dependencies and Integration Points

It includes `pioctl.h` and is shared by Venus, command-line tools, and kernel/user ABI code. The command numbers are ABI-facing and must stay synchronized with implementations in Venus and tools such as `cfs` and repair utilities.

## Risks and Edge Cases

The header documents ioctl-number wrap/collision risk because the `nr` component is 8-bit. Legacy repair commands are kept for compatibility while `_VIOC_REP_CMD` consolidates repair operations. Reusing or renumbering constants can break old tools or collide with low numbers.

## Test Signals

Build Venus and user tools together; run pioctl smoke tests for ACL/token/status/flush/repair commands; verify command numbers remain under the 8-bit limit; test backward compatibility for old repair commands and the consolidated `REP_CMD` interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/venusioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/voltypes.h -->
# sources/distributed-fs/coda/coda-src/vicedep/voltypes.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/voltypes.h` provides small fixed-width type aliases and boolean/null compatibility definitions used by the Coda volume and server code.

## Important APIs, Types, and Functions

It defines `NULL`, `TRUE`, and `FALSE` if absent, includes RPC2 and `stdint.h`, and aliases `bit32`, `bit16`, `byte`, `Device`, `Inode`, and `Error`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The header owns no state, but its aliases are used in persistent volume/vnode structures and inode identifiers. `Device`, `Inode`, and `Error` are 32-bit values here, which constrains ABI and on-disk/RVM layout expectations.

## Dependencies and Integration Points

It is included throughout `vicedep`, `vice`, and `vol` code to stabilize integer types across platforms and generated RPC2 bindings.

## Risks and Edge Cases

The 32-bit `Device` and `Inode` aliases can be risky on platforms with wider native device or inode numbers. Redefining `NULL`/boolean constants may conflict with C++ or modern headers if include ordering changes.

## Test Signals

Compile on 32-bit and 64-bit platforms; add layout/size assertions for persistent structures that use these aliases; run inode/device integration tests on filesystems with large inode numbers if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vicedep/voltypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/Makefile.am -->
# sources/distributed-fs/coda/coda-src/vol/Makefile.am

## Purpose

`sources/distributed-fs/coda/coda-src/vol/Makefile.am` defines the automake build for the Coda volume package library, which is compiled when `BUILD_SERVER` is enabled.

## Important APIs, Types, and Functions

It builds `libvol.la` from directory vnode, cached vnode, volume, utility, VLDB, fssync, index, recovery, volume hash, dump, VRDB, vlist, lock queue, allocation, debug, lock, tree-remove, globals, definitions, resolution, and structure sources/headers. It installs/distributes the `vrdb.5` man page under server builds and includes `testvrdb.cc` as extra distribution content.

## Control Flow

There is no runtime flow. Build-time flow is controlled by `BUILD_SERVER`; when enabled, automake compiles the volume package with RVM/RPC2 flags and include paths for base, kerndep, util, vicedep, dir, ACL, partition, auth2, version-vector, and lookaside modules.

## State and Persistence Behavior

No runtime state is stored here. The file determines which implementation files participate in the volume package that manages persistent volume headers, vnode indexes, RVM recovery, volume hash tables, and related server state.

## Dependencies and Integration Points

It depends on `$(RVM_RPC2_CFLAGS)`, source and build directories for generated `vicedep`/`auth2` headers, and server-only build configuration. It integrates the volume package into the broader server build.

## Risks and Edge Cases

Omitting a source/header from `libvol_la_SOURCES` can break distribution tarballs or incremental builds even if local includes happen to work. Build order depends on generated headers in `coda-src/vicedep` and `auth2`. Client-only builds must not accidentally reference `libvol.la`.

## Test Signals

Run server-enabled configure/build, distribution checks, and clean-tree rebuilds; verify generated include directories exist before compiling volume sources; run volume package unit/smoke tests such as VRDB tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/camprivate.h -->
# sources/distributed-fs/coda/coda-src/vol/camprivate.h

## Purpose

`sources/distributed-fs/coda/coda-src/vol/camprivate.h` declares private Camelot/RVM storage layout structures for the Coda volume package.

## Important APIs, Types, and Functions

It defines `struct VolumeData`, containing a `VolumeDiskData *`, arrays/lists for small and large vnode lists, counts of allocated vnodes and vnode lists, and reserved fields. It also defines `struct VolHead`, combining a `VolumeHeader` with `VolumeData`.

## Control Flow

There is no executable flow. The structures are consumed by recovery/storage code to navigate top-level volume metadata in recoverable storage.

## State and Persistence Behavior

These structures describe persistent RVM/Camelot state. `VolumeData` points to volume disk metadata and recoverable vnode-list arrays. Reserved fields protect future layout growth if fields are inserted before the reserved tail and the reserved count is reduced.

## Dependencies and Integration Points

The header includes `rec_smolist.h` and depends on `VolumeDiskData`, `VolumeHeader`, `bit32`, and vnode-list types from the volume package. It is used by low-level recovery/index code rather than high-level RPC handlers.

## Risks and Edge Cases

Because this is a persistent layout contract, reordering or resizing fields can break existing recoverable storage. Pointer fields are meaningful inside the RVM segment and require correct recovery/remapping. Reserved capacity must be managed carefully during migrations.

## Test Signals

Run recovery initialization and salvage tests against existing RVM segments; add structure-size/layout checks for migration-sensitive builds; verify volume attach/detach and vnode-list traversal after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/camprivate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/clone.cc -->
# sources/distributed-fs/coda/coda-src/vol/clone.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vol/clone.cc` implements volume cloning for the Coda volume package. It copies large and small vnode indexes from an original volume to a new clone, updates inode reference counts, marks writable original directories as cloned for copy-on-write, and removes an older backup clone if supplied.

## Important APIs, Types, and Functions

Public API: `CloneVolume(Error *error, Volume *original, Volume *newv, Volume *old)`. Private helpers: `CloneIndex(Volume *ovp, Volume *cvp, Volume *dvp, VnodeClass vclass)` and `FinalDelete(Volume *vp)`.

## Control Flow

`CloneVolume` initializes the error, clones both `vLarge` and `vSmall` indexes, copies the original volume header to the new volume, and finally deletes/detaches the old backup. `CloneIndex` iterates the original index, optionally reads the corresponding old-backup vnode at the same offset, increments inode refs for containers shared with the new clone, decrements inode refs no longer referenced by the old backup, marks writable original directory vnodes cloned and bumps their data version before writing them back, then writes the vnode image into the clone index. A second pass over the old backup decrements remaining vnode inodes.

## State and Persistence Behavior

The file mutates vnode indexes and inode reference counts on disk/RVM. Writable original directories get `cloned = 1` and `dataVersion++` so later copy-on-write creates newer directory containers and salvage can reason about data versions. The clone receives a clean copy with the clone flag cleared and data version restored. `FinalDelete` removes the old backup volume metadata and detaches the volume object.

## Dependencies and Integration Points

It depends on `vindex`, `vindex_iterator`, `VnodeClassInfo`, `VolumeWriteable`, `CopyVolumeHeader`, inode refcount APIs (`iinc`, `idec`), `DeleteVolume`, `VDetachVolume`, volume/vnode structures, and partition/device ids. It integrates with later `CopyOnWrite` logic in server mutation paths.

## Risks and Edge Cases

The code assumes same-offset correspondence between original and old backup indexes and asserts heavily on inode and index operations. It reads `VnodeClassInfo[vclass]`, while nearby code uses `VnodeClassInfo_Array`, so build-time symbol compatibility matters. Directory clone data-version handling is subtle and explicitly called important for salvage. The second old-backup pass can double-decrement if index correspondence assumptions are wrong.

## Test Signals

Test cloning writable and readonly volumes, cloning with and without an old backup, directory copy-on-write after clone, inode reference counts before and after clone deletion, salvage after interrupted clone/COW, and both small and large vnode classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/clone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/coda_globals.h -->
# sources/distributed-fs/coda/coda-src/vol/coda_globals.h

## Purpose

`sources/distributed-fs/coda/coda-src/vol/coda_globals.h` declares global constants and the top-level recoverable segment layout for the Coda file server's volume storage.

## Important APIs, Types, and Functions

It defines `MAXVOLS`, `LARGEFREESIZE`, `SMALLFREESIZE`, `LARGEGROWSIZE`, `SMALLGROWSIZE`, `bool_t`, `struct camlib_recoverable_segment`, external `camlibRecoverableSegment`, and the `SRV_RVM(name)` accessor macro.

## Control Flow

There is no runtime flow. Code accesses fields in the recoverable segment through `SRV_RVM`.

## State and Persistence Behavior

`camlib_recoverable_segment` is recoverable global state: initialization flag, fixed `VolumeList[MAXVOLS]`, small/large vnode free lists and indices, maximum allocated volume id, reserved space, and dummy padding. This structure anchors all volume headers and vnode free-list state in RVM.

## Dependencies and Integration Points

It depends on `VolHead`, `VnodeDiskObject`, and `VolumeId` from volume headers. Recovery, volume allocation, and vnode allocation code use `camlibRecoverableSegment` and `SRV_RVM` to address persistent server state.

## Risks and Edge Cases

`MAXVOLS` is fixed at 1024 and must remain a power of two. The recoverable segment layout is persistent; field changes require migration. Free-list sizes scale from `MAXVOLS`, so changing capacity affects memory/RVM layout. The macro trusts `camlibRecoverableSegment` is initialized and correctly mapped.

## Test Signals

Run fresh RVM initialization, restart recovery, volume allocation up to capacity boundaries, free-list depletion/growth tests, and layout/migration checks for any change to the segment structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/coda_globals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/cvnode.cc -->
# sources/distributed-fs/coda/coda-src/vol/cvnode.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vol/cvnode.cc` implements the Coda volume package's cached vnode layer. It manages in-memory vnode caches for small and large vnode classes, hash/LRU indexing, fid allocation, vnode allocation, vnode retrieval/locking, writeback to recoverable indexes, abort/flush behavior, and fid conversion helpers.

## Important APIs, Types, and Functions

Global state includes `VnodeClassInfo_Array[nVNODECLASSES]` and a 256-bucket `VnodeHashTable`. Public functions include `VolumeHashOffset`, `VInitVnodes`, `VAllocFid` overloads, `VAllocVnode` overloads, `VGetVnode`, `VPutVnode`, `VFlushVnode`, `VN_VN2Fid`, and `VN_VN2PFid`. Private helpers include `GrowVnLRUCache`, `VAllocVnodeCommon`, `moveHash`, and `StickOnLruChain`.

## Control Flow

Initialization creates circular LRU lists for each vnode class. Allocation first reserves fid bits and uniquifiers, grows RVM vnode arrays if needed, verifies no object already exists in RVM or VM, takes a vnode from the LRU tail, moves it to the target hash bucket, initializes disk and in-memory fields, removes it from LRU, and write-locks it. `VGetVnode` validates volume and lock mode, looks up the hash table, reads from the recoverable index on cache miss, validates magic/type/inconsistency/barren flags, removes the first user from LRU, obtains read or write lock, and bumps volume usage. `VPutVnode` writes dirty/deleted write-locked vnodes to the index, creates resolution logs for directories when enabled, updates volume timestamps, frees bitmap entries for fully deleted vnodes, returns the last user to LRU, and releases locks. `VFlushVnode` aborts a write by rereading the disk object or making the VM entry unreachable.

## State and Persistence Behavior

VM state consists of hash chains, circular LRU lists, lock state, user counts, cached vnode disk objects, dirty/delete flags, writer identity, directory handles, and cache checks. Persistent state is stored through `vindex` into recoverable vnode arrays and volume bitmaps/uniquifiers. `VAllocFid` advances transient and recoverable uniquifier counters and updates the volume header transactionally when extending beyond the RVM counter. `VPutVnode` is the normal path for persisting vnode changes; `VFlushVnode` is the rollback path.

## Dependencies and Integration Points

The file depends on LWP locks, RVM transactions, `vindex`, volume headers, recovery/log APIs (`CreateResLog`), vnode bitmap allocation/free helpers, volume online/writeability checks, directory handle cleanup, `VAddToVolumeUpdateList`, `VBumpVolumeUsage`, and global vnode cache sizing variables `large` and `small`. Server operation code obtains and releases objects through this layer.

## Risks and Edge Cases

Correctness relies on `nUsers`, LRU membership, hash membership, `cacheCheck`, and lock ownership staying synchronized. The cache dynamically grows if only one LRU entry remains, but memory pressure is not otherwise bounded. `VGetVnode` can return `EINCONS`, `EIO`, `VREADONLY`, `VOFFLINE`, `VSALVAGE`, or `EWOULDBLOCK` depending on state and lock mode. `VFlushVnode` has a subtle path that zeroes vnode identifiers before checking `IsEmpty`, which deserves scrutiny. Persistent magic mismatch forces volume offline/salvage.

## Test Signals

Test cache initialization and growth, hash distribution through `VolumeHashOffset`, fid range allocation and uniquifier extension, duplicate allocation detection, read/write/try-lock behavior, inconsistent and barren vnode rejection, dirty writeback, delete bitmap free, abort reread with `VFlushVnode`, resolution log creation for directories, and stress tests with concurrent vnode users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/cvnode.cc -->
