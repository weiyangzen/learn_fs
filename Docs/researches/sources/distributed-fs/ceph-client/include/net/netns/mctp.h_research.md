# sources/distributed-fs/ceph-client/include/net/netns/mctp.h

Purpose: Defines per-network-namespace state for MCTP routing, addressing, keys, and sockets.

Important APIs/types/functions: `MCTP_BINDS_BITS` sizes the bound-socket hash. `struct netns_mctp` contains an RCU-freed route list updated under RTNL, `bind_lock`, a `(type, src_eid, dest_eid)` socket bind hash table, `keys_lock` and key hlist for tag allocations, `default_net`, `neigh_lock`, and a neighbours list. `mctp_bind_hash` hashes bind triples with `hash_32`.

Control flow: MCTP route management updates the route list under RTNL while receive paths read routes through RCU. Socket bind/unbind updates the bind hash under `bind_lock`; packet receive can read bind entries under RCU. Tag keys are manipulated in atomic contexts under `keys_lock` and freed after an RCU grace period. Neighbour updates use `neigh_lock`.

State and persistence: Runtime per-net routes, bind hash buckets, tag keys, default network id, and neighbour list. No durable persistence; RCU protects readers and delayed frees.

Dependencies/integration: Depends on MCTP core routing, address management, socket layer, and namespace lifecycle.

Risks/test signals: Test bind hash collisions and wildcard `MCTP_ADDR_ANY` entries, route removal while packets are received, atomic-context key allocation/free, neighbour cleanup, namespace isolation, and default-net behavior.
