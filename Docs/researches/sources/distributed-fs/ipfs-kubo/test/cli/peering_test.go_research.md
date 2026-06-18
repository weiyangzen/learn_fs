# sources/distributed-fs/ipfs-kubo/test/cli/peering_test.go

Purpose: verifies configured peering relationships reconnect automatically across disconnects and daemon start order. It exercises the harness peering configuration and Kubo's peering service through observable swarm peers.

Important APIs and helpers: local closures `containsPeerID`, `assertPeered`, `assertNotPeered`, and `assertPeerings` convert `from.Peers()` multiaddrs into peer IDs with `h.ExtractPeerID`, then poll with `assert.Eventuallyf`. `harness.CreatePeerNodes` creates initialized nodes with a list of `harness.Peering{From, To}` relationships.

Control flow: `TestPeering` runs four parallel scenarios. The first starts three nodes with bidirectional and one-way peering, verifies all configured peers, disconnects two nodes, and expects reconnection. The second disconnects the target side and expects the configured source to reconnect. The third starts only two nodes, verifies available peerings, starts the third later, and expects the delayed peering to come online. The fourth stops a peered daemon, waits until it is not connected, restarts it, and expects re-peering.

State and persistence: peering configuration is written before daemon startup by the harness. Runtime connection state is transient, but the peering service should continuously enforce configured peerings while daemons run and after peer restarts.

Dependencies and integration points: uses libp2p peer IDs, swarm peer lists, harness peering config generation, daemon lifecycle, and peer disconnect helpers. `testutils.ForEachPar` is used to parallelize peer assertions.

Risks and test signals: reconnection is inherently asynchronous, so the test uses one-minute positive waits and shorter negative waits. It can be flaky under slow networking or delayed peer discovery. Failures indicate that configured peerings are not enforced, reconnection is not triggered, or peer ID extraction from swarm addresses changed.
