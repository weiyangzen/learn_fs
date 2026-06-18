<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_child_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_child_cli.rs

### Purpose
This file implements v1 nexus child state operations: fault, offline, online, and retire. It mirrors the v0 child CLI but uses the v1 nexus service.

### Important APIs, Types, And Functions
`ChildArgs` wraps `ChildCommands`. `FaultArgs` and `ChildOpArgs` carry nexus UUID and child URI. `fault` sends `FaultNexusChildRequest`; `child_operation` sends `ChildOperationRequest` with an action integer.

### Control Flow
The handler maps `Offline`, `Online`, and `Retire` to action values `0`, `1`, and `2`. Each implementation stringifies the UUID, preserves the URI for output, sends the RPC, and prints either the JSON response or the URI.

### State, Persistence, And Dependencies
State changes are remote nexus-child state transitions. The module depends on v1 nexus protobufs, `uuid`, colored JSON, SNAFU, and shared context. It is nested under `v1/nexus_cli.rs`.

### Risks And Test Signals
Action numbers are implicit service contracts. The CLI does not validate that the child URI belongs to the nexus before sending. Tests should cover all action mappings, UUID parsing, JSON/default output, server errors, and behavior for absent children.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_child_cli.rs -->
