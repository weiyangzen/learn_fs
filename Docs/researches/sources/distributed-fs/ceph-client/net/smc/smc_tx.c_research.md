# sources/distributed-fs/ceph-client/net/smc/smc_tx.c

Purpose: Implements SMC send-buffer producer and consumer logic. It copies user data into the local send ring, controls corking/autocorking, transfers data to peer RMBEs with SMC-R RDMA writes or SMC-D ISM writes, and emits CDC messages that advertise producer/cursor state.

Important APIs/types/functions: `smc_tx_sendmsg()` is the socket send entry point. `smc_tx_sndbuf_nonempty()` pushes prepared data to the peer. `smc_tx_pending()` and `smc_tx_work()` retry sends from process/workqueue context. `smc_tx_consumer_update()` sends receive-side consumer cursor updates. `smcd_tx_ism_write()` performs the SMC-D write primitive. Internal helpers manage write-space wakeups, send waits, cork decisions, RDMA/ISM ring chunking, and cursor advancement.

Control flow: The producer loop validates socket state, handles urgent flags, waits for `sndbuf_space`, copies up to two wrapped chunks from `msghdr` into the send buffer, syncs for device access, advances `tx_curs_prep`, decrements send space, and either corks or triggers the consumer. The consumer computes prepared bytes and peer RMBE space, sets write-blocked flags, breaks source and destination rings into chunks, posts RDMA writes for SMC-R or ISM writes for SMC-D, advances producer/sent cursors, then sends CDC. Completion/slot pressure can reschedule TX work.

State and persistence behavior: State is connection-local: send buffer descriptor, `sndbuf_space`, `peer_rmbe_space`, local and remote CDC controls, prepared/sent cursors, urgent flags, send lock, delayed work, link pointer, and stats. No disk persistence exists.

Dependencies and integration points: Depends on socket wait queues, TCP cork state via the underlying CLC socket, SMC CDC, SMC WR slot management, SMC close wakeups, SMC-D ISM APIs, sysctl autocorking, stats, and tracepoints.

Risks and test signals: Risks include cursor wrap errors, peer RMBE window underflow, urgent-data state bugs, link-change races while holding WR slots, corking latency, and missed wakeups for `EPOLLOUT`. Test blocking/nonblocking sends, partial sends, `MSG_MORE`/TCP_CORK/autocorking, urgent data, SMC-D attached buffers, SMC-R inline and non-inline RDMA, peer window exhaustion/reopen, link failover, and close while data is prepared.
