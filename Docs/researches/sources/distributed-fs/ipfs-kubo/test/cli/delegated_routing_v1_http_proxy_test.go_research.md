# sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_proxy_test.go

Purpose: verifies a Kubo node can use another Kubo node’s exposed Routing V1 HTTP API as its routing backend.

Important APIs/functions: `TestRoutingV1Proxy`, `setupNodes`, `waitUntilProvidesComplete`, IPNS helpers, and `config.RouterParser`/`config.Methods`.

Control flow: setup creates three nodes: node 0 exposes Routing V1 with DHT, node 1 uses custom HTTP routing pointing at node 0 and no DHT, and node 2 keeps the DHT operative. Subtests cover provider lookup, peer lookup, IPNS record get/resolve through proxy routing, and publishing an IPNS record from the proxy-backed node for retrieval by the DHT node.

State/persistence: multiple daemons, peer connectivity, DHT provider/IPNS records, and published names.

Dependencies/integration: gateway Routing API exposure, DHT routing, HTTP delegated routing client, IPNS record marshaling, and harness multi-node connectivity.

Risks/test signals: meaningful end-to-end proxy signal; depends on local multi-node DHT convergence and provider completion waiting.
