# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatusWithRandomECPolicy.java

## Purpose
Reuses the default EC file-status test with a random non-default erasure-coding policy, broadening coverage beyond the default policy.

## APIs and Control Flow
The class extends `TestFileStatusWithDefaultECPolicy`, chooses `StripedFileTestUtil.getRandomNonDefaultECPolicy()` in the constructor, logs the selected policy, and overrides `getEcPolicy()` to return that policy. All inherited setup and assertions run against the selected non-default policy.

## State, Dependencies, Integration
State is inherited cluster and namespace metadata from the superclass plus the per-instance `ErasureCodingPolicy`. It depends on `StripedFileTestUtil` and SLF4J logging. It integrates random EC policy selection with the same status-reporting API contract.

## Risks and Test Signals
The inherited assertions remain the main signal. The main risk is nondeterminism: failures may depend on the randomly selected policy unless logs are preserved. The test does not add new methods, so inherited lifecycle assumptions must remain compatible with all non-default policies.
