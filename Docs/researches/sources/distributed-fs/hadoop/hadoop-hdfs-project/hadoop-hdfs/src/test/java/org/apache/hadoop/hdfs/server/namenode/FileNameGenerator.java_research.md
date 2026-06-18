<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FileNameGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FileNameGenerator.java

Purpose: small package-private helper that generates a balanced tree of test file or directory names for NameNode throughput benchmarks, limiting entries per directory.

Important APIs/types/functions: constructors accept `baseDir` and optional `filesPerDir`; `getNextFileName(String)` is synchronized and returns the next leaf path; `getNextDirName(String)` advances the path index vector; `getFileCount()`, `getFilesPerDirectory()`, and `getCurrentDir()` expose generator state.

Control flow: `reset()` fills a fixed 20-level index array with `-1`. Each new file increments `fileCount`; when `fileCount % filesPerDirectory == 0`, a new current directory is built by incrementing the first non-full level or extending depth. Names are formed by concatenating `baseDir`, directory prefixes, and the monotonically increasing file number.

State and persistence: all state is in memory: `pathIndecies`, `currentDir`, `filesPerDirectory`, and `fileCount`. There is no filesystem mutation; callers create the generated paths.

Dependencies and integration points: used by `NNThroughputBenchmark` create/open/delete/rename/mkdir/block-report setup to avoid huge flat directories that would distort benchmark behavior.

Risks and test signals: the fixed 20-level array bounds total generated paths and can throw `ArrayIndexOutOfBoundsException` for extreme workloads; benchmark callers catch that to suggest a different per-directory value. Synchronization protects concurrent calls, but `getFileCount()` is unsynchronized. Signals are deterministic path ordering and bounded directory fanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FileNameGenerator.java -->
