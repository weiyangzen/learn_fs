# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteStripedFileWithFailure.java

Purpose: Disabled stress/regression test scaffold for writing erasure-coded striped files while shutting down data and parity datanodes mid-write.

Important APIs and types: `DFSStripedOutputStream`, `StripedFileTestUtil.randomArray`, `killDatanode`, `verifyLength`, `verifySeek`, `verifyStatefulRead`, `verifyPread`, `FSDataOutputStream`, and JUnit `@Disabled`.

Control flow: `testWriteStripedFileWithDNFailure` is disabled pending HDFS-8704/HDFS-9040. If enabled, it iterates small and large file lengths, all data-node failure counts from 1 to parity count, and parity-node failure counts such that total failures stay within parity capacity. For each combination it manually calls `setup`, writes one byte at a time, kills selected datanodes at halfway through the file, closes output, verifies the number of live datanodes decreased, validates read/seek/pread, deletes the file, and tears down the cluster.

State and persistence behavior: The test uses manual cluster lifecycle rather than `@BeforeEach/@AfterEach`; HDFS state is per combination. Mid-write state includes a wrapped `DFSStripedOutputStream`, an atomic position counter, and killed DataNodes.

Dependencies and integration points: Integrates striped output failure handling, datanode shutdown during writes, EC parity tolerance, read-after-failure verification, and cluster lifecycle utilities.

Risks and test signals: Because it is disabled, it provides no normal CI signal. If re-enabled, it is expensive and failure-injection heavy. Passing would signal striped writes can tolerate bounded data/parity datanode failures during write.
