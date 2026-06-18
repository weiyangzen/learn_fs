<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractVectoredRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractVectoredRead.java

Purpose: Adapts vectored-read contract tests to HDFS across parameterized buffer types.
Important APIs/types/functions: `TestHDFSContractVectoredRead` is a JUnit `@ParameterizedClass` over `params`, extends `AbstractContractVectoredReadTest`, and passes `bufferType` to the superclass.
Control flow: For each buffer type, HDFSContract cluster setup/teardown brackets inherited vectored-read tests that issue ranged reads and compare results.
State and persistence behavior: State includes the static contract cluster and per-parameter test files/buffers.
Dependencies and integration points: Integrates HDFS vectored read implementation with generic contract coverage and JUnit parameterized class support.
Risks and edge cases: Parameterized cluster lifecycle can be expensive. Buffer-type support must match inherited expectations, and range coalescing errors can be subtle.
Test signals: Signals are inherited vectored-read content, range, EOF, and buffer-management assertions for each buffer type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractVectoredRead.java -->
