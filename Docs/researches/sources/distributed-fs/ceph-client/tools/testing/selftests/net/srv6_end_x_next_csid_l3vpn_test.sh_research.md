# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_x_next_csid_l3vpn_test.sh

Purpose: this kselftest validates Linux SRv6 End.X with the `next-csid` flavor in an L3 VPN topology. It builds four router namespaces and two host namespaces, configures IPv4 and IPv6 VPN service over compressed SID containers, and confirms both single-container and two-SID policy forwarding.

Important APIs and functions: the script sources `lib.sh` for `setup_ns`, `cleanup_all_ns`, and kselftest return codes. It uses `ip netns`, `ip -6 route ... encap seg6local action End.X`, `flavors next-csid lblen ... nflen ...`, `End.DT46`, VRF links, dummy links, proxy ARP/NDP, and `ping`. Key helpers include `build_ipv6_addr`, `build_csid`, `build_lcnode_func_prefix`, `set_end_x_nextcsid`, `set_end_x_ll_nextcsid`, `setup_rt_local_sids`, `__setup_l3vpn`, `csid_container_cfg_tests`, and the connectivity check wrappers.

Control flow: prerequisites check root, `ip`, `ping`, `sysctl`, `grep`, `cut`, iproute2 next-csid support, dummy device support, and VRF support. `setup` creates namespaces, router meshes, host VRFs, local SID lookup tables, reduced-encap policies, End.DT46 decap routes, and End.X next-csid adjacencies. Tests first validate C-SID layout acceptance and rejection, then router reachability, host gateway reachability, IPv6 and IPv4 VPN connectivity, and finally link-local next-hop variants for End.X.

State and persistence: all state is transient kernel namespace state. `SETUP_ERR` decides whether cleanup exits as skip or with accumulated `ret`. `nsuccess` and `nfail` track test accounting. Namespace names are shell variables created through `setup_ns`; routes and rules live only until `cleanup_all_ns` runs through the EXIT trap.

Dependencies and integration points: depends on Linux SRv6 seg6local, NEXT-C-SID support in kernel and iproute2, VRF strict mode, dummy netdev, IPv4 forwarding, IPv6 forwarding, and network namespace support. It integrates with `tools/testing/selftests/net/lib.sh` and kselftest skip/fail conventions.

Risks: the test is root-only and can be skipped by missing iproute2 features even when the kernel has support. It assumes specific return code `2` for invalid C-SID route additions. It also relies on shell `eval` namespace variables and on route command formatting remaining stable. The topology is dense, so setup failures can mask behavior as skips.

Test signals: success is observable through OK lines for valid and invalid C-SID container configurations, router pair pings, host gateway pings, IPv4/IPv6 host VPN pings, and repeated VPN pings after switching End.X next-hop programming to IPv6 link-local mode. Any failed ping or unexpected C-SID route return increments `nfail` and exits nonzero.
