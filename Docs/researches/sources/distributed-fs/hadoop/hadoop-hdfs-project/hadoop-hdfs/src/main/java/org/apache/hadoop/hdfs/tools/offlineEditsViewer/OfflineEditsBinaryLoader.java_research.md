## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsBinaryLoader.java

Purpose: `OfflineEditsBinaryLoader` reads a binary HDFS edit log from an `EditLogInputStream` and emits each decoded `FSEditLogOp` to an `OfflineEditsVisitor`. It is the binary-input half of the offline edits viewer.

Important APIs and control flow: the constructor captures the visitor, input stream, and `OfflineEditsViewer.Flags` for transaction-id repair and recovery mode. `loadEdits()` starts the visitor with `inputStream.getVersion(true)`, repeatedly calls `readOp()`, optionally rewrites transaction ids using `nextTxId`, and sends each operation to `visitor.visitOp`. EOF is represented by `readOp()` returning `null`. On `IOException` or `RuntimeException`, non-recovery mode closes the visitor with the error and rethrows. Recovery mode logs the failure and calls `inputStream.resync()` to skip corrupt bytes and continue.

State, persistence, and dependencies: mutable state is limited to `nextTxId` and the input stream position. It depends on NameNode edit-log input classes, SLF4J logging, and Hadoop `IOUtils` cleanup.

Integration points: instantiated by `OfflineEditsLoaderFactory` for non-XML inputs and normally created by `OfflineEditsViewer.go`.

Risks and test signals: test with valid logs, corrupt/truncated logs, recovery mode, and `-fix-txids`. Recovery mode can silently skip operations after logging; consumers need tests that verify resync behavior and final visitor close. `nextTxId` initialization from the first positive input transaction id means invalid leading ids start at 1.
