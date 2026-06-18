# File Research: sources/block-storage/stratisd/src/engine/structures/mod.rs

## Purpose

This module file declares the `lock` and `table` submodules and re-exports their public engine data structures.

## Exports

From `lock`:

- `AllLockReadAvailableGuard`
- `AllLockReadGuard`
- `AllLockWriteAvailableGuard`
- `AllLockWriteGuard`
- `AllOrSomeLock`
- `ExclusiveGuard`
- `Lockable`
- `SharedGuard`
- `SomeLockReadGuard`
- `SomeLockWriteGuard`

From `table`:

- `Table`

## Role In The Codebase

This file is a public façade for engine structures. Other modules can import `crate::engine::structures::Table` or lock guard types without depending on the private file layout.

## Dependencies

It has no runtime logic and only depends on sibling modules `lock` and `table`.
