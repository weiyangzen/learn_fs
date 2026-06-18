# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithRandomECPolicy.java

Purpose: reuses the full `TestReconstructStripedFile` suite with a randomly selected non-default EC policy, broadening reconstruction coverage beyond the system default policy geometry.

Important APIs and types: subclassing `TestReconstructStripedFile`, `ErasureCodingPolicy`, `StripedFileTestUtil.getRandomNonDefaultECPolicy`, JUnit `@Tag("slow")`, and SLF4J logging.

Control flow: the constructor selects a non-default EC policy and logs it. `getEcPolicy` is overridden so the inherited setup, tests, helper methods, and assertions run with that policy's data/parity/cell-size parameters.

State and persistence behavior: inherits all MiniDFS cluster, block file, reconstruction queue, and DataNode state behavior from the parent suite. The only local state is the selected `ecPolicy` field.

Dependencies and integration points: depends on `StripedFileTestUtil` policy selection and the parent class honoring `getEcPolicy` for all derived geometry.

Risks and edge cases: random policy selection increases coverage but reduces reproducibility unless the helper logs enough policy detail for triage. Because all inherited tests execute, policies with smaller parity counts may skip assumption-guarded tests or alter failure matrix boundaries.

Test signals: all inherited reconstruction assertions pass under the chosen non-default EC policy.
