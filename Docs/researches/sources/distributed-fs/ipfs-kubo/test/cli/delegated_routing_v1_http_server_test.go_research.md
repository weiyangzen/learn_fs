# sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_server_test.go

Purpose: server-side Routing V1 API coverage for providers, peers, IPNS get/put, and `GetClosestPeers` behavior across routing modes.

Important APIs/functions: `TestRoutingV1Server`, local `setupNodes`, `boxo/routing/http/client`, `types`, `iter.ReadAllResults`, `autoconf.FallbackBootstrapPeers`, `peer.ToCid`, and IPNS helpers.

Control flow: local multi-node subtests expose routing APIs on DHT nodes and assert provider, peer, and IPNS responses. Disabled-routing subtests configure `none`, `delegated`, and `custom` modes and expect `GetClosestPeers` errors. Enabled-routing subtests use `auto`, `autoclient`, `dht`, and `dhtclient` with fallback bootstrap peers, retrying until WAN DHT returns peer records capped at 20.

State/persistence: local DHT nodes, published IPNS records, lonely node record insertion, bootstrap peer config, and external network routing table state.

Dependencies/integration: Routing V1 server, DHT routers, delegated/custom routing configs, IPNS routing storage, HTTP client iterators, and WAN bootstrap.

Risks/test signals: high coverage but live-network `GetClosestPeers` lane is inherently slower/flakier and can consume minutes.
