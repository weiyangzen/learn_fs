# sources/distributed-fs/ceph-client/net/netfilter/nft_tproxy.c

Purpose: nftables `tproxy` expression for transparent proxy socket assignment in prerouting using optional address and port registers.

Important APIs/types/functions: `struct nft_tproxy`, `nft_tproxy_eval_v4()`, `nft_tproxy_eval_v6()`, `nft_tproxy_init()`, `nft_tproxy_destroy()`, `nf_tproxy_get_sock_*()`, and `nf_tproxy_assign_sock()`.

Control flow: init validates family and register lengths, requires address or port input, and enables IPv4/IPv6 defrag. Eval accepts only TCP/UDP non-fragments, reads transport ports, finds established sockets, handles TCP TIME_WAIT, falls back to listener lookup, and assigns only transparent sockets.

State and persistence: expression stores register selectors and family; defrag references persist while the rule exists. Dependencies include nf_tables registers, nf_tproxy, inet sockets, and nf_defrag. Risks: defrag enable/disable balance, socket reference consumption, family/register mismatch, and break behavior for unsupported packets. Test signals: IPv4/IPv6/inet rules, address-only and port-only use, non-transparent sockets, fragments, TIME_WAIT, and defrag cleanup.
