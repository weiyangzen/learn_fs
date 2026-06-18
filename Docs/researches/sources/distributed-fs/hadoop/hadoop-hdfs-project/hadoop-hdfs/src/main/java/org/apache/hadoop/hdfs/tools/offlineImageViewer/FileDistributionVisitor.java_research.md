## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionVisitor.java

Purpose: `FileDistributionVisitor` is the legacy visitor-based file-size distribution processor for pre-PB/offline image traversal.

Important APIs and control flow: the constructor applies default max size and step, validates interval count against `Integer.MAX_VALUE`, and initializes counters. `visitEnclosingElement` tracks nesting, starts a `FileContext` for each inode, and reads the block count from `BLOCKS` attributes. `visit` fills current path, replication, and cumulative byte size while inside an inode. `leaveEnclosingElement` finalizes inode accounting: negative block count means directory, otherwise it increments file counters, computes replicated space, updates max size, and increments the correct bucket. `finish` and `finishAbnormally` both output distribution data before closing.

State, persistence, and dependencies: mutable state is the element stack, current inode context, distribution array, counters, max size, step, and format flag. Output is through `TextWriterImageVisitor`, while totals are printed to `System.out`.

Integration points: selected by legacy `OfflineImageViewer -p FileDistribution` and driven by `ImageLoaderCurrent`.

Risks and test signals: tests should cover directories, files under construction, block count attributes, zero-length files, bucket boundary behavior, formatted output, and abnormal finish. Unlike the PB calculator, summary totals are sent to stdout rather than the output file, which is a compatibility quirk worth regression-testing.
