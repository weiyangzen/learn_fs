## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRFUAnnotatorTest.java

**Purpose:** Tests `LRFUAnnotator`, the block ordering policy blending recency and frequency.

**Important APIs:** Configures `LRFUAnnotator`, initializes common annotator fixtures, and validates iterator order after create/access operations.

**Control flow:** Setup creates the metadata/iterator through `AbstractBlockAnnotatorTest.init` and selects the LRFU annotator. The test creates blocks, performs access patterns that should change combined recency/frequency scores, then compares iterator output to expected block ID order.

**State and persistence:** Maintains annotator score/order state through block store event listener callbacks and temporary committed block metadata.

**Dependencies and integration:** Extends the abstract annotator test, uses Alluxio configuration, storage dirs, and block iterator APIs consumed by eviction.

**Risks:** LRFU behavior is sensitive to time/score decay parameters; deterministic tests must avoid relying on wall-clock ambiguity. Incorrect score updates affect eviction fairness.

**Test signals:** Confirms basic LRFU ordering and inherits remove/move correctness tests from the base class.
