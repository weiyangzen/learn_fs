# sources/distributed-fs/ceph-client/net/tipc/link.c

## Purpose

`link.c` is the core TIPC link reliability layer. It creates unicast and broadcast links, runs the link finite-state machine, sequences outgoing packets, manages transmit/backlog/deferred queues, handles acknowledgements/NACKs/retransmission, fragments/reassembles input, supports failover/synchronization tunneling, exchanges link protocol state, integrates monitor domain records, and exports link netlink diagnostics.

## Important APIs, Types, and Functions

`struct tipc_link` is the main state object: peer/session/bearer identity, tolerance/abort limits, FSM state, capabilities, monitor state, MTU, transmit queue, backlog by importance, receive sequencing, input/name queues, wakeup queue, reassembly state, congestion window state, broadcast send/receive fields, failover queues, and `struct tipc_stats`. Public APIs include link creation, state predicates, reset, xmit/receive, timeout, state/reset message builders, failover/tunnel preparation, broadcast peer add/remove/sync/ack/nack helpers, property setters, netlink dump helpers, and `tipc_link_dump()`.

Key internal routines include `tipc_link_fsm_evt()`, `tipc_link_update_cwin()`, `tipc_link_advance_backlog()`, `tipc_link_advance_transmq()`, `tipc_link_proto_rcv()`, `tipc_link_build_proto_msg()`, `tipc_data_input()`, `tipc_link_input()`, and `tipc_link_tnl_rcv()`.

## Control Flow

Transmit starts in `tipc_link_xmit()`. It validates MTU, checks per-importance backlog limits, schedules SOCK_WAKEUP pseudo messages on congestion, assigns sequence/ACK/broadcast-ACK fields to packets that fit the congestion window, clones packets into the caller xmit queue, stores originals in `transmq`, and queues or bundles overflow into `backlogq`. ACK processing through data packets, STATE messages, or broadcast ACKs calls `tipc_link_advance_transmq()` to release acked packets and retransmit missing ranges, then updates congestion window and advances backlog.

Receive starts in `tipc_link_rcv()`. LINK_PROTOCOL packets go to `tipc_link_proto_rcv()`. Data packets reset silence counters, validate link state and receive window, release acked transmit packets, defer out-of-order packets with NACK generation, deliver in-order packets upward, and drain deferred packets when gaps close. `tipc_data_input()` routes normal data, connection manager, group protocol, name distributor, crypto, bundler, fragmenter, tunnel, and broadcast protocol users. Fragmented and bundled messages are unpacked before delivery.

Timeout builds RESET, ACTIVATE, or STATE/probe messages depending on FSM state, silence count, monitor probing, unacked receive data, broadcast ACK needs, and transmit queue pressure. Link protocol receive validates sessions and capabilities, handles RESET/ACTIVATE establishment, updates MTU/tolerance/priority, ingests monitor domain data, replies to probes, and processes gap ACK blocks.

## State and Persistence Behavior

All state is in memory per link. The FSM moves among RESETTING, RESET, PEER_RESET, FAILINGOVER, ESTABLISHING, ESTABLISHED, and SYNCHING. Sequence state persists in `snd_nxt`, `rcv_nxt`, state-message sequence numbers, broadcast acked/receive state, and failover drop points. Queue state persists in `transmq`, `backlogq`, `deferdq`, `wakeupq`, and reassembly buffers. Congestion state persists in `window`, `ssthresh`, `cong_acks`, `checkpoint`, and per-importance backlog limits.

## Dependencies and Integration Points

The file depends on TIPC core, subscriptions, broadcast, sockets, name distribution, discovery, netlink, monitor, trace, optional crypto, Linux skb and traffic priority helpers. It integrates with node code for locking and xmit scheduling, bearer code for packet transmission, group/socket receive queues, broadcast global locks, monitor domain gossip in STATE messages, crypto `MSG_CRYPTO` handling, and generic netlink link/stat reporting.

## Risks and Edge Cases

This is a dense reliability state machine. Risks include illegal FSM transitions, sequence wrap mistakes, retransmission storms, stale gap ACK block state, wakeup starvation, memory leaks in reassembly/failover queues, MTU mismatch during tunneling, and broadcast ACK/NACK storms. Broadcast sender and per-peer receiver links share state but have different semantics. Optional crypto reduces MSS; missing that adjustment causes oversize encrypted packets.

## Test Signals

Exercise link establishment/reset, silent peer timeout, priority/tolerance changes, congestion/backlog wakeups, fragmentation and bundling, out-of-order receive with NACK/retransmit, broadcast peer add/remove, gap ACK blocks with broadcast and unicast gaps, failover and synchronization tunneling, monitor threshold changes, crypto-enabled MSS, and netlink link/stat dumps.
