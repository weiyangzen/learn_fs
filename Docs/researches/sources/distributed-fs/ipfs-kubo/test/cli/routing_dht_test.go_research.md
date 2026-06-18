# sources/distributed-fs/ipfs-kubo/test/cli/routing_dht_test.go

Purpose: validates DHT routing CLI commands for peer lookup, IPNS get/put, provider lookup, offline errors, and self-lookup failure, with and without pubsub IPNS support.

Important APIs and helpers: `waitUntilProvidesComplete` polls `provide stat -a` and parses `Provide queue` and `Ongoing provides` lines until no queued or ongoing provides remain. `testRoutingDHT` configures five nodes with `Routing.Type=dht` and optionally starts daemons with pubsub flags. `testSelfFindDHT` checks self lookup.

Control flow: each DHT variant starts connected nodes. `routing findpeer` asks node1 for node0 and expects node0's first swarm address. `routing get` publishes an IPNS record on node2 and retrieves it from node1, then nested tests put the returned record back and verify bad keys fail for `routing put` and `routing get`. `routing findprovs` adds content on node3, waits for provider work to complete, and expects node4 to find node3. Offline tests use an initialized but stopped node and expect online-mode errors for `findprovs`/`findpeer` and an offline put error without `--allow-offline`. Self-find uses `dht findpeer` against the node's own peer ID and expects failure.

State and persistence: IPNS records and provider records are stored in the DHT/network, while local content and name records originate in node repositories. No durable state is checked after restart.

Dependencies and integration points: integrates DHT routing, IPNS publishing, provider subsystem stats, pubsub-related daemon flags, swarm addresses, and routing command validation.

Risks and test signals: exact parsing of `provide stat -a` labels is fragile. Provider discovery depends on provide completion and connected DHT nodes. Failures signal DHT lookup regressions, invalid-key validation drift, broken provider announcements, or offline commands unexpectedly acquiring repo locks or running online-only code.
