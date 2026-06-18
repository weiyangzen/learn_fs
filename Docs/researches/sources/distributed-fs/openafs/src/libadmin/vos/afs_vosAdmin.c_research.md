# sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.c

## Purpose

`afs_vosAdmin.c` is the public VOS administration library implementation. It validates libadmin cell/server handles, translates public `vos_*` API calls into VLDB and volserver RPC/procedure calls, exposes iterator APIs for multi-result queries, and maps internal OpenAFS volume/VLDB structures into public structs from `afs_vosAdmin.h`.

## Important APIs, Types, and Functions

The private `file_server_t` wraps an RX volserver connection with magic/is-valid fields. `IsValidServerHandle` and `IsValidCellHandle` enforce handle validity. `GetServerAndPart`, `copyVLDBEntry`, and `copyvolintXInfo` perform important internal-to-public mapping.

Major exported API families include backup creation, partition get/list, server open/close/sync, fileserver address change/remove/list, transaction status iteration, VLDB get/list/remove/unlock/entry-lock/site-create/site-delete/sync, volume create/delete/rename/dump/restore/online/offline/get/list/move/release/zap/quota-change, partition name/id conversion, `vos_VolumeGet2`, and `vos_ClearVolUpdateCounter`.

Iterator families use `afs_admin_iterator_t` with per-family state structs: `partition_get_t`, `server_get_t`, `transaction_get_t`, `vldb_entry_get_t`, and `volume_get_t`. Each supplies RPC-fill, cache-copy, and sometimes destroy callbacks to `IteratorInit`.

## Control Flow

Most exported functions follow the same pattern: validate arguments, optionally normalize server/partition/volume state, call a lower-level `UV_*`, `AFSVol*`, or `ubik_VL_*` function, set `*st`, and return 1/0. Server handles are opened with `util_AdminServerAddressGetFromName`, token security from the cell handle, and `rx_GetCachedConnection`; they are closed with `rx_ReleaseCachedConnection`.

Read iterators first fetch a bulk list or count from the server/VLDB, initialize an iterator, and lazily copy cached entries to callers via `IteratorNext`. Empty result sets mark the iterator as already done with `ADMITERATORDONE`.

Destructive or persistent operations delegate to established volume-server procedures. For example, create/delete/move/release/zap use `UV_CreateVolume`, `UV_DeleteVolume`, `UV_MoveVolume`, `UV_ReleaseVolume`, and `UV_VolumeZap`/`UV_NukeVolume`. Quota and update-counter changes open explicit volserver transactions with `AFSVolTransCreate`, call `AFSVolSetInfo`, and always attempt `AFSVolEndTrans` if a transaction was opened.

## State and Persistence Behavior

Local state is heap-allocated handles and iterator caches. Persistent state lives remotely in VLDB and volume servers. Functions can change VLDB entries, locks, server addresses, volume placement, volume metadata, volume contents via restore, and quota/update-counter fields. Local dump/restore paths read or write files through `UV_DumpVolume` and `UV_RestoreVolume`.

## Dependencies and Integration Points

This file integrates the libadmin public ABI with `vsprocs`, `vosutils`, `lockprocs`, RX, ubik VLDB RPCs, volserver RPCs, and adminutil iterator/cell-handle infrastructure. It requires valid AFS tokens in the cell handle before opening volserver connections.

## Risks and Edge Cases

`vos_ServerOpen` allocates `file_server_t` before validation and does not free it on failure, so invalid arguments or failed name/connection lookups leak memory. `vos_VolumeMove` computes `from_server_addr` and `to_server_addr` from `from_server->serv` and `to_server->serv` before validating either handle; null/invalid handles can crash before the error path. `vos_VolumeRestore` allows a null `serverHandle` through its conditional validation but then unconditionally dereferences `f_server->serv`, so null server handles can crash.

`GetTransactionFromCache` copies `sizeof(vos_serverTransactionStatus_p)` instead of `sizeof(vos_serverTransactionStatus_t)`, so callers can receive only pointer-sized prefixes of transaction status entries. `vos_VLDBGetBegin` failure cleanup checks `entry->entries` before checking `entry != NULL`, which can dereference null after allocation failure. `vos_VolumeGetBegin` failure cleanup frees `entry` without freeing `entry->vollist` if `UV_XListVolumes` succeeded but later iterator setup failed. `vos_VLDBEntryRemove` deletes a named volume first, then can continue into bulk delete validation and fail with `ADMVOSVLDBDELETEALLNULL`, which makes the single-delete path report failure after already mutating state.

Some exported functions ignore `callBack`, despite accepting it. Partition bounds checks vary between `ADMVOSPARTITIONTOOLARGE` and `ADMVOSPARTITIONIDTOOLARGE`. `copyVLDBEntry` copies all `VOS_MAX_REPLICA_SITES` slots rather than only `nServers`, which is safe only if source structures are initialized.

## Test Signals

Unit tests should cover null and invalid handles for every public API, especially `vos_VolumeMove`, `vos_VolumeRestore`, and iterator begin failure paths under allocation fault injection. Integration tests should exercise each iterator family through empty, single-entry, multi-entry, and done states. Destructive operation tests need an isolated cell to verify create/delete/move/release/zap/restore, VLDB lock/unlock/site mutation, server address changes, and transaction cleanup on errors. ABI tests should validate that every `afs_vosAdmin.h` declaration is implemented and that transaction status entries copy complete data.
