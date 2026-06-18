## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTestBase.java

**Purpose:** Shared fixture for `DefaultBlockWorker` tests. It centralizes two-tier worker storage, mocked master clients, UFS mounts, a real `MonoBlockStore`, and cache helper behavior.

**Important APIs:** Provides `before`, `cacheBlock`, `createMockBlockMasterClient`, and `createMockFileSystemMasterClient`, plus constants for block size, worker ID, UFS mount IDs, worker address, and invalid worker ID.

**Control flow:** The setup creates MEM/HDD temp directories, applies a `ConfigurationRule`, mocks block master heartbeat and worker-ID responses, constructs a spied `TieredBlockStore` and `MonoBlockStore`, registers two UFS mounts, writes an increasing-byte UFS file for load tests, and instantiates `DefaultBlockWorker`.

**State and persistence:** Creates real temporary local storage and UFS files. The helper `cacheBlock` writes random data to UFS, issues a cache request, waits for async completion if requested, and reads the cached local block back.

**Dependencies and integration:** Bridges `DefaultBlockWorker`, `BlockMasterClientPool`, `FileSystemMasterClient`, `Sessions`, `NoopUfsManager`, `NetworkAddressUtils`, `WaitForOptions`, and local block readers.

**Risks:** Because the fixture is shared, configuration mistakes affect many tests. The helper validates data with `ByteBuffer.compareTo`, which depends on buffer position/limit correctness.

**Test signals:** Enables consistent coverage for worker lifecycle, local tier placement, UFS fallback/load/cache, heartbeat defaults, and pin-list defaults.
