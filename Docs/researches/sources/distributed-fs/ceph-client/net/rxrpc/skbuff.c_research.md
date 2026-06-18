# sources/distributed-fs/ceph-client/net/rxrpc/skbuff.c

Purpose: centralizes RxRPC socket-buffer reference/accounting trace helpers. It wraps skb lifecycle events so the subsystem can track outstanding Rx skbs and emit consistent trace records.

Important APIs/functions: `rxrpc_new_skb()` records a newly allocated or received skb, `rxrpc_see_skb()` traces an skb observed in a queue without changing ownership, `rxrpc_get_skb()` increments the accounting counter and takes an skb reference, `rxrpc_free_skb()` decrements accounting and consumes one reference, and `rxrpc_purge_queue()` drains a `sk_buff_head`.

Control flow: all mutating helpers update `rxrpc_n_rx_skbs` through `select_skb_count()` and emit `trace_rxrpc_skb()` with the skb pointer, Linux skb refcount, RxRPC accounting count, and trace reason. `rxrpc_purge_queue()` repeatedly dequeues until empty and consumes each skb.

State and persistence: the only persistent state is the global atomic skb count used for diagnostics. Actual packet memory lifetime remains owned by Linux skb refcounting; these helpers must be paired correctly with real `skb_get()`/`consume_skb()` ownership changes.

Dependencies and integration: used by RxRPC receive/input queues and cleanup paths; depends on Linux skbuff APIs, `rxrpc_skb_trace` values, and subsystem tracepoints.

Risks: because the diagnostic counter is manually maintained, missing a helper call or calling the wrong one creates misleading leak accounting even when the skb refcount is correct. `rxrpc_see_skb()` intentionally does not validate or retain the skb.

Test signals: trace-based leak checks, queue purge tests on non-empty receive queues, refcount debugging, and subsystem shutdown tests expecting `rxrpc_n_rx_skbs` to return to zero.
