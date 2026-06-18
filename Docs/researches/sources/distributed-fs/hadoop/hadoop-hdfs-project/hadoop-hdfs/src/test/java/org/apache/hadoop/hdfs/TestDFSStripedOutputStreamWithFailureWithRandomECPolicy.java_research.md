# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java

Purpose: variant of striped-output failure tests that runs the inherited failure suite with a random non-default erasure coding schema.

Important APIs and types: extends `TestDFSStripedOutputStreamWithFailure`, uses `ECSchema`, `StripedFileTestUtil.getRandomNonDefaultECPolicy`, SLF4J logging, and JUnit `@Tag("slow")`.

Control flow: constructor chooses and logs a random non-default EC policy schema. The overridden `getEcSchema` returns that schema to the base initialization path, so inherited setup computes data/parity units and block sizing from this non-default policy.

State and persistence: only stores the selected schema in an instance field. Persistent state is produced by inherited MiniDFSCluster writes, EC policy registration, DN failures, and verification.

Dependencies and integration: depends entirely on the inherited striped failure framework and random EC policy utility. It broadens coverage from the default schema to alternate codec layouts.

Risks: random policy selection can vary runtime, parity count, DN count, and failure combinations. Failures may be harder to reproduce unless logs capture the selected schema.

Test signals: inherited assertions from the base failure tests are the real signal; this class adds evidence that non-default EC schemas survive the same failure scenarios.
