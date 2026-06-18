# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/MovedBlocks.java

## Purpose

`MovedBlocks` tracks blocks recently selected for movement so the balancer does not repeatedly schedule the same block within a configured time window.

## Important APIs, Types, and Functions

The generic `Locations<L>` wrapper stores a `Block` and synchronized location list, with `clearLocations()`, `addLocation()`, `isLocatedOn()`, `getLocations()`, `getBlock()`, and `getNumBytes()`. `MovedBlocks` itself exposes `put()`, `contains()`, and `cleanup()` over two maps: current window and old window.

## Control Flow

Newly selected blocks are inserted into the current window. `contains()` checks both windows. `cleanup()` compares monotonic time with `lastCleanupTime + winTimeInterval`; once the interval expires, it discards the old window, moves the current window to old, creates a new current map, and updates `lastCleanupTime`.

## State and Persistence Behavior

State is in-memory only: two `Map<Block, Locations<L>>` windows and the last cleanup timestamp. Methods are synchronized, making window mutation thread-safe for concurrent dispatcher source threads. The structure intentionally survives dispatcher reset long enough to prevent near-term rebalancing churn.

## Dependencies and Integration Points

It depends on HDFS `Block` and Hadoop `Time.monotonicNow()`. `Dispatcher` extends `Locations` as `DBlock`, records successful candidate selections with `put()`, checks moved status during candidate filtering, and calls `cleanup()` between iterations.

## Risks and Edge Cases

Window rotation is lazy; stale entries remain until `cleanup()` is called. If the cleanup interval is too long, balancing may skip useful candidates; if too short, blocks can churn. `Locations.getLocations()` returns the mutable backing list even though access is synchronized only during the method call. Correctness depends on `Block.equals`/`hashCode` matching the desired block identity.

## Test Signals

Tests should cover insertion, lookup across current and old windows, cleanup rotation after interval, no rotation before interval, duplicate location suppression, synchronized access under concurrent put/contains, and dispatcher reset retaining moved-block suppression.
