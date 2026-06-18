## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTestUtil.java

### Purpose
`UnderFileSystemTestUtil` contains helper methods for UFS unit tests.

### Important APIs, Types, And Functions
`performListingAsyncAndGetResult` invokes `UnderFileSystem.performListingAsync` and waits for completion using a `CountDownLatch`, storing either result or error in `AtomicReference`s.

### Control Flow
The helper calls `performListingAsync` with null continuation/start-after, `checkStatus` set to true only for `DescendantType.NONE`, and callbacks that set result/error then count down. After `await`, it throws any callback error or returns the result.

### State And Persistence
Uses transient synchronization primitives only.

### Dependencies And Integration Points
Used by async listing tests to make callback APIs testable in synchronous JUnit methods.

### Risks
There is no timeout, so a broken async implementation that never calls back will hang the test. It does not close streams from the returned result.

### Test Signals
Supports concise tests for async metadata sync behavior.
