## sources/distributed-fs/ipfs-kubo/test/integration/bitswap_wo_routing_test.go

Purpose: verifies Bitswap block exchange can work among directly connected peers without routing.

Important APIs and control flow: `TestBitswapWithoutRouting` creates four online core nodes on a mocknet with `libp2p.NilRouterOption`, links all peers, fully connects every node to every other peer, manually inserts blocks into node blockstores, and retrieves them through each node's `Blocks.GetBlock`. It skips the original provider for the first block because the block is not in that node's exchange path.

State and dependencies: state is in-memory blockstore and Bitswap exchange state. Dependencies include go-block-format, go-cid, Kubo core/mock/libp2p, and libp2p mocknet.

Risks: the test relies on direct full-mesh connections and does not exercise provider discovery. The skip for the provider node documents an exchange edge case that could hang if changed carelessly. Test signals are no retrieval errors and exact raw block byte equality.
