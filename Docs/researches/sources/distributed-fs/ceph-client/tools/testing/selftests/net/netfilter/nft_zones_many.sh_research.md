<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_zones_many.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_zones_many.sh

## Purpose
This test measures and validates insertion of many conntrack entries that share identical addresses and ports but live in distinct conntrack zones. It covers both packet-path insertion through nftables and optional ctnetlink insertion through the `conntrack` tool.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `socat`, optional `conntrack`, `date +%s%3N`, and helpers `test_zones()` and `test_conntrack_tool()`. The nft rules use a `numgen inc mod` expression mapped to `ct zone set`, and the ctnetlink path uses `conntrack -I --zone`.

## Control Flow
It creates one namespace, installs nft rules that assign outgoing UDP packets to zones, populates the zone map, sends batches of 1000 UDP packets with identical endpoint tuples, and optionally checks `conntrack -C` for at least the requested count. If `conntrack` is available, it flushes state and inserts the same number of TCP entries directly via ctnetlink, reporting per-1000 timings and final counts.

## State, Persistence, And Dependencies
State is confined to one namespace, nft rules/maps, UDP conntrack timeout, and conntrack table entries. Cleanup removes namespaces. `KSFT_MACHINE_SLOW=yes` lowers the zone count from 2000 to 500.

## Integration Points
This is a performance/regression probe for conntrack zone hash behavior and nftables zone assignment. It complements `nft_nat_zones.sh` by focusing on insertion volume rather than NAT routing correctness.

## Risks
Runtime and reliability depend on host speed, conntrack table capacity, and `socat` throughput. The packet-path count check only runs when `conntrack` exists. The nft map uses `numgen` and may expose parser or modulo behavior changes.

## Test Signals
PASS lines report per-batch insertion durations and final conntrack counts. Failures are packet send errors, final count below expected, ctnetlink insertion errors, or nonzero final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_zones_many.sh -->
