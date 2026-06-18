## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/DelimitedImageVisitor.java

Purpose: `DelimitedImageVisitor` is a legacy `ImageVisitor` implementation that writes one delimiter-separated row per inode or inode-under-construction. It captures common inode fields for spreadsheet or script analysis.

Important APIs and control flow: constructors default to tab delimiter unless a custom delimiter is supplied. An initializer defines the ordered tracked columns: path, replication, modification/access time, block size, block count, byte count, quotas, permission string, user, and group. `visit` records tracked scalar elements and sums `NUM_BYTES` values to compute file size. `visitEnclosingElement` pushes element context and handles `BLOCKS` attributes for block count. `leaveEnclosingElement` pops context; when an inode closes, it writes the ordered row, newline, and resets the per-inode map.

State, persistence, and dependencies: state includes an element stack, tracked field map, delimiter, and rolling `fileSize`. Output is managed by `TextWriterImageVisitor`.

Integration points: selected by legacy `OfflineImageViewer` processor `Delimited`. It depends on `ImageLoaderCurrent` emitting block byte events unless blocks are skipped; the CLI forces `skipBlocks=false` for this processor.

Risks and test signals: tests should cover root path normalization, custom delimiters, missing version-dependent fields, directory rows, and file-size summation across blocks. Since values are not escaped, delimiters embedded in names or metadata can make ambiguous rows.
