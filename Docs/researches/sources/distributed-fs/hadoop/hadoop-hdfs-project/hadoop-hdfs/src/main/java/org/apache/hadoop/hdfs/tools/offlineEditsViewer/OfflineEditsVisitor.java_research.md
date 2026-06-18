## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitor.java

Purpose: `OfflineEditsVisitor` is the sink interface for edit-log processing. Loaders parse input formats and call this interface to produce XML, binary edit logs, or statistics.

Important APIs and control flow: `start(int version)` announces the edit-log layout version before records are delivered. `visitOp(FSEditLogOp op)` is called once per decoded operation. `close(Throwable error)` lets implementations finalize output and optionally include error information when parsing failed. The interface does not prescribe ordering beyond the loader contract, but current loaders call `start`, zero or more `visitOp`, then `close`.

State, persistence, and dependencies: the interface has no state. Implementations own output streams, counters, or edit-log writers. It depends only on `FSEditLogOp` and `IOException`.

Integration points: implemented by `BinaryEditsVisitor`, `XmlEditsVisitor`, and `StatisticsEditsVisitor`; consumed by `OfflineEditsBinaryLoader` and `OfflineEditsXmlLoader`; created by `OfflineEditsVisitorFactory`.

Risks and test signals: visitor implementations must be robust to `close(error)` after partial output. Loader tests should verify `close(null)` on success and `close(error)` on parse failures. Because `visitOp` exposes mutable `FSEditLogOp` objects that loaders may modify for transaction-id repair, implementations should not retain and mutate operations after returning unless explicitly tested.
