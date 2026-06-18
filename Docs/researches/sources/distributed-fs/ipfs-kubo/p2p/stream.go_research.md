<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/stream.go -->
# sources/distributed-fs/ipfs-kubo/p2p/stream.go

## Purpose

This file tracks active P2P forwarding streams and copies bytes bidirectionally between local manet connections and libp2p streams.

## Important APIs, Types, and Functions

`Stream` records ID, protocol, origin/target addresses, peer, local connection, remote stream, and registry. `startStreaming` launches two `io.Copy` goroutines. `StreamRegistry` stores streams, per-peer connection counts, next ID, and libp2p connection manager. `Register`, `Deregister`, `Close`, and `Reset` manage lifecycle and connection-manager tags.

## Control Flow, State, and Integration

Register tags the peer with `stream-fwd`, increments counts, assigns an ID, stores the stream, and starts copying. Either copy direction closes or resets both endpoints and deregisters. Untagging occurs when the last stream for a peer is removed.

## Dependencies, Risks, and Test Signals

Dependencies are `io`, mutexes, libp2p connmgr/network/peer/protocol, and manet. Risks include both copy goroutines racing to close/reset/deregister the same stream, ID growth, and connection-manager tag leaks if deregistration is missed. Stress/integration tests should watch for leaks and correct half-close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/stream.go -->
