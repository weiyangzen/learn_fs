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
