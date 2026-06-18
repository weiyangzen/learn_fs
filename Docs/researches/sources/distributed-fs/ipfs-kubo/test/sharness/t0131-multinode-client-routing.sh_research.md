## sources/distributed-fs/ipfs-kubo/test/sharness/t0131-multinode-client-routing.sh

Purpose: tests DHT client-mode routing in a multi-node network.

Important APIs and helpers: defines `check_file_fetch` and `run_single_file_test`, uses `iptb`, `ipfsi`, `random-data`, `ipfs add`, `ipfs cat`, config for routing/client mode, and cluster connect helpers.

Control flow and state: sets up a testbed, starts nodes, connects them, adds a file on a node configured in client mode, and fetches that file from another client-mode node. It then shuts down the cluster. State includes provider records, blockstore content on the adding node, and DHT/routing state across peers.

Dependencies and integration points: covers libp2p connectivity, routing mode configuration, content providing/finding, Bitswap fetch after routing discovery, and IPTB cluster lifecycle.

Risks and test signals: catches regressions where client-mode nodes cannot publish or discover content through routing peers. The pass signal is byte-for-byte retrieval of the generated file from a different node.
