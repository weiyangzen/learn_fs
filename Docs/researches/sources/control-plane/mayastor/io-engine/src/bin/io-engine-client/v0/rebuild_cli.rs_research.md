<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/rebuild_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/rebuild_cli.rs

### Purpose
`rebuild_cli.rs` implements the v0 nexus-child rebuild control CLI. It starts, stops, pauses, resumes, inspects state, reads detailed stats, and reports progress for a given nexus UUID and child URI.

### Important APIs, Types, And Functions
`RebuildArgs` wraps `RebuildCommands::{Start, Stop, Pause, Resume, State, Stats, Progress}`. `UuidUriArgs` supplies the nexus UUID and child URI. Each command has one async function that maps directly to a v0 rebuild RPC.

### Control Flow
Start/stop/pause/resume build their respective requests with UUID and URI and print the URI on success. `state` prints a one-column state table. `stats` prints block totals, recovered blocks, progress, segment size, block size, and task counters. `progress` prints only progress. JSON mode serializes the full response in all cases.

### State, Persistence, And Dependencies
The module changes and observes remote rebuild jobs. It depends on v0 protobufs, `uuid`, colored JSON, SNAFU mapping, and the shared context. It integrates with nexus child add/remove and child state management.

### Risks And Test Signals
The module trusts server-provided fields and has no local validation for URI consistency with the nexus. Rebuild operations are inherently stateful and races can occur if another controller changes child state concurrently. Tests should cover every request type, JSON/default output, server not-found/conflict statuses, and formatting for stats/progress tables.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/rebuild_cli.rs -->
