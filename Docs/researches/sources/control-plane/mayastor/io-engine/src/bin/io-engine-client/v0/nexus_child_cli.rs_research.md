<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/nexus_child_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/nexus_child_cli.rs

### Purpose
This file implements v0 nexus child state operations nested under the nexus CLI: fault, offline, online, and retire. It is an operational control surface for child state transitions.

### Important APIs, Types, And Functions
`ChildArgs` wraps `ChildCommands`. `FaultArgs` and `ChildOpArgs` carry nexus UUID and child URI. `fault` calls a dedicated v0 RPC, while `child_operation` sends an integer action code for offline, online, or retire.

### Control Flow
The handler maps `Fault` to `fault`, `Offline` to action `0`, `Online` to action `1`, and `Retire` to action `2`. Both functions stringify UUIDs, clone the URI for output, perform the RPC, and either print colored JSON or the child URI.

### State, Persistence, And Dependencies
The module changes remote nexus-child state but persists nothing locally. It depends on v0 nexus child RPC messages, `uuid`, `colored_json`, and shared `Context` output settings. It is invoked through `v0/nexus_cli.rs`.

### Risks And Test Signals
The action integers are implicit protocol contracts and are not self-documenting. A server-side enum reorder or mismatch would change behavior. Tests should cover all action mappings, JSON/default output, UUID parsing, URI pass-through, and gRPC error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/nexus_child_cli.rs -->
