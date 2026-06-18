# sources/distributed-fs/ipfs-kubo/core/node/libp2p/hostopt.go

Purpose: isolates actual libp2p host construction behind a testable function type. Important APIs are `HostOption`, `DefaultHostOption`, and `constructPeerHost`.

Control flow: `constructPeerHost` fetches the node private key from the peerstore for the expected peer ID, errors if missing, prepends identity and peerstore options, and calls `libp2p.New`.

State and persistence: no writes; depends on peerstore contents populated by identity setup.

Dependencies/integration: libp2p, host, peer, peerstore. `Host` receives a `HostOption`, allowing tests or alternate construction to substitute behavior.

Risks: missing private key causes startup failure; this is expected for encrypted libp2p operation. No direct tests in this file.
