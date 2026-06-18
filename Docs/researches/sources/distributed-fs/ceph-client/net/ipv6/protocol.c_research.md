# sources/distributed-fs/ceph-client/net/ipv6/protocol.c

Purpose: Maintains IPv6 protocol and offload dispatch tables for next-header handlers and GSO/GRO offload handlers.

Important APIs, types, and functions: `inet6_protos[MAX_INET_PROTOS]` stores RCU pointers to `struct inet6_protocol` handlers when IPv6 is enabled. `inet6_add_protocol()` and `inet6_del_protocol()` atomically install/remove a handler for a protocol number. `inet6_offloads[MAX_INET_PROTOS]` stores `struct net_offload` handlers, with `inet6_add_offload()` and `inet6_del_offload()` providing the same atomic registration pattern.

Control flow: Add operations use `cmpxchg()` to install only into an empty slot and return `0` on success or `-1` if occupied. Delete operations use `cmpxchg()` to clear only if the current pointer matches the caller's pointer, then call `synchronize_net()` so packet readers finish before module memory can disappear.

State and persistence: Global read-mostly RCU arrays hold registered handlers. State exists for kernel lifetime and is modified by protocol/offload modules; no persistent storage.

Dependencies and integration: Depends on RCU/network synchronization and protocol modules such as IPv6 fragment handling, TCP/UDP, and offload providers. Consumers read these tables during packet input and offload processing.

Risks and test signals: Risks are handler slot collisions, deleting the wrong pointer, and missing synchronization causing use-after-free. Tests should cover duplicate add failures, mismatched delete failures, module unload after unregister, packet traversal during unregister, and offload registration symmetry.
