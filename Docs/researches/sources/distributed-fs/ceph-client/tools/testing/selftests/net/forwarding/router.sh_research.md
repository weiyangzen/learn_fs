
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router.sh

Purpose: Router forwarding selftest for edge-case IPv4/IPv6 forwarding and multicast behavior across two routed links.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, `router_create/destroy`, `start_mcd`, `kill_mcd`, `ping_ipv4`, `ping_ipv6`, `sip_in_class_e`, `create_mcast_sg`, `delete_mcast_sg`, `__mc_mac_mismatch`, `mc_mac_mismatch`, `ipv4_sip_equal_dip`, `ipv6_sip_equal_dip`, `ipv4_dip_link_local`, `ipv4_sip_link_local`.

Control flow: starts `smcrouted`, creates host VRFs and router interfaces, enables forwarding, validates basic IPv4/IPv6 reachability, then sends crafted UDP packets with unusual source/destination properties and uses tc egress filters on `$rp2` to assert forwarding. Multicast tests install S,G routes via `smcroutectl`.

State/persistence: creates VRFs, routes, addresses, clsact qdisc on `$rp2`, multicast daemon temp directory/config/pid, tc filters, neighbor entries, temporary routes, and rp_filter sysctl overrides.

Dependencies/integration: requires `$MCD` (`smcrouted`), `$MC_CLI`, `tc_common.sh`, mausezahn, and root privileges.

Risks: `kill_mcd` uses `pkill $MCD`, which may affect unrelated smcrouted processes. Tests disabling rp_filter must restore it. Multicast behavior depends on daemon availability and table name isolation.

Test signals: basic pings pass; tc counters see five forwarded packets for class-E source, multicast MAC mismatch, source-equals-destination, and IPv4 link-local source/destination cases.
