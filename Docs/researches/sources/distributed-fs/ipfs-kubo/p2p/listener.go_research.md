<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/listener.go -->
# sources/distributed-fs/ipfs-kubo/p2p/listener.go

## Purpose

This file defines listener abstractions and registries for Kubo's libp2p stream forwarding feature.

## Important APIs, Types, and Functions

`Listener` exposes protocol, listen/target addresses, close, done channel, and an internal key. `Listeners` stores protocol-keyed listeners under an RWMutex. `newListenersLocal` creates a local registry. `newListenersP2P` registers a libp2p stream handler match for protocols present in the registry and dispatches incoming streams to `remoteListener.handleStream`. `Register` rejects duplicate keys. `Close` removes matching listeners and closes them outside the lock.

## Control Flow, State, and Integration

The registry is mutable in memory only. Local listeners key by local bind address string; remote listeners key by protocol. The P2P registry integrates with `host.SetStreamHandlerMatch` so active registrations dynamically control accepted libp2p protocols.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p host/network/protocol and multiaddr. Risks include type assertion to `*remoteListener`, protocol key collisions, and handlers observing registry changes concurrently. P2P command/integration tests should validate duplicate listener errors and stream dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/listener.go -->
