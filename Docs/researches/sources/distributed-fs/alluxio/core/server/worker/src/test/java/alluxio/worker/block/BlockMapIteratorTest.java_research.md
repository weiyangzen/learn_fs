# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMapIteratorTest.java

## Purpose
`BlockMapIteratorTest` verifies `BlockMapIterator` batching of block-location maps into proto entries without duplicate tier/medium locations in a batch.

## Important APIs, Types, and Functions
`convertStream()` builds large MEM/SSD/HDD maps with two dirs each and iterates batches. `convertStreamMergedTiers()` uses uneven dir sizes. Both assert that each returned batch has no duplicate `Block.BlockLocation` constructed from tier alias and medium type.

## Control Flow, State, and Persistence
The test generates in-memory maps of decreasing block IDs and consumes iterator batches. It performs no persistence.

## Dependencies and Integration Points
It depends on `BlockMapIterator`, `BlockStoreLocation`, `LocationBlockIdListEntry`, proto `Block.BlockLocation`, and Guava immutable collections.

## Risks and Test Signals
The main signal is that registration/heartbeat streaming can batch location entries without duplicate logical locations. Gaps include exact batch sizing, ordering, empty maps, medium type propagation, and memory behavior for very large maps.
