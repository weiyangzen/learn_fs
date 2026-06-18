## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/RoundRobinAllocatorTest.java

**Purpose:** Tests `RoundRobinAllocator`, which rotates allocation choices across eligible directories while respecting capacity and location constraints.

**Important APIs:** Exercises round-robin allocation through `Allocator.Factory.create`, direct placement assertions, and base helper tests.

**Control flow:** Setup selects `RoundRobinAllocator`; teardown reloads configuration. The main test performs repeated allocations of controlled sizes and validates rotation across dirs/tier targets, behavior after dirs fill, and failure when no eligible location remains. Additional tests reuse base checks for tier wildcard, medium wildcard, and specific-dir allocation.

**State and persistence:** Maintains allocator-internal cursor state plus metadata capacity changes. Temporary directories exist but data is represented mostly through metadata.

**Dependencies and integration:** Extends `AllocatorTestBase`, uses global allocator configuration, storage views, and block store locations.

**Risks:** Cursor state can produce order-dependent failures if not reset between tests or when directory availability changes. Dynamic deletion/fill behavior must not point to removed/full dirs.

**Test signals:** Covers rotation, capacity exhaustion, location filtering, and shared allocator contracts.
