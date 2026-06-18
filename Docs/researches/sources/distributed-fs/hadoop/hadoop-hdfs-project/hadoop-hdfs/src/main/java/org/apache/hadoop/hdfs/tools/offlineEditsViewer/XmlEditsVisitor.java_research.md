## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/XmlEditsVisitor.java

Purpose: `XmlEditsVisitor` writes a parsed edit log as XML. It is the default `hdfs oev` processor and pairs with `OfflineEditsXmlLoader` for round-trip conversion.

Important APIs and control flow: the constructor creates a secure `SAXTransformerFactory`, configures XML output properties, binds a `TransformerHandler` to the supplied output stream, starts the document, and opens the top-level `EDITS` element. `start(int version)` emits `EDITS_VERSION`. `visitOp(FSEditLogOp op)` delegates operation-specific XML serialization to `op.outputToXml(contentHandler)`. `close(Throwable error)` closes the `EDITS` element, optionally emits an `ERROR` element through `XMLUtils.addSaxString`, ends the document, and closes the output stream.

State, persistence, and dependencies: state is the output stream, SAX content handler, and transformer factory. Dependencies include JAXP/SAX, Hadoop XML utilities, and NameNode edit-log operations.

Integration points: created by `OfflineEditsVisitorFactory` for `xml`; consumed by both binary and XML loaders, though `OfflineEditsViewer` prevents XML input to XML output through the CLI.

Risks and test signals: tests should verify well-formed XML on success and after error close, correct version emission, escaping of operation data, and stream closure. One subtle behavior is that the constructor starts output immediately, so errors before `start` still leave a partially opened XML document unless `close` is called.
