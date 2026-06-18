# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierView.java

Purpose: Abstract restricted view over a `StorageTier` for allocator and evictor consumers.

Important APIs: Constructors with optional reserved-space mode; `getDirViews`, `getDirView`, `getTierViewAlias`, and `getTierViewOrdinal`.

Control flow: Subclasses populate the protected `mDirViews` map with appropriate directory view types.

State and persistence: Holds underlying tier reference, directory-view map, and reserved-space flag. No independent persistence.

Dependencies and integration: Base class for `StorageTierAllocatorView` and `StorageTierEvictorView`.

Risks and test signals: `getDirViews` exposes the mutable values collection of the map. Tests should cover alias/ordinal delegation and directory retrieval by index.
