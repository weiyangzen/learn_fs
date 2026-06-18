# sources/distributed-fs/ipfs-kubo/core/coreapi/swarm.go

Purpose: implements CoreAPI swarm networking operations.

Important APIs/types/functions: `SwarmAPI`, private `connInfo`, constants `connectionManagerTag` and `connectionManagerWeight`, methods `Connect`, `Disconnect`, `KnownAddrs`, `LocalAddrs`, `ListenAddrs`, `Peers`, and `connInfo` accessors.

Control flow: `Connect` requires peerHost, clears libp2p swarm backoff when possible, connects, and tags the peer in the connection manager. `Disconnect` splits a multiaddr into transport address and peer ID, closes all peer connections when no transport is specified, or closes the matching connection. Address methods read peerstore/local/listen addresses. `Peers` maps each live connection to a `ConnectionInfo` wrapper with peerstore, direction, address, and stream access.

State and persistence behavior: connects/disconnects mutate live libp2p network state and connection-manager tags. Address/peer listing is read-only. No repo persistence.

Dependencies and integration points: used by `commands/swarm.go`; wraps libp2p host/network/swarm, peerstore EWMA latency, stream protocols, and coreiface error types.

Risks: `Disconnect` returns after closing the first matching connection for a specific address; multiple matching connections are not all closed. Connection-manager tagging keeps explicit connections preferred until other logic removes tags. Offline mode is represented by nil peerHost.

Test signals: exercised by CoreAPI swarm interface tests in `coreapi/test/api_test.go`.
