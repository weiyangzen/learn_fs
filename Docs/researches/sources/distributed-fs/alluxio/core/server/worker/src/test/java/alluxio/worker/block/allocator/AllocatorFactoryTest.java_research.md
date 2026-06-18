## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorFactoryTest.java

**Purpose:** Tests `Allocator.Factory` class selection from Alluxio configuration and default allocator behavior.

**Important APIs:** Exercises `Allocator.Factory.create`, `WORKER_ALLOCATOR_CLASS`, and concrete strategy classes `GreedyAllocator`, `MaxFreeAllocator`, and `RoundRobinAllocator`.

**Control flow:** Setup creates a default `BlockMetadataEvictorView`. Each test sets the allocator class property, calls the factory, and asserts the instance type. The default test leaves original properties and expects `MaxFreeAllocator`.

**State and persistence:** No block state is mutated. It temporarily changes global configuration and reloads properties in `after`.

**Dependencies and integration:** Depends on `Configuration`, `PropertyKey`, `TieredBlockStoreTestUtils.defaultMetadataManagerView`, JUnit rules, and allocator class names.

**Risks:** Factory failures usually appear as reflection or constructor signature issues. Default strategy changes must update this test intentionally.

**Test signals:** Provides direct coverage for configured allocator selection and default policy.
