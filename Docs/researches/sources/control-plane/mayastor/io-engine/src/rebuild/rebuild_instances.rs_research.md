# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_instances.rs

## Purpose
This file provides the `gen_rebuild_instances!` macro, which gives rebuild job types a static in-process registry keyed by job name.

## Important APIs, Types, And Functions
The macro creates a `RebuildJobInstances` map and methods `count`, `remove`, `store`, `lookup`, and `lookup_src` for the target type. `get_instances` initializes a `OnceCell<Mutex<HashMap<String, Arc<T>>>>` and asserts it runs on an SPDK thread.

## Control Flow
Each rebuild type invokes the macro. `store` rejects duplicate names with `JobAlreadyExists`, wraps the job in `Arc`, and inserts it. Lookup and removal return cloned or removed arcs. `lookup_src` filters values by `src_uri`.

## State, Persistence, And Dependencies
State is process-local static memory per macro invocation/type. It depends on `once_cell`, `parking_lot`, `HashMap`, `Arc`, SPDK thread checks, and the rebuild error type.

## Integration Points
`BdevRebuildJob`, `NexusRebuildJob`, and `SnapshotRebuildJob` use this macro to expose job discovery and lifecycle functions to control-plane code.

## Risks
The registry is per type, so the same key can exist in different rebuild classes. The SPDK-thread assertion will panic if called from an arbitrary async runtime thread. Jobs remain alive until explicitly removed, so failed cleanup leaks registry entries.

## Test Signals
Coverage should verify duplicate rejection, removal of absent jobs, lookup by name and source URI, type isolation, and panic behavior or caller discipline for non-SPDK-thread access.
