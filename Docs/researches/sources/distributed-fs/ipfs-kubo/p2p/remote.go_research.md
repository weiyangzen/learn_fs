<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/remote.go -->
# sources/distributed-fs/ipfs-kubo/p2p/remote.go

## Purpose

`remote.go` implements remote forwarding: incoming libp2p streams for a protocol are proxied to a local multiaddr service.

## Important APIs, Types, and Functions

`remoteListener` stores parent `P2P`, protocol, target address, `reportRemote`, and done channel. `ForwardRemote` registers it. `handleStream` dials the local target, optionally writes the remote peer ID line first, creates origin `/ipfs/<peer>` multiaddr, and registers a bidirectional `Stream`. Address methods expose listen and target addresses, and `key` returns the protocol.

## Control Flow, State, and Integration

The libp2p stream handler from `listener.go` invokes `handleStream`. Dial failures or peer multiaddr construction failures reset the remote stream. Successful streams are tracked by `StreamRegistry`.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p network/protocol, multiaddr, and manet. Risks include local target dial failures, `reportRemote` protocol compatibility, and remote listener `close` not unregistering host handlers directly but relying on registry removal. Integration tests should verify service exposure and remote peer reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/remote.go -->
