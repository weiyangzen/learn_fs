# sources/distributed-fs/ipfs-kubo/test/cli/http_gateway_over_libp2p_test.go

Purpose: verifies experimental HTTP gateway over libp2p behavior using two real Kubo nodes and libp2p HTTP clients.

Important APIs/functions: `TestGatewayOverLibp2p` configures `Experimental.Libp2pStreamMounting`, later enables `Experimental.GatewayOverLibp2p`, runs `ipfs p2p forward --allow-custom-protocol /http/1.1`, parses `commands.P2PLsOutput`, and uses both ordinary HTTP and `libp2phttp.Host.NamespacedClient`.

Control flow: two nodes start and connect. One holds gateway data; another acts as HTTP-over-libp2p proxy. Before enabling the gateway feature, HTTP through the proxy is expected to fail. After restart/reconnect, tests assert remote content is not fetched, deserialized responses are rejected, and raw block responses are served through both Kubo p2p proxy and direct libp2p namespaced client.

State and persistence: mutates experimental config, adds blocks to each repo, starts p2p listeners, and restarts the gateway node.

Dependencies/integration: depends on Kubo p2p commands, go-cid, go-libp2p, libp2p HTTP transport, multiaddr conversion, and harness multi-node connectivity.

Risks: experimental flags, p2p listener parsing, and daemon restart timing make this integration-sensitive. Test signals are connection errors before enablement, HTTP status codes, and exact raw block bytes.
