# sources/distributed-fs/ceph-client/net/ipv4/tcp_minisocks.c

## Purpose

`tcp_minisocks.c` implements TCP mini-socket behavior: TIME-WAIT sockets, request sockets in SYN-RECV, and creation/processing of full child sockets from completed passive opens. It contains protocol edge handling shared by IPv4 and IPv6 paths, including PAWS, ECN/AccECN inheritance, TCP-MD5/AO TIME-WAIT support, request validation, deferred accept, and child socket dispatch.

## Important APIs, Types, and Functions

TIME-WAIT handling centers on `tcp_timewait_state_process()`, `tcp_time_wait()`, `tcp_time_wait_init()`, `tcp_twsk_destructor()`, and `tcp_twsk_purge()`. Request/child setup uses `tcp_openreq_init_rwin()`, `tcp_ecn_openreq_child()`, `tcp_ca_openreq_child()`, and `tcp_create_openreq_child()`. SYN-RECV packet validation and completion is `tcp_check_req()`. Established child packet handling is `tcp_child_process()`.

Small helpers include `tcp_in_window()` for sequence-window checks, `tcp_timewait_check_oow_rate_limit()` for out-of-window ACK throttling, `twsk_rcv_nxt_update()` for receive-next and AO SNE updates, and `smc_check_reset_syn_req()` for SMC negotiation cleanup.

## Control Flow

`tcp_timewait_state_process()` first parses timestamps when available and performs PAWS checks. FIN-WAIT-2 mini-sockets repeat receive-window checks, ignore duplicate ACKs, reset on new data after half-close, and transition to true TIME-WAIT when the expected FIN arrives. True TIME-WAIT accepts in-window RST/ACK according to RFC1337 policy, updates timestamp state, reschedules timers, and can accept a new SYN if it is not a duplicate and has a safe sequence/timestamp. Out-of-window non-RST packets trigger rate-limited ACKs.

`tcp_time_wait()` allocates an `inet_timewait_sock`, copies mark, priority, window scaling, receive/send sequence, receive window, timestamps, tx delay, queue mappings, IPv6 metadata when applicable, MD5/AO state, and schedules the hashdance. It enforces a timeout at least derived from RTO and uses fixed `TCP_TIMEWAIT_LEN` for true TIME-WAIT. It then updates TCP metrics and closes the original socket.

`tcp_create_openreq_child()` clones the listener, seeds receive/send sequence variables from the request, initializes timers, timestamp options, window scaling, MSS clamp, ECN/AccECN state, Fast Open fields, BPF socket state, user-frag xarray, and passive-open counters.

`tcp_check_req()` validates packets for request sockets. It handles retransmitted SYNs by retransmitting SYN-ACK with rate limiting, rejects invalid ACKs, PAWS failures, TSecr failures, and out-of-window segments, handles RST/SYN errors, tracks AccECN option observations, supports Fast Open short-circuiting, honors `TCP_DEFER_ACCEPT`, creates child sockets, records RTT, and completes the hashdance.

## State and Persistence

Mini-socket state persists only during handshake or TIME-WAIT. TIME-WAIT sockets store enough connection state to validate late packets and generate ACK/RST responses without a full socket. Request sockets store SYN-derived negotiation state until completion or timeout. Child sockets inherit listener configuration plus request-negotiated options.

MD5 keys may be copied into TIME-WAIT and child sockets. AO state is copied or destroyed through TCP-AO helpers. Congestion control for a child can be selected from route metrics or inherited/defaulted by `tcp_ca_openreq_child()`.

## Dependencies and Integration Points

The file integrates tightly with `tcp_ipv4.c` and IPv6 equivalents through request ops and child creation callbacks. It depends on TCP core state processing, inet connection socket cloning, inet timewait hashdance, dst route metrics, ECN/AccECN helpers, XFRM indirectly through callers, PSP policy, busy poll/NAPI marking, SMC, TCP-AO, TCP-MD5, BPF socket clone hooks, and TCP metrics update.

## Risks

Handshake and TIME-WAIT logic is protocol-edge-heavy. Risks include TIME-WAIT assassination policy, accepting reopening SYNs safely, stale timestamp/PAWS decisions, incorrect request ownership during hashdance, listener overflow behavior, Fast Open reset handling, and dropping or accepting bare ACKs under deferred accept. Concurrency is delicate because request sockets can be stolen, migrated, dropped, or completed by another CPU while packets are being processed.

## Test Signals

Exercise passive opens, SYN retransmission, syncookie/TFO paths, deferred accept, accept-queue overflow with and without abort-on-overflow, TIME-WAIT ACK/RST/new-SYN behavior, FIN-WAIT-2 mini-socket transition, PAWS/TSecr rejection counters, AccECN negotiation/failure modes, MD5/AO child and TIME-WAIT signing, route-selected congestion control on passive open, namespace TIME-WAIT purge, and lockdep/refcount coverage during concurrent accept and packet arrival.
