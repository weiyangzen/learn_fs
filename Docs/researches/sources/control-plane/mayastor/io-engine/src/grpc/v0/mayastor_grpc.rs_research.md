# sources/control-plane/mayastor/io-engine/src/grpc/v0/mayastor_grpc.rs

Purpose: this is the large v0 Mayastor service implementation for legacy provisioning, nexus, replica, snapshot, host, resource, and NVMe-controller RPCs. It maps older protobuf contracts onto current lvs, nexus, bdev, rebuild, and host modules.

Important APIs/types/functions: `MayastorSvc` owns a service lock and timeout-aware `serialized` helper for per-nexus/global resource locking. Conversion impls map `LvsError`, `Protocol`, `Lvs`, `Lvol`, space usage, rebuild stats, features, block devices, resource usage, NVMe controllers, and reservation options into v0 types. RPC methods cover pool create/destroy/list, replica create/list/share/destroy/stats, nexus create/destroy/shutdown/list/child operations/publish/ANA/rebuild/history, snapshot creation, block-device listing, resource usage, controller list/stats, and version/features.

Control flow: simple pool/replica paths use `self.locked` plus `rpc_submit`; nexus paths use `serialized`, which spawns a Tokio task, optionally grabs the global lock, then grabs the protected nexus resource lock before submitting reactor work. Pool creation is idempotent for existing LVS pools and exports captured `PoolConfig`; pool destruction removes config before destroying. Replica create handles idempotent existing bdevs, validates share protocol, creates lvols, and destroys newly-created lvols if sharing fails.

State and persistence: mutates LVS pools/lvols, NVMf exports, nexus structures, rebuild jobs, snapshots, and SPDK controllers. It persists pool config on create/destroy and creates PTPL files for shared replicas. Snapshot requests generate timestamps and UUIDs.

Dependencies and integration points: integrates `io_engine_api::v0`, `Lvs/Lvol`, `PoolConfig`, `nexus_grpc` helpers, `ResourceLockManager`, `controller_grpc`, host block-device/resource modules, rebuild state, and version info.

Risks: legacy idempotency is uneven; some list/stat paths unwrap lvol conversion; v0 names sometimes strip or add `nexus-`; share failures trigger best-effort cleanup; config export before destroy can diverge if destroy fails. Test signals should include pool config persistence, replica share rollback, per-nexus lock contention, invalid reservation/preemption inputs, PTPL cleanup, and v0/v2 nexus naming compatibility.
