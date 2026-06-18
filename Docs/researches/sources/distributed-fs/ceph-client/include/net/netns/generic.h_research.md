# sources/distributed-fs/ceph-client/include/net/netns/generic.h

Purpose: Defines the generic per-net pointer array used by modules to attach private per-namespace data without modifying `struct net`.

Important APIs/types/functions: `struct net_generic` stores a length/RCU header or flexible pointer array. `net_generic(const struct net *net, unsigned int id)` RCU-dereferences `net->gen` and returns `ptr[id]`.

Control flow: Per-net operations with `id` and `size` cause the core to allocate private data and store it in the generic array. Subsystems call `net_generic` to retrieve it.

State and persistence: Runtime per-net pointer array protected by RCU. The header documents that pointers must not be changed while the net namespace is alive and callers must not take private references to the net_generic object itself.

Dependencies/integration: Depends on net namespace core, pernet operations, RCU, and modules needing private netns state such as nftables and synproxy.

Risks/test signals: Test id allocation, array growth under RCU, namespace teardown, invalid id access, and modules obeying lifetime rules.
