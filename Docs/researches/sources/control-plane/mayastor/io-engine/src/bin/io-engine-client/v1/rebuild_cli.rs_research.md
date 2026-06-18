<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/rebuild_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/rebuild_cli.rs

### Purpose
`rebuild_cli.rs` implements v1 rebuild control and inspection for nexus children. It extends the v0 command set with rebuild history.

### Important APIs, Types, And Functions
`RebuildArgs` wraps start, stop, pause, resume, state, stats, progress, and history commands. `UuidUriArgs` identifies a child rebuild by nexus UUID and child URI; `UuidArgs` identifies a nexus for history. `rebuild_state_to_str` renders job states.

### Control Flow
Start/stop/pause/resume send v1 nexus rebuild requests and print the child URI. `state` sends `RebuildStateRequest` and prints the state. `stats` sends `RebuildStatsRequest` and prints total, recovered, transferred, remaining, progress, block/task fields, and partial flag. `progress` reuses stats and prints just progress. `history` fetches records for a nexus and prints child/source URIs, block counters, state, task block size, partial flag, start, and end timestamps.

### State, Persistence, And Dependencies
The module changes and observes remote rebuild jobs and historical records. It depends on v1 nexus protobufs, `uuid`, colored JSON, SNAFU, and enum conversion. It integrates with nexus child lifecycle and rebuild history storage maintained by io-engine.

### Risks And Test Signals
History unwraps start and end timestamps, which can panic for incomplete records. Enum conversion unwraps can panic on unknown states. Tests should cover every command, missing history timestamps, empty history, state mapping, JSON/default output, and concurrent rebuild state transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/rebuild_cli.rs -->
