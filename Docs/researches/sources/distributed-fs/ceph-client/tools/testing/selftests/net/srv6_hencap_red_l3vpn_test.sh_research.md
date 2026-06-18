# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hencap_red_l3vpn_test.sh

Purpose: this script tests SRv6 `H.Encaps.Red` L3 VPN behavior. It verifies reduced SRH encapsulation for IPv4 and IPv6 VPNs across four SRv6 routers and four hosts, including VPN isolation and optional per-route tunnel source (`tunsrc`) handling.

Important APIs and functions: it uses `ip route ... encap seg6 mode encap.red`, `seg6local action End`, `seg6local action End.DT46 vrftable`, VRF devices, proxy NDP/ARP, `ip6tables -t raw`, and namespace sysctls. Major helpers are `setup_rt_networking`, `setup_rt_local_sids`, `__setup_rt_policy`, `setup_rt_policy_ipv6`, `setup_rt_policy_ipv4`, `setup_hs`, `check_tunsrc_support`, `host_vpn_tests`, and `host_vpn_isolation_tests`.

Control flow: after root and command checks, the script verifies iproute2 has `encap.red`, confirms VRF availability, probes tunsrc support in a temporary namespace, then builds a full-mesh router topology and four access hosts. `setup` installs local End and End.DT46 SIDs, unreachable VRF defaults, and six SRv6 policies covering hs1/hs2 IPv4+IPv6 and hs3/hs4 IPv6. Runtime tests validate router reachability, host-to-gateway reachability, intended VPN connectivity, and cross-VPN isolation.

State and persistence: state is held in netns routing tables, VRFs, ip rules, ip6tables raw rules, and transient shell counters. `HAS_TUNSRC` changes whether deprecated `::dead:<rt>` addresses and tunsrc-specific decap filters are installed. The EXIT trap removes namespaces through `cleanup_all_ns`; no durable state is written.

Dependencies and integration points: relies on `lib.sh`, root, network namespaces, iproute2 SRv6 reduced encap support, VRF strict mode, ip6tables when tunsrc is available, and kernel seg6local End/End.DT46. It is part of selftests/net and reports through kselftest skip/fail exit codes.

Risks: optional tunsrc behavior is silently disabled if either route syntax or ip6tables support is missing, so a pass may not cover tunsrc. Isolation checks expect failed pings to return `1`, which can be fragile across ping variants. The script uses broad namespace names from `setup_ns` and many route entries, so partial setup errors become a skip via `SETUP_ERR`.

Test signals: passing output includes router connectivity, IPv4/IPv6 host-to-gateway checks for all hosts, positive hs1/hs2 and hs3/hs4 VPN reachability, and negative cross-VPN isolation, including IPv4-only isolation between hs2 and hs4. Counter variables produce a final passed/failed summary and nonzero status on test failures.
