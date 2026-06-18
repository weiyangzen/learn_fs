## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsViewer.java

Purpose: `OfflineEditsViewer` is the `hdfs oev` command. It converts HDFS edit logs between binary, XML, and statistics formats, with optional screen echoing, transaction-id repair, and binary recovery.

Important APIs and control flow: `buildOptions()` defines required `-i` and `-o` options plus `-p`, `-v`, `-f`, `-r`, and help. `run(String[] argv)` handles no-arg/help cases, parses options, defaults the processor to `xml`, populates a `Flags` value object, and calls `go`. `go` rejects XML-to-XML and binary-to-binary conversions based on the input filename extension and requested processor, creates a visitor through `OfflineEditsVisitorFactory` when one is not supplied, builds an `OfflineEditsLoader`, and calls `loadEdits()`.

State, persistence, and dependencies: the tool is mostly stateless except for `Flags`. It writes output through the chosen visitor. Dependencies include Commons CLI, `ToolRunner`, `StringUtils`, the loader factory, and the visitor factory.

Integration points: used from Hadoop CLI via `ToolRunner`; tests can also call `go` directly with a custom visitor.

Risks and test signals: the extension-based XML detection is simple and should be tested with uppercase or misleading names. `-h` with other options returns `-1`; no args prints help and returns `0`. Conversion matrix tests should cover binary-to-XML, XML-to-binary, stats output, verbose tee output, `-fix-txids`, and recovery failures.
