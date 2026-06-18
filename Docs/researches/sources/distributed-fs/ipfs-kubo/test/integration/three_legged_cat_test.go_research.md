## sources/distributed-fs/ipfs-kubo/test/integration/three_legged_cat_test.go

Purpose: tests a three-node retrieval path where an adder and catter discover each other through a bootstrap/routing node rather than direct pair bootstrap.

Important APIs and control flow: `RunThreeLeggedCat` creates a mocknet, a public bootstrap node, adder, and catter, links all peers, bootstraps both data nodes to the bootstrap peer, adds data via the adder CoreAPI, explicitly provides the root CID through routing, then gets the UnixFS path through the catter CoreAPI and byte-compares. Tests cover instantaneous 1MB plus epic slow blockstore/network/routing and 100MB coast-to-coast presets.

State and dependencies: all state is in-memory mocknet, DHT/routing records, and UnixFS blockstores. Dependencies include Kubo mock public nodes, boxo bootstrap/files, coreapi, libp2p mocknet, and latency configs.

Risks: explicit `Routing.Provide` is required to avoid racing the async reprovider; removing it may make tests flaky. Epic cases are expensive and gated by `IPFS_EPIC_TEST`. Test signal is successful routed discovery and exact content retrieval.
