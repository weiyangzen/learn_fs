# File Research: sources/block-storage/stratisd/src/engine/types/actions.rs

## Purpose

Defines idempotent action result types used across the Stratis engine, pool, filesystem, blockdev, encryption, key, and property APIs. The file centralizes the contract that an operation can succeed while either changing state or proving the requested state was already true.

## Main Types and Behavior

- `EngineAction` is the shared trait for action results. It exposes `is_changed()` and consuming `changed()` so callers can decide whether an operation had an externally reportable effect.
- `CreateAction<T>` represents single-object creation as `Created(T)` or `Identity`.
- `MappingCreateAction<T>` adds `ValueChanged(T)` for key-value stores where the key may exist but the value changes.
- `MappingDeleteAction<T>` and `DeleteAction<T>` represent idempotent removals.
- `SetUnlockAction<T>`, `SetCreateAction<T>`, and `SetDeleteAction<T, U>` model multi-item changes and return vectors only when non-empty.
- `RenameAction<T>` distinguishes `Identity`, `Renamed(T)`, and `NoSource`.
- `StartAction<T>`, `StopAction<T>`, and `GrowAction<T>` model lifecycle and resize outcomes.
- `PropChangeAction<T>` represents property update idempotency, with `ToDisplay` helpers for optional and boolean values.
- Marker structs `Key`, `Clevis`, `EncryptedDevice`, `ReencryptedDevice`, and `RegenAction` provide typed return payloads and user-facing formatting for encryption/key operations.

## Integration Points

The JSON-RPC server and engine code use `EngineAction::is_changed()` heavily to convert engine results into boolean IPC status values. Display implementations provide CLI/API messages for pool creation/deletion, filesystem/snapshot creation, device add/grow, pool start/stop, encryption/decryption, keyring/Clevis binding, and property changes.

## Notable Semantics

`SetUnlockAction::Started(Vec<T>)` can mean the pool started even when no individual devices are newly reported; in that case `is_changed()` is false if the vector is empty. `StopAction::is_changed()` only returns true for `Stopped(_)`, not `CleanedUp(_)` or `Partial(_)`, which is a subtle contract for callers interpreting stop results.
