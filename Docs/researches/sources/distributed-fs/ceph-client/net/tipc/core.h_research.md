# sources/distributed-fs/ceph-client/net/tipc/core.h

## Purpose
This header centralizes TIPC-wide declarations, constants, common includes, per-net state, and utility helpers.

## Important APIs, Types, And Functions
It defines module version, node hash size, maximum bearers, default monitor threshold, node ID lengths, global externs, and `struct tipc_net`. Inline helpers expose `tipc_net()`, `tipc_netid()`, `tipc_nodes()`, `tipc_name_table()`, `tipc_topsrv()`, `tipc_hashfn()`, 16-bit sequence comparisons, range checks, namespace hash mixing, and `hash128to32()`. It also declares sysctl registration helpers conditionally on `CONFIG_SYSCTL`.

## Control Flow
The sequence helpers implement wraparound-aware comparison for 16-bit link sequence numbers. `hash128to32()` folds a 16-byte ID into a nonzero 32-bit value when possible. Other helpers are simple accessors into per-net generic storage and `struct tipc_net` fields.

## State And Persistence
`struct tipc_net` is the central per-network-namespace state container: node identity/addressing, legacy address flag, node table/list, monitor list, bearer list, broadcast link state, socket hash table, name table, topology server, subscription count, capabilities, loopback packet type, optional crypto, finalize work, and scheduled work count.

## Dependencies And Integration Points
The header includes Linux TIPC UAPI, netlink, netdevice, rhashtable, genl, namespace hash, list/locking/memory headers, and forward declarations for all major TIPC subsystems. It is included widely across TIPC implementation files.

## Risks And Test Signals
Risks include layout changes affecting pernet allocation, sequence comparison edge cases, hash folding assumptions about alignment and byte order, and conditional sysctl stubs hiding missing config coverage. Test signals include broad TIPC builds, sequence-number wrap tests, namespace hash behavior checks, and per-net lifecycle tests that touch every `struct tipc_net` member.
