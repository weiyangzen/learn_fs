## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DepthCounter.java

Purpose: `DepthCounter` is a utility for visitor implementations that need to track nesting depth while traversing a structured image or edit representation.

Important APIs and control flow: `incLevel()` increments the internal depth, `decLevel()` decrements only when depth is at least one, and `getLevel()` returns the current integer. The guard in `decLevel()` prevents negative indentation after mismatched close calls.

State, persistence, and dependencies: state is a single integer field. There is no persistence and no runtime dependency beyond Hadoop classification annotations.

Integration points: `IndentedImageVisitor` uses it to decide how much indentation to print for each visited element. The class is generic enough for other visitor-style tools, but in this subset it is only a presentation helper.

Risks and test signals: unit tests should verify initial zero depth, normal increment/decrement behavior, and repeated decrement at zero. It is not thread-safe, but image visitors are single-threaded in the legacy pipeline. Because underflow is silently ignored, tests for higher-level visitors should detect missing or extra `leaveEnclosingElement` calls rather than relying on this class to fail fast.
