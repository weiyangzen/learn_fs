# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/LRUAnnotator.java

Purpose: Implements simple LRU ranking by assigning monotonically increasing logical clock values to accessed or committed blocks.

Important APIs: `updateSortedField` increments the clock and returns a new `LRUSortedField`; `updateSortedFields` sets a batch to the current clock; `isOnlineSorter` returns true; nested `LRUSortedField` compares by clock.

Control flow: Each observed block access gets a larger clock and therefore sorts later under natural order. Management tasks use natural order for cold blocks and reverse order for hot blocks.

State and persistence: Maintains an in-memory `AtomicLong` clock and transient sort fields only.

Dependencies and integration: Used through `BlockAnnotator` by `DefaultBlockIterator`, commonly as the default online orderer.

Risks and test signals: Clock values are process-local and reset on restart, so startup ordering depends on metadata scan order until accesses arrive. Tests should cover monotonic update, compare/equality behavior, and merged per-dir ordering after access events.
