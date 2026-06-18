# Research: sources/distributed-fs/ipfs-kubo/config/peering.go

Purpose: Defines persistent peers that the node should attempt to keep connected.

Important APIs/types/functions: `Peering` contains `Peers []peer.AddrInfo`.

Control flow, state, and persistence: No functions. Peer address info is serialized in config and consumed by the peering service.

Dependencies and integration points: Uses libp2p `peer.AddrInfo`. Profiles and command tooling may mutate it outside this subset.

Risks and test signals: Invalid or stale peer addresses can cause repeated dial attempts. Serialization shape depends on libp2p AddrInfo JSON behavior. No direct tests in this subset.
