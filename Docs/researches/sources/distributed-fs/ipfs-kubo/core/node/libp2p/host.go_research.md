# sources/distributed-fs/ipfs-kubo/core/node/libp2p/host.go

Purpose: constructs the libp2p host and exposes the initial routing object. Important types/APIs are `P2PHostIn`, `P2PHostOut`, and `Host`.

Control flow: `Host` starts with `NoListenAddrs`, flattens grouped libp2p options, loads config, resolves bootstrap peers through autoconf, and builds `RoutingOptionArgs`. It sets optimistic provide when either the experimental flag or DHT sweep is enabled. It injects a libp2p routing constructor that captures the resulting routing in `out.Routing`, then calls the selected `HostOption`. For mock/test hosts that ignore libp2p options, it constructs routing manually and wraps the host with `routedhost`.

State and persistence: reads repo config and datastore; no direct writes. Registers bounded host close on fx stop.

Dependencies/integration: repo, record validator, peerstore, routing option, lifecycle helper, and shutdown helper. It is the join point between configured libp2p options and Kubo routing/provider behavior.

Risks: route construction side effects depend on libp2p applying the routing option; the fallback handles tests but production failures still abort startup. Shutdown can time out through `CloseWithCtx`. No direct test here, but many routing tests depend on its contracts.
