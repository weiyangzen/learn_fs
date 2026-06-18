# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirView.java

Purpose: Abstract restricted view over a `StorageDir` shared by allocator and evictor views.

Important APIs: Abstract `getAvailableBytes`; getters for reserved, index, capacity, committed bytes, parent tier view, medium, and location; `createTempBlockMeta`.

Control flow: Subclasses decide availability semantics, while common methods delegate to the underlying directory. `createTempBlockMeta` creates metadata without inserting it into the directory.

State and persistence: Holds references to underlying dir and tier view. No independent persistence.

Dependencies and integration: Base for `StorageDirAllocatorView` and `StorageDirEvictorView`.

Risks and test signals: Exposes temp metadata creation even to view users, so callers must still add metadata through store paths. Tests should cover location construction and subclass availability differences.
