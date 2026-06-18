# sources/distributed-fs/ceph-client/include/net/netfilter/nf_queue.h

Purpose: Defines the packet queueing interface used to hand netfilter packets to userspace queue handlers such as nfnetlink_queue and later reinject or drop them.

Important APIs/types/functions: `struct nf_queue_entry` stores skb, hook state, hook index, queue id, bridge physical devices, conntrack-unconfirmed flag, and reroute storage. `struct nf_queue_handler` exposes `outfn` and `nf_hook_drop`. APIs include `nf_register_queue_handler`, `nf_unregister_queue_handler`, `nf_queue_entry_get_refs`, `nf_queue_entry_free`, `nf_queue`, and hashing helpers `hash_v4`, `hash_v6`, `hash_bridge`, `nfqueue_hash`.

Control flow: A queue verdict creates an entry, saves hook/device/routing context, dispatches it to the registered handler, and later reinjection resumes at `hook_index`. Queue balancing uses symmetric hashes so both directions tend to select the same queue.

State and persistence: Queued entries hold skb and references until userspace verdict or drop. Hash init uses a random nonzero seed. State is transient but can hold resources if userspace stalls.

Dependencies/integration: Depends on netfilter hooks, skbuff, rhashtable node embedding, IPv4/IPv6/bridge headers, jhash, reciprocal scaling, and bridge netfilter optional fields.

Risks/test signals: Risks include reference leaks, stale route keys, malformed bridge headers, queue imbalance, reinject-after-device-destroy races, and unconfirmed conntrack handling. Test queue-balance, bypass/drop behavior, bridge IPv4/IPv6 packets, namespace exit with queued packets, and userspace timeout scenarios.
