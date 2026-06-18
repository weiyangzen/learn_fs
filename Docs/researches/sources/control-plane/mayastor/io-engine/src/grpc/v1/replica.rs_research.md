# sources/control-plane/mayastor/io-engine/src/grpc/v1/replica.rs

Purpose: this v1 service implements backend-neutral replica create/destroy/list/share/unshare/resize/entity-id APIs and provides common replica wrappers used by snapshot and test services.

Important APIs/types/functions: `ReplicaService` implements `RWSerializer`/`RWLock`. `GrpcReplicaFactory` lists/finds replicas across backends and maps missing pools to `failed_precondition`. `ReplicaGrpc` wraps `ReplicaOps` and provides `wiper`, `destroy`, `share`, `unshare`, `resize`, `set_entity_id`, and `verify_pool`. Conversion impls map `ReplicaOps` and `LvolSpaceUsage` into v1 protobufs. `filter_replicas_by_replica_type` filters regular replicas, snapshots, and clones.

Control flow: `create_replica` validates protocol, finds the target pool by UUID/name, then delegates to `PoolGrpc::create_replica`. Destroy optionally validates the supplied pool before deleting and tags not-found with `gtm-602` metadata. List builds backend filters from requested pool types and suppresses per-backend list errors. Share/unshare take the pool resource lock, update allowed hosts if already shared, and require NVMf for new shares.

State and persistence: mutates replica lvol/backend state, NVMf sharing, PTPL files via `create_ptpl`, size, and entity id. Wiper setup opens bdev descriptors for destructive test operations but actual wiping is in test service.

Dependencies and integration points: integrates `replica_backend`, `pool_backend`, `GrpcPoolFactory`, `ResourceLockManager`, core bdev/wiper/share traits, and v1 pool/replica protobufs.

Risks: list ignores backend errors; resize has a TODO about missing pool lock; share rejects `Off` while unshare is separate; pool verification uses both name and UUID and returns `aborted` for compatibility. Test signals should cover backend filtering, pool mismatch, NVMf idempotent share property updates, PTPL creation failure, resize semantics, not-found metadata, and snapshot/clone query filtering.
