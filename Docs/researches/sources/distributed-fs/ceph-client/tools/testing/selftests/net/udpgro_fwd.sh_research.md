# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_fwd.sh

Purpose: Functional and performance tests for UDP GRO forwarding, GRO fraglist, and GRO forwarding over VXLAN/UDP tunnels for IPv4 and IPv6, including checksum validation after forced segmentation and reaggregation.

Important APIs/functions: `create_ns()` creates source/destination namespaces and veth, optionally attaching XDP dummy on destination. `create_vxlan_endpoint()` and `create_vxlan_pair()` build VXLAN overlay pairs for IPv4 and IPv6. `run_test()` sends one GSO packet of ten UDP frames, counts iptables/ip6tables INPUT hits on UDP 8000 and VXLAN 4789, and validates expected aggregation. `run_test_csum()` uses iperf3 and nstat checksum counters. `run_bench()` pins sender/receiver to CPUs and toggles RPS.

Control flow: loops over families 4 and 6. For each family it tests no GRO, GRO fraglist, GRO fwd with NAT to bypass socket lookup guard, performance before/after `rx-udp-gro-forwarding`, GRO fraglist over VXLAN, GRO fwd over VXLAN with NAT and neighbor priming, then a bridge/veth segmentation topology that disables TX offloads and checks no UDP checksum errors during iperf3.

State and persistence: namespaces, veths, VXLAN devices, bridges, iptables rules, ethtool feature flags, RPS sysfs changes, nstat counters, and background jobs are temporary. `cleanup` runs between scenarios and on exit.

Dependencies and integration: requires root, iproute2 VXLAN/bridge/netns, ethtool features (`generic-receive-offload`, `rx-gro-list`, `rx-udp-gro-forwarding`), iptables/ip6tables, jq, iperf3, compiled benchmark helpers, and BPF object. Uses `lib.sh`.

Risks: packet counter expectations allow VXLAN noise tolerance but still depend on background control traffic. Performance tests skip with one CPU but are not thresholded. NAT dependency and feature availability can cause environment-specific failures.

Test signals: explicit pass/fail lines per scenario based on RX/TX exit status, iptables packet counters, VXLAN counter tolerance, and zero UDP checksum errors.
