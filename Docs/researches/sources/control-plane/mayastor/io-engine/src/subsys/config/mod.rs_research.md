# sources/control-plane/mayastor/io-engine/src/subsys/config/mod.rs

## Purpose
This file implements the Mayastor configuration subsystem. It loads partial YAML config, applies SPDK option groups before use, exports current configuration via JSON-RPC/SPDK config JSON, and persists refreshed config back to disk.

## Important APIs, Types, And Functions
`ConfigSubsystem` builds an SPDK subsystem with init/fini/config callbacks. `EalOpts` and `Config` are serde models. `CONFIG` is the global `OnceCell<Config>`. `Config::get_or_init`, `get`, `read`, `refresh`, `write`, and `apply` are the core API. The subsystem init registers `mayastor_config_export`.

## Control Flow
Startup initializes `CONFIG` from defaults or `Config::read`. `Config::apply` applies NVMe bdev, generic bdev, posix socket, and iobuf options, while NVMf target config is used later during target creation. During SPDK subsystem init, JSON-RPC export is registered and subsystem initialization advances. The export RPC refreshes current settings, then writes back to the original source file if present.

## State, Persistence, And Dependencies
Config state is a process-global immutable `Config`; refreshed exports query live SPDK options. Persistence is YAML on disk at `source`. Dependencies include serde YAML/JSON, SPDK subsystem and JSON callbacks, JSON-RPC registration, and option structs from `opts.rs`.

## Integration Points
`subsys/mod.rs` registers this subsystem before NVMf. NVMf target setup reads `Config::get().nvmf_tgt_conf` and `nexus_opts`. Runtime tooling can call `mayastor_config_export` to save current config.

## Risks
`Config::get` unwraps and will panic if called before initialization. `apply` asserts option setters succeed, turning configuration failures into panics. The source file is overwritten on export without atomic temp-file handling. The config callback serializes to JSON raw output and silently returns on serialization error.

## Test Signals
Test empty and partial YAML reads, unknown-field rejection, source preservation, live refresh after applying options, write failures, export RPC with and without source, and startup ordering that prevents `Config::get` panics.
