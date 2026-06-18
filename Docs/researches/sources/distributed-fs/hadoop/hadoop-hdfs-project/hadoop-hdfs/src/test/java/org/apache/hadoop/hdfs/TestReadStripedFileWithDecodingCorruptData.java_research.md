# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingCorruptData.java

Purpose: slow parameterized EC read suite that corrupts a tolerable number of data and parity internal blocks before reading and verifies the client decoder returns correct file contents.

Important APIs and types: `ReadStripedFileWithDecodingHelper.getParameters`, `initializeCluster`, `tearDownCluster`, `testReadWithBlockCorrupted`, `MiniDFSCluster`, `DistributedFileSystem`, JUnit 5 `@ParameterizedTest`, `@MethodSource`, `@BeforeAll`, `@AfterEach`, `@Timeout(300)`, and `@Tag("slow")`.

Control flow: static setup creates an EC cluster. Parameter rows supply file length, data-block deletion/corruption count, and parity-block count. The test stores parameters, calls `setup` again, constructs a source path using the counts, and delegates to the helper with `delete=false` so blocks are corrupted rather than removed. `tearDown` shuts the cluster after each case.

State and persistence behavior: manipulates DataNode block contents for striped files in a live MiniDFS cluster and relies on helper logic to preserve enough parity/data cells for online decode. Static cluster state is repeatedly reinitialized and torn down, so cleanup sequencing matters.

Dependencies and integration points: delegates core EC policy setup, corruption, and read verification to `ReadStripedFileWithDecodingHelper`, integrating with `StripedFileTestUtil` through that helper. It is a regression lane for the client read path rather than NameNode reconstruction.

Risks and edge cases: setup is annotated `@BeforeAll` but also called inside the test after parameter initialization; with `@AfterEach` teardown this can be confusing and may leak or double-create cluster state if earlier initialization is not closed. The matrix is tagged slow because it multiplies file lengths by corruption combinations.

Test signals: the helper must complete read verification for each tolerable corruption combination without IOException or content mismatch.
