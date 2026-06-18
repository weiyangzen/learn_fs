# sources/distributed-fs/ceph-client/include/net/netfilter/nf_nat.h

Purpose: Defines NAT manipulation types, conntrack NAT extension state, NAT hook registration, packet translation, checksum repair, and common IPv4/IPv6/inet NAT entry points.

Important APIs/types/functions: `enum nf_nat_manip_type`, `HOOK2MANIP`, `union nf_conntrack_nat_help`, and `struct nf_conn_nat` define state. Public APIs include `nf_nat_setup_info`, `nf_nat_alloc_null_binding`, `nf_ct_nat_ext_add`, `nfct_nat`, `nf_nat_oif_changed`, `nf_nat_register_fn/unregister_fn`, `nf_nat_packet`, `nf_nat_manip_pkt`, checksum and ICMP reply translation helpers, family-specific register/unregister functions, `nf_nat_inet_fn`, `nf_ct_nat`, and `nf_nat_initialized`.

Control flow: NAT rules allocate or find the conntrack NAT extension, set up source or destination ranges, and then packet hooks call `nf_nat_packet`/`nf_nat_manip_pkt` according to hook direction. ICMP errors use reply translation helpers to rewrite embedded packets.

State and persistence: NAT state is stored per conntrack in `NF_CT_EXT_NAT`, with optional PPTP helper data and masquerade interface index. It persists for the conntrack lifetime, not beyond runtime.

Dependencies/integration: Depends on conntrack core/extensions/tuples, uapi NAT ranges, netfilter hook registration, IPv4/IPv6 hooks, masquerade, and helpers such as PPTP.

Risks/test signals: Watch hook-to-manip mapping, status-bit initialization, checksum recalculation after payload rewrite, masquerade egress interface changes, extension allocation failures, and ICMP embedded translation. Test SNAT, DNAT, redirect, masquerade, helper-assisted protocols, namespace teardown, and IPv4/IPv6 parity.
