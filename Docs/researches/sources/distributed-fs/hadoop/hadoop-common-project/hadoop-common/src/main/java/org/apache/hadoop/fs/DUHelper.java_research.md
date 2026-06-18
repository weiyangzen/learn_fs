## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DUHelper.java

Purpose: `DUHelper` is a simple recursive Java helper for computing folder byte usage and file counts without shelling out. It appears as a standalone utility rather than part of the `CachingGetSpaceUsed` hierarchy.

Important APIs and types: `getFolderUsage(String)` creates a helper and returns `calculateFolderSize`. `check(String)` computes folder size, file count, and disk usage ratio. Accessors expose `getFileCount()` and `getUsage()`. The private recursive `getFileSize(File)` walks directories and sums file lengths.

Control flow, state, and persistence: each helper instance maintains mutable counters `folderCount`, `fileCount`, `usage`, and `folderSize`. Recursion increments `folderCount`, returns `folder.length()` for direct files, returns zero if `listFiles()` is null, and adds child directory/file sizes. No state is persisted beyond the object.

Dependencies and integration: it uses `java.io.File` and `Shell.WINDOWS` only for the demo `main` output label. It is independent from `DU` and `DF`.

Risks and test signals: recursive walking can be slow, can follow filesystem structures with permission failures as zero-sized directories, and can overflow or recurse deeply on large trees. `check` can divide by zero if `getTotalSpace()` is zero. Tests should cover null input, files vs directories, inaccessible directories, nested counts, empty folders, and usage ratio behavior.
