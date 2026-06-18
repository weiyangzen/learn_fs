<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_tcp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_tcp.sh

## Purpose
This kselftest validates nftables transparent proxy (`tproxy`) handling for TCP in IPv4 and IPv6, for both forwarded traffic and locally originated router traffic. It confirms only traffic to the selected destination is intercepted and that unrelated destinations still reach their real servers.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip rule`, local route tables, `socat` with `ip-transparent`, and helper functions `test_ping()`, `test_ping_router()`, `listener_ready()`, `test_tproxy()`, and protocol/origin wrappers. The nft rules use prerouting `tproxy $ip_proto to :12345 meta mark set 1` and, for local-origin cases, route-output marking.

## Control Flow
It builds a router connected to three endpoint namespaces with IPv4 and IPv6 addressing and forwarding. `test_tproxy()` derives protocol-specific addresses and rules, installs fwmark policy routing to local delivery, starts a transparent echo proxy on the router plus normal TCP servers in ns2/ns3, then sends four requests: ns1 to ns2, ns1 to ns3, router to ns2, and router to ns3. Expected replies distinguish proxied echo from real `PONG_NS*` servers.

## State, Persistence, And Dependencies
State includes four namespaces, veth topology, policy-routing table 100, fwmark rules, nft rulesets, and background `socat` listeners. Cleanup kills namespace processes and removes namespaces; each test case deletes its policy route state.

## Integration Points
This test ties nftables tproxy expressions to Linux policy routing, transparent sockets, IPv4/IPv6 forwarding, and local output marking. It validates both route and filter hook participation.

## Risks
The test depends on `socat` transparent socket support and has comments for a known socat 1.8.0 family-binding bug. Listener timing and policy route cleanup are important; stale table 100 routes could affect later cases. It assumes tproxy support in the kernel and nft.

## Test Signals
PASS lines compare each returned string with expected proxy or real-server output. Failures are wrong replies, missing connectivity before tproxy, nft ruleset/policy route errors, or nonzero final status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_tcp.sh -->
