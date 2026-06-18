<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/replica.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/replica.rs

Purpose: v1 gRPC test builder for replica lifecycle, sharing, resizing, lookup, and data consistency validation.

Important APIs/types: `ReplicaBuilder` stores RPC handle, pool UUID, name, UUID, optional bdev URI, size, thin flag, share protocol, shared URI, and serial. Fluent setters configure name/uuid/pool/size/thin/NVMf. Accessors build NQN, bdev URI, NVMf location, serial, and shared URI. Async methods create, destroy, share, resize, and get a replica. Free functions list replicas, find by UUID, and validate multiple replicas by reading through NVMf.

Control flow: create/share/resize/destroy lock the shared v1 RPC handle and call generated replica client methods. Sharing records returned URI into the builder for later nexus-child use.

State and dependencies: mutates replica service state and remote NVMf sharing state. Depends on pool builders, `io_engine_api`, NVMf helpers, and UUID-derived serial generation.

Risks and test signals: missing fields panic through `expect`/`unwrap`. `destroy` can pass either a pool UUID selector or none. Healthy tests create, share, locate by UUID, then validate data across replicas.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/replica.rs -->
