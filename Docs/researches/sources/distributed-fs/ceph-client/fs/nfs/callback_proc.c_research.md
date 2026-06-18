# sources/distributed-fs/ceph-client/fs/nfs/callback_proc.c

## Purpose
This file implements NFSv4 callback operations after XDR decoding. It handles delegation GETATTR/RECALL, pNFS layout recall and device notifications, v4.1 backchannel sequencing, recall-any and recall-slot requests, lock notifications, and optional v4.2 server-side copy offload completion.

## Important APIs, types, and functions
Exported procedure handlers include `nfs4_callback_getattr()`, `nfs4_callback_recall()`, `nfs4_callback_layoutrecall()`, `nfs4_callback_devicenotify()`, `nfs4_callback_sequence()`, `nfs4_callback_recallany()`, `nfs4_callback_recallslot()`, `nfs4_callback_notify_lock()`, and optional `nfs4_callback_offload()`.

Important helpers include inode lookup by delegation filehandle, layout lookup by stateid or filehandle, `pnfs_check_callback_stateid()`, `initiate_file_draining()`, `initiate_bulk_draining()`, `validate_seqid()`, and `referring_call_exists()`.

## Control flow
Delegation callbacks locate the target inode through the client delegation hash. GETATTR returns change, size, and delegated time attributes only for valid write delegations. RECALL schedules asynchronous delegation return and maps local errors to NFSv4 statuses.

Layout recall locates a layout by stateid or filehandle, commits pending layout data, validates recall sequencing, updates layout stateid, marks matching layout segments for return, and frees commit bucket lsegs. Bulk recalls destroy layouts by fsid or client id. Device notifications iterate decoded notifications, find matching layout drivers, and delete deviceids.

`nfs4_callback_sequence()` validates the session id, backchannel flag, slot id, slot sequence id, cachethis policy, and referring calls before locking the backchannel slot and setting `cps->clp`. Later compound processing frees the slot. Recall-any expires delegation types or triggers pNFS layout recall/state-manager work. Recall-slot lowers the forechannel target slot id.

## State and persistence behavior
The file mutates in-memory NFS client state: delegation return queues, inode attributes, pNFS layout flags and stateids, deviceid cache entries, session slot tables, client state bits, lock wait queues, and copy-offload completion lists. Persistence is protocol-level only: actions schedule RPC state-manager work or complete pending client operations.

## Dependencies and integration points
Dependencies include delegation management, pNFS layout APIs, NFSv4 session slot tables, NFS state manager, tracepoints, lock wait queues, and optional NFSv4.2 copy state. It is invoked exclusively by `callback_xdr.c` after operation decode/preprocessing.

## Risks and test signals
Risks include callback processing without a valid `cps->clp`, slot sequence bugs causing replay/misorder behavior, layout recall races with layoutcommit and bulk recall, wrong stateid comparisons, and memory ownership for decoded device/referring-call arrays. Tests should include v4.0 delegation recalls, v4.1 compound ordering with `CB_SEQUENCE`, layout file/bulk recalls, deviceid delete/change notifications, recall-any type masks, and offload callback matching plus pending-state fallback.
