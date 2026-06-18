<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterUtils.java

## Purpose
Utility class for creating configured master services and selecting metastore implementations for block and inode metadata.

## Important APIs, Types, And Functions
- `createMasters(MasterRegistry, MasterContext)` loads `MasterFactory` implementations from `ServiceUtils`, invokes enabled factories concurrently, and registers created masters.
- `getBlockStoreFactory(String)` returns heap or RocksDB block metastore factories based on `MASTER_BLOCK_METASTORE` or `MASTER_METASTORE`.
- `getInodeStoreFactory(String)` returns heap, RocksDB, or caching RocksDB inode store factories based on inode/metastore configuration and cache size.

## Control Flow
Master creation builds callables for all loaded factories and executes them via `CommonUtils.invokeAll` with a ten-minute timeout. Metastore factory selection checks more-specific config keys first, then falls back to global master metastore type.

## State And Persistence Behavior
Heap metastores are in-memory. RocksDB factories persist metadata under the supplied base directory. Caching inode store wraps RocksDB when the configured inode cache size is nonzero.

## Dependencies And Integration Points
Depends on Alluxio configuration, service loader utilities, metastore types, heap/Rocks/caching metastore classes, and `MasterRegistry`. Used by primary and secondary master process construction.

## Risks And Edge Cases
Factory invocation is parallel, so master factories must tolerate dependency lookup ordering or explicitly fetch already-created required masters. Unknown metastore types throw `IllegalStateException`.

## Test Signals
Signals include correct factory enablement/registration, timeout/error wrapping from `createMasters`, and metastore factory selection for heap, RocksDB, and RocksDB-with-cache configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterUtils.java -->
