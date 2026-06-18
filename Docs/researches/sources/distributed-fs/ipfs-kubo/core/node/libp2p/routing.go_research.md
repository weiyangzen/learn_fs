# sources/distributed-fs/ipfs-kubo/core/node/libp2p/routing.go

Purpose: composes DHT, delegated HTTP, pubsub, offline, content routing, content discovery, accelerated DHT, and AutoRelay feeder behavior. Important APIs include `Router`, `BaseRouting`, `ContentRouting`, `ContentDiscovery`, `Routing`, `OfflineRouting`, `PubsubRouter`, and `autoRelayFeeder`.

Control flow: `BaseRouting` captures the initial routing from host construction, locates a dual DHT, registers DHT shutdown, and optionally replaces the content router with FullRT plus default HTTP routers when accelerated DHT client is enabled. `Routing` sorts grouped routers by priority and builds a composable parallel router. `ContentRouting` tiers content-capable routers. `PubsubRouter` adds a high-priority IPNS-only value store. `autoRelayFeeder` periodically feeds trusted peers, DHT closest peers, and connected swarm peers to an AutoRelay channel with exponential backoff and bounded shutdown.

State and persistence: DHTs and FullRT clients use repo datastore through their constructors; this file manages lifecycle but does not write directly. AutoRelay feeder holds runtime channels.

Dependencies/integration: go-libp2p-kad-dht, fullrt, pubsub-router, routing-helpers, repo/config, shutdown. Risks include duplicate close hooks if composable router detection changes, FullRT readiness delays, and feeder goroutine stalls; shutdown uses context bounds.
