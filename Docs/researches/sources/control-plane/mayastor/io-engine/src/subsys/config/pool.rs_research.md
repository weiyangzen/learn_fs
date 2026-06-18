# sources/control-plane/mayastor/io-engine/src/subsys/config/pool.rs

## Purpose
This file manages a separate YAML pool configuration used to import/recreate pools at startup and export current pool topology.

## Important APIs, Types, And Functions
`PoolConfig::load`, `export`, `delete`, `capture`, `create_pools`, and `import_pools` are the main API. Internal `Pool` converts to `PoolArgs` and from `LvsBdev`. `ShareType` and `Replica` are serialized models, though replica data is informational/skipped. `create_pool` submits LVS creation/import through `rpc_submit`.

## Control Flow
`load` records the config file path and deserializes YAML or returns default for empty/missing files. `import_pools` asserts it runs on the first core and blocks on `create_pools`, which iterates configured pools and calls `create_pool`. `capture` enumerates current `LvsBdev`s into pool records. `export` serializes the config on a blocking task under a mutex, then signals completion back on the primary reactor.

## State, Persistence, And Dependencies
Persistent state is YAML at the configured path. Process state includes `CONFIG_FILE` and a static mutex used to serialize export writes. Dependencies include LVS pool creation, `LvsBdev` iteration, Mayastor reactors/runtime, gRPC `rpc_submit`, tonic status, and serde YAML.

## Integration Points
Startup pool import and runtime pool export use this module. It converts pool records into `PoolArgs` for the LVS backend; encrypted pools get a generated crypto vbdev name.

## Risks
Missing config files are treated the same as empty files. Export writes are not atomic. `Pool::from(LvsBdev)` currently sets `encrypted: false` with an explicit TODO. Replica entries are skipped on serialization and not recreated. `create_pool` requires at least one disk and always uses `Lvs::create_or_import`.

## Test Signals
Test load of empty/missing/valid/invalid YAML, import failure counting, export serialization and mutex behavior, capture from LVS bdevs, encrypted pool arg conversion, delete behavior, and first-core assertion for import.
