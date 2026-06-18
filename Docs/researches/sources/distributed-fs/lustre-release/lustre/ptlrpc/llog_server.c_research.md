# sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_server.c

## Purpose
`llog_server.c` implements server-side handlers for remote llog-origin RPCs. It opens existing local logs on behalf of a client, reads blocks or headers, writes results into the PTLRPC reply capsule, and closes the llog handle after each operation.

## Important APIs, types, and functions
The handlers are `llog_origin_handle_open()`, `llog_origin_handle_next_block()`, `llog_origin_handle_prev_block()`, and `llog_origin_handle_read_header()`. The local helper `llog_origin_close()` dispatches to `llog_cat_close()` for catalog logs and `llog_close()` otherwise. The handlers consume `struct llogd_body`, `struct llog_ctxt`, `struct llog_handle`, and PTLRPC capsule fields defined in `layout.c`.

## Control flow
Open reads the client `RMF_LLOGD_BODY`, packs the reply, optionally treats a nonzero log object id as a logid, reads optional `RMF_NAME`, validates the context index against `LLOG_MAX_CTXTS`, gets the context from the export OBD, opens the existing log by id or name, writes the opened logid into the server body, closes the handle, and drops the context reference.

Next-block and previous-block follow a similar pattern: read body, pre-size server `RMF_EADATA` to `LLOG_MIN_CHUNK_SIZE`, pack the reply, validate/get context, open the log, initialize the handle with flags from the request, mirror the request body into the reply body, get the reply data buffer, and call `llog_next_block()` or `llog_prev_block()`. Next-block passes saved index, target index, current offset, and fixed chunk length so the callee can update cursor state in the reply body.

Read-header reads body, packs a reply containing `RMF_LLOG_LOG_HDR`, validates/get context, opens and initializes the log, copies the in-memory log header into the reply field, logs diagnostic details, then closes and releases.

## State and persistence behavior
The handlers do not create new logs and do not persist changes themselves. They read persistent llog objects through `llog_open()`, `llog_init_handle()`, and block/header readers. Each operation opens and closes a handle, so persistent file lifetime is short and request-scoped. Reply state contains returned logid, block cursor state, data buffers, or header bytes.

## Dependencies and integration points
The code depends on the target export and OBD (`req->rq_export->exp_obd`), service-thread environment (`rq_svc_thread->t_env`), llog context lookup and reference management, local llog open/init/read/close operations, and PTLRPC capsule packing/accessors. Its client peer is `llog_client.c`, and opcode names are surfaced in `lproc_ptlrpc.c`.

## Risks and edge cases
Context index validation is critical because the request carries a zero-based context id. The server always sizes data replies to `LLOG_MIN_CHUNK_SIZE`, while the client can request arbitrary `len`; callers must keep those expectations aligned. The failpoint `OBD_FAIL_MDS_LLOG_UMOUNT_RACE` intentionally exercises context/umount races. All paths must release contexts and close handles on errors. Since remote creation is unsupported, clients expecting create semantics will fail before this server path.

## Test signals
Tests should cover valid and invalid context ids, missing contexts, open by name and id, catalog versus plain log close behavior, next/previous block success and EOF/error propagation, header reads, failpoint-driven unmount races, and leak checks for context references and log handles on every error path.
