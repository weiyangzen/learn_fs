# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ecmp_failover.sh

## Purpose
`tcp_ecmp_failover.sh` verifies that an established TCP flow using an ECMP route fails over to a remaining healthy nexthop after carrier loss on the active device. It covers both IPv4 and IPv6.

## Important APIs, Types, And Functions
Functions include `setup_server()`, `setup_client()`, `setup()`, `cleanup()`, `tcp_ecmp_failover()`, `test_ipv4()`, and `test_ipv6()`. It relies on `forwarding/lib.sh` for kselftest helpers, namespace setup, logging, command requirements, and tcpdump helpers.

## Control Flow
The script creates `client` and `server` namespaces connected by two veth pairs. Each namespace owns a dummy loopback-style endpoint address and installs equal-weight ECMP routes to the peer endpoint through both veth paths. The client disables normal TCP route refresh by raising `tcp_retries1` and enables `ignore_routes_with_linkdown` on both paths. `tcp_ecmp_failover()` starts tcpdump on both server veths, runs `socat` server and client streams, infers the active path from packet counts, brings that server-side veth down, captures on the remaining path, and fails if fewer than 1000 packets arrive after failover.

## State, Persistence, And Dependencies
The script mutates temporary namespaces, veths, dummy links, routes, and sysctls. It depends on root privileges through the forwarding library, plus `socat` and `tcpdump`. No persistent files are intended beyond temporary tcpdump artifacts cleaned by helpers.

## Integration Points
The test targets route cache invalidation and nexthop linkdown behavior for established TCP sockets. It integrates NETDEV_CHANGE, `RTNH_F_LINKDOWN`, `sk_dst_check()` invalidation, ECMP route lookup, and userspace packet capture.

## Risks
Packet count thresholds depend on timing and host scheduling. The initial active-path inference assumes one path dominates during the first capture window. Missing `ignore_routes_with_linkdown` support, tcpdump timing issues, or socat startup delays can cause false failures.

## Test Signals
Passing signals are logged `TCP IPv4 failover` and `TCP IPv6 failover` results with at least 1000 post-failover packets on the alternate veth. Failure signals include missing tools, namespace setup errors, no traffic after linkdown, or cleanup leaving namespaces behind.
