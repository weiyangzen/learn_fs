# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestListFiles.java

Purpose: verifies `FileSystem.listFiles(Path, boolean)` over local files and directories, including recursive and non-recursive behavior and block-location population.

Important APIs/types/functions: `FileSystem.getLocal`, `RemoteIterator<LocatedFileStatus>`, `LocatedFileStatus`, `FSDataOutputStream`, `makeQualified`, and helper `writeFile`.

Control flow/state/persistence: static setup initializes local FS and deletes the test root. `testFile` writes one file and asserts both recursive and non-recursive listing return exactly that file with length and one block location. `testDirectory` checks empty directories, one-file directories, mixed root/nested files with set-based order-independent recursive validation, and non-recursive root listing returning only direct files.

Dependencies/integration points: uses local FS implementation of `listFiles`, block location generation, and path qualification. Test paths can be overridden by subclasses through `setTestPaths`.

Risks/test signals: catches directory traversal regressions, accidental directory entries in file listings, missing block locations, path qualification mismatches, and recursive/non-recursive confusion. Ordering is intentionally ignored for recursive multi-file results.
