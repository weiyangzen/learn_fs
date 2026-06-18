## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/ObjectUnderFileSystemTest.java

### Purpose
`ObjectUnderFileSystemTest` checks selected superclass behavior for object UFS implementations.

### Important APIs, Types, And Functions
`testRetryOnException` directly exercises protected `retryOnException` using a mocked `ObjectStoreOperation`. `testListObjectStorageDescendantTypeNone` builds an anonymous object UFS overriding status/listing methods and calls `UnderFileSystemTestUtil.performListingAsyncAndGetResult`.

### Control Flow
The retry test configures max retries to 20, verifies a `SocketException` is retried and succeeds, then verifies `FileNotFoundException` is thrown without broad retry. The async listing test sets two child file statuses under `root`, requests `DescendantType.NONE`, and expects one item representing the base path.

### State And Persistence
Uses configuration rule state and in-memory mock/anonymous classes. No real object store.

### Dependencies And Integration Points
Depends on Mockito, JUnit, `ConfigurationRule`, `DescendantType`, `ListOptions`, and `UnderFileSystemTestUtil`.

### Risks
Coverage is narrow. It does not cover delete/rename batching, directory marker creation, chunk iteration, or recursive object listing. Anonymous overrides bypass much real superclass listing code.

### Test Signals
Useful signal for retry exception classification and metadata-sync behavior for object-store `DescendantType.NONE`.
