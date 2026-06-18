# sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_client.c

## Purpose
`llog_client.c` implements the client-side remote llog operations table. It adapts generic `llog_operations` callbacks to PTLRPC requests so a client can open an existing remote log, fetch next or previous blocks, and read the log header from a server-side llog origin.

## Important APIs, types, and functions
The exported object is `llog_client_ops`, with callbacks `llog_client_open`, `llog_client_next_block`, `llog_client_prev_block`, `llog_client_read_header`, and `llog_client_close`. The helper `llog_client_entry()` safely gets a referenced `obd_import` from `llog_ctxt::loc_imp` under `loc_mutex`; `llog_client_exit()` releases it and warns if the context import changed during the RPC.

Each RPC uses layout descriptors from `layout.c`: `RQF_LLOG_ORIGIN_HANDLE_CREATE`, `RQF_LLOG_ORIGIN_HANDLE_NEXT_BLOCK`, `RQF_LLOG_ORIGIN_HANDLE_PREV_BLOCK`, and `RQF_LLOG_ORIGIN_HANDLE_READ_HEADER`, with fields `RMF_LLOGD_BODY`, `RMF_NAME`, `RMF_MDT_BODY`, `RMF_EADATA`, and `RMF_LLOG_LOG_HDR`.

## Control flow
Open obtains the import, rejects `LLOG_OPEN_NEW` by assertion because remote creation is unsupported, allocates a create/open request, sets the variable name length even when no name exists so later fields are positioned correctly, packs the request, fills `llogd_body` with optional logid and context index (`loc_idx - 1`), copies the name, calls `do_pack_body()`, waits, and copies the returned logid to the handle.

`llog_client_next_block()` and `llog_client_prev_block()` allocate packed requests, fill `llogd_body` with log id, context index, header flags, block index, requested length, and for next-block the current saved index and offset. They set server `RMF_EADATA` size to the requested buffer length, set reply length, wait for the RPC, copy returned cursor state, then copy the returned data buffer into the caller's buffer. The next-block path has special handling for `-EBADR` and `-EIO`: those codes are accepted as remote EOF-like status only when the reply message status also carries the same value; otherwise the transport error is returned directly.

`llog_client_read_header()` requests the header, validates that the returned header length fits in `lgh_hdr_size`, copies it, updates `lgh_last_idx`, and checks header magic, tail length equality, power-of-two length, minimum chunk size, and maximum handle header size. Close is a no-op because servers close the local file after each remote llog RPC.

## State and persistence behavior
The file does not store persistent data directly. It reads persistent llog contents through server RPCs. It updates in-memory `llog_handle` state: `lgh_id`, `lgh_ctxt`, `lgh_hdr`, `lgh_last_idx`, cursor index, and cursor offset. Import references are acquired per operation and released before return.

## Dependencies and integration points
It depends on `obd_class` import lifetime helpers, PTLRPC allocation/packing/waiting, and generic llog interfaces. Its server peers are implemented in `llog_server.c`; its import is initialized by `llog_net.c`. The llog request/reply layouts come from `layout.c`.

## Risks and edge cases
The code assumes caller-provided buffers are at least `len` bytes and copies exactly `len` from `RMF_EADATA`; server-side lengths therefore must match client expectations. `body->lgd_ctxt_idx = loc_idx - 1` relies on consistent one-based context indexing in the local context and zero-based RPC field. EOF detection is subtle because `-EBADR` and `-EIO` can mean either remote end-of-log or lower-layer failure. Header validation catches corrupt or incompatible logs, but only after copying the advertised header length.

## Test signals
Tests should cover open by logid and by name, absent import retry behavior, next-block cursor advancement and EOF handling for both old `-EIO` and newer `-EBADR` servers, previous-block reads, corrupted header magic and invalid header sizes, import replacement during an operation, and no-op close semantics.
