# File Research: sources/block-storage/stratisd/src/engine/types/mod.rs

## Purpose

Acts as the public type hub for engine-wide Stratis identifiers, action result types, diff types, encryption/key types, udev event wrappers, pool discovery records, and integrity configuration.

## Main Types and Behavior

- Re-exports action, diff, key, engine state, lockable, and error/result types.
- Defines typed UUID wrappers with the `uuid!` macro: `DevUuid`, `FilesystemUuid`, and `PoolUuid`.
- `StratisUuid` unifies device, filesystem, and pool UUIDs behind `Deref<Target = Uuid>` and `Display`.
- `Name` wraps pool/filesystem names and supports string borrowing, display, hashing, and serde.
- `ReportType` currently exposes `StoppedPools`.
- `PoolDevice`, `LockedPoolInfo`, `LockedPoolsInfo`, `StoppedPoolInfo`, `StoppedPoolsInfo`, and `Features` represent discovered locked/stopped pool state.
- `UdevEngineEvent` and `UdevEngineDevice` snapshot libudev event/device data into sendable engine-owned structures.
- `DevicePath` canonicalizes and wraps a device path.
- `ActionAvailability` models increasingly restrictive pool action states.
- `MaybeInconsistent<T>` represents metadata disagreement across devices.
- `PoolIdentifier<U>` supports name-or-UUID lookup and display.
- `UuidOrConflict` handles ambiguous name-to-UUID mappings.
- `StratSigblockVersion` validates V1/V2 metadata versions.
- `IntegrityTagSpec`, `IntegritySpec`, and `ValidatedIntegritySpec` define and validate dm-integrity metadata defaults.

## Integration Points

This module is imported widely by engine, JSON-RPC, D-Bus, and daemon runtime code. It is the type-level contract between Stratis engine internals and IPC layers.

## Notable Semantics

`UuidOrConflict` maintains an invariant that conflict sets have more than one UUID and collapses back to a single UUID when removals leave one member. `ValidatedIntegritySpec` enforces 4096-byte journal-size alignment and fills defaults for tag spec, block size, and superblock allocation.
