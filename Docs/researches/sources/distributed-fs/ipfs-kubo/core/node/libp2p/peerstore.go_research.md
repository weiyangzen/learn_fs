# sources/distributed-fs/ipfs-kubo/core/node/libp2p/peerstore.go

Purpose: provides the libp2p peerstore and closes it with the node lifecycle. Important API is `Peerstore`.

Control flow: constructs an in-memory peerstore with `pstoremem.NewPeerstore`, registers an fx `OnStop` hook, and closes it through `shutdown.CloseWithCtx`.

State and persistence: peerstore is memory-backed; no durable peer metadata is written by this provider.

Dependencies/integration: pstoremem, fx, shutdown helper. Used by identity setup, host construction, and IPNS record validation.

Risks: peerstore close can block, so bounded shutdown is important. No direct tests.
