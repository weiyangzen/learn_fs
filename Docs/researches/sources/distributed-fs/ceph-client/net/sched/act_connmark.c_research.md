# sources/distributed-fs/ceph-client/net/sched/act_connmark.c

Purpose: implements the `connmark` TC action, copying a netfilter connection mark into `skb->mark` so classifier/qdisc policy can use conntrack state.

Important APIs/functions: `tcf_connmark_act()` performs lookup and mark copy; `tcf_connmark_init()` creates/replaces action parameters; `tcf_connmark_dump()` reports action and zone; `tcf_connmark_cleanup()` releases RCU parameters. Parameters are stored in `struct tcf_connmark_parms` with net namespace, zone, and action.

Control flow: runtime updates lastuse/basic stats, determines IPv4 or IPv6 protocol, first tries `nf_ct_get()` from the skb, and if absent builds a conntrack tuple from the packet and looks it up in the configured zone. On success it assigns `skb->mark = ct->mark`, releases any lookup reference, increments overlimit stats as a "marked packet" counter, and returns the configured action.

State and persistence: action instances live in the shared TC IDR. Mutable parameters are replaced under the action lock and freed with `kfree_rcu()`. Packet state is changed by writing `skb->mark`; conntrack table state is read only.

Dependencies and integration: depends on `NETFILTER`, `NF_CONNTRACK`, and `NF_CONNTRACK_MARK`; integrates TC action registration/pernet state, RCU parameter lookup, and nf_conntrack tuple APIs.

Risks: packets without valid IPv4/IPv6 headers or conntrack entries pass through without mark changes. Zone mismatch or tuple extraction failure silently leaves the old skb mark. The action uses overlimits as a semantic counter, so stats readers need to know this convention.

Test signals: IPv4/IPv6 packets with attached ct, ingress packets requiring tuple lookup, non-IP packets, configured zones, mark copy correctness, replacement cleanup under traffic, and statistics indicating marked packets.
