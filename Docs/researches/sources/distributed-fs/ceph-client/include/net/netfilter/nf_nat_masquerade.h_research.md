# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat_masquerade.h

Purpose: Declares masquerade NAT entry points that derive source addresses from the outgoing interface and clean up flows when interface addressing changes.

Important APIs/types/functions: `nf_nat_masquerade_ipv4`, `nf_nat_masquerade_ipv6`, `nf_nat_masquerade_inet_register_notifiers`, and `nf_nat_masquerade_inet_unregister_notifiers`.

Control flow: NAT rules call the IPv4 or IPv6 masquerade helper with the skb, NAT range, and output device. Notifiers register to observe address/device events that invalidate masqueraded conntracks.

State and persistence: Per-conntrack masquerade state is held through `nf_conn_nat.masq_index` in `nf_nat.h`; notifier registration is process-global runtime state.

Dependencies/integration: Depends on NAT range definitions, netdevice lifetime, IPv4/IPv6 address selection, conntrack cleanup, and notifier chains.

Risks/test signals: Risks include stale conntracks after address changes, wrong output interface index, missing notifier registration, and IPv6 parity. Test interface down/up, address replacement, namespace teardown, multiple egress devices, and rule unload.
