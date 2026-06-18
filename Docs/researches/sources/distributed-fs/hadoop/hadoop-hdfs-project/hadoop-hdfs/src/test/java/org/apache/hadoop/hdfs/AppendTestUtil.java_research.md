# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AppendTestUtil.java

`AppendTestUtil` is a compact HDFS append-test helper. It provides reproducible pseudo-random data, fixed small block-size constants, alternate-user filesystem creation, helper file creation, and byte-for-byte validation for append scenarios.

Important APIs include `randomBytes`, `randomFilePartition`, `createHdfsWithDifferentUsername`, `write`, `check`, `initBuffer`, `createFile`, `checkFullFile`, and `testAppend`. The class initializes a logged global random seed and thread-local `Random` instances derived from it. File-checking paths assert length through `DFSInputStream.getFileLength()` when available or `FileStatus.getLen()` otherwise, then read expected byte sequences and EOF. `testAppend` creates an initial file, appends identical content repeatedly, validates length after each close, and positional-reads all appended segments.

State is mostly process-local random state: `SEED`, `RANDOM`, and mutable static `seed`. Persistent effects are only the files created or appended through caller-provided `FileSystem` instances; streams returned by `createFile` must be closed by callers. Dependencies include Hadoop `FileSystem`, HDFS `DistributedFileSystem`/`DFSInputStream`, `UserGroupInformation`, JUnit assertions, and `DFSTestUtil`.

Risks are centered on shared static seed reuse, inefficient byte-at-a-time validation for large files, and assumptions in `randomFilePartition` about valid `n`/`parts` ranges. Test signals are strong for append correctness: length assertions, byte comparisons with failing offsets, EOF checks, and logged seeds for reproduction.
