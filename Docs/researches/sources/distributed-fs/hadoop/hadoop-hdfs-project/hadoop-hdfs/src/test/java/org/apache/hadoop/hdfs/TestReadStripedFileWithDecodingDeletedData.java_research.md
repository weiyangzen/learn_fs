# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingDeletedData.java

Purpose: slow parameterized EC read suite that deletes, rather than corrupts, a tolerable number of data and parity internal blocks and verifies online decoding can satisfy stateful reads.

Important APIs and types: `ReadStripedFileWithDecodingHelper.getParameters`, `initializeCluster`, `tearDownCluster`, `testReadWithBlockCorrupted`, `MiniDFSCluster`, `DistributedFileSystem`, JUnit 5 parameterized test support, `@BeforeAll`, `@AfterAll`, `@Timeout(300)`, and `@Tag("slow")`.

Control flow: setup initializes a shared EC MiniDFS cluster. Each parameterized invocation saves the file length and data/parity missing counts, builds a path like `/deleted_<data>_<parity>`, and delegates to the helper with `delete=true`. Teardown occurs once after all cases.

State and persistence behavior: tests missing block files and/or missing block locations in a live EC cluster. Because the cluster is shared across all parameter combinations, generated paths include counts to avoid collisions and keep state distinguishable.

Dependencies and integration points: helper-driven integration with EC policy setup, DataNode storage mutation, and striped read verification. This lane complements the corrupt-data variant by exercising missing-block behavior instead of checksum/corruption detection.

Risks and edge cases: shared cluster state means one failed or partially cleaned parameter case can affect later cases. Coverage is bounded to helper-provided tolerable combinations; unrecoverable deletion counts are not expected to pass.

Test signals: successful helper read verification across file lengths and data/parity deletion counts.
