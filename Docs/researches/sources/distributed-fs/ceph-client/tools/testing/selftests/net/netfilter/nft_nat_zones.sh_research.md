<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat_zones.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat_zones.sh

## Purpose
This test validates connection tracking zones combined with NAT source port reallocation when many clients share the same IP address and source port. The gateway must isolate identical tuples by ingress interface/zone and still NAT all connections to a common server.

## Important APIs, Types, And Functions
The script uses `lib.sh` helpers, `nft`, `ip -batch`, `conntrack`, `socat`, `ping`, namespace sysctls, and `ss`. The key helper is `listener_ready()`. The nftables rules use maps from interface name to mark and conntrack zone, dynamic sets for ICMP/TCP flow accounting, `ct original zone set`, `ct mark`, policy routing marks, and `masquerade`.

## Control Flow
It creates gateway and server namespaces plus up to `maxclients` client namespaces, with all clients using the same client IPs. Batched `ip` commands configure per-client veths, duplicate gateway-side addresses, policy routing tables, and fwmark rules. The gateway nft rules assign zones and marks by input interface, record flow tuples in dynamic sets, and masquerade toward the server. The script first runs parallel pings and validates dynamic ICMP set counters, then runs TCP `socat` connections from all clients using source port 10000 and verifies dynamic TCP flow entries.

## State, Persistence, And Dependencies
State includes many netns, veth devices, policy routing tables, neighbor-cache sysctl changes, nft dynamic sets/maps, conntrack zones, and a server `socat` process. Cleanup restores neighbor GC thresholds and removes namespaces. `KSFT_MACHINE_SLOW=yes` reduces client count.

## Integration Points
This is an end-to-end stress/regression test for nf_conntrack zone isolation, NAT port reallocation, dynamic nft sets, mark-reflect sysctls, and policy routing. It complements simpler NAT tests by forcing tuple collisions at scale.

## Risks
The test is resource-heavy and can be slow on debug/KASAN kernels. It assumes per-interface duplicate addressing and large dynamic sets are supported. Failures may arise from neighbor table limits, missing `socat`, or timing on listener readiness.

## Test Signals
PASS conditions are successful ping from all clients, exact ICMP counter totals per client and server-facing interface, successful TCP connections from all clients, and expected TCP flow entries in gateway nft sets. Failures print missing set elements, conntrack stats, or connection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat_zones.sh -->
