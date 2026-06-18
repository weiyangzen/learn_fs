## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IndentedImageVisitor.java

Purpose: `IndentedImageVisitor` writes a tree-like text dump of legacy fsimage traversal events with indentation for nested structures.

Important APIs and control flow: constructors delegate to `TextWriterImageVisitor`. `visit` prints the current indentation followed by `ELEMENT = value`. The `long` overload formats delegation-token date fields as `Date.toString()` and otherwise prints the number. `visitEnclosingElement` prints the container name, optionally with a bracketed key/value pair, and increments depth. `leaveEnclosingElement` decrements depth. `finishAbnormally` prints a console warning before closing through the superclass.

State, persistence, and dependencies: state is a `DepthCounter` and a static cache of indent strings for shallow depths. Output is handled by `TextWriterImageVisitor`. Dependencies include `Date`.

Integration points: selected by legacy `OfflineImageViewer -p Indented` and driven by `ImageLoaderCurrent`.

Risks and test signals: tests should verify indentation, deep nesting fallback, date formatting for delegation token fields, and balanced depth. Output uses platform/default `Date.toString()` timezone representation, which can make exact-string tests environment-sensitive. The visitor is diagnostic, so it intentionally preserves event order rather than sorting or normalizing records.
