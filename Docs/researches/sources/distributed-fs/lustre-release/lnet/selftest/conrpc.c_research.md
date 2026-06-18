# sources/distributed-fs/lustre-release/lnet/selftest/conrpc.c

## Purpose
Implements the console-side RPC transaction layer for LNet Selftest. It converts console session, group, batch, test, debug, and stats operations into SRPC client RPCs, groups them into `lstcon_rpc_trans` transactions, waits for completion, aggregates results, and runs the session pinger.

## Important APIs And Functions
Key structures are `lstcon_rpc` and `lstcon_rpc_trans`. Core lifecycle functions are `lstcon_rpc_trans_prep()`, `lstcon_rpc_trans_addreq()`, `lstcon_rpc_trans_postwait()`, `lstcon_rpc_trans_abort()`, `lstcon_rpc_trans_destroy()`, and `lstcon_rpc_cleanup_wait()`. Request builders include `lstcon_sesrpc_prep()`, `lstcon_dbgrpc_prep()`, `lstcon_batrpc_prep()`, `lstcon_testrpc_prep()`, and `lstcon_statrpc_prep()`. Reply/stat handling is done by `lstcon_rpc_get_reply()`, `lstcon_rpc_trans_stat()`, `lstcon_rpc_stat_reply()`, and `lstcon_rpc_trans_interpreter()`.

## Control Flow
Callers create a transaction, add per-node RPCs, post all requests, release the session mutex while waiting, then reacquire it to abort unfinished RPCs on timeout, interruption, or shutdown. `lstcon_rpc_done()` is the SRPC completion callback; it records status and timestamp, marks the wrapper finished, decrements the transaction remaining counter, and wakes the waiter when all RPCs complete. Test client-add RPCs allocate bulk pages and pack destination process IDs; server-add RPCs compute loop needs without sending destination bulk.

## State And Persistence
All state is volatile and rooted in `console_session`: active transaction list, console RPC freelist, RPC live counter, node timestamps/states, feature masks, and pinger timer. No disk persistence exists. Embedded node ping RPCs are reset in place rather than recycled.

## Dependencies And Integration Points
Depends on `console.h`, `conrpc.h`, `timer.h`, `selftest.h`, SRPC framework helpers (`sfw_create_rpc()`, `sfw_post_rpc()`, `sfw_abort_rpc()`, `sfw_unpack_message()`), LNet NID conversion, wait queues, spinlocks, atomics, pages, and user-copy helpers.

## Risks
Important risks are orphaned posted RPCs after transaction destruction, timestamp-sensitive node-down marking, destination span/distribution errors, mixed feature negotiation returning `EPROTO`, and pinger interactions with shutdown and embedded RPC list membership.

## Test Signals
Exercise session create/end, feature mismatch, add-test bulk destination packing, transaction timeout and abort behavior, pinger recycle/stop paths, and final assertions that the freelist is empty and live RPC counter is zero.
