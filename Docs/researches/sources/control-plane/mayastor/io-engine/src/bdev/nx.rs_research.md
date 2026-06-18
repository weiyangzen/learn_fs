## sources/control-plane/mayastor/io-engine/src/bdev/nx.rs

### Purpose
`nx.rs` implements a URI adapter for creating and destroying nexus devices directly from `nexus:///name?size=...&children=...`. It is intended for testing and benchmarking rather than normal control-plane operation.

### Important APIs, Types, And Functions
`Nexus` stores name, size in bytes, and child URIs. `TryFrom<&Url>` parses the URI. `GetName` returns the nexus name. `CreateDestroy` calls `nexus_create()` and `nexus_lookup_mut().destroy()`.

### Control Flow
Parsing requires a nonempty path, `size` query parsed through byte-unit, and `children` query split on commas; unknown parameters are rejected. `create()` calls `crate::bdev::nexus::nexus_create()` with no UUID and returns the nexus name. `destroy()` looks up the mutable nexus by name and calls its async destroy method.

### State, Persistence, And Dependencies
State is owned by the nexus subsystem after creation; this adapter stores only parsed URI data. Dependencies include URI helpers, byte-unit parsing, unknown-parameter rejection, nexus create/lookup/destroy, and `BdevError` mapping.

### Integration Points
Generic `bdev_create()` can use this adapter to spin up nexus devices in tests or performance tools. It bypasses gRPC/control-plane workflows and therefore should not be treated as the primary product lifecycle path.

### Risks
Children are split by comma without escaping, which is acceptable for current URI forms but fragile for future child URI syntaxes. Empty children entries are not filtered. The adapter does not manage persistence keys or share state.

### Test Signals
Cover missing size, invalid size, missing children, unknown parameters, multiple child parsing, empty child entries, create error mapping, destroy missing nexus, and successful destroy error propagation.
