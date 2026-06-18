# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/hdfs-site.xml

Purpose: this RBF test `hdfs-site.xml` provides a minimal HDFS site override for tests. It exists to make tiny test block sizes legal.

Important property: it sets `dfs.namenode.fs-limits.min-block-size` to `0`, disabling the normal minimum block-size guard because many tests create tiny blocks.

Control flow and integration behavior: Hadoop test clusters and filesystem tests pick this resource up as part of test configuration. It affects NameNode validation during file creation and block allocation.

State and persistence behavior: the configuration does not persist application data, but it changes NameNode policy so test files with very small blocks can be created instead of rejected.

Risks and test signals: this is test-only behavior and should not be confused with production defaults. If tests unexpectedly use production-like min block sizes, many small-block fixtures could fail at file creation time.
