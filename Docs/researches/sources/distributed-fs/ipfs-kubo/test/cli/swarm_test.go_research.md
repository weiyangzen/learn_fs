# sources/distributed-fs/ipfs-kubo/test/cli/swarm_test.go

Purpose: tests selected `ipfs swarm` commands, especially `swarm peers --identify` JSON output and `swarm addrs autonat` reachability output.

Important APIs and types: local structs model identify JSON: `identifyType`, `peer`, and `expectedOutputType`. Tests use `RunIPFS("swarm", "peers", "--enc=json", "--identify")`, `id --enc=json`, `SwarmAddrs`, and `swarm addrs autonat --enc=json`.

Control flow: one test verifies a node with no connections returns an empty peers list. Connected-peer tests verify identify fields include the peer ID, public key, agent version, addresses with `/p2p/<peer>`, and protocols. Another test compares the `Identify` object from `swarm peers --identify` to the peer's own `ipfs id --enc=json` output. The AutoNAT test parses reachability, reachable/unreachable/unknown arrays, and asserts reachability is one of `Public`, `Private`, or `Unknown`.

State and persistence: observations are live swarm and identify state. No persisted data is tested.

Dependencies and integration points: integrates swarm peer listing, identify protocol metadata, node IDs, multiaddrs, AutoNAT reachability reporting, and JSON encoding.

Risks and test signals: output assumes at least one connected peer appears at index 0. Address ordering or protocol set changes can affect exact comparisons. Failures indicate identify data not being surfaced, peer list JSON shape drift, or AutoNAT status returning invalid values.
