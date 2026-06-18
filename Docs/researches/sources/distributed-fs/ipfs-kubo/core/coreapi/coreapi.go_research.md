# sources/distributed-fs/ipfs-kubo/core/coreapi/coreapi.go

Purpose: constructs the experimental embeddable Kubo CoreAPI facade over an `IpfsNode` and exposes typed sub-APIs.

Important APIs/types/functions: `CoreAPI` stores node services and option state. `NewCoreAPI`, sub-API accessors (`Unixfs`, `Block`, `Dag`, `Name`, `Key`, `Object`, `Pin`, `Swarm`, `PubSub`, `Routing`), `WithOptions`, and `getSession`.

Control flow: `NewCoreAPI` initializes default API settings then calls `WithOptions`. `WithOptions` copies parent settings, applies options, copies node dependencies into a new CoreAPI value, installs `checkOnline` and `checkPublishAllowed` closures, reads repo config, and if offline constructs an offline namesys/routing stack and clears peerstore/host/validator. If offline or fetch-blocks disabled, it replaces exchange/blockservice/DAG with offline local-only variants. `getSession` returns a shallow copy with a read-only session DAG.

State and persistence behavior: construction is mostly read-only, but returned APIs mutate underlying node services when sub-APIs are used. Offline options redirect reads/writes to local datastore/router behavior without changing the node. `checkPublishAllowed` prevents manual IPNS publish while IPNS mount is active unless the fusemount context marks a publish.

Dependencies and integration points: central bridge from `core.IpfsNode` to `coreiface`. Integrates namesys, offline routing, blockservice, path resolvers, repo config, fuse mount context, pubsub, provider, and tracing-enabled sub-APIs.

Risks: `WithOptions` requires `api.nd`; manually constructed CoreAPI without node cannot apply options. Offline mode clears several fields, so sub-APIs that assume peerHost/peerstore must return offline errors. Config errors prevent API creation.

Test signals: `coreapi/test/api_test.go` runs the shared CoreAPI interface suite against this implementation.
