# sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp.sh

## Purpose

This selftest verifies that an IPv4 ICMP unreachable generated in a namespace without an IPv4 source address uses the dummy source address `192.0.0.8` specified by RFC 7600 instead of `0.0.0.0`.

## Important APIs, Types, and Functions

The script sources `lib.sh`, defines constants for two namespaces and routes, creates `cleanup`, and uses `setup_ns`, `ip route add ... via inet6`, sysctl, `ping`, `tcpdump`, `awk`, and namespace helpers.

## Control Flow

The script creates namespaces `NS1` and `NS2`, connects them with a veth, assigns IPv4 only to NS1 and IPv6 to both ends, installs IPv4 routes via IPv6 next hops, enables IPv4 forwarding and disables ICMP rate limiting in NS2, starts a ping from NS1 to an unreachable IPv4 address behind NS2, captures the first non-echo ICMP packet with tcpdump, extracts the source IP, and compares it to `192.0.0.8`.

## State and Persistence Behavior

Temporary state includes namespaces, veth, addresses, routes, sysctls in NS2, a temporary capture file, and background ping/tcpdump processes. Cleanup removes the temp file and namespaces.

## Dependencies and Integration Points

It depends on IPv4 routes via IPv6 nexthops, `tcpdump`, ping, network namespaces, and kernel ICMP source address selection. It integrates with the kernel behavior for ICMP errors when no IPv4 address is available in the generating namespace.

## Risks and Edge Cases

The topology comment appears to list NS1's IPv6 address as NS2's address in one line, but the commands use distinct `2001:db8:1::1` and `::2`. The test assumes tcpdump sees exactly one relevant ICMP response before timeout. If ICMP rate limiting or forwarding settings fail, the response can be missing.

## Test Signals

Success prints `OK` and exits 0 when tcpdump shows `192.0.0.8` as the ICMP response source. Any other source prints a failure message and exits 1.
