# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageTierViewTest.java

Purpose: tests `StorageTierEvictorView` directory-view accessors and metadata-view linkage.

Important APIs and helpers: setup creates default block metadata, selects a storage tier, wraps it in `BlockMetadataEvictorView`, and obtains a `StorageTierEvictorView`. Tests cover `getDirViews`, `getDirView`, bad-index handling, tier alias, tier ordinal, and `getBlockMetadataEvictorView`.

Control flow and state: the view is initialized once from real test metadata. Assertions compare view values back to underlying `StorageTier` properties and expected default layout directory count.

Dependencies and integration: depends on `TieredBlockStoreTestUtils.defaultMetadataManager`, `TemporaryFolder`, and Alluxio storage metadata view classes.

Risks and test signals: coverage is accessor-focused and documents bad directory index behavior returning `null`. It provides support-level signal for eviction-policy code that consumes tier views.
