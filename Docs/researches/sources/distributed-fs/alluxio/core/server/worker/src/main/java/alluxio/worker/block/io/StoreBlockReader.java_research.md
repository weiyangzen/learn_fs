# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockReader.java

Purpose: Local file block reader wrapper that emits stream tracking events for committed block reads.

Important APIs: Constructor opens the block path from `BlockMeta`; `close` sends a close event then delegates to `LocalFileBlockReader.close`.

Control flow: For positive session IDs, construction calls `BlockStreamTracker.readerOpened`; close calls `readerClosed`. Internal or non-session reads skip tracking.

State and persistence: Holds session ID and block metadata. It reads the committed block file path but does not alter metadata.

Dependencies and integration: Extends `LocalFileBlockReader`, consumes `BlockMeta`, and feeds `DefaultStoreLoadTracker` through `BlockStreamTracker`.

Risks and test signals: Close must be called exactly once by callers to avoid stale load-tracker state; repeated close behavior depends on superclass. Tests should cover tracked versus untracked session IDs and exception behavior around close.
