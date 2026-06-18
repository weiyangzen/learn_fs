# sources/distributed-fs/ipfs-kubo/core/node/groups.go

Purpose: defines the high-level fx option groups that assemble storage, identity, libp2p, IPNS, online/offline routing, and the full IPFS node. Important exports are `BaseLibP2P`, `LibP2P`, `Storage`, `Identity`, `IPNS`, `Online`, `Offline`, `Core`, `Networked`, and `IPFS`.

Control flow: `LibP2P` interprets connection manager, pubsub, AutoNAT, relay, AutoTLS, transport, discovery, routing, resource-manager, and NAT-check settings into fx providers/invokes. AutoTLS may append wildcard WSS listeners when TCP and WebSocket transports are enabled. `Storage` configures blockstore cache options and chooses filestore support. `Identity` validates peer ID/private key and adds self keys to the peerstore. `Online` validates IPNS republish durations, enables bitswap, DNS, namesys, peering, p2p service, libp2p, and providers. `Offline` supplies offline exchange/routing/provider variants. `IPFS` pulls config from `BuildCfg`, validates import/provide config, migrates old sharding settings, writes UnixFS HAMT globals, and returns the final graph.

State and persistence: mutates `cfg.Addresses.Swarm` for AutoWSS, sets global UnixFS sharding knobs, and reads repo resource overrides. Dependencies span almost every node package plus libp2p pubsub, resource-manager, and Kubo config.

Risks: fatal logging is used for incompatible relay/AutoTLS/sharding settings; config migration modifies in-memory config; provider strategy influences multiple subsystems. Tests are indirect through libp2p option tests, routing tests, provider tests, and startup integration.
