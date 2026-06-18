# sources/distributed-fs/ipfs-kubo/core/node/identity.go

Purpose: supplies identity providers for fx injection. Important APIs are `PeerID` and `PrivateKey`.

Control flow: `PeerID` returns a closure that injects a fixed `peer.ID`. `PrivateKey` returns a closure that derives the peer ID from the configured private key, verifies it matches the expected ID, and returns the key or an error.

State and persistence: no writes. The functions validate already-loaded config identity material.

Dependencies and integration: depends on libp2p crypto and peer packages. `groups.go` uses these providers in the `Identity` graph, and libp2p host construction later retrieves the private key from the peerstore.

Risks: a mismatched private key causes startup failure, which is correct for identity integrity. Tests are indirect through identity startup paths; no direct unit tests in this subset.
