# sources/control-plane/mayastor/io-engine/src/core/logical_volume.rs

## Purpose
Defines the backend-neutral logical volume interface used by replicas, LVM volumes, and event/reporting code.

## Important APIs, Types, and Functions
- `LogicalVolume` trait exposes identity, pool identity, entity ID, provisioning/read-only flags, size/accounting, backend type, snapshot/clone role, parent snapshot, share protocol/URI, allowed hosts, and encryption.
- `LvolSpaceUsage` carries capacity, allocated bytes, cluster size/counts, snapshot allocation, and optional clone-derived snapshot allocation.

## Control Flow and State
This file declares contracts only. Implementors supply state from backend-specific volume metadata. Consumers can treat LVS and LVM-style volumes uniformly for listing, event metadata, and share state.

There is no state or persistence in this file, but fields map directly to persisted backend metadata and runtime share configuration.

## Dependencies and Integration Points
Depends on `Protocol` and `PoolBackend`. Implemented by LVS `Lvol` and LVM volume types, and consumed by eventing, replica APIs, and gRPC response builders.

## Risks and Test Signals
The trait returns many owned `String` values, so repeated reporting can allocate heavily. Semantics such as `allocated`, `committed`, and snapshot allocation must be consistent across backends. Tests should compare LVS and LVM implementations for identical API semantics, especially snapshot/clone flags and share metadata.
