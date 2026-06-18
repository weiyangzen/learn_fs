<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/controller_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/controller_cli.rs

### Purpose
`controller_cli.rs` exposes v0 host NVMe-controller inspection commands. It lists controllers and prints controller I/O statistics through the legacy Mayastor v0 service.

### Important APIs, Types, And Functions
`ControllerArgs` wraps `ControllerCommands::{List, Stats}`. `controller_state_to_str` maps `NvmeControllerState` integers to text. `list_controllers` and `controller_stats` are the RPC-backed command implementations.

### Control Flow
The handler dispatches by subcommand. `list_controllers` calls `list_nvme_controllers(Null {})`, then prints name, size, state, and block size. `controller_stats` calls `stat_nvme_controllers(Null {})`, unwraps each controller's `stats`, and prints read/write operation and byte counters. JSON output serializes the full response.

### State, Persistence, And Dependencies
The module is read-only against remote io-engine state. It depends on v0 `io_engine_api`, `colored_json`, `std::convert::TryFrom`, and `Context` formatting. It integrates with host NVMe controller discovery and statistics exported by the server.

### Risks And Test Signals
Enum conversion and `stats.as_ref().unwrap()` can panic if the server sends unknown states or incomplete stats. The default header says `NAMEs`, likely a typo but part of current output. Tests should include empty-controller responses, unknown enum behavior, missing stats, JSON output, and expected table columns for list and stats.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/controller_cli.rs -->
