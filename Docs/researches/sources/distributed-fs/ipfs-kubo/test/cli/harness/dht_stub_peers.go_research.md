# sources/distributed-fs/ipfs-kubo/test/cli/harness/dht_stub_peers.go

Purpose: supplies in-process loopback libp2p DHT peers so tests can exercise provider records without the public DHT.

Important APIs/types/functions: `stubPeerPool` owns libp2p hosts, DHT instances, a shared `records.ProviderStore`, and a cancel function. `newStubPeerPool(count)` creates server-mode DHT peers, full-mesh connects them, and shares `sharedMemStore`. `Close` tears down hosts and DHTs. `sharedMemStore` implements `AddProvider`, `GetProviders`, and `Close`.

Control flow: harness code lazily creates a pool, injects peer multiaddrs into node bootstrap config, and sets `TEST_DHT_STUB`. Kubo daemons send real DHT messages over loopback; provider records are accumulated in the shared in-memory map keyed by hex-encoded record key.

State and persistence: all provider state is in memory and disappears on cleanup. The only persistent effect is node config bootstrap mutation performed by the caller.

Dependencies/integration: depends on go-libp2p, go-libp2p-kad-dht, peer IDs, DHT provider-store interfaces, and harness cleanup.

Risks: full-mesh connection cost grows quadratically; stale peers can leak ports if cleanup is skipped. The fixed `stubDHTPeerCount` of 20 is tied to Kademlia bucket assumptions. Test signal is whether provider discovery works locally in DHT-dependent CLI tests.
