<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_object.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/peer_object.c

## Purpose
`peer_object.c` manages remote transport endpoint records. Peers are deduplicated per local endpoint and remote address, hold route/PMTU/congestion metadata, provide exported kernel query helpers, and integrate with keepalive and error distribution.

## Important APIs, Types, And Functions
Important functions include `rxrpc_lookup_peer_rcu()`, `rxrpc_assess_MTU_size()`, `rxrpc_alloc_peer()`, `rxrpc_new_incoming_peer()`, `rxrpc_lookup_peer()`, `rxrpc_get_peer()`, `rxrpc_get_peer_maybe()`, `rxrpc_put_peer()`, `rxrpc_destroy_all_peers()`, `rxrpc_kernel_get_call_peer()`, `rxrpc_kernel_get_srtt()`, `rxrpc_kernel_remote_srx()`, `rxrpc_kernel_remote_addr()`, `rxrpc_kernel_set_peer_data()`, and `rxrpc_kernel_get_peer_data()`.

## Control Flow
Peer lookup hashes local pointer plus transport address, searches the namespace peer hash under RCU, and either references an existing peer or creates a candidate, assesses its route MTU, then inserts it under `peer_hash_lock` after a race recheck. Incoming peers allocated elsewhere are initialized and inserted into the same hash and keepalive-new list. Refcount drop removes the peer from hash and keepalive lists, asserts no error targets remain, releases the local endpoint, and RCU-frees the peer.

## State And Persistence
`struct rxrpc_peer` persists remote `sockaddr_rxrpc`, hash key/link, local reference, refcount, error target hlist, service connection tree/seqlock, keepalive link, MTU/PMTU data, GSO segment max, recent RTT/RTO, congestion slow-start threshold, debug ID, and application data.

## Dependencies And Integration Points
The file uses route lookup (`ip_route_output_ports`, `ip6_route_output`), namespace peer hash/keepalive lists, local endpoint refs, PMTU/keepalive/event code, connection and call ownership, and exported AF_RXRPC kernel APIs for services such as AFS.

## Risks And Edge Cases
Route lookup failures leave conservative MTU defaults. IPv6 support is conditional. Hash buckets are not sorted despite a compare function. Candidate insertion must handle races without leaking refs. Exported address pointers are borrowed; callers must keep peer lifetime stable.

## Test Signals
Cover concurrent peer lookup races, incoming and outgoing peer insertion, IPv4/IPv6 route MTU assessment, refcount underflow/leak checks, exported app-data helpers, destroy-all leak diagnostics, and PMTU defaults on route failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_object.c -->
