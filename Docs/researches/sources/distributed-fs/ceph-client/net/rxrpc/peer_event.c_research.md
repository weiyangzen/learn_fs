<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_event.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/peer_event.c

## Purpose
`peer_event.c` handles asynchronous peer-level events: ICMP/ICMPv6/local socket errors, PMTU reduction/probing feedback, distribution of peer errors to affected calls, and namespace-wide peer keepalive scheduling.

## Important APIs, Types, And Functions
Important functions include `rxrpc_input_error()`, `rxrpc_peer_keepalive_worker()`, and `rxrpc_input_probe_for_pmtud()`. Internal helpers include `rxrpc_lookup_peer_local_rcu()`, `rxrpc_adjust_mtu()`, `rxrpc_store_error()`, `rxrpc_distribute_error()`, `rxrpc_peer_get_tx_mark()`, and `rxrpc_peer_keepalive_dispatch()`.

## Control Flow
Socket error input reconstructs the remote `sockaddr_rxrpc` from `sock_exterr_skb`, looks up and references the peer under RCU, traces the ICMP data, applies MTU reductions for fragmentation-needed/packet-too-big, or maps the error to local/network call completion and drains `peer->error_targets`. Keepalive work collects new and expired peers from hashed time buckets, optionally uses the local endpoint, sends VERSION keepalives when the last TX time is outside the keepalive window, and requeues peers into future buckets. PMTU probing interprets ACKed probe serials or send failures, adjusts good/bad/trial data sizes and jumbo capacity, and marks pending probes.

## State And Persistence
Persistent peer state includes `if_mtu`, `max_data`, PMTU good/bad/trial/lost/probing/pending fields, `ackr_max_data`, `pmtud_jumbo`, `last_tx_at`, and the peer error target list. Namespace state includes keepalive bucket lists, cursor, base time, timer, and work item.

## Dependencies And Integration Points
This file integrates with UDP error queues, IPv4/IPv6 ICMP metadata, peer lookup from `peer_object.c`, call completion/event input, VERSION keepalive sends from `output.c`, local endpoint active use accounting, and RACK/PMTU logic in ACK handling.

## Risks And Edge Cases
Address reconstruction differs for IPv4 errors on IPv6 sockets and vice versa. MTU reports of zero force heuristic reductions. Error distribution temporarily drops the peer lock while completing calls. Keepalive scheduling relies on signed low-word timestamp reconstruction and bucket cursor arithmetic.

## Test Signals
Test ICMP frag-needed and ICMPv6 packet-too-big handling, local errors distributed to calls, mixed-family error reconstruction, PMTU binary-search progression and lost-probe retry, keepalive bucket scheduling, peer/local refcount balance, and namespace shutdown with keepalive work pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_event.c -->
