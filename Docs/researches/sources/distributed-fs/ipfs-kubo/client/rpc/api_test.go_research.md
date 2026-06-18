# sources/distributed-fs/ipfs-kubo/client/rpc/api_test.go

## Purpose
This test file validates the HTTP CoreAPI client against real harness nodes and focused URL/header behavior.

## Important APIs, Types, And Functions
`NodeProvider.MakeAPISwarm` creates harness nodes, initializes empty repos, enables filestore, sets provide strategy to roots, starts daemons with optional online connectivity, builds `NewApi` clients, and removes the default empty-node pin. Tests include `TestHttpApi`, `Test_NewURLApiWithClient_With_Headers`, and `Test_NewURLApiWithClient_HTTP_Variant`.

## Control Flow
`TestHttpApi` runs the shared `coreiface/tests.TestApi`. Header testing uses an `httptest.Server` and calls `api.Pin().Rm` to assert custom headers reach HTTP requests. Scheme testing checks TCP, TLS, HTTPS, and TLS/HTTP multiaddrs map to expected URLs.

## State And Persistence Behavior
It creates temporary harness repos and running daemons; test cleanup is owned by the harness.

## Dependencies And Integration Points
It integrates RPC client construction, CLI harness nodes, `coreiface` conformance tests, config mutation, pubsub startup, and multiaddr URL handling.

## Risks And Test Signals
Risks are harness flakiness and broad shared API test failures being hard to localize. Signals are complete CoreAPI conformance, expected custom header receipt, and correct URL scheme decisions.
