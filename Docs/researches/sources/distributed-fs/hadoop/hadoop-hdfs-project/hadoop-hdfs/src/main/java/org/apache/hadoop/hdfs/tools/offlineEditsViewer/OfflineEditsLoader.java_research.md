## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsLoader.java

Purpose: `OfflineEditsLoader` defines the minimal loader abstraction for the offline edits viewer: load an edit-log representation and drive an `OfflineEditsVisitor`. Its nested factory selects XML or binary loading based on input format.

Important APIs and control flow: the interface exposes `loadEdits()`. `OfflineEditsLoaderFactory.createLoader(visitor, inputFileName, xmlInput, flags)` returns `OfflineEditsXmlLoader` for XML inputs. For binary inputs, it constructs an `EditLogFileInputStream` with invalid transaction-id bounds and wraps it in `OfflineEditsBinaryLoader`. The factory carefully closes the edit-log input stream if loader construction fails before ownership is transferred.

State, persistence, and dependencies: the interface has no state. The factory depends on `File`, `EditLogFileInputStream`, `EditLogInputStream`, and `HdfsServerConstants.INVALID_TXID`. Persistence is delegated to visitors and loaders.

Integration points: `OfflineEditsViewer.go` invokes this factory after selecting a processor/visitor. It is the indirection point that lets the same visitor consume XML or binary edits.

Risks and test signals: tests should assert that binary stream resources close on factory failure, that XML and binary paths choose the expected loader, and that invalid input names propagate `IOException`. The factory assumes the caller correctly determines `xmlInput`; `OfflineEditsViewer` currently uses a filename `.xml` suffix, so mislabeled files are parsed by the wrong loader.
