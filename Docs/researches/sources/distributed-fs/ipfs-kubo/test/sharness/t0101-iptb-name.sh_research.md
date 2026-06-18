## sources/distributed-fs/ipfs-kubo/test/sharness/t0101-iptb-name.sh

Purpose: verifies multi-node IPNS publishing and recursive IPNS resolution across an IPTB cluster.

Important APIs and helpers: uses `iptb testbed create`, `ipfsi <node> add`, `ipfsi <node> name publish`, `iptb attr get id`, `ipfsi cat`, `test_cmp`, and `iptb stop`.

Control flow and state: creates a three-node localipfs testbed, adds a file on node 1, publishes it under node 1's IPNS name, publishes a second IPNS entry on node 2 that points to node 1's name, then cats the node 2 name from node 3 and compares content.

Dependencies and integration points: covers IPTB orchestration, multi-node routing, IPNS record publication, recursive name resolution, and cross-node content retrieval.

Risks and test signals: catches failures in namesys recursion, provider discovery, or multi-node IPNS propagation. The pass signal is node 3 retrieving exactly the file initially added by node 1 through a chained `/ipns/` reference.
