# sources/distributed-fs/ceph-client/tools/testing/selftests/net/macvlan_mcast_shared_mac.sh

## Purpose
This shell selftest verifies multicast delivery to a macvlan bridge port when the source MAC equals the macvlan's own MAC, modeling shared virtual MAC cases such as VRRP.

## Important APIs and Functions
`setup` creates source and bridge namespaces, a veth pair, assigns `SHARED_MAC` to the source veth and macvlan, configures IPv4 addresses, creates `macvlan0` in bridge mode, and enables all-multicast. `test_macvlan_mcast_shared_mac` starts tcpdump on `macvlan0`, waits for listening, sends multicast pings from the source namespace, and counts captured ICMP packets. `cleanup` removes capture files and namespaces.

## Control Flow and State
The script sources `lib.sh`, sets a cleanup trap, builds the topology, runs one test, logs it through `log_test`, and exits with accumulated `EXIT_STATUS`. State consists of temporary namespaces, veth/macvlan links, IP addresses, and temporary capture files.

## Dependencies and Integration
It depends on root, `ip`, `ping`, `tcpdump`, macvlan bridge mode, multicast delivery, and `lib.sh` result helpers.

## Risks and Test Signals
Tcpdump startup is timing-sensitive and guarded by `slowwait` on its output. Multicast filtering or lack of all-multicast support can cause false failures. The pass signal is at least one ICMP packet in the capture and a kselftest OK result.
