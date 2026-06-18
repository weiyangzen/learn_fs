# sources/distributed-fs/ipfs-kubo/core/coreapi/routing.go

Purpose: implements CoreAPI routing get/put/find/provide operations over libp2p routing and Kubo provider systems.

Important APIs/types/functions: `RoutingAPI`, methods `Get`, `Put`, `FindPeer`, `FindProviders`, `Provide`, helper `normalizeKey`, and recursive helper `provideKeysRec`.

Control flow: `Get` requires node online and fetches normalized key value. `Put` parses allow-offline option, checks online accordingly, normalizes key, and stores value. `FindPeer` and `FindProviders` require online mode; provider lookup resolves the path to a root CID and validates provider count. `Provide` resolves a path, verifies the root block is local, then either starts single-CID providing or recursively walks the local DAG in an offline DAG service, streaming unique CIDs into a multihash slice before one `StartProviding`.

State and persistence behavior: `Put` writes routing records through routing backend; with offline router it can store local records in datastore. `Provide` mutates provider advertisement state. Reads may query network and local routing.

Dependencies and integration points: used by `commands/routing.go` and external CoreAPI callers. Integrates blockstore, provider, routing validators, path resolution, cidutil streaming sets, and tracing.

Risks: `Get` checks `api.nd.IsOnline` directly rather than `checkOnline`, so offline option semantics differ from `Put`. Recursive provide accumulates all multihashes in memory before announcing. `provideKeysRec` has careful errCh race handling; regressions here can hide DAG walk errors or hang on context cancellation.

Test signals: covered by CoreAPI interface tests and provider-related tests. Command-level routing uses this implementation for get/put.
