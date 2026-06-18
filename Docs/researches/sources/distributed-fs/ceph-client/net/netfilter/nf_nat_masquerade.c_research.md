
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_masquerade.c

Purpose: Implements IPv4/IPv6 MASQUERADE source NAT and notifier-driven cleanup of conntracks bound to disappearing devices or addresses.

Important APIs and functions: `nf_nat_masquerade_ipv4()` and `nf_nat_masquerade_ipv6()` select the outgoing interface source address and call `nf_nat_setup_info()`. `nf_nat_masquerade_inet_register_notifiers()` and `_unregister_notifiers()` manage shared notifier registration. Cleanup scheduling uses `nf_nat_masq_schedule()`, `iterate_cleanup_work()`, `device_cmp()`, and `inet_cmp()`.

Control flow: For new/related postrouting packets, IPv4 selects a source address with `inet_select_addr()` and IPv6 with `ipv6_dev_get_saddr()`, records `masq_index` in the NAT extension when available, builds a range with `NF_NAT_RANGE_MAP_IPS`, and delegates setup to NAT core. Device-down or address-removal notifier callbacks schedule bounded background work to iterate conntrack and remove entries matching the interface or address.

State and persistence: Global state includes notifier refcount under `masq_mutex`, atomic worker count, and static notifier blocks. Per-conntrack state stores `nat->masq_index`. Work items hold netns references and optional address filters.

Dependencies and integration: Used by nftables/iptables masquerade expressions. Depends on NAT core, conntrack cleanup iterator, netdevice and inet/inet6 address notifier chains, and per-net lifetime tracking.

Risks: Risks include worker storms from address churn, skipped cleanup when allocation/module ref fails, refcount underflow/overflow, netns lifetime, IPv4 zero-source special case, address selection failure, and cleanup matching reply tuple destination. Test signals include IPv4 and IPv6 masquerade, device down flush, individual address removal, many concurrent notifier events, namespace teardown, and notifier register/unregister nesting.
