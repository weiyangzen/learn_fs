# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/Block.java

## Purpose
`Block` is the core HDFS block identity/value type, carrying block id, length, and generation stamp. Its equality, hash, and ordering are intentionally based only on block id, while helper methods support stricter id-plus-generation comparison.

## Important APIs, types, and functions
Static constants define block file prefix and metadata extension. Regex patterns parse block and meta filenames. Static helpers include `isBlockFilename`, `filename2id`, `isMetaFilename`, `metaToBlockFile`, `getGenerationStamp`, `getBlockId`, `toString(Block)`, and `matchingIdAndGenStamp`. Instance APIs include constructors from ids, another block, or a block file; setters/getters; `getBlockName`; `appendStringTo`; Writable `write/readFields`; id-only `writeId/readId`; `compareTo`; `equals`; and `hashCode`.

## Control flow
Writable serialization writes block id, byte length, and generation stamp, and deserialization rejects negative `numBytes`. Filename parsing returns 0 or the grandfather generation stamp when patterns do not match. `compareTo`, `equals`, and `hashCode` ignore length and generation stamp, matching the class contract.

## State and persistence behavior
State is mutable block id, number of bytes, and generation stamp. The class participates in Hadoop Writable serialization and is registered in `WritableFactories`, so it crosses RPC/storage serialization boundaries.

## Dependencies and integration points
It depends on `Writable`, `WritableFactories`, regex utilities, `HdfsConstants`, and Java `File`. It is foundational across HDFS protocol, NameNode metadata, DataNode storage, block readers, and block reports.

## Risks and test signals
Critical tests should verify filename regexes including negative ids and metadata generation stamps, Writable round trip and negative-size rejection, equality/hash ignoring generation stamp, `matchingIdAndGenStamp` strict comparison, and compatibility of `writeId/readId`. Callers must avoid using `equals` when generation stamp matters.
