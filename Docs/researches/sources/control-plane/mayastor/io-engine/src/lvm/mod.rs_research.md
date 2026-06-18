# sources/control-plane/mayastor/io-engine/src/lvm/mod.rs

## Purpose
This module is the public integration layer for the LVM backend. It documents LVM concepts, wires internal modules, exports pool/replica types, provides reactor bridging helpers, and implements io-engine pool and replica backend traits for LVM.

## Important APIs, types, and functions
The module re-exports `VolumeGroup`, `LogicalVolume`, `QueryArgs`, `CmnQueryArgs`, and `Error`. `is_alphanumeric` validates query values allowed in LVM `--select` expressions. `tokio_submit`, `spdk_run!`, and `tokio_run!` bridge work between SPDK reactor context and tokio process execution.

Trait implementations include `PoolOps` and `IPoolProps` for `VolumeGroup`, `ReplicaOps`, `SnapshotOps`, and `BdevStater` for `LogicalVolume`, plus `PoolLvmFactory` and `ReplLvmFactory` implementing backend factory interfaces.

## Control flow
Pool create/import/list/find calls route to `VolumeGroup` methods when the LVM feature is enabled. Replica list/find routes to `LogicalVolume::lookup/list` with Mayastor tag filters. Replica operations delegate share/unshare/update/resize/destroy to `lv_replica`. Snapshot and clone methods return unsupported or empty lists because LVM snapshots are not implemented for this backend.

## State and persistence behavior
This file does not persist directly, but it decides which persistent LVM-tagged pools and replicas are visible to the generic backend layer. Factory methods filter by feature flags and requested `PoolBackend`. Stats and grow/reset are currently unsupported for LVM.

## Dependencies and integration points
It depends on core logical-volume/share/stats traits, pool and replica backend traits, LVM property types, and futures oneshot channels. It is the main adapter consumed by control-plane APIs that operate generically over pool backends.

## Risks and test signals
Feature-gate checks must stay consistent across find/list paths; `ReplLvmFactory::find` does not check the LVM feature flag while list does. Snapshot methods intentionally return unsupported/empty behavior, which callers must handle. `FindPoolArgs::UuidOrName` currently treats the value as uuid only. Tests should exercise backend filtering, feature disabled behavior, pool/replica trait conversions, unsupported operations, and reactor tokio bridge errors.
