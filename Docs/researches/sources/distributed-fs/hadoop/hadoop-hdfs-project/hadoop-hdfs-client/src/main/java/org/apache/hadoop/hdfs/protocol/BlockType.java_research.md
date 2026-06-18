# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockType.java

## Purpose
`BlockType` classifies HDFS blocks as replicated contiguous blocks or erasure-coded striped blocks.

## Important APIs, types, and functions
Enum values are `CONTIGUOUS` and `STRIPED`. `fromBlockId(long)` uses the highest bit of the block id to identify striped blocks. `BLOCK_ID_MASK` and `BLOCK_ID_MASK_STRIPED` define the current bit mask.

## Control flow
`fromBlockId` masks the id and returns `STRIPED` if the striped bit is set, otherwise `CONTIGUOUS`.

## State and persistence behavior
Enum constants and bit masks are static protocol conventions. No local persistence occurs.

## Dependencies and integration points
It is used by block-management and protocol code to interpret block ids for replicated versus erasure-coded layouts.

## Risks and test signals
Tests should cover high-bit set/unset ids, legacy random ids that may make conversion unreliable, and future extension compatibility if additional high bits are claimed.
