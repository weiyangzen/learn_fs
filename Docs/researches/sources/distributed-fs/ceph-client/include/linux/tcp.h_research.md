<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tcp.h -->
# sources/distributed-fs/ceph-client/include/linux/tcp.h

## Purpose
defines the kernel TCP socket state structures, request/time-wait variants, option records, SACK/Fast Open helpers, TSQ deferred flags, and socket option setter prototypes used by the networking stack.

## Important APIs, Types, and Functions
The file is 663 lines and exports these visible symbol families: types/enums `tcp_fastopen_cookie`, `tcp_sack_block_wire`, `tcp_sack_block`, `tcp_options_received`, `tcp_request_sock_ops`, `tcp_request_sock`, `tcp_sock`, `tsq_enum`, `tsq_flags`, `tcp_timewait_sock`, `sk_buff`; macros/constants `TCP_FASTOPEN_COOKIE_MIN`, `TCP_FASTOPEN_COOKIE_MAX`, `TCP_FASTOPEN_COOKIE_SIZE`, `TCP_SACK_SEEN`, `TCP_DSACK_SEEN`, `TCP_NUM_SACKS`, `TCP_RMEM_TO_WIN_SCALE`, `TCP_RACK_RECOVERY_THRESH`, `TCP_DEFERRED_ALL`, `tw_rcv_nxt`, `tw_snd_nxt`; function-like macros `tcp_rsk`, `BPF_SOCK_OPS_TEST_FLAG`, `tcp_sk`, `tcp_sk_rw`; inline helpers `__tcp_hdrlen`, `tcp_hdrlen`, `inner_tcp_hdrlen`, `skb_tcp_all_headers`, `skb_inner_tcp_all_headers`, `tcp_optlen`, `tcp_clear_options`, `tcp_rsk_used_ao`, `tcp_passive_fastopen`, `fastopen_queue_tune`, `tcp_move_syn`, `tcp_saved_syn_free`, `tcp_saved_syn_len`, `tcp_mss_clamp`, and 1 more; external prototypes `__tcp_hdrlen`, `skb_transport_offset`, `skb_inner_transport_offset`, `WRITE_ONCE`, `tcp_skb_shift`, `__tcp_sock_set_cork`, `tcp_sock_set_cork`, `tcp_sock_set_keepcnt`, `tcp_sock_set_keepidle_locked`, `tcp_sock_set_keepidle`, `tcp_sock_set_keepintvl`, `__tcp_sock_set_nodelay`, `tcp_sock_set_nodelay`, `tcp_sock_set_quickack`, and 4 more.

## Control Flow
Packet paths use header helpers (`tcp_hdr()`, `tcp_hdrlen()`, inner-header variants, `skb_tcp_all_headers()`) to locate TCP headers in skbs. Listener/SYN processing uses `tcp_request_sock`; established sockets use `struct tcp_sock` embedded after `inet_connection_sock`; time-wait sockets use `tcp_timewait_sock`. Timers, release callbacks, ACK processing, congestion control, Fast Open, SACK/RACK, ECN/AccECN, MPTCP/SMC, MD5/TCP-AO, BPF sock_ops, and pacing update fields in `tcp_sock`.

## State and Persistence Behavior
`struct tcp_sock` is long-lived per connection and stores send/receive sequence space, windows, RTT estimators, congestion state, retransmit and out-of-order queues, timers, ECN counters, Fast Open state, security options, and statistics. Request sockets and time-wait sockets hold reduced state for handshake and TIME_WAIT lifetimes.

## Dependencies and Integration Points
It depends on skbuff, socket, inet connection/timewait state, UAPI TCP definitions, hrtimers, lists, rbtree state, optional TLS, MPTCP, SMC, MD5, TCP-AO, and BPF features. Direct includes are `linux/skbuff.h`, `linux/win_minmax.h`, `net/sock.h`, `net/inet_connection_sock.h`, `net/inet_timewait_sock.h`, `uapi/linux/tcp.h`.

## Risks and Edge Cases
Cacheline layout and field semantics are performance-critical and documented externally. Lockless listener reads require READ_ONCE-style care; endian/header-length mistakes corrupt skb parsing; optional feature fields change layout; and deferred TSQ/timer flags must be drained in release callbacks.

## Test Signals
Run TCP selftests, packetdrill, MPTCP/SMC/TCP-AO/MD5 config builds, GSO/encapsulation header tests, Fast Open and SACK/RACK recovery tests, BPF sock_ops coverage, and cacheline/layout checks from networking documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tcp.h -->
