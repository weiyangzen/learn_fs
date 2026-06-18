## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorContractTest.java

**Purpose:** Defines contract tests that all `Allocator` implementations in the allocator package must satisfy.

**Important APIs:** Uses package scanning to discover `Allocator` implementation classes, sets `WORKER_ALLOCATOR_CLASS`, calls `Allocator.Factory.create`, and validates allocation through `assertTempBlockMeta`.

**Control flow:** `before` extends `AllocatorTestBase` setup, then uses Guava `ClassPath` to find classes implementing `Allocator`. Tests iterate each strategy, reset the metadata view, and verify oversized allocations fail, valid allocations succeed for tier-specific and any-tier targets, and allocation still works after deleting one directory from each tier.

**State and persistence:** Uses temporary tier directories and metadata views from the base class. Directory deletion mutates in-memory `StorageTier` lists to simulate failed/removed dirs.

**Dependencies and integration:** Depends on reflection/classpath scanning, global configuration, allocator factory, `BlockMetadataEvictorView`, and base helper assertions.

**Risks:** Reflection can miss implementations if classloader packaging changes. Contract coverage protects common behavior but not exact placement policy.

**Test signals:** Ensures all allocator strategies honor capacity boundaries, tier constraints, any-tier behavior, and dynamic directory removal.
