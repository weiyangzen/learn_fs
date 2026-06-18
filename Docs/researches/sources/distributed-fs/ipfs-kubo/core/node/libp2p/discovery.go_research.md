# sources/distributed-fs/ipfs-kubo/core/node/libp2p/discovery.go

Purpose: wires local peer discovery, currently mDNS, into the libp2p host. Important APIs are `discoveryHandler`, `HandlePeerFound`, `DiscoveryHandler`, and `SetupDiscovery`.

Control flow: `DiscoveryHandler` captures a lifecycle context and host. On peer discovery, `HandlePeerFound` attempts `host.Connect` with a 30-second timeout and logs failures. `SetupDiscovery` starts an mDNS service only when enabled; start errors are logged and swallowed so node startup continues.

State and persistence: no durable state. Runtime state is the lifecycle context held by the handler and the mdns service instance.

Dependencies/integration: libp2p host/peer/mdns, fx, and Kubo lifecycle helpers. `BaseLibP2P` provides the handler and `LibP2P` invokes setup based on `Discovery.MDNS.Enabled`.

Risks: mDNS startup failure only logs, which is desirable for noncritical discovery but can hide local-discovery regressions. No direct tests here; integration behavior is observable through host discovery tests elsewhere.
