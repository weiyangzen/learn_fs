# sources/distributed-fs/ceph-client/include/net/netfilter/nft_meta.h

Purpose: Declares nftables meta expression state and operations for reading and setting packet, socket, interface, cgroup, mark, priority, and related metadata.

Important APIs/types/functions: `struct nft_meta` stores key, data length, and source/destination register. APIs include get/set init, dump, eval, destroy, validate, and `nft_meta_inner_eval` for inner tunnel context.

Control flow: Netlink init validates the selected meta key and register direction. Datapath eval reads metadata into registers or writes from registers to mutable skb fields. Set validation prevents illegal writes in unsupported hooks or contexts.

State and persistence: Expression-private state is in rules. Writes modify per-packet skb metadata or referenced packet context; no independent persistence.

Dependencies/integration: Depends on `nf_tables.h`, uapi meta keys, skb fields, socket/device/cgroup metadata, and inner tunnel payload context from nft core.

Risks/test signals: Test register lengths, set-only vs get-only keys, mutable metadata in each hook, inner packet evaluation, namespace-sensitive device ids, cgroup/socket edge cases, and dump/init round trips.
