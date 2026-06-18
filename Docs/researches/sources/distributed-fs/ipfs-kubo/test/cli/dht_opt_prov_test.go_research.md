# sources/distributed-fs/ipfs-kubo/test/cli/dht_opt_prov_test.go

Purpose: smoke test for experimental optimistic DHT provide.

Important APIs/functions: `TestDHTOptimisticProvide`, `config.Experimental.OptimisticProvide`, `config.Provide.DHT.SweepEnabled`, `routing provide`, and `routing findprovs`.

Control flow: two nodes are initialized, node 0 enables optimistic provide and disables the sweeping provider to use the legacy path, daemons connect, node 0 adds content and runs explicit provide, and node 1 searches for one provider, expecting node 0’s peer ID.

State/persistence: two daemon repos, provider records, and random content.

Dependencies/integration: experimental provide path, DHT provider storage/query, config flags, and local harness networking.

Risks/test signals: minimal smoke coverage; it confirms basic discoverability but not timing, retries, or large provider sets.
