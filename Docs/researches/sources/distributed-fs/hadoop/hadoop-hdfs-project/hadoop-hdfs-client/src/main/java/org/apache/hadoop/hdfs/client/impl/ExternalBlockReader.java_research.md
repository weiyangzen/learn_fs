# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/ExternalBlockReader.java

## Purpose
`ExternalBlockReader` adapts a pluggable `ReplicaAccessor` into the standard HDFS `BlockReader` interface, allowing custom replica-reading implementations to participate in normal DFS input stream reads.

## Important APIs, types, and functions
The constructor receives a `ReplicaAccessor`, visible replica length, and start offset. `read(byte[],...)` and `read(ByteBuffer)` call the accessor at the current `pos` and advance `pos` only on non-negative reads. `skip` advances forward without exceeding `visibleLength`. `available` returns remaining bytes capped to `Integer.MAX_VALUE`. `isShortCircuit` and `getNetworkDistance` delegate to the accessor. `readFully` and `readAll` delegate to `BlockReaderUtil`.

## Control flow
Reads are positional through the accessor rather than stream-position based. EOF is propagated directly if the accessor returns a negative value. Skips do not invoke the accessor and cannot move backward. `close` closes the accessor.

## State and persistence behavior
State consists of the accessor, visible length, and mutable current position. The class persists nothing and exposes no checksum or zero-copy mmap support (`getDataChecksum` and `getClientMmap` return null).

## Dependencies and integration points
It depends on `ReplicaAccessor`, `BlockReader`, `ClientMmap`, `ReadOption`, `DataChecksum`, and `BlockReaderUtil`. It is configured indirectly by `DfsClientConf` replica accessor builder classes and used when external replica access is selected.

## Risks and test signals
Tests should cover positional advancement, EOF without position advancement, skip clamping at visible length, large remaining length in `available`, accessor close propagation, direct `ByteBuffer` reads, and integration with `readFully`/`readAll`. A functional risk is that checksum and mmap are unsupported, so callers must tolerate null checksum and no zero-copy path.
