# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BaseTierManagementTaskTest.java

Purpose: shared fixture for tier-management background task tests. It creates a deterministic two-tier `TieredBlockStore` layout and exposes selected storage directories for alignment, promotion, and swap/restore tests.

Important APIs and helpers: constants define tier aliases, block sizes, and the synthetic load session/block IDs. `init()` configures the accepting reviewer, LRU annotator, default block size, and load-detection cooldown, then builds the default test tier layout. `startSimulateLoad()` creates a temporary uncommitted block and writer; `stopSimulateLoad()` aborts it and closes the writer.

Control flow and state: `init()` uses `TieredBlockStoreTestUtils.setupDefaultConf`, constructs a real `TieredBlockStore`, then reflects out its private `mMetaManager` to obtain `BlockMetadataManager`, `BlockIterator`, and concrete `StorageDir` objects. The synthetic writer keeps the worker "busy" until tests release it, gating background management tasks.

Dependencies and integration: depends on global `Configuration`, `TieredBlockStore`, `BlockMetadataManager`, `LRUAnnotator`, `AllocateOptions`, and JUnit `TemporaryFolder`.

Risks and test signals: reflection against `mMetaManager` is brittle if internals are renamed. Global configuration mutation requires callers to reload/reset before setup. The fixture strongly signals integration-level task behavior because it uses real block-store metadata rather than mocks.
