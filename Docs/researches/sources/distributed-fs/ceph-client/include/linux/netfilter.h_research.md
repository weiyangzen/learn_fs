# sources/distributed-fs/ceph-client/include/linux/netfilter.h

## Purpose
`netfilter.h` defines the in-kernel hook interface for packet filtering, NAT/conntrack integration hooks, checksum/route helpers, and no-op fallback behavior when netfilter is disabled. It is the dispatch contract between protocol paths, hook providers, conntrack/NAT modules, and packet continuations.

## Important APIs, Types, and Functions
Important types include `struct nf_hook_state`, `nf_hookfn`, `struct nf_hook_ops`, `struct nf_hook_entry`, `struct nf_hook_entries`, `struct nf_sockopt_ops`, `struct nf_nat_hook`, `struct nf_ct_hook`, `struct nfnl_ct_hook`, and `struct nf_defrag_hook`. Important helpers include `NF_DROP_GETERR`, `NF_DROP_REASON`, `nf_inet_addr_cmp`, `nf_inet_addr_mask`, `nf_hook_state_init`, `nf_hook`, `NF_HOOK`, `NF_HOOK_COND`, `NF_HOOK_LIST`, `nf_nat_decode_session`, and conntrack fallbacks such as `nf_ct_attach` and `nf_ct_get_tuple_skb`.

## Control Flow
Protocol code calls `nf_hook()` or `NF_HOOK*`. With jump labels, constant hook sites can skip work when no hooks are registered. Otherwise the function enters RCU, selects the per-net hook array by protocol family, initializes state, and calls `nf_hook_slow()` or list variant. Return value `1` means the caller must continue with `okfn`; other verdicts indicate the hook consumed, queued, stolen, or dropped the skb. NAT and conntrack integration is indirect through RCU-published hook tables.

## State and Persistence
State is per-net namespace hook arrays plus global RCU hook pointers for NAT, conntrack, netlink conntrack, and defragmentation. Hook arrays are read under RCU and updated by register/unregister APIs. There is no durable persistence.

## Dependencies and Integration Points
The header integrates with `sk_buff`, `net_device`, sockets, network namespaces, static keys, module ownership, netfilter verdict definitions, conntrack zones, `flowi`, NAT, defrag, and netlink conntrack. Device-level ingress/egress hooks referenced by `struct net_device` point back into this contract.

## Risks
Packet ownership is verdict-dependent and easy to get wrong. Hooks returning stolen/queued/drop must own disposal, while return `1` requires continuation. RCU hook pointer access must be respected. Hook priority ordering affects security behavior. The disabled-netfilter fallback compiles to unconditional `okfn`.

## Test Signals
Register/unregister hooks under packet load with RCU debugging, verify hook priority ordering, exercise all verdicts including `NF_STOLEN` and drop-with-error, build with and without `CONFIG_NETFILTER`, test IPv4/IPv6/ARP/bridge family selection, and cover NAT/conntrack module load/unload.
