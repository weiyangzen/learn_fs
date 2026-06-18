<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/bdev_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/bdev_cli.rs

### Purpose
This file implements v0 bdev CLI operations: list, create from URI, share over NVMf, unshare, and destroy. It is a thin clap-to-v0-gRPC adapter with human-table and JSON output modes.

### Important APIs, Types, And Functions
`BdevArgs` owns a `BdevCommands` subcommand. `CreateArgs`, `ShareArgs`, `DestroyArgs`, and `UnshareArgs` model the CLI inputs. `BdevShareProtocol` currently supports only `Nvmf`. The handler dispatches to `list`, `create`, `share`, `destroy`, or `unshare`.

### Control Flow
`list` calls `ctx.bdev.list(Null {})` and either serializes the response or prints bdev UUID, block count, block size, claim owner, name, and share URI. `create` sends `BdevUri { uri }` and prints the created name. `share` maps the enum to `"nvmf"`, sends `BdevShareRequest`, and prints the returned URI. `destroy` first lists bdevs to find the name, unshares it by name, then destroys by the original URI found in the list response. `unshare` sends the bdev name.

### State, Persistence, And Dependencies
The module persists no state. All durable effects are remote io-engine bdev operations. It depends on v0 protobuf types, `colored_json`, `byte_unit` indirectly through `Context`, `url::Url`, and SNAFU gRPC status mapping.

### Risks And Test Signals
`destroy` depends on a prior list response and destroys by URI, so stale list data or duplicate names would be risky. It unshares before destroy and propagates an unshare error even when the bdev is not shared. JSON formatting uses `unwrap`. Tests should cover create URI validation, destroy not-found mapping to gRPC not-found, share allowed-host propagation, empty list behavior, and JSON/default output shape.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/bdev_cli.rs -->
