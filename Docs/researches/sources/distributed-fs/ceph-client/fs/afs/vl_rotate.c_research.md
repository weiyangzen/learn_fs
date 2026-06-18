# sources/distributed-fs/ceph-client/fs/afs/vl_rotate.c

Purpose: Implements volume location server cursor setup, server/address selection, retry rotation, and operation teardown for kAFS VLDB queries.

Important APIs and functions: `afs_begin_vlserver_operation()` initializes `struct afs_vl_cursor`, associates the cell/key, handles pending signals, and seeds the cumulative error state. `afs_select_vlserver()` is the central iterator: it starts DNS/VL server-list lookup, sends VL probes, picks a responsive server by preferred index or lowest RTT, rotates through address lists, records per-address errors, and decides whether to retry or stop. `afs_end_vlserver_operation()` releases cursor-held address/server-list references and returns the prioritized error. `afs_vl_dump_edestaddrreq()` provides bounded debug diagnostics for address resolution failures.

Control flow: First selection triggers `afs_start_vl_iteration()`, which queues cell DNS lookup when records are missing or expired, waits for lookup when necessary, obtains the RCU-protected VL server list under `vl_servers_lock`, and initializes the untried server bitmap. Subsequent calls interpret the previous RPC's `call_error`, `abort_code`, and `call_responded` fields. Network reachability errors rotate addresses; strange VL aborts rotate servers; `-ECONNRESET` marks a whole-list retry; success or local errors stop iteration.

State and persistence: The cursor owns temporary references to `server_list` and `alist`, updates `alist->preferred` when a nonpreferred address responded, and writes `last_error` into the address entry. Persistent cell state includes DNS source/status/expiry and the VL server list. The cumulative error records the most useful terminal reason across probes and calls.

Dependencies and integration points: Depends on AFS cell DNS maintenance, VL probe helpers, RxRPC peers in address lists, trace/debug helpers, and error-prioritization helpers from AFS internals. It is consumed by VL client calls in `volume.c` and server/address refresh code.

Risks: Bitmap construction assumes the server count fits an unsigned long. Correctness depends on balanced `afs_get_*`/`afs_put_*` references on all retry paths and on not using stale address lists after restart. Retry policy affects mount latency and failover behavior under partial outages.

Test signals: Exercise cells with expired DNS, no DNS record, multiple VL servers with mixed RTTs, per-address network failures, unsupported operations, reset-triggered retries, and signal interruption before operation start.
