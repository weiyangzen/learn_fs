# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCachedBlocksList.java

## Purpose
`TestCachedBlocksList` validates the intrusive cached-block lists held by `DatanodeDescriptor`: pending cached, cached, and pending uncached. It ensures list ordering, insertion, removal, iterator removal, random removal, and independent membership across multiple datanode/list combinations.

## Important APIs, Types, and Functions
The test uses `DatanodeDescriptor.CachedBlocksList`, `CachedBlock`, and `DatanodeID`. Helpers are `testAddElementsToList` and `testRemoveElementsFromList`.

## Control Flow
`testSingleList` creates one descriptor and three cached blocks. It checks empty initial lists, appends blocks, prepends one block, removes a middle block, and clears the list while verifying iterator order after each operation. `testMultipleLists` creates two descriptors and five lists, inserts 8000 `CachedBlock` instances into each list, then removes all blocks either through iterator removal or pseudo-random explicit removal.

## State and Persistence Behavior
All state is in memory. The tested lists attach `CachedBlock` entries to datanode-specific linked-list state, so the same block objects must be able to appear in multiple descriptor lists without corrupting list pointers.

## Dependencies and Integration Points
The test is internal to HDFS caching metadata. It does not use cluster services, but it protects the data structures used by centralized cache management and datanode cache directives.

## Risks and Edge Cases
The high-risk area is pointer corruption in intrusive lists when blocks are inserted into several lists or removed through different paths. The 8000-block randomized removal pass is a stress signal for iterator consistency and per-list independence.

## Test Signals
Assertions verify empty-list state, exact iteration order, successful add/remove return values, no remaining iterator entries after clear/removal, and stability across multiple datanode cached-block lists.
