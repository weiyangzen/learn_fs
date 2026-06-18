## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/LsImageVisitor.java

Purpose: `LsImageVisitor` renders legacy fsimage inode entries in a format similar to `hdfs dfs -lsr`, including type marker, permissions, replication, owner/group, size, modification time, and path.

Important APIs and control flow: `newLine` resets per-inode fields and marks `inInode`. `visitEnclosingElement` starts a new line for `INODE` and records `BLOCKS` count attributes. `visit` records path, permission string, replication, owner, group, block byte totals, modification time, and symlink target while inside an inode. `leaveEnclosingElement` prints the formatted row when an `INODE` closes. Directories are identified by negative block count and get a `d` prefix; files get `-`; symlinks append ` -> target`.

State, persistence, and dependencies: per-inode state is stored in primitive/string fields, with a context stack and reusable `StringBuilder`/`Formatter`. Output is through `TextWriterImageVisitor`.

Integration points: default legacy `OfflineImageViewer` processor. The CLI forces block enumeration for this visitor because file sizes are computed by summing `NUM_BYTES`.

Risks and test signals: tests should cover root path, directories, files, symlinks, under-replication display fallback, missing optional fields, and ordering differences from live `lsr`. Exact formatting widths are part of compatibility. Because entries are fsimage order, tests must not assume lexicographic sort.
