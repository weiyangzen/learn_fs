# sources/distributed-fs/ipfs-kubo/core/corehttp/metrics.go

## Purpose
Provides HTTP serve options for Prometheus scraping, OpenCensus export/zpages, HTTP request instrumentation, and a custom libp2p connected-peer collector.

## Important APIs, Types, and Functions
Exports `MetricsScrapingOption`, `MetricsOpenCensusCollectionOption`, `MetricsOpenCensusDefaultPrometheusRegistry`, `MetricsCollectionOption`, `IpfsNodeCollector`, `PeersTotalValues`, and `peersTotalMetric`.

## Control Flow and State
Scraping mounts `promhttp.HandlerFor` using the default gatherer. OpenCensus options register Prometheus exporters and optional zpages. `MetricsCollectionOption` registers or reuses four Prometheus collectors, wraps a child mux with request/response size, duration, and counter middleware, and returns that child mux for downstream handlers. `PeersTotalValues` iterates current peer host connections and groups peers by the first connection's transport protocol stack.

## Dependencies and Integration Points
Depends on Prometheus, OpenCensus exporters, zpages, `core.IpfsNode.PeerHost`, and net/http. It wraps the same mux used by gateway/API handlers and contributes `ipfs_http_*` and `ipfs_p2p_peers_total` telemetry.

## Risks and Test Signals
Risks include global collector registration collisions, type assertions on already-registered collectors, nondeterministic transport selection for peers with multiple connections, and nil `PeerHost` handling. `metrics_test.go` covers peer counting over libp2p test swarms; additional signals include duplicate initialization and scrape output validation.
