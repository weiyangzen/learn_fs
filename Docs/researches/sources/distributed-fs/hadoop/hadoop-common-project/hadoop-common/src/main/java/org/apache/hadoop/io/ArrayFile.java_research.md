<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayFile.java

Purpose: dense file-backed array abstraction implemented on top of `MapFile` with monotonically increasing long keys.

Important APIs, types, and functions: `ArrayFile.Writer` extends `MapFile.Writer`, fixes the key class to `LongWritable`, and `append(Writable)` writes at the current count then increments it. `ArrayFile.Reader` extends `MapFile.Reader` and exposes `seek(long)`, `next(Writable)`, `key()`, and `get(long, Writable)` using a reusable `LongWritable` key.

Control flow: writing appends values in order with implicit indexes. Reading seeks or gets by numeric index and delegates to `MapFile` lookup/iteration.

State and persistence: writer state is the current count. reader state is the reusable key holding the most recent index. Persistent data is the underlying MapFile directory with sequence data and index files.

Dependencies and integration points: depends on Hadoop `FileSystem`, `Path`, `MapFile`, `LongWritable`, `SequenceFile.CompressionType`, and progress callbacks.

Risks and test signals: callers must append in dense order; random writes are not supported. Tests should cover compressed and uncompressed writers, seek/next/get semantics, key reporting, empty/missing index behavior, and MapFile compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayFile.java -->
