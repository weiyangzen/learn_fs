<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapFile.java

## Purpose
Comprehensive tests for `MapFile` reader/writer behavior, index construction/repair, seek/getClosest/midKey/finalKey APIs, file rename/delete/merge helpers, constructor compatibility, and failure paths.

## Important APIs, Types, and Functions
Uses `MapFile.Writer`, `MapFile.Reader`, `MapFile.rename`, `delete`, `fix`, `Merger`, writer options `keyClass`, `valueClass`, `compression`, reader comparator options, `WritableComparator`, `SequenceFile.CompressionType`, local filesystem, Mockito spies, and cleanup via `IOUtils.cleanupWithLogger`. Helpers create writers/readers under a temp `TEST_DIR` with index interval 4.

## Control Flow and State
`setup()` deletes and recreates the temp root for each test. Current API tests write ordered key/value pairs and validate `getClosest`, `midKey`, `finalKey`, iteration reset, seek success/failure, type mismatches, and key ordering enforcement. File-operation tests validate rename success, false return and thrown IO paths, mkdir failures, path filesystem exceptions, and delete. Index repair tests remove/rename the `index` file and call `MapFile.fix`, including block-compressed data. Deprecated constructor tests instantiate legacy writer/reader signatures. Merge writes five overlapping sorted map files, merges them, checks global sorted iteration, and verifies inputs are deleted. A `main` invocation smoke-tests `MapFile.main`.

## Dependencies and Integration Points
Integrates `SequenceFile` data/index files, Hadoop local filesystem, compression codec plumbing, writable comparators, and MapFile command-line behavior. It is a high-value persistence regression suite because `MapFile` is an indexed directory containing data and index sequence files.

## Risks and Test Signals
Risks include stale temp files, incorrect path in `testFix()` when deleting `./.testFix.mapfile/index`, broad catch/fail blocks obscuring root causes, and mocked codecs not exercising real compression streams. Signals include exact closest-key boundary behavior, `midKey` null for empty files, IO messages for rename/mkdir failures, sorted merge ordering, deleted inputs, repaired indexes with zero misses, and exception on descending append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapFile.java -->
