# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageDirViewTest.java

Purpose: validates `StorageDirEvictorView` as an eviction-facing wrapper over a real storage directory.

Important APIs and helpers: setup builds default metadata, obtains a tier and directory, then wraps them in `BlockMetadataEvictorView`, `StorageTierEvictorView`, and `StorageDirEvictorView`. Tests cover parent view, available/committed/capacity bytes, dir index, medium type, location conversion, evictable block filtering, and temp block creation.

Control flow and state: `getEvictableBlocks()` starts empty, adds a committed block, then checks bytes and block listing. It changes view state through pinned/in-use block tracking in the metadata view and verifies evictable blocks disappear and reappear accordingly.

Dependencies and integration: depends on metadata manager test utilities, `DefaultBlockMeta`, `DefaultTempBlockMeta`, Hamcrest matchers, and `BlockStoreLocation`.

Risks and test signals: strong signal that eviction views respect pinned/in-use state and delegate storage metrics correctly. It does not exercise actual eviction execution or concurrent pin changes.
