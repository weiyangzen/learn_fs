# subset-b-007511 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/StoragePolicyAdmin.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/StoragePolicyAdmin.java

Purpose: `StoragePolicyAdmin` is the `hdfs storagepolicies` command implementation. It extends `Configured` and implements `Tool`, dispatching dash-prefixed subcommands through `AdminHelper.Command` instances. The user-facing operations are listing all block storage policies, getting the policy for one path, setting a policy, unsetting a policy, and scheduling `satisfyStoragePolicy`.

Important APIs and control flow: `main` runs the tool with a fresh `Configuration`; `run` validates a subcommand, strips it from the argument list, and delegates to one of the private command classes. `ListStoragePoliciesCommand` calls `FileSystem.get(conf).getAllStoragePolicies()`. `GetStoragePolicyCommand` resolves a path-specific filesystem, obtains `FileStatus`, checks for `HdfsFileStatus`, maps the storage policy id to a `BlockStoragePolicy`, and reports unsupported filesystems. `SetStoragePolicyCommand`, `UnsetStoragePolicyCommand`, and `SatisfyStoragePolicyCommand` call the corresponding `FileSystem` APIs.

State, persistence, and dependencies: the class itself is stateless; persistence happens only through HDFS NameNode RPCs behind `FileSystem`. Dependencies include `BlockStoragePolicySpi`, HDFS protocol types, `Path`, `FileStatus`, `TableListing`, and `StringUtils` option parsing.

Integration points: this is a command-line adapter over HDFS storage-policy APIs and follows the same `AdminHelper` conventions as other HDFS admin tools. Exit codes distinguish usage errors (`1`) from remote/API failures (`2`) and command-dispatch exceptions (`-1`).

Risks and test signals: tests should cover missing options, non-HDFS paths, nonexistent paths, unspecified policies, and each RPC-backed command. A key compatibility risk is assuming policy ids from `HdfsFileStatus` can be resolved by scanning `fs.getAllStoragePolicies()`; unsupported or proxy filesystems should produce the documented error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/StoragePolicyAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/BinaryEditsVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/BinaryEditsVisitor.java

Purpose: `BinaryEditsVisitor` is an `OfflineEditsVisitor` implementation that writes visited edit-log operations back out in native Hadoop binary edit-log format. It is used when converting XML edits into binary or copying binary edits through the offline edits viewer pipeline.

Important APIs and control flow: the constructor creates an `EditLogFileOutputStream` for the destination file and initializes it with `NameNodeLayoutVersion.CURRENT_LAYOUT_VERSION`. `start(int version)` is a no-op because the output stream was already created with the current layout. `visitOp(FSEditLogOp op)` serializes each operation by calling `elfos.write(op)`. `close(Throwable error)` marks the stream ready to flush, performs `flushAndSync(true)`, and closes the stream regardless of whether the close was normal or error-driven.

State, persistence, and dependencies: the only durable state is the output edit-log file managed by `EditLogFileOutputStream`. The visitor depends on NameNode edit-log serialization classes and `Configuration`; it does not interpret operation payloads itself.

Integration points: produced by `OfflineEditsVisitorFactory` for processor `binary` and driven by `OfflineEditsBinaryLoader` or `OfflineEditsXmlLoader` through the `OfflineEditsVisitor` contract.

Risks and test signals: tests should verify that output is created, flushed, and readable as an edit log. Important edge cases are error closes, operations whose transaction ids were rewritten by a loader, and cross-version behavior because this writer always emits the current layout version rather than the input version passed to `start`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/BinaryEditsVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsBinaryLoader.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsBinaryLoader.java

Purpose: `OfflineEditsBinaryLoader` reads a binary HDFS edit log from an `EditLogInputStream` and emits each decoded `FSEditLogOp` to an `OfflineEditsVisitor`. It is the binary-input half of the offline edits viewer.

Important APIs and control flow: the constructor captures the visitor, input stream, and `OfflineEditsViewer.Flags` for transaction-id repair and recovery mode. `loadEdits()` starts the visitor with `inputStream.getVersion(true)`, repeatedly calls `readOp()`, optionally rewrites transaction ids using `nextTxId`, and sends each operation to `visitor.visitOp`. EOF is represented by `readOp()` returning `null`. On `IOException` or `RuntimeException`, non-recovery mode closes the visitor with the error and rethrows. Recovery mode logs the failure and calls `inputStream.resync()` to skip corrupt bytes and continue.

State, persistence, and dependencies: mutable state is limited to `nextTxId` and the input stream position. It depends on NameNode edit-log input classes, SLF4J logging, and Hadoop `IOUtils` cleanup.

Integration points: instantiated by `OfflineEditsLoaderFactory` for non-XML inputs and normally created by `OfflineEditsViewer.go`.

Risks and test signals: test with valid logs, corrupt/truncated logs, recovery mode, and `-fix-txids`. Recovery mode can silently skip operations after logging; consumers need tests that verify resync behavior and final visitor close. `nextTxId` initialization from the first positive input transaction id means invalid leading ids start at 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsBinaryLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsLoader.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsLoader.java

Purpose: `OfflineEditsLoader` defines the minimal loader abstraction for the offline edits viewer: load an edit-log representation and drive an `OfflineEditsVisitor`. Its nested factory selects XML or binary loading based on input format.

Important APIs and control flow: the interface exposes `loadEdits()`. `OfflineEditsLoaderFactory.createLoader(visitor, inputFileName, xmlInput, flags)` returns `OfflineEditsXmlLoader` for XML inputs. For binary inputs, it constructs an `EditLogFileInputStream` with invalid transaction-id bounds and wraps it in `OfflineEditsBinaryLoader`. The factory carefully closes the edit-log input stream if loader construction fails before ownership is transferred.

State, persistence, and dependencies: the interface has no state. The factory depends on `File`, `EditLogFileInputStream`, `EditLogInputStream`, and `HdfsServerConstants.INVALID_TXID`. Persistence is delegated to visitors and loaders.

Integration points: `OfflineEditsViewer.go` invokes this factory after selecting a processor/visitor. It is the indirection point that lets the same visitor consume XML or binary edits.

Risks and test signals: tests should assert that binary stream resources close on factory failure, that XML and binary paths choose the expected loader, and that invalid input names propagate `IOException`. The factory assumes the caller correctly determines `xmlInput`; `OfflineEditsViewer` currently uses a filename `.xml` suffix, so mislabeled files are parsed by the wrong loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsViewer.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsViewer.java

Purpose: `OfflineEditsViewer` is the `hdfs oev` command. It converts HDFS edit logs between binary, XML, and statistics formats, with optional screen echoing, transaction-id repair, and binary recovery.

Important APIs and control flow: `buildOptions()` defines required `-i` and `-o` options plus `-p`, `-v`, `-f`, `-r`, and help. `run(String[] argv)` handles no-arg/help cases, parses options, defaults the processor to `xml`, populates a `Flags` value object, and calls `go`. `go` rejects XML-to-XML and binary-to-binary conversions based on the input filename extension and requested processor, creates a visitor through `OfflineEditsVisitorFactory` when one is not supplied, builds an `OfflineEditsLoader`, and calls `loadEdits()`.

State, persistence, and dependencies: the tool is mostly stateless except for `Flags`. It writes output through the chosen visitor. Dependencies include Commons CLI, `ToolRunner`, `StringUtils`, the loader factory, and the visitor factory.

Integration points: used from Hadoop CLI via `ToolRunner`; tests can also call `go` directly with a custom visitor.

Risks and test signals: the extension-based XML detection is simple and should be tested with uppercase or misleading names. `-h` with other options returns `-1`; no args prints help and returns `0`. Conversion matrix tests should cover binary-to-XML, XML-to-binary, stats output, verbose tee output, `-fix-txids`, and recovery failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsViewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitor.java

Purpose: `OfflineEditsVisitor` is the sink interface for edit-log processing. Loaders parse input formats and call this interface to produce XML, binary edit logs, or statistics.

Important APIs and control flow: `start(int version)` announces the edit-log layout version before records are delivered. `visitOp(FSEditLogOp op)` is called once per decoded operation. `close(Throwable error)` lets implementations finalize output and optionally include error information when parsing failed. The interface does not prescribe ordering beyond the loader contract, but current loaders call `start`, zero or more `visitOp`, then `close`.

State, persistence, and dependencies: the interface has no state. Implementations own output streams, counters, or edit-log writers. It depends only on `FSEditLogOp` and `IOException`.

Integration points: implemented by `BinaryEditsVisitor`, `XmlEditsVisitor`, and `StatisticsEditsVisitor`; consumed by `OfflineEditsBinaryLoader` and `OfflineEditsXmlLoader`; created by `OfflineEditsVisitorFactory`.

Risks and test signals: visitor implementations must be robust to `close(error)` after partial output. Loader tests should verify `close(null)` on success and `close(error)` on parse failures. Because `visitOp` exposes mutable `FSEditLogOp` objects that loaders may modify for transaction-id repair, implementations should not retain and mutate operations after returning unless explicitly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitorFactory.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitorFactory.java

Purpose: `OfflineEditsVisitorFactory` maps a processor name to the concrete `OfflineEditsVisitor` that writes the requested output format.

Important APIs and control flow: `getEditsVisitor(filename, processor, printToScreen)` special-cases `binary` to return `BinaryEditsVisitor`. For text-like processors it opens the output file via `Files.newOutputStream`, optionally wraps it and `System.out` in a `TeeOutputStream`, then constructs `XmlEditsVisitor` for `xml` or `StatisticsEditsVisitor` for `stats`. Unknown processors throw an `IOException` listing valid values. The method nulls local stream references after successful visitor construction so the returned visitor owns the stream.

State, persistence, and dependencies: persistence is the output file. Dependencies include NIO file streams, `TeeOutputStream`, Hadoop `IOUtils`, and case-insensitive `StringUtils`.

Integration points: called by `OfflineEditsViewer.go` unless a caller supplies a custom visitor directly. It centralizes supported processor names used by command-line help.

Risks and test signals: tests should verify stream ownership: on constructor failure, streams close; on success, visitors close them. `printToScreen` should duplicate XML/stats output but not binary output. Unknown processor tests should cover casing and message content. One behavioral risk is that closing a `TeeOutputStream` closes `System.out`, which can affect long-lived embedding contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsVisitorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsXmlLoader.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsXmlLoader.java

Purpose: `OfflineEditsXmlLoader` parses XML produced by the offline edits viewer and reconstructs `FSEditLogOp` instances for a visitor, enabling XML-to-binary conversion and XML-to-stats processing.

Important APIs and control flow: the class extends SAX `DefaultHandler` and implements `OfflineEditsLoader`. `loadEdits()` creates a secure `XMLReader`, disables DTD and external entity features, parses the UTF-8 file, and closes the visitor. SAX callbacks implement a finite-state parser: `EXPECT_EDITS_TAG`, `EXPECT_VERSION`, `EXPECT_RECORD`, `EXPECT_OPCODE`, `EXPECT_DATA`, `HANDLE_DATA`, and `EXPECT_END`. Nested XML data is accumulated into `XMLUtils.Stanza` trees, decoded via `FSEditLogOp.decodeXml`, optionally transaction-id-fixed, and delivered to `visitor.visitOp`.

State, persistence, and dependencies: mutable parser state includes `state`, current `stanza`, `stanzaStack`, current opcode, character buffer, and `nextTxId`. It depends on HDFS XML utilities, `FSEditLogOpCodes`, `OpInstanceCache`, and SAX.

Integration points: selected by `OfflineEditsLoaderFactory` for XML inputs. It shares the `-fix-txids` behavior with `OfflineEditsBinaryLoader`.

Risks and test signals: tests should cover malformed tag ordering, bad opcodes, nested stanza decoding, UTF-8 input, parser security features, and transaction-id repair. SAX forces `IOException` from visitors to be wrapped as `RuntimeException`, so error tests should assert visitor close behavior and exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/OfflineEditsXmlLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/StatisticsEditsVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/StatisticsEditsVisitor.java

Purpose: `StatisticsEditsVisitor` counts edit-log operation opcodes and writes a human-readable summary. It is the implementation behind `hdfs oev -p stats`.

Important APIs and control flow: the constructor wraps the supplied `OutputStream` in a UTF-8 `PrintWriter`. `start(int version)` records the log version. `visitOp(FSEditLogOp op)` increments a `Map<FSEditLogOpCodes, Long>` keyed by `op.opCode`. `close(Throwable error)` writes `getStatisticsString()`, appends an error marker if supplied, and closes the writer. `getStatistics()` exposes the live count map for tests or embedding; `getStatisticsString()` emits version plus every known opcode, defaulting missing counts to zero.

State, persistence, and dependencies: state is the version and opcode-count map. Output persistence is the stream provided by the factory. Dependencies include `FSEditLogOp`, `FSEditLogOpCodes`, and UTF-8 I/O wrappers.

Integration points: created by `OfflineEditsVisitorFactory` and driven by either binary or XML loaders.

Risks and test signals: tests should verify zero-count rows for all opcodes, count increments by opcode, error text on abnormal close, and stream closure. Because it exposes the mutable map, embedding code can mutate counts; tests should treat `getStatistics()` as a live view. Large logs should be low-memory because counts are per opcode, not per operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/StatisticsEditsVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TeeOutputStream.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TeeOutputStream.java

Purpose: `TeeOutputStream` is a small `OutputStream` adapter that duplicates writes, flushes, and closes to multiple underlying streams. It supports verbose offline edits output to both a file and the console.

Important APIs and control flow: the constructor stores an `OutputStream[]`. `write(int)`, `write(byte[])`, and `write(byte[], int, int)` iterate in array order and forward the call to each stream. `flush()` and `close()` similarly forward to each stream.

State, persistence, and dependencies: state is just the array reference. The output side effects are entirely determined by the wrapped streams. There are no Hadoop dependencies in this class.

Integration points: `OfflineEditsVisitorFactory` uses it when `printToScreen` is true for XML or stats processors, pairing a file stream with `System.out`.

Risks and test signals: tests should cover forwarding for all write overloads and flushing. Failure semantics are simple but important: if an earlier stream throws, later streams are not called. Closing also closes every wrapped stream, including `System.out` in current usage; embedding tests should detect whether this is acceptable. The class does not guard against null entries or concurrent writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TeeOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/XmlEditsVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/XmlEditsVisitor.java

Purpose: `XmlEditsVisitor` writes a parsed edit log as XML. It is the default `hdfs oev` processor and pairs with `OfflineEditsXmlLoader` for round-trip conversion.

Important APIs and control flow: the constructor creates a secure `SAXTransformerFactory`, configures XML output properties, binds a `TransformerHandler` to the supplied output stream, starts the document, and opens the top-level `EDITS` element. `start(int version)` emits `EDITS_VERSION`. `visitOp(FSEditLogOp op)` delegates operation-specific XML serialization to `op.outputToXml(contentHandler)`. `close(Throwable error)` closes the `EDITS` element, optionally emits an `ERROR` element through `XMLUtils.addSaxString`, ends the document, and closes the output stream.

State, persistence, and dependencies: state is the output stream, SAX content handler, and transformer factory. Dependencies include JAXP/SAX, Hadoop XML utilities, and NameNode edit-log operations.

Integration points: created by `OfflineEditsVisitorFactory` for `xml`; consumed by both binary and XML loaders, though `OfflineEditsViewer` prevents XML input to XML output through the CLI.

Risks and test signals: tests should verify well-formed XML on success and after error close, correct version emission, escaping of operation data, and stream closure. One subtle behavior is that the constructor starts output immediately, so errors before `start` still leave a partially opened XML document unless `close` is called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/XmlEditsVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DelimitedImageVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DelimitedImageVisitor.java

Purpose: `DelimitedImageVisitor` is a legacy `ImageVisitor` implementation that writes one delimiter-separated row per inode or inode-under-construction. It captures common inode fields for spreadsheet or script analysis.

Important APIs and control flow: constructors default to tab delimiter unless a custom delimiter is supplied. An initializer defines the ordered tracked columns: path, replication, modification/access time, block size, block count, byte count, quotas, permission string, user, and group. `visit` records tracked scalar elements and sums `NUM_BYTES` values to compute file size. `visitEnclosingElement` pushes element context and handles `BLOCKS` attributes for block count. `leaveEnclosingElement` pops context; when an inode closes, it writes the ordered row, newline, and resets the per-inode map.

State, persistence, and dependencies: state includes an element stack, tracked field map, delimiter, and rolling `fileSize`. Output is managed by `TextWriterImageVisitor`.

Integration points: selected by legacy `OfflineImageViewer` processor `Delimited`. It depends on `ImageLoaderCurrent` emitting block byte events unless blocks are skipped; the CLI forces `skipBlocks=false` for this processor.

Risks and test signals: tests should cover root path normalization, custom delimiters, missing version-dependent fields, directory rows, and file-size summation across blocks. Since values are not escaped, delimiters embedded in names or metadata can make ambiguous rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DelimitedImageVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DepthCounter.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DepthCounter.java

Purpose: `DepthCounter` is a utility for visitor implementations that need to track nesting depth while traversing a structured image or edit representation.

Important APIs and control flow: `incLevel()` increments the internal depth, `decLevel()` decrements only when depth is at least one, and `getLevel()` returns the current integer. The guard in `decLevel()` prevents negative indentation after mismatched close calls.

State, persistence, and dependencies: state is a single integer field. There is no persistence and no runtime dependency beyond Hadoop classification annotations.

Integration points: `IndentedImageVisitor` uses it to decide how much indentation to print for each visited element. The class is generic enough for other visitor-style tools, but in this subset it is only a presentation helper.

Risks and test signals: unit tests should verify initial zero depth, normal increment/decrement behavior, and repeated decrement at zero. It is not thread-safe, but image visitors are single-threaded in the legacy pipeline. Because underflow is silently ignored, tests for higher-level visitors should detect missing or extra `leaveEnclosingElement` calls rather than relying on this class to fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DepthCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageHandler.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageHandler.java

Purpose: `FSImageHandler` is the Netty HTTP handler that exposes a read-only subset of WebHDFS against an offline protobuf fsimage loaded by `FSImageLoader`.

Important APIs and control flow: `channelActive` registers channels with a `ChannelGroup`. `channelRead0` accepts only HTTP GET, parses the URI with `QueryStringDecoder`, validates that the path starts with the WebHDFS prefix, uppercases the `op` parameter, and dispatches to `FSImageLoader` methods for `GETFILESTATUS`, `LISTSTATUS`, `GETACLSTATUS`, `GETXATTRS`, `LISTXATTRS`, and `GETCONTENTSUMMARY`. Responses are JSON UTF-8 with `Content-Length` and connection close. `exceptionCaught` converts exceptions to JSON and maps argument errors to 400, missing paths to 404, IO errors to 403, and other failures to 500.

State, persistence, and dependencies: state is the shared immutable-ish `FSImageLoader` and active channel group. Dependencies are Netty HTTP classes, WebHDFS constants, `JsonUtil`, and Hadoop string utilities.

Integration points: instantiated by `WebImageViewer` for `OfflineImageViewerPB -p Web`.

Risks and test signals: tests should cover method rejection, missing/invalid `op`, path-prefix validation, xattr query parameters, exception-to-status mapping, and JSON response bodies. Security scope is intentionally local/offline; no authentication or HTTPS is provided. Large responses are materialized as a full string before being wrapped in a `ByteBuf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageLoader.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageLoader.java

Purpose: `FSImageLoader` loads protobuf fsimage sections into memory and provides JSON-producing namespace query methods used by the Web processor.

Important APIs and control flow: `load(inputFile)` checks the fsimage magic, loads the `FileSummary`, sorts sections by `SectionName`, and reads `STRING_TABLE`, `INODE`, `INODE_REFERENCE`, and `INODE_DIR`. Inodes are stored as serialized byte arrays sorted by id; directories map parent inode id to child ids, resolving reference children through the reference section. Query methods resolve paths via `lookup`, binary-search inodes via `fromINodeId`, and format WebHDFS-compatible JSON for file status, listings, content summaries, xattrs, and ACLs.

State, persistence, and dependencies: persistent input is the fsimage file; runtime state is `stringTable`, sorted `inodes`, and `dirmap`. It depends on fsimage protobuf classes, `FSImageUtil`, `FSImageFormatPBINode.Loader`, `JsonUtil`, ACL/XAttr types, and Guava-like Hadoop third-party collections.

Integration points: `FSImageHandler` calls these methods for offline WebHDFS. `FileDistributionCalculator` independently reads protobuf image sections and does not use this loader.

Risks and test signals: tests should cover path lookup, root and empty directories, symlinks, erasure-coded files, xattr filtering and not-found errors, ACL loading, recursive content summaries, and reference children. `fromINodeId` returns `null` when missing, so callers can throw later `NullPointerException`; corrupted images should have explicit tests. Memory use scales with all inode byte arrays and directory maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionCalculator.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionCalculator.java

Purpose: `FileDistributionCalculator` computes file-size distribution directly from a protobuf fsimage without using the legacy visitor pipeline. It backs `OfflineImageViewerPB -p FileDistribution`.

Important APIs and control flow: the constructor applies defaults for max size and interval, validates the number of buckets against `MAX_INTERVALS`, and allocates an integer distribution array. `visit(RandomAccessFile)` validates fsimage format, loads the summary, seeks to the `INODE` section, wraps it for compression and length limiting, then calls `run` and `output`. `run` parses the inode-section header and each delimited inode, counting files, directories, blocks, total replicated space, max file size, and bucket counts based on summed block bytes. `output` writes either raw byte bucket starts or human-readable ranges plus totals.

State, persistence, and dependencies: state is counters and the distribution array. Dependencies include protobuf fsimage classes, `FSImageUtil`, `LimitInputStream`, `BlockProto`, `StringUtils.byteDesc`, and `Configuration`.

Integration points: selected by `OfflineImageViewerPB` and writes to the command output stream.

Risks and test signals: tests should cover default values, bucket boundaries, files larger than max size, max-size not divisible by step, compressed images, empty images, and OOM-prevention validation. The progress message every 1,048,576 inodes goes to the same output stream and may affect machine parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionCalculator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionVisitor.java

Purpose: `FileDistributionVisitor` is the legacy visitor-based file-size distribution processor for pre-PB/offline image traversal.

Important APIs and control flow: the constructor applies default max size and step, validates interval count against `Integer.MAX_VALUE`, and initializes counters. `visitEnclosingElement` tracks nesting, starts a `FileContext` for each inode, and reads the block count from `BLOCKS` attributes. `visit` fills current path, replication, and cumulative byte size while inside an inode. `leaveEnclosingElement` finalizes inode accounting: negative block count means directory, otherwise it increments file counters, computes replicated space, updates max size, and increments the correct bucket. `finish` and `finishAbnormally` both output distribution data before closing.

State, persistence, and dependencies: mutable state is the element stack, current inode context, distribution array, counters, max size, step, and format flag. Output is through `TextWriterImageVisitor`, while totals are printed to `System.out`.

Integration points: selected by legacy `OfflineImageViewer -p FileDistribution` and driven by `ImageLoaderCurrent`.

Risks and test signals: tests should cover directories, files under construction, block count attributes, zero-length files, bucket boundary behavior, formatted output, and abnormal finish. Unlike the PB calculator, summary totals are sent to stdout rather than the output file, which is a compatibility quirk worth regression-testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IgnoreSnapshotException.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IgnoreSnapshotException.java

Purpose: `IgnoreSnapshotException` is a marker `IOException` used by offline image viewer components to signal intentionally ignored snapshot data.

Important APIs and control flow: the class has only a no-argument constructor and no additional fields or methods. Its value is its type identity, allowing callers to catch it separately from other `IOException` failures.

State, persistence, and dependencies: it has no state, persistence behavior, or non-JDK dependencies.

Integration points: it belongs to the offline image viewer package and is intended for code paths that choose to skip snapshot processing. In this subset, `ImageLoaderCurrent` handles snapshot structures directly and does not throw this exception.

Risks and test signals: tests should only need to verify catch behavior where other components use the marker. Because the exception carries no message or cause, diagnostic quality depends on the catch site. Future code using it should document whether ignoring snapshots is a normal mode or a degraded result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IgnoreSnapshotException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoader.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoader.java

Purpose: `ImageLoader` is the legacy binary fsimage parser abstraction. Implementations accept a `DataInputStream`, traverse an image, and emit structural events to an `ImageVisitor`.

Important APIs and control flow: `loadImage(DataInputStream, ImageVisitor, boolean enumerateBlocks)` parses an image and controls whether individual file blocks are visited. `canLoadVersion(int)` declares supported layout versions. The nested `LoaderFactory.getLoader(version)` currently tries a single `ImageLoaderCurrent` instance and returns it if `canLoadVersion` matches; otherwise it returns `null`.

State, persistence, and dependencies: the interface itself has no state. Implementations own parser state and do not persist output directly; visitors do. It depends on `DataInputStream`, `IOException`, and Hadoop classification annotations.

Integration points: legacy `OfflineImageViewer.go()` reads the image version, asks this factory for a loader, and invokes `loadImage`.

Risks and test signals: adding support for a new layout version requires updating or adding loaders in the factory. Tests should verify unsupported versions return `null` and callers handle that path. Since the factory creates a new loader each call, implementation state is not shared across viewer runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoaderCurrent.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoaderCurrent.java

Purpose: `ImageLoaderCurrent` is the legacy binary fsimage parser for layout versions `-16` through `-51`. It decodes the non-protobuf fsimage format and emits `ImageVisitor` events for metadata, inodes, snapshots, blocks, permissions, delegation tokens, and cache state.

Important APIs and control flow: `canLoadVersion` checks a static version array. `loadImage` starts the visitor, reads the layout version and optional layout flags, emits namespace metadata, conditionally reads sequential block id, transaction id, inode id, snapshot counters, and compression metadata, then wraps the stream if compressed. It delegates to `processINodes`, clears snapshot reference tracking maps, processes under-construction inodes, delegation tokens, and cache manager state, then closes the top-level element and calls `finish` or `finishAbnormally`.

State, persistence, and dependencies: parser state includes `imageVersion`, `subtreeMap` for referenced snapshot subtrees, `dirNodeMap` for directory id to path, and a date formatter. It reads persistent fsimage bytes but writes only visitor output. Dependencies include NameNode layout feature flags, `FSImageSerialization`, compression codecs, `DelegationTokenIdentifier`, `DelegationKey`, permissions, and HDFS constants.

Integration points: selected by `ImageLoader.LoaderFactory` and driven by legacy `OfflineImageViewer`.

Risks and test signals: this file is highly layout-sensitive. Tests should cover each feature gate, compressed images, block skipping, local-name versus full-path layouts, snapshot diffs and references, symlinks, directories, files under construction, delegation tokens, and cache state. Skipping blocks uses a fixed 24 bytes per block assumption; layout changes around block serialization must be guarded by compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoaderCurrent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageVisitor.java

Purpose: `ImageVisitor` is the legacy visitor contract for fsimage traversal. Loaders emit structural `ImageElement` events, and concrete visitors transform those events into text, XML, statistics, or other views.

Important APIs and control flow: `ImageElement` enumerates all recognized fsimage fields and structural containers, including namespace metadata, inode fields, block fields, under-construction files, delegation tokens, snapshot metadata, and cache entries. Abstract lifecycle methods are `start`, `finish`, and `finishAbnormally`. Leaf values are delivered with `visit(ImageElement, String)` plus numeric convenience overloads. Containers are opened with `visitEnclosingElement`, optionally with a key/value attribute, and closed with `leaveEnclosingElement`.

State, persistence, and dependencies: the base class has no state or persistence. Implementations maintain traversal stacks and output writers.

Integration points: `ImageLoaderCurrent` drives this contract. Visitors in this subset include delimited, indented, ls, name distribution, and file distribution renderers; `XmlImageVisitor` and `TextWriterImageVisitor` are adjacent package dependencies.

Risks and test signals: contract correctness depends on balanced open/close events and consistent element meanings across layout versions. Tests should use small synthetic traversal sequences to validate each visitor, plus loader integration tests that assert expected event order for representative images. Adding new fsimage fields requires extending the enum and deciding how each visitor handles them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IndentedImageVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IndentedImageVisitor.java

Purpose: `IndentedImageVisitor` writes a tree-like text dump of legacy fsimage traversal events with indentation for nested structures.

Important APIs and control flow: constructors delegate to `TextWriterImageVisitor`. `visit` prints the current indentation followed by `ELEMENT = value`. The `long` overload formats delegation-token date fields as `Date.toString()` and otherwise prints the number. `visitEnclosingElement` prints the container name, optionally with a bracketed key/value pair, and increments depth. `leaveEnclosingElement` decrements depth. `finishAbnormally` prints a console warning before closing through the superclass.

State, persistence, and dependencies: state is a `DepthCounter` and a static cache of indent strings for shallow depths. Output is handled by `TextWriterImageVisitor`. Dependencies include `Date`.

Integration points: selected by legacy `OfflineImageViewer -p Indented` and driven by `ImageLoaderCurrent`.

Risks and test signals: tests should verify indentation, deep nesting fallback, date formatting for delegation token fields, and balanced depth. Output uses platform/default `Date.toString()` timezone representation, which can make exact-string tests environment-sensitive. The visitor is diagnostic, so it intentionally preserves event order rather than sorting or normalizing records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IndentedImageVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/LsImageVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/LsImageVisitor.java

Purpose: `LsImageVisitor` renders legacy fsimage inode entries in a format similar to `hdfs dfs -lsr`, including type marker, permissions, replication, owner/group, size, modification time, and path.

Important APIs and control flow: `newLine` resets per-inode fields and marks `inInode`. `visitEnclosingElement` starts a new line for `INODE` and records `BLOCKS` count attributes. `visit` records path, permission string, replication, owner, group, block byte totals, modification time, and symlink target while inside an inode. `leaveEnclosingElement` prints the formatted row when an `INODE` closes. Directories are identified by negative block count and get a `d` prefix; files get `-`; symlinks append ` -> target`.

State, persistence, and dependencies: per-inode state is stored in primitive/string fields, with a context stack and reusable `StringBuilder`/`Formatter`. Output is through `TextWriterImageVisitor`.

Integration points: default legacy `OfflineImageViewer` processor. The CLI forces block enumeration for this visitor because file sizes are computed by summing `NUM_BYTES`.

Risks and test signals: tests should cover root path, directories, files, symlinks, under-replication display fallback, missing optional fields, and ordering differences from live `lsr`. Exact formatting widths are part of compatibility. Because entries are fsimage order, tests must not assume lexicographic sort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/LsImageVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/NameDistributionVisitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/NameDistributionVisitor.java

Purpose: `NameDistributionVisitor` analyzes basename reuse in a legacy fsimage and estimates heap savings if repeated file-name byte arrays were reused.

Important APIs and control flow: `visit` watches for `INODE_PATH`, extracts the substring after the last slash, and increments a `HashMap<String, Integer>`. It ignores container events. `finish` writes the number of unique names, buckets names by frequency thresholds from 100000 down to 2, estimates saved bytes as `(24 + name.length()) * (count - 1)`, emits per-bucket summaries, then closes through the superclass.

State, persistence, and dependencies: state is the `counts` map. Output is handled by `TextWriterImageVisitor`. It depends only on basic collections and Hadoop classification annotations.

Integration points: selected by legacy `OfflineImageViewer -p NameDistribution` and driven by `ImageLoaderCurrent`.

Risks and test signals: tests should include root path, repeated basenames in different directories, names with no slash, and bucket-boundary frequencies. The byte-savings estimate uses Java `String.length()` and a fixed byte-array overhead, so it is approximate and JVM-dependent. Very large namespaces can make the `HashMap` memory-heavy because every unique basename is retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/NameDistributionVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageReconstructor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageReconstructor.java

Purpose: `OfflineImageReconstructor` is the ReverseXML implementation for protobuf fsimages. It reads XML produced by the PB image writer and writes a binary fsimage plus `.md5`.

Important APIs and control flow: `run(inputPath, outputPath)` deletes stale output, opens UTF-8 XML input and a digesting counted output stream, calls `processXml`, then saves the MD5. The constructor creates a secure StAX reader and registers `SectionProcessor` handlers for Name, ErasureCoding, INode, SecretManager, CacheManager, SnapshotDiff, INodeReference, INodeDirectory, FilesUnderConstruction, and Snapshot sections. `processXml` validates `<version>`, writes the magic header, processes each required section once, writes the generated string table after other sections, then writes `FileSummary` and its length.

State, persistence, and dependencies: state includes output byte count, section offsets, `FileSummary.Builder`, a generated string table, latest string id, and a date parser. Dependencies include fsimage protobufs, `PBImageXmlWriter` tag constants, StAX, MD5 utilities, ACL/XAttr encoding masks, and protobuf builders.

Integration points: called by `OfflineImageViewerPB` for processor `ReverseXML`; it is the inverse of PB XML output.

Risks and test signals: round-trip XML-to-image tests should cover every section, ACLs, xattrs, erasure coding, snapshots, cache manager data, string-table limits, layout-version mismatch, unknown/duplicate sections, and MD5 generation. A concrete code risk is in `CacheManagerSectionProcessor`: it loads per-pool/per-directive nodes but calls `processPoolXml(node)` and `processDirectiveXml(node)` instead of passing the local entry node, which can break cache-manager reconstruction and should have targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageReconstructor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewer.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewer.java

Purpose: `OfflineImageViewer` is the legacy `hdfs oiv_legacy` command for old binary fsimage formats. It selects a legacy `ImageVisitor`, reads the image version, and delegates parsing to `ImageLoaderCurrent` through the loader factory.

Important APIs and control flow: the constructor stores input file, processor, and `skipBlocks`. `go()` opens a `PositionTrackingInputStream`, wraps it in `DataInputStream`, reads the version with `findImageVersion` using mark/reset, obtains an `ImageLoader`, and invokes `loadImage`. On failure it logs the byte offset before cleanup. `main` parses CLI options, validates delimiter usage, selects `Indented`, `XML`, `Delimited`, `FileDistribution`, `NameDistribution`, or default `Ls`, and forces block enumeration for processors that need file sizes.

State, persistence, and dependencies: state is the selected input path, visitor, and skip-block flag. Output is visitor-owned. Dependencies include Commons CLI, `PositionTrackingInputStream`, `ImageLoader`, visitor classes, and Hadoop `IOUtils`.

Integration points: legacy companion to the PB `OfflineImageViewerPB`; useful for older layout versions not handled by PB tools.

Risks and test signals: tests should cover CLI parsing, delimiter validation, default processor, skip-block override, unsupported versions, EOF handling, and failure offset logging. `findImageVersion` assumes the buffered stream supports mark/reset, which current construction satisfies. Main catches IO errors and prints messages rather than returning structured status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewerPB.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewerPB.java

Purpose: `OfflineImageViewerPB` is the primary `hdfs oiv` command for protobuf fsimages. It supports XML dump, reverse XML reconstruction, file distribution, WebHDFS-like browsing, delimited text, and corruption detection.

Important APIs and control flow: `buildOptions()` defines input, optional output, processor, Web address, file-distribution parameters, delimiter, storage-policy and erasure-coding flags, temp directory, and thread count. `run` handles no-arg/help cases, parses options, defaults processor to `Web` and output to stdout, creates a `Configuration`, opens a `PrintStream` when needed, then dispatches on uppercase processor. Each case instantiates the appropriate worker: `FileDistributionCalculator`, `PBImageXmlWriter`, `OfflineImageReconstructor`, `WebImageViewer`, `PBImageDelimitedTextWriter`, or `PBImageCorruptionDetector`. It checks `PrintStream.checkError()` before returning success.

State, persistence, and dependencies: the class is stateless. Persistence includes output files, optional reconstructed image `.md5`, web server lifecycle, and temp paths owned by selected processors. Dependencies include Commons CLI, Hadoop `Configuration`, `NetUtils`, `ExitUtil`, and PB image processors.

Integration points: invoked by the Hadoop CLI and by tests through `run`.

Risks and test signals: tests should cover each processor, stdout output, invalid processor, help exit codes, parse failures, disk-full detection via `checkError`, and cleanup of closeable processors. `ReverseXML` catches exceptions and calls `ExitUtil.terminate(1)`, which needs test harness handling. Web mode runs until the viewer stops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewerPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruption.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruption.java

Purpose: `PBImageCorruption` is a value object used by the protobuf image corruption detector to represent one suspicious inode id and the kinds of corruption associated with it.

Important APIs and control flow: the private enum `PBImageCorruptionType` defines output labels for `CORRUPT_NODE` and `MISSING_CHILD`. The constructor requires at least one of the boolean corruption flags and initializes an `EnumSet` plus the corrupt-child count. Mutators add missing-child or corrupt-node aspects and update the count. Accessors return the inode id, a compact type string, and the number of corrupt children. `getType()` concatenates `CorruptNode`, `With`, and `MissingChild` when both aspects are present.

State, persistence, and dependencies: state is inode id, corruption type set, and corrupt-child count. There is no persistence. Dependencies are limited to `EnumSet`.

Integration points: consumed by `PBImageCorruptionDetector` output generation and summary bookkeeping.

Risks and test signals: tests should cover constructor validation, each single corruption type, combined type formatting, updates through mutators, and child-count changes. The type string is presentation logic and should be treated as compatibility-sensitive if downstream tools parse delimited corruption output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruption.java -->
