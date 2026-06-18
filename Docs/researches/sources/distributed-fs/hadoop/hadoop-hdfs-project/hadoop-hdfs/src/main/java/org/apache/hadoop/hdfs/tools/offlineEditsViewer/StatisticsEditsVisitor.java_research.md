## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/StatisticsEditsVisitor.java

Purpose: `StatisticsEditsVisitor` counts edit-log operation opcodes and writes a human-readable summary. It is the implementation behind `hdfs oev -p stats`.

Important APIs and control flow: the constructor wraps the supplied `OutputStream` in a UTF-8 `PrintWriter`. `start(int version)` records the log version. `visitOp(FSEditLogOp op)` increments a `Map<FSEditLogOpCodes, Long>` keyed by `op.opCode`. `close(Throwable error)` writes `getStatisticsString()`, appends an error marker if supplied, and closes the writer. `getStatistics()` exposes the live count map for tests or embedding; `getStatisticsString()` emits version plus every known opcode, defaulting missing counts to zero.

State, persistence, and dependencies: state is the version and opcode-count map. Output persistence is the stream provided by the factory. Dependencies include `FSEditLogOp`, `FSEditLogOpCodes`, and UTF-8 I/O wrappers.

Integration points: created by `OfflineEditsVisitorFactory` and driven by either binary or XML loaders.

Risks and test signals: tests should verify zero-count rows for all opcodes, count increments by opcode, error text on abnormal close, and stream closure. Because it exposes the mutable map, embedding code can mutate counts; tests should treat `getStatistics()` as a live view. Large logs should be low-memory because counts are per opcode, not per operation.
