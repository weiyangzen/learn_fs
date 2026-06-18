<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_next_csid_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_next_csid_l3vpn_test.sh

## Purpose

`srv6_end_next_csid_l3vpn_test.sh` validates the SRv6 End NEXT-C-SID flavor in an IPv4/IPv6 L3VPN topology. It covers compressed SID containers for reduced encapsulation, transition from a C-SID container to a regular SID, and validation of locator-block/node-function length parameters.

## Important APIs, Types, and Functions

The script sources `lib.sh` and defines helpers for router/host namespace creation, inter-router links, IPv6 address construction (`build_ipv6_addr`), C-SID construction (`build_csid`, `build_lcnode_func_prefix`), local SID setup, VPN policy setup (`__setup_l3vpn`, `setup_ipv4_vpn_2sids`, `setup_ipv6_vpn_1sid`), connectivity checks, C-SID config tests, and feature probes. It uses `encap seg6 mode encap.red`, `encap seg6local action End flavors next-csid lblen ... nflen ...`, and `End.DT46 vrftable`.

## Control Flow

Preflight checks root, `ip`, `ping`, `sysctl`, `grep`, `cut`, iproute2 NEXT-C-SID support, dummy device support, and VRF strict mode. Setup creates four routers and two hosts, a mesh of inter-router links, per-host VRFs, default unreachable routes, NEXT-C-SID local behaviors for each router, localsid rules for regular and compressed locator prefixes, IPv6 one-SID VPN policies, and IPv4 two-SID VPN policies. Runtime first tests valid/invalid C-SID container configurations, then router connectivity, host-gateway connectivity, and IPv4/IPv6 VPN connectivity.

## State and Persistence Behavior

State is namespace-scoped through `setup_ns`/`cleanup_all_ns`: veth links, dummy devices, VRFs, route tables 90 and 91, proxy ARP/NDP, forwarding sysctls, and local SID routes. `SETUP_ERR` causes cleanup to return kselftest skip if setup fails before the test phase.

## Dependencies and Integration Points

It depends on kernel and iproute2 support for SRv6 NEXT-C-SID flavor, `encap.red`, End.DT46, VRF strict mode, dummy devices, IPv4/IPv6 forwarding, and compressed SID locator layout. It integrates with SRv6 compressed SID processing and L3VPN decapsulation into a VRF.

## Risks and Edge Cases

The script constructs IPv6 addresses from hex strings manually, so formatting bugs would change the effective SID. The C-SID config matrix expects invalid route-add attempts to return status 2, which may vary with iproute2 error behavior. It validates reachability, not packet headers, so it infers reduced encapsulation and C-SID advancement from forwarding success.

## Test Signals

Important signals are acceptance/rejection of each C-SID container configuration, all-pairs router reachability, host-gateway IPv4/IPv6 reachability, and bidirectional host VPN reachability for IPv6 one-SID and IPv4 two-SID policies. The summary should report zero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_next_csid_l3vpn_test.sh -->
