# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/BenchmarkThroughput.java

`BenchmarkThroughput` is a manual Hadoop `Tool` that times simple write/read loops for plain local files, raw local `FileSystem`, checksum local `FileSystem`, and a `MiniDFSCluster` HDFS instance. It prints elapsed seconds for each operation rather than asserting correctness.

The main control path parses an optional repetition count, reads `dfsthroughput.file.size` and `dfsthroughput.buffer.size`, resolves `mapred.temp.dir` from `hadoop.tmp.dir` when needed, and initializes a `LocalDirAllocator`. Helper pairs `writeLocalFile`/`readLocalFile` use Java streams, while `writeFile`/`readFile` use Hadoop `FileSystem` APIs. `writeAndReadLocalFile` and `writeAndReadFile` wrap cleanup. `run` benchmarks local variants first, then starts a one-rack `MiniDFSCluster`, waits active, benchmarks DFS, and shuts it down.

State includes `startTime`, `BUFFER_SIZE`, and allocated temporary paths. The tool creates potentially very large temporary files under the configured temp directory; cleanup is best effort. Dependencies include `Configured`, `Tool`, `ToolRunner`, `LocalDirAllocator`, `ChecksumFileSystem`, `MiniDFSCluster`, `GenericTestUtils`, and `Time`.

Risks include the 10 GB default file size, write loops that can exceed requested size when the total is not buffer-aligned, ignored read byte counts except EOF, and cleanup failures being swallowed for filesystem files. Useful signals are elapsed-time output and absence of filesystem exceptions.
