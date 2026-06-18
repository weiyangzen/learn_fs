## sources/distributed-fs/ipfs-kubo/test/sharness/t0190-quic-ping.sh

Purpose: validates peer ping over QUIC-v1 swarm addresses.

Important APIs and helpers: uses IPTB, `ipfsi config --json Addresses.Swarm`, peer ID retrieval, `ipfsi ping -n2`, invalid self-ping and zero-count cases, and `iptb stop`.

Control flow and state: initializes a two-node testbed, configures QUIC swarm addresses, starts nodes, records peer IDs, verifies each node can ping the other, verifies pinging self through the command fails, verifies `-n0` fails, and stops the cluster.

Dependencies and integration points: covers QUIC transport listener/dialer setup, libp2p ping protocol, swarm address config, and command validation.

Risks and test signals: catches QUIC transport regressions and bad ping argument handling. Passing requires bidirectional remote ping success and expected failures for self and zero-count pings.
