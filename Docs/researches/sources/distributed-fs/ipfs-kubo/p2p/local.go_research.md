<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/local.go -->
# sources/distributed-fs/ipfs-kubo/p2p/local.go

## Purpose

`local.go` implements local forwarding: a local manet listener accepts local connections and opens libp2p streams to a remote peer/protocol.

## Important APIs, Types, and Functions

`localListener` stores context, parent `P2P`, protocol, listen address, remote peer, manet listener, and done channel. `ForwardLocal` listens on a multiaddr, registers the listener, and starts accept loop. `dial` opens a libp2p stream with a 30-second timeout. `acceptConns` handles temporary accept errors. `setupStream` creates a `Stream` binding local connection to remote stream and registers it.

## Control Flow, State, and Integration

Each accepted local connection spawns a goroutine that dials the remote peer and then starts bidirectional copying through `StreamRegistry`. `close` closes the local listener and done channel. Listener state is in-memory and removed through registry close operations.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p network/peer/protocol, multiaddr net, and temp error catcher. Risks include accept loop not closing `done` on natural errors, hard-coded dial timeout, and local sockets closed on dial failure. Integration tests should confirm local TCP/Unix forwarding and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/local.go -->
