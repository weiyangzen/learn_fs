# Research: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers.go

Purpose: Converts bootstrap peer configuration between serialized multiaddr strings and structured libp2p peer address info.

Important APIs/types/functions: `ErrInvalidPeerAddr`, `(*Config).BootstrapPeers`, `(*Config).SetBootstrapPeers`, `ParseBootstrapPeers`, and `BootstrapPeerStrings`.

Control flow, state, and persistence: `ParseBootstrapPeers` validates each string as a multiaddr and converts p2p multiaddrs to `peer.AddrInfo`. `SetBootstrapPeers` writes formatted strings back to `Config.Bootstrap`. `BootstrapPeerStrings` panics on `AddrInfoToP2pAddrs` errors, treating them as programmer errors.

Dependencies and integration points: Uses libp2p `peer` and multiaddr packages. `autoconf.go` uses parsing after expanding bootstrap placeholders. Repo config stores only strings.

Risks and test signals: All entries must be valid p2p multiaddrs; mixed invalid entries fail the entire parse. `ErrInvalidPeerAddr` is declared but not used in this file. `bootstrap_peers_test.go` covers round-trip formatting for autoconf fallback peers.
