# sources/distributed-fs/ipfs-kubo/client/rpc/swarm.go

## Purpose
This file implements libp2p swarm operations over HTTP RPC.

## Important APIs, Types, And Functions
`SwarmAPI` exposes `Connect`, `Disconnect`, `Peers`, `KnownAddrs`, `LocalAddrs`, and `ListenAddrs`. `connInfo` implements `iface.ConnectionInfo`.

## Control Flow
`Connect` encapsulates each address with `/p2p/<peer>` and sends them to `swarm/connect`. Peer/listener methods decode JSON strings into peer IDs, multiaddrs, durations, directions, and protocol IDs.

## State And Persistence Behavior
Connect/disconnect mutate live swarm connections. Address and peer listing are read-only views of libp2p state.

## Dependencies And Integration Points
It integrates Kubo `swarm/*` commands, libp2p peer/network/protocol types, and multiaddr parsing.

## Risks And Test Signals
Risks include parse failures aborting whole result sets, ignored latency parse errors, and connect behavior with empty address lists. Signals are CoreAPI swarm connect/list/address tests.
