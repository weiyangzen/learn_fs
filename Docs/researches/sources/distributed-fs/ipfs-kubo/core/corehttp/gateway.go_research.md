# sources/distributed-fs/ipfs-kubo/core/corehttp/gateway.go

## Purpose
Builds Kubo HTTP gateway serve options, including path-based gateways, hostname/subdomain gateways, version reporting, and the libp2p gateway endpoint. It adapts `core.IpfsNode` block, namesys, routing, resolver, and config state into Boxo gateway handlers.

## Important APIs, Types, and Functions
Key entry points are `GatewayOption`, `HostnameOption`, `VersionOption`, `Libp2pGatewayOption`, `newGatewayBackend`, `getGatewayConfig`, `withMetricLabels`, `newServerDomainAttrFn`, and `offlineGatewayErrWrapper`. Constants include `defaultPaths`, `subdomainGatewaySpec`, and `defaultKnownGateways`.

## Control Flow and State
Serve options read repo config, build a gateway backend, wrap it with configured headers/CORS, add bounded OTel `server.domain` labels, then mount handlers on the mux. `newGatewayBackend` switches to offline blockservice, offline value store, a rebuilt namesys, and offline path resolver when `Gateway.NoFetch` is true. `getGatewayConfig` fills Boxo defaults, copies implicit localhost subdomain gateway config, and applies per-host public gateway overrides.

## Dependencies and Integration Points
Depends on Boxo gateway, blockservice, namesys, path resolver, Kubo config defaults, `core.IpfsNode`, libp2p routing, and OTel HTTP instrumentation. It is used by daemon HTTP setup and coordinates with API/WebUI/routing handlers through the shared serve option pattern.

## Risks and Test Signals
Risks include accidentally fetching in `NoFetch` mode, high-cardinality metrics labels, incorrect public gateway inheritance, disabled localhost defaults not being removed, and offline errors mapping to the wrong HTTP status. Tests cover version output and `DeserializedResponses` inheritance; integration coverage should exercise path gateway, hostname gateway, libp2p trustless mode, DNSLink/no-fetch behavior, and configured headers.
