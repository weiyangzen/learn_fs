# sources/distributed-fs/ceph-client/net/netfilter/nft_dup_netdev.c

Purpose: implements the netdev-family nftables `dup` expression that duplicates a packet to an egress interface while rule evaluation continues.

Important APIs/types/functions: `struct nft_dup_netdev` stores the source register containing the output ifindex. `nft_dup_netdev_eval()` reads that ifindex and calls `nf_dup_netdev_egress()`. `nft_dup_netdev_offload()` maps the same action to `FLOW_ACTION_MIRRED` through `nft_fwd_dup_netdev_offload()`.

Control flow: init requires `NFTA_DUP_SREG_DEV` and validates a register load of `sizeof(int)`. Eval performs the duplication without changing the verdict. Dump emits the source register. Offload action reports that this expression is a hardware action. Module init registers an expression type limited to `NFPROTO_NETDEV`.

State/persistence: state is only the register index; no per-packet persistence beyond the cloned/transmitted skb in `nf_dup_netdev_egress()`. Dependencies include nf_tables offload, netdev duplication helpers, and netdev-family hook support. Risks include invalid ifindex values in the register, recursion/loop behavior delegated to duplication helpers, offload mismatch between mirror and software duplicate, and using the expression outside netdev family. Test signals: duplicate to valid and invalid devices, ingress/egress netdev chains, continued rule evaluation after duplication, offload rule generation, and module unload/register cleanup.
