# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlocks.java

## Purpose
`LocatedBlocks` is the collection-level response for block-location lookup. It stores file length, an ordered list of located blocks, under-construction status, last block metadata, file encryption info, and EC policy.

## APIs and Control Flow
Getters expose blocks, count, indexed access, file length, last block, construction status, encryption info, and EC policy. `findBlock(offset)` performs binary search using a synthetic one-byte key and a comparator that returns equality when ranges overlap. `insertRange(blockIdx, newBlocks)` merges refreshed block ranges into the sorted existing list, replacing same-offset entries and inserting new earlier entries. `getInsertIndex()` converts a binary-search result to an insertion index.

## State, Dependencies, and Integration
The list is stored by reference and mutated by `insertRange`. The class integrates with `ClientProtocol.getBlockLocations`, DFSInputStream block refresh, encryption metadata, and erasure-coded files.

## Risks and Test Signals
The default constructor leaves `blocks` null; callers must use `locatedBlockCount()` or avoid direct `getLocatedBlocks()` iteration. `insertRange()` asserts sorted input rather than throwing. Tests should cover binary search at block boundaries, empty/null lists, range insertion/replacement, under-construction last-block flags, and EC/encryption metadata propagation.
