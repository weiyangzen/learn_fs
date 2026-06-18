<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx4_netfilter_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx4_netfilter_test.sh

## Purpose

`srv6_end_dx4_netfilter_test.sh` validates that SRv6 `End.DX4` decapsulation and forwarding work when lightweight-tunnel netfilter hooks are enabled and raw-table rpfilter rules are installed.

## Important APIs, Types, and Functions

The script is standalone and defines `ksft_skip`. Functions include `setup_rt_networking`, `setup_rt_netfilter`, `setup_hs`, `setup_vpn_config`, `host_tests`, and `router_netfilter_tests`. It uses IPv6 underlay routing, IPv4 host routes, `encap seg6local action End.DX4 nh4 ... dev ...`, `sysctl net.netfilter.nf_hooks_lwtunnel=1`, and `iptables -t raw -A PREROUTING -m rpfilter --invert -j DROP`.

## Control Flow

Setup creates two router namespaces and two host namespaces for one tenant, installs bidirectional SRv6 encapsulation and End.DX4 decapsulation routes, and first checks host connectivity without netfilter. Then it enables lwtunnel netfilter hooks and rpfilter in both routers and repeats the host connectivity tests.

## State and Persistence Behavior

All devices, namespaces, routes, sysctls, and iptables rules are temporary. Cleanup deletes veth links and any `rt-*` or `hs-*` namespaces. State is less isolated by name than some lib.sh-based scripts, so namespace name collisions are possible.

## Dependencies and Integration Points

It depends on SRv6 End.DX4, IPv4/IPv6 forwarding, iptables raw table, rpfilter match, lwtunnel netfilter hook support, and root privileges. It integrates SRv6 decapsulation with netfilter PREROUTING behavior.

## Risks and Edge Cases

The header comment has some copy/paste wording, but the route action is correctly `End.DX4`. Cleanup greps broad namespace patterns. Missing iptables or rpfilter support is not preflighted and will surface as failure.

## Test Signals

Both host pings should pass before and after netfilter hook/rpfilter setup. A failure after enabling hooks suggests lwtunnel/netfilter integration rejected decapsulated SRv6 traffic incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx4_netfilter_test.sh -->
