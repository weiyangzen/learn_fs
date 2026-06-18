# sources/distributed-fs/ceph-client/net/smc/smc_rx.c

Purpose: Implements receive-side SMC data handling. It copies or splices data from the local RMBE into user buffers/pipes, advances consumer cursors, handles urgent data, wakes readers, and sends CDC consumer updates to the peer.

Important APIs/types/functions: `smc_rx_recvmsg()` is the socket receive entry point under the socket lock. `smc_rx_wait()` blocks until data/error/shutdown/criterion. `smc_rx_init()` installs `sk_data_ready` and initializes splice and urgent state. Internal helpers include `smc_rx_wake_up()`, `smc_rx_update_consumer()`, `smc_rx_splice()`, `smc_rx_recv_urg()`, and `smc_rx_recvmsg_data_available()`.

Control flow: On receive, the code rejects unsupported error-queue reads, handles listen/not-connected and `MSG_OOB`, computes timeout and low-water target, then loops until the requested target is read or a stop condition occurs. It waits for `bytes_to_rcv`, handles shutdown/error rules, copies up to two ring-buffer chunks to `msghdr` or a pipe, syncs RMB memory for CPU access, decrements `bytes_to_rcv` for non-peek reads, advances the consumer cursor, and sends a CDC update when thresholds, urgent data, or peer requests require it. Splice buffers defer consumer cursor advancement until pipe buffer release.

State and persistence behavior: State lives in `struct smc_connection`: local consumer cursor, `bytes_to_rcv`, urgent state/cursor/byte, `splice_pending`, RMB descriptor and offsets, and CDC flags. Pipe buffer private state holds an SMC socket reference, page reference, and byte count until release.

Dependencies and integration points: Depends on SMC core cursor helpers, CDC update transmission via `smc_tx_consumer_update()`, socket wait queues and async wakeups, splice pipe APIs, tracepoints, and SMC stats. It is called by AF_SMC socket receive paths after CDC receive processing has made data visible.

Risks and test signals: Risks include ring wrap accounting, `MSG_PEEK` interaction with urgent data, splice lifetime/page ownership, memory barriers around `bytes_to_rcv`, and missed consumer updates causing sender stalls. Test normal reads, partial reads, `MSG_WAITALL`, nonblocking timeouts, shutdown/error behavior, urgent byte inline/non-inline, splice and pipe release, wrapped RMB buffers, SMC-R vmalloc RMBs, and CDC update threshold behavior.
