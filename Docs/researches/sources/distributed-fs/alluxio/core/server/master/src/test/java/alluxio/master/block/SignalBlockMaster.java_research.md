<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/SignalBlockMaster.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/SignalBlockMaster.java

**Purpose:** Test helper subclass of `DefaultBlockMaster` that emits a latch signal when a block lock is acquired, enabling deterministic race orchestration in block master concurrency tests.

**Important APIs/types/functions:** Extends `DefaultBlockMaster`, overrides package-private `lockBlock(long)`, returns `LockResource`, and exposes `setLatch(CountDownLatch)`. Constructors mirror the default master constructor variants used by tests.

**Control flow:** `lockBlock` delegates to `super.lockBlock(blockId)`, then calls `mLatch.countDown()` before returning the lock resource. Test code swaps latches before exercising a race, causing readers or second writers to proceed once the first operation has entered the protected section.

**State and persistence behavior:** Holds only a mutable `CountDownLatch` reference and does not change persistence. Its side effect is synchronization-only; it relies on `CountDownLatch` no-op behavior after reaching zero.

**Dependencies and integration points:** Integrates with `ConcurrentBlockMasterTest` and any test needing visibility into `DefaultBlockMaster` lock timing. It depends on package-private access to `lockBlock`, so it lives in the same package.

**Risks:** Because it signals after the lock is acquired but before the caller's operation completes, tests depend on exact internal call placement. If `DefaultBlockMaster` changes locking granularity, this helper may no longer synchronize at the intended point.

**Test signals:** There are no direct assertions in this helper. Its signal is observed indirectly when concurrent tests proceed and complete without deadlock or illegal state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/SignalBlockMaster.java -->
