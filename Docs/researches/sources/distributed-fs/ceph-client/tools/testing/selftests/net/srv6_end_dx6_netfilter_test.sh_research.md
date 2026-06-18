<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx6_netfilter_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx6_netfilter_test.sh

## Purpose

`srv6_end_dx6_netfilter_test.sh` validates SRv6 `End.DX6` forwarding with lightweight-tunnel netfilter hooks and IPv6 raw-table rpfilter rules.

## Important APIs, Types, and Functions

It mirrors the DX4 netfilter test with IPv6 host addressing and `encap seg6local action End.DX6 nh6 ... dev ...`. `setup_rt_netfilter` enables `net.netfilter.nf_hooks_lwtunnel` and installs `ip6tables -t raw PREROUTING -m rpfilter --invert -j DROP`.

## Control Flow

The script builds two routers and two hosts, configures IPv6 SRv6 encapsulation and End.DX6 decapsulation routes, verifies host connectivity, enables netfilter hooks/rpfilter in both routers, and verifies host connectivity again.

## State and Persistence Behavior

State is temporary namespaces, veth links, IPv6 routes, sysctls, and ip6tables rules. Cleanup deletes broad `rt-*` and `hs-*` namespace names plus underlay links.

## Dependencies and Integration Points

It depends on SRv6 End.DX6, IPv6 forwarding/proxy NDP, ip6tables raw table, rpfilter match, lwtunnel netfilter support, and iproute2 seg6 support. It tests the integration between SRv6 decapsulation and IPv6 netfilter PREROUTING.

## Risks and Edge Cases

Some comments refer to End.DX4 or ARP due to copy/paste, but the implementation uses IPv6 and End.DX6. Missing ip6tables/rpfilter support is not checked early. Namespace cleanup patterns may remove unrelated similarly named test namespaces.

## Test Signals

The signal is successful bidirectional IPv6 pings both before and after netfilter is enabled. The printed summary should show zero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx6_netfilter_test.sh -->
