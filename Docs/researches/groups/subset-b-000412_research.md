# subset-b-000412 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/context.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/context.rs

### Purpose
`context.rs` is the shared execution context for `io-engine-client`. It normalizes connection options, constructs the v0 and v1 tonic clients, stores output preferences, and provides common table, verbosity, and byte-unit formatting helpers used by every CLI command module.

### Important APIs, Types, And Functions
The main public surface is `Context::new`, `Context::v1`, `Context::v2`, `Context::units`, `Context::units_with`, `Context::print_list`, and `Context::print_streamed_list`. `OutputFormat` selects human or JSON output, and `Units` selects bytes, binary, or decimal display. The nested private `v1` module aliases all v1 generated service clients and groups them into `v1::Context`.

### Control Flow
`Context::new` accepts a bind string, verbosity flags, units, and output format. It parses the URI, falls back to bracketed IPv6 parsing when plain parsing fails, injects `http` when no scheme is present, adds port `10124` when no port is supplied, and defaults the path to `/`. It then builds a tonic `Endpoint` and eagerly connects v0 Mayastor/Bdev/Json clients plus all v1 clients. Printing helpers build aligned table columns from the first rows and headers; headers prefixed with `>` are right-aligned. `print_streamed_list` buffers the first streamed row to size columns, emits the header when verbose, then drains the channel.

### State, Persistence, And Dependencies
The context owns client handles, verbosity, unit preference, and output mode for a single process invocation. It persists nothing beyond stdout/stderr. Dependencies include `tonic::transport::Endpoint`, generated `io_engine_api` clients, `http::Uri` parts, `byte_unit`, `bytes`, and SNAFU errors. URI normalization is an integration point for both `API_VERSION=v0` and default v1 clients.

### Risks And Test Signals
Every client connection uses `unwrap`, so transport failures panic instead of returning `ContextCreate`. `print_list` asserts non-empty data and matching header length, so callers must guard empty lists. `print_streamed_list` sizes columns from the first row only, so later longer rows can exceed header widths. Useful tests cover bind strings with host-only, IPv6, explicit ports, quiet/verbose formatting, right-aligned numeric columns, byte-unit selection, and connection error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/main.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/main.rs

### Purpose
`main.rs` is the top-level binary entrypoint for `io-engine-client`. It selects the v0 or v1 command tree, initializes logging, defines shared gRPC client aliases, and centralizes user-facing error reporting.

### Important APIs, Types, And Functions
The file defines `MayaClient`, `BdevClient`, and `JsonClient` aliases over tonic `Channel`, the shared `ClientError` enum, and the crate-local `Result<T>`. `ClientError` covers gRPC statuses, context construction failures, and CLI-level missing-value validation.

### Control Flow
The Tokio main runtime uses two worker threads. It reads `API_VERSION`: `v0` dispatches to `v0::main_`, `v1` and unset both dispatch to `v1::main_`, and any other value panics. If the selected command tree returns an error, the binary prints the display error, prints a SNAFU backtrace when available, and exits with status 1.

### State, Persistence, And Dependencies
The binary is stateless aside from environment variables and process exit status. It depends on generated v0 clients, `tonic`, `snafu`, `env_logger`, Tokio, and the sibling `context`, `v0`, and `v1` modules. It integrates with every subcommand through the shared `ClientError` and `Result` type.

### Risks And Test Signals
Invalid `API_VERSION` is a panic rather than a formatted CLI error. The default API version is v1, which matters for scripts written before v1 became default. Tests should assert default/v0/v1 dispatch, non-zero exit on subcommand error, backtrace printing when enabled, and compatibility of `ClientError` display strings used by operators and automation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/main.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/device_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/device_cli.rs

### Purpose
This file implements the v0 block-device discovery CLI. It lists host block devices, optionally including devices already in use, and formats partition, filesystem, and device-link metadata.

### Important APIs, Types, And Functions
`DeviceArgs` supports `DeviceCommands::List(ListArgs)`. `ListArgs` carries the `--all` flag. `get_partition_type` formats optional partition metadata, and `list_block_devices` performs the RPC and output conversion.

### Control Flow
The handler calls `list_block_devices`. That sends `ListBlockDevicesRequest { all }` to the v0 Mayastor client. JSON output consumes and prints the full response. Default output extracts optional filesystem fields, optional partition type, availability, model, path, and quoted devlinks into a wide table.

### State, Persistence, And Dependencies
The command is read-only. It depends on host device scanning performed by io-engine, v0 protobuf structs, `colored_json`, and the shared table printer. It integrates with pool creation workflows because operators use the output to pick candidate devices.

### Risks And Test Signals
Output width can become large with many symlinks. v0 has a single `mountpoint` string, unlike v1's mountpoint list. Tests should cover devices with and without partition/filesystem fields, `--all` propagation, empty results, devlink quoting, and JSON output consuming the response without later borrows.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/device_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/jsonrpc_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/jsonrpc_cli.rs

### Purpose
`jsonrpc_cli.rs` provides a v0 escape hatch for calling a raw SPDK JSON-RPC method through io-engine's gRPC JSON proxy. It is useful for methods not modeled by typed CLI subcommands.

### Important APIs, Types, And Functions
`JsonrpcArgs` carries a method name and optional raw JSON parameter string. `json_rpc_call` sends `JsonRpcRequest { method, params }` through `ctx.json`.

### Control Flow
The command does not parse the params locally; it forwards the string to the server. It logs that default output is JSON when the user did not request JSON explicitly, then prints `response.result` using colored JSON formatting. There is no separate table mode.

### State, Persistence, And Dependencies
The module persists no state and delegates all side effects to the named JSON-RPC method. Dependencies are v0 JSON protobuf types, `colored_json`, SNAFU status mapping, and tracing debug logs.

### Risks And Test Signals
Because params are raw strings, malformed JSON errors surface from the server. `to_colored_json_auto().unwrap()` can panic if the result is not valid JSON text. Tests should exercise empty params, invalid params propagation, successful raw call output, default-mode JSON behavior, and server errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/jsonrpc_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/mod.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/mod.rs

### Purpose
`v0/mod.rs` defines the v0 command tree for `io-engine-client`. It wires global options, v0 subcommands, context construction, and dispatch to each v0 CLI module.

### Important APIs, Types, And Functions
The file exports modules for bdev, controller, device, jsonrpc, nexus, perf, pool, rebuild, replica, and snapshot commands. `Opts` defines global `--bind`, `--quiet`, `--verbose`, `--units`, and `--output`. `Commands` enumerates all v0 command groups. `main_` is called by the top-level binary when `API_VERSION=v0`.

### Control Flow
`main_` parses clap arguments, builds a shared `Context`, then matches the selected `Commands` variant and awaits the corresponding handler. The default bind is `http://127.0.0.1:10124`; the default unit base is raw bytes; output defaults to human-readable tables.

### State, Persistence, And Dependencies
The module keeps only process-local parsed options. It depends on clap, `version_info`, SNAFU context mapping, and the shared context. It integrates with `main.rs` through `pub(super) async fn main_`.

### Risks And Test Signals
Every command pays the cost and failure surface of constructing all clients in `Context::new`, even if it only needs one. Global option defaults differ from v1, especially unit base and bind environment support. Tests should validate clap command availability, global option propagation, default values, quiet/verbose conflict, and dispatch to each handler.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/mod.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/nexus_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/nexus_cli.rs

### Purpose
`nexus_cli.rs` is the v0 CLI for nexus lifecycle and control operations. It creates, destroys, shuts down, publishes, unpublishes, lists, resizes indirectly through v1 child display, manages children, and gets/sets NVMe ANA state.

### Important APIs, Types, And Functions
`NexusArgs` owns `NexusCommands`, including `Create`, `Create2`, `Destroy`, `Shutdown`, `Publish`, `Unpublish`, `AnaState`, `Add`, `Remove`, `List`, `List2`, `Children`, `Children2`, and nested child commands. Helper enums include `NexusShareProtocol` and `NvmeAnaState`. Mapping helpers convert nexus, child, reason, and ANA enum integers to display strings.

### Control Flow
Create commands generate a UUID when omitted, require at least one child, convert byte sizes, and send v0 create requests. `create2` includes name, NVMe controller ID bounds, reservation/preempt keys, and nexus info key. Destroy/shutdown/unpublish send single UUID requests. Publish defaults to NBD when no protocol is supplied and supports NVMf plus allowed hosts. List commands print nexus rows and optional child URIs. `children` reads v0 list output and filters by UUID; `children2` reads v1 nexus output to include child state reasons. ANA state either queries or sets based on the optional state argument. Add/remove convert `url::Url` to strings.

### State, Persistence, And Dependencies
All state is remote io-engine nexus state. The module depends on both v0 and v1 protobufs, `byte_unit`, `url`, `uuid`, tonic `Status`, and colored JSON. It integrates with v0 Mayastor RPCs and uses the v1 nexus client for richer child reason display.

### Risks And Test Signals
Several enum conversions use `unwrap`, so unknown server values can panic. `Publish` defaults to NBD in v0 while v1 defaults to NVMf, a compatibility trap. `children` fails with invalid-argument if the nexus is absent. Tests should cover missing children validation, autogenerated UUIDs, v0/v1 child listing differences, ANA get/set mappings, publish defaults, allowed-host propagation, and unknown enum handling.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/nexus_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/perf_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/perf_cli.rs

### Purpose
`perf_cli.rs` exposes the v0 resource-usage command. It reports process-level usage data, primarily the values returned by a server-side `getrusage`-style call.

### Important APIs, Types, And Functions
`PerfArgs` wraps `PerfCommands::Resource`. `get_resource_usage` calls `ctx.client.get_resource_usage(Null {})` and formats soft faults, hard faults, voluntary context switches, and involuntary context switches.

### Control Flow
The handler dispatches to `get_resource_usage`. The function logs a verbose request message, performs the RPC, and either prints the whole response as JSON or, when `usage` exists, prints a single table row. If `usage` is absent the table remains empty and is passed to `print_list`.

### State, Persistence, And Dependencies
The command is read-only and has no local persistence. It depends on v0 protobufs, `colored_json`, SNAFU gRPC mapping, and `Context` table printing.

### Risks And Test Signals
If the server returns `usage: None` in default mode, `ctx.print_list` receives an empty table and panics. Tests should cover populated usage, absent usage, JSON output, verbose logging, and empty response behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/perf_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/pool_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/pool_cli.rs

### Purpose
This file implements the v0 pool CLI for create, destroy, and list operations. It targets the legacy Mayastor pool RPCs and formats capacity using the shared unit preference.

### Important APIs, Types, And Functions
`PoolArgs` wraps `PoolCommands::{Create, Destroy, List}`. `CreateArgs` carries pool name and appended disk list, while `DestroyArgs` carries pool name. `pool_state_to_str` maps v0 pool-state enum values.

### Control Flow
`create` sends `CreatePoolRequest { name, disks }` and prints the pool name or JSON response. `destroy` sends `DestroyPoolRequest` and prints the name. `list` calls `list_pools(Null {})`, handles empty lists, converts capacity and used bytes through `Context::units`, maps state, joins disks, and prints a table.

### State, Persistence, And Dependencies
The module mutates remote pool state but stores nothing locally. Dependencies include v0 pool protobufs, `byte_unit`, `colored_json`, and `TryFrom` enum conversion. It integrates with device discovery and replica creation workflows.

### Risks And Test Signals
`pool_state_to_str` unwraps enum conversion and can panic on unknown values. Create does not locally require at least one disk, leaving validation to the server. Tests should cover create disk append semantics, empty list behavior, state mapping, unit formatting, destroy JSON silence, and server errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/pool_cli.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/replica_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/replica_cli.rs

### Purpose
This file implements v0 replica lifecycle, sharing, listing, and statistics commands. It supports both old create/list shapes and v2 create/list shapes while retaining v0 RPC transport.

### Important APIs, Types, And Functions
`ReplicaArgs` wraps `ReplicaCommands::{Create, Create2, Destroy, List, List2, Share, Stats}`. `CreateArgs` and `Create2Args` parse pool, name, UUID, size, thin provisioning, share protocol, and allowed hosts. `ShareProtocol` maps to numeric protocol values. `parse_byte` parses sizes, and `replica_protocol_to_str` renders protocol integers.

### Control Flow
Create maps protocol `None`/`none` to 0 and `nvmf` to 1, then sends either `CreateReplicaRequest` or `CreateReplicaRequestV2`. Destroy sends UUID only. `list` and `list2` fetch all replicas and print old or v2 columns. `share` sends `ShareReplicaRequest` but does not include CLI allowed hosts because `ShareArgs` has no allowed-host field. `stats` calls `stat_replicas` and unwraps each stats payload.

### State, Persistence, And Dependencies
The module creates and destroys remote replica bdevs and changes sharing state. It depends on v0 replica protobufs, `byte_unit`, `colored_json`, and shared formatting. It integrates with pool state and NVMf export paths.

### Risks And Test Signals
`stats.as_ref().unwrap()` can panic on incomplete responses. Protocol values are numeric and only partially modeled. `destroy` and unshare-like operations produce no JSON body in JSON mode. Tests should cover size parsing, allowed-host propagation on create, list/list2 column differences, stats with missing stats, protocol mapping, and server validation failures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/replica_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/snapshot_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/snapshot_cli.rs

### Purpose
`snapshot_cli.rs` is the minimal v0 snapshot CLI. It exposes only a single command to create a snapshot for a nexus UUID.

### Important APIs, Types, And Functions
`SnapshotArgs` wraps `SnapshotCommands::Create`. `CreateArgs` carries the nexus UUID. `create` sends `CreateSnapshotRequest` through the v0 Mayastor client.

### Control Flow
The handler dispatches to `create`, which stringifies the UUID, calls `create_snapshot`, then prints either the full JSON response or the UUID in default mode.

### State, Persistence, And Dependencies
The module creates remote snapshot state and has no local persistence. It depends on v0 snapshot RPCs, `uuid`, colored JSON, SNAFU, and `Context`.

### Risks And Test Signals
The v0 surface gives no list or destroy operation in this CLI, so cleanup must use other APIs. Tests should cover UUID parsing, successful create output, JSON formatting, and server-side errors for absent or invalid nexus UUIDs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/snapshot_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/bdev_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/bdev_cli.rs

### Purpose
This file implements v1 bdev CLI operations. It mirrors the v0 bdev command set but uses v1 service-specific RPCs and includes capacity in default list output.

### Important APIs, Types, And Functions
`BdevArgs` and `BdevCommands` define list, create, share, destroy, and unshare. `BdevShareProtocol` supports `Nvmf`. `CreateArgs`, `ShareArgs`, `DestroyArgs`, and `UnshareArgs` define command inputs. The implementation uses `ctx.v1.bdev`.

### Control Flow
`list` sends `ListBdevOptions { name: None }`, computes capacity as `num_blocks * blk_size`, and prints bdev metadata. `create` sends `CreateBdevRequest` and unwraps the optional returned bdev to print its name. `destroy` lists all bdevs, finds by name, unshares by name, then destroys by URI. `share` maps to `common::ShareProtocol::Nvmf` and propagates allowed hosts. `unshare` sends the name.

### State, Persistence, And Dependencies
All state changes occur in the remote v1 bdev service. Dependencies include v1 protobufs, `byte_unit`, `url`, colored JSON, SNAFU, and the shared context. It integrates with NVMf target management and lower-level bdev creation modules.

### Risks And Test Signals
Returned optional bdev fields are unwrapped in create/share. Capacity multiplication can overflow in theory. Destroy has the same list-then-unshare-then-destroy race as v0. Tests should cover optional response fields, allowed-host propagation, list filtering future compatibility, destroy not found, and default/JSON output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/bdev_cli.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/device_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/device_cli.rs

### Purpose
This file implements v1 host block-device discovery. It is the v1 equivalent of the device CLI and accounts for v1 filesystem mountpoint lists.

### Important APIs, Types, And Functions
`DeviceArgs` supports `DeviceCommands::List(ListArgs)`. `ListArgs` carries `--all`. `get_partition_type` formats partition scheme and type ID. `list_block_devices` calls `ctx.v1.host.list_block_devices`.

### Control Flow
The command sends `ListBlockDevicesRequest { all }`. JSON output serializes the response. Default output consumes the device vector, extracts optional filesystem data, joins multiple mountpoints and devlinks, formats availability, partition type, size, model, and device path, then prints a table.

### State, Persistence, And Dependencies
The module is read-only against remote host state. It depends on v1 host protobufs, colored JSON, SNAFU, and shared table formatting. It feeds operator decisions for pool creation/import.

### Risks And Test Signals
The table can be wide for many mountpoints or symlinks. Since it consumes the response in both branches, future code must avoid borrowing after `into_inner`. Tests should cover multiple mountpoints, missing filesystem/partition, `--all`, empty lists, and JSON output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/device_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/jsonrpc_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/jsonrpc_cli.rs

### Purpose
`jsonrpc_cli.rs` exposes raw JSON-RPC calls over the v1 JSON gRPC service. It is a compatibility and debugging escape hatch for SPDK or io-engine methods not covered by typed commands.

### Important APIs, Types, And Functions
`JsonrpcArgs` carries `method` and optional raw `params`. `json_rpc_call` sends `v1rpc::json::JsonRpcRequest` through `ctx.v1.json`.

### Control Flow
The command forwards method and parameter string unchanged. It treats default output as JSON, logs that fact at debug level, and prints the server `result` through colored JSON formatting.

### State, Persistence, And Dependencies
No local state is stored. Effects depend entirely on the invoked JSON-RPC method. Dependencies include v1 JSON protobufs, colored JSON, SNAFU status mapping, and tracing.

### Risks And Test Signals
Malformed params are detected server-side. Non-JSON or unexpected result text can panic in the colored JSON unwrap. Tests should cover empty params, successful raw method output, server parse errors, default-vs-json behavior, and error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/jsonrpc_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/mod.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/mod.rs

### Purpose
`v1/mod.rs` defines the default v1 `io-engine-client` command tree. It wires v1 global options, command modules, context construction, and dispatch.

### Important APIs, Types, And Functions
The file exports v1 command modules for bdev, controller, device, jsonrpc, nexus, perf, pool, rebuild, replica, snapshot, stats, plus private snapshot-rebuild and test modules. `Opts` defines global bind/quiet/verbose/units/output options. `Commands` includes v1-only `Stats`, `Test`, and `snapshot-rebuild`.

### Control Flow
`main_` parses clap options, creates `Context`, and matches the selected command to its handler. The default bind is `http://127.0.0.1` with optional `MY_POD_IP` environment override; `Context::new` adds port 10124. The default unit base is decimal.

### State, Persistence, And Dependencies
The module holds process-local CLI options only. It depends on clap, `version_info`, SNAFU context mapping, and all sibling command modules. It is selected by default from top-level `main.rs`.

### Risks And Test Signals
Differences from v0 defaults can surprise scripts: v1 is default, bind can come from `MY_POD_IP`, and units default to decimal. Tests should validate command availability, environment bind handling, global option propagation, command dispatch, quiet/verbose conflict, and default units.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/mod.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_cli.rs

### Purpose
`nexus_cli.rs` implements v1 nexus lifecycle and control commands. It creates named nexus devices, manages sharing and ANA state, lists nexus and child health, adds/removes children, resizes nexus devices, and delegates child state operations.

### Important APIs, Types, And Functions
`NexusArgs` wraps `NexusCommands` for create, destroy, shutdown, publish, unpublish, ANA state, add, remove, list, children, resize, and nested child commands. `NexusShareProtocol`, `ResvType`, and `NvmeAnaState` model CLI enums. `ResvType` converts to `NvmeReservation`. Helper functions map nexus, child, reason, and ANA enum values to strings.

### Control Flow
`nexus_create` treats an empty UUID string as "generate one", defaults name to UUID, requires children, maps reservation type, and sends `CreateNexusRequest` with controller IDs, reservation keys, and nexus-info key. Destroy sends a request then lists nexus for JSON output. List prints name, UUID, size, state, rebuild count, path, and optional child URIs. Children list filters by UUID or name and includes reason plus fault timestamp. Publish defaults to NVMf and propagates allowed hosts. Resize sends requested size and prints confirmation.

### State, Persistence, And Dependencies
All durable effects are remote nexus changes. The module depends on v1 nexus/common protobufs, `byte_unit`, `url`, `uuid`, tonic status, colored JSON, and the shared context. It integrates with replica backends, NVMf target export, rebuild state, and persistent NexusInfo keys.

### Risks And Test Signals
Many response fields and enum conversions use `unwrap`; missing nexus payloads or unknown enum values can panic. Destroy returns a list response in JSON mode rather than the destroy result. Tests should cover generated UUIDs, no-child validation, reservation mapping, publish defaults, allowed hosts, child reason/fault timestamp output, resize request sizing, and unknown/missing response fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/perf_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/perf_cli.rs

### Purpose
`perf_cli.rs` provides the v1 command-tree entry for process resource usage, but it still calls the legacy v0 RPC because no v1 equivalent exists.

### Important APIs, Types, And Functions
`PerfArgs` wraps `PerfCommands::Resource`. `get_resource_usage` is marked with a TODO noting the lack of a v1 RPC and uses `ctx.client.get_resource_usage`.

### Control Flow
The handler calls `get_resource_usage`, which sends v0 `Null {}` to the legacy client, prints JSON if requested, or builds a single table row from optional `usage` fields.

### State, Persistence, And Dependencies
The command is read-only and stores nothing locally. It depends on v0 performance protobufs from inside the v1 command tree, colored JSON, SNAFU, and table formatting.

### Risks And Test Signals
The v1 CLI remains coupled to v0 service availability for this command. As in v0, missing `usage` can lead to an empty table passed to `print_list`. Tests should cover legacy-client use, missing usage, output modes, and behavior if future v1 APIs replace this path.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/perf_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/pool_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/pool_cli.rs

### Purpose
This file implements the v1 storage-pool CLI. It supports create, import, destroy, export, expand, list, clear-errors, and probe operations with pool type and encryption options.

### Important APIs, Types, And Functions
`PoolArgs` wraps `PoolCommands`. Input structs model operation-specific names, UUIDs, disks, pool type, encryption keys, cipher, cluster size, and metadata expansion options. `Cipher` maps to v1 common cipher values, and `PoolType` maps to `Lvs` or `Lvm`. `build_encryption`, `build_import_encryption`, `list_pools`, `pool_state_to_str`, and `pool_status_to_str` are key helpers.

### Control Flow
Create/import build optional encryption payloads and send v1 requests. Destroy/export send name and optional UUID and print confirmation in default mode. Expand first lists a pool to capture previous capacity, errors if absent, calls `grow_pool_v2`, and prints old/new capacity. List calls `list_pools` with optional name/UUID/type filters. `list_pools` can format either one pool or a vector, computes usage percentages, metadata usage, disk capacity, encryption, alerts, and error counts. Clear-errors sends selected disks then reuses list formatting. Probe wraps an import request and optional import flag.

### State, Persistence, And Dependencies
Durable state is remote pool metadata and underlying disk state. Dependencies include v1 pool/common protobufs, `byte_unit`, `either`, colored JSON, tonic `Status`, `uuid`, and `TryFrom`. It integrates with disk discovery, replica allocation, encryption handling, and persistent pool metadata.

### Risks And Test Signals
Encryption key lengths are inconsistent between create (`len * 4`) and import (`len`) and should be verified against API expectations. `expand` filters by name and type but passes UUID only to grow, not to the initial list. JSON output for destroy/export/expand is silent. Tests should cover encryption payloads, pool type/cipher mapping, empty lists, alert/default handling, metadata info absence, expand not-found, clear-errors disk selection, and probe output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/pool_cli.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/replica_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/replica_cli.rs

### Purpose
This file implements v1 replica lifecycle, sharing, resizing, listing, and I/O statistics commands. It is the primary CLI for v1 replica resources.

### Important APIs, Types, And Functions
`ReplicaArgs` wraps create, destroy, list, share, unshare, resize, and stats. `CreateArgs` includes name, UUID, pool identifier, size, share protocol, thin provisioning, and allowed hosts. `ShareProtocol` maps `none`/`nvmf`; `ResizeArgs` parses a new size. `share_proto_to_str` formats protocol integers.

### Control Flow
Create sends `CreateReplicaRequest` with `pooluuid` populated from the CLI pool string and defaulted remaining fields. Destroy sends UUID and no pool selector. List fetches all replicas and prints pool/name/UUID/thin/share/size/capacity/allocation/URI/snapshot/clone/encryption data, unwrapping usage. Share sends a protocol but currently does not pass allowed hosts because the share args lack that field. Unshare sends UUID. Resize sends requested size. Stats calls the v1 stats service and prints per-replica I/O counters when nested stats exist.

### State, Persistence, And Dependencies
The module creates, deletes, exports, unexports, and resizes remote replica state. Dependencies include v1 replica/stats protobufs, `byte_unit`, `uuid`, colored JSON, and shared formatting. It integrates with pools, snapshots/clones, NVMf sharing, and stats collection.

### Risks And Test Signals
`usage.as_ref().unwrap()` can panic if the server omits usage. The CLI field `pool` is written to `pooluuid`, so name-vs-UUID semantics depend on server interpretation. JSON mode is silent for destroy/unshare. Tests should cover usage absence, encryption defaults, clone/snapshot fields, resize sizing, protocol mapping, stats filtering, and pool identifier behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/replica_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_cli.rs

### Purpose
`snapshot_cli.rs` implements v1 snapshot and clone management. It supports nexus-coordinated snapshot creation, per-replica snapshot creation, listing, destruction, clone creation, and clone listing.

### Important APIs, Types, And Functions
`SnapshotArgs` wraps `CreateForNexus`, `CreateForReplica`, `List`, `Destroy`, `CreateClone`, and `ListClone`. Input structs carry nexus/replica/snapshot UUIDs, snapshot names, entity and transaction IDs, pool selectors, and clone identifiers.

### Control Flow
`create_for_nexus` requires equal counts of replica UUIDs and snapshot UUIDs, zips them into descriptors, sends `NexusCreateSnapshotRequest`, and prints nexus plus per-replica status. `create_for_replica` sends a direct snapshot request and prints snapshot metadata. `list` filters by optional source and snapshot UUID. `destroy` builds a oneof pool selector from optional pool UUID or name. Clone commands create or list replicas derived from snapshots and print allocation and ancestry fields.

### State, Persistence, And Dependencies
The module creates and deletes remote snapshot metadata and clone replicas. Dependencies include v1 snapshot protobufs, `uuid`, colored JSON, SNAFU, and shared context. It integrates with replica and nexus data paths, snapshot metadata persistence, and clone allocation accounting.

### Risks And Test Signals
Several optional fields are unwrapped, including nexus response and clone usage. Timestamp defaults may hide missing metadata. The count-mismatch error uses `MissingValue`, which is semantically approximate. Tests should cover count validation, pool selector conflicts, optional usage absence, clone list empty behavior, JSON/default output, and server failures for invalid snapshot/replica IDs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_rebuild_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_rebuild_cli.rs

### Purpose
This file exposes v1 snapshot-rebuild operations: create/start, destroy, and list. It is a separate command group from normal child rebuilds and targets replica reconstruction from snapshot sources.

### Important APIs, Types, And Functions
`SnapshotRebuildArgs` wraps `Create`, `Destroy`, and `List`. `CreateArgs` carries replica UUID and snapshot URI. `UuidArgs` and `ListArgs` identify rebuilds. `rebuild_status_to_str` maps `RebuildStatus` to display strings.

### Control Flow
Create sends `CreateSnapshotRebuildRequest` using the replica UUID as both `replica_uuid` and `uuid`, with empty snapshot UUID and replica URI, the provided snapshot URI, and bitmap disabled. Destroy sends UUID and always prints a deletion message. List optionally filters by rebuild UUID and prints rebuild UUID, snapshot URI, status, total/rebuilt/remaining, and timestamps.

### State, Persistence, And Dependencies
The module creates and destroys remote snapshot rebuild jobs. It depends on v1 snapshot-rebuild protobufs, `uuid`, colored JSON, and SNAFU. It integrates with experimental snapshot rebuild support enabled in the io-engine binary.

### Risks And Test Signals
Create hardcodes several empty/default request fields, so it may only cover one narrow server path. Destroy ignores output mode and always prints. The table header labels the rebuild UUID column as `REPLICA`, which may confuse operators. Tests should cover create request construction, status mapping, optional timestamps, JSON/default modes, destroy output, and server-side validation of empty fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_rebuild_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/stats_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/stats_cli.rs

### Purpose
`stats_cli.rs` implements v1 I/O statistics commands for pools, nexus, replicas, plus a reset command. It provides formatted latency and byte counters.

### Important APIs, Types, And Functions
`StatsArgs` wraps `Pool`, `Nexus`, `Replica`, and `Reset`. `NameArgs` is an optional filter. `io_stats_row` formats a `v1rpc::stats::IoStats`, `adjust_bytes` converts bytes to binary units, and `ticks_to_time` converts SPDK ticks to microseconds using `tick_rate`.

### Control Flow
Each resource command calls the matching stats RPC with optional name, handles empty results with verbose messages, and prints a common table of operation counts, byte totals, average/aggregate latency ticks converted to time, and max/min latencies. Replica stats unwrap nested `stats` in each `ReplicaIoStats`. Reset sends `reset_io_stats(())` and prints completion.

### State, Persistence, And Dependencies
Read commands observe remote cumulative stats. Reset mutates remote counters. Dependencies include v1 stats protobufs, `byte_unit`, colored JSON, SNAFU, and shared context. It integrates with bdev/nexus/replica stats collection and SPDK tick-rate reporting.

### Risks And Test Signals
`ticks_to_time` divides by `tick_rate`; zero would panic. Replica nested stats are unwrapped. `adjust_bytes` always uses binary units and ignores global unit preference. Tests should cover zero tick rate, missing replica stats, empty named and unnamed results, reset behavior, JSON/default output, and latency conversion correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/stats_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/test_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/test_cli.rs

### Purpose
`test_cli.rs` exposes v1 testing and fault-injection utilities. It lists test features, adds/removes fault injections, and streams wipe progress for test-only resource wiping.

### Important APIs, Types, And Functions
`TestArgs` wraps `Features`, `Inject`, and `Wipe`. `Resource` currently supports `Replica`. `WipeMethod` maps to v1 wipe methods and checksum algorithm. `WipeArgs` carries resource UUID, optional pool selector, method, and optional chunk size. Helpers format bandwidth, checksum, and byte units.

### Control Flow
`features` calls `get_features`. `injections` lists injections when no add/remove arguments are present; otherwise it iterates add requests then remove requests. `replica_wipe` builds an optional pool oneof, wipe options, and chunk size, then consumes a server stream. JSON mode prints each streamed response. Default mode spawns a task to transform streamed responses into rows and passes an mpsc receiver to `Context::print_streamed_list`.

### State, Persistence, And Dependencies
The module mutates remote fault-injection state and can wipe replica data. It depends on v1 test protobufs, futures streams, `byte_unit`, `uuid`, strum derives, colored JSON, SNAFU, and Tokio channels. It integrates with test/fault-injection builds and destructive test workflows.

### Risks And Test Signals
Wipe is destructive; CLI validation only restricts resource enum and pool selector conflicts. The spawned streaming task unwraps channel sends, so consumer failure can panic. Bandwidth is blank for missing or non-normal elapsed durations. Tests should cover pool oneof construction, method mapping, chunked streaming, JSON streaming, injection add/remove/list, checksum formatting, and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/test_cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine.rs

### Purpose
`io-engine.rs` is the main io-engine data-plane binary. It initializes logging, environment, SPDK reactors, hugepage checks, feature toggles, persistent store, gRPC serving, registration, diagnostics, and process-level safety settings.

### Important APIs, Types, And Functions
Important functions are `start_tokio_runtime`, `hugepage_get_nr`, `hugepage_check`, and `main`. The `print_feature!` macro logs compile-time feature status. `PAGES_NEEDED` defines the hugepage threshold. The binary invokes `io_engine::CPS_INIT!()`.

### Control Flow
`main` parses `MayastorCliArgs`, initializes logging, configures `PR_SET_IO_FLUSHER`, optionally enables coredumps, handles diagnostics commands early, checks hugepages, logs io_uring and NVMe multipath support, initializes `MayastorEnvironment`, starts the Tokio side runtime, marks reactors running, and polls the primary reactor. `start_tokio_runtime` applies env-driven feature flags for partial rebuild, reset, LVM, snapshot rebuild, channel debug, RDMA, diskpool encryption, and blobstore unmap; initializes resource locks; optionally connects persistent store; spawns device and reactor monitors; runs the gRPC server; and optionally runs registration. A joined future failure raises `SIGUSR1`.

### State, Persistence, And Dependencies
The binary controls process-wide state: environment variables, global atomic feature flags, SPDK blobstore behavior, resource lock manager, persistent store connection, gRPC server state, registration, reactor state, and event generation. Dependencies include `io_engine` core modules, `events_api`, `futures`, `sysfs`, `signal_hook`, `spdk_rs`, logger, persistent store, and version info.

### Risks And Test Signals
Hugepage insufficiency exits only in non-debug builds. Some feature switches are environment variables, making behavior dependent on deployment environment. `ms.event(Start).generate()` occurs after reactor polling/fini, which is worth verifying against expected lifecycle semantics. Tests and validation should cover CLI parsing, diagnostics early exit, hugepage paths absent/present, env flag effects, persistent store retry settings, gRPC startup failures, registration failures, and internal abort exit.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/jsonrpc.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/jsonrpc.rs

### Purpose
This standalone binary is a raw SPDK JSON-RPC client over a Unix socket. It is retained as a low-level debugging tool even though typed gRPC commands cover most user workflows.

### Important APIs, Types, And Functions
`Opt` parses the socket path and subcommand. `Sub::Raw` carries a method and optional JSON argument string. The Tokio `main` calls `jsonrpc::call`.

### Control Flow
The binary parses CLI args, matches `raw`, parses the optional argument into `serde_json::Value` when present, calls the method with `Some(args)` or `None`, pretty-prints the returned JSON, and prints the result. If pretty-printing a returned value fails in the argument path, it debug-prints the value and returns an empty string.

### State, Persistence, And Dependencies
The binary stores no state. Its effects depend entirely on the JSON-RPC method invoked through the socket, defaulting to `/var/tmp/mayastor.sock`. Dependencies include clap, serde_json, the repository `jsonrpc` crate, Tokio, and version info.

### Risks And Test Signals
Raw methods can mutate SPDK state without typed validation. The code assumes argument strings are JSON and returns parse errors locally. Tests should cover no-arg and arg calls, invalid JSON, socket failures, method errors, and pretty-printed output stability.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/jsonrpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/nvmet.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/nvmet.rs

### Purpose
`nvmet.rs` is a test utility that starts a small io-engine environment, creates a fixed-name nexus over provided NVMe-oF target URIs, and shares it over NVMf. It is intended for manual or automated nexus behavior testing.

### Important APIs, Types, And Functions
The file defines a fixed `NEXUS` UUID/name, `Args` for size and URI list, `start_tokio_runtime`, `create_nexus`, and `main`. It uses `nexus_create`, `nexus_lookup_mut`, and the `Share` trait.

### Control Flow
`main` parses target URIs, builds default `MayastorCliArgs` with RPC address `0.0.0.0:10124` and reactor mask `0xF`, initializes logging and environment, starts a small Tokio runtime running the gRPC server, schedules `create_nexus` on the reactor, and polls. `create_nexus` converts MB to bytes, creates the nexus with the fixed name, looks it up, and shares it over NVMf.

### State, Persistence, And Dependencies
The utility mutates local SPDK/io-engine state by creating and sharing a nexus. It depends on reactor initialization, NVMf target support, provided remote NVMe targets, gRPC server startup, logger, and version info. It does not use persistent store or normal registration.

### Risks And Test Signals
The fixed nexus UUID can collide with an existing resource. Many operations unwrap and are expected to crash on setup failure. The header comments note limitations for rebuild tests. Validation should cover URI parsing, size conversion, gRPC availability, successful NVMf share URI, behavior on child connection failure, and fixed-name collision.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/nvmet.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/spdk.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/spdk.rs

### Purpose
`spdk.rs` is a minimal wrapper around `spdk_app_start` for testing SPDK with a given configuration when the full io-engine stack is unnecessary.

### Important APIs, Types, And Functions
The binary prepares C argv values, initializes `spdk_app_opts`, calls `spdk_app_parse_args`, sets app name and shutdown callback, and starts the SPDK app with `app_start_cb`. `spdk_shutdown_cb` unregisters optional delay support and stops the SPDK app.

### Control Flow
`main` converts Rust args to `CString`, builds a null-terminated C argv array, initializes SPDK options, lets SPDK parse standard app args, installs shutdown callback, starts the app, finalizes SPDK, and returns an I/O error on nonzero status. `app_start_cb` registers artificial delay support when `MAYASTOR_DELAY` is set.

### State, Persistence, And Dependencies
The binary owns a standalone SPDK app lifecycle and any SPDK resources configured by arguments. It depends on `spdk_rs::libspdk`, libc-compatible argument handling, and the repository `delay` module. It stores no repository state.

### Risks And Test Signals
The app name CString is leaked into SPDK with `into_raw`, appropriate for process lifetime but notable. Argument parsing and callbacks are unsafe FFI boundaries. Tests should cover SPDK argument parsing failures, successful start/stop, `MAYASTOR_DELAY` behavior, shutdown callback cleanup, and nonzero SPDK return codes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/spdk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/uring-support.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/uring-support.rs

### Purpose
`uring-support.rs` is a tiny diagnostic binary that exits according to kernel io_uring support. It is useful for scripts and deployment checks.

### Important APIs, Types, And Functions
`Args` is an empty clap parser used for standard help/version output. `main` calls `io_engine::bdev::util::uring::kernel_support`.

### Control Flow
The binary parses arguments, checks kernel support, and exits with code `0` when supported and `1` when not supported by casting `!supported` to `i32`.

### State, Persistence, And Dependencies
There is no state or persistence. Dependencies are clap, version info, and the io-engine uring utility.

### Risks And Test Signals
The behavior is encoded solely in exit status, not stdout. Tests should cover supported and unsupported mocked paths, help/version parsing, and shell-script interpretation of the exit code.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/uring-support.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/constants.rs -->
## sources/control-plane/mayastor/io-engine/src/constants.rs

### Purpose
`constants.rs` centralizes small string constants used across io-engine for driver names, NVMe identity, NQN construction, eventing trace filters, and service identity.

### Important APIs, Types, And Functions
The file exports `NEXUS_CAS_DRIVER`, `NVME_CONTROLLER_MODEL_ID`, `NVME_NQN_PREFIX`, `EVENTING_TARGET`, and `SERVICE_NAME`.

### Control Flow
There is no runtime control flow. These constants are compiled into callers that need stable string identifiers.

### State, Persistence, And Dependencies
The file has no dependencies and no mutable state. The constants participate in integration with NVMe initiators/targets, eventing, and external component naming.

### Risks And Test Signals
Changing these strings can break compatibility with persisted metadata, event consumers, NQN conventions, or controller identity expectations. Tests should assert generated NQNs/model IDs and event source names where external contracts depend on them.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/bdev.rs -->
## sources/control-plane/mayastor/io-engine/src/core/bdev.rs

### Purpose
`core/bdev.rs` wraps `spdk_rs::Bdev` in io-engine core types. It provides lookup/open/stat/share/unshare behavior, bdev iteration, display/debug formatting, and a `BdevStater` abstraction for I/O statistics.

### Important APIs, Types, And Functions
`Bdev<T>` is a newtype over `spdk_rs::Bdev<T>`, with `UntypedBdev` as `Bdev<()>`. Key methods include `checked_from_ptr`, `open_by_name`, `open`, `lookup_by_name`, `get_by_name`, `lookup_by_uuid_str`, `driver`, `bdev_first`, `get_tick_rate`, `stats_async`, `stats_errors_async`, and stats reset functions. The file implements the `Share` trait for `Bdev<T>`, defines `is_shared`, `BdevIter`, `BdevStater`, `BdevErrorStats`, and `BdevStats`.

### Control Flow
Lookup methods wrap SPDK global bdev lookup and iteration. Opening creates a `BdevDesc` with `bdev_event_callback` and wraps it in `DescriptorGuard`. Stats methods await SPDK async stats and convert them to core structs, using `spdk_get_ticks_hz` for tick rate. Sharing builds an `NvmfSubsystem` from the bdev, applies PTPL path, controller ID range, ANA reporting, host access policy, and allowed hosts, then starts the subsystem. Updating share properties adjusts allowed-host state for existing NVMf subsystems. Unshare stops the NVMf subsystem if present. URI helpers recover original bdev URIs from aliases and append UUID when missing.

### State, Persistence, And Dependencies
The wrapper holds SPDK bdev handles but does not own bdev lifetime. It changes NVMf subsystem state during share/unshare and reads bdev aliases, stats, claims, and module names. Dependencies include `spdk_rs`, `nix::errno`, `async_trait`, `snafu`, `NvmfSubsystem`, NVMf target URI helpers, share property types, and bdev URI comparison.

### Risks And Test Signals
`checked_from_ptr` relies on unsafe pointer wrapping. `stats_errors_async` expects error stats to be present after requesting them. `shared` returns `Some(Off)` instead of `None` for unshared bdevs, so callers must handle both. NVMf sharing depends on global subsystem lookup by bdev name. Tests should cover lookup/open failures, descriptor guard drop behavior through callers, share/unshare allowed-host updates, URI alias matching, stats conversion, error-count filtering, and iteration over global bdevs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/block_device.rs -->
## sources/control-plane/mayastor/io-engine/src/core/block_device.rs

### Purpose
`block_device.rs` defines the core block-device abstraction traits and shared I/O statistics types. It is a boundary between high-level nexus/replica code and concrete SPDK-backed devices.

### Important APIs, Types, And Functions
`BlockDeviceIoStats` is a mergeable counter/latency struct. `BlockDeviceIoErrorStats` aliases SPDK error stats. `BlockDevice` describes device metadata, open, stats, I/O controller, and event-listener operations. `BlockDeviceDescriptor` models an opened descriptor. `BlockDeviceHandle` defines DMA allocation, read/write/compare/reset/unmap/write-zeroes/flush, NVMe admin and reservation operations, snapshot creation, passthrough, host ID, and controller-failure checks. `ReadOptions`, callback type aliases, `DeviceTimeoutAction`, and `DeviceIoController` complete the API.

### Control Flow
The trait supplies async convenience wrappers around callback-style I/O methods. Each wrapper creates a oneshot channel, submits the callback operation with `block_device_io_completion`, awaits completion, and converts non-success status into the corresponding `CoreError` with offset and length context. Default NVMe reservation and passthrough methods return not-supported errors unless an implementation overrides them.

### State, Persistence, And Dependencies
This file stores no concrete state but defines how implementations expose state. `BlockDeviceIoStats` uses saturating merge strategies, allowing aggregation. Dependencies include `spdk_rs` DMA buffers and I/O vectors, futures oneshot channels, `nix::errno`, `uuid`, `merge`, and core error/status types.

### Risks And Test Signals
The async wrappers `expect` successful oneshot receipt; dropped callbacks panic. Caller comments require I/O vector lengths to match block counts but the trait cannot enforce it. `ticks_to_time` users elsewhere depend on nonzero tick rate from stats. Tests should cover success and failure completion mapping for read/write/compare, callback drop behavior, unsupported NVMe default methods, merge saturation, and implementation conformance for block sizing and alignment.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/block_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/descriptor.rs -->
## sources/control-plane/mayastor/io-engine/src/core/descriptor.rs

### Purpose
`descriptor.rs` provides `DescriptorGuard`, an RAII wrapper around `spdk_rs::BdevDesc`. It centralizes descriptor close behavior, nexus-module claim/unclaim operations, and conversion from descriptor to I/O handle.

### Important APIs, Types, And Functions
`DescriptorGuard<T>` stores a `BdevDesc<T>` and the owning SPDK `Thread`. `UntypedDescriptorGuard` is `DescriptorGuard<()>`. Methods include `new`, `claim`, `unclaim`, `bdev`, and `into_handle`. It implements `Deref`, `Drop`, `Debug`, and an unsafe `Sync` implementation.

### Control Flow
`new` captures the current SPDK thread. `claim` finds the nexus bdev module and calls `claim_bdev`; `unclaim` releases the bdev through the same module. `bdev` returns a `Bdev<T>` wrapper around the descriptor's bdev. `into_handle` consumes the guard and delegates to `BdevHandle::try_from`. On drop, the descriptor is closed on the captured thread when available, directly on the primary thread when already there, or by sending a close message to the primary thread otherwise.

### State, Persistence, And Dependencies
The guard owns an open SPDK descriptor and optionally records its thread affinity. It changes SPDK bdev claim state through the nexus module and closes descriptors asynchronously across threads. Dependencies include `spdk_rs::{BdevDesc, BdevModule, Thread}`, `NEXUS_MODULE_NAME`, `Bdev`, `BdevHandle`, and `CoreError`.

### Risks And Test Signals
Correct close-thread routing is critical; closing on the wrong reactor thread can violate SPDK assumptions. `Sync` safety relies on only shared read access except `Drop`. Claim/unclaim logs errors and returns bool/void rather than rich errors. Tests should cover drop on owning, primary, and non-primary threads; claim failure; unclaim failure; debug formatting; and handle conversion preserving descriptor ownership.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/descriptor.rs -->
