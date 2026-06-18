# sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt.go

Purpose: builds routing option implementations for DHT, delegated HTTP, custom routers, nil routing, and HTTP provider address resolution. Important APIs are `RoutingOptionArgs`, `RoutingOption`, `EndpointSource`, `determineCapabilities`, `collectAllEndpoints`, `constructDefaultHTTPRouters`, `ConstructDelegatedOnlyRouting`, `ConstructDefaultRouting`, `constructDHTRouting`, `ConstructDelegatedRouting`, `httpRouterAddrFunc`, and `parseMultiaddrs`.

Control flow: endpoint collection merges delegated routers and publishers, with `IPFS_HTTP_ROUTERS` overriding read endpoints. Capabilities are inferred per endpoint and merged by origin so one HTTP router/composer is built per base URL. Default routing combines DHT and HTTP routers in parallel; delegated-only requires at least one HTTP router; custom routing delegates to `irouting.Parse`; DHT routing configures dual WAN/LAN DHT and test stubs when `TEST_DHT_STUB` is set. `httpRouterAddrFunc` prefers explicit Announce, then AutoNAT V2 confirmed addrs, then `host.Addrs`, always appending AppendAnnounce.

State and persistence: DHT routing receives datastore; HTTP routing may sign with identity private key but this file stores nothing.

Dependencies/integration: autoconf, Kubo routing/config, libp2p DHT/host/multiaddr. Risks include endpoint capability misclassification, env override surprises, and reliance on experimental `BasicHost.ConfirmedAddrs`. Tests cover capability logic and address selection.
