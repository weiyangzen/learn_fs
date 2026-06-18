# File Research: sources/block-storage/stratisd/src/engine/types/diff.rs

## Purpose

Provides generic and Stratis-specific structures for reporting state differences between old and new engine snapshots.

## Main Types and Behavior

- `Compare` is implemented for any `PartialEq + Clone` type and returns `Diff::Changed(new)` or `Diff::Unchanged(new)`.
- `Diff<T>` stores the current value in both variants, supports `is_changed()`, `changed()`, `Deref`, and `DerefMut`.
- `ThinPoolDiff` tracks thin pool `allocated_size` and `used`.
- `StratPoolDiff` tracks pool physical size, metadata size, and allocation-space exhaustion.
- `StratFilesystemDiff` tracks filesystem size and used space.
- `PoolDiff` groups thin-pool and pool-level diffs.
- `StratBlockDevDiff` tracks block device size changes.

## Integration Points

These types are used by background event processing and IPC notification paths to determine whether pool, filesystem, or blockdev attributes need to be reported.

## Notable Semantics

`Diff<T>` keeps the updated value even when unchanged, allowing downstream calculations to use a uniform dereference path without separately carrying a current-state value.
