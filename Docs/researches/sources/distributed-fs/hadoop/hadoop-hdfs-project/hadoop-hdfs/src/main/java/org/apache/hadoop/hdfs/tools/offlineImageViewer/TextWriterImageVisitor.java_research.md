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
