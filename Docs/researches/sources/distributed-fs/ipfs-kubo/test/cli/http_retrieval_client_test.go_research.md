# sources/distributed-fs/ipfs-kubo/test/cli/http_retrieval_client_test.go

Purpose: end-to-end test for HTTP-only content retrieval through delegated routing and trustless gateway block responses.

Important APIs/functions: `TestHTTPRetrievalClient`, `NewMockHTTPProviderServer`, and `splitHostPort`. The test configures `HTTPRetrieval.Enabled`, `TLSInsecureSkipVerify`, and `Routing.DelegatedRouters`, then uses a `httprouting.MockHTTPContentRouter`.

Control flow: the test computes a CID without adding data locally (`ipfs add -n`), starts an HTTPS HTTP/2 mock provider that serves `/ipfs/{cid}` with `application/vnd.ipld.raw`, registers that provider in a delegated routing server, starts Kubo, verifies `routing findprovs`, and finally runs `ipfs cat` to retrieve bytes over HTTP.

State and persistence: node config changes persist in the test repo; the actual content is intentionally not added to the local repo. Mock routing/provider state is in-memory httptest server state.

Dependencies/integration: integrates Boxo routing HTTP server/types, Kubo HTTP retrieval config, random test data, peer/multiaddr types, and harness daemon lifecycle.

Risks: depends on TLS skip verify and HTTP/2 test server behavior. The provider peer ID is static and only the multiaddr matters, so peer identity is not deeply validated. Test signals are provider lookup output and exact `ipfs cat` body.
