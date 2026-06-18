# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower.sh

Purpose: comprehensive flower classifier match test for Ethernet, IPv4, VLAN PCP/VID, TOS/TTL/fragment flags, ingress device, MPLS fields and label-stack entries, and ERSPAN options. It runs with `skip_hw` and optionally `skip_sw`.

Important functions include `match_dst_mac_test`, `match_src_mac_test`, `match_dst_ip_test`, `match_src_ip_test`, `match_ip_flags_test`, `match_pcp_test`, `match_vlan_test`, `match_ip_tos_test`, `match_ip_ttl_test`, `match_indev_test`, `mpls_lse`, `match_mpls_*`, and `match_erspan_opts_test`. Setup creates H1/H2 addresses, clsact on H2, and caches MACs.

Control flow adds pairs or sets of flower filters, sends crafted packets with `$MZ`, checks counters for correct and incorrect filters, removes filters, and repeats in offload mode when supported. MPLS tests manually construct LSE bytes because mausezahn cannot build MPLS in L2 mode; ERSPAN tests create tunnel devices and match decap metadata. State is tc filters, VLAN/tunnel devices, clsact qdisc, and host VRFs. Risks include feature probes, exact packet crafting, offload support, and high counter expectations for the MPLS LSE matrix. Test signals are exact tc packet counters and support-skip helpers for MPLS/ERSPAN.
