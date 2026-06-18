# sources/distributed-fs/ipfs-kubo/test/cli/dht_autoclient_test.go

Purpose: smoke-tests DHT `autoclient` routing in a local ten-node network.

Important APIs/functions: `TestDHTAutoclient`, `harness.NewNodes`, `ForEachPar`, `StartDaemons`, `Connect`, `IPFSAdd`, and `cat`.

Control flow: nodes 8 and 9 are configured as `Routing.Type=autoclient`, all ten daemons start and connect, then one subtest verifies content added by an autoclient node can be retrieved by another autoclient node, while another verifies server-mode-added content is retrievable from every node.

State/persistence: multi-node blockstores, DHT routing state, provider records, and random byte payloads.

Dependencies/integration: DHT mode selection, autoclient behavior, provider discovery, Bitswap/content retrieval, and harness network connection helpers.

Risks/test signals: concise but depends on local routing convergence. Use of `Stdout.Trimmed()` with random bytes plus appended carriage return is intended to preserve comparison shape.
