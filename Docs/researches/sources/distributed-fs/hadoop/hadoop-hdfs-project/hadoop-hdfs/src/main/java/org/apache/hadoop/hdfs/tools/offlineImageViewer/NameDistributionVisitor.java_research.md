## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/NameDistributionVisitor.java

Purpose: `NameDistributionVisitor` analyzes basename reuse in a legacy fsimage and estimates heap savings if repeated file-name byte arrays were reused.

Important APIs and control flow: `visit` watches for `INODE_PATH`, extracts the substring after the last slash, and increments a `HashMap<String, Integer>`. It ignores container events. `finish` writes the number of unique names, buckets names by frequency thresholds from 100000 down to 2, estimates saved bytes as `(24 + name.length()) * (count - 1)`, emits per-bucket summaries, then closes through the superclass.

State, persistence, and dependencies: state is the `counts` map. Output is handled by `TextWriterImageVisitor`. It depends only on basic collections and Hadoop classification annotations.

Integration points: selected by legacy `OfflineImageViewer -p NameDistribution` and driven by `ImageLoaderCurrent`.

Risks and test signals: tests should include root path, repeated basenames in different directories, names with no slash, and bucket-boundary frequencies. The byte-savings estimate uses Java `String.length()` and a fixed byte-array overhead, so it is approximate and JVM-dependent. Very large namespaces can make the `HashMap` memory-heavy because every unique basename is retained.
