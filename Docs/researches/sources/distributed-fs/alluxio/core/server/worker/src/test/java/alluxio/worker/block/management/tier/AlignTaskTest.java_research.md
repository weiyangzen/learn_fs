## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/AlignTaskTest.java

**Purpose:** Tests `AlignTask`, a tier-management task that aligns blocks across tiers according to management policy.

**Important APIs:** Exercises `AlignTask.run` or task execution through `BaseTierManagementTaskTest`, block placement helpers, and tier-alignment configuration.

**Control flow:** Setup calls the base tier-management fixture and creates an `AlignTask` for the test metadata/store context. The test seeds blocks in tiers/dirs, runs the task, and validates that blocks are moved into the expected aligned layout.

**State and persistence:** Uses temporary tiered block store state from the base class, including real local block metadata/files and movement side effects.

**Dependencies and integration:** Depends on tier-management base fixtures, `TieredBlockStore`, allocation/move logic, configuration flags for tier alignment, and block metadata views.

**Risks:** Alignment tasks can conflict with locks, reserved space, and ongoing writes. Incorrect move planning could churn data or violate storage constraints.

**Test signals:** Provides focused coverage that the alignment management task produces expected placement changes under a controlled tier topology.
