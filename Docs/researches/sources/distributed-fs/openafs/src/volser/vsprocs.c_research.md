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
