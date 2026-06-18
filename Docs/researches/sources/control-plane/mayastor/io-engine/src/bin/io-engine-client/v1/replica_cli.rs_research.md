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
