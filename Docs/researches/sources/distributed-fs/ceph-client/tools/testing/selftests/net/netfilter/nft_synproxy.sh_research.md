<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_synproxy.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_synproxy.sh

## Purpose
This script verifies nftables `synproxy` can establish a TCP connection through a router when direct SYN forwarding is otherwise blocked. It uses `iperf3` to prove application data can pass after SYN proxy negotiation.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip`, `iperf3`, `modprobe nf_conntrack`, veth devices, and namespace-scoped sysctls. The nft rules combine raw-priority `notrack` for incoming SYNs, `ct state new,established accept`, `synproxy mss 1460 sack-perm timestamp`, invalid drops, and a final SYN drop.

## Control Flow
It creates router, client, and server namespaces; configures two subnets; enables IPv4 forwarding and strict TCP conntrack mode; validates bidirectional ping; starts an `iperf3` server; installs the synproxy ruleset; then runs a bounded `iperf3` client transfer from client to server.

## State, Persistence, And Dependencies
State includes the three namespaces, veth links, forwarding/sysctl settings, conntrack module state, an nft ruleset in the router, and a background `iperf3` server. Cleanup kills endpoint namespace processes and removes namespaces.

## Integration Points
This test covers nftables synproxy integration with conntrack strictness, raw-hook notrack behavior, forward-hook policy, and real TCP data transfer. It is part of netfilter selftest coverage for TCP handshake proxying.

## Risks
It depends on `iperf3`, nft synproxy support, conntrack, and root network namespace operations. A one-second server startup sleep is a simple readiness mechanism and can be fragile on slow hosts. The test is IPv4-only despite using an `inet` table.

## Test Signals
PASS is a successful 1 MiB `iperf3` transfer through the synproxy rules. Failure signals are ping failures, inability to load the nft synproxy ruleset, `iperf3` client failure, and dumped router ruleset on transfer failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_synproxy.sh -->
