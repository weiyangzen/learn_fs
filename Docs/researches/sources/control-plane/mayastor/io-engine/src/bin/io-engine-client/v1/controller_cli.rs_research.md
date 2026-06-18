<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/controller_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/controller_cli.rs

### Purpose
`controller_cli.rs` implements v1 host NVMe controller inspection. It lists controllers and retrieves statistics for one named controller through the v1 host service.

### Important APIs, Types, And Functions
`ControllerArgs` wraps `ControllerCommands::{List, Stats}`. `StatsArgs` requires a controller name. `controller_state_to_str` renders v1 host controller states. `list_controllers` and `controller_stats` perform the service calls.

### Control Flow
`list_controllers` calls `ctx.v1.host.list_nvme_controllers(())` and prints name, size, state, and block size. `controller_stats` calls `stat_nvme_controller` for a name, handles `stats: None`, and prints read/write/unmap counters and byte totals. JSON mode prints full responses.

### State, Persistence, And Dependencies
The command is read-only. It depends on v1 host protobufs, colored JSON, SNAFU, and `TryFrom` enum conversion. It integrates with host NVMe initiator state, which is also visible through nexus children and replica backends.

### Risks And Test Signals
Unknown controller states still panic via `unwrap`. The default list header retains `NAMEs`. Tests should cover stats absent/present, unknown state values, single-name stats request construction, empty list handling, and JSON output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/controller_cli.rs -->
