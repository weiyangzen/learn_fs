# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreCommitBlockTest.java

Purpose: tests `PagedBlockStore.commitBlock` event ordering and failure behavior for local metadata commit and master commit.

Important APIs and helpers: setup constructs a local page-store dir, mocked `BlockMasterClientPool`/`BlockMasterClient`, `PagedBlockStoreDir`, and a spied `BlockStoreEventListener`. `prepareBlockStore()` allocates a temp block, creates a block writer, waits for cache manager read-write state, appends data, and registers the listener.

Control flow and state: success test commits locally and to master and verifies both listener callbacks. One test overrides `PagedBlockMetaStore.commit` to throw and expects no local or master callbacks. Another makes `BlockMasterClient.commitBlock` throw `UNAVAILABLE`; local callback fires but master callback does not.

Dependencies and integration: depends on `PagedBlockStore`, `CacheManager.Factory`, page-store dirs, mocked block master RPC, `CreateBlockOptions`, and event listener contracts.

Risks and test signals: good signal for partial failure boundaries and listener notification sequencing. It uses a real local page store but mocks master RPC and worker ID.
