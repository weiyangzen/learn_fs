# subset-b-007822 research

Grouped research for the OpenAFS volserver files in `sources/distributed-fs/openafs/src/volser`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volmain.c -->
# sources/distributed-fs/openafs/src/volser/volmain.c

## Purpose

`volmain.c` is the executable entry point for the OpenAFS volume server (`volserver`). It initializes platform services, audit and logging, the OpenAFS volume package, Rx networking, security classes, and the Volser RPC service. It also starts the background transaction maintenance loop that periodically garbage-collects stale volume transactions and releases accumulated partition locks when the server is idle.

The file is operational glue rather than RPC business logic. Most volume operations live in `volprocs.c`, while transaction list mechanics live in `voltrans.c`; `volmain.c` owns daemon lifetime and the global policy knobs those modules consume.

## Important APIs, Types, and Globals

- `main(int argc, char **argv)` performs process initialization, option parsing, volume package setup, Rx service creation, and starts the Rx server loop.
- `ParseArgs` defines and applies command-line options for logging, Rx binding/MTU/jumbograms, worker thread count, audit sinks, sync policy, config path, restricted query policy, and server-to-server encryption policy.
- `BKGLoop` is the detached background daemon. Every `GCWAKEUP` seconds it calls `GCTrans()` and `TryUnlock()`, and reopens the log every ten loop iterations.
- `TryUnlock` releases partition locks via `VPFullUnlock()` when there are no running RPC calls and no active Volser transactions.
- `MyBeforeProc` and `MyAfterProc` update `runningCalls` under `VTRANS_LOCK`; they are installed as Rx service callbacks to make idle detection reliable.
- `shutdown_signal` in pthread builds logs live transactions at shutdown, including transaction id, volume id, and partition, then exits.
- `volser_syscall` provides the platform-specific hook for Rx/syscall integration, with Solaris ioctl, generic ENOSYS fallback, and regular `AFS_SYSCALL` paths.
- `vol_rxstat_userok` authorizes Rx statistics management through `afsconf_SuperUser`.
- `vol_IsLocalRealmMatch` delegates local-realm checks to the cell configuration directory and logs failures.

Important globals exported to other volserver code include:

- `tdir`, the opened AFS configuration directory used by auth/audit checks.
- `DoLogging`, `restrictedQueryLevel`, `DoPreserveVolumeStats`, and `doCrypt`, which affect RPC behavior in `volprocs.c`.
- Rx/network knobs: `rxBind`, `rxkadDisableDotCheck`, `rxJumbograms`, `rxMaxMTU`, `udpBufSize`, `SHostAddrs`.
- Worker/concurrency knob `lwps`, defaulting to 9 but raised to at least 4 for service execution and capped at `MAXLWP`.

## Control Flow

Startup begins with audit initialization and AFS server path initialization. `configDir` defaults to the server etc directory, then `ParseArgs` may override configuration, logging, Rx, thread, audit, query, and encryption options. Audit options are opened before service startup so later events can be recorded.

After error table setup, platform-specific init, and logging setup, `main` initializes the volume package with `VInitVolumePackage2(volumeServer, &opts)`, initializes the local lock used by lower-level destructive operations, initializes the directory package, and installs the volserver syscall callback where supported. Rx packet, UDP buffer, bind host, jumbo, MTU, interface, and dead-time options are applied before services are created.

The background loop is started before the Rx services are registered. It sleeps for `GCWAKEUP`, runs transaction GC, tries to release partition locks if idle, and periodically reopens the log. In pthread builds it is a detached pthread; in LWP builds it is an LWP process.

The server then opens the AFS config directory, installs the audit user realm check, builds server security objects, and creates the `VOLSER` Rx service with `AFSVolExecuteRequest` as the generated RPC dispatcher. The before/after hooks track active calls. The secondary `rpcstats` service is registered for Rx statistics. Finally `rx_SetRxStatUserOk` installs the stats authorization callback and `rx_StartServer(1)` donates the main thread to the Rx worker pool.

## State and Persistence Behavior

This file does not directly mutate volume contents, but it controls persistent side effects by initializing the volume package and exposing daemon-wide policy:

- Logging destination and rotation behavior are selected before most operational logs are emitted.
- Audit start, finish, exit, and command-line events are emitted through `osi_audit`.
- `TryUnlock` closes partition lock file descriptors via `VPFullUnlock`; this changes process-held locks, not on-disk metadata.
- Signal shutdown logs active transactions but does not attempt graceful rollback; the message explicitly warns that affected volumes may need salvage.
- `runningCalls` is in-memory process state that gates lock release. It is protected by `VTRANS_LOCK`, shared with transaction list state.
- `doCrypt` controls whether server-to-server calls in `volprocs.c` use clear or encrypted rxkad security, including an inherit mode based on the incoming call.

## Dependencies and Integration Points

`volmain.c` depends on the OpenAFS volume package (`VInitVolumePackage2`, partition handling, directory package), Rx (`rx_InitHost`, service creation, Rx stats), auth/cell configuration (`afsconf_Open`, security object construction), audit (`osi_audit_*`), and platform runtime wrappers. It integrates with:

- `volprocs.c` through `VPFullUnlock`, global policy variables, and the generated `AFSVolExecuteRequest` dispatcher.
- `voltrans.c` through `TransList()` and `GCTrans()`.
- common volserver logging and abort helpers declared in `volser_internal.h`.
- generated RPC statistics service `RXSTATS_ExecuteRequest`.

## Risks and Edge Cases

- `shutdown_signal` exits after logging active transactions; interrupted updates can leave volumes requiring salvage. This is intentional but operationally risky.
- `TryUnlock` assumes `runningCalls == 0` and an empty transaction list are sufficient to release all accumulated partition locks. Bugs in before/after accounting would affect lock lifetime.
- `ParseArgs` accepts many options that modify global behavior; incompatible logging options are checked, but most runtime policy is global and process-wide.
- `rxBind` host selection depends on netinfo/netrestrict parsing. Wrong configuration can bind the volume service to an unintended address.
- `rxkadDisableDotCheck` weakens principal validation when explicitly requested.
- LWP and pthread paths differ for sleep, signal handling, and polling, so changes need platform-specific review.

## Test Signals

Useful tests include daemon startup with default and explicit `-config`, logging modes (`-logfile`, `-syslog`, `-transarc-logs`), invalid option combinations, restricted query policy behavior, server-to-server crypto modes, Rx bind with netinfo/netrestrict, and signal shutdown while a long-running transaction exists. Runtime tests should confirm `GCTrans` is called periodically and `VPFullUnlock` only runs after both active calls and transactions drop to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volmain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volprocs.c -->
# sources/distributed-fs/openafs/src/volser/volprocs.c

## Purpose

`volprocs.c` implements the server-side Volser RPC procedures behind the generated `AFSVolExecuteRequest` dispatcher. It is the operational core for remote volume administration: partition queries, volume creation/deletion, clone/reclone, transaction create/end, dump/restore/forward, status and metadata changes, volume listings, transaction monitoring, RO-to-RW conversion, dump sizing, and volume splitting.

The file follows a wrapper pattern: exported `SAFSVol*` functions perform audit logging and call static `Vol*` implementations that contain authorization, transaction lookup, volume package calls, filesystem synchronization, and error handling.

## Important APIs, Types, and Functions

Major exported RPC entry points include:

- Partition and listing: `SAFSVolPartitionInfo`, `SAFSVolPartitionInfo64`, `SAFSVolListPartitions`, `SAFSVolXListPartitions`, `SAFSVolListOneVolume`, `SAFSVolXListOneVolume`, `SAFSVolListVolumes`, `SAFSVolXListVolumes`.
- Destructive or mutating volume operations: `SAFSVolNukeVolume`, `SAFSVolCreateVolume`, `SAFSVolDeleteVolume`, `SAFSVolClone`, `SAFSVolReClone`, `SAFSVolRestore`, `SAFSVolSetFlags`, `SAFSVolSetInfo`, `SAFSVolSetIdsTypes`, `SAFSVolSetDate`, `SAFSVolConvertROtoRWvolume`, `SAFSVolSplitVolume`.
- Transaction and transfer operations: `SAFSVolTransCreate`, `SAFSVolEndTrans`, `SAFSVolForward`, `SAFSVolForwardMultiple`, `SAFSVolDump`, `SAFSVolDumpV2`, `SAFSVolGetSize`.
- Query and diagnostic operations: `SAFSVolGetFlags`, `SAFSVolGetStatus`, `SAFSVolGetName`, `SAFSVolMonitor`, `SAFSVolGetNthVolume` (not implemented), `SAFSVolSignalRestore` (no-op handshake).

Important helpers include:

- `VPFullUnlock_r` and `VPFullUnlock` close partition lock file descriptors, used by `volmain.c` when the daemon is idle.
- `ConvertVolume`, `ConvertPartition`, and `GetPartName` map numeric ids to volume header names and `/vicep*` partition names.
- `VAttachVolumeByName_retry` and `VAttachVolume_retry` wrap volume attachment and, in demand-attach builds, wait through transient `VSALVAGING` states before returning `VSALVAGE`.
- `XAttachVolume` attaches a volume by id and partition by converting both to names.
- `ViceCreateRoot` constructs the initial root directory vnode and ACL for a newly created read-write volume.
- `MakeClient` creates client-side security for server-to-server transfer, honoring `doCrypt` from `volmain.c`.
- `GetNextVol`, `FillVolInfo`, `GetVolObject`, and `GetVolInfo` implement partition-directory scanning and population of `volintInfo` / `volintXInfo`.

Local abstractions:

- `volint_info_type_t` distinguishes base and extended wire volume info.
- `volint_info_handle_t` wraps either `volintInfo` or `volintXInfo` and is used by macros `VOLINT_INFO_STORE` and `VOLINT_INFO_PTR` to share fill logic.
- `vol_info_list_mode_t` distinguishes single-volume and multi-volume listing behavior.

## Control Flow

Most mutating RPCs follow the same flow:

1. Authorize with `afsconf_SuperUser(tdir, call, caller)`.
2. Log caller and operation when `DoLogging` is enabled.
3. Create or find a Volser transaction with `NewTrans` or `FindTrans`.
4. Reject deleted transactions via `VTDeleted`.
5. Record the active call/procedure name with `TSetRxCall` for monitoring.
6. Invoke volume package, dump/restore, FSYNC, or namei/inode operations.
7. Update persistent volume headers with `VUpdateVolume` where needed.
8. Clear the tracked Rx call and release/delete the transaction with `TRELE` or `DeleteTrans`.
9. Return the primary operation error, falling back to `VOLSERTRELE_ERROR` for transaction release failures when no earlier error exists.

Queries use `afsconf_CheckRestrictedQuery(tdir, call, restrictedQueryLevel)` instead of superuser-only authorization. This allows the `-restricted_query` daemon option to choose whether non-admin users may issue read-only volume and partition queries.

Create flow: `VolCreateVolume` validates name/type/id, creates a transaction, calls `VCreateVolume`, initializes metadata, optionally creates a root directory with `ViceCreateRoot`, marks the new volume `DESTROY_ME` and out of service until the caller finishes setup, writes the header, stores the attached volume in the transaction, and returns the transaction id.

Clone/reclone flow: `VolClone` creates a transaction for the target clone id, optionally attaches an old purge volume, validates parent/device/type relationships, calls `CloneVolume`, adjusts clone type/name/dates/stats, updates headers, detaches the new volume, updates the original, breaks callbacks, and deletes the target transaction. `VolReClone` is similar but reclones into an existing clone and optionally preserves volume statistics.

Transfer flow: `VolDump` streams a dump to the incoming Rx call through `DumpVolume`. `VolRestore` drops directory buffers, calls `RestoreVolume`, and breaks callbacks. `VolForward` and `SAFSVolForwardMultiple` create outbound Rx client calls to destination volservers, start remote restore transactions, stream dump data into those calls, end remote restore, and close connections. `SAFSVolForwardMultiple` returns per-destination result codes and treats overall success as at least one attempted transfer path proceeding through `DumpVolMulti`.

Listing flow: `VolList*` opens the partition directory, scans volume header filenames with `GetNextVol`, and either returns ids or calls `GetVolInfo` for metadata. `GetVolInfo` creates a temporary transaction to avoid concurrent manipulation, attaches the volume, filters `DESTROY_ME` volumes in multi-list mode, asks the fileserver for in-core state in demand-attach builds, fills the on-wire structure, detaches, and deletes the temporary transaction.

Monitor flow: `VolMonitor` takes `VTRANS_LOCK`, walks `TransList()`, locks each transaction, and copies transaction id, age fields, return code, volume id, partition, flags, last procedure name, and Rx call progress into a dynamically growing `transDebugEntries` array.

## State and Persistence Behavior

This file performs direct persistent volume mutations through OpenAFS volume package APIs:

- `VCreateVolume`, `VUpdateVolume`, `VDetachVolume`, `VPurgeVolume`, `CloneVolume`, `RestoreVolume`, `nuke`, `namei_ConvertROtoRWvolume` / `inode_ConvertROtoRWvolume`, and `split_volume`.
- Volume header fields changed include type, parent/clone/backup ids, name, quota, creation/update dates, day-use counters, update counters, service/blessed state, `destroyMe`, `needsSalvaged`, backup date, stats fields, and disk usage.
- `ViceCreateRoot` creates the root directory inode, writes directory contents, creates the initial ACL for `system:administrators`, writes vnode index data, updates the uniquifier, and computes disk usage.
- `FSYNC_VolOp` calls coordinate with the file server for callback breaks, move forwarding, volume checkout/onlining during conversion, query state, pending operations, and demand-salvage scheduling.
- Dump and restore procedures stream over Rx calls and can leave partial remote state if network or destination restore fails after remote restore has started.

In-memory state is also important:

- `struct volser_trans` objects pin attached volumes and serialize operations per volume/partition.
- `TSetRxCall` / `TClearRxCall` maintain transaction debug state for `VolMonitor`.
- `restrictedQueryLevel`, `DoPreserveVolumeStats`, and `doCrypt` are global policies set by `volmain.c`.

## Dependencies and Integration Points

`volprocs.c` sits at the intersection of Rx RPC, auth, the OpenAFS volume package, partition scanning, dump/restore codecs, FSYNC daemon coordination, and audit logging. Key dependencies include:

- `volser.h` for transaction flags, volume type constants, error values, and server-to-server crypto enum.
- `voltrans.c` APIs (`NewTrans`, `FindTrans`, `DeleteTrans`, `TRELE`, `TransList`) for transaction lifetime.
- `voltrans_inline.h` for transaction call/procedure tracking.
- `dumpstuff.h` for `DumpVolume`, `DumpVolMulti`, `RestoreVolume`, `StartAFSVolRestore`, `EndAFSVolRestore`, and `SizeDumpVolume`.
- `physio.h`, `vol.h`, `volume_inline.h`, partition and vnode APIs for low-level volume metadata and inode operations.
- `afsconf` for superuser and restricted-query checks, plus client auth construction for outbound volserver calls.
- `afs/audit.h` for per-RPC audit events.

## Risks and Edge Cases

- Many paths manipulate volume headers and file data directly. Failures between metadata updates, detaches, FSYNC notifications, and transaction deletion can leave offline, `DESTROY_ME`, partially cloned, partially restored, or salvage-needed volumes.
- `VolCreateVolume` requires a nonzero caller-supplied volume id and returns `E2BIG` if missing, which is an unusual error mapping.
- Name length checks use the historical 31-character limit, while newer constants elsewhere allow longer names. Changing this could affect protocol compatibility.
- `VolSetInfo` calls `VUpdateVolume` but ignores the resulting `error` on return; it always returns 0 unless `TRELE` fails. That is a notable behavior to preserve or test before changing.
- `VolGetName` allocates a one-byte buffer before transaction lookup; if lookup fails, that allocation remains owned by the RPC marshalling path only if the caller respects the output contract.
- `SAFSVolForwardMultiple` has complex partial-failure semantics. Callers must inspect the returned per-destination codes even when the function returns 0.
- Demand-attach builds have special state synthesis for listings; non-DAFS builds infer online status differently. Cross-build behavior can diverge.
- Temporary transactions created during listing can make busy volumes report `VBUSY` or omit `DESTROY_ME` volumes in multi-list results.
- RO-to-RW conversion warns that a failed conversion may leave an inconsistent or partially converted state; salvage or restore may be required.
- Transaction locking is split between the global transaction list lock and per-transaction locks. New code must preserve lock ordering and avoid holding `VTRANS_LOCK` around blocking volume operations unless already established.

## Test Signals

Important tests include authorization boundaries for superuser-only versus restricted query RPCs; create/delete/end transaction lifecycle; clone and reclone preserving or clearing stats according to `DoPreserveVolumeStats`; dump/restore and forward with interrupted Rx calls; multi-forward partial success; list-volume behavior for busy, offline, `DESTROY_ME`, needs-salvage, and demand-attach pending-operation states; `VolMonitor` output during an active dump/restore; RO-to-RW conversion failure recovery; and split-volume validation that both volumes are on the same device and the target is freshly created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volser.p.h -->
# sources/distributed-fs/openafs/src/volser/volser.p.h

## Purpose

`volser.p.h` is the core public/private Volser header for server and utility code. It defines transaction flags, volume type aliases, the `struct volser_trans` transaction object, timing and helper constants, Volser-specific error values, backup/listing structures, restore/release flag bits, utility prototypes, and the server-to-server encryption policy enum.

## Important APIs, Types, and Constants

The most important type is `struct volser_trans`, which represents an active volume transaction. Its fields include list linkage, transaction id, last-active and creation times, return code, attached `Volume *`, volume id, partition id, remote dump transaction state, reference count, attach-mode flags, current volume flags, transaction flags, restore incrementality, debug procedure/call fields, and a pthread mutex in pthread builds.

Flag groups:

- Volume state flags: `VTDeleteOnSalvage`, `VTOutOfService`, `VTDeleted`.
- Initial attach flags: `ITOffline`, `ITBusy`, `ITReadOnly`, `ITCreate`, `ITCreateVolID`.
- Transaction state flags: `TTDeleted`.
- Volume type aliases: `volser_RW`, `volser_RO`, `volser_BACK`, `volser_RWREPL`.
- Restore/copy/clone flags: `RV_FULLRST`, `RV_OFFLINE`, `RV_CRDUMP`, `RV_CRKEEP`, `RV_CRNEW`, `RV_LUDUMP`, `RV_LUKEEP`, `RV_LUNEW`, `RV_RDONLY`, `RV_CPINCR`, `RV_NOVLDB`, `RV_NOCLONE`, `RV_NODEL`, `RV_RWONLY`.
- Release flags: `REL_COMPLETE`, `REL_FULLDUMPS`, `REL_STAYUP`.
- Volume info validity flags such as `PARTVALID`, `CLONEVALID`, `IDVALID`, `NAMEVALID`, `ENTRYVALID`, and `REUSECLONEID`.

Concurrency macros:

- `THOLD(tt)` increments a transaction reference count directly.
- `VTRANS_OBJ_LOCK_INIT`, `VTRANS_OBJ_LOCK_DESTROY`, `VTRANS_OBJ_LOCK`, and `VTRANS_OBJ_UNLOCK` map to `opr_mutex_*` in pthread builds and no-ops otherwise.

Other definitions include:

- `GCWAKEUP`, the background GC wake interval used by `volmain.c` and `voltrans.c`.
- `MAXHELPERS` and `VHIdle` / `VHRequest`, historical helper state definitions.
- Volser service constants: `VOLSERVICE_ID`, `VOLSER_MAXVOLNAME`, `VOLSER_OLDMAXVOLNAME`.
- Backup-facing structs `volDescription` and `partList`.
- Utility prototypes for volume id parsing, name extraction, and ubik client initialization.
- `enum vol_s2s_crypt` with `VS2SC_NEVER`, `VS2SC_INHERIT`, and `VS2SC_ALWAYS`.

## Control Flow Role

This header does not execute logic, but it shapes control flow across the volserver:

- `IT*` flags passed to `SAFSVolTransCreate` determine the attachment mode used by `volprocs.c`.
- `VT*` flags set by `VolSetFlags` are reflected into volume header state and used to reject operations on deleted transactions.
- `TTDeleted` lets `DeleteTrans` mark a transaction for later free when references are still outstanding.
- `GCWAKEUP` coordinates the sleep period for transaction GC.
- `enum vol_s2s_crypt` controls security selection in outbound `VolForward` calls.

## State and Persistence Behavior

The header itself has no persistence side effects. It defines the in-memory transaction state used to pin volume objects and the bit values that map to persisted volume header changes in `volprocs.c`. For example, `VTDeleteOnSalvage` maps to `V_destroyMe`, and `VTOutOfService` maps to `V_inService` changes when flags are applied.

Because `THOLD` is a raw increment macro, callers must already be in the expected locking context. Misuse can corrupt transaction lifetime and affect whether attached volumes are detached or purged.

## Dependencies and Integration Points

`volser.p.h` includes OpenAFS volume definitions, ubik declarations, and pthread declarations in pthread builds. It is consumed by `volmain.c`, `volprocs.c`, `voltrans.c`, Volser client utilities, and higher-level `vsprocs.c` code. It also declares selected utility APIs that cross between command/client code and server-side modules.

## Risks and Edge Cases

- `struct volser_trans` is shared by multiple modules; field changes are ABI/source-sensitive inside the OpenAFS tree.
- Some flags are marked obsolete or dangerous, such as `ITReadOnly` being documented as "DO NOT USE".
- The pthread lock macros become no-ops in non-pthread builds, so code must not rely on per-transaction lock behavior unless guarded by the global model used in LWP builds.
- Historical name limits (`VOLSER_OLDMAXVOLNAME`, `ISNAMEVALID`) can conflict with newer maximums.
- Error values overlap with longstanding OpenAFS client expectations; renumbering or reusing them would be protocol-risky.

## Test Signals

Tests should indirectly validate this header through transaction creation modes, flag-setting RPCs, transaction deletion while referenced, stale transaction GC, server-to-server crypto option parsing, and restore/release flag behavior in higher-level vos operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volser.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volser_internal.h -->
# sources/distributed-fs/openafs/src/volser/volser_internal.h

## Purpose

`volser_internal.h` gathers internal cross-module prototypes for the Volser implementation and related vos utility code. It is not the RPC interface definition; instead, it lets C files in this area call shared helpers without exposing them as stable external API.

## Important APIs and Declarations

Server/internal declarations include:

- `Abort`, `Log`, and `InitErrTabs` from `common.c`.
- `split_volume` from `vol_split.c`.
- Transaction APIs from `voltrans.c`: `FindTrans`, `NewTrans`, `TransList`, `DeleteTrans`, `TRELE`, and `GCTrans`.
- `VPFullUnlock` from `volprocs.c`.

The file also declares a broad set of `UV_*` vos-side procedures from `vsprocs.c`, including create, move, backup, release, dump, restore, add/remove site, list, sync, rename, status, zap, set info, copy, clone, dump cloned volume, get size, and convert RO. These are higher-level client orchestration functions that talk to volservers and VLDB.

Global utility declarations:

- `MapNetworkToHost` for VLDB entry conversion.
- `PrintError`, `init_volintInfo`, and VLDB entry enumeration helpers.
- `verbose` and `noresolve` globals used by command-line utility paths.

## Control Flow Role

The header enables the daemon entry point to call transaction GC and partition unlock logic, enables `volprocs.c` to use transaction functions, and enables vos/client code to share orchestration APIs. In the researched files, its main role is connecting:

- `volmain.c` to `GCTrans`, `TransList`, and `VPFullUnlock`.
- `volprocs.c` to `split_volume`, transaction APIs, and common logging/error helpers.
- `voltrans.c` to `Log`.

## State and Persistence Behavior

The header has no direct state or persistence behavior. It declares functions that do have major side effects:

- `DeleteTrans` can detach volumes and terminate Rx calls.
- `GCTrans` can purge timed-out temporary volumes.
- `UV_*` functions can modify VLDB entries, create/delete/restore volumes, and coordinate cross-server moves/releases.
- `split_volume` can move vnode data between volumes.

Consumers must treat these declarations as side-effecting operational APIs, not pure helpers.

## Dependencies and Integration Points

The header forward-declares `struct nvldbentry` and uses Volser/Rx/volume-related types expected to be available through surrounding includes. It is a central compile-time integration point between the volserver daemon, server RPC implementation, transaction manager, volume splitting, and vos command/client orchestration.

## Risks and Edge Cases

- This file mixes server-side and client-side `UV_*` declarations. That increases coupling and can make dependency boundaries unclear.
- Prototype drift between implementations and this header would cause compile warnings or ABI bugs, especially for function-pointer callback signatures used by dump/restore.
- Many functions return OpenAFS-specific `afs_int32` or integer error codes with different conventions; callers must preserve each function's expected error handling.

## Test Signals

Compile coverage across volserver and vos utilities is the primary signal. Runtime coverage should exercise transaction creation/deletion/GC, volume split, and representative `UV_*` orchestration paths such as create, move, release, dump, restore, and list operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volser_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volser_prototypes.h -->
# sources/distributed-fs/openafs/src/volser/volser_prototypes.h

## Purpose

`volser_prototypes.h` is a smaller public prototype header for selected vos/Volser utility functions. It declares commonly used `UV_*` client functions, partition and host mapping helpers, and security binding helpers.

## Important APIs

Declared functions include:

- `MapPartIdIntoName` and `MapHostToNetwork` for translating partition ids and VLDB host fields.
- `UV_Bind` for creating an Rx connection to a volume server.
- `UV_SetSecurity` for installing client security.
- `UV_CreateVolume`, `UV_DeleteVolume`, `UV_ListOneVolume`, and `UV_RestoreVolume` for common volume operations.

Forward declarations for `struct nvldbentry` and `struct volintInfo` avoid pulling in heavier headers for prototypes.

## Control Flow Role

This header does not implement logic. It allows client and utility code to call a compact subset of `vsprocs.c` functionality. Compared with `volser_internal.h`, it presents fewer declarations and appears oriented toward broader users that do not need the full internal orchestration surface.

## State and Persistence Behavior

The header itself is stateless. The declared `UV_*` functions can create, delete, list, and restore volumes, which implies persistent changes on volservers and VLDB coordination depending on the implementation. `UV_SetSecurity` changes process-level client security state for subsequent calls.

## Dependencies and Integration Points

The declarations depend on Rx types (`struct rx_connection`, `struct rx_securityClass`, `struct rx_call`), VLDB entry types, Volser wire types, and OpenAFS integer types supplied by including translation units. It integrates utility code with the Volser RPC client layer.

## Risks and Edge Cases

- Keeping this small header consistent with `volser_internal.h` and `vsprocs.c` matters because duplicate or divergent prototypes can hide call-site bugs.
- Callback signatures for restore data writers must match exactly or restore streams can fail at runtime.
- The header does not document ownership or allocation behavior for returned `volintInfo **`; callers must follow implementation conventions.

## Test Signals

Compile tests for utilities including this header, plus runtime vos tests for bind/security setup, create/delete, list-one-volume, and restore, provide the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/volser_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/voltrans.c -->
# sources/distributed-fs/openafs/src/volser/voltrans.c

## Purpose

`voltrans.c` implements the in-memory Volser transaction registry. Transactions serialize and track operations on a given volume id and partition, hold attached `Volume *` objects, provide debug/status data to `volprocs.c`, and allow stale or abandoned operations to be reclaimed by the background GC loop.

## Important APIs and State

Module state:

- `static struct volser_trans *allTrans` is the head of the active transaction list.
- `static afs_int32 transCounter` generates transaction ids starting at 1.
- `OLDTRANSTIME` is the idle timeout for deleting unreferenced old transactions.
- `OLDTRANSWARN` is the threshold for logging old transaction warnings.
- `GCDeletes` counts GC deletions but is only internal diagnostic state.

Exported functions:

- `NewTrans(VolumeId avol, afs_int32 apart)` allocates and registers a transaction if the same volume/partition is not already active.
- `FindTrans(afs_int32 atrans)` finds a transaction by id, refreshes its timestamp, increments its reference count, and returns it.
- `DeleteTrans(struct volser_trans *atrans, afs_int32 lock)` removes a transaction when possible, detaching its volume and killing its tracked Rx call; if references remain, it marks `TTDeleted` and drops one reference.
- `TRELE(struct volser_trans *at)` releases a transaction reference, deleting it if it was marked deleted and the caller held the last reference.
- `GCTrans(void)` logs old transactions and deletes timed-out unreferenced transactions; if a timed-out transaction owns a temporary `DESTROY_ME` volume that is not already marked `VTDeleted`, it purges the volume.
- `TransList(void)` returns the raw list head for callers that already coordinate locking or only need status traversal.

## Control Flow

`NewTrans` allocates before taking `VTRANS_LOCK`, then scans `allTrans` to enforce one active transaction per volume/partition. On success it initializes ids, reference count, timestamps, debug fields, per-transaction lock, links the object at the list head, and returns it with refcount 1.

`FindTrans` takes `VTRANS_LOCK`, scans by transaction id, refreshes `time`, increments `refCount`, unlocks, and returns. Callers are responsible for `TRELE` or `DeleteTrans`.

`DeleteTrans` optionally takes the global lock. If the reference count is greater than one, it decrements the count, marks `TTDeleted`, and leaves the object in the list for the final releaser. If the caller owns the last reference, it unlinks the transaction, detaches any attached volume, aborts any tracked Rx call with `RX_CALL_DEAD`, destroys the per-transaction lock, frees the object, and returns.

`TRELE` validates nonzero refcount, refreshes the transaction time, and either completes a deferred delete or decrements `refCount`.

`GCTrans` runs under `VTRANS_LOCK` from the background loop. It logs transactions older than the warning threshold. For unreferenced transactions older than `OLDTRANSTIME`, it temporarily increments the refcount, purges abandoned temporary volumes outside the global lock when required, reacquires the lock, and calls `DeleteTrans`. It carefully reads `tt->next` after relocking because the list can change while the global lock is dropped.

## State and Persistence Behavior

Most state is in-memory transaction metadata. Persistent effects occur only during cleanup:

- `DeleteTrans` detaches `tt->volume` with `VDetachVolume`, which can write or release volume package state depending on the volume object.
- `GCTrans` can call `VPurgeVolume` for timed-out temporary volumes marked `DESTROY_ME`, deleting volume data as cleanup for abandoned create/clone/restore operations.
- If a transaction has an active Rx call pointer, `DeleteTrans` marks that call dead with `rxi_CallError`.

Reference counts and flags are the core safety mechanism. A transaction marked `TTDeleted` remains allocated until the final `TRELE`, preventing use-after-free while other code still holds references.

## Dependencies and Integration Points

The module depends on `volser.h` for `struct volser_trans` and flags, `volser_internal.h` for logging, Rx for call errors, and the volume package for detach/purge operations. It is driven by:

- `volprocs.c`, which creates, finds, releases, and deletes transactions for every RPC.
- `volmain.c`, whose background thread calls `GCTrans` and checks `TransList` for idle unlock behavior.
- `voltrans_inline.h`, which updates debug fields stored inside `struct volser_trans`.

## Risks and Edge Cases

- `TransList` returns the raw list head without locking. Callers must take `VTRANS_LOCK` when traversing in concurrent builds.
- `transCounter` monotonically increments without wrap handling. Extremely long-lived processes could eventually wrap transaction ids.
- `DeleteTrans` assumes the passed pointer is still in `allTrans`; misuse returns `-1` and may leave attached state untouched.
- GC drops and reacquires `VTRANS_LOCK` around `VPurgeVolume`; the code accounts for list mutation, but future edits must preserve that care.
- Refcount changes are protected by `VTRANS_LOCK`, while debug fields use per-transaction locks in pthread builds. New fields need a clear locking rule.

## Test Signals

Tests should cover duplicate transaction rejection for the same volume/partition, find/release lifecycle, delete while another reference is held, final `TRELE` after `TTDeleted`, detach on delete, Rx call cancellation on delete, GC warning and timeout behavior, GC purge of abandoned temporary volumes, and concurrent monitor/list traversal under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/voltrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/voltrans_inline.h -->
# sources/distributed-fs/openafs/src/volser/voltrans_inline.h

## Purpose

`voltrans_inline.h` provides small inline helpers for updating the debug/tracking fields of a `struct volser_trans`. The fields record the most recent Rx call and procedure name for transaction status reporting and for aborting calls when a transaction is deleted.

## Important APIs

- `TSetRxCall_r(struct volser_trans *tt, struct rx_call *call, const char *name)` updates `lastProcName` and `rxCallPtr` while the caller already holds the transaction object lock.
- `TClearRxCall_r(struct volser_trans *tt)` clears `rxCallPtr` while the caller already holds the transaction object lock.
- `TSetRxCall(struct volser_trans *tt, struct rx_call *call, const char *name)` wraps `TSetRxCall_r` with `VTRANS_OBJ_LOCK` / `VTRANS_OBJ_UNLOCK`.
- `TClearRxCall(struct volser_trans *tt)` wraps `TClearRxCall_r` with the same locking.

The helpers copy procedure names with `strlcpy` into the fixed-size `lastProcName` field and only update fields when non-null arguments are provided where applicable.

## Control Flow Role

RPC implementations call `TSetRxCall` before long-running or externally visible work and `TClearRxCall` when done. Some code that already holds the transaction lock uses the `_r` variants to avoid double-locking. `VolMonitor` later reports these fields, and `DeleteTrans` can signal the tracked call with `RX_CALL_DEAD`.

## State and Persistence Behavior

The helpers modify only in-memory fields in `struct volser_trans`. They have no direct persistence behavior. Indirectly, accurate `rxCallPtr` state affects whether transaction deletion can abort a live Rx call, and accurate `lastProcName` improves operational diagnosis of long-running or stuck volume operations.

## Dependencies and Integration Points

This header includes `volser.h` for `struct volser_trans` and lock macros. It is used by `volprocs.c` and depends on the transaction object's locking model defined by `volser.p.h`. The stored fields are read by `VolMonitor` in `volprocs.c` and used by `DeleteTrans` in `voltrans.c`.

## Risks and Edge Cases

- The `_r` variants require the caller to hold the transaction lock. Calling them unlocked in pthread builds can race with monitoring or deletion.
- Passing `NULL` for `name` leaves the previous `lastProcName` in place. That is useful for call updates but can mislead diagnostics if callers expect it to clear.
- `TClearRxCall` clears only the call pointer, not `lastProcName`; monitoring can show the last operation even after the call finishes.
- Non-pthread builds compile transaction object locks as no-ops, so correctness relies on the broader LWP/global-lock execution model.

## Test Signals

Tests should inspect `SAFSVolMonitor` output during active dump/restore/forward calls, after call completion, and after transaction deletion. Race-focused tests should verify no stale live `rxCallPtr` remains after normal completion and that deletion of a transaction with an active call reports the call as dead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/voltrans_inline.h -->
