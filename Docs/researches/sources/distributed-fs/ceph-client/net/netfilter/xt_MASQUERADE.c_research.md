# sources/distributed-fs/ceph-client/net/netfilter/xt_MASQUERADE.c

Purpose: `MASQUERADE` NAT target performs automatic-source SNAT using the outgoing interface address.

Important APIs/types/functions: `masquerade_tg_check()`, `masquerade_tg()`, `masquerade_tg6_checkentry()`, `masquerade_tg6()`, notifier registration via `nf_nat_masquerade_inet_register_notifiers()`, and destroy.

Control flow: check rejects explicit MAP_IPS and invalid IPv4 range count, then pins conntrack. Runtime builds/uses NAT range and calls IPv4/IPv6 masquerade helper in POST_ROUTING. Module init registers targets then masquerade notifiers with unwind.

State and persistence: conntrack refs per rule, NAT bindings in conntrack, and global masquerade notifiers. Dependencies include nat table, nf_nat_masquerade, conntrack, and netdevice/address notifications. Risks: notifier registration order, legacy range conversion, ref symmetry, and disallowed explicit mapping. Test signals: MAP_IPS rejection, range size validation, IPv4/IPv6 postrouting, notifier failure unwind, address change cleanup, and destroy put.
