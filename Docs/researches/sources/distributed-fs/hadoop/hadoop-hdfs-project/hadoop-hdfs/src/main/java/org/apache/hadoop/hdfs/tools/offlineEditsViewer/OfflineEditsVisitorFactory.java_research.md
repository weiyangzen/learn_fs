## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitorFactory.java

Purpose: `OfflineEditsVisitorFactory` maps a processor name to the concrete `OfflineEditsVisitor` that writes the requested output format.

Important APIs and control flow: `getEditsVisitor(filename, processor, printToScreen)` special-cases `binary` to return `BinaryEditsVisitor`. For text-like processors it opens the output file via `Files.newOutputStream`, optionally wraps it and `System.out` in a `TeeOutputStream`, then constructs `XmlEditsVisitor` for `xml` or `StatisticsEditsVisitor` for `stats`. Unknown processors throw an `IOException` listing valid values. The method nulls local stream references after successful visitor construction so the returned visitor owns the stream.

State, persistence, and dependencies: persistence is the output file. Dependencies include NIO file streams, `TeeOutputStream`, Hadoop `IOUtils`, and case-insensitive `StringUtils`.

Integration points: called by `OfflineEditsViewer.go` unless a caller supplies a custom visitor directly. It centralizes supported processor names used by command-line help.

Risks and test signals: tests should verify stream ownership: on constructor failure, streams close; on success, visitors close them. `printToScreen` should duplicate XML/stats output but not binary output. Unknown processor tests should cover casing and message content. One behavioral risk is that closing a `TeeOutputStream` closes `System.out`, which can affect long-lived embedding contexts.
