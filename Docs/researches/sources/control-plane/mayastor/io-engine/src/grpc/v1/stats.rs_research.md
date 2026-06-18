# sources/control-plane/mayastor/io-engine/src/grpc/v1/stats.rs

Purpose: this v1 service reports and resets pool, nexus, and replica I/O statistics while coordinating with pool/replica/nexus locks to avoid concurrent mutation races.

Important APIs/types/functions: `StatsService` stores its own lock plus cloned `PoolService` and `ReplicaService`. It implements `Serializer::locked` for reset operations that take stats write lock, pool/replica read locks, and global resource lock. Helper methods `shared` and `nexus_lock` coordinate read paths. RPCs are `get_pool_io_stats`, `get_nexus_io_stats`, `get_replica_io_stats`, and `reset_io_stats`. Conversion impls map `BdevStats` to `IoStats` and `ReplicaBdevStats` to `ReplicaIoStats`.

Control flow: pool and replica stats take stats read lock plus the corresponding service read lock, list matching backend objects, issue concurrent `stats()` futures via `join_all`, and collect errors. Nexus stats take stats read lock plus global lock, optionally selecting one nexus by name. Reset takes stronger locks and submits a reactor future that iterates every bdev and resets counters.

State and persistence: read calls do not persist; reset mutates in-memory/SPDK bdev I/O counters for all bdevs. Statistics include latency ticks and tick rate.

Dependencies and integration points: integrates `ResourceLockManager`, `GrpcPoolFactory`, `GrpcReplicaFactory`, `nexus`, `UntypedBdev`, `BdevStater`, and v1 stats protobufs.

Risks: pool/replica listing suppresses backend list errors with `unwrap_or_default`, but later stat errors fail the whole response; reset affects all bdevs, not only Mayastor-owned objects; panic logging loses request args in some shared paths. Test signals should cover lock ordering/deadlock, partial stat failures, named and all-object stats, reset side effects, and conversion of latency fields.
