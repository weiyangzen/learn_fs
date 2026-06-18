<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_udp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_udp.sh

## Purpose
This script validates nftables transparent proxy behavior for UDP forwarding over IPv4 and IPv6. It ensures UDP traffic to ns2 can be intercepted and relayed by a transparent proxy while traffic to ns3 and router-originated traffic remain unproxied.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip rule`, local route table 100, `socat` UDP listeners with `ip-transparent`, and helpers `test_ping()`, `test_ping_router()`, `listener_ready()`, and `test_tproxy_udp_forward()`. The nft rule is a prerouting `udp dport 8080 tproxy ... meta mark set 1` match.

## Control Flow
It creates the same four-namespace, three-subnet router topology as the TCP tproxy test. For each address family, it adds fwmark routing for ns2's address, installs a tproxy rule, starts a UDP transparent relay on the router and normal UDP servers in ns2/ns3, then sends packets from ns1 and nsrouter to ns2/ns3. ns1-to-ns2 should echo through the proxy; other paths should return real server strings.

## State, Persistence, And Dependencies
State includes namespace topology, forwarding sysctls, policy routing, nft rules, and background UDP `socat` listeners. The UDP timeout is longer than TCP because datagram relay startup and response timing are slower. Cleanup removes namespace processes and all namespaces.

## Integration Points
This is the UDP companion to TCP tproxy coverage and validates nftables tproxy with datagram transparent sockets and policy routing. It also checks that local router-originated traffic is not captured in the forward-only UDP scenario.

## Risks
UDP tests are timing-sensitive and depend on `socat` behavior with `shut-none`, `reuseport`, and transparent bind options. The script only tests forwarded tproxy, not local-output UDP interception. Stale fwmark routes would affect later protocol cases if cleanup failed.

## Test Signals
PASS output is based on exact returned strings for ns1/nsrouter to ns2/ns3. Wrong strings, timeouts, missing listeners, or baseline ping failures set `ret=1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_udp.sh -->
