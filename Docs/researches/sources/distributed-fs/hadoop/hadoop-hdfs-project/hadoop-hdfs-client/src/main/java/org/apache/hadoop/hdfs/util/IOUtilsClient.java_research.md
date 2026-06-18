# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/IOUtilsClient.java

Purpose: `IOUtilsClient` contains client-side cleanup and read-statistics helpers.

Important APIs/types/functions: `cleanupWithLogger(Logger, Closeable...)` closes each non-null closeable and logs any thrown `Throwable` at debug level. `updateReadStatistics(ReadStatistics, int, BlockReader)` delegates to the overload using `blockReader.isShortCircuit()` and network distance. The overload increments short-circuit, local, or remote byte counts when `nRead > 0`.

Control flow: cleanup intentionally suppresses all close failures. Statistics updates ignore zero/negative reads, then classify by short-circuit first, network distance zero second, remote otherwise.

State and persistence behavior: stateless utility; mutates caller-provided `ReadStatistics`.

Dependencies and integration points: depends on `BlockReader`, `ReadStatistics`, SLF4J, and Java `Closeable`. Used throughout HDFS client cleanup/error paths and read accounting.

Risks and test signals: suppressing `Throwable` is appropriate for cleanup but can hide serious errors if used outside exception cleanup paths. Tests should cover null closeables, thrown `IOException`/runtime error suppression, and statistics classification for short-circuit/local/remote/zero-byte reads.
