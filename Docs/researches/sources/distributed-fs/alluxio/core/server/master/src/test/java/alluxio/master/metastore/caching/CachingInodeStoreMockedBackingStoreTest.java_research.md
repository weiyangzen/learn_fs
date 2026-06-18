# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/caching/CachingInodeStoreMockedBackingStoreTest.java

Purpose: tests `CachingInodeStore` cache hit behavior, eviction, listing cache accounting, backing-store flush, checkpoint restore, and skip-cache reads using a spied heap backing store.

Important APIs/types/functions: uses `CachingInodeStore`, `HeapInodeStore`, `InodeStore`, `ReadOption`, `CheckpointInputStream`, cache internals `mInodeCache`, `mEdgeCache`, and `mListingCache`, plus Mockito read/write verification.

Control flow: setup creates a spied heap backing store, wraps it in `CachingInodeStore`, and writes one test directory. Basic cache tests repeatedly call `getMutable`, `get`, `getChild`, and `getChildren` and verify no backing reads. Many-read tests create more inodes/edges than cache size and assert backing writes do not exceed expected once-per-object levels. Removal/write tests ensure cached values reflect deletes and updates. Eviction tests force inode/edge evictions and verify backing reads occur when needed. `edgeIndexTest` runs concurrent add/remove operations, waits for eviction sleep, and verifies edge cache indices. Listing cache tests cover many directories, one large directory, and add/remove edge churn without incorrect weight growth. `flushToBackingStore` verifies cache flush pushes inodes/edges to backing. `backupRestore` checkpoint round-trips cached state. `skipCache` reads from backing without populating the inode cache.

State and persistence behavior: state is split between caches and heap backing store; explicit flush synchronizes. Checkpoint state is serialized to an in-memory byte array.

Dependencies and integration points: targets production cache behavior used by Rocks-backed inode stores and recursive/listing paths.

Risks: accesses package-private cache internals, making tests sensitive to implementation refactors. Concurrency test is time/operation-count based.

Test signals: strong targeted signal for cache correctness, eviction invariants, backing-store isolation, and checkpoint compatibility.
