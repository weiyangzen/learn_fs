# Research: subset-b-007824

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vsprocs.c -->
# sources/distributed-fs/openafs/src/volser/vsprocs.c

## Purpose

`vsprocs.c` is the high-level client-side implementation behind many `vos`/volume-server operations in OpenAFS. It coordinates VLDB metadata updates through the global ubik VLDB client `cstruct`, volume-server RPCs over Rx connections, volume transactions, dump/restore streaming, replica release, server/partition inventory, and repair/synchronization of VLDB entries against real volume-server state. It is not a daemon and does not persist local state itself; its durable effects are remote: volume headers/data on file servers and VLDB entries/locks in the VLDB service.

## Important APIs, Types, and Functions

- Global controls: `verbose` and `noresolve` alter operator output; static `uvclass`/`uvindex` are the Rx security class/index installed by `UV_SetSecurity`; `cstruct` is the shared ubik VLDB client imported from `vsutils.c`.
- Error/output helpers: `PrintError`, `EPRINT*`, `EGOTO*`, `VPRINT*`, and `VDONE` centralize volserver/VLDB/Rx diagnostics and the file’s goto-based cleanup style.
- Byte-order helpers: `MapNetworkToHost` copies an `nvldbentry` while converting server addresses from network to host order for VLDB XDR calls; `MapHostToNetwork` converts in-place to network order for local logic and display helpers.
- Connection/transaction helpers: `UV_Bind` creates Rx connections to volserver `VOLSERVICE_ID`; `AFSVolCreateVolume_retry` and `AFSVolTransCreate_retry` retry `VOLSERVOLBUSY` up to three times; `DoVolDelete`, `DoVolClone`, `ListOneVolume`, `VolumeExists`, `GetTrans`, `CheckTrans`, and `PutTrans` encapsulate common volserver transaction lifecycles.
- VLDB lock helper: `GetLockedEntry` calls `ubik_VL_SetLock`, then fetches the entry and converts it for local use. It deliberately tolerates `VL_RERELEASE` for release recovery.
- CRUD and movement APIs: `UV_CreateVolume*`, `UV_DeleteVolume`, `UV_NukeVolume`, `UV_MoveVolume*`, `UV_CopyVolume*`, `UV_BackupVolume`, `UV_CloneVolume`, and `UV_ConvertRO`.
- Release APIs: `UV_ReleaseVolume`, `GetTrans`, `SimulateForwardMultiple`, `CheckTrans`, and `PutTrans` implement the read-only replica release pipeline.
- Dump/restore APIs: `UV_DumpVolume`, `UV_DumpClonedVolume`, `UV_RestoreVolume*`, and `UV_GetSize` drive Rx call streaming via caller-supplied dump/write callbacks.
- Site/VLDB manipulation APIs: `UV_AddSite*`, `UV_RemoveSite`, `UV_ChangeLocation`, `UV_LockRelease`, `UV_RenameVolume`.
- Inventory and repair APIs: `UV_ListPartitions`, `UV_ListVolumes`, `UV_XListVolumes`, `UV_ListOneVolume`, `UV_XListOneVolume`, `UV_SyncVolume`, `UV_SyncVldb`, `UV_SyncServer`, `CheckVolume*`, and `CheckVldb*`.
- Maintenance APIs: `UV_PartitionInfo64`, `UV_VolserStatus`, `UV_VolumeZap`, `UV_SetVolume`, and `UV_SetVolumeInfo`.

## Control Flow

Most exported operations follow the same sequence: bind to one or more volume servers with `UV_Bind`, optionally lock the VLDB entry with `GetLockedEntry`, start one or more volume transactions with `AFSVolTransCreate_retry` or create volumes with `AFSVolCreateVolume(_retry)`, mutate volume state with `AFSVol*` RPCs, update VLDB entries via the wrapper functions from `vsutils.c`, end all transactions, release VLDB locks, destroy Rx connections, and report the first meaningful error.

Creation (`UV_CreateVolume3`) allocates or validates RW/RO/BK ids, creates the RW volume, sets quota and online flags, creates the VLDB entry, then ends the transaction. If VLDB creation fails after volume creation, it tries to delete the created volume before returning the VLDB error.

Deletion (`UV_DeleteVolume`) locks/fetches the VLDB entry if present, deletes the on-disk target via `DoVolDelete`, then either clears BK/RO/RW flags and site records or deletes the entire VLDB entry if no useful references remain. Missing-on-disk and missing-in-VLDB conditions are tracked separately so `vos delete` can warn while still completing whichever side can be fixed.

Move/copy are multi-phase operations. `UV_MoveVolume2` verifies the source is the RW site, creates an optional local clone, creates the destination volume, forwards a full or incremental dump through `AFSVolForward`, brings the destination online, updates the VLDB RW site, then deletes the old source/backup/temp clone. `UV_CopyVolume2` uses similar clone/forward logic but creates a new volume and optionally a new VLDB entry instead of changing the source entry. Both use `setjmp`/signal recovery; interruption enters cleanup that ends transactions, restores source flags where possible, deletes temporary volumes, and prints a manual verification warning.

Release (`UV_ReleaseVolume`) is the most complex path. It locks the RW entry, determines whether this is a complete release, forced release, partial recovery, new-site-only release, or full dump requirement, creates or reuses a release clone, marks RO sites with `VLSF_DONTUSE`/`VLSF_NEWREPSITE`, creates destination transactions, forwards to one or more replicas via `AFSVolForwardMultiple` or a simulated single-forward fallback, brings released sites online, updates VLDB state after each batch, deletes temporary clones, clears release markers, and unlocks by replacing the VLDB entry. It intentionally stages VLDB visibility so at least one RO can remain discoverable where possible.

Dump and restore are stream-oriented. Dump starts a busy transaction, creates an Rx call, starts `AFSVolDump`/`AFSVolDumpV2`, delegates bytes to the caller callback, ends the call, and ends the transaction. The cloned dump variant first creates a temporary clone and deletes it after the dump. Restore chooses or allocates the target id, creates or opens the destination volume, starts `AFSVolRestore`, delegates input bytes to the caller callback, resets ids/types/dates/flags, ends the transaction, and creates or replaces VLDB metadata if requested by the mode.

Sync paths reconcile metadata with storage. `UV_SyncVldb` scans volumes on a server/partition, sorts them by RW id/type, and feeds each volume header into `CheckVolume`. `UV_SyncServer` scans VLDB entries matching a server/partition and feeds each into `CheckVldb`. `UV_SyncVolume` combines a VLDB-name lookup with optional server-side volume discovery. The `CheckVolume*` and `CheckVldb*` helpers perform a dry first pass, then lock/refetch only if an update is needed.

## State and Persistence Behavior

The file’s state is mostly transient C stack/global state. Persistent effects are remote:

- VLDB entries are created, replaced, deleted, and locked/unlocked via ubik calls and `VLDB_*` wrappers.
- File-server volumes are created, cloned, deleted, restored, renamed, marked online/offline/out-of-service/delete-on-salvage, and assigned forwarding pointers via `AFSVol*`.
- Volume ids are allocated or the VLDB maximum id is advanced with `ubik_VL_GetNewVolumeId`.
- Release state is encoded in VLDB flags such as `VLSF_DONTUSE`, `VLSF_NEWREPSITE`, `VLF_*EXISTS`, `VLOP_*`, plus `cloneId`.
- Move/copy/dump use static `jmp_buf env` and static `interrupt` for process-local signal recovery, so these flows are not reentrant and assume one active such operation in the process.

## Dependencies and Integration Points

`vsprocs.c` depends on Rx, ubik, rxkad/security setup, VLDB RPC definitions, volserver RPC definitions, local volume/location helpers from `lockdata`/`volser_internal`, XDR allocation/free conventions, host name resolution utilities, partition naming conventions, and command-layer callbacks for dump/restore data movement. It integrates with `vsutils.c` for VLDB compatibility wrappers and with `volser_prototypes.h`/`vsutils_prototypes.h` for public declarations consumed by `vos` and related tools.

## Risks and Edge Cases

- Cross-service consistency is fragile: many operations update both volserver state and VLDB state, and failures between those steps can leave partially moved, orphaned, or stale volumes.
- `setjmp`/`longjmp` signal recovery is process-global and hard to compose with threads or concurrent operations.
- Some cleanup branches call `exit(1)` instead of returning, which is appropriate for command-line recovery but risky for library-like embedding.
- Byte order is easy to misuse because VLDB entries are sometimes expected in network order locally and host order for XDR wrapper calls.
- Several string copies use historical fixed volume-name limits; many checks exist, but new call paths need to preserve suffix length rules for `.readonly`, `.backup`, `.clone`, and temp names.
- Release has nuanced state transitions; regressions can make RO replicas unavailable, mark sites as released when data transfer failed, or leave `VL_RERELEASE`/`VLSF_DONTUSE` state behind.
- Older server compatibility paths (`RXGEN_OPCODE`, old partition/list APIs, simulated `ForwardMultiple`) must be preserved for mixed deployments.

## Test Signals

Useful coverage includes create/delete round trips with VLDB validation; moving a RW volume across servers/partitions with and without clones; interrupted move/copy recovery; backup and clone creation with existing and missing destination volumes; release scenarios for first release, forced release, partial failed release recovery, new-site-only release, old servers without `ForwardMultiple`, and timed-out transactions; dump/restore full and incremental callbacks including `SIGPIPE`/`SIGINT`; syncvldb/syncserv dry-run versus mutating mode; byte-order assertions around `MapHostToNetwork`/`MapNetworkToHost`; and mixed old/new VLDB/volserver compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vsprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vsutils.c -->
# sources/distributed-fs/openafs/src/volser/vsutils.c

## Purpose

`vsutils.c` provides VLDB utility wrappers and command helpers used by volser client code. Its main job is to hide differences between old, new, and UUID-capable VLDB RPC interfaces while exposing a stable `nvldbentry`-based API to `vsprocs.c` and `vos` code. It also initializes the ubik VLDB client and translates user volume names/ids.

## Important APIs and Types

- `struct ubik_client *cstruct` is the shared VLDB client used by `vsprocs.c`.
- `ovlentry_to_nvlentry` and `nvlentry_to_ovlentry` translate between old `vldbentry` and newer `nvldbentry` records. `nvlentry_to_ovlentry` rejects entries with too many servers for old VLDB limits.
- `newvlserver` caches the detected server capability: unknown, old, new, or UUID-capable.
- `VLDB_CreateEntry`, `VLDB_GetEntryByID`, `VLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, and `VLDB_ListAttributesN2` wrap ubik VL calls and fall back when new opcodes are unsupported.
- `VLDB_IsSameAddrs` asks a UUID-capable VLDB whether two server addresses belong to the same multihomed file server, with a small ring cache of address lists.
- `vsu_ClientInit` calls `ugen_ClientInitFlags` to create a ubik client for `AFSCONF_VLDBSERVICE`.
- `vsu_ExtractName` strips `.readonly` and `.backup` suffixes from user-supplied names.
- `vsu_GetVolumeID` parses decimal ids or resolves names through the VLDB and returns RW/RO/BK ids based on suffix.

## Control Flow

The VLDB wrappers optimistically call the newer `N` interfaces while `newvlserver` is unknown. If a call returns `RXGEN_OPCODE`, the wrapper records the server as old and retries the old opcode after translating structures. Successful new calls mark the server as new. `VLDB_IsSameAddrs` upgrades detection to UUID-capable only after `ubik_VL_GetAddrsU` succeeds.

List operations normalize claimed entry counts so callers never iterate beyond the actual returned XDR array length. Old bulk entries are converted to `nbulkentries` and freed with `xdr_free`.

Name/id helpers first parse numeric ids strictly with `strtoul`; if parsing fails, they strip volume suffixes, fetch the base entry by name, and select the matching volume id slot.

## State and Persistence Behavior

This file persists no data locally. It maintains process-global capability/cache state (`cstruct`, `newvlserver`, `cacheips`, `cacheip_index`) and performs durable changes only through VLDB RPCs. The address cache is unsynchronized process memory and assumes typical single-threaded volser client use.

## Dependencies and Integration Points

The file integrates with ubik, rx/rxkad, AFS cell configuration, VLDB generated RPCs, XDR allocation/free helpers, `ugen_ClientInitFlags`, and the volser operation layer in `vsprocs.c`. `vsutils_prototypes.h` exposes these wrappers to other compilation units.

## Risks and Edge Cases

- Capability detection is global for the process; mixed VLDB server capabilities in one client lifetime would be hard to represent.
- Old VLDB fallback cannot represent more servers than the old `OMAXNSERVERS` limit.
- `VLDB_IsSameAddrs` returns conservative false for old/new non-UUID interfaces, so multihomed duplicate detection depends on modern VLDB support.
- The address cache is fixed-size and not protected by locks.
- `vsu_GetVolumeID` ignores its `acstruct` parameter and relies on global `cstruct`.
- Volume-name suffix handling uses old max-name limits and intentionally strips only `.readonly` and `.backup`.

## Test Signals

Tests should simulate `RXGEN_OPCODE` fallback for create/get/replace/list; validate old/new entry conversion including too-many-server rejection; verify list count clamping; cover UUID address equivalence and cache hits/misses; parse numeric ids including invalid trailing characters; resolve `.readonly`/`.backup` suffixes; and initialize a VLDB client with configured security flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vsutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vsutils_prototypes.h -->
# sources/distributed-fs/openafs/src/volser/vsutils_prototypes.h

## Purpose

`vsutils_prototypes.h` is the small public header for `vsutils.c`. It declares the VLDB compatibility wrappers and volume-name/id helper APIs consumed by volser client code.

## Important APIs

The header exports prototypes for `VLDB_CreateEntry`, `VLDB_GetEntryByID`, `VLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `VLDB_IsSameAddrs`, `vsu_ExtractName`, and `vsu_GetVolumeID`. The signatures expose VLDB types such as `nvldbentry`, `VldbListByAttributes`, and `nbulkentries`, so includers must already have the generated VLDB type definitions in scope.

## Control Flow and State

There is no executable control flow or local state. The include guard `_VSUTILS_PROTOTYPES_H` prevents duplicate declarations. All runtime behavior and process-global state live in `vsutils.c`.

## Dependencies and Integration Points

This header is included by `vsutils.c` and `vsprocs.c`; it is part of the volser client module’s internal/public C interface. Because it does not include the VLDB or AFS base headers itself, build order and include context matter.

## Risks and Test Signals

The main risk is declaration drift from `vsutils.c`; compiler warnings with strict prototypes are the strongest signal. API changes should be validated by building volser clients and by checking that all includers have the required type declarations before this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vsutils_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/Makefile.in -->
# sources/distributed-fs/openafs/src/xstat/Makefile.in

## Purpose

`src/xstat/Makefile.in` builds and installs the OpenAFS extended statistics client libraries and test tools for file-server (`xstat_fs`) and cache-manager (`xstat_cm`) statistics collection.

## Important Targets and Variables

- Includes `Makefile.config`, `Makefile.pthread`, and `Makefile.libtool`, so the module uses configured compiler, pthread, install, and libtool rules.
- `LT_deps` links against rxkad, fsint, cmd, util, and opr libtool libraries.
- `all` builds shared/static xstat libraries, installs generated public headers into `${TOP_INCDIR}/afs`, installs static archives into `${TOP_LIBDIR}`, and builds `xstat_fs_test` and `xstat_cm_test`.
- File-server targets build `liboafs_xstat_fs.la`, `libxstat_fs.a`, generated callback server stubs `afscbint.ss.c/.h`, and `xstat_fs_test`.
- Cache-manager targets build `liboafs_xstat_cm.la`, `libxstat_cm.a`, and `xstat_cm_test`.
- `install` and `dest` copy headers, static libraries, and test programs to configured or legacy destination trees.
- `clean` removes libtool outputs, generated callback stubs, archives, tests, core files, and component-version source.

## Control Flow

The build first ensures exported headers and libraries are available under top-level include/library directories. FS library builds include `xstat_fs.lo`, `xstat_fs_callback.lo`, generated `afscbint.ss.lo`, and component version metadata. CM library builds include `xstat_cm.lo` and component version metadata. Test binaries statically link their respective libtool libraries plus shared dependencies and roken/platform libraries.

## State and Persistence Behavior

Build outputs are local artifacts: `.lo`, `.o`, `.la`, `.a`, generated `afscbint.*`, `AFS_component_version_number.c`, installed headers/libraries, and test binaries. No runtime state is managed here.

## Dependencies and Integration Points

This makefile integrates the xstat sources with the OpenAFS top-level build, libtool abstraction, generated fsint callback stubs, Rx/RxKAD, command parsing, util, opr, roken, and platform `XLIBS`. Public consumers get `afs/xstat_fs.h`, `afs/xstat_cm.h`, `libxstat_fs.a`, and `libxstat_cm.a`.

## Risks and Test Signals

Risks include stale generated `afscbint` stubs, missing dependency libraries, divergence between libtool shared/static rules, and install/dest path differences. Signals are successful `make all`, `make install DESTDIR=...`, `make clean && make`, and execution/linking of `xstat_fs_test`/`xstat_cm_test` in a configured tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_cm.c -->
# sources/distributed-fs/openafs/src/xstat/xstat_cm.c

## Purpose

`xstat_cm.c` implements the client side of Cache Manager extended statistics collection. It creates unauthenticated Rx connections to one or more cache managers, starts a pthread probe loop, periodically calls `RXAFSCB_GetXStats` for requested collection ids, stores the latest result in exported globals, and invokes a caller-provided handler after each collection.

## Important APIs, Types, and Variables

- Exported globals: `xstat_cm_numServers`, `xstat_cm_ConnInfo`, `xstat_cm_Results`, and `xstat_cmData`.
- Private state: probe frequency, initialization flag, debug flag, one-shot flag, handler pointer, probe thread id, collection count/id array, and a mutex/condition variable for forced probes.
- `xstat_cm_CleanupInit` resets result pointers and fixed result buffer metadata.
- `xstat_cm_Cleanup` destroys Rx connections and optionally frees the connection array.
- `xstat_cm_Init` validates arguments, records configuration, allocates/copies collection ids, initializes Rx/security, creates per-server Rx connections, and starts the probe thread.
- `xstat_cm_LWP` is the probe thread body; it iterates servers and collection ids, calls `RXAFSCB_GetXStats`, fills `xstat_cm_Results`, and invokes the handler.
- `xstat_cm_ForceProbeNow` signals the condition variable so a continuous probe wakes early.
- `xstat_cm_Wait` joins one-shot probes or sleeps/selects in continuous mode.

## Control Flow

Initialization is mandatory before all other operations. `xstat_cm_Init` rejects invalid server counts, socket arrays, probe intervals, handlers, collection counts, and collection arrays. It sets global mode flags, allocates storage, initializes result state, calls `rx_Init`, creates a null security object, resolves host names for display, creates service-1 Rx connections to each target cache manager, and starts `xstat_cm_LWP`.

The probe thread increments `probeNum` once per round. For each valid connection and each requested collection id, it resets the static data buffer length/content, records the target connection and collection number, calls `RXAFSCB_GetXStats`, stores the RPC result code in `probeOK`, and calls the handler with no explicit arguments; the handler reads exported globals. In one-shot mode the thread exits after one full pass. In continuous mode it waits on `xstat_cm_force_cv` until the next absolute timeout or a forced signal.

Cleanup destroys any existing Rx connections and can free the connection array, but it does not join or cancel the probe thread in continuous mode.

## State and Persistence Behavior

All state is process-local memory. The latest probe result uses a fixed global `xstat_cmData` buffer of `AFSCB_MAX_XSTAT_LONGS`, so each collection overwrites previous data. There is no local persistence. Network state consists of Rx connections to cache managers. The module is effectively singleton: repeated `xstat_cm_Init` calls are accepted as no-ops after printing a warning.

## Dependencies and Integration Points

The file depends on Rx, the generated AFS callback interface (`RXAFSCB_GetXStats`), pthreads, opr mutex/condition wrappers, host utility resolution, and `xstat_cm.h`. Consumers are typically `xstat_cm_test` or monitoring tools that install a handler and inspect `xstat_cm_Results`.

## Risks and Edge Cases

- Global result state is not protected while the handler and probe thread operate; consumers must treat it as thread-owned during callbacks.
- `malloc` for `xstat_cm_collIDP` is not checked before `memcpy`.
- Continuous cleanup does not stop/join the probe thread, so freeing memory while it runs would be unsafe.
- A connection creation failure sets a final `-2` return but still starts the probe thread and leaves null connections skipped.
- `xstat_cm_Results.data.AFSCB_CollData_len` is reset to max before each call, and the buffer is memset using `AFSCB_MAX_XSTAT_LONGS * 4`, assuming 32-bit `afs_int32`.
- Null Rx security is intentional for this probe interface but should be considered when exposing stats across trust boundaries.

## Test Signals

Tests should cover invalid argument rejection, one-shot completion and `pthread_join`, forced wakeups in continuous mode, handler invocation count for N servers times M collections, null connection skipping after partial init failure, Rx init/security failure injection, cleanup destroying connections, and correct result metadata (`probeNum`, `probeTime`, `connP`, `collectionNumber`, `probeOK`, data length).
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_cm.h -->
# sources/distributed-fs/openafs/src/xstat/xstat_cm.h

## Purpose

`xstat_cm.h` is the public interface for the Cache Manager extended statistics collector implemented in `xstat_cm.c`. It defines initialization flags, connection/result structures, exported globals, and the functions a monitoring program uses to start, force, wait for, and clean up cache-manager probes.

## Important APIs and Types

- Flags: `XSTAT_CM_INITFLAG_DEBUGGING` enables diagnostic output; `XSTAT_CM_INITFLAG_ONE_SHOT` makes the probe thread stop after one collection round.
- `struct xstat_cm_ConnectionInfo` stores the target socket, Rx connection, and resolved host name.
- `struct xstat_cm_ProbeResults` stores the current probe number, probe time, connection pointer, collection id, callback data buffer, and RPC result status.
- Exported globals expose connection count/array and latest probe results.
- `xstat_cm_Init`, `xstat_cm_ForceProbeNow`, `xstat_cm_Cleanup`, and `xstat_cm_Wait` are the public lifecycle functions.

## Control Flow and State

The header describes the required lifecycle: call `xstat_cm_Init` first with sockets, interval, handler, flags, and collection ids; read latest results from exported globals inside the handler; optionally force probes; wait for one-shot or continuous operation; call cleanup when done. Runtime state is defined in `xstat_cm.c`, not in this header.

## Dependencies and Integration Points

The header includes platform socket headers, Rx definitions, generated `afscbint.h`, and `afs_stats.h`. It defines `FSINT_COMMON_XG` before including stats so applications can include xstat and fsint interfaces together. Installed copies are produced by `src/xstat/Makefile.in`.

## Risks and Test Signals

Because the interface exposes global mutable state instead of opaque handles, only one active collector instance is supported per process. ABI/API changes to the structs affect external monitoring tools. Build tests should include this header from standalone consumers on Unix and NT environments; runtime tests should validate the documented lifecycle against `xstat_cm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_cm.h -->
