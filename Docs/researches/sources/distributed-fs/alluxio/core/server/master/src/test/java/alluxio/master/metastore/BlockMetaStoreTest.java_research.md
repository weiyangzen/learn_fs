# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/BlockMetaStoreTest.java

Purpose: parameterized behavioral tests for block metadata stores backed by RocksDB and heap memory.

Important APIs/types/functions: uses `BlockMetaStore`, `RocksBlockMetaStore`, `HeapBlockMetaStore`, protobuf `BlockMeta` and `BlockLocation`, `CloseableIterator`, and configuration key `ROCKS_BLOCK_CONF_FILE`.

Control flow: parameter setup creates a temporary Rocks options file and supplies both Rocks and heap store factories. Each test creates a fresh store and closes it after. Rocks-specific tests reopen with a valid config file and run `testPutGet`, or reopen with invalid config text and expect a `RuntimeException` caused by `RocksDBException`. `testPutGet` writes three blocks and verifies lengths. `testIterator` verifies iterator order and content for three blocks. `blockLocations` writes five blocks and one location each, then reads locations back. `blockSize` verifies `size` increments with writes and returns to zero after removals.

State and persistence behavior: heap store is transient; Rocks store persists under the temporary directory during each store instance. Tests explicitly clear after some operations.

Dependencies and integration points: verifies common `BlockMetaStore` contract used by block master metadata, plus RocksDB option-file loading.

Risks: iterator ordering is assumed to match insertion/id order. It does not test multiple locations per block, duplicate locations, remove-location behavior, or checkpoint/restore.

Test signals: good cross-implementation contract signal for basic block metadata CRUD and Rocks config handling.
