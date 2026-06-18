# sources/distributed-fs/openafs/src/rx/rx.c lines 8630-9761

## Purpose

This chunk implements the public and internal tail of RX RPC statistics handling, plus a few platform/debug helpers near the end of `rx.c`. It begins in the middle of `rx_CopyProcessRPCStats`, whose prologue at lines 8624-8629 allocates a single `rx_function_entry_v1_t` copy buffer; the visible lines complete the copy, lookup, and release behavior for one process-level RPC operation statistic. The rest of the statistics block records per-call timing/byte counts, marshals process and peer statistics into the rxstat wire representation, exposes query/enable/disable/clear controls, and installs the authorization callback used by the rxstat service.

The non-statistics tail contains Windows DLL initialization, optional debug dumping of all live RX calls, socket error-queue draining and retry-aware sends for platforms with `AFS_RXERRQ_ENV`, the common `rxi_NetSend` wrapper used by packet transmission code, and `rxi_GetLocalAddr`, which reports the loopback-or-bound local address RX should use for packets sent to itself.

## Important APIs, Types, and Functions

- `rx_CopyProcessRPCStats(afs_uint64 op)` completes a single-operation process-stat copy. `op` packs `rxInterface` in the high 32 bits and `currentFunc` in the low 32 bits. It requires process stats to be enabled, rejects interface `-1`, finds the matching `rx_interface_stat` in `processStats`, copies one `rx_function_entry_v1_t`, and returns an owned blob for accessor helpers in `rx.h`.
- `rx_CopyPeerRPCStats(afs_uint64 op, afs_uint32 peerHost, afs_uint16 peerPort)` mirrors the process copy path for a specific `rx_peer`, using `rxi_FindPeer(peerHost, peerPort, 0)` and the peer's `rpcStats` queue.
- `rx_ReleaseRPCStats(void *stats)` frees the one-entry blob returned by the copy helpers.
- `rxi_AddRpcStat(...)` is the shared update primitive. It finds or creates an `rx_interface_stat` entry, verifies that the recorded function count matches the caller's interface shape, bounds-checks `currentFunc`, then increments invocation count, byte counters, queue/execution time sums, squared sums, and min/max clocks.
- `rxi_IncrementTimeAndCount(...)` is the internal recorder called by `rx_RecordCallStatistics` in `rx_call.c`. It updates peer and/or process queues depending on `rxi_monitor_peerStats` and `rxi_monitor_processStats`.
- `rx_IncrementTimeAndCount(...)` is the legacy public wrapper for older rxgen stubs. It converts `afs_hyper_t` byte counters to `afs_uint64` and delegates to `rxi_IncrementTimeAndCount`.
- `rx_MarshallProcessRPCStats(...)` serializes an array of `rx_function_entry_v1_t` records as `afs_uint32` words. Each 64-bit counter is split into high and low words, and each `struct clock` contributes `sec` and `usec`.
- `rx_RetrieveProcessRPCStats(...)` and `rx_RetrievePeerRPCStats(...)` snapshot all enabled process or peer stats into an allocated wire buffer for rxstat service responses.
- `rx_FreeRPCStats(...)` releases buffers allocated by the retrieve APIs.
- `rx_queryProcessRPCStats`, `rx_queryPeerRPCStats`, `rx_enableProcessRPCStats`, `rx_enablePeerRPCStats`, `rx_disableProcessRPCStats`, `rx_disablePeerRPCStats`, `rx_clearProcessRPCStats`, and `rx_clearPeerRPCStats` are the operational control surface.
- `rx_SetRxStatUserOk` and `rx_RxStatUserOk` manage the authorization callback consulted by `src/rxstat/rxstat.c` before enabling, disabling, or clearing stats through the `MRXSTATS_*` RPCs.
- `rx_DumpCalls(FILE *outputFile, char *cookie)` is available outside the kernel and, when `RXDEBUG_PACKET` is built, writes call queue depths, state, connection IDs, timers, abort state, and optional refcount diagnostics for every `rx_call` in `rx_allCallsp`.
- `rxi_HandleSocketErrors`, `NetSend_retry`, and `rxi_NetSend` isolate platform socket send behavior. `rxi_NetSend` refuses sends after RX shutdown, otherwise calls `osi_NetSend` directly or via error-queue retries.
- `rxi_GetLocalAddr(struct sockaddr_in *sin)` fills the address RX uses for local self-traffic after successful `rx_InitHost`.

The central data types come from `rx.h`: `rx_function_entry_v1_t` stores remote peer/port, direction, interface/function identity, invocation and byte counters, and queue/execution timing aggregates; `rx_interface_stat_t` embeds queue links plus a flexible `stats[1]` array that this code allocates as `sizeof(rx_interface_stat_t) + totalFunc * sizeof(rx_function_entry_v1_t)`. Clear flags such as `AFS_RX_STATS_CLEAR_INVOCATIONS` and `AFS_RX_STATS_CLEAR_EXEC_TIME_MAX` select fields for bulk zeroing or min/max reset.

## Control Flow

RPC statistics collection starts when an admin or server initialization path calls one of the enable functions. Both enable functions take `rx_rpc_stats`, set global `rx_enable_stats = 1`, and set either `rxi_monitor_processStats` or `rxi_monitor_peerStats`. The global `rx_enable_stats` is consumed by generated rxgen stubs; modern generated stubs call `rx_RecordCallStatistics`, which computes queue time as `call->startTime - call->queueTime` and execution time as current time minus `call->startTime`, then calls `rxi_IncrementTimeAndCount`.

`rxi_IncrementTimeAndCount` exits immediately if neither monitor flag is set. Otherwise it holds `rx_rpc_stats` across the whole update. For peer stats it also takes `peer->peer_lock`, adds or updates an entry on `peer->rpcStats`, and, on first creation, links the same stat object into the global `peerStats` queue via `entryPeers`. For process stats it adds or updates an entry in `processStats` using wildcard remote host/port values `0xffffffff`. `rxi_AddRpcStat` rejects inconsistent interface metadata before writing counters, so a reused interface id with a different `totalFunc` or an out-of-range function index will silently skip that invocation by returning `-1`.

Snapshot retrieval follows a two-phase shape. `rx_RetrieveProcessRPCStats` and `rx_RetrievePeerRPCStats` initialize all out parameters to empty success, set `*myVersion = RX_STATS_RETRIEVAL_VERSION`, acquire `rx_rpc_stats`, and return an empty success if the relevant monitor is disabled. For supported callers, they compute `space = stat_count * sizeof(rx_function_entry_v1_t)` using `rxi_rpc_process_stat_cnt` or `rxi_rpc_peer_stat_cnt`, allocate that much memory through `rxi_Alloc`, then scan `processStats` or global `peerStats` and call `rx_MarshallProcessRPCStats` for each interface's function array. On allocation failure they return `ENOMEM` after leaving the result pointer null. The rxstat service wraps these functions and reports `rpcStats_len` as allocated bytes divided by `sizeof(afs_uint32)`.

Disabling process stats holds `rx_rpc_stats`, clears `rxi_monitor_processStats`, disables global `rx_enable_stats` if peer monitoring is also off, walks `processStats` with `opr_queue_ScanSafe`, unlinks every stat, frees its flexible allocation, and decrements `rxi_rpc_process_stat_cnt` by the freed function count.

Disabling peer stats clears `rxi_monitor_peerStats` and potentially `rx_enable_stats`, then walks every bucket of `rx_peerHashTable`. For each bucket it takes `rx_peerHashTable_lock` and `rx_rpc_stats`, tries to acquire each peer lock, and only clears peers whose `peer_lock` is immediately available. For a clearable peer it temporarily unlinks the peer from the hash chain, bumps neighboring and target refcounts before dropping the hash-table lock, removes all per-peer `rpcStats` entries from both the peer queue and `peerStats`, frees each allocation, decrements `rxi_rpc_peer_stat_cnt`, releases `peer_lock`, reacquires the hash-table lock, drops temporary refs, and continues. Peers whose lock cannot be acquired are left in place and skipped for that pass.

The two clear functions keep stat objects allocated but reset selected fields. They scan `processStats` or `peerStats` under `rx_rpc_stats`, iterate over each interface's `func_total`, and apply the requested bitmask. Counters and sums are zeroed, max clocks are set to zero, and min clocks are reset to the sentinel `9999999` seconds/useconds used by the allocator/clear path.

The send helper path is short: `rxi_NetSend` first checks `rxi_IsRunning()`. If RX is still running it delegates to `NetSend_retry` when `AFS_RXERRQ_ENV` is enabled; that helper retries `osi_NetSend` up to `RXI_SENDMSG_RETRY` times, draining pending asynchronous socket errors with `rxi_HandleSocketErrors` after failed attempts. Without that build option it calls `osi_NetSend` once. If RX is no longer running, `rxi_NetSend` returns `WSAESHUTDOWN` on Windows or `ESHUTDOWN` elsewhere.

## State and Persistence Behavior

All stats in this chunk are in-memory runtime state. There is no durable persistence; disabling stats frees the currently accumulated structures, while clear operations preserve structure identity but reset selected fields. Process stats accumulate for the process lifetime until disabled or cleared. Peer stats are tied to `rx_peer` lifetime and are also represented in the global `peerStats` queue so retrieval can scan all peer-backed stat blocks without traversing every peer hash bucket.

The state accounting is explicit: `rxi_rpc_process_stat_cnt` and `rxi_rpc_peer_stat_cnt` count function entries, not interface objects. They are incremented by `totalFunc` when `rxi_FindRpcStat` creates an interface stat and decremented by the same function count when freeing. Retrieval uses those counters to size the serialized output, so counter/queue drift would either truncate marshaling, overrun the allocation, or report misleading `statCount`.

The monitor flags gate both collection and retrieval. `rx_enable_stats` is a broader exported flag that generated stubs test before invoking the recorder; `rxi_monitor_processStats` and `rxi_monitor_peerStats` select which queues are actually updated. Query and enable paths consistently use `rx_rpc_stats`, but `rx_disablePeerRPCStats` writes `rxi_monitor_peerStats` and `rx_enable_stats` before taking `rx_rpc_stats`, making those particular flag transitions more concurrency-sensitive than the process-disable path.

Socket helper state is limited to transient error queues and the global RX running flag. `rxi_HandleSocketErrors` preserves userland `errno`, allocates a 256-byte control-message buffer, repeatedly calls `osi_HandleSocketError` until no pending errors remain, then frees the buffer. `rxi_GetLocalAddr` reads the global `rx_host` and `rx_port`; it returns the configured bind address when nonzero or IPv4 loopback `127.0.0.1` otherwise.

## Dependencies and Integration Points

- Generated rxgen stubs test `rx_enable_stats` and call `rx_RecordCallStatistics`, which lives in `rx_call.c` and feeds this chunk's `rxi_IncrementTimeAndCount`.
- `src/rxstat/rxstat.c` exposes these APIs through the `RX_STATS_SERVICE_ID` service. Retrieve/query methods call directly into the retrieval/query functions, while enable/disable/clear methods first call `rx_RxStatUserOk`.
- Server and client initialization code such as `bosserver`, `kaserver`, `ptserver`, `vlserver`, `viced`, `volser`, and kernel pioctl paths can enable process stats directly.
- `rx.h` publishes the stat structs, clear flags, retrieval version constants, and inline accessors such as `RPCOpStat_NumCalls`, `RPCOpStat_BytesSent`, and `RPCOpStat_ExecTimeSum` for one-entry copy blobs.
- `rx_prototypes.h` exports the process/peer retrieval, query, enable/disable, clear, copy, release, authorization, `rxi_NetSend`, and local-address helper prototypes to other RX components.
- `rxi_NetSend` is the common network send dependency for `rx_packet.c` packet transmission, multi-packet sends, raw abort sends, and internal keepalive/challenge paths in `rx.c`.
- Queue manipulation depends on `opr_queue` primitives; memory management uses `rxi_Alloc`/`rxi_Free`; timing math uses `clock_GetTime`, `clock_Add`, `clock_AddSq`, `clock_Lt`, and `clock_Gt`.
- Platform integration is controlled by build flags: `AFS_NT40_ENV` for `DllMain` and Windows shutdown codes, `RXDEBUG_PACKET` for call dumping, `RX_ENABLE_LOCKS`/`RX_REFCOUNT_CHECK` for extra dump fields, and `AFS_RXERRQ_ENV` for Linux-style asynchronous socket error handling.

## Risks and Edge Cases

- Both copy helpers allocate their one-entry buffer before checking monitor flags, `rxInterface == -1`, and peer existence. Early returns on those checks do not free `rpcop_stat`, so repeated failed copy calls can leak `sizeof(rx_function_entry_v1_t)` allocations. The not-found-after-lock path does free correctly.
- `rx_CopyPeerRPCStats` returns without releasing the allocated copy buffer if `rxi_FindPeer` fails. It also does not visibly release a peer reference after a successful `rxi_FindPeer`; whether that is correct depends on `rxi_FindPeer`'s refcount contract from earlier in the file.
- `currentFunc` from the low 32 bits of `op` is not bounds-checked in the copy helpers before indexing `rpc_stat->stats[currentFunc]`. In contrast, update path `rxi_AddRpcStat` explicitly rejects out-of-range `currentFunc`. A malformed copy request for a valid interface could read past the allocated stats array.
- Retrieval allocates `rxi_rpc_*_stat_cnt * sizeof(rx_function_entry_v1_t)` bytes but marshals `rx_function_entry_v1_t` as 28 `afs_uint32` words per function, not necessarily the in-memory struct size on every ABI. The type definition and comment warn that version/format changes require care; any padding or layout change must preserve the allocation-versus-marshaled-word contract.
- `rx_RetrieveProcessRPCStats` and `rx_RetrievePeerRPCStats` set `*allocSize = space` before confirming allocation success. On `ENOMEM`, callers should rely on the returned code and null `*stats`, not on `allocSize` alone.
- `rx_disablePeerRPCStats` skips peers whose lock cannot be acquired with `MUTEX_TRYENTER`, so disabling peer stats may leave old per-peer stat structures allocated until peer destruction, shutdown cleanup, or a later disable pass that can acquire the lock.
- `rx_disablePeerRPCStats` mutates monitor/global flags outside `rx_rpc_stats`, unlike query, enable, and process disable. Concurrent recorders may observe transitional state inconsistently, especially because generated stubs gate on `rx_enable_stats` before entering this code's locked update path.
- The peer-disable loop temporarily removes peers from the hash chain while freeing stats, then does not reinsert them in the visible block. That may be intentional because this code is trying to isolate peers during cleanup, but it is a high-risk area: peer hash traversal, refcount bumps, and stat freeing are interleaved under multiple locks.
- Clear functions reset min clocks to `9999999`, matching allocation initialization. Tests and reporting tools must treat that sentinel as "no sample yet" after a clear.
- `rxi_NetSend` returns a positive shutdown errno (`ESHUTDOWN`/`WSAESHUTDOWN`) without calling `osi_NetSend` after RX shutdown, while other send errors may be platform-specific positive or negative codes. Callers such as `rx_packet.c` treat any nonzero return as failure, but tests should not assume a single sign convention for all errors.
- `NetSend_retry` drains all pending socket errors after each failed send attempt. This can consume asynchronous errors caused by other peers or threads, which is acknowledged by the comment; the recovery model relies on RX packet retransmission tolerating occasional dropped sends.
- `rx_DumpCalls` locks each call while formatting fields but traverses `rx_allCallsp` without an obvious global list lock in this chunk. It is debug-only, but concurrent call teardown could be a concern depending on surrounding debug build invariants.

## Test Signals

- Enabling process stats should make `rx_queryProcessRPCStats` nonzero and set exported `rx_enable_stats`; disabling process stats should clear process monitoring, free `processStats`, decrement `rxi_rpc_process_stat_cnt` to zero, and clear `rx_enable_stats` only when peer stats are also disabled.
- Enabling peer stats should make `rx_queryPeerRPCStats` nonzero and cause `rxi_IncrementTimeAndCount` to create entries in both a peer's `rpcStats` queue and the global `peerStats` queue.
- A recorded call should increment exactly one function entry's invocation count, add sent/received bytes, update queue and execution sums/squares, and adjust min/max clocks from the sentinel values.
- Mismatched `totalFunc` for an existing interface id/direction should not corrupt or resize the existing stats array; out-of-range `currentFunc` should be rejected by the recorder.
- Retrieval with stats disabled should return success with `statCount == 0`, `allocSize == 0`, and `stats == NULL`. Retrieval with stats enabled and records present should return `myVersion == RX_STATS_RETRIEVAL_VERSION`, a current clock stamp, and a `statCount` equal to the function-entry counter.
- Marshaling tests should verify field order and 64-bit high/low splitting for invocations, bytes sent, and bytes received, plus `sec/usec` pairs for every queue and execution clock aggregate.
- `rx_FreeRPCStats` should be paired with successful retrieve allocations, and `rx_ReleaseRPCStats` should be paired with successful single-operation copy blobs.
- Clear-flag tests should cover individual bits and `AFS_RX_STATS_CLEAR_ALL`, confirming that counters/sums zero, max fields zero, and min fields reset to `9999999`.
- Rxstat service tests should verify authorization: with no `rx_SetRxStatUserOk` callback or a callback returning false, enable/disable/clear RPCs return `EPERM`; retrieve/query/version paths remain callable.
- Peer-disable tests should include peers whose locks are held so the `MUTEX_TRYENTER` skip path is exercised, then verify whether skipped stat objects remain reachable or are cleaned by a later pass.
- `rxi_NetSend` tests should cover running versus shutdown states, direct `osi_NetSend` behavior without `AFS_RXERRQ_ENV`, retry behavior with a failing first send and drained socket errors, and eventual propagation of the last nonzero send error after retry exhaustion.
- `rxi_GetLocalAddr` should return `rx_host:rx_port` when RX was initialized with a bind host and `127.0.0.1:rx_port` when `rx_host == 0`.
