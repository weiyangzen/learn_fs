# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataInputStream.java

Purpose: `HdfsDataInputStream` is the public evolving HDFS implementation of `FSDataInputStream`. It exposes HDFS-specific read state and statistics while supporting both plain `DFSInputStream` and encrypted `CryptoInputStream` wrappers.

Important APIs/types/functions: constructors accept `DFSInputStream` or `CryptoInputStream`; the crypto constructor verifies the wrapped stream is a `DFSInputStream`. `getWrappedStream()` returns the actual stream stored in the superclass. Private `getDFSInputStream()` unwraps crypto when needed. Public HDFS-specific methods are `getCurrentDatanode()`, `getCurrentBlock()`, `getAllBlocks()`, `getVisibleLength()`, `getReadStatistics()`, and `clearReadStatistics()`.

Control flow: all HDFS-specific methods delegate to the underlying `DFSInputStream`, unwrapping crypto first. `getAllBlocks()` may perform I/O through the underlying stream. Statistics can exceed application-visible bytes because buffering may read ahead.

State and persistence behavior: this class stores no fields beyond inherited stream state. Persistent HDFS state is not changed. It exposes transient client read state such as current DataNode, current block, located blocks, file length, and read statistics.

Dependencies and integration points: integrates with `FSDataInputStream`, `CryptoInputStream`, `DFSInputStream`, `ReadStatistics`, `DatanodeInfo`, `ExtendedBlock`, and `LocatedBlock`. It is returned by HDFS open paths when callers need HDFS-specific read inspection.

Risks: type assumptions are strict; passing a crypto stream that does not wrap `DFSInputStream` fails immediately. Methods expose mutable/read-live underlying state, so callers should not assume stable block lists during concurrent reads. Tests should cover plain and crypto construction, unwrap behavior, statistics clearing, visible length including under-construction last block, and delegation while encrypted.
