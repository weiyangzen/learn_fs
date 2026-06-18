# sources/distributed-fs/ceph-client/net/tipc/addr.h

## Purpose
This header declares TIPC address helpers and the internal user address shape aligned with `sockaddr_tipc`.

## Important APIs, Types, And Functions
`struct tipc_uaddr` mirrors TIPC socket address variants for service address, service range, and socket address. Inline helpers include `tipc_uaddr()`, `tipc_uaddr_valid()`, `tipc_own_addr()`, `tipc_own_id()`, `tipc_own_id_string()`, `tipc_cluster_mask()`, `tipc_node2scope()`, `tipc_scope2node()`, and `in_own_node()`. External declarations expose the address functions implemented in `addr.c`.

## Control Flow
The validation helper checks minimum sockaddr length, family `AF_TIPC`, and address type. Service ranges are accepted only when upper is greater than or equal to lower. Scope helpers map node address presence to node or cluster scope and translate node scope back to the namespace's own node address.

## State And Persistence
No independent state is stored here. Inline accessors read `struct tipc_net` per-net namespace identity fields.

## Dependencies And Integration Points
The header depends on Linux TIPC UAPI types, network namespace generic storage, and `core.h`. It is included by socket, name-table, bearer, and address-management code that needs TIPC address interpretation.

## Risks And Test Signals
Risks include ABI layout drift between `tipc_uaddr` and `sockaddr_tipc`, accepting malformed lengths, and scope conversion errors for anonymous or cluster-scoped addresses. Test signals include sockaddr validation coverage, bind/connect/sendmsg address tests, and compile-time review when UAPI address structures change.
