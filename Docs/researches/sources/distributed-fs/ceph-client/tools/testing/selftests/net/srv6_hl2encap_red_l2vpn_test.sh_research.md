# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hl2encap_red_l2vpn_test.sh

Purpose: this selftest validates SRv6 `H.L2Encaps.Red` behavior for an L2 VPN. It tunnels host Ethernet frames carrying IPv4 or IPv6 over an SRv6 router fabric and decapsulates them with End.DX2 to the destination access interface.

Important APIs and functions: it uses `ip route ... encap seg6 mode l2encap.red`, `seg6local action End`, `seg6local action End.DX2 oif`, dummy devices, static neighbor entries, manual MAC assignment, and pings. Important helpers are `setup_rt_local_sids`, `__setup_rt_policy`, `setup_decap`, `set_mac_address`, `set_host_l2peer`, `setup_l2vpn`, `router_tests`, `host2gateway_tests`, and `host_vpn_tests`.

Control flow: root and tool checks are followed by iproute2 `l2encap.red` support and dummy device probing. `setup` creates four router namespaces and two host namespaces, meshes router veth links, assigns router underlay addresses, creates host access links, adds End local SIDs, then configures two directional L2 VPN paths. hs1 to hs2 uses a direct decap SID; hs2 to hs1 traverses rt4 and rt3 before End.DX2 at rt1.

State and persistence: all state is transient network namespace state. The script deliberately rewrites host and router-side access MAC addresses so L2 forwarding and static neighbor entries align with the remote host identity. `SETUP_ERR`, `ret`, `nsuccess`, and `nfail` track execution state, and the EXIT trap invokes namespace cleanup.

Dependencies and integration points: depends on root, network namespaces, iproute2 SRv6 l2 reduced encapsulation, kernel seg6local End and End.DX2, dummy netdev, sysctl, ping, and `lib.sh`. It integrates with kselftest by returning skip before setup completion and fail on connectivity failures.

Risks: Linux SRv6 L2 support is limited here to L2 frames carrying IPv4/IPv6, so other ethertypes are out of scope. The test depends on stable manually generated MAC addresses and static neighbor entries; neighbor learning changes or duplicate MACs would affect results. The destination-side `setup_decap "${rtsrc}"` naming is subtle because `rtsrc` is the decap router for the opposite direction.

Test signals: positive signals are full router mesh pings, host-to-gateway pings for IPv4 and IPv6, and bidirectional hs1/hs2 VPN pings for both protocols. Any unexpected ping failure logs a `[FAIL]` line and the final summary exits with failure.
