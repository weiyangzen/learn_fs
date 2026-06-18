## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRUAnnotatorTest.java

**Purpose:** Tests `LRUAnnotator`, the least-recently-used block ordering implementation for eviction iteration.

**Important APIs:** Configures `LRUAnnotator`, uses common block create/access helpers, and validates `BlockIterator` order.

**Control flow:** Setup initializes the abstract annotator fixture with LRU configuration. The test creates blocks, accesses selected blocks, and expects iterator order to place least recently used blocks first.

**State and persistence:** State is maintained in annotator/listener order structures and temporary committed block metadata.

**Dependencies and integration:** Extends `AbstractBlockAnnotatorTest`; integrates with `BlockStoreEventListener`, `BlockIterator`, tiered metadata, and eviction ordering.

**Risks:** Missing access notifications or incorrect order updates can cause hot blocks to be evicted. Tests must keep event sequence deterministic.

**Test signals:** Verifies LRU-specific access ordering and inherits common remove/move iterator tests.
