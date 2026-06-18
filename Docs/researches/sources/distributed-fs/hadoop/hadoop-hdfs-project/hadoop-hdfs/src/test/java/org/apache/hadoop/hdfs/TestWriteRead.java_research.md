# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteRead.java

Purpose: Stress-style tests for reading files while they are still being written, covering sequential reads, positional reads, reads of the current block, hflush visibility, close visibility, and a command-line mode for real clusters.

Important APIs and types: `MiniDFSCluster`, `FileSystem`, `FileContext`, `FSDataOutputStream.hflush`, `HdfsDataInputStream.getVisibleLength`, `FSDataInputStream.read`, positional `read(position, ...)`, `FileStatus.getLen`, and `CreateFlag`.

Control flow: `@BeforeEach` starts a three-datanode cluster with 100 KB block size and creates `/tmp`. Tests configure sequential or positional read options and call `testWriteAndRead`. The helper opens a file for create/append/truncate, writes repeated chunks, hflushes every other iteration, then reads back only the visible length from either the beginning or a block-internal position. After final close it verifies readers see all bytes and NameNode length matches. Helper methods support both `FileSystem` and `FileContext` paths. `main` parses options and runs against an existing cluster.

State and persistence behavior: The key state is visible length versus bytes written but not hflushed. HDFS namespace length is checked after close. Command-line options mutate instance fields for alternate runs.

Dependencies and integration points: Integrates DFS write pipeline, hflush semantics, visible length reporting, read APIs, append/truncate behavior, FileContext compatibility, and NameNode length metadata.

Risks and test signals: This is timing/load heavy (`350` write-read loops in unit tests) and verbose logging can be large. Passing signals readers never observe less than the expected visible data and never more than total written data while a file is open.
