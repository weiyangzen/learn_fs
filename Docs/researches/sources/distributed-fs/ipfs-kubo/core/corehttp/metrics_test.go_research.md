# sources/distributed-fs/ipfs-kubo/core/corehttp/metrics_test.go

## Purpose
Tests the peer-count aggregation used by `IpfsNodeCollector`.

## Important APIs, Types, and Functions
Defines `TestPeersTotal`, which builds four basic libp2p hosts over generated swarms, dials three peers from the center host, and inspects `PeersTotalValues`.

## Control Flow and State
The test connects host 0 to hosts 1-3, waits briefly for swarm state, wraps host 0 in an `IpfsNode`, and sums `/ip4/tcp` plus `/ip4/udp/quic-v1` counts. It tolerates at most two transport buckets.

## Dependencies and Integration Points
Depends on libp2p basic host and swarm testing packages. It exercises the collector without a Prometheus registry.

## Risks and Test Signals
The sleep is timing-sensitive and the transport bucket set depends on libp2p defaults. It is a useful regression signal for peer counting semantics but not for full metric registration or scrape formatting.
