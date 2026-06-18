# sources/distributed-fs/ipfs-kubo/core/commands/swarm.go

Purpose: implements `ipfs swarm` networking commands for addresses, connections, peers, peering, resource-manager stats, and address filters.

Important APIs/types/functions: `SwarmCmd` registers `addrs`, `connect`, `disconnect`, `filters`, `peers`, `peering`, and experimental `resources`. Output helpers include `stringList`, `addrMap`, `peeringResult`, `connInfo`, `connInfos`, and `addrInfos`. Address helpers `parseAddresses` and `resolveAddresses` resolve DNS multiaddrs. Filter helpers mutate config: `filtersAdd`, `filtersRemoveAll`, and `filtersRemove`.

Control flow: peering add/rm parse multiaddrs or peer IDs and call `node.Peering` methods; peering changes are explicitly not persisted. `swarm peers` obtains CoreAPI connections, optionally enriches with latency, streams, direction, and identify data from peerstore. `resources` recomputes configured libp2p limits, merges live resource-manager stats, and emits text/JSON. `addrs` lists known/local/listen addresses via CoreAPI. `connect` resolves peer addresses then calls CoreAPI `Swarm().Connect`; `disconnect` resolves addresses then closes matching connections. `filters` lists in-memory deny filters; add/rm update both `n.Filters` and the repo config opened via `fsrepo.Open`.

State and persistence behavior: connects/disconnects mutate live libp2p network state and connection-manager tags via CoreAPI. Peering commands mutate live peering service only, not config. Filter add/rm persist `Swarm.AddrFilters` using `Repo.SetConfig` and also mutate live filters. Resource stats and address listings are read-only.

Dependencies and integration points: uses CoreAPI `Swarm`, command environment node/config root, libp2p peerstore/network/protocol/resource-manager, Kubo `libp2p.LimitConfig`, multiaddr DNS resolver, multiaddr-filter parsing, and fsrepo config persistence.

Risks: `resolveAddresses` launches DNS resolution goroutines and reports one buffered error after collecting results; simultaneous errors are collapsed. It assumes a non-nil DNS resolver for non-`/p2p` addresses. Filter config updates open the repo separately and can race with other config writers. Peering runtime changes disappear after daemon restart. `swarm peers --identify` ignores `identifyPeer` errors.

Test signals: no local tests. Behavioral coverage is largely through CoreAPI swarm interface tests and command-tree validation.
