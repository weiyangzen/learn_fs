# sources/distributed-fs/ipfs-kubo/routing/delegated.go

Purpose: parses custom routing configuration into HTTP, DHT, sequential, parallel, and composed routing implementations.

Important APIs and control flow: `Parse` validates method config, recursively builds named routers through `parse`, caches created routers, detects dependency loops, and assigns routers to a `Composer`. HTTP routers build a delegated routing client with response body limits, OpenTelemetry transport span names, identity, provider info, user agent, protocol filtering, streaming results, and content router batching/concurrency. DHT routers create regular, private/public, or full-routing-table DHTs based on config.

State and persistence: no direct persistence; DHT routers use the provided datastore and host, and HTTP routers may advertise provider info from dynamic addresses.

Dependencies and integration: depends on Kubo config routing structures, Boxo delegated routing clients, libp2p DHT/fullrt, validators, host, datastore, OpenCensus/OpenTelemetry, and `Composer`.

Risks and test signals: `extraHTTP` and `extraDHT` are assumed non-nil for selected router types; malformed configs can panic before type checks. `view.Register` may error on duplicate registration. Tests cover parser composition, recursive nesting, and loop detection.
