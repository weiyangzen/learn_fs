<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect.sh

## Purpose
`tc_l2_redirect.sh` is an integration test for tc BPF L2-to-IP-tunnel redirect programs. It builds a veth and namespace topology, attaches sections from `tc_l2_redirect_kern.o`, programs the pinned tunnel-interface map with `tc_l2_redirect_user`, and verifies IPv4 and IPv6 reachability through IPIP and IP6 tunnel devices.

## Important APIs, Types, And Functions
Key shell functions are `config_common()`, `cleanup()`, `l2_to_ipip()`, and `l2_to_ip6tnl()`. It drives `ip netns`, `ip link`, `ip route`, `tc qdisc/filter`, `sysctl`, `ping`, and the user helper `./tc_l2_redirect`.

## Control Flow
The script snapshots global rp_filter and IPv6 sysctls, removes stale topology, then iterates selected test names and directions. `config_common()` creates `ns1` and `ns2`, veth pairs, tunnel endpoints, tc clsact qdiscs, and an ingress drop filter in `ns2`. Each test creates an external tunnel on the host, attaches a redirect section on ingress or egress, updates the pinned `tun_iface` map with the tunnel ifindex, pings VIP addresses, optionally tests direct egress, and calls `cleanup()`.

## State And Persistence
State is mostly system state: network namespaces, veth devices, tunnel devices, routes, qdiscs, tc filters, sysctls, and `/sys/fs/bpf/tc/globals/tun_iface`. Cleanup restores saved sysctl values and deletes topology and pinned map artifacts.

## Dependencies And Integration Points
It depends on root privileges, iproute2 with BPF support, ping, kernel IPIP/IP6 tunnel support, tc clsact, BPF map pinning, and the companion kernel and user sample files. The script integrates map values written by userspace with tc programs attached by iproute2.

## Risks And Edge Cases
The script changes global forwarding/rp_filter/IPv6 settings and assumes cleanup runs. Failures before cleanup, missing privileges, unavailable IPv6, existing namespace/device names, or missing tunnel modules can leave host networking altered. The tests use fixed addresses and ifnames that can conflict with local setup.

## Test Signals
Passing output prints `OK` for `l2_to_ipip` and `l2_to_ip6tnl` in ingress and egress modes. Additional signals are successful tc filter attach, pinned map update, namespace pings to `10.10.1.102` and `2401:face::66`, and absence of leftover namespaces/qdiscs after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect.sh -->
