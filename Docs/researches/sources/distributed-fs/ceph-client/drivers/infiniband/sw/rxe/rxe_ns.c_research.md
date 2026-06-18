# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.c

## Purpose

`rxe_ns.c` makes RXE network-namespace aware by registering pernet storage for RXE UDP tunnel sockets and releasing those sockets on namespace teardown.

## Important APIs, Types, and Functions

`struct rxe_ns_sock` stores RCU-protected IPv4/IPv6 socket pointers. `rxe_namespace_init()`/`rxe_namespace_exit()` register pernet operations. `rxe_ns_pernet_sk4()`/`set_sk4()` and IPv6 equivalents get and set namespace socket pointers.

## Control Flow

Module init registers the pernet subsystem. Socket creation is deferred until the first RXE device in a namespace calls network initialization. Namespace exit clears stored pointers and releases any remaining UDP tunnel sockets.

## State and Persistence Behavior

The pernet `rxe_ns_sock` instance persists for each network namespace. Socket pointers are RCU-updated and synchronized on writes, allowing lockless readers under RCU assumptions.

## Dependencies and Integration Points

The file uses Linux pernet storage, RCU, network namespaces, and UDP tunnel socket release. `rxe_net.c` uses these accessors to share tunnel sockets across RXE devices in a namespace.

## Risks and Edge Cases

Socket lifetime depends on coordinated reference handling with `rxe_net.c`. Namespace exit can race recent device deletion, so pointers are cleared before release. IPv6 support is conditional and must compile away cleanly.

## Test Signals

Create/delete RXE devices inside multiple net namespaces, test IPv4/IPv6 traffic, delete namespaces with active RXE sockets, unload the module after namespace churn, and build without IPv6.
