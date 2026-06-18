# sources/distributed-fs/ipfs-kubo/test/cli/ping_test.go

Purpose: smoke-tests `ipfs ping` against connected peers, unreachable peers, self, zero count, and an offline peer.

Important APIs and functions: `TestPing` uses `harness.NewT(t).NewNodes(2).Init().StartDaemons().Connect()`, `PeerID().String()`, `IPFS`, and `RunIPFS`. Assertions inspect exit codes, stdout prefixes, and stderr messages.

Control flow: connected-peer tests ping each direction with `-n 2`. The unreachable-peer case uses a hard-coded peer ID and expects stdout to include `Looking up peer ...` before stderr begins with `Error:`. Self-ping runs against each node's own peer ID and expects exit code 1 plus `can't ping self`. Count zero expects `ping count must be greater than 0`. Offline peer starts two connected daemons, stops one, then expects `ping failed`.

State and persistence: no persistence is asserted. The test relies on live swarm connections and daemon state.

Dependencies and integration points: exercises libp2p ping, peer lookup, CLI argument validation, daemon connectivity, and harness daemon lifecycle.

Risks and test signals: unreachable peer lookup may vary with routing behavior, so the test checks broad error shape. Failure indicates broken ping validation, self-guard removal, incorrect exit codes, or connectivity cleanup problems after daemon stop.
