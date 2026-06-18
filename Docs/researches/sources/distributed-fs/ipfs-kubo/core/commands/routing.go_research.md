# sources/distributed-fs/ipfs-kubo/core/commands/routing.go

Purpose: implements `ipfs routing` subcommands for finding providers/peers, getting/putting routing records, and legacy provide/reprovide operations. Several commands are deprecated or experimental and proxy newer systems while keeping script compatibility.

Important APIs/types/functions: `RoutingCmd` registers `findprovs`, `findpeer`, `get`, `put`, `provide`, and `reprovide`. `provideCids`, `provideCidsRec`, `printEvent`, and `escapeDhtKey` are helpers. `errAllowOffline` rewrites offline put errors into a user-facing hint.

Control flow: provider/peer lookup requires an online node, wraps the request context with routing query event registration, starts async routing calls, publishes events, and emits each event. Legacy `routing provide` parses stdin arguments, checks `Provide.Enabled`, requires local blocks, starts provider records through `nd.Provider`, optionally walks DAGs recursively, and if a DHT client is active performs synchronous `provideCIDSync` for immediate announcement. `routing reprovide` checks legacy provider support and calls `provider.Reprovider.Reprovide`. `routing get` and `put` go through CoreAPI `Routing()`, base64-wrapping record bytes in query events for command transport.

State and persistence behavior: `put` writes routing records via CoreAPI and can write local-only IPNS data when `--allow-offline` is accepted by the routing layer. `provide` and `reprovide` mutate provider announcement state but not block data. Recursive provide walks local DAG data.

Dependencies and integration points: uses libp2p `routing.QueryEvent`, Kubo node routing/provider/DHTClient, CoreAPI routing, IPNS key parsing, CID parsing, blockstore/DAG service, and repo config `Provide.*`.

Risks: legacy recursive provide re-walks shared subgraphs and can re-announce duplicates. Event output is best-effort; some verbose provider events do not fully reflect provider-system internals. `put` validates IPNS names before emitting the peer ID, but routing validation still depends on record validators. Direct use of `nd.DHTClient` relies on `HasActiveDHTClient` to avoid typed-nil panics.

Test signals: no direct tests in this file. Related risk is covered indirectly by CoreAPI routing tests in the interface test suite and by `core_test.go` typed-nil DHT client tests.
