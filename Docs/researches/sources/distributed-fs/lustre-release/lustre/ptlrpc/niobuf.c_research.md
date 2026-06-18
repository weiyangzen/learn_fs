# sources/distributed-fs/lustre-release/lustre/ptlrpc/niobuf.c

## Purpose
`niobuf.c` is the PTLRPC/LNet buffer transport layer. It binds memory descriptors for request, reply, and bulk data, sends RPCs and replies, registers passive client bulk buffers, starts active server bulk transfers, aborts/unregisters bulk operations, computes adaptive reply timeout metadata, and lowers CPU resume latency around in-flight RPCs when PM-QoS is enabled.

## Important APIs, types, and functions
Global PM-QoS tunables are `ptlrpc_enable_pmqos`, `ptlrpc_pmqos_latency_max_usec`, `ptlrpc_pmqos_default_duration_usec`, and `ptlrpc_pmqos_use_stats_for_duration`. Internal helpers include `ptl_send_buf()`, `mdunlink_iterate_helper()`, `ptlrpc_at_set_reply()`, and `kick_cpu_latency()`.

Server-side bulk APIs under `CONFIG_LUSTRE_FS_SERVER` are `ptlrpc_prep_bulk_exp()`, `ptlrpc_start_bulk_transfer()`, and `ptlrpc_abort_bulk()`. Client/passive bulk APIs are `ptlrpc_register_bulk()` and `ptlrpc_unregister_bulk()`. Reply APIs are `ptlrpc_send_reply()`, `ptlrpc_reply()`, `ptlrpc_send_error()`, and `ptlrpc_error()`. The outbound client send path is `ptl_send_rpc()`, and server request receive buffers are posted by `ptlrpc_register_rqbd()`.

## Control flow
`ptl_send_buf()` constructs an LNet MD for a contiguous buffer, optionally carries a bulk cookie, binds it, bumps `ptlrpc_pending`, and issues `LNetPut()`. If `LNetPut()` fails, it unlinks the MD so the normal callback path completes the failed send and still returns success to the caller.

Server bulk preparation creates a descriptor for an already received request, references the export, sets server mode, and installs `server_bulk_callback`. `ptlrpc_start_bulk_transfer()` derives self and peer NIDs from the request path, computes match bits and MD count, binds each MD, then starts `LNetPut()` for server-to-client bulk put sources or `LNetGet()` for server pulls. On mid-loop errors it adjusts reference counts, unlinks posted MDs, and relies on callbacks for completion. `ptlrpc_abort_bulk()` unlinks all MDs and waits in one-second intervals with long-timeout warnings until callbacks mark the descriptor inactive.

`ptlrpc_register_bulk()` is the client/passive side. It resets reused descriptor state, validates match bits, attaches match entries on the reply portal for each bulk MD, attaches MDs with GET or PUT permissions according to bulk type, and records registration state. Attach failures unlink any partial state, mark request status `-ENOMEM`, and clear `bd_registered`. `ptlrpc_unregister_bulk()` clears registration, optionally sets an async unlink deadline under failpoint control, unlinks MDs, moves the request to `RQ_PHASE_UNREG_BULK` when it must wait, and either returns immediately for async or blocks until callbacks finish.

`ptlrpc_send_reply()` validates the reply state, converts failed-OBD replies to `-ENODEV`, sets reply type/status/opcode, packs pool reply data and adaptive-timeout fields, gets a connection, wraps the reply with security, removes the request from export tracking to avoid resend races, stamps send time, and sends through `ptl_send_buf()` with ACK only for difficult replies that need it. Error helpers allocate a minimal reply if needed and preserve selected non-fatal status codes as regular replies.

`ptl_send_rpc()` is the client outbound path. It handles failpoints, failed imports, connecting imports with non-uptodate peers, message handle/type/connection-count/header flags, resend XID rules for `-EINPROGRESS`, match-bit setup for bulk or reply-matchbits peers, resend callbacks, memalloc context, security wrapping, bulk registration, reply buffer allocation and reply ME/MD attachment, request state flag resets, request reference for send callback, stats, deadline calculation, request send through `ptl_send_buf()`, PM-QoS kick, and cleanup for request-send, reply-attach, and bulk-registration failures.

`ptlrpc_register_rqbd()` posts service request buffers by attaching an LNet ME to the service request portal and an MD over `rqbd_buffer`, using local CPT insertion when available.

## State and persistence behavior
No data is persisted. The file mutates live network state: LNet match entries and memory descriptors, bulk descriptor refs/failure/registration fields, request phases and flags, reply states and refcounts, import/request timestamps and deadlines, service request-buffer refcounts, OBD stats counters, and per-CPU PM-QoS requests/deadlines. Cleanup depends on LNet callbacks to drop pending refs and wake waiters.

## Dependencies and integration points
It depends on LNet APIs (`LNetMDBind`, `LNetPut`, `LNetGet`, `LNetMEAttach`, `LNetMDAttach`, `LNetMDUnlink`), PTLRPC callbacks, security wrapping (`sptlrpc_*`), adaptive timeout helpers, OBD import/export state, lprocfs service stats, CPU latency QoS infrastructure, and failure-injection macros. It is called from PTLRPC client queueing, server reply paths, OST/MDT bulk handlers, and GSS upcall code for no-reply RPC sends.

## Risks and edge cases
The code is concurrency-sensitive because MD callbacks can fire while registration loops are still running. Refcount and phase transitions must stay balanced on all partial-failure paths. `ptl_send_buf()` intentionally returns success after `LNetPut()` failure if unlink/callback will complete the request, which can surprise callers. Bulk match-bit arithmetic must stay aligned between client and server or buffers will not match. Async unregister can leave cleanup pending under deadlines. Reply sending must not lose difficult-reply lock accounting. PM-QoS code allocates per-CPU requests under locks and may return early on allocation failure, leaving later CPUs untouched. Failpoints cover many rare cleanup paths and should remain exercised.

## Test signals
Tests should cover client RPC send with and without replies, reply attach failure, bulk registration attach failure at different MD positions, server bulk put/get success and mid-loop failure, unregister sync and async paths, abort waits and long-unlink warnings, resend after `-EINPROGRESS` with new XID, failed OBD reply conversion, difficult reply ACK/no-ACK behavior, security wrap failures, request buffer posting failure, PM-QoS sysfs tuning effects, and failpoints named in this file (`OBD_FAIL_PTLRPC_*`, `OBD_FAIL_MDS_LLOG_UMOUNT_RACE` for related llog path).
