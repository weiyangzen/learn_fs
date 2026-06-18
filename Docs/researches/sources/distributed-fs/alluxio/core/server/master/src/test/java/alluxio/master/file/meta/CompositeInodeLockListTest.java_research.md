# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CompositeInodeLockListTest.java

## Purpose
Unit tests for `CompositeInodeLockList`, which extends an existing base lock list while preserving ownership boundaries. The tests validate extension, lock mode reporting, locked inode list views, and close/unlock behavior.

## Important APIs/types/functions
- Extends `BaseInodeLockingTest`.
- Uses `SimpleInodeLockList` as `mBase` and `CompositeInodeLockList` as `mComposite`.
- Exercises `lockRootEdge`, `lockInode`, `lockEdge`, `unlockLastInode`, `unlockLastEdge`, `close`, `getLockMode`, `getLockedInodes`, `numInodes`, `isEmpty`, and `get`.

## Control flow
- `unlockOnlyExtension` locks part of the path in the base, extends in composite, closes composite, and verifies only base locks remain.
- `extendFromEdge` starts from base locked through an edge, then locks inode/edge in composite and checks list contents and write-mode promotion.
- `extendFromInode` starts with only root inode locked, then extends edge/inode and validates similar state.
- `extendFromWriteLocked` verifies a base write-locked root edge makes composite lock mode WRITE.
- `doubleWriteLock` locks and unlocks a write-locked inode while retaining WRITE mode.
- `unlockIntoBase` calls `unlockLastEdge` when only base owns the edge, validating boundary handling.

## State and persistence behavior
- In-memory lock state only; no inode metadata persistence.
- Teardown closes composite/base and then asserts all locks released through the base class.

## Dependencies and integration points
- Integrates composite lock-list semantics with `InodeLockManager`, `LockMode`, and fixed inode tree fixture.

## Risks and edge cases
- Some tests do not assert exceptions for boundary unlocks, implying current behavior may be no-op/tolerant.
- Does not cover mixed read/write upgrades on every possible node/edge sequence.

## Test signals
- Strong signal that composite lock lists do not release locks they do not own and report lock mode/list state correctly.
