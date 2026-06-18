# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierEvictorView.java

Purpose: Evictor-facing tier view that wraps each directory with a `StorageDirEvictorView` tied to a block metadata evictor view.

Important APIs: Constructor and `getBlockMetadataEvictorView`.

Control flow: Construction creates one evictor dir view per underlying storage dir and stores it by index.

State and persistence: View state only, plus reference to the owning evictor view. No persistence.

Dependencies and integration: Used by `BlockMetadataEvictorView`, deprecated evictors, and management planners.

Risks and test signals: Like allocator tier views, it snapshots the directory set. Tests should cover evictor-view reference preservation and directory wrapper creation.
