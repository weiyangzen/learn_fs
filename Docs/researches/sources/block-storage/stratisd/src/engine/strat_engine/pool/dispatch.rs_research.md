# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/dispatch.rs

## Purpose

`dispatch.rs` defines `AnyPool`, an enum wrapper that erases whether a pool is backed by the v1 or v2 implementation while still implementing the common `Pool` trait.

## Key Type

- `AnyPool`
  - `V1(Box<v1::StratPool>)`
  - `V2(Box<v2::StratPool>)`

## Main Responsibilities

- Forward every `Pool` trait method to the matching v1 or v2 pool.
- Preserve a single engine-facing pool type while allowing metadata-version-specific implementations.
- Normalize trait object returns for filesystems and block devices.

## Forwarded Behavior

The implementation delegates:

- Cache initialization and blockdev addition/growth.
- Filesystem creation, deletion, rename, snapshot, size limits, and merge scheduling.
- Encryption binding, rebinding, unbinding, pool encryption, reencryption, decryption, token slots, and volume-key loading.
- Pool metadata queries.
- Pool size, allocation, overprovisioning, and availability queries.
- Blockdev user info mutation.
- Current/last pool and filesystem metadata dumps.
- Metadata version reporting.

## Dependencies and Interactions

- Bridges `pool::v1` and `pool::v2`.
- Implements the `engine::Pool` trait.
- Uses shared action/result types such as `CreateAction`, `DeleteAction`, `RenameAction`, `SetCreateAction`, `PoolDiff`, and `ActionAvailability`.

## Notable Details

This file contains almost no business logic. Its correctness depends on exact delegation parity: each trait method must call the corresponding implementation on both variants.
