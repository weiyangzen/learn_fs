# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFileWithRandomECPolicy.java

Purpose: reuses `TestSafeModeWithStripedFile` with a random non-default EC policy to ensure safe-mode safe-block accounting works across different EC geometries.

Important APIs and types: subclassing `TestSafeModeWithStripedFile`, `ErasureCodingPolicy`, `StripedFileTestUtil.getRandomNonDefaultECPolicy`, and SLF4J logging.

Control flow: constructor selects and logs a non-default EC policy. `getEcPolicy` returns that policy, causing inherited setup and tests to compute data/parity counts, cell size, DataNode count, block size, and minimum storage expectations from the selected policy.

State and persistence behavior: inherits all striped safe-mode cluster state behavior from the parent class. Local state is only the selected EC policy.

Dependencies and integration points: depends on the parent suite using `getEcPolicy` polymorphically and on `StripedFileTestUtil` returning a valid enabled system policy.

Risks and edge cases: random policy selection improves breadth but can make failures less reproducible. Policies with different data/parity counts alter the timing and number of DataNode restarts needed to exit safe mode.

Test signals: inherited safe-mode safe-block assertions pass under the selected non-default EC policy.
