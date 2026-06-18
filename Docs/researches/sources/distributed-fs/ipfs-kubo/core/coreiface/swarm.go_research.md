# sources/distributed-fs/ipfs-kubo/core/coreiface/swarm.go

## Purpose
Defines CoreAPI swarm networking operations and connection metadata.

## Important APIs, Types, and Functions
Defines `ErrNotConnected`, `ErrConnNotFound`, `ConnectionInfo`, and `SwarmAPI` methods `Connect`, `Connectedness`, `Peers`, `KnownAddrs`, `LocalAddrs`, `ListenAddrs`, and `Disconnect`.

## Control Flow and State
No implementation is present. The interface describes live libp2p connection state, peerstore-known addresses, local/listen addresses, and connect/disconnect operations.

## Dependencies and Integration Points
Depends on context, multiaddr, libp2p network/peer types. Routing and pubsub tests use swarm APIs for local address and peer identity checks.

## Risks and Test Signals
Risks include confusing known vs connected addresses, stale connection info, and disconnect races. Conformance in this subset is indirect through routing/pubsub tests; dedicated swarm tests should cover connection lifecycle and error sentinels.
