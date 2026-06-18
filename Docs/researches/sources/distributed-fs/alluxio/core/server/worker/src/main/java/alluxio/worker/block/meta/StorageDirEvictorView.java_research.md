# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirEvictorView.java

Purpose: Limited storage-directory view for evictors and management planners, including projected move-in and move-out accounting.

Important APIs: `getAvailableBytes`, `getEvictableBlocks`, `getEvitableBytes`, `clearBlockMarks`, `isMarkedToMoveOut`, `markBlockMoveIn`, and `markBlockMoveOut`.

Control flow: Available bytes are adjusted by projected move-out bytes minus move-in bytes. Evictable block lists and bytes filter the underlying directory's blocks through `BlockMetadataEvictorView.isBlockEvictable`.

State and persistence: Maintains in-memory sets of block IDs marked to move in/out and their byte totals. Underlying directory state persists separately.

Dependencies and integration: Created by `StorageTierEvictorView`; used by deprecated evictors and swap-restore balancing.

Risks and test signals: Class is not synchronized; duplicate marks are ignored by sets. There is a typo-like API name `getEvitableBytes`. Tests should cover mark accounting, clearing marks, duplicate marks, filtering pinned/locked blocks, and projected availability.
