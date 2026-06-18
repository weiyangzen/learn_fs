# sources/control-plane/mayastor/io-engine/src/grpc/v1/pool.rs

Purpose: this v1 service implements backend-neutral pool creation, import, listing, export, destroy, grow, error clearing, and disk probing. It abstracts LVS and optional LVM backends behind `PoolFactory`/`PoolOps`.

Important APIs/types/functions: `PoolService` implements `RWSerializer`/`RWLock`; `PoolEncryptionParams` and `util_fetch_secret_params` handle inline or secret-backed encryption keys; `PoolGrpc` wraps a `PoolOps` with a held resource lock; `PoolErrorsNt` builds alert status from bdev error stats and IO-stall state; `pool_to_proto` and `AsyncFrom` map pools to protobuf; `GrpcPoolFactory` selects/list/finds backend factories. `PoolRpc` methods include create/destroy/export/import/list/grow_v2/clear_errors/probe.

Control flow: create/import fetch encryption data before taking the service lock, validate pool type and UUID, take subsystem/resource locks by pool name, ensure no backend already owns the requested pool, then call backend create/import via `spdk_submit!`. Finder locates a pool and locks its name. Listing iterates factories and logs per-backend list failures. Probe parses disk URIs and invokes per-URI probe with import options, collecting structured errors.

State and persistence: mutates pool backend state, may create encrypted crypto vbdev metadata, exports/destroys/imports pools, grows pools, clears error counters, and reads cached `pool_information` state for alert generation.

Dependencies and integration points: integrates `pool_backend`, `secret_provider`, `ResourceLockManager`, encryption types, bdev URI probing, `MayastorEnvironment`, and v1 pool/common protobufs.

Risks: secret retrieval happens outside the service lock and may expose latency; pool locks are by name with TODOs for UUID/disk-content collision; list suppresses backend errors; alert state depends on cached pool info; deprecated `grow_pool` always returns unimplemented. Test signals should cover encryption validation/secret keys, backend feature gating, cross-backend duplicate detection, lock contention, pool alert thresholds, probe error aggregation, and LVM disabled behavior.
