# sources/distributed-fs/ipfs-kubo/test/cli/harness/nodes.go

Purpose: collection helpers for operating on multiple `Node` instances in integration tests.

Important APIs/types/functions: `Nodes` is `[]*Node`. Methods include `Init`, `ForEachPar`, `Connect`, `StartDaemons`, and `StopDaemons`.

Control flow: initialization and daemon start/stop are parallelized with goroutines and a wait group. `Connect` intentionally connects nodes serially to avoid TLS handshake problems, then verifies each node has at least one peer address with a peer ID.

State and persistence: mutates every node repo and daemon process through delegated `Node` methods. No separate persistence exists in the collection.

Dependencies/integration: relies on `Node` methods, `testutils.ForEachPar` for initialization, sync wait groups, multiaddr peer-ID parsing, and harness logging.

Risks: `Connect` assumes `node.Peers()[0]` exists and will panic if peer setup silently failed. Parallel start/stop increases speed but can expose shared binary or port races. Test signals are successful multi-node daemon startup and peer table entries.
