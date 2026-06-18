# sources/distributed-fs/openafs/src/volser/volprocs.c

## Purpose

`volprocs.c` implements the server-side Volser RPC procedures behind the generated `AFSVolExecuteRequest` dispatcher. It is the operational core for remote volume administration: partition queries, volume creation/deletion, clone/reclone, transaction create/end, dump/restore/forward, status and metadata changes, volume listings, transaction monitoring, RO-to-RW conversion, dump sizing, and volume splitting.

The file follows a wrapper pattern: exported `SAFSVol*` functions perform audit logging and call static `Vol*` implementations that contain authorization, transaction lookup, volume package calls, filesystem synchronization, and error handling.

## Important APIs, Types, and Functions

Major exported RPC entry points include partition/listing calls (`SAFSVolPartitionInfo`, `SAFSVolPartitionInfo64`, `SAFSVolListPartitions`, `SAFSVolXListPartitions`, `SAFSVolListOneVolume`, `SAFSVolXListOneVolume`, `SAFSVolListVolumes`, `SAFSVolXListVolumes`), mutating calls (`SAFSVolNukeVolume`, `SAFSVolCreateVolume`, `SAFSVolDeleteVolume`, `SAFSVolClone`, `SAFSVolReClone`, `SAFSVolRestore`, `SAFSVolSetFlags`, `SAFSVolSetInfo`, `SAFSVolSetIdsTypes`, `SAFSVolSetDate`, `SAFSVolConvertROtoRWvolume`, `SAFSVolSplitVolume`), transfer calls (`SAFSVolTransCreate`, `SAFSVolEndTrans`, `SAFSVolForward`, `SAFSVolForwardMultiple`, `SAFSVolDump`, `SAFSVolDumpV2`, `SAFSVolGetSize`), and diagnostics (`SAFSVolGetFlags`, `SAFSVolGetStatus`, `SAFSVolGetName`, `SAFSVolMonitor`, `SAFSVolGetNthVolume`, `SAFSVolSignalRestore`).

Important helpers include `VPFullUnlock`, partition/volume name converters, retrying attach wrappers, `ViceCreateRoot`, `MakeClient`, `GetNextVol`, `FillVolInfo`, demand-attach `GetVolObject`, and `GetVolInfo`. Local abstraction types `volint_info_type_t`, `volint_info_handle_t`, and `vol_info_list_mode_t` share listing fill logic between base and extended wire structures.

## Control Flow

Most mutating RPCs authorize with `afsconf_SuperUser`, find or create a `struct volser_trans`, reject `VTDeleted`, record the active call with `TSetRxCall`, perform volume package or FSYNC work, update headers with `VUpdateVolume`, clear the tracked call, and release or delete the transaction with `TRELE` or `DeleteTrans`. Query RPCs use `afsconf_CheckRestrictedQuery` and the daemon's `restrictedQueryLevel`.

Create flow initializes a new volume, optionally creates the root directory, marks it out of service and `DESTROY_ME` until setup completes, writes metadata, and returns a transaction id. Clone/reclone validate source/target relationships, run `CloneVolume`, update names/types/dates/stats, detach targets, update originals, and break callbacks. Dump/restore/forward stream volume dumps over Rx and coordinate remote restores. Listing scans partition directories for volume headers and optionally attaches volumes to fill `volintInfo` or `volintXInfo`. `VolMonitor` walks active transactions under locks and reports transaction and Rx call state.

## State and Persistence Behavior

This file directly mutates volume state through `VCreateVolume`, `VUpdateVolume`, `VDetachVolume`, `VPurgeVolume`, `CloneVolume`, `RestoreVolume`, `nuke`, RO-to-RW conversion helpers, and `split_volume`. It changes volume ids, types, names, quotas, timestamps, service/blessed state, destroy/salvage flags, backup/clone fields, stats, disk usage, and root vnode/ACL data. It coordinates with the file server through `FSYNC_VolOp` for callback breaks, move forwarding, volume checkout/onlining, query state, pending operations, and salvage scheduling.

In-memory state includes transaction-held attached volumes and debug call/procedure fields. Global policy from `volmain.c` controls query authorization, stats preservation, and outbound server-to-server encryption.

## Dependencies and Integration Points

The file integrates Rx RPC, audit, auth, the OpenAFS volume package, partition scanning, dump/restore codecs, FSYNC daemon coordination, transaction management from `voltrans.c`, transaction tracking helpers from `voltrans_inline.h`, and constants/types from `volser.h`.

## Risks and Edge Cases

Important risks include partial persistent state after failures between metadata updates, detaches, FSYNC notifications, and transaction deletion; unusual error mapping for missing create ids; historical 31-character name limits; `VolSetInfo` ignoring `VUpdateVolume` errors on return; multi-forward partial failure semantics; DAFS versus non-DAFS listing differences; temporary listing transactions making busy volumes visible as `VBUSY`; RO-to-RW conversion leaving partially converted data on failure; and lock-order hazards between global and per-transaction locks.

## Test Signals

High-value tests cover authorization boundaries, create/delete/end transaction lifecycle, clone/reclone with stats preservation toggles, dump/restore interruption, forward and multi-forward partial success, listings for busy/offline/destroy/salvage/pending-operation volumes, monitor output during long calls, RO-to-RW conversion failure recovery, and split-volume validation.
