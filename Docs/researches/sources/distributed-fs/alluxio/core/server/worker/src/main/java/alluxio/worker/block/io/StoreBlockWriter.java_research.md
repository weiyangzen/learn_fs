# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/StoreBlockWriter.java

Purpose: Local file block writer wrapper that emits stream tracking events for temp block writes.

Important APIs: Constructor opens the temp path from `TempBlockMeta`; `close` sends writer close events and delegates to `LocalFileBlockWriter.close`.

Control flow: Positive session IDs produce `writerOpened` on construction and `writerClosed` on close. Internal writes skip tracking.

State and persistence: Holds temp block metadata and writes to the temp block file path through the superclass.

Dependencies and integration: Extends `LocalFileBlockWriter`, consumes `TempBlockMeta`, and feeds load detection through `BlockStreamTracker`.

Risks and test signals: If writer construction succeeds but close is missed, background management may see stale load. Tests should cover event ordering, session filtering, and close delegation.
