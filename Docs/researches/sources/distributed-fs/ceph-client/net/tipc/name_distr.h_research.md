# sources/distributed-fs/ceph-client/net/tipc/name_distr.h

## Purpose
`name_distr.h` defines the compact on-wire item used by TIPC name distribution and declares the publication distribution API used by the name table and node receive paths. It is the contract between local publication storage and `NAME_DISTRIBUTOR` protocol messages.

## Important APIs, Types, And Functions
The header defines `ITEM_SIZE` as `sizeof(struct distr_item)` and `struct distr_item`, whose network-byte-order fields are `type`, `lower`, `upper`, `port`, and `key`. Public prototypes are `tipc_named_publish()`, `tipc_named_withdraw()`, `tipc_named_node_up()`, `tipc_named_rcv()`, `tipc_named_reinit()`, and `tipc_publ_notify()`.

## Control Flow
The header itself has no executable flow. Callers publish or withdraw a local `struct publication`, pass the returned skb to broadcast/replicast as needed, invoke `tipc_named_node_up()` when a peer link becomes reachable, feed queued received distributor messages through `tipc_named_rcv()`, and call `tipc_publ_notify()` when a peer is lost.

## State And Persistence
No state is allocated by the header. The persistent state it describes is encoded as `distr_item` records inside `NAME_DISTRIBUTOR` message payloads. The comments explicitly define that all fields are network byte order and that the publishing node is not stored per item because it is inferred from the enclosing message.

## Dependencies And Integration Points
The header includes `name_table.h` for `struct publication` and publication-related types. It is included by `name_distr.c`, `name_table.c`, `net.c`, and `node.c`, tying together socket publication changes, node up/down events, and receive-side name table updates.

## Risks And Edge Cases
Any layout or byte-order change is wire-protocol visible. Because node identity is implicit in the containing message, callers must not process a `distr_item` without a validated `msg_orignode()`. `ITEM_SIZE` is used for MTU packing and receive item counts, so padding or struct layout changes would affect compatibility.

## Test Signals
Compile-time ABI checks, publication encode/decode tests, mixed-endian interoperability, MTU packing tests using `ITEM_SIZE`, receive validation of item counts, and compatibility tests with legacy and non-legacy name distribution all exercise this header's contract.
