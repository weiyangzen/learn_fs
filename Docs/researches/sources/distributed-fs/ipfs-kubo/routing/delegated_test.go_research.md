# sources/distributed-fs/ipfs-kubo/routing/delegated_test.go

Purpose: validates custom routing parser behavior for HTTP routers and composable router graphs.

Important APIs and control flow: `TestParser` builds HTTP and sequential routers and checks methods sharing router names share router instances in the resulting `Composer`. `TestParserRecursive` builds nested sequential and parallel router graphs and expects a `Composer`. `TestParserRecursiveLoop` creates a dependency loop and checks for the loop error. `generatePeerID` creates an Ed25519 key and base64 private key for HTTP router identity.

State and persistence: no disk state; creates crypto keys and routing structs.

Dependencies and integration: exercises `Parse`, HTTP router construction, config router types, and composer assignment.

Risks and test signals: tests use dummy HTTP endpoints but do not perform network calls. They do not cover DHT routers, missing parameters, invalid keys, duplicate metric view registration, or nil extra params.
