# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.h

## Purpose

`rxe_ns.h` declares per-network-namespace RXE socket accessors and namespace registration hooks, including IPv6-disabled stubs.

## Important APIs, Types, and Functions

It exposes `rxe_ns_pernet_sk4()`, `rxe_ns_pernet_set_sk4()`, optional `rxe_ns_pernet_sk6()`, optional `rxe_ns_pernet_set_sk6()`, `rxe_namespace_init()`, and `rxe_namespace_exit()`.

## Control Flow

RXE initialization registers namespace support, and network setup uses the socket accessors to lazily create, reuse, and release pernet UDP tunnel sockets.

## State and Persistence Behavior

No state is stored in the header. It exposes RCU-managed socket pointers implemented in `rxe_ns.c`.

## Dependencies and Integration Points

It connects RXE transport setup to Linux network namespace lifecycle and is included by `rxe_net.c`.

## Risks and Edge Cases

IPv6 stubs return `NULL` and ignore setters, so callers must treat IPv6 tunnel creation as optional. Include order may matter if `struct net` or `struct sock` are not already visible.

## Test Signals

Build with and without IPv6 and run RXE device setup/teardown inside network namespaces.
