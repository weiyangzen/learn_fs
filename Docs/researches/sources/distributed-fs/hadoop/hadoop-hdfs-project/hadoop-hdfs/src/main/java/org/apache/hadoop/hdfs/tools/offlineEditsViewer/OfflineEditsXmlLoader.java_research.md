## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsXmlLoader.java

Purpose: `OfflineEditsXmlLoader` parses XML produced by the offline edits viewer and reconstructs `FSEditLogOp` instances for a visitor, enabling XML-to-binary conversion and XML-to-stats processing.

Important APIs and control flow: the class extends SAX `DefaultHandler` and implements `OfflineEditsLoader`. `loadEdits()` creates a secure `XMLReader`, disables DTD and external entity features, parses the UTF-8 file, and closes the visitor. SAX callbacks implement a finite-state parser: `EXPECT_EDITS_TAG`, `EXPECT_VERSION`, `EXPECT_RECORD`, `EXPECT_OPCODE`, `EXPECT_DATA`, `HANDLE_DATA`, and `EXPECT_END`. Nested XML data is accumulated into `XMLUtils.Stanza` trees, decoded via `FSEditLogOp.decodeXml`, optionally transaction-id-fixed, and delivered to `visitor.visitOp`.

State, persistence, and dependencies: mutable parser state includes `state`, current `stanza`, `stanzaStack`, current opcode, character buffer, and `nextTxId`. It depends on HDFS XML utilities, `FSEditLogOpCodes`, `OpInstanceCache`, and SAX.

Integration points: selected by `OfflineEditsLoaderFactory` for XML inputs. It shares the `-fix-txids` behavior with `OfflineEditsBinaryLoader`.

Risks and test signals: tests should cover malformed tag ordering, bad opcodes, nested stanza decoding, UTF-8 input, parser security features, and transaction-id repair. SAX forces `IOException` from visitors to be wrapped as `RuntimeException`, so error tests should assert visitor close behavior and exception propagation.
