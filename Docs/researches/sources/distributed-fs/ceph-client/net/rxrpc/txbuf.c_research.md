# sources/distributed-fs/ceph-client/net/rxrpc/txbuf.c

Purpose: allocates, traces, and frees RxRPC transmit data buffers used by the send path before packets are secured and queued.

Important APIs/functions: `rxrpc_alloc_data_txbuf()` creates a `struct rxrpc_txbuf` and associated page-fragment data area, `rxrpc_see_txbuf()` emits a trace without changing lifetime, and `rxrpc_put_txbuf()` drops a reference and frees on last put. `rxrpc_free_txbuf()` performs final release. Globals `rxrpc_txbuf_debug_ids` and `rxrpc_nr_txbuf` provide debug identity and live-count accounting.

Control flow: allocation creates the metadata object, computes a data offset after a jumbo header aligned to the security data alignment, allocates aligned data from `conn->tx_data_alloc` under `tx_data_alloc_lock`, initializes refcount/debug fields/space/sequence/client flag, traces allocation, and increments the live count. Put uses `__refcount_dec_and_test()`, traces the new refcount, and frees the page fragment plus metadata when dead.

State and persistence: buffers are transient per call. Persistent state includes live debug counters and connection-level page-frag allocator state. `txb->seq` is set to `call->send_top + 1`, so allocation assumes caller serializes sequencing with the call send path.

Dependencies and integration: called through security-class `alloc_txbuf()` paths and consumed by `sendmsg.c` queueing. Uses page-frag allocation, refcount APIs, tracepoints, and RxRPC connection/call structures.

Risks: data is freed via `page_frag_free(txb->data)` even though `data` points past an internal offset; this relies on page-frag free semantics accepting the returned address. Alignment, offset, and data-size calculations must remain consistent with security headers and jumbo header assumptions. Missing puts leak page-frag memory and `rxrpc_nr_txbuf`.

Test signals: allocation failure injection, alignment-sensitive security modes, send/abort paths that drop pending txbufs, trace count returning to zero, and stress tests around concurrent calls sharing a connection page-frag allocator.
