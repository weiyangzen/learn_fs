# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/DefaultStorageTierAssocTest.java

## Purpose
`DefaultStorageTierAssocTest` verifies storage-tier alias ordering, ordinal lookup, intersection-list construction, and ordinal interpretation for special and out-of-range tier indexes.

## Important APIs, Types, and Functions
The tests are `storageAliasListConstructor()` and `interpretTier()`. They exercise `DefaultStorageTierAssoc`, `StorageTierAssoc`, `Constants.MEDIUM_*`, `Constants.FIRST_TIER`, `Constants.SECOND_TIER`, `Constants.LAST_TIER`, `BlockStoreLocation.anyDirInTier()`, and `DefaultStorageTierAssoc.interpretOrdinal()`.

## Control Flow, State, and Persistence
The constructor test builds ordered aliases including a custom alias, checks size, alias-to-ordinal and ordinal-to-alias mappings, ordered alias list preservation, and adjacent tier intersections. The ordinal test covers single-tier and ten-tier cases, positive overflow, negative indexes, and named constants. There is no persistence.

## Dependencies and Integration Points
It depends on JUnit, Alluxio storage tier classes, and worker block-store locations. It protects tier ordering used by master and worker storage placement logic.

## Risks and Test Signals
Risks covered are off-by-one tier interpretation, custom alias handling, and incorrect adjacent-tier intersection generation. Passing tests signal stable tier semantics for configured storage levels.
