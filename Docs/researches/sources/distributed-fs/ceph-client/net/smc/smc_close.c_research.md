# sources/distributed-fs/ceph-client/net/smc/smc_close.c

## Purpose
`smc_close.c` implements normal and abnormal SMC socket shutdown. It releases internal TCP CLC sockets, cleans up unaccepted children, waits for prepared sends to leave the send buffer, sends CDC close/write-done/abort indicators, cancels pending close/TX work, handles active aborts, drives active close and shutdown-write state transitions, processes peer close/abort work, frees connections, and initializes close work items.

## Important APIs, Types, And Functions
Public functions are `smc_clcsock_release()`, `smc_close_wake_tx_prepared()`, `smc_close_abort()`, `smc_close_active_abort()`, `smc_close_active()`, `smc_close_shutdown_write()`, and `smc_close_init()`. Internal helpers include `smc_close_cleanup_listen()`, `smc_close_stream_wait()`, `smc_close_wr()`, `smc_close_final()`, `smc_close_cancel_work()`, `smc_close_sent_any_close()`, `smc_close_passive_abort_received()`, and `smc_close_passive_work()`.

## Control Flow
Active full close enters `smc_close_active()`. From `SMC_ACTIVE`, it waits up to linger or `SMC_MAX_STREAM_WAIT_TIMEOUT` for prepared TX data, flushes pending TX, cancels delayed TX work, sends final close CDC flags, moves to `SMC_PEERCLOSEWAIT1`, and shuts down the CLC TCP socket. Other states either confirm a peer close, finish after prior shutdown-write, wait for peer final close, or send an abort from `SMC_PROCESSABORT`. `smc_close_shutdown_write()` is the half-close path: from active it flushes data, sends `peer_done_writing`, and moves to `SMC_PEERCLOSEWAIT1`; from passive close it acknowledges write shutdown and moves to `SMC_APPCLOSEWAIT2`.

Passive close is scheduled by CDC receive into `conn.close_work`. `smc_close_passive_work()` locks the socket, interprets `peer_conn_abort`, `peer_conn_closed`, and `peer_done_writing`, transitions among active/passive close states, wakes readers and writers, and frees the SMC connection plus CLC socket when the socket is dead or detached. Active abort marks errors, aborts the TCP CLC socket, cancels close/TX work, drives states to `SMC_CLOSED`, and releases resources depending on whether passive close references remain.

## State And Persistence
Close state is stored in `sk->sk_state`, `sk_shutdown`, `sk_err`, CDC transmit and receive connection-state flags, `conn.killed`, `wait_close_tx_prepared`, delayed TX work, close work, and CLC socket pointer protected by `clcsock_release_lock`. Listen cleanup drains `accept_q` and closes never-accepted SMC children. Socket references are deliberately held for passive close and workqueue paths, with `sock_put()` paired in state transitions.

## Dependencies And Integration Points
The file depends on `smc_tx_prepared_sends()`, `smc_tx_pending()`, CDC send helpers, close predicates from `smc_cdc.h`, connection freeing from SMC core, TCP abort/shutdown/release, socket wait queues, and the shared `smc_close_wq`. It is called from `af_smc.c` release/shutdown/listen cleanup and from CDC receive when peer close flags arrive.

## Risks And Edge Cases
The close state machine is reference-count sensitive. Some states represent postponed passive close and require exactly one `sock_put()`. Work cancellation temporarily releases the socket lock to avoid deadlocks. `smc_close_final()` sends abort instead of clean close if unread bytes remain. Linger and process-exiting paths alter wait duration. CLC socket release must handle listen children and avoid canceling the currently running listen work. Races with peer close can force the active path to restart its switch.

## Test Signals
Useful tests include active close with and without pending corked data, shutdown write followed by peer close, passive peer done-writing, passive peer closed, peer abort with unread data, simultaneous close, close while listen children are queued, release during nonblocking connect/listen work, linger timeout and signal interruption, abnormal link termination, CLC socket release races, and lockdep/refcount/KASAN coverage for close work cancellation and final `sock_put()` paths.
