## sources/distributed-fs/ipfs-kubo/test/sharness/t0182-circuit-relay.sh

Purpose: verifies relay-v2 circuit relay connectivity through a configured relay node.

Important APIs and helpers: uses IPTB, `ipfsi id`, JSON config with `jq`, static relay configuration, swarm connect, peer ID extraction, and peer list assertions.

Control flow and state: initializes nodes, starts them for configuration, records peer IDs, configures one node as a static relay for node A, configures the relay node and node B, restarts nodes, connects A and B to the relay, waits until relay reservation/readiness is available, connects A to B through the relay, then checks connection output and peer lists for A and B.

Dependencies and integration points: covers libp2p relay service/client config, reservation readiness, multiaddr relay paths, swarm connection reporting, and IPTB orchestration.

Risks and test signals: catches relay reservation timing, wrong static relay config, and peer list inconsistencies after relayed connections. Passing requires successful relay connection output and expected peer entries on both endpoints.
