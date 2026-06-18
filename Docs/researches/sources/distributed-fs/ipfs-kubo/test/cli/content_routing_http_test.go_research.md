# sources/distributed-fs/ipfs-kubo/test/cli/content_routing_http_test.go

Purpose: verifies delegated HTTP content routing is used for uncached block retrieval and sends the Kubo version as User-Agent.

Important APIs/types/functions: `userAgentRecorder`, `TestContentRoutingHTTP`, `httprouting.MockHTTPContentRouter`, `boxo/routing/http/server.Handler`, `httptest.NewServer`, and async `Runner.Run`.

Control flow: a mock HTTP routing server records user agents, a node is configured with `Routing.DelegatedRouters`, content is added in no-pin/offline mode to compute a CID, and a long-running `block stat` for that CID is started. The test waits until `FindProviders` is called and compares recorded user agents with `ipfs id -f <aver>`.

State/persistence: temporary daemon config and mock router call counters; the spawned `block stat` process is killed in cleanup.

Dependencies/integration: delegated routing client, content router server adapter, command runner lifecycle, user-agent version formatting, and provider lookup paths.

Risks/test signals: asynchronous and timeout-sensitive. It confirms lookup initiation, not successful retrieval.
