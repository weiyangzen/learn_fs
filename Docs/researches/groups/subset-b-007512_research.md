# subset-b-007512 Research

Grouped research for Hadoop HDFS offline image viewer, snapshot CLI, utility, and WebHDFS authentication files. Each section preserves the source path and is intended to be split into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruptionDetector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruptionDetector.java

## Purpose
`PBImageCorruptionDetector` is an offline image viewer processor that extends `PBImageTextWriter` to detect limited fsimage namespace corruption while producing delimited text output. It focuses on directory-section references to missing inode IDs and directories whose child list contains missing children; it explicitly does not claim exhaustive fsimage validation.

## APIs and Types
The main API is package-visible construction with `PrintStream`, delimiter, and metadata temp path, plus overrides of `getHeader`, `getEntry`, `checkNode`, `buildNamespace`, and `afterOutput`. `OutputEntryBuilder` formats rows with corruption type, id, snapshot flag, parent path/id, name, node/ref/unknown type, and corrupt child count. `CorruptionChecker` records inode IDs from the INode section and reference IDs from the INodeReference section.

## Control Flow
During the first `PBImageTextWriter` pass, `checkNode` delegates directory collection to the superclass and records every inode id. In the directory-section pass, `buildNamespace` saves reference IDs, checks parent existence, stores child-parent relationships, checks child existence, and records parent missing-child corruption counts. During output, only inodes present in `corruptionsMap` produce rows; leftover corruptions without resolvable paths are emitted in `afterOutput`.

## State and Persistence
State is in-memory for corruption detection: a `HashSet` of inode IDs, a `HashSet` of reference IDs, and a `TreeMap<Long, PBImageCorruption>` for deterministic row order of unresolved corruptions. Namespace metadata persistence is inherited from `PBImageTextWriter` and may be memory or LevelDB depending on temp path.

## Dependencies and Integration
It depends on `FsImageProto`, `PBImageTextWriter`, `PBImageCorruption`, `IgnoreSnapshotException`, and Hadoop `Preconditions`. It integrates with OIV DetectCorruption processing and reuses superclass metadata loading, path lookup, and delimited escaping.

## Risks
`buildNamespace` assumes `refIdList` is non-null and that every ref child index is valid; corrupt references outside the list may fail rather than report a row. The output marks unresolved corruptions as `isSnapshot=true` when path/name lookup fails, which is a pragmatic label rather than proof the node came from a snapshot. Detection is intentionally narrow and misses block-level, permission, xattr, quota, and protobuf structural corruption beyond parse failures.

## Test Signals
Tests should cover missing child inode, missing parent inode, combined missing-node plus missing-child corruption, valid reference children, corruptions whose parent path cannot be resolved, custom delimiters, and deterministic ordering of leftover corruption rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageCorruptionDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageDelimitedTextWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageDelimitedTextWriter.java

## Purpose
`PBImageDelimitedTextWriter` renders each inode from a protobuf fsimage as one delimited text row, similar to recursive HDFS listing output, with optional storage policy and erasure coding policy columns.

## APIs and Types
It extends `PBImageTextWriter` and implements `getEntry`, `getHeader`, and no-op `afterOutput`. Constructors select delimiter/temp metadata storage and optional storage policy, EC policy, thread count, parallel output path, and configuration. The nested `OutputEntryBuilder` extracts file, directory, and symlink metadata into row fields.

## Control Flow
For each inode, `getEntry` builds a `Path` from parent path and inode name, then `OutputEntryBuilder` switches on inode type. Files contribute replication, mtime, atime, preferred block size, block count, file size, permissions, ACL marker, storage policy, and optional EC policy by ID. Directories contribute mtime, quotas, directory permission prefix, ACL marker, storage policy from xattrs, and optional EC policy xattr name. Symlinks contribute permission and times but not target text.

## State and Persistence
The writer holds booleans for optional columns and an `ErasureCodingPolicyManager` initialized only when EC output is requested with a non-null `Configuration`. All namespace metadata, xattr decoding, and permission string-table access are inherited from `PBImageTextWriter`; this class persists no data.

## Dependencies and Integration
It depends on `FSImageLoader.getFileSize`, `ErasureCodingPolicyManager`, `FsImageProto.INodeSection`, `Path`, `PermissionStatus`, and `HdfsConstants`. It is an OIV text processor implementation backed by the two-pass superclass scanner.

## Risks
`SimpleDateFormat` uses the default JVM timezone, so output is environment-dependent. Symlink targets are not included despite inode-specific metadata extraction. Directory calls to `dir.getXAttrs()` rely on protobuf default behavior when xattrs are absent. EC policy names may remain `-` if the manager does not know an ID.

## Test Signals
Useful tests compare header/row column count under optional flags, exercise file/directory/symlink inodes, verify ACL plus suffix, storage-policy xattr decoding, EC policy ID and xattr policy name paths, CSV escaping inherited from the superclass, and stable path construction for root and empty names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageDelimitedTextWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageTextWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageTextWriter.java

## Purpose
`PBImageTextWriter` is the abstract base for OIV processors that emit one text entry per resolvable inode from a protobuf fsimage. Because protobuf fsimage sections are not ordered for path reconstruction, it performs two metadata-loading passes before producing rows.

## APIs and Types
Subclasses implement `getEntry(String parent, INode inode)`, `getHeader()`, and `afterOutput()`. Protected/package hooks include `checkNode`, `buildNamespace`, `getPermission`, `getStoragePolicy`, `getErasureCodingPolicyName`, `putDirChildToMetadataMap`, `getNodeName`, `getParentId`, `serialOutStream`, `printIfNotEmpty`, and static `mergeFiles`. `MetadataMap` abstracts inode-parent and directory-name storage, with `InMemoryMetadataDB` and `LevelDBMetadataMap` implementations.

## Control Flow
`visit(filePath)` verifies fsimage format, loads the file summary, sorts sections by protobuf section order, loads the string table and inode reference section, scans INode sections to save directory names, scans INodeDirectory sections to build child-parent relationships, syncs metadata, then rescans inode data for output. Output is serial unless multiple threads, a real parallel output path, and multiple INodeSub sections are available. Parallel output writes each subsection to a temp file, validates parsed count against expected inode count from the first subsection, writes the header to the destination, and appends temp files in order.

## State and Persistence
The superclass owns `SerialNumberManager.StringTable`, output stream, delimiter, source filename, thread settings, and an erasure-coding xattr sentinel. In-memory metadata stores `Dir` objects and parent maps; LevelDB metadata creates two DBs under the supplied base directory and batches writes in groups of 1024 with a 16K-entry directory path LRU cache. Snapshot/reference paths that cannot be resolved are represented by `IgnoreSnapshotException` and skipped.

## Dependencies and Integration
It depends on NameNode fsimage protobuf classes, `FSImageUtil`, `FSImageFormatPBINode`, `FSImageFormatProtobuf.SectionName`, `SerialNumberManager`, LevelDB JNI/IQ80 APIs, Hadoop `Path`, xattr helpers, and Hadoop IO utilities. It is the shared engine for delimited text and corruption detection processors.

## Risks
LevelDB path cache recursion is synchronized but all reads share LevelDB handles; parallel output calls metadata lookups concurrently, so metadata implementation assumptions matter. `append(String)` uses CSV escaping and newline replacement but not full delimiter-aware quoting for arbitrary custom delimiters. Snapshot inodes are silently skipped except for aggregate warnings. Parallel mode leaves a partially written destination if merge fails after header creation. Recursive path construction can be expensive or stack-heavy for very deep trees despite caching.

## Test Signals
Tests should cover serial and parallel output equivalence, in-memory versus LevelDB metadata, root path and empty-name handling, missing parent/reference snapshot skips, string-table permission resolution, storage policy and EC xattr decoding, temp file cleanup after merge, malformed subsection count detection, and escaping of commas, delimiters, CRLF, and LF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageTextWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageXmlWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageXmlWriter.java

## Purpose
`PBImageXmlWriter` converts a protobuf fsimage into an XML document that preserves the fsimage's major sections: namespace metadata, string-table-dependent inode data, erasure coding policies, inode references/directories, files under construction, snapshots, snapshot diffs, secret manager state, and cache manager state.

## APIs and Types
The public API is construction from `Configuration` and `PrintStream`, `visit(RandomAccessFile)`, and static `createSimpleDateFormat()`. The class exposes many XML tag-name constants. Private dump methods handle each section and protobuf subtype, while `o(tag, value)` emits mangled XML values and compact boolean tags.

## Control Flow
`visit` validates the fsimage, loads summary metadata, prints XML prolog/root/version, sorts sections by `SectionName`, wraps each section input with compression and length limits, then dispatches to section-specific dump methods. Dump methods parse protobuf-delimited records until expected counts or EOF, emitting nested tags for blocks, ACLs, xattrs, quotas, EC schemas, delegation keys/tokens, cache directives, snapshot tables, and diff entries.

## State and Persistence
The writer keeps a `Configuration`, `PrintStream`, UTC `SimpleDateFormat`, and a loaded string table. It writes directly to the supplied stream and does not build persistent intermediate state. Date output is UTC ISO-like with millisecond precision. XAttr values are emitted as UTF-8 text when valid or hex otherwise.

## Dependencies and Integration
It depends on fsimage protobufs, `FSImageUtil`, `FSImageLoader.loadStringTable`, `FSImageFormatPBINode.Loader`, `PBHelperClient`, `XMLUtils`, Hadoop ACL/permission classes, erasure coding schemas, and `VersionInfo`. It is the protobuf-era XML OIV writer rather than the legacy visitor-driven XML writer.

## Risks
The string table must be processed before sections that decode permissions, ACLs, and xattrs; section sorting should provide that ordering, but unknown/new section behavior is limited. Some optional booleans are represented by presence only, which may surprise consumers expecting explicit false values. XML is streamed without recovery; parse or write failures leave truncated output. Secret manager material and delegation token fields are printed, so output handling is security-sensitive. Schema changes require new tag constants and dump logic.

## Test Signals
Tests should validate XML well-formedness, string-table ordering, xattr UTF-8 versus hex output, ACL and permission formatting, EC policy schema options, snapshot diff branches for file and directory diffs, secret/cache manager expected counts, UTC date formatting, and invalid/unknown diff type failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/PBImageXmlWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TextWriterImageVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TextWriterImageVisitor.java

## Purpose
`TextWriterImageVisitor` is a legacy `ImageVisitor` base class that gives visitor implementations UTF-8 text-file output with optional mirroring to standard output.

## APIs and Types
It is package-private and abstract. Constructors open the destination file and choose whether to print to screen. It overrides `finish` and `finishAbnormally` to close the writer, and exposes protected `write(String)` to subclasses.

## Control Flow
Construction opens an `OutputStreamWriter` from `Files.newOutputStream(Paths.get(filename))` and marks writing as allowed. `write` checks `okToWrite`, optionally prints to `System.out`, writes to the file writer, and disables further writes if an `IOException` occurs. Both normal and abnormal finish close the writer and mark it closed.

## State and Persistence
State is only `printToScreen`, `okToWrite`, and the final writer. Output is immediately sent to the writer object but flushed/closed through normal Java writer semantics. There is no atomic file replacement; partial output remains if processing fails after construction.

## Dependencies and Integration
It depends on the legacy offline image visitor API, Java NIO file opening, and UTF-8. `XmlImageVisitor` subclasses it.

## Risks
There is no try-with-resources ownership; callers must ensure `finish` or `finishAbnormally` runs. `close` is not idempotent-protected beyond writer behavior. Mirroring uses process-wide `System.out`, which is awkward for tests. The class does not add newlines, so subclasses own formatting correctness.

## Test Signals
Tests should cover UTF-8 output, write-after-close failure, abnormal close behavior, mirror-to-screen behavior with captured stdout, and propagation of write exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TextWriterImageVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/WebImageViewer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/WebImageViewer.java

## Purpose
`WebImageViewer` loads an fsimage and exposes a read-only WebHDFS-like HTTP API for that offline namespace using Netty.

## APIs and Types
Public constructors accept an `InetSocketAddress` with optional `Configuration`. Public methods are `start(String fsimage)`, testing-visible `initServer(String fsimage)`, testing-visible `getPort()`, and `close()`. The class owns Netty bootstrap, boss/worker event-loop groups, a channel group, bound channel, mutable bound address, and configuration.

## Control Flow
Construction configures Netty NIO groups and applies Hadoop security configuration to `UserGroupInformation`. `start` rejects secure mode, initializes the server, then blocks on the channel close future until interrupted. `initServer` loads the fsimage through `FSImageLoader`, installs an HTTP request decoder, string encoder, HTTP response encoder, and `FSImageHandler`, binds to the requested address, records the actual local address, and adds the server channel to the group. `close` closes all channels and gracefully shuts down both groups.

## State and Persistence
The loaded fsimage is retained by `FSImageHandler`/`FSImageLoader` for serving requests; this class persists no new files. Network state consists of live channels and event-loop threads.

## Dependencies and Integration
It depends on Netty, Hadoop `Configuration`, `CommonConfigurationKeysPublic`, `UserGroupInformation`, `FSImageLoader`, and `FSImageHandler`. It integrates the offline image loader with WebHDFS-compatible request handling.

## Risks
Secure mode is unsupported and fails at runtime. `start` only closes on interruption, so other init failures depend on caller cleanup. Pipeline ordering includes `StringEncoder` before `HttpResponseEncoder`, which depends on handler output types. Long-lived event loops require `close` in tests to avoid leaked threads. The viewer exposes offline namespace metadata over the configured bind address without authentication.

## Test Signals
Tests should bind to port 0 and assert `getPort`, reject secure configuration, issue representative WebHDFS requests, verify `close` releases the port/threads, and exercise invalid fsimage load failure without leaked channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/WebImageViewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/XmlImageVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/XmlImageVisitor.java

## Purpose
`XmlImageVisitor` is the legacy visitor-based XML writer for offline image viewing. It emits simple XML tags as the older `ImageVisitor` traversal calls arrive.

## APIs and Types
Constructors accept output filename and optional screen mirroring. It overrides `start`, `finish`, `finishAbnormally`, `visit`, `visitEnclosingElement`, and `leaveEnclosingElement`. A `Deque<ImageElement>` tracks open enclosing tags.

## Control Flow
`start` writes the XML declaration. Scalar `visit` emits a full tag through `writeTag`. Enclosing visits write an opening tag and push the element; the keyed overload emits one XML attribute without value mangling. `leaveEnclosingElement` pops and writes the closing tag, failing if there is no open element. Abnormal finish writes an XML comment before closing.

## State and Persistence
The tag stack is in memory. File output and close behavior come from `TextWriterImageVisitor`. Values are mangled through `XMLUtils.mangleXmlString`; attribute values are not passed through `XMLUtils`.

## Dependencies and Integration
It depends on the legacy `ImageVisitor` protocol, `ImageElement`, `TextWriterImageVisitor`, and `XMLUtils`. It is separate from protobuf-specific `PBImageXmlWriter`.

## Risks
Attribute values can produce invalid XML if they contain special characters. Unbalanced visitor calls fail at close-tag time or leave malformed output. Partial XML is expected on abnormal finish. It does not write a root element by itself; traversal must supply one.

## Test Signals
Tests should cover balanced and unbalanced nesting, special-character value mangling, keyed enclosing element attributes with special characters, abnormal finish output, and write/close propagation from the superclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/XmlImageVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshot.java

## Purpose
`LsSnapshot` is a private HDFS CLI tool implementing `hdfs lsSnapshot <snapshotDir>` to list snapshots for one snapshottable directory.

## APIs and Types
It extends `Configured` and implements `Tool`. The public API is `run(String[] argv)` and `main`, which delegates through `ToolRunner`.

## Control Flow
`run` builds usage text, requires exactly one argument, constructs a `Path`, obtains a `DistributedFileSystem` through `AdminHelper.getDFS(getConf())`, calls `getSnapshotListing(snapshotRoot)`, and prints results with `SnapshotStatus.print`. On exception it prints only the first line of the localized message and returns 1.

## State and Persistence
The tool has no persistent state. It reads cluster state via the configured DFS client and writes to stdout/stderr.

## Dependencies and Integration
It depends on `DistributedFileSystem`, `SnapshotStatus`, `AdminHelper`, `Tool`, and Hadoop configuration injection. It integrates into HDFS command-line administration.

## Risks
Error handling assumes `getLocalizedMessage()` is non-null. It does not verify the filesystem type itself because `AdminHelper.getDFS` is responsible. Usage text comments mention snapshottable directories generally, while this command lists snapshots under a specific path.

## Test Signals
Tests should cover argument count validation, successful print delegation, DFS exception message trimming, null/empty exception messages, and `main` exit-code behavior through a tool harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshottableDir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshottableDir.java

## Purpose
`LsSnapshottableDir` implements the `hdfs lsSnapshottableDir` CLI to list snapshottable directories visible to the current user, or all of them for a superuser.

## APIs and Types
It extends `Configured`, implements `Tool`, and exposes `run(String[] argv)` plus `main`.

## Control Flow
`run` requires zero arguments, obtains the default `FileSystem`, checks that it is a `DistributedFileSystem`, invokes `getSnapshottableDirListing`, and prints via `SnapshottableDirectoryStatus.print`. `IOException` is caught, shortened to the first localized-message line, printed, and returned as failure.

## State and Persistence
It keeps no state and performs no writes except stdout/stderr. Data comes from NameNode RPC through the DFS client.

## Dependencies and Integration
It depends on `FileSystem`, `DistributedFileSystem`, `SnapshottableDirectoryStatus`, and `ToolRunner`. It is part of the HDFS snapshot admin tool set.

## Risks
The tool rejects non-DFS filesystems at runtime. Like related snapshot tools, it assumes exception messages are non-null. It does not expose filters or machine-readable output.

## Test Signals
Tests should validate zero-argument usage, non-DFS rejection, successful listing print path, IOException formatting, and `ToolRunner` integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshottableDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/SnapshotDiff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/SnapshotDiff.java

## Purpose
`SnapshotDiff` implements `hdfs snapshotDiff <snapshotDir> <from> <to>` to print differences between two snapshots or between a snapshot and the current directory tree.

## APIs and Types
It extends `Configured` and implements `Tool`. Constructors default to `HdfsConfiguration` or accept any `Configuration`. `getSnapshotName` normalizes `"."`, `.snapshot/name`, and `/.snapshot/name` forms. `run` and `main` provide CLI execution.

## Control Flow
`run` requires three arguments, resolves the filesystem from the snapshot root URI, enforces `DistributedFileSystem`, normalizes from/to names, invokes `dfs.getSnapshotDiffReport`, and prints the report string. `IOException` prints a short error line and the full stack trace to stderr before returning failure.

## State and Persistence
No persistent state. The command reads NameNode snapshot metadata through the DFS client and writes a textual diff report.

## Dependencies and Integration
It depends on `DistributedFileSystem`, `SnapshotDiffReport`, `HdfsConstants`, `Path`, and `ToolRunner`. It is a CLI wrapper over the DFS snapshot diff RPC.

## Risks
`getSnapshotName` uses string prefix slicing and must stay aligned with `.snapshot` constants. Stack traces on normal user-facing errors are noisy. Exception message splitting assumes non-null localized messages. It does not validate that from/to are distinct.

## Test Signals
Tests should cover normalization for `"."`, `.snapshot/foo`, `/.snapshot/foo`, raw snapshot names, argument count errors, non-DFS filesystem rejection, successful report printing, and IOException stderr format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/SnapshotDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AsyncRFAAppender.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AsyncRFAAppender.java

## Purpose
`AsyncRFAAppender` adapts log4j1 `AsyncAppender` configuration to lazily wrap a `RollingFileAppender`, mainly for NameNode audit and metric logging before log4j2 migration.

## APIs and Types
It extends `AsyncAppender`, overrides `append(LoggingEvent)`, and exposes bean-style getters/setters for max file size, backup index, filename, conversion pattern, blocking, and buffer size.

## Control Flow
The first append checks whether the rolling appender exists. A synchronized initializer creates a `PatternLayout`, constructs a `RollingFileAppender` in append mode, applies rollover settings, adds it to the async appender, marks assignment complete, and applies async blocking/buffer settings before delegating append handling to the superclass.

## State and Persistence
State is logging configuration plus a lazily assigned `RollingFileAppender` and volatile assignment flag. Persistence is the target log file and backups created by log4j.

## Dependencies and Integration
It depends on log4j1 classes. It integrates with log4j properties that can set bean fields but cannot directly wrap RFA in async mode.

## Risks
Missing or invalid `fileName` fails on first log event, possibly far from startup. Setter calls after first append do not reconfigure the already-created appender. `rollingFileAppender == null` is checked outside synchronization; correctness relies on the volatile assignment guard inside. Constructor `IOException` is wrapped in unchecked `RuntimeException`.

## Test Signals
Tests should instantiate via setters, append a first event, verify rolling appender creation and file output, check max size/backup settings, exercise missing filename failure, and verify post-initialization setter changes do not silently affect the created appender unless intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AsyncRFAAppender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AtomicFileOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AtomicFileOutputStream.java

## Purpose
`AtomicFileOutputStream` writes to `target.tmp`, fsyncs, closes, and then moves the temp file over the target so consumers see either the old complete file or the new complete file.

## APIs and Types
It extends `FilterOutputStream`, with constructor `AtomicFileOutputStream(File)`, override `write(byte[], int, int)`, override `close()`, and `abort()`.

## Control Flow
Construction opens `f.getName() + ".tmp"` in the same parent directory. `close` flushes, forces the file channel to disk, closes the stream, then renames temp to original. If `renameTo` fails, it deletes an existing original and calls `NativeIO.renameTo`. If flushing/closing fails, it attempts to close the file descriptor and deletes the temp file. `abort` closes without commit and deletes temp.

## State and Persistence
State is the original and temp absolute files. Persistence semantics include fsync of file contents but not an explicit parent-directory fsync. On Windows, replacement is not atomic because the original is deleted before native rename.

## Dependencies and Integration
It depends on Java file APIs, NIO `Files.delete`, Hadoop `IOUtils`, and `NativeIO`. It is used by `PersistentLongFile` and `MD5FileUtils` for durable sidecar writes.

## Risks
Concurrent writers to the same target share the same `.tmp` path and can corrupt each other. Parent directory durability is not guaranteed after rename. Windows behavior can temporarily remove the target. `abort` logs but cannot guarantee cleanup if close/delete fails. The constructor assumes a non-null parent directory.

## Test Signals
Tests should cover successful commit, overwrite existing file, failed write/flush cleanup via injected stream or filesystem shim, abort cleanup, no original replacement after abort, and platform-specific rename fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AtomicFileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/BestEffortLongFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/BestEffortLongFile.java

## Purpose
`BestEffortLongFile` stores one long value on disk in binary form without fsync, intended for frequently updated values where exact persistence is not correctness-critical.

## APIs and Types
It implements `Closeable` and exposes constructor `(File, defaultVal)`, `get()`, `set(long)`, and `close()`.

## Control Flow
`get` and `set` call `lazyOpen`. `lazyOpen` reads existing bytes if present, validates exact 8-byte length, decodes with Guava `Longs`, or uses the default. It then opens a `RandomAccessFile` in `rw` mode and stores its channel. `set` rewrites an 8-byte buffer at file position 0 using `IOUtils.writeFully` and updates the cached value.

## State and Persistence
State includes the target file, default value, cached long, lazily opened channel, and reusable 8-byte buffer. Writes are not fsynced and are binary, not textual. The file remains open until `close`.

## Dependencies and Integration
It depends on Hadoop `IOUtils` and shaded Guava `Files`/`Longs`. It complements `PersistentLongFile` where performance matters more than durability.

## Risks
Partial or corrupted files with nonzero non-8-byte length cause `IOException`. No locking protects concurrent processes or threads. The file is not truncated before writing, but fixed 8-byte writes keep valid files at the expected length. Directory creation is not handled.

## Test Signals
Tests should cover absent file default, valid persisted value, invalid length failure, set/get round trip, reopen after close, and behavior when parent directories are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/BestEffortLongFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ByteArray.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ByteArray.java

## Purpose
`ByteArray` wraps a `byte[]` so byte content, not object identity, can be used for equality and hash-based map/set keys.

## APIs and Types
The public API is constructor `ByteArray(byte[])`, `getBytes()`, `hashCode()`, and `equals(Object)`.

## Control Flow
`hashCode` lazily caches `Arrays.hashCode(bytes)` when the cached field is zero. `equals` type-checks and compares with `Arrays.equals`.

## State and Persistence
State is the original mutable byte array reference and cached hash int. There is no copying or persistence.

## Dependencies and Integration
It depends only on `Arrays` and Hadoop audience annotations. It is a lightweight utility for internal byte-key maps.

## Risks
The wrapper is unsafe if the underlying array is mutated after construction or after hash caching; equality and hash code can diverge from map bucket placement. Arrays whose actual hash is zero cause recomputation each call. `getBytes` exposes the mutable reference.

## Test Signals
Tests should cover equal-content arrays, different content, non-`ByteArray` comparison, hash caching behavior, and mutation-after-insertion hazards documented by failing/expected behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ByteArray.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Canceler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Canceler.java

## Purpose
`Canceler` is a simple cross-thread cancellation flag with a human-readable reason.

## APIs and Types
It exposes `cancel(String reason)`, `isCancelled()`, and `getCancellationReason()`.

## Control Flow
Calling `cancel` stores the reason in a volatile field. Polling code checks non-null reason with `isCancelled` and may retrieve the reason.

## State and Persistence
State is a single volatile `String`. Cancellation is one-way unless callers pass `null`, which the method does not prevent but would effectively clear cancellation.

## Dependencies and Integration
It has no runtime dependencies beyond annotations. `DataTransferThrottler` accepts an optional `Canceler` to stop sleeping early.

## Risks
There is no synchronization beyond volatile visibility and no compare-and-set semantics for competing cancellation reasons. Passing null is not guarded. Consumers must poll; cancellation does not interrupt waiting threads by itself.

## Test Signals
Tests should cover initial state, cancellation visibility across threads, reason retrieval, and null reason behavior if supported or prohibited by future changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Canceler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ConstEnumCounters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ConstEnumCounters.java

## Purpose
`ConstEnumCounters` is an immutable-flavored subclass of `EnumCounters` initialized to a constant value for every enum constant.

## APIs and Types
It extends `EnumCounters<E>`, defines runtime `ConstEnumException`, and overrides all mutating methods (`negation`, `set`, `reset`, `add`, `subtract`) as final methods throwing a shared exception.

## Control Flow
Construction calls the superclass zero-initializing constructor, then a private `forceReset` calls `super.reset(defaultVal)` before mutation is disabled through overrides.

## State and Persistence
State is inherited counter array. There is no persistence. The object is not strictly immutable against inherited methods not overridden in the future or reflection, but public current mutators are blocked.

## Dependencies and Integration
It depends on `EnumCounters` and is useful where a constant all-enum counter vector should be shared without accidental mutation.

## Risks
The shared exception instance has one creation stack trace, which may reduce diagnostic detail. Subclass immutability depends on keeping overrides aligned with superclass mutators. The inherited `asArray` returns a copy, which is safe.

## Test Signals
Tests should verify default values, every mutator throws, read methods still work, equality/hash/toString inherited behavior, and that future superclass mutators are added to this subclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ConstEnumCounters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/CyclicIteration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/CyclicIteration.java

## Purpose
`CyclicIteration` provides an `Iterable` over a `NavigableMap` that starts after a supplied key, wraps to the first entry, and stops after each entry has been returned once.

## APIs and Types
The public API is constructor `(NavigableMap<K,V>, K startingkey)` and `iterator()`. The private `CyclicIterator` implements `Iterator<Map.Entry<K,V>>`.

## Control Flow
Construction stores the map and an exclusive `tailMap(startingkey, false)`, or nulls for empty maps. The iterator starts from the tail iterator, falls back to the full map iterator when the tail is exhausted, remembers the first returned entry, and stops when the next candidate equals that first entry. `remove` is unsupported.

## State and Persistence
State is iterator-local plus references to live map views. No persistence. Iteration reflects the underlying map view behavior and is not explicitly fail-fast beyond the map's own iterators.

## Dependencies and Integration
It depends on Java collections and Hadoop audience/stability annotations. It is suitable for round-robin-style scans over sorted maps.

## Risks
Concurrent map modification follows underlying iterator semantics. If `startingkey` is null, behavior depends on map comparator/null support. Entry equality is used to detect wrap completion, so unusual entry equality implementations may matter.

## Test Signals
Tests should cover empty map, start before first, start at existing key, start between keys, start after last, single-entry map, unsupported remove, and concurrent modification behavior for the chosen map implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/CyclicIteration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/DataTransferThrottler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/DataTransferThrottler.java

## Purpose
`DataTransferThrottler` enforces a shared byte-per-second budget across one or more threads by sleeping callers when recent transfer volume exceeds the configured period allowance.

## APIs and Types
Constructors accept bandwidth alone with a 500 ms period or explicit period plus bandwidth. Public synchronized methods are `getBandwidth`, `setBandwidth`, `throttle(long)`, and `throttle(long, Canceler)`.

## Control Flow
Each throttle call subtracts transferred bytes from the current period reserve and adds to in-flight used bytes. While reserve is non-positive, it checks cancellation, waits until the current period ends, advances by one period if within a three-period extension, or resets accounting after long idle time. It restores interrupted status and exits the loop if wait is interrupted, then subtracts the call's bytes from `bytesAlreadyUsed`.

## State and Persistence
All mutable state is guarded by the object monitor: period, period extension, bytes per period, current period start, reserve, and bytes already used. No persistence.

## Dependencies and Integration
It depends on `Time.monotonicNow` and optional `Canceler`. It is used by HDFS data transfer paths to shape aggregate throughput.

## Risks
`setBandwidth` affects future periods but can produce zero `bytesPerPeriod` for very low bandwidth with short periods due to integer division, causing pathological throttling. Synchronization serializes all callers. Cancellation only exits sleeping logic and does not undo already-accounted bytes until method exit. Interrupted waits do not throw, so callers must inspect thread interrupt state.

## Test Signals
Tests should cover no-op for nonpositive bytes, bandwidth getter/setter, sleep behavior with fake/controlled time if available, cancellation return, interrupt restoration, long-idle reset, and low-bandwidth rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/DataTransferThrottler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Diff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Diff.java

## Purpose
`Diff` represents changes between a previous sorted element list and a current sorted element list using two sorted lists: created elements and deleted elements. It supports create/delete/modify, undo, lookup in previous/current views, applying diffs, and combining posterior diffs.

## APIs and Types
`Element<K>` supplies comparable keyed elements. `Processor<E>` handles overwritten/deleted elements during combine. `Container<E>` wraps a determinate lookup result that may be null. `UndoInfo<E>` stores data for undoing delete/modify. Public methods expose created/deleted lists, mutation operations, undo operations, previous/current accessors, apply-to-previous/current transforms, combination, and `toString`.

## Control Flow
Mutations binary-search sorted created/deleted lists. `create` inserts into created. `delete` removes a newly created element or inserts into deleted. `modify` replaces a created element or records old in deleted and new in created. `accessPrevious` and `accessCurrent` swap list roles to determine if a key is known present/absent. `apply2Previous` subtracts deleted from previous, then merges created. `apply2Current` reverses the operation. `combinePosterior` merges another diff by replaying create, delete, or modify cases in sorted order.

## State and Persistence
State is two lazily allocated sorted `List<E>` fields. No persistence or synchronization. Correctness relies on object identity in some remove/contains paths and sorted list invariants.

## Dependencies and Integration
It depends on Java collections and Hadoop `Preconditions`. It is a core utility for snapshot/diff-like namespace state handling where compact reversible list changes are needed.

## Risks
Callers must provide elements whose `compareTo(K)` and `getKey()` remain stable. Undo methods are explicitly undefined unless called for the immediately corresponding previous operation with returned `UndoInfo`. Some code paths use negative binary-search insertion points in `remove`, which is correct for undo insertion-point semantics but brittle if list state changed. The class is not thread-safe and can throw `AssertionError`/`Preconditions` on invariant violations.

## Test Signals
Tests should cover all documented state cases, sorted insertion/removal, create-delete cancellation, delete-create replacement, repeated modify, undo for each operation, access previous/current known-present/known-absent/unknown cases, apply round trips, combinePosterior with a deleted processor, and invariant violation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Diff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumCounters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumCounters.java

## Purpose
`EnumCounters` stores one long counter per enum constant, indexed by ordinal, with arithmetic and aggregate helpers.

## APIs and Types
Constructors accept an enum class with optional default value. Public methods include `get`, `asArray`, `negation`, `set`, `reset`, `add`, `subtract`, `sum`, `deepCopyEnumCounter`, `allLessOrEqual`, `anyGreaterOrEqual`, plus equality, hash, and string formatting.

## Control Flow
Construction validates `enumClass.getEnumConstants()` and allocates a long array. Operations directly index by `e.ordinal()` or iterate over the full counter array. Copy/arithmetic against another `EnumCounters<E>` assumes the same enum shape; `equals` additionally checks enum class identity.

## State and Persistence
State is enum class and long array. `asArray` returns a cloned array, so direct external mutation is avoided. No persistence or synchronization.

## Dependencies and Integration
It depends on Hadoop `Preconditions` and Apache Commons `ArrayUtils`. `ConstEnumCounters` subclasses it for immutable default vectors.

## Risks
Methods accepting another `EnumCounters<E>` do not runtime-check enum class before indexing, so raw-type misuse can corrupt logic or throw length issues. Counter overflow is unchecked. `toString` assumes at least one enum constant; empty enums would cause substring failure.

## Test Signals
Tests should cover default and custom initialization, ordinal mapping, array copy isolation, arithmetic operations, equality across same/different enum classes, deep copy independence, threshold helpers, overflow behavior if relevant, and empty enum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumCounters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumDoubles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumDoubles.java

## Purpose
`EnumDoubles` is the double-valued counterpart to `EnumCounters`, storing one double per enum constant by ordinal.

## APIs and Types
Constructor accepts enum class. Public final operations include `get`, `negation`, `set`, `reset`, `add`, `subtract`, plus equality, hash, and string formatting.

## Control Flow
Operations index directly by enum ordinal or iterate over the double array. Equality requires the same enum class and `Arrays.equals` over double values.

## State and Persistence
State is enum class plus double array. No persistence and no synchronization. There is no method exposing the backing array.

## Dependencies and Integration
It depends on Hadoop `Preconditions` and Java `Arrays`. It is used where enum-indexed floating point metrics or ratios are more suitable than integer counters.

## Risks
Floating point special cases follow Java array equality semantics, including NaN and signed zero behavior. Methods accepting another `EnumDoubles<E>` trust generic type correctness. `toString` assumes at least one enum constant.

## Test Signals
Tests should cover ordinal mapping, arithmetic, reset/negation, equality for NaN and signed zero if important, same versus different enum classes, and empty enum formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumDoubles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Holder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Holder.java

## Purpose
`Holder<T>` is a minimal mutable wrapper around a value, useful when callers need a replaceable reference in collections or closures.

## APIs and Types
It exposes public field `held`, constructor `Holder(T held)`, and `toString`.

## Control Flow
Construction assigns the field. `toString` delegates to `String.valueOf`, producing `"null"` for null values.

## State and Persistence
State is the public mutable field. No persistence, validation, or synchronization.

## Dependencies and Integration
It has no external dependencies. It is a small utility for avoiding repeated lookups or emulating pass-by-reference.

## Risks
Public mutability makes invariants caller-owned. It does not implement `equals`/`hashCode`, so holder identity is used in collections. Thread visibility is not guaranteed without external synchronization.

## Test Signals
Tests are minimal: construction, mutation, null `toString`, and identity equality expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Holder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightHashSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightHashSet.java

## Purpose
`LightWeightHashSet` is a memory-conscious non-thread-safe hash set backed by a power-of-two bucket array and singly linked collision chains. It disallows null elements and supports polling/removing batches.

## APIs and Types
It implements `Collection<T>`. Public APIs include constructors with capacity/load factors, `size`, `isEmpty`, `getCapacity`, `contains`, `getElement`, `add`, `addAll`, `remove`, `pollN`, `pollAll`, `pollToArray`, `iterator`, `clear`, `toArray`, `containsAll`, `removeAll`, and diagnostics. `LinkedElement<T>` stores element, next pointer, and cached hash.

## Control Flow
Adds validate non-null, compute bucket index by `hash & mask`, reject duplicates by hash/equality scan, prepend a linked element, increment size/modification, and resize if above threshold. Removes unlink matching bucket entries and shrink if below threshold. Poll methods remove arbitrary bucket-order elements. Iterators scan buckets and are fail-fast using a modification epoch, with iterator `remove` supported.

## State and Persistence
State includes bucket array, capacity, hash mask, initial capacity, size, load factors, thresholds, and modification count. Resize rehashes existing linked elements into a new bucket array. No persistence or synchronization.

## Dependencies and Integration
It depends on Java collections and SLF4J. `LightWeightLinkedSet` extends it to preserve insertion order.

## Risks
Not thread-safe. `contains(Object)` casts unchecked to `T`; incompatible key types can throw `ClassCastException`. `toArray(T[])` does not null-terminate when the supplied array is larger than size, diverging from the `Collection` contract. Poll loops assume internal size/capacity consistency. Poor hash distribution degrades to bucket scans.

## Test Signals
Tests should cover load-factor expansion/shrink, duplicate add, null rejection, contains/getElement, arbitrary poll counts including zero/all, iterator fail-fast and remove, clear resets capacity, `toArray` contract including oversized arrays, and collision-heavy elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightHashSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightLinkedSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightLinkedSet.java

## Purpose
`LightWeightLinkedSet` extends `LightWeightHashSet` with an all-element doubly linked list so iteration and polling follow insertion order.

## APIs and Types
It adds `DoubleLinkedElement<T>` with before/after pointers, tracks `head`, `tail`, and a bookmark iterator. Public additions include `pollFirst`, ordered overrides of `pollN`, `pollAll`, `toArray`, `iterator`, `clear`, `getBookmark`, and `resetBookmark`.

## Control Flow
Adds use the superclass bucket lookup but allocate `DoubleLinkedElement`, prepend to the bucket, append to the insertion-order list, and adjust bookmark if needed. Removal delegates bucket unlinking to the superclass override path, then unlinks from the doubly linked list and advances bookmark if the removed element was next. Ordered poll methods repeatedly remove from `head`. Iterators walk `after` pointers and are fail-fast; iterator removal is unsupported.

## State and Persistence
State is inherited hash table plus ordered linked-list pointers and bookmark iterator state. No persistence or synchronization.

## Dependencies and Integration
It depends on `LightWeightHashSet` internals and Java iterator exceptions. It is used where low overhead and stable insertion-order traversal/polling are needed.

## Risks
It is tightly coupled to superclass `removeElem` returning the exact linked element. Bookmark state is mutated by `getBookmark`, which may be surprising. Iterator remove is unsupported even though the superclass iterator supports it. Like the superclass, it does not null-terminate oversized arrays.

## Test Signals
Tests should cover insertion-order iteration, duplicate handling, remove head/tail/middle, pollFirst, pollN ordering, pollAll ordering and clear, bookmark progression/removal/reset, fail-fast iteration, and resizing while preserving order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightLinkedSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/MD5FileUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/MD5FileUtils.java

## Purpose
`MD5FileUtils` provides static helpers for md5sum-compatible sidecar files named `<data>.md5`, including compute, save, read, verify, and rename operations.

## APIs and Types
Public APIs are `verifySavedMD5`, `readStoredMd5ForFile`, `computeMd5ForFile`, `saveMD5File(File, MD5Hash)`, `renameMD5File`, and `getDigestFileForFile`. It uses `LINE_REGEX` to parse 32 lowercase hex digits plus filename.

## Control Flow
Reading opens the md5 file as UTF-8, reads and trims the first line, validates the regex, checks the referenced filename basename against the expected data file, and returns `MD5Hash`. Computing streams the data file through `DigestInputStream` into `IOUtils.NullOutputStream`. Saving writes `"<hex> *<name>\n"` through `AtomicFileOutputStream`. Renaming reads the old digest, writes a new sidecar for the new filename, then deletes the old sidecar.

## State and Persistence
The class is stateless. Persistence is the `.md5` sidecar, written atomically through `AtomicFileOutputStream`.

## Dependencies and Integration
It depends on Java security digest APIs, Hadoop `MD5Hash`, `IOUtils`, `StringUtils`, and `AtomicFileOutputStream`. It supports fsimage/editlog checksum workflows and other HDFS file sidecars.

## Risks
Only lowercase md5 hex matches. `verifySavedMD5` reports its `expectedMD5` as "computed" but does not compute internally. If no sidecar exists, `readStoredMd5ForFile` returns null and verify will fail by inequality. `renameMD5File` can leave both sidecars if old delete fails. The filename check ignores directories by comparing basename only.

## Test Signals
Tests should cover md5 computation, save/read round trip, missing sidecar, invalid format, uppercase hash rejection, wrong referenced filename, verify mismatch, atomic save content, and rename side effects when deletion fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/MD5FileUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/PersistentLongFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/PersistentLongFile.java

## Purpose
`PersistentLongFile` stores one long value as text in a file, updating it atomically and durably through `AtomicFileOutputStream`.

## APIs and Types
The class exposes constructor `(File, defaultVal)`, `get()`, `set(long)`, and static `writeFile`/`readFile` helpers.

## Control Flow
`get` lazily loads once from `readFile`, defaulting when the file does not exist. `set` writes only if the cached value differs or has not been loaded, then updates the cache. `writeFile` writes decimal text plus newline through `AtomicFileOutputStream`, aborting in finally if close did not complete. `readFile` parses the first line as a long and wraps number format errors as `IOException`.

## State and Persistence
State is file, default value, cached long, and loaded flag. Persistence is textual and intended durable because the atomic stream flushes and forces file contents before rename.

## Dependencies and Integration
It depends on `AtomicFileOutputStream`, Hadoop `IOUtils`, and SLF4J. It contrasts with `BestEffortLongFile` for correctness-critical values.

## Risks
No synchronization protects concurrent callers. Parent directory creation is not handled. A malformed existing file causes hard failure rather than defaulting. Atomic stream limitations, such as no parent-directory fsync and shared `.tmp` path, apply here.

## Test Signals
Tests should cover absent file default, read existing value, set/write/reopen, no rewrite for same loaded value if observable, malformed file failure, abort cleanup on injected write failure, and concurrent write expectations if documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/PersistentLongFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReadOnlyList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReadOnlyList.java

## Purpose
`ReadOnlyList` defines a minimal unmodifiable indexed iterable and utilities for binary search and adapting between `ReadOnlyList` and Java `List` views.

## APIs and Types
The interface exposes `isEmpty`, `size`, `get`, and `iterator`. `Util` provides `emptyList`, `binarySearch`, `asReadOnlyList(List)`, and `asList(ReadOnlyList)`.

## Control Flow
`binarySearch` mirrors `Collections.binarySearch` over the read-only interface. `asReadOnlyList` delegates read methods and iterator to the backing list. `asList` returns an anonymous `List` implementing only iteration, emptiness, size, get, `toArray()`, and `toString`; all mutators and many query/list-iterator operations throw `UnsupportedOperationException`.

## State and Persistence
Adapters are live views over backing lists, not snapshots. No persistence or synchronization.

## Dependencies and Integration
It depends on Java collection interfaces and Hadoop annotations. It is useful in HDFS internals that want read-only list exposure without copying.

## Risks
`asReadOnlyList` still exposes the backing list iterator, whose `remove` may mutate if supported. `asList` is only a partial `List` implementation; even harmless queries like `contains` throw. Live views reflect concurrent backing mutations. `toArray(T[])` is unsupported in `asList`.

## Test Signals
Tests should cover binary-search found/insertion cases, empty list, live-view behavior, unsupported operations, iterator mutation behavior for mutable backing lists, and `toString` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReadOnlyList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReferenceCountMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReferenceCountMap.java

## Purpose
`ReferenceCountMap` deduplicates equal instances while maintaining a reference count on the canonical stored instance.

## APIs and Types
Generic type `E` must implement `ReferenceCounter`, which supplies `getRefCount`, `incrementAndGetRefCount`, and `decrementAndGetRefCount`. Public APIs include `put`, `remove`, `getReferenceCount`, `getUniqueElementsSize`, testing-visible `getEntries`, and `clear`.

## Control Flow
`put` uses `ConcurrentHashMap.putIfAbsent`; if an equivalent entry exists, it increments and returns that canonical value, otherwise increments the new key and returns it. `remove` looks up an equivalent value, decrements it, and removes the map entry when the count reaches zero. `getEntries` snapshots keys into an immutable list.

## State and Persistence
State is a `ConcurrentHashMap<E,E>` plus mutable counters inside values. No persistence. Despite concurrent map use, the class comment says it is not thread-safe because counter operations and remove races are not atomic as a compound operation.

## Dependencies and Integration
It depends on Java concurrent maps, shaded Guava `ImmutableList`, and Hadoop annotations. It is meant for memory deduplication of ref-counted internal objects.

## Risks
Key equality/hash must remain stable while stored. Concurrent put/remove can race counter updates. Removing an absent key is silent. Negative ref counts are possible if `ReferenceCounter` permits them or remove is overcalled.

## Test Signals
Tests should cover canonical instance return, duplicate increments, removal decrement and final map removal, absent removal, key mutation hazards, `getEntries` snapshot, and concurrent race behavior if usage evolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ReferenceCountMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLock.java

## Purpose
`RwLock` defines the read/write locking abstraction used by FSNamesystem, with support for multiple lock modes.

## APIs and Types
It declares mode-aware read and write lock/unlock methods, interruptible acquisition, and lock-held checks. Default methods route legacy no-mode calls to `RwLockMode.GLOBAL` and default operation names to `"OTHER"`.

## Control Flow
Implementations provide actual locking semantics for `readLock`, `readLockInterruptibly`, `readUnlock`, `hasReadLock`, `writeLock`, `writeLockInterruptibly`, `writeUnlock`, and `hasWriteLock`. Interface defaults normalize simple calls into mode-aware calls.

## State and Persistence
No state in the interface. Implementations own lock state, metrics, and operation-name handling.

## Dependencies and Integration
It depends on `RwLockMode`. It is an FSNamesystem-facing contract and supports fine-grained locking modes such as global, filesystem, and block-manager locks.

## Risks
Default methods can hide mode selection mistakes if callers should use a non-global mode. Operation names are free-form strings, so metrics/logging consistency depends on callers. Implementations must preserve reentrancy/ownership semantics expected by existing FSNamesystem code.

## Test Signals
Implementation tests should verify default delegation, mode-specific acquisition/release, interruptible behavior, held-lock checks by current thread, write/read exclusion, and operation-name propagation to metrics/logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLockMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLockMode.java

## Purpose
`RwLockMode` enumerates read/write lock domains for fine-grained locking.

## APIs and Types
The enum constants are `GLOBAL`, `FS`, and `BM`.

## Control Flow
There is no behavior. Callers pass modes to `RwLock` implementations to select the lock domain.

## State and Persistence
Enum constants are static JVM state only. No persistence.

## Dependencies and Integration
It integrates directly with `RwLock` and FSNamesystem fine-grained locking code. `GLOBAL` is the default used by `RwLock` compatibility methods, while `FS` and `BM` represent filesystem and block-manager scopes.

## Risks
Adding modes is source-compatible but can require implementation updates. Misusing a narrower mode where global coordination is required can introduce races.

## Test Signals
Tests should verify all `RwLock` implementations handle every enum constant and that default interface methods still route to `GLOBAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLockMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/XMLUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/XMLUtils.java

## Purpose
`XMLUtils` centralizes XML-safe string mangling/unmangling, SAX string emission, and a simple parsed XML stanza tree representation for HDFS internals.

## APIs and Types
Public nested exceptions are `InvalidXmlException` and `UnmanglingError`. Public methods include `mangleXmlString`, `unmangleXmlString`, and `addSaxString`. Nested `Stanza` stores a value plus sorted child-name map to lists of child stanzas, with accessors and `toString`.

## Control Flow
`mangleXmlString` iterates Unicode code points, mangling XML-illegal code points and backslash as `\XXXX;`, and optionally replacing XML entity characters with entity references. `unmangleXmlString` runs a small state machine for backslash escapes and optional entity refs, throwing `UnmanglingError` on malformed escapes/entities. `addSaxString` emits a tag and mangled character data. `Stanza` adds children into a `TreeMap`, retrieves single or multiple children, and formats nested content.

## State and Persistence
The utility methods are stateless. `Stanza` holds mutable value and child lists in memory. No persistence.

## Dependencies and Integration
It depends on SAX `ContentHandler`, `AttributesImpl`, Java collections, and Hadoop annotations. It is used by offline image XML writers and XML parsing/serialization code that must preserve characters XML cannot represent directly.

## Risks
The mangling format uses exactly four hex positions despite code points potentially exceeding `0xffff`; current illegal code points handled here fit that pattern except backslash. `unmangleXmlString` only decodes named entity refs it knows, not numeric refs. `Stanza.getValueOrNull` rejects multiple values for a key, so callers must choose child-list APIs for repeated tags. `mangleXmlString` does not handle null input.

## Test Signals
Tests should cover XML-illegal controls, allowed tab/LF/CR, surrogate/noncharacters, backslash round trip, entity creation/decoding, malformed escape and entity errors, SAX emission, stanza multiple-child handling, and deterministic `TreeMap` ordering in `toString`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/XMLUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilter.java

## Purpose
`AuthFilter` customizes Hadoop HTTP proxy-user authentication for WebHDFS by allowing delegation-token URL authentication to bypass Kerberos authentication.

## APIs and Types
It extends `ProxyUserAuthenticationFilter` and overrides `doFilter(ServletRequest, ServletResponse, FilterChain)`.

## Control Flow
`doFilter` wraps the request with `ProxyUserAuthenticationFilter.toLowerCase`, reads the `delegation` query parameter by `DelegationParam.NAME`, and checks that the servlet path starts with `WebHdfsFileSystem.PATH_PREFIX`. When both are true, it delegates directly to the downstream filter chain with the lower-cased request and returns. Otherwise it invokes the superclass filter.

## State and Persistence
The filter has no added state and no persistence. Authentication state is managed by the superclass and downstream token handling.

## Dependencies and Integration
It depends on servlet APIs, `DelegationParam`, `WebHdfsFileSystem`, and Hadoop authentication server filters. It is installed by `AuthFilterInitializer`.

## Risks
The bypass relies on downstream WebHDFS code validating the delegation token; this filter only skips Kerberos. Request lower-casing may affect parameter/path handling consistently with proxy-user filter expectations. Path prefix matching must not overmatch unintended servlets.

## Test Signals
Tests should cover delegation token on WebHDFS path bypassing superclass auth, delegation token on non-WebHDFS path not bypassing, no token path, lower-case wrapper behavior, and interaction with proxy-user parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilterInitializer.java

## Purpose
`AuthFilterInitializer` builds and registers the servlet filter configuration for HDFS WebHDFS authentication using `AuthFilter`.

## APIs and Types
It extends `FilterInitializer`. Constructor sets the config prefix to `hadoop.http.authentication.`. `createFilterConfig(Configuration)` is protected for testing/extension, and `initFilter(FilterContainer, Configuration)` registers the filter.

## Control Flow
`createFilterConfig` starts with `AuthenticationFilterInitializer.getFilterConfigMap`, copies proxy-user configuration entries from `hadoop.proxyuser.*` into filter keys prefixed with `proxyuser`, defaults the auth type to Kerberos when UGI security is enabled or pseudo otherwise, sets cookie path to `/`, and returns the map. `initFilter` adds `AuthFilter` by name and class to the provided container.

## State and Persistence
State is the config prefix string. No persistence. Runtime behavior depends on global `UserGroupInformation.isSecurityEnabled()`.

## Dependencies and Integration
It depends on Hadoop HTTP filter container APIs, security authentication initializers, UGI, `ProxyUsers`, Kerberos and pseudo authentication handler constants, and `AuthFilter`.

## Risks
The default auth type is determined at initialization time from UGI global state, so tests and embedded servers must configure UGI before calling it. Proxy-user key rewriting is string-based and must match authentication filter expectations. Cookie path `/` affects all server paths.

## Test Signals
Tests should verify inherited auth config copying, proxy-user entry translation, Kerberos versus pseudo defaulting, preservation of explicit type, cookie path setting, and `FilterContainer.addFilter` parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilterInitializer.java -->
