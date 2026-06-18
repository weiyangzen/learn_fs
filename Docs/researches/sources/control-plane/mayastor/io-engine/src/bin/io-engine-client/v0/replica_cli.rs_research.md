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
