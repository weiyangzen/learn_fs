# sources/control-plane/mayastor/io-engine/src/pool_backend.rs

## Purpose
This file defines the backend-neutral pool contract used by io-engine. It models pool creation arguments, metadata, backend selection, pool operations, error mapping, and the factory that probes enabled backends.

## Important APIs, Types, And Functions
`PoolArgs`, `PoolMetadataArgs`, `ReplicaArgs`, `ListPoolArgs`, and `FindPoolArgs` are request models. `PoolBackend` selects `Lvs` or `Lvm` and can be parsed/serialized. `GenericError` and `Error` convert backend failures to errno and tonic status. `PoolOps` defines create replica, destroy, export, grow, and reset errors. `IPoolFactory` is implemented by concrete backends. `PoolFactory::all_backends`, `backends`, `factories`, `new`, and `find` select and probe backends.

## Control Flow
Callers construct pool or list/find args, then either create a concrete factory or ask `PoolFactory::find` to probe every enabled backend. `PoolFactory::backends` filters all backends through `PoolBackend::enabled`. `find` returns the first backend that yields a pool, preserves the last backend error, and returns `NotFound` if none match and no backend returned a richer error.

## State, Persistence, And Dependencies
This file owns no runtime state. It defines contracts for state held by backend implementations. It depends on core bdev stats traits, encryption keys, logical volume types, `snafu`, `nix::errno`, tonic status conversion, and the concrete LVS/LVM factories.

## Integration Points
RPC layers use these traits to remain backend-neutral. LVS and LVM modules implement the factory and operation traits. Replica creation flows pass `ReplicaArgs` into `PoolOps::create_repl`, while metrics layers use `IPoolProps` and `BdevStater`.

## Risks
Factory probing can mask earlier backend errors if a later backend also errors. Backend enablement is dynamic, so feature or runtime configuration can change visible backends. `FindPoolArgs::uuid_or_name` is a compatibility path that can make name/uuid ambiguity observable.

## Test Signals
Coverage should verify backend filtering, `PoolFactory::find` with uuid/name/name+uuid, error-to-tonic and error-to-errno mapping, `ReplicaArgs` builder flags, encryption argument propagation, and behavior when one backend is disabled or errors.
