## sources/distributed-fs/ipfs-kubo/test/sharness/t0195-noise.sh

Purpose: verifies Noise security transport interoperability and incompatibility with TLS-only peers.

Important APIs and helpers: uses IPTB, `ipfs config --json Swarm.Transports.Security.TLS/Noise`, swarm addresses, peer IDs, `ipfsi ping`, `iptb connect`, and error assertions.

Control flow and state: initializes testbed nodes, configures security transports so selected nodes support Noise and another supports TLS-only behavior, starts compatible nodes, verifies Noise-backed bidirectional ping, then starts incompatible nodes and asserts connection negotiation fails with a security protocol error.

Dependencies and integration points: covers libp2p security transport selection, Noise/TLS negotiation, ping over secured streams, and connection diagnostics.

Risks and test signals: catches accidental fallback to disabled security transports or unclear negotiation failures. Signals are successful pings among compatible nodes and expected failure text for TLS-incompatible connection.
