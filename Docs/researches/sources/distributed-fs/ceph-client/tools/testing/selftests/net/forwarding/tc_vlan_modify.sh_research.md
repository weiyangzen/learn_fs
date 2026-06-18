# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_vlan_modify.sh

Purpose: verifies `tc action vlan modify id` can translate VLAN IDs at bridge ingress or egress to connect two otherwise separated VLAN endpoints.

Important functions are `switch_create`, `vlan_modify_ingress`, and `vlan_modify_egress`. H1 has base addresses and VLAN 85; H2 has base addresses and VLAN 65. The bridge is VLAN-aware with both VLANs admitted on both switch ports, and clsact on `$swp1/$swp2`.

Control flow first confirms pings from `$h1.85` to `$h2.65` fail for IPv4 and IPv6. In ingress mode it installs filters on each switch-port ingress to rewrite incoming VLAN IDs to the peer VLAN, then expects pings to succeed. In egress mode it rewrites on egress with opposite IDs and expects success. State is bridge VLAN table, VLAN uppers, tc filters, and VRFs. Risks include bridge VLAN membership masking modify failures, filter protocol `all` applying broadly, and cleanup order. Test signals are negative `ping_do`/`ping6_do` before filters and positive checks after VLAN modify filters, logged separately for ingress and egress.
