# sources/distributed-fs/ipfs-kubo/core/core.go

Purpose: defines the central `IpfsNode` runtime object and core lifecycle helpers for context, shutdown, bootstrap, DHT-client detection, and temporary bootstrap peer persistence.

Important APIs/types/functions: `IpfsNode` aggregates identity, repo, pinning, block/DAG services, fetchers, path resolvers, networking, routing/provider/DHT, pubsub, P2P, and lifecycle flags. `Mounts`, `Close`, `HasActiveDHTClient`, `Context`, `Bootstrap`, `TempBootstrapPeersKey`, `loadBootstrapPeers`, `saveTempBootstrapPeers`, `loadTempBootstrapPeers`, and `ConstructPeerHostOpts` are defined here.

Control flow: `Close` delegates to the node stop function. `Context` lazily falls back to `context.TODO`. `HasActiveDHTClient` rejects nil, routinghelpers.Null, and typed-nil dual/fullrt DHT clients before treating a client as usable. `Bootstrap` no-ops without routing, closes an existing bootstrapper, installs config-backed peer loading and datastore-backed backup peer save/load when absent, applies backup interval from config, then calls `bootstrap.Bootstrap`.

State and persistence behavior: `saveTempBootstrapPeers` writes JSON-encoded bootstrap peer strings into repo datastore key `/local/temp_bootstrap_peers` and syncs that key. `loadTempBootstrapPeers` reads and parses it. `Bootstrap` mutates `n.Bootstrapper` and may close the previous one.

Dependencies and integration points: this struct is the dependency injection hub for CoreAPI, commands, HTTP, node construction, libp2p services, block services, namesys, provider systems, and repo/config.

Risks: `Close` assumes `stop` is non-nil. Lazy `Context` fallback can mask missing initialization. `HasActiveDHTClient` only knows specific nil/no-op types, so custom routing implementations may be treated as active without deeper validation. Temporary bootstrap peer datastore errors are logged and ignored in bootstrap callbacks.

Test signals: `core_test.go` covers node initialization and DHT-client typed-nil/no-op/valid cases.
