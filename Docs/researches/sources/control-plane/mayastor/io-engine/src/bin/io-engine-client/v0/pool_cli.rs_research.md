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
